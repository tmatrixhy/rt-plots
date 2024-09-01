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
# ..


def setup_logging(cvars: argparse.ArgumentParser) -> None:
    if cvars.verbose >= 3:
        level = logging.DEBUG
    elif cvars.verbose == 2:
        level = logging.INFO
    elif cvars.verbose == 1:
        level = logging.WARNING
    else:
        level = logging.ERROR

    logging.basicConfig(
        level=level, 
        format="[ {asctime:s} ]|[ {name:>32s} ]|[{lineno:4d}]|[  {levelname:<8s} ]|[ {message:s} ]",
        datefmt="%Y-%m-%dT%H:%M:%SL",
        style="{" )
    
    return


def parse_cvars() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-s", "--sims", type=int, help="number of simulations to run")
    parser.add_argument(
        "-v", "--verbose", action="count", default=0, help="increase logging verbosity level"
    )

    parser = parser.parse_args()

    return parser
