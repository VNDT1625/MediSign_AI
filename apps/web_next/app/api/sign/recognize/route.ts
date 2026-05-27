/**
 * `app/api/sign/recognize/route.ts` — Next.js Route Handler proxy.
 *
 * Mục đích:
 *   1. Nhận multipart/form-data từ trình duyệt: 1 blob video (webm/mp4).
 *   2. Gọi Google Gemini Vision (free tier) để nhận diện ngôn ngữ ký hiệu
 *      Việt (VSL) trong video → trả về 1 chuỗi tiếng Việt mô tả triệu chứng.
 *   3. Giấu `GOOGLE_GEMINI_API_KEY` ở server, browser không thấy.
 *
 * Tại sao là Route Handler riêng (không gộp vào /ai/chat):
 *   - VSL recognition là model multimodal video, không phải LLM text-only
 *     của FastAPI backend hiện tại.
 *   - Tách proxy giúp giấu API key của Google + dễ swap sang model khác
 *     (custom VSL model) sau này — UI chỉ cần đổi 1 endpoint.
 *
 * Strategy upload:
 *   - Video < 15s, < 18MB → dùng inline (base64) trong generateContent.
 *     Đây là path nhanh nhất; Gemini docs giới hạn 20MB / request.
 *   - Video lớn hơn → trả 413 (UI ép user record ngắn lại). Phase 2 có thể
 *     chuyển sang Files API resumable upload.
 *
 * Free tier: Gemini 2.5 Flash 10 RPM / 250 RPD / 250K TPM (Dec 2025).
 *   - 1 video ~= vài chục K token → đủ rộng cho cả demo + dev.
 *   - Khi vượt limit, response 429 → UI hiển thị "thử lại sau 1 phút".
 *
 * @see https://ai.google.dev/gemini-api/docs/video-understanding
 */

import { NextResponse, type NextRequest } from "next/server";

// Cần Node runtime (multipart parse + base64 encode buffer lớn).
export const runtime = "nodejs";
// Phòng case framework cache empty body.
export const dynamic = "force-dynamic";

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const GEMINI_MODEL = "gemini-2.5-flash";
const GEMINI_API_BASE = "https://generativelanguage.googleapis.com/v1beta";

/** Tối đa 18MB (Gemini limit 20MB, để 2MB margin cho prompt + json). */
const MAX_VIDEO_BYTES = 18 * 1024 * 1024;

/** Tổng timeout cho cả request (record video → recognize): 60s. */
const REQUEST_TIMEOUT_MS = 60_000;

/**
 * System prompt yêu cầu Gemini trả JSON cố định để parser an toàn.
 * Có schema rõ ràng — mọi câu trả lời ngoài JSON sẽ rớt vào fallback.
 */
const PROMPT = `Bạn là một trợ lý nhận diện ngôn ngữ ký hiệu Việt Nam (VSL — Vietnamese Sign Language).

Người trong video đang ký hiệu một triệu chứng y tế hoặc một câu hỏi y tế bằng VSL.

NHIỆM VỤ:
1. Quan sát kỹ cử chỉ tay, biểu cảm khuôn mặt, và chuyển động của người ký hiệu.
2. Dịch những gì họ đang ký hiệu thành MỘT câu tiếng Việt tự nhiên, ngắn gọn, dễ hiểu.
3. Tập trung vào ngữ cảnh y tế (triệu chứng, đau, mức độ, thời gian).
4. Nếu video quá ngắn / quá mờ / không nhìn rõ tay người, trả về câu mô tả chung chung.

QUAN TRỌNG:
- Trả về DUY NHẤT một object JSON hợp lệ, không kèm markdown, không kèm giải thích.
- Schema:
  {
    "text": "<câu tiếng Việt mô tả ý người ký hiệu>",
    "confidence": <số thực 0.0 - 1.0>,
    "notes": "<ghi chú ngắn nếu video không rõ, có thể để rỗng>"
  }

VÍ DỤ OUTPUT TỐT:
  {"text": "Tôi bị đau bụng từ hôm qua", "confidence": 0.85, "notes": ""}
  {"text": "Tôi bị sốt cao và ho nhiều", "confidence": 0.78, "notes": ""}
  {"text": "Tôi cần lời khuyên y tế", "confidence": 0.55, "notes": "Cử chỉ chung chung, không rõ triệu chứng cụ thể"}`;

// ---------------------------------------------------------------------------
// Response shapes
// ---------------------------------------------------------------------------

type SignRecognitionResponse = {
  text: string;
  confidence: number;
  notes: string;
};

type ApiErrorPayload = {
  code: string;
  message: string;
};

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function errorResponse(
  status: number,
  code: string,
  message: string,
): NextResponse<ApiErrorPayload> {
  return NextResponse.json({ code, message }, { status });
}

/**
 * Gọi Gemini generateContent với video inline (base64).
 * Trả về raw text từ candidates[0].content.parts[0].text.
 */
async function callGemini(
  apiKey: string,
  videoBase64: string,
  mimeType: string,
  signal: AbortSignal,
): Promise<string> {
  const url = `${GEMINI_API_BASE}/models/${GEMINI_MODEL}:generateContent?key=${encodeURIComponent(apiKey)}`;

  const body = {
    contents: [
      {
        role: "user",
        parts: [
          { text: PROMPT },
          {
            inlineData: {
              mimeType,
              data: videoBase64,
            },
          },
        ],
      },
    ],
    generationConfig: {
      // Buộc trả JSON.
      responseMimeType: "application/json",
      // Giảm hallucination, ưu tiên ổn định.
      temperature: 0.2,
      // Giới hạn output để tiết kiệm token (câu mô tả y tế thường < 200 chars).
      maxOutputTokens: 256,
    },
  };

  const response = await fetch(url, {
    method: "POST",
    headers: {
      "content-type": "application/json",
      accept: "application/json",
    },
    body: JSON.stringify(body),
    signal,
  });

  if (!response.ok) {
    const errBody = await response.text().catch(() => "");
    throw new Error(
      `Gemini API ${response.status}: ${errBody.slice(0, 200) || response.statusText}`,
    );
  }

  const data = (await response.json()) as {
    candidates?: Array<{
      content?: { parts?: Array<{ text?: string }> };
      finishReason?: string;
    }>;
  };

  const text = data.candidates?.[0]?.content?.parts?.[0]?.text;
  if (typeof text !== "string" || text.length === 0) {
    throw new Error("Gemini trả về response rỗng.");
  }

  return text;
}

/**
 * Parse JSON Gemini trả về thành response chuẩn.
 * Gemini đôi khi vẫn wrap trong ```json``` dù đã set responseMimeType,
 * nên tự strip code fence trước khi JSON.parse.
 */
function parseGeminiJson(raw: string): SignRecognitionResponse {
  let cleaned = raw.trim();
  // Strip markdown code fences nếu có.
  if (cleaned.startsWith("```")) {
    cleaned = cleaned.replace(/^```(?:json)?\s*/i, "").replace(/```\s*$/, "");
  }

  const parsed: unknown = JSON.parse(cleaned);
  if (!parsed || typeof parsed !== "object") {
    throw new Error("Gemini không trả về JSON object.");
  }

  const obj = parsed as Record<string, unknown>;
  const text = typeof obj.text === "string" ? obj.text.trim() : "";
  const confidence = typeof obj.confidence === "number" ? obj.confidence : 0;
  const notes = typeof obj.notes === "string" ? obj.notes : "";

  if (!text) {
    throw new Error("Gemini trả về JSON nhưng thiếu trường text.");
  }

  return {
    text,
    confidence: Math.min(1, Math.max(0, confidence)),
    notes,
  };
}

// ---------------------------------------------------------------------------
// Handler
// ---------------------------------------------------------------------------

export async function POST(req: NextRequest): Promise<NextResponse> {
  const apiKey = process.env.GOOGLE_GEMINI_API_KEY;
  if (!apiKey) {
    return errorResponse(
      500,
      "SIGN_API_NOT_CONFIGURED",
      "Server chưa cấu hình GOOGLE_GEMINI_API_KEY.",
    );
  }

  // Parse multipart form-data.
  let formData: FormData;
  try {
    formData = await req.formData();
  } catch {
    return errorResponse(
      400,
      "SIGN_INVALID_FORM",
      "Body không phải multipart/form-data hợp lệ.",
    );
  }

  const file = formData.get("video");
  if (!(file instanceof Blob)) {
    return errorResponse(
      400,
      "SIGN_VIDEO_MISSING",
      "Thiếu trường 'video' trong form-data.",
    );
  }

  if (file.size === 0) {
    return errorResponse(400, "SIGN_VIDEO_EMPTY", "Video rỗng.");
  }

  if (file.size > MAX_VIDEO_BYTES) {
    return errorResponse(
      413,
      "SIGN_VIDEO_TOO_LARGE",
      `Video lớn hơn ${Math.round(MAX_VIDEO_BYTES / 1024 / 1024)}MB. Hãy quay ngắn hơn (dưới 15 giây).`,
    );
  }

  const mimeType = file.type || "video/webm";

  // Convert Blob → base64 (Node Buffer là cách nhanh nhất).
  const arrayBuffer = await file.arrayBuffer();
  const videoBase64 = Buffer.from(arrayBuffer).toString("base64");

  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);

  try {
    const raw = await callGemini(apiKey, videoBase64, mimeType, controller.signal);
    const parsed = parseGeminiJson(raw);
    return NextResponse.json(parsed);
  } catch (err) {
    const isAbort =
      err instanceof Error &&
      (err.name === "AbortError" || /aborted/i.test(err.message));
    if (isAbort) {
      return errorResponse(
        504,
        "SIGN_TIMEOUT",
        "Quá thời gian chờ. Hãy thử lại với video ngắn hơn.",
      );
    }
    const message = err instanceof Error ? err.message : "Lỗi không xác định.";
    // eslint-disable-next-line no-console
    console.error("[/api/sign/recognize] error:", message);
    return errorResponse(
      502,
      "SIGN_UPSTREAM_ERROR",
      "Không nhận diện được video. Hãy quay lại với ánh sáng tốt hơn và cử chỉ rõ ràng.",
    );
  } finally {
    clearTimeout(timer);
  }
}
