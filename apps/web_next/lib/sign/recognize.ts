/**
 * `lib/sign/recognize.ts` — client-side wrapper gọi route handler proxy
 * `/api/sign/recognize`.
 *
 * Tách ra file riêng để:
 *   - Component composer chỉ phải `import { recognizeSignVideo }` —
 *     không lo về fetch / FormData / error normalization.
 *   - Test có thể stub bằng `vi.mock("@/lib/sign/recognize")`.
 */

export type SignRecognitionResult = {
  text: string;
  confidence: number;
  notes: string;
};

export type SignRecognitionError = {
  code: string;
  message: string;
};

/** Class lỗi để component bắt và hiển thị toast/banner. */
export class SignRecognitionFailure extends Error {
  readonly code: string;
  readonly status: number;
  constructor(code: string, message: string, status: number) {
    super(message);
    this.name = "SignRecognitionFailure";
    this.code = code;
    this.status = status;
  }
}

/**
 * Gửi blob video lên `/api/sign/recognize`. Trả về câu tiếng Việt
 * Gemini nhận diện được.
 *
 * @throws {SignRecognitionFailure} khi server trả non-2xx hoặc body lỗi.
 */
export async function recognizeSignVideo(
  blob: Blob,
  signal?: AbortSignal,
): Promise<SignRecognitionResult> {
  const form = new FormData();
  // File phía Gemini sẽ infer MIME từ blob.type — đặt tên file để dễ debug.
  form.append("video", blob, "sign.webm");

  const response = await fetch("/api/sign/recognize", {
    method: "POST",
    body: form,
    signal,
  });

  if (!response.ok) {
    let errBody: SignRecognitionError | null = null;
    try {
      errBody = (await response.json()) as SignRecognitionError;
    } catch {
      // Body không phải JSON — dùng statusText.
    }
    throw new SignRecognitionFailure(
      errBody?.code ?? "SIGN_UNKNOWN_ERROR",
      errBody?.message ?? response.statusText ?? "Lỗi không xác định",
      response.status,
    );
  }

  const data = (await response.json()) as SignRecognitionResult;
  return data;
}
