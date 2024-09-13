from sqlalchemy import Column, Integer, String, Boolean
from utils.db import Base
from sqlalchemy.orm import relationship


class Item(Base):
    __tablename__ = "items"

    code = Column(String(255), primary_key=True)
    brand = Column(String(255))
    description = Column(String(255))
    isBox = Column(Boolean)
    dimension = Column(String(255))
    price = Column(Integer)

    platforms = relationship("Platform", back_populates="items")
