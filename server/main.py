import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager
from controllers import items
from controllers import platforms, robots
from utils.db import engine, Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Application startup")
    Base.metadata.create_all(bind=engine)

    yield
    print("Application shutdown")


app = FastAPI(lifespan=lifespan)
app.include_router(robots.router, prefix="/api/robot")
app.include_router(items.itemsRouter, prefix="/api/items")
app.include_router(platforms.platformsRouter, prefix="/api/platforms")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
