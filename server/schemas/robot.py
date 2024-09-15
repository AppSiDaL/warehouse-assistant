from typing import Optional
from pydantic import BaseModel, Field


class RobotResponseSchema(BaseModel):
    id: int = Field(..., description="Id of the robot")
    microcontroller: str = Field(..., description="Microcontroller of the robot")
    architecture: str = Field(..., description="Architecture of the robot")
    cpu_usage: Optional[int] = Field(..., description="CPU usage of the robot")
    ram_usage: Optional[int] = Field(..., description="RAM usage of the robot")
    storage_usage: Optional[int] = Field(..., description="Storage usage of the robot")
    location: Optional[str] = Field(..., description="Location of the robot")
    
    class Config:
        from_attributes = True
        orm_mode = True
        
class RobotRequestSchema(RobotResponseSchema):
    pass