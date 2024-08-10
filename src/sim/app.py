"""
This module contains the SimulationApp class for the simulation application.
"""

# third party
from flask import Flask, render_template
from flask_socketio import SocketIO, emit


class SimulationApp:
    """
    Class representing the simulation application.

    Args:
        app (Flask): Flask application instance.
        socketio (SocketIO): SocketIO instance for emitting data.
        simulation_ids (dict): Dictionary of simulation IDs.

    Attributes:
        app (Flask): Flask application instance.
        socketio (SocketIO): SocketIO instance for emitting data.
        simulations (dict): Dictionary of simulation instances.

    """

    def __init__(self, app: Flask, socketio: SocketIO, simulation_ids: dict) -> None:
        self.app = app
        self.socketio = socketio
        self.simulations = simulation_ids
        self._setup_routes()
        self._setup_socketio_events()

    def _setup_routes(self) -> None:
        """
        Setup routes for the application.
        """
        @self.app.route('/')
        def index() -> str:
            """
            Render the index template.
            """
            return render_template('index.html', simulation_ids=self.simulations.keys())

        @self.app.route('/favicon.ico')
        def favicon() -> str:
            """
            Return empty response for favicon.
            """
            return '', 204

    def _setup_socketio_events(self) -> None:
        """
        Setup SocketIO events for the application.
        """
        @self.socketio.on('start')
        def handle_start(data: dict) -> None:
            """
            Handle the 'start' event.
            """
            sim_id = data['sim_id']
            if sim_id in self.simulations:
                self.simulations[sim_id].start()

        @self.socketio.on('pause')
        def handle_pause(data: dict) -> None:
            """
            Handle the 'pause' event.
            """
            sim_id = data['sim_id']
            if sim_id in self.simulations:
                self.simulations[sim_id].pause()

        @self.socketio.on('resume')
        def handle_resume(data: dict) -> None:
            """
            Handle the 'resume' event.
            """
            sim_id = data['sim_id']
            if sim_id in self.simulations:
                self.simulations[sim_id].resume()

        @self.socketio.on('initiate')
        def handle_initiate(data: dict) -> None:
            """
            Handle the 'initiate' event.
            """
            sim_id = data['sim_id']
            if sim_id in self.simulations:
                self.simulations[sim_id].initiate()

        @self.socketio.on('restart')
        def handle_restart(data: dict) -> None:
            """
            Handle the 'restart' event.
            """
            sim_id = data['sim_id']
            if sim_id in self.simulations:
                self.simulations[sim_id].restart()
                self.socketio.emit('clear_data', {'sim_id': sim_id})

    def run(self, debug: bool = True) -> None:
        """
        Run the simulation application.

        Args:
            debug (bool, optional): Enable debug mode. Defaults to True.
        """
        self.socketio.run(self.app, debug=debug)
