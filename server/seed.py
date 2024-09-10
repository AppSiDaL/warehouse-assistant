from sqlalchemy import create_engine
from models.items import Item
from utils.db import SessionLocal, engine, Base
import json

Base.metadata.create_all(bind=engine)

db_session = SessionLocal()

with open("seeders/items.json") as f:
    items_data = json.load(f)
    db_session = SessionLocal()
    items = [
        Item(
            code=item["code"],
            brand=item["brand"],
            isBox=item["isBox"],
            description=item["description"],
            dimension=item["dimension"],
            quantity=item["quantity"],
            price=item["price"]
        )
        for item in items_data
    ]
    db_session.bulk_save_objects(items)
    db_session.commit()

db_session.close()