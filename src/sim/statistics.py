"""
This module contains the Statistics class that is responsible for calculating the statistics of the simulation values.
"""
# locals
import logging
import itertools
from collections import deque

logger = logging.getLogger(__name__)


class Statistics:
    def __init__(self, sample_queue: deque):
        """
        Initialize the Statistics class.

        Args:
            sample_queue (deque): A deque object containing the simulation values.
        """
        self.sample_queue = sample_queue
        self.attr_init = False
        self._stat_attributes = {}

    def proc_calculate_running_avg(self, sample_size: int = 21) -> float:
        """
        Calculate the running average of the simulation values.

        Args:
            sample_size (int): The number of samples to consider for calculating the running average.

        Returns:
            float: The running average of the simulation values.
        """
        if len(self.sample_queue) < sample_size:
            self._s_running_avg = 0
            return

        summation = sum(itertools.islice(self.sample_queue, len(self.sample_queue) - sample_size, len(self.sample_queue) - 1))

        self._s_running_avg = summation / sample_size

    def process(self):
        """
        Process the statistics by dynamically calling all methods 
        that start with 'proc_' and setting attributes that start with '_s_'.
        """
        for attr_name in dir(self):
            if attr_name.startswith('proc_'):
                method = getattr(self, attr_name)
                if callable(method):
                    method()

        if not self.attr_init:
            self._stat_attributes = {
                attr_name[3:]: attr_name for attr_name in dir(self) if attr_name.startswith('_s_')}
            self.attr_init = True

    def get_updates(self):
        """
        Get the updates of the statistics attributes.

        Returns:
            dict: A dictionary containing the updates of the statistics attributes.
        """
        res = {}
        for key, attr_name in self._stat_attributes.items():
            res[key] = getattr(self, attr_name)
        return res
