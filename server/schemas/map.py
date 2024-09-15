from pydantic import BaseModel

class MapRequestSchema(BaseModel):
    corridor_color: str
    platform_position: str  # e.g., "left", "right", "front", "back"