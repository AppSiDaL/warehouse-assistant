from fastapi import APIRouter, Query, Depends, Body
from fastapi.responses import StreamingResponse, FileResponse, HTMLResponse
from utils.control import send_command
from utils.mapGenerator import generate_map_image, modify_map_image
import cv2
from cv.inference import run_inference
from models.robot import Robot
from sqlalchemy.orm import Session
from utils.dependencies import get_db
from schemas.robot import (
    RobotResponseSchema,
    RobotRequestSchema,
    OptionalRobotRequestSchema,
)
from schemas.map import MapRequestSchema
import os
from PIL import Image
from models.platform import Platform

router = APIRouter()
from cv.config import VIDEO_SOURCE, MODEL_PATH, OUTPUT_JSON

IMAGE_PATH = "static/generated_map.png"


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


@router.get("/status", response_model=RobotResponseSchema)
def status(db: Session = Depends(get_db)):
    robot = db.query(Robot).first()
    return robot


@router.post("/status", response_model=RobotResponseSchema)
def update_status(robot: RobotRequestSchema, db: Session = Depends(get_db)):
    db.query(Robot).update(robot.dict())
    db.commit()
    return robot


@router.get("/opencv_vision")
def video_feed1(video_source: int = 0, model_path: str = "path/to/your/model.pt"):
    return StreamingResponse(
        video_stream(video_source, model_path),
        media_type="multipart/x-mixed-replace; boundary=frame",
    )


def opencv_stream(video_source, model_path, output_json):
    for frame in run_inference(
        video_source, model_path, output_json, display=False, use_ocr=False
    ):
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


@router.post("/control/{command}")
async def control_car(command: str):
    return send_command(command)


@router.post("/generate_map_image")
def generate_map_image_endpoint(map_request: MapRequestSchema = Body(...)):
    # Crear el directorio si no existe
    os.makedirs(os.path.dirname(IMAGE_PATH), exist_ok=True)

    # Cargar la imagen existente si existe, de lo contrario crear una nueva
    if os.path.exists(IMAGE_PATH):
        img = Image.open(IMAGE_PATH)
        img = modify_map_image(
            img, map_request.corridor_color, map_request.platform_position
        )
    else:
        img = generate_map_image(
            map_request.corridor_color, map_request.platform_position
        )

    # Guardar la imagen en el servidor
    img.save(IMAGE_PATH, format="PNG")

    return {"message": "Image generated and saved successfully"}


@router.get("/get_map_image")
def get_map_image():
    """if os.path.exists(IMAGE_PATH):
        return FileResponse(IMAGE_PATH, media_type="image/png")
    else:
        return {"message": "Image not found"}"""
    img_path = "static/map.png"
    if os.path.exists(img_path):
        return FileResponse(img_path, media_type="image/png")
    else:
        return {"message": "Image not found"}


@router.put("/{id}")
def modify_robot(
    id: int, robot: OptionalRobotRequestSchema, db: Session = Depends(get_db)
):
    item = db.query(Robot).filter(Robot.id == id).first()
    if not robot:
        raise HTTPException(status_code=404, detail="Robot not found")
    item.location = robot.location
    db.commit()
    return item


@router.get("/get_location")
def get_location(db: Session = Depends(get_db)):
    robot = db.query(Robot).first()
    if robot and robot.location:
        platform = db.query(Platform).filter(Platform.code == robot.location).first()
        if platform:
            return {
                "robot_location": robot.location,
                "platform_position": platform.position,
            }
    return {"message": "Robot location or platform not found"}
