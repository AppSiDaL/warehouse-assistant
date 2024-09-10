from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse, HTMLResponse
from utils.control import send_command
import cv2
from cv.inference import run_inference

router = APIRouter()
from cv.config import VIDEO_SOURCE, MODEL_PATH, OUTPUT_JSON


def video_stream(video_source, model_path):
    cap = cv2.VideoCapture(video_source)
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        ret, jpeg = cv2.imencode(".jpg", frame)
        if ret:
            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" + jpeg.tobytes() + b"\r\n\r\n"
            )


@router.get("/opencv_vision")
def video_feed1(video_source: int = 0, model_path: str = "path/to/your/model.pt"):
    return StreamingResponse(
        video_stream(video_source, model_path),
        media_type="multipart/x-mixed-replace; boundary=frame",
    )


def opencv_stream(video_source, model_path, output_json):
    for frame in run_inference(video_source, model_path, output_json, display=False):
        yield (b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n\r\n")


@router.get("/run_inference")
def run_inference_endpoint(
    video_source: int = Query(VIDEO_SOURCE),
    model_path: str = Query(MODEL_PATH),
    output_json: str = Query(OUTPUT_JSON),
):
    return StreamingResponse(
        opencv_stream(video_source, model_path, output_json),
        media_type="multipart/x-mixed-replace; boundary=frame",
    )


@router.get("/", response_class=HTMLResponse)
async def read_items():
    html_content = """
    <html>
        <head>
            <title>Video Streaming</title>
            <script>
                function sendCommand(command) {
                    fetch('/control/' + command, { method: 'POST' });
                }
            </script>
        </head>
        <body>
            <h1>Camera 1</h1>
            <img src="/opencv_vision">
            <h1>Camera 2</h1>
            <img src="/video_feed2">
            <h1>Control</h1>
            <button onclick="sendCommand('forward')">Forward</button>
            <button onclick="sendCommand('backward')">Backward</button>
            <button onclick="sendCommand('left')">Left</button>
            <button onclick="sendCommand('right')">Right</button>
            <button onclick="sendCommand('stop')">Stop</button>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)


@router.post("/control/{command}")
async def control_car(command: str):
    return send_command(command)
