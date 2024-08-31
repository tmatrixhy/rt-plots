"""
This module provides web APIs for interacting with Monte Carlo simulations.
"""
# locals
import logging
from pathlib import Path
from typing import Dict

# project
from src.sim.simulator import MonteCarloSimulation
from src.sim.utils import log_name

# third party
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles


logger = logging.getLogger(log_name)


class SimulationWEBAPIs:
    def __init__(self, sims: Dict[str, MonteCarloSimulation]):
        self.app = FastAPI()
        self.app.mount(
            "/static", 
            StaticFiles(
                directory=Path(__file__).parent / "static"), 
                name="static")
        self.sims = sims
        self.ids = [sim_id for sim_id in self.sims.keys()]
        self._setup_routes()

    def _setup_routes(self):
        # Define a list of routes and their corresponding action names
        routes = [
            ("/", self.read_index, ["GET"]),
            ("/simulation-ids/", self.get_simulation_ids, ["GET"]),
            ("/control/{sim_id}/start", "start", ["POST"]),
            ("/control/{sim_id}/pause", "pause", ["POST"]),
            ("/control/{sim_id}/resume", "resume", ["POST"]),
            ("/control/{sim_id}/stop", "stop", ["POST"]),
            ("/control/{sim_id}/restart", "restart", ["POST"]),
            ("/control/{sim_id}/mark", "mark", ["POST"])
        ]

        # Dynamically add routes to the FastAPI app
        for path, action, methods in routes:
            if type(action) == str:
                self.app.add_api_route(path, self.handle_request(action), methods=methods)
            else:
                self.app.add_api_route(path, action, methods=methods)

    def handle_request(self, action: str):
        def handler(sim_id: str):
            sim = self.sims.get(sim_id)
            if not sim:
                raise HTTPException(status_code=404, detail="Simulation not found")
            if hasattr(sim, action):
                getattr(sim, action)()
                return {"message": f"success"}
            else:
                raise HTTPException(status_code=400, detail=f"failure")
        
        return handler

    def read_index(self):
        index_file = Path(__file__).parent / "static" / "index.html"
        return HTMLResponse(content=index_file.read_text(), status_code=200)
    
    def get_simulation_ids(self):
        return {"simulation_ids": self.ids }
