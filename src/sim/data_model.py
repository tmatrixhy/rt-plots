"""
Data Models
"""
# locals
from datetime import datetime
from typing import List, Optional

# third party
from sqlmodel import SQLModel, Field

class SampleData(SQLModel, table=True):
    timestamp: datetime = Field(default=datetime.utcnow, primary_key=True)
    sim_id: str = Field(foreign_key="simid.sim_id")
    value: float
    mark: Optional[float] = None
    delta: Optional[float] = None

class SimID(SQLModel, table=True):
    sim_id: str = Field(primary_key=True)
