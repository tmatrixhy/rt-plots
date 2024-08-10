import random
import time
import threading
import sys
from flask import Flask, render_template
from flask_socketio import SocketIO, emit

class MonteCarloSimulation:
    def __init__(self, socketio):
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
                'x': current_time,
                'y': self.current_value,
                'initiate_value': self.initiate_value,
                'max_delta': self.max_delta,
            })

            time.sleep(0.1)


class SimulationApp:
    def __init__(self, app:Flask, sockio: SocketIO, sim: MonteCarloSimulation):
        self.app = app
        self.socketio = sockio
        self.simulation = sim
        self._setup_routes()
        self._setup_socketio_events()

    def _setup_routes(self):
        @self.app.route('/')
        def index():
            return render_template('index.html')

    def _setup_socketio_events(self):
        @self.socketio.on('pause')
        def handle_pause():
            self.simulation.pause()
        
        @self.socketio.on('start')
        def handle_start():
            self.simulation.start()

        @self.socketio.on('resume')
        def handle_resume():
            self.simulation.resume()

        @self.socketio.on('initiate')
        def handle_initiate():
            self.simulation.initiate()

        @self.socketio.on('restart')
        def handle_restart():
            self.simulation.restart()
            self.socketio.emit('clear_data')


if __name__ == '__main__':
    app = Flask(__name__)
    sockio = SocketIO(app)
    sim = MonteCarloSimulation(sockio)
    flask_app = SimulationApp(app, sockio, sim)
    try:
        sockio.run(app, debug=True)
    except Exception as e:
        print(e)
    finally:
        sim.pause()  # Stop the simulation
        sys.exit(0)
