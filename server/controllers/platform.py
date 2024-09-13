from models.platforms import Platform
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional, Dict, Any
from schemas.platform import PlatformResponseSchema, PlatformRequestSchema,OptionalPlatformResponseSchema
from sqlalchemy.orm import Session
from utils.dependencies import get_db

platformsRouter = APIRouter()


@platformsRouter.get("/", response_model=List[PlatformResponseSchema])
async def read_all_classes(db: Session = Depends(get_db)):
    items = db.query(Platform).all()
    return items

@platformsRouter.get("/{id}", response_model=PlatformResponseSchema)
async def read_class(id: str, db: Session = Depends(get_db)):
    item = db.query(Platform).filter(Platform.code == str(id)).first()
    if not item:
        raise HTTPException(status_code=404, detail="Class not found")
    return item

@platformsRouter.put("/{id}", response_model=PlatformResponseSchema)
async def update_class(id: str, platform: OptionalPlatformResponseSchema, db: Session = Depends(get_db)):
    item = db.query(Platform).filter(Platform.code == str(id)).first()
    if not item:
        raise HTTPException(status_code=404, detail="Class not found")
    item.items_count = platform.items_count
    item.items_type = platform.items_type
    db.commit()
    return item
