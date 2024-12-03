import React, { useState, useEffect, useRef } from "react";
import * as tf from "@tensorflow/tfjs";
import "@tensorflow/tfjs-backend-webgl"; // set backend to webgl
import Loader from "./Loader";
import ButtonHandler from "./ButtonHandler";
import { detect, detectVideo } from "../utils/detect";
import "./App.css";


export default function InferenceComponent() {
    const [loading, setLoading] = useState({ loading: true, progress: 0 }); // loading state
    const [model, setModel] = useState({
      net: null,
      inputShape: [1, 0, 0, 3],
    }); // init model & input shape
  
    // references
    const imageRef = useRef(null);
    const cameraRef = useRef(null);
    const videoRef = useRef(null);
    const canvasRef = useRef(null);
  
    // model configs
    const modelName = "products";

    useEffect(() => {
      const modelPath= `${window.location.href}/${modelName}_web_model/model.json`;
      console.log(modelPath)
      tf.ready().then(async () => {
        const yolov8 = await tf.loadGraphModel(
          modelPath,
          {
            onProgress: (fractions) => {
              setLoading({ loading: true, progress: fractions }); // set loading fractions
            },
          }
        ); // load model
  
        // warming up model
        const dummyInput = tf.ones(yolov8.inputs[0].shape);
        const warmupResults = yolov8.execute(dummyInput);
  
        setLoading({ loading: false, progress: 1 });
        setModel({
          net: yolov8,
          inputShape: yolov8.inputs[0].shape,
        }); // set model & input shape
  
        tf.dispose([warmupResults, dummyInput]); // cleanup memory
      });
    }, []);
  
    return (
      <div className="App">
        {loading.loading && <Loader>Loading model... {(loading.progress * 100).toFixed(2)}%</Loader>}
        <div className="header">
          <p>
            Serving : <code className="code">{modelName}</code>
          </p>
        </div>
  
        <div className="content">
          <video
            autoPlay
            muted
            ref={cameraRef}
            onPlay={() => detectVideo(cameraRef.current, model, canvasRef.current)}
          />
          <canvas width={model.inputShape[1]} height={model.inputShape[2]} ref={canvasRef} />
        </div>
  
        <ButtonHandler imageRef={imageRef} cameraRef={cameraRef} videoRef={videoRef} />
      </div>
    );
}

