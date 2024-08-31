"""
This module is the entry point for the simulation application. 
It creates a Flask app and starts the socketio server.
"""
# locals
import sys
import uuid
import random
import logging
import asyncio
import argparse

# project
from src.sim.db_client import DatabaseClient
from src.sim.data_model import SimID
from src.sim.simulator import MonteCarloSimulation
from src.sim.web_apis import SimulationWEBAPIs
from src.sim.web_server import WebServer
from src.sim.utils import parse_cvars, log_name

# third party
# ..


logger = logging.getLogger(log_name)


async def main():
    cvars = parse_cvars()

    num_simulations = cvars.sims if cvars.sims else 4

    simulation_ids = []
    sims = {}

    for _ in range(num_simulations):
        rand = str(uuid.uuid4()).replace("-", "")[:6]
        simulation_ids.append(f"sim-{rand}")

    db_client = DatabaseClient()

    for sim_id in simulation_ids:
        sampling_frequency = random.randint(5, 10)
        sim_id = f"{sim_id}-{sampling_frequency}-Hz"
        db_client.write(SimID(sim_id=sim_id))
        sims[sim_id] = MonteCarloSimulation(
            sim_id, db_client, sampling_frequency)
        sims[sim_id].start()
    
    web_api = SimulationWEBAPIs(sims)
    web_server = WebServer(
        web_apis=web_api,
        host="0.0.0.0", 
        port=8080
    )
    try:
        await web_server.start_server()
    finally:
        await web_server.stop_server()
        db_client.close()
        for sim_id, simulation in sims.items():
            simulation.stop()
        sys.exit(0)

if __name__ == "__main__":
    asyncio.run(main())
