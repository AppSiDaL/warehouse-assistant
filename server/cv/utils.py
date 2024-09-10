import cv2
from pyzbar import pyzbar
import json

# Known parameters
KNOWN_WIDTH = 0.5  # Example: known width of the object in meters
FOCAL_LENGTH = 800  # Example: focal length of the camera in pixels
AVERAGE_BOX_DEPTH = 0.5  # Example: average depth of a box in meters
PALLET_DEPTH = 2.0  # Example: depth of the pallet in meters


def estimate_distance(known_width, focal_length, pixel_width):
    return (known_width * focal_length) / pixel_width


def draw_polygon(frame, polygon):
    cv2.polylines(frame, [polygon], isClosed=True, color=(0, 255, 0), thickness=2)


def draw_text(
    frame, text, position, font_scale=0.5, color=(255, 255, 255), thickness=2
):
    (text_width, text_height), baseline = cv2.getTextSize(
        text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness
    )
    cv2.rectangle(
        frame,
        (position[0], position[1] - text_height - 10),
        (position[0] + text_width, position[1]),
        (0, 0, 0),
        -1,
    )
    cv2.putText(
        frame,
        text,
        (position[0], position[1] - 5),
        cv2.FONT_HERSHEY_SIMPLEX,
        font_scale,
        color,
        thickness,
    )


def estimate_box_count(distances, average_box_depth, pallet_depth, current_count):
    if not distances:
        return 0
    closest_distance = min(distances)
    num_boxes_in_depth = int(pallet_depth / average_box_depth)
    return num_boxes_in_depth * current_count


def process_detections(frame, detections, polygon_zone, plataform_data, qr):
    distances = []
    for i in range(len(detections.xyxy)):
        box_x1, box_y1, box_x2, box_y2 = detections.xyxy[i]
        box_width = box_x2 - box_x1
        distance = estimate_distance(KNOWN_WIDTH, FOCAL_LENGTH, box_width)
        distances.append(distance)

        # Draw a filled rectangle as background for the text
        text = f"Dist: {distance:.2f}m"
        (text_width, text_height), baseline = cv2.getTextSize(
            text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2
        )
        cv2.rectangle(
            frame,
            (int(box_x1), int(box_y1) - text_height - 10),
            (int(box_x1) + text_width, int(box_y1)),
            (0, 0, 0),
            -1,
        )

        # Put the distance text on the frame
        cv2.putText(
            frame,
            text,
            (int(box_x1), int(box_y1) - 5),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2,
        )

        # Draw tracker ID for class 1 (platform)
        if detections.class_id[i] == 1 and i < len(detections.tracker_id):
            platform_id = str(detections.tracker_id[i])
            current_count = polygon_zone.current_count
            type = plataform_data[platform_id]["type"] if platform_id in plataform_data else ""
            if qr:
                type = qr[0].data.decode("utf-8")
            # Update platform data and save type
            if platform_id in plataform_data:
                plataform_data[platform_id]["type"] = type
                if current_count > plataform_data[platform_id]["visible_boxes"]:
                    plataform_data[platform_id]["visible_boxes"] = current_count
            else:
                plataform_data[platform_id] = {
                    "visible_boxes": current_count,
                    "total_boxes": 0,
                    "type": type,
                }

            draw_text(
                frame,
                f"ID: {detections.tracker_id[i]}",
                (int(box_x1), int(box_y1) - text_height - 30),
                font_scale=0.7,
            )

    # Estimate the number of boxes on the platform
    if distances:
        for platform_id in plataform_data:
            box_count = estimate_box_count(
                distances,
                AVERAGE_BOX_DEPTH,
                PALLET_DEPTH,
                plataform_data[platform_id]["visible_boxes"],
            )
            plataform_data[platform_id]["total_boxes"] = box_count
            draw_text(
                frame,
                f"Estimated boxes: {box_count}",
                (10, 120),
                font_scale=1,
                color=(0, 255, 0),
            )


def scan_qr_codes(frame):
    qrcodes = pyzbar.decode(frame)
    for qrcode in qrcodes:
        (x, y, w, h) = qrcode.rect
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
        qrcode_data = qrcode.data.decode("utf-8")
        qrcode_type = qrcode.type
        text = f"{qrcode_data} ({qrcode_type})"
        draw_text(frame, text, (x, y - 10), font_scale=0.5, color=(0, 0, 255))
    return qrcodes


def save_data_to_json(plataform_data, output_json):
    with open(output_json, "w") as f:
        json.dump(plataform_data, f, indent=4)
