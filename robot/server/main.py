from utils.serial import send_command
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/control/{command}")
async def control_car(command: str):
    return send_command(command)