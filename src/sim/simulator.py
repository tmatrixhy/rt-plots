"""
Monte Carlo simulation.
"""
# locals
import time
import random
import logging
import threading
from collections import deque
from datetime import datetime

# project
from src.sim.statistics import Statistics
from src.sim.db_client import DatabaseClient
from src.sim.data_model import SampleData

# third party
# ..

# constants
logger = logging.getLogger(__name__)


class MonteCarloSimulation:
    """
    Monte Carlo Simulation class.
    Attributes:
        sim_id (str): The ID of the simulation.
        db_client (DatabaseClient): The database client used to write simulation data.
        sample_hz (int): The sample rate in hertz (default: 10).
        max_sample_queue (int): The maximum length of the sample queue (default: 1000).
        sample_periods (list): The periods at which statistics are calculated.
        sample_queue (deque): The queue to store sampled values.
        running (bool): Indicates whether the simulation is running.
        thread (Thread): The thread used to run the simulation loop.
        data_lock (Lock): The lock used to synchronize access to simulation data.
        start_time (float): The start time of the simulation.
        sample_frequency (float): The time interval between samples.
        stats (Statistics): The statistics object used to calculate statistics on the sample queue.
        samples (int): The number of samples taken.
        current_value (float): The current value of the simulation.
        mark_value (float): The initiation value.
        max_delta (float): The maximum change in value since the initiation.
    """
    def __init__(self, 
                 sim_id: str, 
                 db_client: DatabaseClient, 
                 sample_hz: int=10, 
                 max_sample_queue: int=1000) -> None:
        self.sim_id = sim_id
        self.db_client = db_client
        self.max_sample_queue = max_sample_queue
        self.sample_periods = [23, 53, 107, 223]
        self.sample_queue = deque(maxlen=self.max_sample_queue)
        self.running = False
        self.thread = None
        self.data_lock = threading.Lock()
        self.start_time = time.time()
        self.sample_frequency = 1 / sample_hz # hertz to seconds
        self.stats = Statistics(
            sample_periods=self.sample_periods, 
            sample_queue=self.sample_queue)
        # values
        self.samples = 0
        self.current_value = 0
        self.mark_value = None
        self.max_delta = 0

    def start(self) -> None:
        """
        Start the simulation.
        """
        logger.debug(f"Starting simulation {self.sim_id}")
        self.reset()
        self.running = True
        self.thread = threading.Thread(target=self.run_simulation)
        self.thread.start()

    def pause(self) -> None:
        """
        Pause the simulation.
        """
        logger.debug(f"Pausing simulation {self.sim_id}")
        self.running = False

    def stop(self) -> None:
        """
        Stop the simulation.
        """
        logger.debug(f"Stopping simulation {self.sim_id}")
        self.pause()
        if self.thread is not None:
            self.thread.join()
        logger.debug(f"closed {self.sim_id}")

    def restart(self) -> None:
        """
        Restart the simulation.
        """
        logger.debug(f"Restarting simulation {self.sim_id}")
        self.stop()
        self.reset()
        self.start()

    def resume(self) -> None:
        """
        Resume the simulation.
        """
        if not self.running:
            logger.debug(f"Resuming simulation {self.sim_id}")
            self.running = True
            self.thread = threading.Thread(target=self.run_simulation)
            self.thread.start()

    def reset(self) -> None:
        self.sample_queue = deque(maxlen=self.max_sample_queue)
        self.start_time = time.time()
        self.stats = Statistics(
            sample_periods=self.sample_periods, 
            sample_queue=self.sample_queue)
        self.samples = 0
        self.current_value = 0
        self.mark_value = None
        self.max_delta = 0

    def mark(self) -> None:
        """
        Set the current value as the initiation value.
        """
        self.mark_value = self.current_value
        self.curr_delta = self.current_value - self.mark_value
        self.increasing = True
        logger.debug(f"Simulation: {self.sim_id} MARKED with value {self.mark_value}")

    def clear_mark(self) -> None:
        """
        Clears mark
        """
        self.mark_value = None
        self.increasing = False
        self.max_delta = 0
        self.curr_delta = 0

    def sample(self, lower:float=-5.0, upper:float=5.0) -> None:
        """
        Sample a random value within the specified range.
        
        :param lower: The lower bound of the range (default: -5.0)
        :param upper: The upper bound of the range (default: 5.0)
        """
        return random.uniform(lower, upper)

    def update(self, stats:dict) -> None:
        # do fancy things, definitely not something this simple:
        if self.mark_value:
            self.max_delta = self.current_value - self.mark_value

    def run_simulation(self) -> None:
        """
        Run the simulation loop.
        """
        try:
            while self.running:
                with self.data_lock:
                    current_time = datetime.utcnow()

                    # sample from distribution
                    change = self.sample()

                    # increment sample count
                    self.samples += 1

                    # take step
                    self.current_value += change

                    # maintain max sample_queue length
                    if len(self.sample_queue) == self.max_sample_queue - 5:
                        self.sample_queue.popleft()

                    # add current value to sample_queue
                    self.sample_queue.append(self.current_value)

                    # process and get stats on latest sample_queue
                    stats_results = self.stats.process()

                    # calculate fancy things
                    if len(self.sample_queue) > self.sample_periods[-1]:
                        self.update(stats_results)

                    # create db payload
                    payload = SampleData(
                        timestamp=current_time,
                        sim_id=self.sim_id,
                        samples=self.samples,
                        value=self.current_value,
                        mark=self.mark_value,
                        delta=self.max_delta,
                        statistics=stats_results
                    )
                    self.db_client.write(payload)
                    
                    # wait to sample again
                    time.sleep(self.sample_frequency)
        except KeyboardInterrupt:
            self.thread.join()
