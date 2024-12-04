from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import cv2
import time

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
camera2 = cv2.VideoCapture(1)

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


# Run the FastAPI app
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)