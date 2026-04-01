import 'package:dio/dio.dart';
import '../models/communication_mode.dart';
import 'triage_service.dart';

/// ══════════════════════════════════════════════════════════════
/// REAL TRIAGE SERVICE — Production implementation using:
///   - Backend API (FastAPI) with Gemini integration
///   - Hybrid mode: rule-based for emergencies, AI for details
/// ══════════════════════════════════════════════════════════════

class RealTriageService implements TriageService {
  late final Dio _dio;
  bool _isReady = false;

  // Backend URL - should be configured via environment
  static const String _baseUrl = 'http://localhost:8000';

  RealTriageService({String? baseUrl}) {
    _dio = Dio(BaseOptions(
      baseUrl: baseUrl ?? _baseUrl,
      connectTimeout: const Duration(seconds: 10),
      receiveTimeout: const Duration(seconds: 30),
      headers: {
        'Content-Type': 'application/json',
      },
    ));
  }

  @override
  Future<bool> initialize() async {
    try {
      // Test connection to backend
      await _dio.get('/health');
      _isReady = true;
      return true;
    } catch (e) {
      // Backend not available - will use local fallback
      _isReady = true; // Still allow local processing
      return true;
    }
  }

  @override
  bool get isReady => _isReady;

  @override
  Future<TriageOutput> analyze(TriageInput input) async {
    // Build symptom text from input
    final symptomText = _buildSymptomText(input);

    try {
      // Try to call backend API
      final response = await _dio.post(
        '/api/v1/consult/triage',
        data: {
          'symptom_text': symptomText,
          'age': input.patientAge,
          'gender': input.patientGender,
          'duration': input.duration?.name,
        },
      );

      if (response.statusCode == 200) {
        return _mapBackendResponse(response.data);
      }
    } catch (e) {
      // Fallback to local rule-based triage
    }

    // Fallback: local rule-based triage
    return _localFallbackTriage(input);
  }

  @override
  Future<TriageOutput> analyzeText(String text) async {
    return analyze(TriageInput(textDescription: text));
  }

  String _buildSymptomText(TriageInput input) {
    final parts = <String>[];

    if (input.bodyRegions.isNotEmpty) {
      parts
          .add('Vùng đau: ${input.bodyRegions.map((r) => r.label).join(', ')}');
    }
    if (input.symptoms.isNotEmpty) {
      parts
          .add('Triệu chứng: ${input.symptoms.map((s) => s.label).join(', ')}');
    }
    if (input.severity != null) {
      parts.add('Mức độ: ${input.severity!.label}');
    }
    if (input.duration != null) {
      parts.add('Thời gian: ${input.duration!.label}');
    }
    if (input.voiceTranscript != null && input.voiceTranscript!.isNotEmpty) {
      parts.add('Mô tả: ${input.voiceTranscript}');
    }
    if (input.textDescription != null && input.textDescription!.isNotEmpty) {
      parts.add('Mô tả: ${input.textDescription}');
    }

    return parts.join('. ');
  }

  TriageOutput _mapBackendResponse(Map<String, dynamic> data) {
    final urgencyLevel = data['urgency_level'] as String? ?? 'non_emergency';
    final summary = data['summary'] as String? ?? '';
    final recommendations = (data['recommendations'] as List<dynamic>?)
            ?.map((r) => r.toString())
            .toList() ??
        [];

    final level = _mapUrgencyToLevel(urgencyLevel);
    final advice = _buildAdviceList(level, recommendations);

    return TriageOutput(
      level: level,
      summary: summary,
      advice: advice,
      confidence: 0.9,
      rawResponse: data.toString(),
    );
  }

  TriageLevel _mapUrgencyToLevel(String urgency) {
    switch (urgency.toLowerCase()) {
      case 'emergency':
        return TriageLevel.red;
      case 'urgent':
        return TriageLevel.yellow;
      default:
        return TriageLevel.green;
    }
  }

  List<TriageAdvice> _buildAdviceList(
      TriageLevel level, List<String> recommendations) {
    final colors = {
      TriageLevel.green: 0xFF22C55E,
      TriageLevel.yellow: 0xFFF59E0B,
      TriageLevel.red: 0xFFEF4444,
    };

    final icons = {
      TriageLevel.green: ['💧', '😴', '🌡️', '📅'],
      TriageLevel.yellow: ['🏥', '💊', '📝'],
      TriageLevel.red: ['🚑', '📞', '⚠️'],
    };

    if (recommendations.isNotEmpty) {
      return recommendations.asMap().entries.map((entry) {
        final icon = icons[level]![entry.key % icons[level]!.length];
        return TriageAdvice(
          emoji: icon,
          title: entry.value.length > 30
              ? '${entry.value.substring(0, 27)}...'
              : entry.value,
          description: entry.value,
          color: colors[level],
        );
      }).toList();
    }

    // Default advice based on level
    return _getDefaultAdvice(level);
  }

  List<TriageAdvice> _getDefaultAdvice(TriageLevel level) {
    switch (level) {
      case TriageLevel.green:
        return const [
          TriageAdvice(
            emoji: '💧',
            title: 'Uống nhiều nước',
            description: 'Ít nhất 2 lít mỗi ngày',
            color: 0xFF22C55E,
          ),
          TriageAdvice(
            emoji: '😴',
            title: 'Nghỉ ngơi đầy đủ',
            description: 'Ngủ 7-8 tiếng mỗi đêm',
            color: 0xFF22C55E,
          ),
          TriageAdvice(
            emoji: '🌡️',
            title: 'Theo dõi nhiệt độ',
            description: 'Đo 2 lần/ngày, sáng và tối',
            color: 0xFF22C55E,
          ),
        ];
      case TriageLevel.yellow:
        return const [
          TriageAdvice(
            emoji: '🏥',
            title: 'Đi khám bác sĩ',
            description: 'Trong 1-2 ngày tới',
            color: 0xFFF59E0B,
          ),
          TriageAdvice(
            emoji: '📝',
            title: 'Ghi lại triệu chứng',
            description: 'Để kể bác sĩ khi đi khám',
            color: 0xFFF59E0B,
          ),
        ];
      case TriageLevel.red:
        return const [
          TriageAdvice(
            emoji: '🚑',
            title: 'ĐI VIỆN NGAY',
            description: 'Gọi 115 hoặc nhờ người đưa đi',
            color: 0xFFEF4444,
          ),
          TriageAdvice(
            emoji: '📞',
            title: 'Gọi người thân',
            description: 'Nhờ ai đó ở bên cạnh hỗ trợ',
            color: 0xFFEF4444,
          ),
        ];
    }
  }

  /// Local rule-based fallback when backend is unavailable
  TriageOutput _localFallbackTriage(TriageInput input) {
    final level = _calculateLocalLevel(input);
    final summary = _generateLocalSummary(level);
    final advice = _getDefaultAdvice(level);

    return TriageOutput(
      level: level,
      summary: summary,
      advice: advice,
      confidence: 0.7,
      rawResponse: 'Local fallback',
    );
  }

  TriageLevel _calculateLocalLevel(TriageInput input) {
    // Check for emergency keywords in text
    final text =
        '${input.voiceTranscript ?? ''} ${input.textDescription ?? ''}';

    final emergencyKeywords = [
      'khó thở',
      'đau ngực',
      'chảy máu',
      'ngất',
      'co giật',
      'đau bụng dữ dội',
    ];

    for (final keyword in emergencyKeywords) {
      if (text.toLowerCase().contains(keyword)) {
        return TriageLevel.red;
      }
    }

    // Check severity
    if (input.severity == Severity.critical) {
      return TriageLevel.red;
    }
    if (input.severity == Severity.severe) {
      return TriageLevel.yellow;
    }

    // Check symptoms
    if (input.symptoms.contains(SymptomIcon.chestPain) ||
        input.symptoms.contains(SymptomIcon.breathless) ||
        input.symptoms.contains(SymptomIcon.bleeding)) {
      return TriageLevel.red;
    }

    // Check duration
    if (input.duration == SymptomDuration.moreThanWeek) {
      return TriageLevel.yellow;
    }

    return TriageLevel.green;
  }

  String _generateLocalSummary(TriageLevel level) {
    switch (level) {
      case TriageLevel.green:
        return 'Triệu chứng nhẹ, có thể tự theo dõi tại nhà.';
      case TriageLevel.yellow:
        return 'Triệu chứng cần theo dõi. Nên đến cơ sở y tế trong 1-2 ngày.';
      case TriageLevel.red:
        return 'CẦN ĐI KHÁM NGAY! Gọi 115 nếu tình trạng nghiêm trọng.';
    }
  }

  @override
  void dispose() {
    _dio.close();
  }
}
