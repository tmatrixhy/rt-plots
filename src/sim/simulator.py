"""
This module contains the MonteCarloSimulation class for running a Monte Carlo simulation.
"""
# locals
import time
import random
import logging
import threading

# third party
from flask_socketio import SocketIO, emit

logger = logging.getLogger(__name__)

class MonteCarloSimulation:
    """
    Class representing a Monte Carlo simulation.

    Args:
        sim_id (str): Unique ID for the simulation.
        socketio (SocketIO): SocketIO instance for emitting data.
        sample_hz (int): Frequency of data sampling in Hz.

    Attributes:
        sim_id (str): Unique ID for the simulation.
        socketio (SocketIO): SocketIO instance for emitting data.
        current_value (float): Current value of the simulation.
        initiate_value (float): Initial value of the simulation.
        max_delta (float): Maximum change in value since initiation.
        running (bool): Flag indicating if the simulation is running.
        thread (Thread): Thread object for running the simulation.
        data_lock (Lock): Lock for thread-safe access to data.
        start_time (float): Start time of the simulation.
        sleep_frequency (float): Time interval between data samples in seconds.
    """

    def __init__(self, sim_id: str, socketio: SocketIO, sample_hz:int=10) -> None:
        self.sim_id = sim_id
        self.socketio = socketio
        self.current_value = 0
        self.initiate_value = None
        self.max_delta = 0
        self.running = False
        self.thread = None
        self.data_lock = threading.Lock()
        self.start_time = time.time()
        self.sleep_frequency = 1 / sample_hz # hertz to seconds

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

    def run_simulation(self) -> None:
        """
        Run the simulation loop.
        """
        while self.running:
            with self.data_lock:
                current_time = time.time() - self.start_time
                change = random.uniform(-5, 5)
                self.current_value += change

                if self.initiate_value is not None:
                    self.max_delta = self.current_value - self.initiate_value

            self.socketio.emit('new_data', {
                'sim_id': self.sim_id,
                'x': current_time,
                'y': self.current_value,
                'initiate_value': self.initiate_value,
                'max_delta': self.max_delta,
            })

            time.sleep(self.sleep_frequency)
