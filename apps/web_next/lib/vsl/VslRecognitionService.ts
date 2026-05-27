import * as tf from '@tensorflow/tfjs';
import { FilesetResolver, HandLandmarker, HandLandmarkerResult } from '@mediapipe/tasks-vision';

export const VSL_CLASSES = ["dau", "dau_dau", "bung", "sot", "ho", "kho_tho", "chong_mat", "thuoc", "bac_si", "khan_cap"];
export const VSL_LABELS: Record<string, string> = {
  "dau": "Đau",
  "dau_dau": "Đau đầu", 
  "bung": "Bụng",
  "sot": "Sốt",
  "ho": "Ho",
  "kho_tho": "Khó thở",
  "chong_mat": "Chóng mặt",
  "thuoc": "Thuốc",
  "bac_si": "Bác sĩ",
  "khan_cap": "Khẩn cấp"
};

export class VslRecognitionService {
  private videoElement: HTMLVideoElement | null = null;
  private canvasElement: HTMLCanvasElement | null = null;
  private handLandmarker: HandLandmarker | null = null;
  private model: tf.LayersModel | null = null;
  private isProcessing = false;
  private landmarkBuffer: number[][] = [];
  private onResultCallback: ((label: string, confidence: number) => void) | null = null;
  private inferenceIntervalId: any = null;
  private animationFrameId: number | null = null;
  private predictionWindow: Array<{ classCode: string; confidence: number; margin: number }> = [];
  private lastEmittedClassCode: string | null = null;
  private lastEmittedAt = 0;

  async init(videoElement: HTMLVideoElement, canvasElement?: HTMLCanvasElement): Promise<void> {
    this.videoElement = videoElement;
    if (canvasElement) {
      this.canvasElement = canvasElement;
    }

    try {
      // 1. Initialize TensorFlow.js
      await tf.ready();
      console.log("TensorFlow.js ready.");

      // 2. Build the Bi-LSTM model and load exported Keras weights.
      this.model = await this.buildAndLoadModel();
      console.log("VSL TF.js model loaded successfully.");

      // 3. Initialize MediaPipe HandLandmarker
      const vision = await FilesetResolver.forVisionTasks(
        "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@latest/wasm"
      );
      this.handLandmarker = await HandLandmarker.createFromOptions(vision, {
        baseOptions: {
          modelAssetPath: "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task",
          delegate: "GPU"
        },
        runningMode: "VIDEO",
        numHands: 2
      });
      console.log("MediaPipe HandLandmarker initialized successfully.");
    } catch (error) {
      console.error("Failed to initialize VslRecognitionService:", error);
      throw error;
    }
  }

  private async buildAndLoadModel(): Promise<tf.LayersModel> {
    const model = tf.sequential();
    model.add(tf.layers.inputLayer({ inputShape: [30, 126], name: "hand_landmarks_sequence" }));
    model.add(tf.layers.bidirectional({
      layer: tf.layers.lstm({ units: 64, returnSequences: true, name: "forward_lstm" }),
      backwardLayer: tf.layers.lstm({ units: 64, returnSequences: true, goBackwards: true, name: "backward_lstm" }),
      name: "bidirectional"
    } as any));
    model.add(tf.layers.batchNormalization({ name: "batch_normalization" }));
    model.add(tf.layers.dropout({ rate: 0.3, name: "dropout" }));
    model.add(tf.layers.bidirectional({
      layer: tf.layers.lstm({ units: 32, returnSequences: false, name: "forward_lstm_1" }),
      backwardLayer: tf.layers.lstm({ units: 32, returnSequences: false, goBackwards: true, name: "backward_lstm_1" }),
      name: "bidirectional_1"
    } as any));
    model.add(tf.layers.batchNormalization({ name: "batch_normalization_1" }));
    model.add(tf.layers.dropout({ rate: 0.3, name: "dropout_1" }));
    model.add(tf.layers.dense({ units: 32, activation: "relu", name: "dense" }));
    model.add(tf.layers.dropout({ rate: 0.2, name: "dropout_2" }));
    model.add(tf.layers.dense({ units: VSL_CLASSES.length, activation: "softmax", name: "output_gesture" }));

    const [manifestResponse, weightsResponse] = await Promise.all([
      fetch("/models/vsl/weights.json"),
      fetch("/models/vsl/weights.bin")
    ]);
    if (!manifestResponse.ok || !weightsResponse.ok) {
      throw new Error("Không tải được trọng số VSL cho web.");
    }

    const manifest = await manifestResponse.json() as {
      weights: Array<{ shape: number[]; offset: number; length: number }>;
    };
    const buffer = await weightsResponse.arrayBuffer();
    const tensors = manifest.weights.map((entry) => {
      const values = new Float32Array(buffer.slice(entry.offset, entry.offset + entry.length));
      return tf.tensor(values, entry.shape);
    });

    model.setWeights(tensors);
    tensors.forEach((tensor) => tensor.dispose());
    return model;
  }

  start(): void {
    if (this.isProcessing) return;
    if (!this.handLandmarker || !this.model || !this.videoElement) {
      console.warn("VslRecognitionService not fully initialized.");
      return;
    }

    this.isProcessing = true;
    this.landmarkBuffer = [];
    this.predictionWindow = [];
    this.lastEmittedClassCode = null;
    this.lastEmittedAt = 0;

    // Frame processing loop
    const processFrame = () => {
      if (!this.isProcessing || !this.videoElement || !this.handLandmarker) return;

      if (this.videoElement.readyState >= HTMLMediaElement.HAVE_CURRENT_DATA) {
        try {
          const timestamp = performance.now();
          const result = this.handLandmarker.detectForVideo(this.videoElement, timestamp);
          
          // Draw landmarks on overlay canvas
          if (this.canvasElement) {
            this.drawLandmarks(this.canvasElement, result);
          }

          // Extract features (126 elements)
          const frameFeatures = this.extractFeatures(result);
          
          // Push to sliding window
          this.landmarkBuffer.push(Array.from(frameFeatures));
          if (this.landmarkBuffer.length > 30) {
            this.landmarkBuffer.shift(); // Keep size at 30
          }
        } catch (err) {
          console.error("Error in frame processing:", err);
        }
      }

      this.animationFrameId = requestAnimationFrame(processFrame);
    };

    this.animationFrameId = requestAnimationFrame(processFrame);

    // Inference loop every 500ms
    this.inferenceIntervalId = setInterval(() => {
      this.runInference();
    }, 500);
  }

  stop(): void {
    this.isProcessing = false;
    if (this.inferenceIntervalId) {
      clearInterval(this.inferenceIntervalId);
      this.inferenceIntervalId = null;
    }
    if (this.animationFrameId) {
      cancelAnimationFrame(this.animationFrameId);
      this.animationFrameId = null;
    }
  }

  onResult(callback: (label: string, confidence: number) => void): void {
    this.onResultCallback = callback;
  }

  destroy(): void {
    this.stop();
    if (this.handLandmarker) {
      this.handLandmarker.close();
      this.handLandmarker = null;
    }
    this.model = null;
    this.videoElement = null;
    this.canvasElement = null;
    this.landmarkBuffer = [];
    this.predictionWindow = [];
    this.lastEmittedClassCode = null;
    this.lastEmittedAt = 0;
    this.onResultCallback = null;
  }

  private extractFeatures(result: HandLandmarkerResult): Float32Array {
    const features = new Float32Array(126); // 21 joints * 3 coords * 2 hands

    if (!result.landmarks || !result.handedness) {
      return features;
    }

    for (let i = 0; i < result.landmarks.length; i++) {
      const handLandmarks = result.landmarks[i];
      const handLabel = result.handedness[i]?.[0]?.categoryName || '';
      // Left hand maps to offset 0, Right hand maps to offset 63
      const isLeft = handLabel.toLowerCase() === 'left';
      const offset = isLeft ? 0 : 63;
      const normalized = this.normalizeHandLandmarks(handLandmarks);

      for (let j = 0; j < 21; j++) {
        features[offset + j * 3] = normalized[j * 3];
        features[offset + j * 3 + 1] = normalized[j * 3 + 1];
        features[offset + j * 3 + 2] = normalized[j * 3 + 2];
      }
    }

    return features;
  }

  private normalizeHandLandmarks(handLandmarks: HandLandmarkerResult["landmarks"][number]): number[] {
    if (!handLandmarks.length) return Array(63).fill(0);

    const wrist = handLandmarks[0];
    let maxDistance = 1e-6;
    for (const landmark of handLandmarks) {
      const dx = landmark.x - wrist.x;
      const dy = landmark.y - wrist.y;
      const dz = landmark.z - wrist.z;
      maxDistance = Math.max(maxDistance, Math.hypot(dx, dy, dz));
    }

    const values: number[] = [];
    for (const landmark of handLandmarks) {
      values.push((landmark.x - wrist.x) / maxDistance);
      values.push((landmark.y - wrist.y) / maxDistance);
      values.push((landmark.z - wrist.z) / maxDistance);
    }
    return values;
  }

  private async runInference(): Promise<void> {
    if (!this.model || this.landmarkBuffer.length < 30) return;

    try {
      // Input shape: [1, 30, 126]
      const inputTensor = tf.tensor3d([this.landmarkBuffer], [1, 30, 126]);
      const prediction = this.model.predict(inputTensor) as tf.Tensor;
      const probabilities = await prediction.data();

      // Find best class
      let maxIdx = 0;
      let maxProb = 0;
      let secondProb = 0;
      for (let i = 0; i < probabilities.length; i++) {
        if (probabilities[i] > maxProb) {
          secondProb = maxProb;
          maxProb = probabilities[i];
          maxIdx = i;
        } else if (probabilities[i] > secondProb) {
          secondProb = probabilities[i];
        }
      }

      // Dispose tensors to avoid memory leaks
      inputTensor.dispose();
      prediction.dispose();

      const classCode = VSL_CLASSES[maxIdx];
      this.acceptPrediction(classCode, maxProb, maxProb - secondProb);
    } catch (err) {
      console.error("Error during model inference:", err);
    }
  }

  private acceptPrediction(classCode: string, confidence: number, margin: number): void {
    this.predictionWindow.push({ classCode, confidence, margin });
    if (this.predictionWindow.length > 5) this.predictionWindow.shift();
    if (this.predictionWindow.length < 3) return;

    const votes = this.predictionWindow.filter((item) => item.classCode === classCode);
    const voteCount = votes.length;
    const avgConfidence = votes.reduce((sum, item) => sum + item.confidence, 0) / voteCount;
    const avgMargin = votes.reduce((sum, item) => sum + item.margin, 0) / voteCount;

    const minVotes = classCode === "khan_cap" ? 5 : 3;
    const minConfidence = classCode === "khan_cap" ? 0.97 : 0.78;
    const minMargin = classCode === "khan_cap" ? 0.45 : 0.12;
    if (voteCount < minVotes || avgConfidence < minConfidence || avgMargin < minMargin) return;

    const now = performance.now();
    if (this.lastEmittedClassCode === classCode && now - this.lastEmittedAt < 2500) return;

    this.lastEmittedClassCode = classCode;
    this.lastEmittedAt = now;
    const label = VSL_LABELS[classCode] || classCode;
    this.onResultCallback?.(label, Math.round(avgConfidence * 100));
  }

  private drawLandmarks(canvas: HTMLCanvasElement, result: HandLandmarkerResult): void {
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Adjust canvas size to match layout if size mismatch
    if (canvas.width !== canvas.clientWidth || canvas.height !== canvas.clientHeight) {
      canvas.width = canvas.clientWidth || 640;
      canvas.height = canvas.clientHeight || 480;
    }

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    if (!result.landmarks) return;

    ctx.strokeStyle = "rgba(34, 197, 94, 0.85)"; // Neon green
    ctx.fillStyle = "rgba(34, 197, 94, 0.95)";
    ctx.lineWidth = 2.5;

    // Standard connections mapping
    const HAND_CONNECTIONS = [
      // Thumb
      [0, 1], [1, 2], [2, 3], [3, 4],
      // Index
      [0, 5], [5, 6], [6, 7], [7, 8],
      // Middle
      [9, 10], [10, 11], [11, 12],
      // Ring
      [13, 14], [14, 15], [15, 16],
      // Pinky
      [0, 17], [17, 18], [18, 19], [19, 20],
      // Knuckle connections to draw palm base
      [5, 9], [9, 13], [13, 17]
    ];

    for (const handLandmarks of result.landmarks) {
      // Draw lines
      for (const [start, end] of HAND_CONNECTIONS) {
        const startLm = handLandmarks[start];
        const endLm = handLandmarks[end];
        if (startLm && endLm) {
          ctx.beginPath();
          ctx.moveTo(startLm.x * canvas.width, startLm.y * canvas.height);
          ctx.lineTo(endLm.x * canvas.width, endLm.y * canvas.height);
          ctx.stroke();
        }
      }

      // Draw points
      for (const lm of handLandmarks) {
        ctx.beginPath();
        ctx.arc(lm.x * canvas.width, lm.y * canvas.height, 3.5, 0, 2 * Math.PI);
        ctx.fill();
      }
    }
  }
}
