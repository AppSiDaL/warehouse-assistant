from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from utils.serial import send_command

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir cualquier origen
    allow_credentials=True,
    allow_methods=["*"],  # Permitir cualquier método
    allow_headers=["*"],  # Permitir cualquier encabezado
)

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/control/{command}")
async def control_car(command: str):
    return send_command(command)