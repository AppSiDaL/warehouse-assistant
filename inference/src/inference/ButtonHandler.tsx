import { useState, useRef } from "react";
import { Webcam } from "../utils/webcam";

interface ButtonHandlerProps {
  imageRef: React.RefObject<HTMLImageElement>;
  cameraRef: React.RefObject<HTMLDivElement>;
  videoRef: React.RefObject<HTMLVideoElement>;
}

const ButtonHandler: React.FC<ButtonHandlerProps> = ({
  imageRef,
  cameraRef,
}) => {
  const [streaming, setStreaming] = useState<null | "camera" | "image">(null); // streaming state
  const inputImageRef = useRef<HTMLInputElement>(null); // video input reference
  const webcam = new Webcam(); // webcam handler

  // closing image
  const closeImage = () => {
    const url = imageRef?.current?.src;
    if (imageRef.current) {
      imageRef.current.src = "#"; // restore image source
      URL.revokeObjectURL(url ?? ""); // revoke url

      setStreaming(null); // set streaming to null
      if (inputImageRef.current) inputImageRef.current.value = ""; // reset input image
      imageRef.current.style.display = "none"; // hide image
    }
  };

  return (
    <div className="btn-container">
      {/* Webcam Handler */}
      <button
        onClick={() => {
          // if not streaming
          if (streaming === null || streaming === "image") {
            // closing image streaming
            if (streaming === "image") closeImage();
            webcam.open(cameraRef.current); // open webcam
            if (cameraRef.current) {
              cameraRef.current.style.display = "block"; // show camera
            }
            setStreaming("camera"); // set streaming to camera
          }
          // closing video streaming
          else if (streaming === "camera") {
            webcam.close(cameraRef.current);
            if (cameraRef.current) {
              cameraRef.current.style.display = "none";
            }
            setStreaming(null);
          } else
            alert(
              `Can't handle more than 1 stream\nCurrently streaming : ${streaming}`
            ); // if streaming video
        }}
      >
        {streaming === "camera" ? "Close" : "Open"} Webcam
      </button>
    </div>
  );
};

export default ButtonHandler;
