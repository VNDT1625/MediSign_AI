import '../models/health_profile.dart';

/// Accessibility configuration derived from HealthProfile.difficulties.
///
/// Tâm lý thiết kế: User đã trả lời về khó khăn trong onboarding.
/// Service này biến data đó thành các giá trị cụ thể để UI tự điều chỉnh.
///
/// Nguyên tắc: Nếu user nói "mắt kém" → font to hơn, contrast cao hơn.
/// Nếu user nói "tay run" → nút lớn hơn, khoảng cách rộng hơn.
class AccessibilityConfig {
  AccessibilityConfig._();

  static final AccessibilityConfig _instance = AccessibilityConfig._();
  static AccessibilityConfig get instance => _instance;

  Set<Difficulty> _difficulties = {};

  /// Gọi sau onboarding để cập nhật config
  void update(Set<Difficulty> difficulties) {
    _difficulties = difficulties;
  }

  // ═══════════════════════════════════════════════
  //  FLAGS
  // ═══════════════════════════════════════════════

  bool get hasVisionDifficulty => _difficulties.contains(Difficulty.vision);
  bool get hasHearingDifficulty => _difficulties.contains(Difficulty.hearing);
  bool get hasSpeechDifficulty => _difficulties.contains(Difficulty.speech);
  bool get hasMobilityDifficulty => _difficulties.contains(Difficulty.mobility);
  bool get hasCognitiveDifficulty => _difficulties.contains(Difficulty.cognitive);
  bool get hasNoDifficulty =>
      _difficulties.isEmpty || _difficulties.contains(Difficulty.none);

  // ═══════════════════════════════════════════════
  //  COMPUTED VALUES — UI reads these to adapt
  // ═══════════════════════════════════════════════

  /// Font scale factor (1.0 = default, 1.25 = vision impaired)
  double get fontScale => hasVisionDifficulty ? 1.2 : 1.0;

  /// Minimum touch target size (48dp = WCAG, 56dp = vision/mobility)
  double get minTouchTarget =>
      (hasVisionDifficulty || hasMobilityDifficulty) ? 56.0 : 48.0;

  /// Extra padding between interactive elements (motor difficulties)
  double get elementSpacing => hasMobilityDifficulty ? 16.0 : 12.0;

  /// Whether to auto-start voice mode in consult (for speech/vision)
  bool get preferVoiceInput => hasVisionDifficulty && !hasSpeechDifficulty;

  /// Whether to show sign language mode prominently
  bool get preferSignLanguage =>
      hasHearingDifficulty || hasSpeechDifficulty;

  /// Whether to simplify UI (fewer elements, bigger buttons)
  bool get simplifiedMode => hasCognitiveDifficulty;

  /// Whether to use high contrast colors
  bool get highContrast => hasVisionDifficulty;

  /// Card border radius (larger for vision impaired — easier to distinguish)
  double get cardRadius => hasVisionDifficulty ? 24.0 : 20.0;

  /// Button height
  double get buttonHeight =>
      (hasVisionDifficulty || hasMobilityDifficulty) ? 60.0 : 52.0;

  /// Icon size multiplier
  double get iconScale =>
      hasVisionDifficulty ? 1.3 : 1.0;

  /// Thời gian hiển thị SnackBar / Toast (dài hơn cho cognitive)
  int get toastDurationMs => hasCognitiveDifficulty ? 5000 : 3000;

  /// Summary mô tả config hiện tại (cho debug/profile page)
  String get summary {
    if (hasNoDifficulty) return 'Mặc định';
    final parts = <String>[];
    if (hasVisionDifficulty) parts.add('Chữ to, tương phản cao');
    if (hasHearingDifficulty) parts.add('Ưu tiên hình ảnh');
    if (hasSpeechDifficulty) parts.add('Ưu tiên ký hiệu');
    if (hasMobilityDifficulty) parts.add('Nút lớn, khoảng cách rộng');
    if (hasCognitiveDifficulty) parts.add('Giao diện đơn giản');
    return parts.join(' · ');
  }
}
