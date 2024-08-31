import cv2
import time

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
    cap2 = open_camera(2)

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