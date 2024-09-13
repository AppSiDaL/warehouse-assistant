from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from utils.db import Base


class Robot(Base):
    __tablename__ = "robots"

    id = Column(Integer, primary_key=True)
    microcontroller = Column(String(255))
    architecture = Column(String(255))
    cpu_usage = Column(Integer,nullable=True)
    ram_usage = Column(Integer,nullable=True)
    storage_usage = Column(Integer,nullable=True)
    location= Column(String(255), ForeignKey('platforms.code'), nullable=True)
    
    platforms = relationship("Platform", back_populates="robots")