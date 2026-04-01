import 'dart:async';

import '../models/communication_mode.dart';

/// ══════════════════════════════════════════════════════════════
/// AI TRIAGE SERVICE — Skeleton for AI-powered symptom analysis
/// ══════════════════════════════════════════════════════════════
///
/// HOW TO INTEGRATE REAL AI:
/// 1. Option A — On-device (offline/local mode):
///    - Add: tflite_flutter: ^0.10.4
///    - Train a classifier: symptoms → triage level + advice
///    - Put model in assets/models/triage_model.tflite
///
/// 2. Option B — Cloud API:
///    - Use Gemini, GPT-4, or custom medical AI API
///    - Send structured symptom data → receive triage result
///
/// 3. Option C — Hybrid:
///    - On-device for basic triage (fast, offline)
///    - Cloud API for detailed analysis (when connected)
///
/// 4. Create `RealTriageService` that implements `TriageService`
///
/// 5. In app.dart or DI, replace:
///    MockTriageService() → RealTriageService()
/// ══════════════════════════════════════════════════════════════

/// Input data for triage analysis.
class TriageInput {
  const TriageInput({
    this.bodyRegions = const {},
    this.symptoms = const {},
    this.severity,
    this.duration,
    this.voiceTranscript,
    this.signSequence = const [],
    this.textDescription,
    this.patientAge,
    this.patientGender,
  });

  /// Selected body regions from body map.
  final Set<BodyRegion> bodyRegions;

  /// Selected symptom icons.
  final Set<SymptomIcon> symptoms;

  /// Severity level (from severity picker).
  final Severity? severity;

  /// Duration (from duration picker).
  final SymptomDuration? duration;

  /// Raw voice transcript (from STT).
  final String? voiceTranscript;

  /// Sequence of recognized signs (from sign language).
  final List<String> signSequence;

  /// Free-text description (from text mode).
  final String? textDescription;

  /// Optional patient demographics.
  final int? patientAge;
  final String? patientGender;

  /// Merge all inputs into a single text description for AI.
  String toPrompt() {
    final parts = <String>[];

    if (bodyRegions.isNotEmpty) {
      parts.add('Vùng đau: ${bodyRegions.map((r) => r.label).join(', ')}');
    }
    if (symptoms.isNotEmpty) {
      parts.add('Triệu chứng: ${symptoms.map((s) => s.label).join(', ')}');
    }
    if (severity != null) {
      parts.add('Mức độ: ${severity!.label}');
    }
    if (duration != null) {
      parts.add('Thời gian: ${duration!.label}');
    }
    if (voiceTranscript != null && voiceTranscript!.isNotEmpty) {
      parts.add('Mô tả giọng nói: $voiceTranscript');
    }
    if (signSequence.isNotEmpty) {
      parts.add('Ký hiệu: ${signSequence.join(' → ')}');
    }
    if (textDescription != null && textDescription!.isNotEmpty) {
      parts.add('Mô tả văn bản: $textDescription');
    }
    if (patientAge != null) {
      parts.add('Tuổi: $patientAge');
    }
    if (patientGender != null) {
      parts.add('Giới tính: $patientGender');
    }

    return parts.join('\n');
  }
}

/// Output from triage analysis.
class TriageOutput {
  const TriageOutput({
    required this.level,
    required this.summary,
    required this.advice,
    this.confidence = 0.0,
    this.rawResponse,
  });

  /// Triage level (green/yellow/red).
  final TriageLevel level;

  /// Short summary of the analysis.
  final String summary;

  /// List of advice items with emoji and descriptions.
  final List<TriageAdvice> advice;

  /// Confidence score of the analysis, 0.0 to 1.0.
  final double confidence;

  /// Raw response from AI (for debugging).
  final String? rawResponse;
}

/// A single advice item.
class TriageAdvice {
  const TriageAdvice({
    required this.emoji,
    required this.title,
    required this.description,
    required this.color,
  });

  final String emoji;
  final String title;
  final String description;
  final dynamic color; // Color type — using dynamic to avoid flutter import in service
}

/// Abstract interface for triage AI.
/// Implement this to swap in your real AI.
abstract class TriageService {
  /// Initialize the service (load model, warm up API, etc.).
  Future<bool> initialize();

  /// Whether the service is ready to analyze.
  bool get isReady;

  /// Analyze symptoms and return triage result.
  /// This is the main entry point for all consultation modes.
  Future<TriageOutput> analyze(TriageInput input);

  /// Analyze free-text symptoms (for voice/text mode).
  /// Convenience method that creates a TriageInput internally.
  Future<TriageOutput> analyzeText(String text);

  /// Release resources.
  void dispose();
}

/// ══════════════════════════════════════════════════════════════
/// MOCK IMPLEMENTATION — Replace with RealTriageService later.
/// ══════════════════════════════════════════════════════════════
class MockTriageService implements TriageService {
  bool _isReady = false;

  @override
  Future<bool> initialize() async {
    // TODO: Replace with real initialization
    // Example (on-device):
    //   _interpreter = await Interpreter.fromAsset('assets/models/triage_model.tflite');
    //   _labels = await rootBundle.loadString('assets/models/triage_labels.txt');
    //
    // Example (cloud):
    //   _apiKey = await SecureStorage.read('gemini_api_key');
    //   _client = GenerativeModel(model: 'gemini-pro', apiKey: _apiKey);

    await Future.delayed(const Duration(milliseconds: 300));
    _isReady = true;
    return true;
  }

  @override
  bool get isReady => _isReady;

  @override
  Future<TriageOutput> analyze(TriageInput input) async {
    // TODO: Replace with real AI analysis
    // Example (cloud — Gemini):
    //   final prompt = '''
    //     Bạn là bác sĩ AI. Phân tích triệu chứng sau và trả về JSON:
    //     ${input.toPrompt()}
    //
    //     Trả về: { "level": "green|yellow|red", "summary": "...", "advice": [...] }
    //   ''';
    //   final response = await _model.generateContent([Content.text(prompt)]);
    //   return _parseResponse(response.text);
    //
    // Example (on-device — TFLite):
    //   final features = _extractFeatures(input);
    //   _interpreter.run(features, outputBuffer);
    //   return _decodeOutput(outputBuffer);

    // ── Mock: rule-based triage ──
    await Future.delayed(const Duration(milliseconds: 1500));

    final level = _calculateMockLevel(input);
    return TriageOutput(
      level: level,
      summary: _generateMockSummary(input, level),
      advice: _generateMockAdvice(level),
      confidence: 0.85,
      rawResponse: 'MOCK_RESPONSE: ${input.toPrompt()}',
    );
  }

  @override
  Future<TriageOutput> analyzeText(String text) async {
    return analyze(TriageInput(textDescription: text));
  }

  TriageLevel _calculateMockLevel(TriageInput input) {
    // Emergency signs
    if (input.symptoms.contains(SymptomIcon.chestPain) ||
        input.symptoms.contains(SymptomIcon.bleeding) ||
        input.symptoms.contains(SymptomIcon.breathless) ||
        input.severity == Severity.critical) {
      return TriageLevel.red;
    }

    // Warning signs
    if (input.severity == Severity.severe ||
        input.symptoms.length >= 4 ||
        input.duration == SymptomDuration.moreThanWeek) {
      return TriageLevel.yellow;
    }

    // Check text for emergency keywords
    final text = (input.voiceTranscript ?? '') + (input.textDescription ?? '');
    final emergencyKeywords = ['khó thở', 'đau ngực', 'chảy máu', 'ngất', 'co giật'];
    for (final keyword in emergencyKeywords) {
      if (text.toLowerCase().contains(keyword)) {
        return TriageLevel.red;
      }
    }

    return TriageLevel.green;
  }

  String _generateMockSummary(TriageInput input, TriageLevel level) {
    switch (level) {
      case TriageLevel.green:
        return 'Triệu chứng nhẹ, có thể tự theo dõi tại nhà. Nghỉ ngơi và uống đủ nước.';
      case TriageLevel.yellow:
        return 'Triệu chứng cần theo dõi. Nên đến cơ sở y tế trong 1-2 ngày tới nếu không đỡ.';
      case TriageLevel.red:
        return 'CẦN ĐI KHÁM NGAY! Triệu chứng có dấu hiệu nguy hiểm, không nên chờ đợi.';
    }
  }

  List<TriageAdvice> _generateMockAdvice(TriageLevel level) {
    switch (level) {
      case TriageLevel.green:
        return const [
          TriageAdvice(emoji: '💧', title: 'Uống nhiều nước', description: 'Ít nhất 2 lít mỗi ngày', color: 0xFF22C55E),
          TriageAdvice(emoji: '😴', title: 'Nghỉ ngơi đầy đủ', description: 'Ngủ 7-8 tiếng mỗi đêm', color: 0xFF8B5CF6),
          TriageAdvice(emoji: '🌡️', title: 'Theo dõi nhiệt độ', description: 'Đo 2 lần/ngày, sáng và tối', color: 0xFFF59E0B),
          TriageAdvice(emoji: '📅', title: 'Theo dõi 2-3 ngày', description: 'Nếu không đỡ, hãy đi khám', color: 0xFF3B82F6),
        ];
      case TriageLevel.yellow:
        return const [
          TriageAdvice(emoji: '🏥', title: 'Đi khám bác sĩ', description: 'Trong 1-2 ngày tới', color: 0xFFF59E0B),
          TriageAdvice(emoji: '💊', title: 'Uống thuốc hạ sốt nếu sốt', description: 'Paracetamol theo đúng liều', color: 0xFF3B82F6),
          TriageAdvice(emoji: '📝', title: 'Ghi lại triệu chứng', description: 'Để kể bác sĩ khi đi khám', color: 0xFF8B5CF6),
        ];
      case TriageLevel.red:
        return const [
          TriageAdvice(emoji: '🚑', title: 'ĐI VIỆN NGAY', description: 'Gọi 115 hoặc nhờ người đưa đi', color: 0xFFEF4444),
          TriageAdvice(emoji: '📞', title: 'Gọi người thân', description: 'Nhờ ai đó ở bên cạnh hỗ trợ', color: 0xFFF59E0B),
          TriageAdvice(emoji: '⚠️', title: 'KHÔNG tự uống thuốc', description: 'Chờ bác sĩ chỉ định', color: 0xFFEF4444),
        ];
    }
  }

  @override
  void dispose() {
    // TODO: 
    //   _interpreter.close();
    //   _client.dispose();
  }
}
