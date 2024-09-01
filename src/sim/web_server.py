"""
WebServer class for starting and stopping the uvicorn web server.
"""
# locals
import asyncio
import logging

# project
#from src.sim.utils import log_level_map

# third party
import uvicorn


logger = logging.getLogger(__name__)


class WebServer:
    def __init__(self, web_apis, host, port):
        self.web_apis = web_apis
        self.host = host
        self.port = port

    async def start_server(self):
        try:
            await asyncio.sleep(0.1)
            logger.error(logger.getEffectiveLevel())
            #logger.error(log_level_map)
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

    async def stop_server(self):
        self.server.should_exit = True
