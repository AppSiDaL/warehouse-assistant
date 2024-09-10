import cv2
import os


def extract_frames(video_path, output_path, interval):
    # Open the video file
    video = cv2.VideoCapture(video_path)

    # Get the frames per second (fps) of the video
    fps = video.get(cv2.CAP_PROP_FPS)

    # Calculate the frame interval based on the desired interval (frames per second)
    frame_interval = int(fps / interval)

    # Initialize variables
    frame_count = 0
    success = True

    # Ensure the output directory exists
    os.makedirs(output_path, exist_ok=True)

    while success:
        # Read the next frame from the video
        success, frame = video.read()

        if not success:
            break

        # Check if the current frame number is a multiple of the frame interval
        if frame_count % frame_interval == 0:
            # Save the frame as an image file
            cv2.imwrite(f"{output_path}/frame_{frame_count}.jpg", frame)

        # Increment the frame count
        frame_count += 1

    # Release the video file
    video.release()


import os
import shutil


def combine_files(source_dirs, output_dir):
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    for idx, source_dir in enumerate(source_dirs, start=1):
        file_count = 1
        prefix = f"video{idx}_"

        # List all files in the source directory
        files = sorted(os.listdir(source_dir))

        for file in files:
            # Construct the full file path
            file_path = os.path.join(source_dir, file)

            # Check if it's a file
            if os.path.isfile(file_path):
                # Get the file extension
                file_extension = os.path.splitext(file)[1]

                # Construct the new file name
                new_file_name = f"{prefix}{file_count:05d}{file_extension}"
                new_file_path = os.path.join(output_dir, new_file_name)

                # Copy the file to the new location with the new name
                shutil.copy(file_path, new_file_path)

                # Increment the file count
                file_count += 1


if __name__ == "__main__":
    # Example usage
    video_path = (
        "/Users/gilbertodavalosnava/Documents/AppSiDaL/warehouse-assistant/server/box2.MOV"
    )
    output_path = (
        "/Users/gilbertodavalosnava/Documents/AppSiDaL/warehouse-assistant/server/box2"
    )
    interval = 5  # Extract 2 frames per second

    extract_frames(video_path, output_path, interval)
#   source_dirs = [
#      "/Users/gilbertodavalosnava/Documents/AppSiDaL/warehouse-assistant/server/1",
#     "/Users/gilbertodavalosnava/Documents/AppSiDaL/warehouse-assistant/server/2",
#      "/Users/gilbertodavalosnava/Documents/AppSiDaL/warehouse-assistant/server/3",
#      "/Users/gilbertodavalosnava/Documents/AppSiDaL/warehouse-assistant/server/4"
#  ]
# output_dir = "/Users/gilbertodavalosnava/Documents/AppSiDaL/warehouse-assistant/server/frames"

# combine_files(source_dirs, output_dir)
