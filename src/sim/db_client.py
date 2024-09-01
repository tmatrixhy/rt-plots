"""
DB Client
"""
# locals
import queue
import logging
from typing import Union

# project
from src.sim.data_model import SampleData, SimID
from src.sim.config import DATABASE_URL

# third party
from sqlmodel import create_engine, SQLModel, Session

# constants
logger = logging.getLogger(__name__)


class DatabaseClient:
    """
    A database client that manages buffered writes to a database using SQLAlchemy and SQLModel.

    The client maintains multiple buffers to handle high-throughput data writes efficiently.
    Data can be written either immediately or buffered and committed in bulk when the buffer
    reaches its limit. The buffers are flushed either when they are full or when the client is closed.
    """
    def __init__(self, num_buffers:int=3, buffer_limit:int=500) -> None:
        self.engine = create_engine(
            DATABASE_URL,
            echo=False,  # Set to True for debugging SQL statements
            pool_pre_ping=True,  # Use pre-ping to avoid stale connections in the pool
            pool_size=10,  # Default pool size
            max_overflow=20  # Overflow size of the pool
        )
        SQLModel.metadata.create_all(self.engine)
        self.buffer_limit = buffer_limit  # Maximum size of each buffer
        self.num_buffers = num_buffers  # Number of buffers to use
        self.buffers = [queue.Queue() for _ in range(num_buffers)]
        self.current_buffer = 0  # Index of the current buffer to use

    def write(self, 
        sample_data: Union[SampleData, SimID], immediate_commit:bool=False) -> None:
        """
        Writes data to the database, either immediately 
            or by adding it to a buffer for bulk processing.
        """
        if immediate_commit:
            with Session(self.engine) as session:
                session.add(sample_data)
                session.commit()
            return

        # add item to buffer
        self.buffers[self.current_buffer].put(sample_data)
        
        # check if item caused buffer overflow and flush if so
        if self.buffers[self.current_buffer].qsize() >= self.buffer_limit:
            self.flush_buffer(self.current_buffer)
            self.current_buffer = (self.current_buffer + 1) % self.num_buffers

    def flush_buffer(self, index:int) -> None:
        """
        Flushes the buffer at the specified index by writing 
            its contents to the database.
        """
        with Session(self.engine) as session:
            items = []
            while not self.buffers[index].empty():
                items.append(self.buffers[index].get())
            
            session.bulk_save_objects(items)
            session.commit()

    def close(self) -> None:
        self.engine.dispose()
