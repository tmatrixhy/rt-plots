"""
WebServer class for starting and stopping the uvicorn web server.
"""
# locals
import asyncio
import logging

# project
from src.sim.web_apis import SimulationWEBAPIs

# third party
import uvicorn

# constants
logger = logging.getLogger(__name__)


class WebServer:
    def __init__(self, web_apis:SimulationWEBAPIs, host:str, port:int) -> None:
        self.web_apis = web_apis
        self.host = host
        self.port = port

    async def start_server(self) -> None:
        try:
            await asyncio.sleep(0.1)
            config = uvicorn.Config(
                self.web_apis.app, 
                host=self.host, 
                port=self.port, 
                lifespan="on",
                log_config=None,
                log_level=logger.getEffectiveLevel()
            )
            self.server = uvicorn.Server(config)
            await self.server.serve()
        except asyncio.CancelledError:
            pass

    async def stop_server(self) -> None:
        self.server.should_exit = True
