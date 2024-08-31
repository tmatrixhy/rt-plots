"""
WebServer class for starting and stopping the uvicorn web server.
"""
# locals
import asyncio
import logging

# project
from src.sim.utils import log_level_map, log_name

# third party
import uvicorn


logger = logging.getLogger(log_name)


class WebServer:
    def __init__(self, web_apis, host, port):
        self.web_apis = web_apis
        self.host = host
        self.port = port

    async def start_server(self):
        try:
            logger.error(logger.getEffectiveLevel())
            config = uvicorn.Config(
                self.web_apis.app, 
                host=self.host, 
                port=self.port, 
                lifespan="on",
                log_config=None,
                log_level=log_level_map.get(
                    logger.getEffectiveLevel(), "error")
            )
            self.server = uvicorn.Server(config)
            await self.server.serve()
        except asyncio.CancelledError:
            pass

    async def stop_server(self):
        self.server.should_exit = True
