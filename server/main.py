import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from controllers import items, platforms, robots
from utils.db import engine, Base

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Application startup")
    Base.metadata.create_all(bind=engine)

    yield
    print("Application shutdown")

app = FastAPI(lifespan=lifespan)

# Configuración de CORS
origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://localhost:3000",  # Añade aquí las URLs de tus frontends
    "http://your-frontend-domain.com",
    "http://localhost:4321",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Permitir estos orígenes
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos los métodos
    allow_headers=["*"],  # Permitir todos los headers
)

app.include_router(robots.router, prefix="/api/robot")
app.include_router(items.itemsRouter, prefix="/api/items")
app.include_router(platforms.platformsRouter, prefix="/api/platforms")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)