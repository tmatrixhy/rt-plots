import random
import time
import threading
import sys
from flask import Flask, render_template
from flask_socketio import SocketIO, emit

class MonteCarloSimulation:
    def __init__(self, sim_id, socketio):
        self.sim_id = sim_id  # Unique ID for the simulation
        self.socketio = socketio
        self.current_value = 0
        self.initiate_value = None
        self.max_delta = 0
        self.running = False
        self.thread = None  # Keep track of the running thread
        self.data_lock = threading.Lock()
        self.start_time = time.time()
    
    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self.run_simulation)
        self.thread.start()

    def pause(self):
        self.running = False

    def stop(self):
        self.pause()
        if self.thread is not None:
            self.thread.join()  # Ensure the thread is fully terminated

    def restart(self):
        self.stop()
        self.current_value = 0
        self.initiate_value = None
        self.max_delta = 0
        self.start_time = time.time()
        self.start()

    def resume(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self.run_simulation)
            self.thread.start()

    def initiate(self):
        with self.data_lock:
            self.initiate_value = self.current_value
            self.max_delta = 0

    def run_simulation(self):
        while self.running:
            with self.data_lock:
                current_time = time.time() - self.start_time
                change = random.uniform(-5, 5)
                self.current_value += change

                if self.initiate_value is not None:
                    self.max_delta = self.current_value - self.initiate_value
            
            self.socketio.emit('new_data', {
                'sim_id': self.sim_id,
                'x': current_time,
                'y': self.current_value,
                'initiate_value': self.initiate_value,
                'max_delta': self.max_delta,
            })

            time.sleep(0.1)


class SimulationApp:
    def __init__(self, app: Flask, socketio: SocketIO, simulation_ids: dict):
        self.app = app
        self.socketio = socketio
        self.simulations = simulation_ids
        self._setup_routes()
        self._setup_socketio_events()

    def _setup_routes(self):
        @self.app.route('/')
        def index():
            return render_template('index.html', simulation_ids=self.simulations.keys())

        @app.route('/favicon.ico')
        def favicon():
            return '', 204

    def _setup_socketio_events(self):
        @self.socketio.on('start')
        def handle_start(data):
            sim_id = data['sim_id']
            if sim_id in self.simulations:
                self.simulations[sim_id].start()

        @self.socketio.on('pause')
        def handle_pause(data):
            sim_id = data['sim_id']
            if sim_id in self.simulations:
                self.simulations[sim_id].pause()

        @self.socketio.on('resume')
        def handle_resume(data):
            sim_id = data['sim_id']
            if sim_id in self.simulations:
                self.simulations[sim_id].resume()

        @self.socketio.on('initiate')
        def handle_initiate(data):
            sim_id = data['sim_id']
            if sim_id in self.simulations:
                self.simulations[sim_id].initiate()

        @self.socketio.on('restart')
        def handle_restart(data):
            sim_id = data['sim_id']
            if sim_id in self.simulations:
                self.simulations[sim_id].restart()
                self.socketio.emit('clear_data', {'sim_id': sim_id})

    def run(self, debug=True):
        self.socketio.run(self.app, debug=debug)


if __name__ == '__main__':
    simulation_ids = ["sim_a", "sim_b", "sim_c"]  # List of simulation IDs

    app = Flask(__name__)
    socketio = SocketIO(app)
    
    sims = {}  # Dictionary to hold simulations by ID
    for sim_id in simulation_ids:
        sims[sim_id] = MonteCarloSimulation(sim_id, socketio)
        sims[sim_id].start()

    flask_app = SimulationApp(app, socketio, sims)

    try:
        flask_app.run(debug=True)
    except Exception as e:
        print(e)
    finally:
        for sim in flask_app.simulations.values():
            sim.stop()  # Stop all simulations
        sys.exit(0)
