enum ConsultMode {
  hybrid,
  local,
  cloud,
}

extension ConsultModeLabel on ConsultMode {
  String get label {
    switch (this) {
      case ConsultMode.hybrid:
        return 'Hybrid';
      case ConsultMode.local:
        return 'Local';
      case ConsultMode.cloud:
        return 'Cloud';
    }
  }

  /// User-friendly Vietnamese title (no technical jargon).
  String get title {
    switch (this) {
      case ConsultMode.hybrid:
        return 'Tốt nhất cho tôi';
      case ConsultMode.local:
        return 'Riêng tư tuyệt đối';
      case ConsultMode.cloud:
        return 'Nhẹ nhất';
    }
  }

  /// Short description explaining what each mode means.
  String get description {
    switch (this) {
      case ConsultMode.hybrid:
        return 'AI mạnh + Bảo mật cao';
      case ConsultMode.local:
        return 'Không gửi gì lên mạng';
      case ConsultMode.cloud:
        return 'Cần internet, máy yếu OK';
    }
  }

  /// Emoji icon for visual identification.
  String get emoji {
    switch (this) {
      case ConsultMode.hybrid:
        return '🔀';
      case ConsultMode.local:
        return '🔒';
      case ConsultMode.cloud:
        return '☁️';
    }
  }

  /// Whether this mode is the recommended default.
  bool get isRecommended => this == ConsultMode.hybrid;

  /// Semantic label for screen readers.
  String get semanticLabel {
    switch (this) {
      case ConsultMode.hybrid:
        return 'Chế độ kết hợp. Tốt nhất cho tôi. AI mạnh và bảo mật cao.';
      case ConsultMode.local:
        return 'Chế độ riêng tư. Mọi thứ ở trên máy bạn, không gửi dữ liệu lên mạng.';
      case ConsultMode.cloud:
        return 'Chế độ nhẹ. Cần internet, phù hợp máy yếu.';
    }
  }
}
