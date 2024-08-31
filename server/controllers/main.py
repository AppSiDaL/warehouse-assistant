from fastapi import APIRouter
from fastapi.responses import StreamingResponse, HTMLResponse
from utils.video import generate_frame
from utils.control import send_command

router = APIRouter()

@router.get('/video_feed1')
def video_feed1():
    return StreamingResponse(generate_frame(1),
                             media_type='multipart/x-mixed-replace; boundary=frame')

@router.get('/video_feed2')
def video_feed2():
    return StreamingResponse(generate_frame(2),
                             media_type='multipart/x-mixed-replace; boundary=frame')

@router.get('/', response_class=HTMLResponse)
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
            <img src="/video_feed1">
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

@router.post('/control/{command}')
async def control_car(command: str):
    return send_command(command)