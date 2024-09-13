from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from utils.db import Base


class Platform(Base):
    __tablename__ = "platforms"

    code = Column(String(255), primary_key=True)
    items_type = Column(String(255), ForeignKey('items.code'), nullable=True)
    items_count = Column(Integer, nullable=True)
    dimension = Column(String(255))
    position = Column(String(255))
    
    items = relationship("Item", back_populates="platforms")
    robots = relationship("Robot", back_populates="platforms")