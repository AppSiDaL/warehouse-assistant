from sqlalchemy import Column, Integer, String, Boolean
from utils.db import Base


class Item(Base):
    __tablename__ = "items"

    code = Column(String(255), primary_key=True)
    brand = Column(String(255))
    description = Column(String(255))
    isBox = Column(Boolean)
    dimension = Column(String(255))
    quantity = Column(Integer)
    price = Column(Integer)
