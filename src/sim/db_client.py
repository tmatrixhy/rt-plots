"""
DB Client
"""
# locals
import logging

# third party
from sqlmodel import create_engine, SQLModel, Session

# project
from src.sim.data_model import SampleData
from src.sim.config import DATABASE_URL


class DatabaseClient:
    def __init__(self):
        self.engine = create_engine(
            DATABASE_URL,
            echo=False,  # Set to True for debugging SQL statements
            pool_pre_ping=True,  # Use pre-ping to avoid stale connections in the pool
            pool_size=10,  # Default pool size
            max_overflow=20  # Overflow size of the pool
        )
        SQLModel.metadata.create_all(self.engine)

    def write(self, sample_data: SampleData):
        with Session(self.engine) as session:
            session.add(sample_data)
            session.commit()
            logging.debug("Data inserted successfully.")
