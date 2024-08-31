"""
This file contains utility functions for the simulation module.
"""
# locals
import argparse
import logging

# project
# ..

# third party
# ..

# constants
logging.basicConfig(
    level=logging.INFO, 
    format="[ {asctime:s} ]|[ {name:>32s} ]|[{lineno:4d}]|[  {levelname:<8s} ]|[ {message:s} ]",
    datefmt="%Y-%m-%dT%H:%M:%SL",
    style="{" )


log_level_map = {
    logging.DEBUG: "debug",
    logging.INFO: "info",
    logging.WARNING: "warning",
    logging.ERROR: "error",
    logging.CRITICAL: "critical"
}


log_name = "src.sim.utils"


def parse_cvars():
    logger = logging.getLogger(__name__)
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-s", "--sims", type=int, help="number of simulations to run")
    parser.add_argument(
        "-v", "--verbose", action="count", default=0, help="increase logging verbosity level"
    )

    parser = parser.parse_args()

    if parser.verbose >= 3:
        logger.setLevel(level=logging.DEBUG)
    elif parser.verbose == 2:
        logger.setLevel(level=logging.INFO)
    elif parser.verbose == 1:
        logger.setLevel(level=logging.WARNING)
    else:
        logger.setLevel(level=logging.ERROR)

    return parser
