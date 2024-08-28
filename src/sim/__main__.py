"""
This module is the entry point for the simulation application. 
It creates a Flask app and starts the socketio server.
"""
# locals
import sys
import random
import logging

# project
from src.sim.db_client import DatabaseClient
from src.sim.data_model import SimID
from src.sim.simulator import MonteCarloSimulation
from src.sim.rest_api import SimulationRESTAPI

# third party
import uvicorn

# setup logging
logging.basicConfig(
    level=logging.INFO, 
    format="[ {asctime:s} ]|[ {name:>32s} ]|[{lineno:4d}]|[  {levelname:<8s} ]|[ {message:s} ]",
    datefmt="%Y-%m-%dT%H:%M:%SL",
    style="{" )
logger = logging.getLogger(__name__)


if __name__ == '__main__':
    num_simulations = 4
    simulation_ids = []

    db_client = DatabaseClient()

    for x in range(num_simulations):
        z = random.randint(1, 100000)
        simulation_ids.append(f"sim_{z}_{x}")

    sims = {}

    try:
        for sim_id in simulation_ids:
            # simulation parameters
            sampling_frequency = random.randint(5, 10)
            sim_id = f"{sim_id} - {sampling_frequency} Hz"
            db_client.write(SimID(sim_id=sim_id))
            sims[sim_id] = MonteCarloSimulation(
                sim_id, db_client, sampling_frequency)
            sims[sim_id].start()
        
        rest_api = SimulationRESTAPI(sims)
        
        uvicorn.run(rest_api.app, host="0.0.0.0", port=8080)
    except Exception as e:
        logger.error(f"Simulation failed to start: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        for sim_id, simulation in sims.items():
            simulation.stop()
        sys.exit(0)
