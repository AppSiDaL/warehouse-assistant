from pydantic import BaseModel, Field
from typing import Optional

class PlatformResponseSchema(BaseModel):
    code: str = Field(..., description="Code of the platform")
    items_type: Optional[str] = Field(None, description="Type of items in the platform")
    items_count: Optional[int] = Field(None, description="Number of items in the platform")
    dimension: str = Field(..., description="Dimension of the platform")
    position: str = Field(..., description="Position of the platform")
    class Config:
        from_attributes = True
        orm_mode = True
        
class PlatformRequestSchema(PlatformResponseSchema):
    pass


class OptionalPlatformResponseSchema(BaseModel):
    code: Optional[str] = Field(None, description="Code of the platform")
    items_type: Optional[str] = Field(None, description="Type of items in the platform")
    items_count: Optional[int] = Field(None, description="Number of items in the platform")
    dimension: Optional[str] = Field(None, description="Dimension of the platform")
    position: Optional[str] = Field(None, description="Position of the platform")
    class Config:
        from_attributes = True
        orm_mode = True