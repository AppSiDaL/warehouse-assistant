from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from utils.serial import send_command
from fastapi import FastAPI, APIRouter
from fastapi.responses import StreamingResponse
import io
from autodrive.cv2test import capture_and_process_frame
import cv2
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

@app.get("/drive")
def get_frame():
    frame = capture_and_process_frame()
    
    # Encode the frame in JPEG format
    _, jpeg = cv2.imencode('.jpg', frame)
    return StreamingResponse(io.BytesIO(jpeg.tobytes()), media_type="image/jpeg")

# Run the FastAPI app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)