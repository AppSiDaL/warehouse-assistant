from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional, Dict, Any
from schemas.item import ItemResponseSchema, ItemRequestSchema
from sqlalchemy.orm import Session
from utils.dependencies import get_db
from models.item import Item
from models.platform import Platform  # Importar el modelo Platform
from sqlalchemy import func
itemsRouter = APIRouter()

previous_total_quantity = 500


@itemsRouter.get("/", response_model=Dict[str, Any])
async def read_classes(modelId: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(Item)
    items = query.all()

    # Sumar todas las items_count del modelo Platform
    total_quantity = db.query(Platform).with_entities(func.sum(Platform.items_count)).scalar() or 0

    # Calcular el crecimiento
    growth = (
        (total_quantity - previous_total_quantity) / previous_total_quantity
    ) * 100

    # Convertir los objetos Item a diccionarios usando Pydantic
    items_dict = [ItemResponseSchema.from_orm(item).dict() for item in items]

    return {"items": items_dict, "total_quantity": total_quantity, "growth": growth}


@itemsRouter.get("/{id}", response_model=ItemResponseSchema)
async def read_class(id: str, db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.code == str(id)).first()
    if not item:
        raise HTTPException(status_code=404, detail="Class not found")
    return item


@itemsRouter.put("/add/{id}", response_model=ItemResponseSchema)
async def add_class(id: str, db: Session = Depends(get_db), total_boxes: int = None):
    item = db.query(Item).filter(Item.code == str(id)).first()
    if not item:
        raise HTTPException(status_code=404, detail="Class not found")
    item.quantity += total_boxes
    db.commit()
    db.refresh(item)
    return item


@itemsRouter.post("/", response_model=ItemResponseSchema)
async def create_class(
    item: ItemRequestSchema,
    db: Session = Depends(get_db),
):
    newItem = Item(
        code=item.code,
        brand=item.brand,
        isBox=item.isBox,
        description=item.description,
        dimension=item.dimension,
        quantity=item.quantity,
        price=item.price,
    )
    db.add(newItem)
    db.commit()
    db.refresh(newItem)
    return newItem


@itemsRouter.put("/{id}", response_model=ItemResponseSchema)
async def update_class(
    id: str,
    classe: ItemRequestSchema,
    db: Session = Depends(get_db),
):
    existing_class = db.query(Item).filter(Item.id == int(id)).first()
    if not existing_class:
        raise HTTPException(status_code=404, detail="Class not found")

    existing_class.name = classe.name
    existing_class.images_number = classe.images_number
    existing_class.modelId = classe.modelId

    db.commit()
    db.refresh(existing_class)
    return existing_class


@itemsRouter.delete("/all", response_model=dict)
async def delete_classes(db: Session = Depends(get_db)):
    db.query(Item).delete()
    db.commit()

    return {"detail": "All classes deleted successfully"}