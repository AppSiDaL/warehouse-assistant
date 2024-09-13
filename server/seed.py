
from sqlalchemy import create_engine, text
from models.items import Item
from models.platforms import Platform
from utils.db import SessionLocal, engine, Base
import json

Base.metadata.create_all(bind=engine)

db_session = SessionLocal()

# Truncate the items table for SQLite
db_session.execute(text("DELETE FROM items;"))
db_session.commit()

with open("seeders/items.json") as f:
    items_data = json.load(f)
    items = [
        Item(
            code=item["code"],
            brand=item["brand"],
            isBox=item["isBox"],
            description=item["description"],
            dimension=item["dimension"],
            price=item["price"]
        )
        for item in items_data
    ]
    db_session.bulk_save_objects(items)
    db_session.commit()

with open("seeders/platforms.json") as f:
    platforms_data = json.load(f)
    platforms = [
        Platform(
            code=platform["code"],
            items_count=platform["items_count"],
            dimension=platform["dimension"]
        )
        for platform in platforms_data
    ]
    db_session.bulk_save_objects(platforms)
    db_session.commit()
db_session.close()