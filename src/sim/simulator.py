"""
This module contains the MonteCarloSimulation class for running a Monte Carlo simulation.
"""
# locals
import time
import random
import logging
import threading
import itertools
from collections import deque
from datetime import datetime

# project
from src.sim.statistics import Statistics
from src.sim.db_client import DatabaseClient
from src.sim.data_model import SampleData

logger = logging.getLogger(__name__)

class MonteCarloSimulation:
    """
    Class representing a Monte Carlo simulation.

    Args:
        sim_id (str): Unique ID for the simulation.
        db_client (DatabaseClient): Database client for writing data.
        sample_hz (int): Frequency of data sampling in Hz.

    Attributes:
        sim_id (str): Unique ID for the simulation.
        db_client (DatabaseClient): Database client for writing data.
        current_value (float): Current value of the simulation.
        initiate_value (float): Initial value of the simulation.
        max_delta (float): Maximum change in value since initiation.
        running (bool): Flag indicating if the simulation is running.
        thread (Thread): Thread object for running the simulation.
        data_lock (Lock): Lock for thread-safe access to data.
        start_time (float): Start time of the simulation.
        sleep_frequency (float): Time interval between data samples in seconds.
    """

    def __init__(self, 
                 sim_id: str, 
                 db_client: DatabaseClient, 
                 sample_hz:int=10, 
                 max_sample_queue:int=1000) -> None:
        self.sim_id = sim_id
        self.db_client = db_client
        self.max_sample_queue = max_sample_queue
        self.sample_queue = deque(maxlen=self.max_sample_queue)
        self.current_value = 0
        self.initiate_value = None
        self.max_delta = 0
        self.running = False
        self.thread = None
        self.data_lock = threading.Lock()
        self.start_time = time.time()
        self.sample_frequency = 1 / sample_hz # hertz to seconds
        #self.stats = Statistics(self.sample_queue)

    def start(self) -> None:
        """
        Start the simulation.
        """
        logger.info(f"Starting simulation {self.sim_id}")
        self.running = True
        self.thread = threading.Thread(target=self.run_simulation)
        self.thread.start()

    def pause(self) -> None:
        """
        Pause the simulation.
        """
        logger.info(f"Pausing simulation {self.sim_id}")
        self.running = False

    def stop(self) -> None:
        """
        Stop the simulation.
        """
        logger.info(f"Stopping simulation {self.sim_id}")
        self.pause()
        if self.thread is not None:
            self.thread.join()

    def restart(self) -> None:
        """
        Restart the simulation.
        """
        logger.info(f"Restarting simulation {self.sim_id}")
        self.stop()
        self.current_value = 0
        self.initiate_value = None
        self.max_delta = 0
        self.sample_queue = deque(maxlen=self.max_sample_queue)
        self.start_time = time.time()
        self.start()

    def resume(self) -> None:
        """
        Resume the simulation.
        """
        if not self.running:
            logger.info(f"Resuming simulation {self.sim_id}")
            self.running = True
            self.thread = threading.Thread(target=self.run_simulation)
            self.thread.start()

    def initiate(self) -> None:
        """
        Set the current value as the initiation value.
        """
        with self.data_lock:
            self.initiate_value = self.current_value
            self.max_delta = 0
            logger.info(f"Initiated simulation {self.sim_id} with value {self.initiate_value}")

    def sample(self, lower: float=-5.0, upper:float=5.0) -> None:
        """
        Sample a random value within the specified range.
        
        :param lower: The lower bound of the range (default: -5.0)
        :param upper: The upper bound of the range (default: 5.0)
        """
        return random.uniform(lower, upper)
    
    def run_simulation(self) -> None:
        """
        Run the simulation loop.
        """
        while self.running:
            with self.data_lock:
                current_time = datetime.utcnow()
                                
                change = self.sample()

                self.current_value += change

                # if len(self.sample_queue) == self.max_sample_queue - 5:
                #     self.sample_queue.popleft()

                # self.sample_queue.append(self.current_value)

                # self.stats.process()
                
                if self.initiate_value is not None:
                    self.max_delta = self.current_value - self.initiate_value

                payload = SampleData(
                    timestamp=current_time,
                    sim_id=self.sim_id,
                    value=self.current_value,
                    mark=self.initiate_value,
                    delta=self.max_delta
                )

                # payload.update(self.stats.get_updates())

                self.db_client.write(payload)

                time.sleep(self.sample_frequency)
