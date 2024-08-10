"""
This module is the entry point for the simulation application. 
It creates a Flask app and starts the socketio server.
"""
# locals
import sys
import random
import logging

# third party
from flask import Flask
from flask_socketio import SocketIO

# project
from src.sim.app import SimulationApp
from src.sim.simulator import MonteCarloSimulation

# setup logging
logging.basicConfig(
    level=logging.INFO, 
    format="[ {asctime:s} ]|[ {name:>32s} ]|[{lineno:4d}]|[  {levelname:<8s} ]|[ {message:s} ]",
    datefmt="%Y-%m-%dT%H:%M:%SL",
    style="{" )
logger = logging.getLogger(__name__)

if __name__ == '__main__':
    simulation_ids = ["sim_a", "sim_b", "sim_c"]

    app = Flask(__name__)
    socketio = SocketIO(app)

    sims = {}
    for sim_id in simulation_ids:
        rand_int = random.randint(1, 10)
        sim_id = f"{sim_id} - {rand_int} Hz"
        sims[sim_id] = MonteCarloSimulation(
            sim_id, socketio, rand_int)
        sims[sim_id].start()

    flask_app = SimulationApp(app, socketio, sims)

    try:
        flask_app.run(debug=True)
    except Exception as e:
        logger.error(e)
    finally:
        for sim in flask_app.simulations.values():
            sim.stop()
        sys.exit(0)
