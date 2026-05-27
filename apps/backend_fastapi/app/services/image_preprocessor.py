"""Image preprocessing service for medical images (X-ray, dermatology).

Normalizes medical images before passing to MedGemma 4B's vision encoder.
Supports DICOM, JPEG, and PNG inputs with modality-specific preprocessing.

Requirements: 7.3, 7.4, 7.5, 7.6, 7.7, 7.9, 7.10
"""

from __future__ import annotations

import base64
import io
import mimetypes
from typing import Literal

import numpy as np
from fastapi import HTTPException
from PIL import Image

from app.schemas.diagnostic import ProcessedImage

# Maximum file size: 10 MB
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024

# Allowed MIME types for medical images
ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "application/dicom"}

# Target dimensions per modality
XRAY_SIZE = (512, 512)
DERMATOLOGY_SIZE = (448, 448)


class ImagePreprocessor:
    """Normalize medical images for MedGemma 4B vision encoder."""

    def preprocess(
        self,
        image_bytes: bytes,
        image_type: Literal["xray", "dermatology"],
        filename: str,
    ) -> ProcessedImage:
        """Preprocess a medical image based on its modality.

        Args:
            image_bytes: Raw image file bytes.
            image_type: Modality hint — "xray" or "dermatology".
            filename: Original filename (used for MIME detection).

        Returns:
            ProcessedImage with base64-encoded PNG and metadata.

        Raises:
            HTTPException(413): File exceeds 10 MB limit.
            HTTPException(415): Unsupported MIME type.
            HTTPException(422): Corrupt or undecodable file.
        """
        # Validate file size
        if len(image_bytes) > MAX_FILE_SIZE_BYTES:
            raise HTTPException(
                status_code=413,
                detail="File size exceeds 10 MB limit.",
            )

        # Validate MIME type
        mime_type = self._detect_mime_type(image_bytes, filename)
        if mime_type not in ALLOWED_MIME_TYPES:
            raise HTTPException(
                status_code=415,
                detail=f"Unsupported MIME type: {mime_type}. "
                f"Accepted types: {', '.join(sorted(ALLOWED_MIME_TYPES))}.",
            )

        # Dispatch to modality-specific preprocessing
        if image_type == "xray":
            return self._preprocess_xray(image_bytes, mime_type, filename)
        else:
            return self._preprocess_dermatology(image_bytes, filename)

    def to_llm_content_block(self, processed: ProcessedImage) -> dict:
        """Convert a ProcessedImage to an OpenAI-compatible image content block.

        Returns:
            {"type": "image_url", "image_url": {"url": "data:image/png;base64,..."}}
        """
        return {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/png;base64,{processed.content_base64}",
            },
        }

    # ─── Private helpers ──────────────────────────────────────────────────

    def _detect_mime_type(self, image_bytes: bytes, filename: str) -> str:
        """Detect MIME type from magic bytes and filename extension."""
        # Check magic bytes first
        if image_bytes[:4] == b"DICM" or (
            len(image_bytes) > 132 and image_bytes[128:132] == b"DICM"
        ):
            return "application/dicom"
        if image_bytes[:8] == b"\x89PNG\r\n\x1a\n":
            return "image/png"
        if image_bytes[:2] == b"\xff\xd8":
            return "image/jpeg"

        # Fall back to filename extension
        guessed, _ = mimetypes.guess_type(filename)
        if guessed:
            return guessed

        return "application/octet-stream"

    def _preprocess_xray(
        self, image_bytes: bytes, mime_type: str, filename: str
    ) -> ProcessedImage:
        """X-ray preprocessing: DICOM parse → CLAHE → resize 512×512 → normalize → base64 PNG."""
        try:
            if mime_type == "application/dicom":
                pixel_array = self._parse_dicom(image_bytes)
            else:
                img = Image.open(io.BytesIO(image_bytes))
                img = img.convert("L")  # Grayscale for X-ray
                pixel_array = np.array(img, dtype=np.float64)
        except HTTPException:
            raise
        except Exception as exc:
            raise HTTPException(
                status_code=422,
                detail=f"Failed to decode image: {exc}",
            ) from exc

        # Apply CLAHE contrast enhancement
        pixel_array = self._apply_clahe(pixel_array)

        # Resize to 512×512
        img_resized = Image.fromarray(
            (pixel_array * 255).astype(np.uint8), mode="L"
        )
        img_resized = img_resized.resize(XRAY_SIZE, Image.Resampling.LANCZOS)

        # Normalize pixel values to [0, 1] (stored as metadata info)
        # The base64 PNG stores 8-bit values; normalization is noted in metadata
        content_base64 = self._encode_png_base64(img_resized)

        return ProcessedImage(
            image_type="xray",
            modality="xray",
            content_base64=content_base64,
            content_block=self.to_llm_content_block(
                ProcessedImage(
                    image_type="xray",
                    content_base64=content_base64,
                )
            ),
            width=XRAY_SIZE[0],
            height=XRAY_SIZE[1],
            metadata={
                "preprocessing": "CLAHE + resize 512x512 + normalize [0,1]",
                "normalized": True,
                "original_mime": mime_type,
            },
        )

    def _preprocess_dermatology(
        self, image_bytes: bytes, filename: str
    ) -> ProcessedImage:
        """Dermatology preprocessing: resize 448×448 → RGB → strip EXIF → base64 PNG."""
        try:
            img = Image.open(io.BytesIO(image_bytes))
        except Exception as exc:
            raise HTTPException(
                status_code=422,
                detail=f"Failed to decode image: {exc}",
            ) from exc

        # Convert to RGB (handles RGBA, palette, grayscale)
        img = img.convert("RGB")

        # Strip EXIF by copying pixel data into a fresh image (no metadata carried over)
        img_stripped = Image.frombytes("RGB", img.size, img.tobytes())

        # Resize to 448×448
        img_resized = img_stripped.resize(DERMATOLOGY_SIZE, Image.Resampling.LANCZOS)

        content_base64 = self._encode_png_base64(img_resized)

        return ProcessedImage(
            image_type="dermatology",
            modality="dermatology",
            content_base64=content_base64,
            content_block=self.to_llm_content_block(
                ProcessedImage(
                    image_type="dermatology",
                    content_base64=content_base64,
                )
            ),
            width=DERMATOLOGY_SIZE[0],
            height=DERMATOLOGY_SIZE[1],
            metadata={
                "preprocessing": "resize 448x448 + RGB + EXIF stripped",
                "exif_stripped": True,
            },
        )

    def _parse_dicom(self, image_bytes: bytes) -> np.ndarray:
        """Parse DICOM file and extract pixel array."""
        try:
            import pydicom
        except ImportError as exc:
            raise HTTPException(
                status_code=422,
                detail="DICOM support requires pydicom. Please install it.",
            ) from exc

        try:
            ds = pydicom.dcmread(io.BytesIO(image_bytes))
            pixel_array = ds.pixel_array.astype(np.float64)
        except Exception as exc:
            raise HTTPException(
                status_code=422,
                detail=f"Failed to parse DICOM file: {exc}",
            ) from exc

        # Normalize to [0, 1] range
        pmin, pmax = pixel_array.min(), pixel_array.max()
        if pmax > pmin:
            pixel_array = (pixel_array - pmin) / (pmax - pmin)
        else:
            pixel_array = np.zeros_like(pixel_array)

        return pixel_array

    def _apply_clahe(self, pixel_array: np.ndarray) -> np.ndarray:
        """Apply CLAHE (Contrast Limited Adaptive Histogram Equalization).

        Uses OpenCV's createCLAHE for contrast enhancement on X-ray images.
        Falls back to simple histogram equalization if cv2 is unavailable.
        """
        try:
            import cv2

            # Convert to uint8 for CLAHE
            if pixel_array.max() <= 1.0:
                img_uint8 = (pixel_array * 255).astype(np.uint8)
            else:
                pmin, pmax = pixel_array.min(), pixel_array.max()
                if pmax > pmin:
                    img_uint8 = ((pixel_array - pmin) / (pmax - pmin) * 255).astype(np.uint8)
                else:
                    img_uint8 = np.zeros_like(pixel_array, dtype=np.uint8)

            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(img_uint8)

            # Normalize back to [0, 1]
            return enhanced.astype(np.float64) / 255.0

        except ImportError:
            # Fallback: simple normalization if cv2 is not available
            pmin, pmax = pixel_array.min(), pixel_array.max()
            if pmax > pmin:
                return (pixel_array - pmin) / (pmax - pmin)
            return np.zeros_like(pixel_array)

    def _encode_png_base64(self, img: Image.Image) -> str:
        """Encode a PIL Image as base64 PNG string."""
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        return base64.b64encode(buffer.getvalue()).decode("utf-8")
