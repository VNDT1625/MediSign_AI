/**
 * VslRecognitionService — Vietnamese Sign Language realtime recognizer.
 *
 * Pipeline tuân theo chuẩn quốc tế Sign Language Recognition (SLR):
 *   1. MediaPipe stack 3-in-1 (Hand + Face + Pose) — bản web tách thành
 *      3 task riêng vì TasksVision JS chưa expose Holistic single-call.
 *   2. Trích landmarks → feature vector 465-D (51 pose + 126 hand + 288 face).
 *   3. Head-pose de-rotation: dùng matrix Procrustes của FaceLandmarker để
 *      đưa face landmarks về canonical frame → bất biến với nghiêng đầu.
 *   4. Body-relative normalization: anchor pose theo midpoint vai-hông;
 *      hand theo wrist; face theo mũi.
 *   5. Sliding window 30 frame, inference Bi-LSTM 2Hz.
 *   6. Voting + confidence + margin gate trước khi emit.
 *
 * Tham chiếu literature:
 *   - Watson 2010 (Purdue): NMM là grammatically obligatory cho ASL.
 *   - Lyu et al. 2025 (arXiv 2507.20884): mouth là feature face quan trọng nhất.
 *   - MediaPipe Holistic blog 2020: cấu trúc 540+ keypoint chuẩn.
 *   - Testing MediaPipe Holistic for NMM (arXiv 2403.10367): khuyến nghị
 *     tách face contour + lips inner/outer + brows riêng.
 */

import * as tf from "@tensorflow/tfjs";
import {
  FilesetResolver,
  HandLandmarker,
  HandLandmarkerResult,
  FaceLandmarker,
  FaceLandmarkerResult,
  PoseLandmarker,
  PoseLandmarkerResult,
  NormalizedLandmark,
} from "@mediapipe/tasks-vision";

import {
  POSE_UPPER_BODY,
  POSE_DIM,
  FACE_KEY_INDICES,
  FACE_DIM,
  HAND_DIM,
  FULL_FEATURE_DIM,
  FEATURE_OFFSETS,
  HAND_CONNECTIONS,
  POSE_CONNECTIONS,
  FACE_CONTOUR_GROUPS,
} from "./landmarkSpec";

/**
 * VSL_CLASSES / VSL_LABELS — fallback 10 từ legacy. Sau init() sẽ được
 * cập nhật từ `/models/vsl/classes.json` (single source of truth) để hỗ
 * trợ vocabulary mở rộng (150-300+ từ y tế) mà không cần đụng code.
 */
export const VSL_CLASSES: string[] = [
  "dau", "dau_dau", "bung", "sot", "ho",
  "kho_tho", "chong_mat", "thuoc", "bac_si", "khan_cap",
];
export const VSL_LABELS: Record<string, string> = {
  dau: "Đau",
  dau_dau: "Đau đầu",
  bung: "Bụng",
  sot: "Sốt",
  ho: "Ho",
  kho_tho: "Khó thở",
  chong_mat: "Chóng mặt",
  thuoc: "Thuốc",
  bac_si: "Bác sĩ",
  khan_cap: "Khẩn cấp",
};

/**
 * Schema của `classes.json`:
 *   { version, feature_dim, sequence_length, categories: [{name, items: [{code, vi}]}] }
 * Hàm này flatten về danh sách `code` ổn định (theo thứ tự xuất hiện
 * trong file) và map `code → vi`. Thứ tự PHẢI khớp với thứ tự output
 * neuron của model — pipeline Python phải sort/serialize cùng thứ tự
 * này khi train.
 */
async function loadVocabularyFromManifest(): Promise<{
  codes: string[];
  labels: Record<string, string>;
} | null> {
  try {
    const resp = await fetch("/models/vsl/classes.json", { cache: "no-store" });
    if (!resp.ok) return null;
    const json = (await resp.json()) as {
      categories?: Array<{ items?: Array<{ code: string; vi: string }> }>;
    };
    const codes: string[] = [];
    const labels: Record<string, string> = {};
    for (const cat of json.categories ?? []) {
      for (const item of cat.items ?? []) {
        if (!item.code) continue;
        codes.push(item.code);
        labels[item.code] = item.vi ?? item.code;
      }
    }
    return codes.length > 0 ? { codes, labels } : null;
  } catch (err) {
    console.warn("[VSL] Failed to load classes.json, falling back to legacy 10:", err);
    return null;
  }
}

// Chế độ feature vector mà service đang chạy (suy ra từ model input shape).
type FeatureMode = "hand_only_126" | "hand_face_225" | "holistic_495";

export class VslRecognitionService {
  private videoElement: HTMLVideoElement | null = null;
  private canvasElement: HTMLCanvasElement | null = null;

  private handLandmarker: HandLandmarker | null = null;
  private faceLandmarker: FaceLandmarker | null = null;
  private poseLandmarker: PoseLandmarker | null = null;

  private model: tf.LayersModel | null = null;
  private modelFeatureDim: number = HAND_DIM;
  private featureMode: FeatureMode = "hand_only_126";

  private isProcessing = false;
  private landmarkBuffer: number[][] = [];
  private onResultCallback: ((label: string, confidence: number) => void) | null = null;
  private inferenceIntervalId: any = null;
  private animationFrameId: number | null = null;
  private predictionWindow: Array<{ classCode: string; confidence: number; margin: number }> = [];
  private lastEmittedClassCode: string | null = null;
  private lastEmittedAt = 0;

  private lastHandResult: HandLandmarkerResult | null = null;
  private lastFaceResult: FaceLandmarkerResult | null = null;
  private lastPoseResult: PoseLandmarkerResult | null = null;

  /**
   * Tracker state cho 2 slot tay (Left=0, Right=63 trong feature vector).
   * Mỗi slot lưu landmark cuối được gán + thời điểm — phục vụ:
   *  - Continuity assignment khi nhãn handedness của MediaPipe nhảy.
   *  - Carry-forward khi tay mất tracking ≤ HAND_STALE_MS (occlusion ngắn).
   * Note: ta lưu deep copy palm center để rẻ; không cần lưu cả 21 điểm.
   */
  private handSlots: Array<{
    landmarks: NormalizedLandmark[] | null;
    palm: { x: number; y: number; z: number } | null;
    timestamp: number;
  }> = [
    { landmarks: null, palm: null, timestamp: 0 },
    { landmarks: null, palm: null, timestamp: 0 },
  ];
  /** Carry-forward cho phép nếu mất tracking ≤ 200ms (≈ 6 frame @ 30fps). */
  private static readonly HAND_STALE_MS = 200;

  // ─────────────────────────────────────────────────────────────────────
  // Lifecycle
  // ─────────────────────────────────────────────────────────────────────

  async init(videoElement: HTMLVideoElement, canvasElement?: HTMLCanvasElement): Promise<void> {
    this.videoElement = videoElement;
    if (canvasElement) this.canvasElement = canvasElement;

    try {
      await tf.ready();

      // Load vocabulary từ classes.json (single source of truth) song song
      // với MediaPipe init. Nếu manifest mới có hơn 10 từ → vocab tự mở rộng.
      const vocabPromise = loadVocabularyFromManifest();

      const vision = await FilesetResolver.forVisionTasks(
        "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@latest/wasm",
      );

      // Build model + load 3 landmarkers song song để rút ngắn init time.
      const [model, handLM, faceLM, poseLM, vocab] = await Promise.all([
        this.buildAndLoadModel(),
        this.initHandLandmarker(vision),
        this.initFaceLandmarker(vision),
        this.initPoseLandmarker(vision),
        vocabPromise,
      ]);
      this.model = model;
      this.handLandmarker = handLM;
      this.faceLandmarker = faceLM;
      this.poseLandmarker = poseLM;

      // Update vocabulary nếu manifest tải được. Mutate cùng object để
      // các consumer đã capture tham chiếu vẫn nhận được giá trị mới.
      if (vocab) {
        const expectedClassCount = vocab.codes.length;
        const modelOutShape = (model.outputs[0].shape ?? []) as Array<number | null>;
        const modelClassCount = modelOutShape[modelOutShape.length - 1] ?? 0;
        if (modelClassCount !== expectedClassCount) {
          console.warn(
            `[VSL] classes.json có ${expectedClassCount} class nhưng model output ${modelClassCount}. ` +
              `Giữ vocabulary từ JSON (UI sẽ hiển thị code chưa map nếu lệch). ` +
              `Hãy retrain model + xuất lại weights để khớp.`,
          );
        }
        VSL_CLASSES.length = 0;
        VSL_CLASSES.push(...vocab.codes);
        for (const k of Object.keys(VSL_LABELS)) delete VSL_LABELS[k];
        Object.assign(VSL_LABELS, vocab.labels);
        console.log(`[VSL] Loaded vocabulary: ${VSL_CLASSES.length} classes from classes.json`);
      }

      // Suy ra mode từ input shape của model.
      const inputShape = (model.inputs[0].shape ?? []) as Array<number | null>;
      const featureDim = inputShape[inputShape.length - 1];
      if (featureDim === FULL_FEATURE_DIM) {
        // Holistic v2 (495-D): pose 45 + hand 126 + face 324 (108 điểm × 3).
        this.modelFeatureDim = FULL_FEATURE_DIM;
        this.featureMode = "holistic_495";
      } else if (featureDim === HAND_DIM + 99) {
        // Bản v2 cũ: hand + face đơn giản (225). Giữ tương thích.
        this.modelFeatureDim = HAND_DIM + 99;
        this.featureMode = "hand_face_225";
      } else if (featureDim === HAND_DIM) {
        this.modelFeatureDim = HAND_DIM;
        this.featureMode = "hand_only_126";
      } else {
        console.warn(`[VSL] Unexpected model dim ${featureDim}; fallback hand-only.`);
        this.modelFeatureDim = HAND_DIM;
        this.featureMode = "hand_only_126";
      }
      console.log(`[VSL] Ready. Mode=${this.featureMode} (${this.modelFeatureDim}-D).`);
    } catch (err) {
      console.error("[VSL] Init failed:", err);
      throw err;
    }
  }

  private async initHandLandmarker(vision: any): Promise<HandLandmarker> {
    return HandLandmarker.createFromOptions(vision, {
      baseOptions: {
        modelAssetPath:
          "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task",
        delegate: "GPU",
      },
      runningMode: "VIDEO",
      numHands: 2,
      // Hạ ngưỡng để bắt được tay khi 2 tay chạm/che lấp nhau hoặc tay
      // chỉ ló một phần trong frame. Giá trị mặc định 0.5 quá conservative
      // cho SLR realtime — paper SLR thường dùng 0.3-0.4.
      minHandDetectionConfidence: 0.3,
      minHandPresenceConfidence: 0.3,
      // Tracking confidence giữ cao hơn detection — khi đã có tay và đang
      // track, không nên drop dễ dàng giữa frame.
      minTrackingConfidence: 0.5,
    });
  }

  private async initFaceLandmarker(vision: any): Promise<FaceLandmarker> {
    return FaceLandmarker.createFromOptions(vision, {
      baseOptions: {
        modelAssetPath:
          "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task",
        delegate: "GPU",
      },
      runningMode: "VIDEO",
      numFaces: 1,
      // Không dùng `facialTransformationMatrixes` cho de-rotation nữa
      // (matrix kia ở metric face-space, không khớp với landmark image-
      // normalized space). Service tự dựng local frame từ 3 anchor (mũi +
      // 2 mắt + cằm) trong `fillFaceFeatures` — chính xác hơn.
      outputFacialTransformationMatrixes: false,
      outputFaceBlendshapes: false,
    });
  }

  private async initPoseLandmarker(vision: any): Promise<PoseLandmarker> {
    return PoseLandmarker.createFromOptions(vision, {
      baseOptions: {
        // Lite version đủ tốt cho upper-body + nhẹ ~3MB, GPU friendly.
        modelAssetPath:
          "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/latest/pose_landmarker_lite.task",
        delegate: "GPU",
      },
      runningMode: "VIDEO",
      numPoses: 1,
    });
  }

  // ─────────────────────────────────────────────────────────────────────
  // Model build / load
  // ─────────────────────────────────────────────────────────────────────

  private async buildAndLoadModel(): Promise<tf.LayersModel> {
    const [manifestResp, weightsResp] = await Promise.all([
      fetch("/models/vsl/weights.json"),
      fetch("/models/vsl/weights.bin"),
    ]);
    if (!manifestResp.ok || !weightsResp.ok) {
      throw new Error("Không tải được trọng số VSL cho web.");
    }
    const manifest = (await manifestResp.json()) as {
      weights: Array<{ name?: string; shape: number[]; offset: number; length: number }>;
    };

    // Đọc input feature dim từ shape kernel đầu tiên.
    const inferredDim = manifest.weights[0]?.shape?.[0] ?? HAND_DIM;
    if (![HAND_DIM, HAND_DIM + 99, FULL_FEATURE_DIM].includes(inferredDim)) {
      console.warn(
        `[VSL] Manifest first-kernel shape[0] = ${inferredDim}; ` +
          `expected ${HAND_DIM} | ${HAND_DIM + 99} | ${FULL_FEATURE_DIM}.`,
      );
    }

    // Đọc số class output từ shape của `output_gesture/bias`.
    // Lưu ý TF.js convention: `manifest.weights` xếp trainable trước, sau
    // đó là non-trainable (BN moving_mean/variance). Vì vậy phần tử cuối
    // KHÔNG phải output bias mà là `batch_normalization_1/moving_variance`
    // shape [64] — nếu lấy nó làm class count sẽ build sai (units=64).
    // Tìm theo tên là cách an toàn duy nhất.
    const outputBias = manifest.weights.find((w) =>
      (w.name ?? "").includes("output_gesture") &&
      (w.name ?? "").endsWith("bias")
    );
    const inferredClassCount = (outputBias && outputBias.shape.length === 1)
      ? outputBias.shape[0]
      : VSL_CLASSES.length;

    // Bi-LSTM giống pipeline Python. Initializer "zeros" tránh cost
    // QR decomposition của orthogonal initializer (block main thread).
    const fastInit = { kernelInitializer: "zeros", recurrentInitializer: "zeros" } as const;

    const model = tf.sequential();
    model.add(tf.layers.inputLayer({ inputShape: [30, inferredDim], name: "vsl_landmarks_sequence" }));
    model.add(tf.layers.bidirectional({
      layer: tf.layers.lstm({ units: 64, returnSequences: true, ...fastInit }) as any,
      mergeMode: "concat",
      name: "bidirectional",
    }));
    model.add(tf.layers.batchNormalization({ name: "batch_normalization" }));
    model.add(tf.layers.dropout({ rate: 0.3, name: "dropout" }));
    model.add(tf.layers.bidirectional({
      layer: tf.layers.lstm({ units: 32, returnSequences: false, ...fastInit }) as any,
      mergeMode: "concat",
      name: "bidirectional_1",
    }));
    model.add(tf.layers.batchNormalization({ name: "batch_normalization_1" }));
    model.add(tf.layers.dropout({ rate: 0.3, name: "dropout_1" }));
    model.add(tf.layers.dense({ units: 32, activation: "relu", kernelInitializer: "zeros", name: "dense" }));
    model.add(tf.layers.dropout({ rate: 0.2, name: "dropout_2" }));
    model.add(tf.layers.dense({
      units: inferredClassCount,
      activation: "softmax",
      kernelInitializer: "zeros",
      name: "output_gesture",
    }));

    if (manifest.weights.length !== model.weights.length) {
      throw new Error(
        `VSL manifest size mismatch: expect ${model.weights.length}, got ${manifest.weights.length}.`,
      );
    }

    const buffer = await weightsResp.arrayBuffer();
    const orderedTensors = manifest.weights.map((entry) => {
      const values = new Float32Array(buffer.slice(entry.offset, entry.offset + entry.length));
      return tf.tensor(values, entry.shape);
    });

    for (let i = 0; i < orderedTensors.length; i++) {
      const got = orderedTensors[i].shape;
      const exp = model.weights[i].shape;
      const sameShape = got.length === exp.length && got.every((d, k) => d === exp[k]);
      if (!sameShape) {
        const wName = model.weights[i].name;
        const manifestName = manifest.weights[i].name ?? "(unnamed)";
        console.error(
          `[VSL] Weight #${i} (${wName}) shape mismatch: expect ${JSON.stringify(exp)}, got ${JSON.stringify(got)} (manifest "${manifestName}").`,
        );
        orderedTensors.forEach((t) => t.dispose());
        throw new Error(`VSL weight shape mismatch at index ${i} (${wName}).`);
      }
    }

    await new Promise((r) => setTimeout(r, 0)); // yield trước heavy setWeights
    model.setWeights(orderedTensors);
    orderedTensors.forEach((t) => t.dispose());
    return model;
  }

  // ─────────────────────────────────────────────────────────────────────
  // Frame loop
  // ─────────────────────────────────────────────────────────────────────

  start(): void {
    if (this.isProcessing) return;
    if (!this.handLandmarker || !this.faceLandmarker || !this.poseLandmarker || !this.model || !this.videoElement) {
      console.warn("[VSL] Service not fully initialized.");
      return;
    }

    this.isProcessing = true;
    this.landmarkBuffer = [];
    this.predictionWindow = [];
    this.lastEmittedClassCode = null;
    this.lastEmittedAt = 0;
    this.lastHandResult = null;
    this.lastFaceResult = null;
    this.lastPoseResult = null;
    // Reset hand slot tracker để session mới không kế thừa palm position cũ.
    this.handSlots = [
      { landmarks: null, palm: null, timestamp: 0 },
      { landmarks: null, palm: null, timestamp: 0 },
    ];

    const processFrame = () => {
      if (!this.isProcessing || !this.videoElement) return;
      if (this.videoElement.readyState >= HTMLMediaElement.HAVE_CURRENT_DATA) {
        try {
          const ts = performance.now();
          const handR = this.handLandmarker!.detectForVideo(this.videoElement, ts);
          const faceR = this.faceLandmarker!.detectForVideo(this.videoElement, ts);
          const poseR = this.poseLandmarker!.detectForVideo(this.videoElement, ts);

          this.lastHandResult = handR;
          this.lastFaceResult = faceR;
          this.lastPoseResult = poseR;

          if (this.canvasElement) this.drawOverlay(this.canvasElement, handR, faceR, poseR);

          const feats = this.extractFeatures(handR, faceR, poseR);
          this.landmarkBuffer.push(Array.from(feats));
          if (this.landmarkBuffer.length > 30) this.landmarkBuffer.shift();
        } catch (err) {
          console.error("[VSL] Frame processing error:", err);
        }
      }
      this.animationFrameId = requestAnimationFrame(processFrame);
    };
    this.animationFrameId = requestAnimationFrame(processFrame);

    this.inferenceIntervalId = setInterval(() => this.runInference(), 500);
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

  destroy(): void {
    this.stop();
    this.handLandmarker?.close();
    this.faceLandmarker?.close();
    this.poseLandmarker?.close();
    this.handLandmarker = null;
    this.faceLandmarker = null;
    this.poseLandmarker = null;
    this.model = null;
    this.videoElement = null;
    this.canvasElement = null;
    this.landmarkBuffer = [];
    this.predictionWindow = [];
    this.lastEmittedClassCode = null;
    this.lastEmittedAt = 0;
    this.lastHandResult = null;
    this.lastFaceResult = null;
    this.lastPoseResult = null;
    this.handSlots = [
      { landmarks: null, palm: null, timestamp: 0 },
      { landmarks: null, palm: null, timestamp: 0 },
    ];
    this.onResultCallback = null;
  }

  onResult(callback: (label: string, confidence: number) => void): void {
    this.onResultCallback = callback;
  }

  // ─────────────────────────────────────────────────────────────────────
  // Feature extraction
  // ─────────────────────────────────────────────────────────────────────

  /**
   * Trích vector feature theo `featureMode`:
   *   - hand_only_126: 21×3×2 = 126
   *   - hand_face_225: 126 + 99 (33 face key) — bản trung gian
   *   - holistic_495 : 45 pose + 126 hand + 324 face — chuẩn quốc tế
   */
  private extractFeatures(
    handR: HandLandmarkerResult,
    faceR: FaceLandmarkerResult,
    poseR: PoseLandmarkerResult,
  ): Float32Array {
    const dim = this.modelFeatureDim;
    const feats = new Float32Array(dim);

    // Mode mới (holistic): pose trước, rồi hand, rồi face — khớp với
    // FEATURE_OFFSETS định nghĩa trong landmarkSpec.ts.
    if (this.featureMode === "holistic_495") {
      this.fillPoseFeatures(feats, FEATURE_OFFSETS.POSE_START, poseR);
      this.fillHandFeatures(feats, FEATURE_OFFSETS.HAND_START, handR);
      this.fillFaceFeatures(feats, FEATURE_OFFSETS.FACE_START, faceR);
      return feats;
    }

    // Legacy modes: hand đầu, face nối sau (compat với weights cũ).
    this.fillHandFeatures(feats, 0, handR);
    if (this.featureMode === "hand_face_225") {
      this.fillFaceFeaturesLegacy(feats, HAND_DIM, faceR);
    }
    return feats;
  }

  // ── POSE block ──────────────────────────────────────────────────────
  private fillPoseFeatures(
    out: Float32Array,
    offset: number,
    poseR: PoseLandmarkerResult,
  ): void {
    const lm = poseR.landmarks?.[0];
    if (!lm || lm.length === 0) return;

    // Anchor = midpoint giữa 2 vai (idx 11, 12).
    // Scale = khoảng cách từ vai trái đến hông trái (ổn định, không phụ
    // thuộc tay đang giơ lên/xuống — tránh feature blow-up khi tay vung).
    const sL = lm[11], sR = lm[12], hL = lm[23];
    if (!sL || !sR || !hL) return;
    const cx = (sL.x + sR.x) / 2;
    const cy = (sL.y + sR.y) / 2;
    const cz = (sL.z + sR.z) / 2;
    const scale = Math.max(
      Math.hypot(sL.x - hL.x, sL.y - hL.y, sL.z - hL.z),
      1e-6,
    );

    for (let j = 0; j < POSE_UPPER_BODY.length; j++) {
      const idx = POSE_UPPER_BODY[j];
      const p = lm[idx];
      if (!p) continue;
      out[offset + j * 3] = (p.x - cx) / scale;
      out[offset + j * 3 + 1] = (p.y - cy) / scale;
      out[offset + j * 3 + 2] = (p.z - cz) / scale;
    }
  }

  // ── HAND block ──────────────────────────────────────────────────────
  /**
   * Gán 2 slot tay (L=0, R=63) ổn định qua thời gian. Vấn đề thực tế:
   *
   *  1. Khi 2 tay chạm vào nhau, MediaPipe HandLandmarker thường chỉ
   *     detect được 1 → slot kia bị set zeros → model thấy "tay biến mất"
   *     đột ngột giữa sequence → ảnh hưởng dự đoán.
   *  2. Handedness label "Left"/"Right" của MediaPipe có thể flip giữa
   *     các frame liền kề khi 2 tay che lấp nhau → cùng 1 tay vật lý
   *     nhảy giữa 2 slot → feature vector "teleport".
   *
   * Chiến lược (chuẩn industry — tham chiếu KwameGilbert/SignLens, paper
   * arXiv 2405.03545 về MediaPipe Holistic ROI):
   *   - Lấy palm center (idx 9 - middle MCP) của mỗi hand vừa detect.
   *   - Match với palm center của 2 slot (last frame) bằng nearest-distance
   *     assignment (Hungarian-lite cho 2x2 case).
   *   - Tiebreak khi không có history: dùng nhãn handedness gốc + body
   *     midline (từ pose nose hoặc shoulder midpoint).
   *   - Nếu 1 slot không có hand match: nếu vẫn còn fresh (≤ 200ms),
   *     giữ nguyên landmark frame trước (carry-forward); ngược lại zero.
   */
  private fillHandFeatures(
    out: Float32Array,
    offset: number,
    handR: HandLandmarkerResult,
  ): void {
    const now = performance.now();
    const detected: Array<{
      landmarks: NormalizedLandmark[];
      label: string;
      palm: { x: number; y: number; z: number };
    }> = [];
    if (handR.landmarks && handR.handedness) {
      for (let i = 0; i < handR.landmarks.length; i++) {
        const lm = handR.landmarks[i];
        if (!lm || lm.length < 21) continue;
        const palm = lm[9] ?? lm[0];
        detected.push({
          landmarks: lm,
          label: handR.handedness[i]?.[0]?.categoryName?.toLowerCase() ?? "",
          palm: { x: palm.x, y: palm.y, z: palm.z },
        });
      }
    }

    // Body midline (x): dùng để tiebreak khi không có history.
    // Lấy từ pose mũi nếu có, fallback 0.5 (giữa frame).
    let midlineX = 0.5;
    const noseLM = this.lastPoseResult?.landmarks?.[0]?.[0];
    if (noseLM) midlineX = noseLM.x;

    // Tính assignment hand[i] → slot[0=Left, 1=Right].
    const assignment = this.assignHandSlots(detected, midlineX);

    // Update slots + ghi feature vector.
    for (let slot = 0; slot < 2; slot++) {
      const handIdx = assignment[slot];
      const slotState = this.handSlots[slot];
      let lmToUse: NormalizedLandmark[] | null = null;

      if (handIdx >= 0) {
        // Có hand match → cập nhật slot với landmark mới.
        const det = detected[handIdx];
        slotState.landmarks = det.landmarks;
        slotState.palm = det.palm;
        slotState.timestamp = now;
        lmToUse = det.landmarks;
      } else if (
        slotState.landmarks &&
        now - slotState.timestamp <= VslRecognitionService.HAND_STALE_MS
      ) {
        // Không có hand mới nhưng slot còn fresh → carry-forward.
        lmToUse = slotState.landmarks;
      } else {
        // Slot stale → clear để zero out feature.
        slotState.landmarks = null;
        slotState.palm = null;
      }

      if (!lmToUse) continue; // zeros (do Float32Array khởi tạo 0)

      const handOffset = offset + (slot === 0 ? 0 : 63);
      const norm = this.normalizeHand(lmToUse);
      for (let j = 0; j < 21; j++) {
        out[handOffset + j * 3] = norm[j * 3];
        out[handOffset + j * 3 + 1] = norm[j * 3 + 1];
        out[handOffset + j * 3 + 2] = norm[j * 3 + 2];
      }
    }
  }

  /**
   * Trả về `[handIdx_for_slot0, handIdx_for_slot1]`. -1 nếu slot không
   * được gán. Logic:
   *   1. Nếu cả 2 slot đều có history fresh → match 2×N theo nearest palm
   *      distance, ưu tiên match cost thấp trước.
   *   2. Nếu chỉ 1 slot có history → slot đó match nearest, slot còn lại
   *      lấy hand chưa match.
   *   3. Nếu không slot nào có history (frame đầu hoặc occlusion dài) →
   *      dùng MediaPipe handedness label nếu có, không thì midline tiebreak.
   */
  private assignHandSlots(
    detected: Array<{
      landmarks: NormalizedLandmark[];
      label: string;
      palm: { x: number; y: number; z: number };
    }>,
    midlineX: number,
  ): [number, number] {
    const out: [number, number] = [-1, -1];
    if (detected.length === 0) return out;

    const now = performance.now();
    const slotFresh = this.handSlots.map(
      (s) => s.palm !== null && now - s.timestamp <= VslRecognitionService.HAND_STALE_MS,
    );

    const dist2 = (a: { x: number; y: number; z: number }, b: { x: number; y: number; z: number }) =>
      (a.x - b.x) ** 2 + (a.y - b.y) ** 2 + (a.z - b.z) ** 2;

    // Case 1 & 2: có ít nhất 1 slot fresh → continuity matching.
    if (slotFresh[0] || slotFresh[1]) {
      const used = new Set<number>();
      // Greedy: tìm cặp (slot, hand) khoảng cách bé nhất, lock, lặp lại.
      const pairs: Array<{ slot: number; hand: number; d: number }> = [];
      for (let s = 0; s < 2; s++) {
        if (!slotFresh[s]) continue;
        const slotPalm = this.handSlots[s].palm!;
        for (let h = 0; h < detected.length; h++) {
          pairs.push({ slot: s, hand: h, d: dist2(slotPalm, detected[h].palm) });
        }
      }
      pairs.sort((a, b) => a.d - b.d);
      const slotTaken = new Set<number>();
      for (const p of pairs) {
        // Threshold: nếu palm di chuyển > 0.25 đơn vị normalized chỉ trong
        // 1 frame thì coi là 2 tay khác nhau, không phải continuity của cùng 1 tay.
        if (p.d > 0.0625) continue;
        if (slotTaken.has(p.slot) || used.has(p.hand)) continue;
        out[p.slot] = p.hand;
        slotTaken.add(p.slot);
        used.add(p.hand);
      }
      // Slot còn trống → gán hand chưa dùng theo nearest-to-midline tiebreak.
      const unusedHands = detected.map((_, i) => i).filter((i) => !used.has(i));
      for (let s = 0; s < 2; s++) {
        if (out[s] !== -1) continue;
        if (unusedHands.length === 0) break;
        // Slot 0 (L) ưu tiên hand có x < midline; slot 1 (R) thì x ≥ midline.
        // (Nhớ rằng video đã mirror — landmark x tăng từ trái sang phải user).
        unusedHands.sort((a, b) => {
          const ax = detected[a].palm.x;
          const bx = detected[b].palm.x;
          return s === 0 ? ax - bx : bx - ax;
        });
        const pick = unusedHands.shift()!;
        out[s] = pick;
      }
      return out;
    }

    // Case 3: cả 2 slot đều stale → bootstrap.
    // Ưu tiên handedness label từ MediaPipe nếu có.
    for (let h = 0; h < detected.length; h++) {
      const lbl = detected[h].label;
      if (lbl === "left" && out[0] === -1) out[0] = h;
      else if (lbl === "right" && out[1] === -1) out[1] = h;
    }
    // Nếu vẫn còn slot trống và còn hand chưa dùng → gán theo midline.
    const used = new Set<number>(out.filter((v) => v !== -1));
    const remaining = detected.map((_, i) => i).filter((i) => !used.has(i));
    remaining.sort((a, b) => detected[a].palm.x - detected[b].palm.x); // x nhỏ → trái
    for (let s = 0; s < 2; s++) {
      if (out[s] !== -1) continue;
      if (remaining.length === 0) break;
      // Slot 0 (Left) lấy hand có x nhỏ nhất còn lại; slot 1 lấy hand x lớn nhất.
      out[s] = s === 0 ? remaining.shift()! : remaining.pop()!;
    }
    return out;
  }

  private normalizeHand(handLM: HandLandmarkerResult["landmarks"][number]): number[] {
    if (!handLM.length) return Array(63).fill(0);
    const wrist = handLM[0];
    let maxDist = 1e-6;
    for (const lm of handLM) {
      maxDist = Math.max(maxDist, Math.hypot(lm.x - wrist.x, lm.y - wrist.y, lm.z - wrist.z));
    }
    const out: number[] = [];
    for (const lm of handLM) {
      out.push((lm.x - wrist.x) / maxDist, (lm.y - wrist.y) / maxDist, (lm.z - wrist.z) / maxDist);
    }
    return out;
  }

  // ── FACE block (holistic mode) ──────────────────────────────────────
  /**
   * Chuẩn hoá face để bất biến với head pose (yaw/pitch/roll):
   *
   * Trước đây dùng `facialTransformationMatrixes` của FaceLandmarker.
   * Đó là matrix ở metric face space (mm), KHÔNG hợp với toạ độ image-
   * normalized [0..1] mà landmark trả về → áp lẫn 2 hệ → mesh vỡ.
   *
   * Giải pháp đúng: build **local face frame** từ chính các landmark
   * image-space, dùng 3 anchor:
   *   - Đỉnh mũi (idx 1)              ← origin
   *   - Trung điểm 2 góc mắt trong (133 + 362) ← cùng "eyes baseline"
   *   - Cằm (idx 152)                 ← để xác định trục dọc
   *
   *   X-axis (right) = (mắt_R − mắt_L) chuẩn hoá
   *   Y-axis (down)  = (cằm − trung_điểm_mắt) chuẩn hoá rồi orthogonalize
   *   Z-axis        = X × Y
   *
   * Sau đó xoay mọi điểm face vào hệ trục này. Khi đầu nghiêng yaw/pitch/
   * roll, 3 anchor nghiêng theo nhau → frame xoay theo → toạ độ trong
   * frame ổn định. Đó là Procrustes alignment đơn giản.
   *
   * Scale: chia cho khoảng cách 2 mắt (interocular distance) — chuẩn
   * cosmetic-vision invariant.
   */
  private fillFaceFeatures(
    out: Float32Array,
    offset: number,
    faceR: FaceLandmarkerResult,
  ): void {
    const faceLM = faceR.faceLandmarks?.[0];
    if (!faceLM || faceLM.length === 0) return;

    const noseTip = faceLM[1];
    const eyeL = faceLM[133]; // inner corner mắt trái
    const eyeR = faceLM[362]; // inner corner mắt phải
    const chin = faceLM[152];
    if (!noseTip || !eyeL || !eyeR || !chin) return;

    // X-axis: vector từ mắt trái sang mắt phải.
    let xAxis = sub(eyeR, eyeL);
    const interocular = norm(xAxis);
    if (interocular < 1e-6) return;
    xAxis = scale(xAxis, 1 / interocular);

    // Y-axis tạm thời: từ trung điểm 2 mắt xuống cằm. Sau đó
    // orthogonalize (Gram-Schmidt) loại bỏ thành phần dọc theo X.
    const eyesMid = mid(eyeL, eyeR);
    let yRaw = sub(chin, eyesMid);
    const yProj = dot(yRaw, xAxis);
    let yAxis = sub(yRaw, scale(xAxis, yProj));
    const yLen = norm(yAxis);
    if (yLen < 1e-6) return;
    yAxis = scale(yAxis, 1 / yLen);

    // Z-axis = X × Y (right-handed).
    const zAxis = cross(xAxis, yAxis);

    // Scale chuẩn hoá: dùng interocular distance làm 1 unit.
    const scaleNorm = interocular;

    // Project mọi key landmark vào local frame.
    for (let j = 0; j < FACE_KEY_INDICES.length; j++) {
      const lm = faceLM[FACE_KEY_INDICES[j]];
      if (!lm) continue;
      const dx = lm.x - noseTip.x;
      const dy = lm.y - noseTip.y;
      const dz = lm.z - noseTip.z;
      // Tọa độ trong local frame = dot product với từng trục
      const fx = (dx * xAxis.x + dy * xAxis.y + dz * xAxis.z) / scaleNorm;
      const fy = (dx * yAxis.x + dy * yAxis.y + dz * yAxis.z) / scaleNorm;
      const fz = (dx * zAxis.x + dy * zAxis.y + dz * zAxis.z) / scaleNorm;
      out[offset + j * 3] = fx;
      out[offset + j * 3 + 1] = fy;
      out[offset + j * 3 + 2] = fz;
    }
  }

  // ── FACE block (legacy 33-keypoint mode, chỉ giữ để tương thích) ───
  private fillFaceFeaturesLegacy(
    out: Float32Array,
    offset: number,
    faceR: FaceLandmarkerResult,
  ): void {
    // 33 điểm cố định lúc trước — đã thay bằng FACE_KEY_INDICES (~96 điểm).
    // Khi model đã train mode này, chỉ trích 33 đầu tiên của FACE_KEY_INDICES.
    const SUBSET = FACE_KEY_INDICES.slice(0, 33);
    const faceLM = faceR.faceLandmarks?.[0];
    if (!faceLM) return;
    const anchor = faceLM[1] ?? faceLM[0];
    if (!anchor) return;

    let maxDist = 1e-6;
    for (const idx of SUBSET) {
      const lm = faceLM[idx];
      if (!lm) continue;
      maxDist = Math.max(maxDist, Math.hypot(lm.x - anchor.x, lm.y - anchor.y, lm.z - anchor.z));
    }
    for (let j = 0; j < SUBSET.length; j++) {
      const lm = faceLM[SUBSET[j]];
      if (!lm) continue;
      out[offset + j * 3] = (lm.x - anchor.x) / maxDist;
      out[offset + j * 3 + 1] = (lm.y - anchor.y) / maxDist;
      out[offset + j * 3 + 2] = (lm.z - anchor.z) / maxDist;
    }
  }

  // ─────────────────────────────────────────────────────────────────────
  // Inference + voting
  // ─────────────────────────────────────────────────────────────────────

  private async runInference(): Promise<void> {
    if (!this.model || this.landmarkBuffer.length < 30) return;
    try {
      const dim = this.modelFeatureDim;
      const inputTensor = tf.tensor3d([this.landmarkBuffer], [1, 30, dim]);
      const prediction = this.model.predict(inputTensor) as tf.Tensor;
      const probs = await prediction.data();

      let maxIdx = 0, maxProb = 0, secondProb = 0;
      for (let i = 0; i < probs.length; i++) {
        if (probs[i] > maxProb) {
          secondProb = maxProb;
          maxProb = probs[i];
          maxIdx = i;
        } else if (probs[i] > secondProb) {
          secondProb = probs[i];
        }
      }

      inputTensor.dispose();
      prediction.dispose();

      if (typeof window !== "undefined" && (window as any).__VSL_DEBUG) {
        console.table(VSL_CLASSES.map((c, i) => ({ class: c, prob: probs[i].toFixed(3) })));
      }

      this.acceptPrediction(VSL_CLASSES[maxIdx], maxProb, maxProb - secondProb);
    } catch (err) {
      console.error("[VSL] Inference error:", err);
    }
  }

  private acceptPrediction(classCode: string, confidence: number, margin: number): void {
    this.predictionWindow.push({ classCode, confidence, margin });
    if (this.predictionWindow.length > 5) this.predictionWindow.shift();
    if (this.predictionWindow.length < 3) return;

    const votes = this.predictionWindow.filter((it) => it.classCode === classCode);
    const voteCount = votes.length;
    const avgConf = votes.reduce((s, it) => s + it.confidence, 0) / voteCount;
    const avgMargin = votes.reduce((s, it) => s + it.margin, 0) / voteCount;

    const minVotes = classCode === "khan_cap" ? 5 : 3;
    const minConf = classCode === "khan_cap" ? 0.97 : 0.78;
    const minMargin = classCode === "khan_cap" ? 0.45 : 0.12;
    if (voteCount < minVotes || avgConf < minConf || avgMargin < minMargin) return;

    const now = performance.now();
    if (this.lastEmittedClassCode === classCode && now - this.lastEmittedAt < 2500) return;

    this.lastEmittedClassCode = classCode;
    this.lastEmittedAt = now;
    this.onResultCallback?.(VSL_LABELS[classCode] || classCode, Math.round(avgConf * 100));
  }

  // ─────────────────────────────────────────────────────────────────────
  // Overlay
  // ─────────────────────────────────────────────────────────────────────

  private drawOverlay(
    canvas: HTMLCanvasElement,
    handR: HandLandmarkerResult,
    faceR: FaceLandmarkerResult,
    poseR: PoseLandmarkerResult,
  ): void {
    const ctx = canvas.getContext("2d");
    if (!ctx || !this.videoElement) return;

    // Sync canvas resolution với video stream NATIVE dimensions, không
    // phải DOM clientWidth/Height. Lý do:
    //   - Landmark MediaPipe trả về normalized [0..1] theo VIDEO frame.
    //   - <video> CSS dùng `object-cover` → crop video để fill DOM box.
    //   - <canvas> stretched theo DOM box (không crop).
    //   Nếu canvas.width = clientWidth (DOM), khi nhân với x ∈ [0..1] ta
    //   được toạ độ trong DOM box, KHÔNG khớp với chỗ pixel video thật
    //   sự được render → mesh lệch (đặc biệt rõ khi đứng gần camera vì
    //   crop ratio lệch nhiều hơn).
    //
    // Cách đúng: set canvas internal resolution = video native, và để
    // CSS xử lý cùng `object-cover` để hai layer crop đồng bộ.
    const vw = this.videoElement.videoWidth;
    const vh = this.videoElement.videoHeight;
    if (vw > 0 && vh > 0 && (canvas.width !== vw || canvas.height !== vh)) {
      canvas.width = vw;
      canvas.height = vh;
    }
    if (canvas.width === 0 || canvas.height === 0) return;

    ctx.clearRect(0, 0, canvas.width, canvas.height);
    const W = canvas.width;
    const H = canvas.height;

    // ── Pose skeleton (sky blue) ──
    const poseLM = poseR.landmarks?.[0];
    if (poseLM && poseLM.length > 0) {
      ctx.strokeStyle = "rgba(56, 189, 248, 0.85)"; // sky-400
      ctx.fillStyle = "rgba(56, 189, 248, 0.95)";
      ctx.lineWidth = Math.max(2, W / 480); // lineWidth scale theo res
      for (const [a, b] of POSE_CONNECTIONS) {
        const p1 = poseLM[a], p2 = poseLM[b];
        if (!p1 || !p2) continue;
        ctx.beginPath();
        ctx.moveTo(p1.x * W, p1.y * H);
        ctx.lineTo(p2.x * W, p2.y * H);
        ctx.stroke();
      }
      // "Cổ": 1 line từ midpoint tai (7, 8) xuống midpoint vai (11, 12).
      // Tự tính midpoint thay vì nối tai-vai trực tiếp → tránh tam giác
      // nhọn vì đầu hẹp và vai rộng.
      const earL = poseLM[7], earR = poseLM[8];
      const shoL = poseLM[11], shoR = poseLM[12];
      if (earL && earR && shoL && shoR) {
        const headMidX = (earL.x + earR.x) / 2;
        const headMidY = (earL.y + earR.y) / 2;
        const shoMidX = (shoL.x + shoR.x) / 2;
        const shoMidY = (shoL.y + shoR.y) / 2;
        ctx.beginPath();
        ctx.moveTo(headMidX * W, headMidY * H);
        ctx.lineTo(shoMidX * W, shoMidY * H);
        ctx.stroke();
      }
      const dotR = Math.max(2.5, W / 320);
      for (const idx of POSE_UPPER_BODY) {
        const p = poseLM[idx];
        if (!p) continue;
        ctx.beginPath();
        ctx.arc(p.x * W, p.y * H, dotR, 0, 2 * Math.PI);
        ctx.fill();
      }
    }

    // ── Face contours (pink) ──
    const faceLM = faceR.faceLandmarks?.[0];
    if (faceLM && faceLM.length > 0) {
      ctx.strokeStyle = "rgba(244, 114, 182, 0.55)"; // pink-400 mỏng
      ctx.lineWidth = Math.max(1.2, W / 800);
      for (const group of FACE_CONTOUR_GROUPS) {
        ctx.beginPath();
        for (let i = 0; i < group.indices.length; i++) {
          const lm = faceLM[group.indices[i]];
          if (!lm) continue;
          const x = lm.x * W;
          const y = lm.y * H;
          if (i === 0) ctx.moveTo(x, y);
          else ctx.lineTo(x, y);
        }
        if (group.closed) ctx.closePath();
        ctx.stroke();
      }

      // Highlight lips bằng dot đậm hơn để xác nhận trực quan có track môi.
      ctx.fillStyle = "rgba(244, 114, 182, 0.95)";
      const LIP_GROUPS = FACE_CONTOUR_GROUPS.filter((g) => g.name.startsWith("lips"));
      const lipDotR = Math.max(1.6, W / 640);
      for (const g of LIP_GROUPS) {
        for (const idx of g.indices) {
          const lm = faceLM[idx];
          if (!lm) continue;
          ctx.beginPath();
          ctx.arc(lm.x * W, lm.y * H, lipDotR, 0, 2 * Math.PI);
          ctx.fill();
        }
      }
    }

    // ── Hand skeleton (green) ──
    if (handR.landmarks) {
      ctx.strokeStyle = "rgba(34, 197, 94, 0.85)";
      ctx.fillStyle = "rgba(34, 197, 94, 0.95)";
      ctx.lineWidth = Math.max(2.5, W / 400);
      const handDotR = Math.max(3.2, W / 280);
      for (const handLM of handR.landmarks) {
        for (const [a, b] of HAND_CONNECTIONS) {
          const p1 = handLM[a], p2 = handLM[b];
          if (!p1 || !p2) continue;
          ctx.beginPath();
          ctx.moveTo(p1.x * W, p1.y * H);
          ctx.lineTo(p2.x * W, p2.y * H);
          ctx.stroke();
        }
        for (const lm of handLM) {
          ctx.beginPath();
          ctx.arc(lm.x * W, lm.y * H, handDotR, 0, 2 * Math.PI);
          ctx.fill();
        }
      }
    }
  }
}

// Re-export feature dims để consumer biết shape tổng quan.
export { FULL_FEATURE_DIM };

// ─── Vector helpers (3-D, image-normalized space) ─────────────────────
type V3 = { x: number; y: number; z: number };
const sub = (a: V3, b: V3): V3 => ({ x: a.x - b.x, y: a.y - b.y, z: a.z - b.z });
const mid = (a: V3, b: V3): V3 => ({ x: (a.x + b.x) / 2, y: (a.y + b.y) / 2, z: (a.z + b.z) / 2 });
const dot = (a: V3, b: V3): number => a.x * b.x + a.y * b.y + a.z * b.z;
const norm = (a: V3): number => Math.hypot(a.x, a.y, a.z);
const scale = (a: V3, k: number): V3 => ({ x: a.x * k, y: a.y * k, z: a.z * k });
const cross = (a: V3, b: V3): V3 => ({
  x: a.y * b.z - a.z * b.y,
  y: a.z * b.x - a.x * b.z,
  z: a.x * b.y - a.y * b.x,
});
