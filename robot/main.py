from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import cv2
import time
from autodrive.serialcom import send_command

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Open the two cameras
camera1 = cv2.VideoCapture(0)
camera2 = cv2.VideoCapture(10)

# Allow the cameras to warmup
time.sleep(0.1)


def generate_frames(camera):
    while True:
        ret, frame = camera.read()
        if not ret:
            break
        _, jpeg = cv2.imencode(".jpg", frame)
        frame = jpeg.tobytes()
        yield (b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")
        time.sleep(0.1)  # Adjust the sleep time as needed


@app.get("/cam1")
def get_frame_camera1():
    return StreamingResponse(
        generate_frames(camera1), media_type="multipart/x-mixed-replace; boundary=frame"
    )


@app.get("/cam2")
def get_frame_camera2():
    return StreamingResponse(
        generate_frames(camera2), media_type="multipart/x-mixed-replace; boundary=frame"
    )


import os


@app.get("/start")
def get_current_command():
    send_command("start")
    return {"status": "success", "command": "start"}


# Run the FastAPI app
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)


#python autodrive/main.py --labels-json resources/path-labels.json --hef resources/path2.hef --input rpi