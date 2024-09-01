"""
Calculate statistics of the simulation values.
"""
# locals
import logging
import itertools
from collections import deque

# project
# ..

# third party
# ..

# constants
logger = logging.getLogger(__name__)


class Statistics:
    def __init__(self, sample_periods:list, sample_queue: deque) -> None:
        """
        Initialize the Statistics class.

        Args:
            sample_periods (list): list of periods for calculating running average
            sample_queue (deque): A deque object containing the simulation values.
        """
        self.sample_queue = sample_queue
        self.sample_periods = sample_periods
        self.attr_init = False
        self._stat_attributes = {}

    def proc_calculate_running_avg(self, sample_size: int = 21) -> None:
        """
        Calculate the running average of the simulation values.

        Args:
            sample_size (int): The number of samples to consider for calculating the running average.

        Returns:
            float: The running average of the simulation values.
        """
        if len(self.sample_queue) < sample_size:
            running_avg = 0
            setattr(self, f"_s_running_avg_{sample_size}", running_avg)
            return

        summation = sum(itertools.islice(self.sample_queue, len(self.sample_queue) - sample_size, len(self.sample_queue) - 1))

        running_avg = summation / sample_size

        setattr(self, f"_s_running_avg_{sample_size}", running_avg)

    def proc_ema(self, sample_size:int=21, alpha:float=0.1) -> None:
        """
        Calculate exponential moving average
        """
        if len(self.sample_queue) < sample_size:
            ema = 0
            setattr(self, f"_s_ema_{sample_size}", ema)
            return

        sample = itertools.islice(self.sample_queue, len(self.sample_queue) - sample_size, len(self.sample_queue) - 1)
        ema = 1
        for x in sample:
            ema = alpha * x + (1 - alpha) * ema
        
        setattr(self, f"_s_ema_{sample_size}", ema)

    def process(self) -> dict:
        """
        Process the statistics by dynamically calling all methods 
        that start with 'proc_' and setting attributes that start with '_s_'.

        Get the updates of the statistics attributes.

        Returns:
            dict: A dictionary containing the updates of the statistics attributes.
        """
        for attr_name in dir(self):
            if attr_name.startswith('proc_calculate_running'):
                method = getattr(self, attr_name)
                if callable(method):
                    for x in self.sample_periods:
                        method(x)
            elif attr_name.startswith('proc_ema'):
                method = getattr(self, attr_name)
                if callable(method):
                    method(x)

        if not self.attr_init:
            self._stat_attributes = {
                attr_name[3:]: attr_name for attr_name in dir(self) if attr_name.startswith('_s_')}
            self.attr_init = True
        
        res = {}

        for key, attr_name in self._stat_attributes.items():
            res[key] = getattr(self, attr_name)

        return res
