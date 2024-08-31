import threading
import uvicorn
from fastapi import FastAPI
from utils.video import capture_frames
from controllers.main import router

app = FastAPI()
app.include_router(router)

if __name__ == '__main__':
    # Inicia el hilo de captura de cuadros
    t = threading.Thread(target=capture_frames)
    t.daemon = True
    t.start()

    # Inicia el servidor FastAPI
    uvicorn.run(app, host='0.0.0.0', port=8000)