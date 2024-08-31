import cv2
import threading
import time
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import uvicorn

app = FastAPI()

# Variables globales para almacenar los cuadros de las cámaras
frame1 = None
frame2 = None

def open_camera(camera_index):
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        print(f"Error: No se puede abrir la cámara {camera_index}")
        return None
    return cap

def capture_frames():
    global frame1, frame2
    cap1 = open_camera(0)
    cap2 = open_camera(1)

    if cap1 is None or cap2 is None:
        return

    while cap1.isOpened() and cap2.isOpened():
        ret1, frame1 = cap1.read()
        ret2, frame2 = cap2.read()

        if not ret1:
            print("Error: No se puede leer el cuadro de la cámara 1")
            break
        if not ret2:
            print("Error: No se puede leer el cuadro de la cámara 2")
            break

        time.sleep(0.03)  # Ajusta según la tasa de cuadros deseada

    cap1.release()
    cap2.release()

def generate_frame(camera):
    global frame1, frame2
    while True:
        if camera == 1:
            if frame1 is not None:
                ret, jpeg = cv2.imencode('.jpg', frame1)
                if ret:
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')
        elif camera == 2:
            if frame2 is not None:
                ret, jpeg = cv2.imencode('.jpg', frame2)
                if ret:
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')

@app.get('/video_feed1')
def video_feed1():
    return StreamingResponse(generate_frame(1),
                             media_type='multipart/x-mixed-replace; boundary=frame')

@app.get('/video_feed2')
def video_feed2():
    return StreamingResponse(generate_frame(2),
                             media_type='multipart/x-mixed-replace; boundary=frame')

@app.get('/')
def index():
    return '''
    <html>
        <head>
            <title>Video Streaming</title>
        </head>
        <body>
            <h1>Camera 1</h1>
            <img src="/video_feed1">
            <h1>Camera 2</h1>
            <img src="/video_feed2">
        </body>
    </html>
    '''

if __name__ == '__main__':
    # Inicia el hilo de captura de cuadros
    t = threading.Thread(target=capture_frames)
    t.daemon = True
    t.start()

    # Inicia el servidor FastAPI
    uvicorn.run(app, host='0.0.0.0', port=8000)