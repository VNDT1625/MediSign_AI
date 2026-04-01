import 'soul_garden_service.dart';
import 'memory_recall_service.dart';
import 'comfort_ai_service.dart';

/// Soul Garden Integration Service
/// Tich hop Soul Garden context vao AI Triage/Consult flow
class SoulGardenIntegrationService {
  SoulGardenIntegrationService._();
  static final instance = SoulGardenIntegrationService._();

  final SoulGardenService _soulGarden = SoulGardenService.instance;
  final MemoryRecallService _memoryRecall = MemoryRecallService.instance;
  final ComfortAIService _comfortAI = ComfortAIService.instance;

  /// Lay context cho AI dua tren Soul Garden
  String getAIPromptContext() {
    return _soulGarden.getAIMemoryContext();
  }

  /// Kiem tra user co bi trieu chung tam thanh khong
  /// Neu co, them comforting message vao response
  String? checkAndAddComfort(String symptomText) {
    final textLower = symptomText.toLowerCase();

    final mentalKeywords = [
      'buon',
      'chan',
      'met',
      'stress',
      'cang',
      'lo lang',
      'co don',
      'tuc gian',
    ];

    final hasMentalKeyword = mentalKeywords.any((k) => textLower.contains(k));

    if (hasMentalKeyword) {
      return _comfortAI.getComfortingMessage(userMessage: symptomText);
    }

    return null;
  }

  /// Lay personalized advice dua tren history
  List<String> getPersonalizedAdvice() {
    final advice = <String>[];

    final streak = _soulGarden.streak;
    if (streak > 0) {
      advice.add('Ban da ghi nhat ky $streak ngay lien tiep');
    }

    final stats = _soulGarden.statsForDays(7);
    if (stats.averageScore < 2.5) {
      advice.add('Tam trang cua ban khong tot trong thoi gian qua');
    }

    return advice;
  }

  /// Lay encouraging message
  String getEncouragingMessage() {
    final recentPositive = _soulGarden.getPositiveMemories(days: 14, limit: 1);

    if (recentPositive.isNotEmpty) {
      return 'Hay nho rang: "${recentPositive.first.content.substring(0, 30)}..." - Ban da qua duoc nhieu thu!';
    }

    return 'Ban co the lam duoc!';
  }

  /// Build full consult prompt
  String buildConsultPrompt(String userQuestion) {
    final buffer = StringBuffer();

    buffer.writeln('## Cau hoi:');
    buffer.writeln(userQuestion);
    buffer.writeln();
    buffer.writeln(_soulGarden.getAIMemoryContext());

    final comfort = checkAndAddComfort(userQuestion);
    if (comfort != null) {
      buffer.writeln(comfort);
    }

    return buffer.toString();
  }

  /// Check if need professional help
  bool shouldRecommendPsychologist() {
    return _comfortAI.shouldRecommendProfessional();
  }

  /// Get professional recommendation
  String getPsychologistRecommendation() {
    return _comfortAI.getProfessionalRecommendation();
  }

  /// Get daily reminder
  DailyMemoryReminder? getDailyMemoryReminder() {
    return _memoryRecall.getDailyReminder();
  }

  /// Get today highlight
  MemoryHighlight? getTodayHighlight() {
    return _memoryRecall.getMemoryHighlight();
  }
}
