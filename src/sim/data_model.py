"""
Data Models
"""
# locals
import logging
from datetime import datetime
from typing import List, Optional, Dict

# third party
from pydantic import BaseModel
from sqlalchemy import Column
from sqlmodel import SQLModel, Field
from sqlalchemy.dialects.postgresql import JSON

logger = logging.getLogger(__name__)

class SampleData(SQLModel, table=True):
    timestamp: datetime = Field(default=datetime.utcnow, primary_key=True)
    sim_id: str = Field(foreign_key="simid.sim_id")
    value: float
    mark: Optional[float] = None
    delta: Optional[float] = None
    statistics: Optional[Dict[str, float]] = Field(default_factory=dict, sa_column=Column(JSON))

class SimID(SQLModel, table=True):
    sim_id: str = Field(primary_key=True)

class SimulationControlRequest(BaseModel):
    sim_id: str
    action: str
    additional_data: Optional[dict] = None
