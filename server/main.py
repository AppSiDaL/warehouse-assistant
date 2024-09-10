import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager
from controllers import robot, items
from utils.db import engine, Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Application startup")
    Base.metadata.create_all(bind=engine)

    yield
    print("Application shutdown")


app = FastAPI(lifespan=lifespan)
app.include_router(robot.router, prefix="/api/robot")
app.include_router(items.itemsRouter, prefix="/api/items")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
