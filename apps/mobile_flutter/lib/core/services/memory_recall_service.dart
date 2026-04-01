import '../models/journal_entry.dart';
import 'soul_garden_service.dart';

/// Memory Recall Service - Gợi nhớ kỷ niệm đẹp theo thời gian
/// Hỗ trợ trí nhớ, time capsule, nhắc nhở kỷ niệm
class MemoryRecallService {
  MemoryRecallService._();
  static final instance = MemoryRecallService._();

  final SoulGardenService _soulGarden = SoulGardenService.instance;

  /// Lấy "On This Day" - kỷ niệm cùng ngày năm trước
  OnThisDayResult getOnThisDay() {
    final memories = _soulGarden.getMemoriesFromExactlyOneYearAgo();

    if (memories.isEmpty) {
      return const OnThisDayResult(
        hasMemory: false,
        memories: [],
        message: 'Chưa có kỷ niệm nào vào ngày này năm trước.',
      );
    }

    final yearsAgo = DateTime.now().year - memories.first.date.year;
    return OnThisDayResult(
      hasMemory: true,
      memories: memories,
      message: '💫 $yearsAgo năm trước vào ngày này...',
    );
  }

  /// Lấy kỷ niệm tuần này các năm trước
  List<JournalEntry> getWeekMemories() {
    final memories = <JournalEntry>[];
    final now = DateTime.now();

    for (int yearOffset = 1; yearOffset <= 3; yearOffset++) {
      // targetYear can be used for filtering memories by year if needed
      // final targetYear = now.year - yearOffset;
      final weekStart = now.subtract(Duration(days: now.weekday - 1));

      for (int i = 0; i < 7; i++) {
        final targetDate = weekStart.subtract(Duration(days: i));
        final entries = _soulGarden.getMemoriesFromDaysAgo(
          now.difference(targetDate).inDays,
          exactDay: targetDate.day,
        );
        memories.addAll(entries);
      }
    }

    return memories;
  }

  /// Lấy memory highlight - khoảnh khắc nổi bật nhất
  MemoryHighlight? getMemoryHighlight() {
    final positives = _soulGarden.getPositiveMemories(days: 90, limit: 10);

    if (positives.isEmpty) return null;

    // Chọn entry có mood cao nhất và có nội dung hay nhất
    final best = positives.firstWhere(
      (e) => e.content.length > 20,
      orElse: () => positives.first,
    );

    return MemoryHighlight(
      entry: best,
      highlightType: _classifyHighlight(best),
      suggestedTitle: _generateTitle(best),
    );
  }

  HighlightType _classifyHighlight(JournalEntry entry) {
    final content = entry.content.toLowerCase();

    if (content.contains('gia đình') ||
        content.contains('bố mẹ') ||
        content.contains('con cái')) {
      return HighlightType.family;
    }
    if (content.contains('thành công') ||
        content.contains('được khen') ||
        content.contains('giải thưởng')) {
      return HighlightType.achievement;
    }
    if (content.contains('tập') ||
        content.contains('gym') ||
        content.contains('thể dục')) {
      return HighlightType.fitness;
    }
    if (content.contains('biết ơn') || content.contains('cảm ơn')) {
      return HighlightType.gratitude;
    }
    return HighlightType.joyful;
  }

  String _generateTitle(JournalEntry entry) {
    final dateStr =
        '${entry.date.day}/${entry.date.month}/${entry.date.year}';
    return '${entry.mood.emoji} $dateStr';
  }

  /// Lên lịch nhắc nhở memory capsule
  Future<void> scheduleMemoryReminder({
    required String title,
    required String content,
    Mood? mood,
    Duration? delay,
  }) async {
    final capsule = _soulGarden.createMemoryCapsule(
      title: title,
      content: content,
      mood: mood,
    );
    _soulGarden.addCapsule(capsule);

    // Trong thực tế, sẽ dùng local notification để nhắc sau delay
    // Delay mặc định: 30 ngày
  }

  /// Lấy tất cả upcoming reminders
  List<MemoryCapsule> getUpcomingReminders() {
    return _soulGarden.capsules
        .where((c) => c.remindedAt == null)
        .toList();
  }

  /// Trigger nhắc nhở hàng ngày (gọi mỗi khi mở app)
  DailyMemoryReminder? getDailyReminder() {
    // 1. Check time capsule cần nhắc
    final capsules = _soulGarden.getTodaysCapsules();
    if (capsules.isNotEmpty) {
      return DailyMemoryReminder(
        type: ReminderType.memoryCapsule,
        title: '📸 Kỷ niệm của bạn',
        message: capsules.first.content,
        data: capsules.first,
      );
    }

    // 2. Check "on this day"
    final onThisDay = getOnThisDay();
    if (onThisDay.hasMemory) {
      return DailyMemoryReminder(
        type: ReminderType.onThisDay,
        title: '⏰ Cùng ngày',
        message: onThisDay.memories.first.content,
        data: onThisDay.memories.first,
      );
    }

    // 3. Random positive memory
    final positives = _soulGarden.getPositiveMemories(days: 30, limit: 1);
    if (positives.isNotEmpty) {
      return DailyMemoryReminder(
        type: ReminderType.positiveMemory,
        title: '💚 Khoảnh khắc đẹp',
        message: positives.first.content,
        data: positives.first,
      );
    }

    return null;
  }

  /// Memory game - tạo câu hỏi trắc nghiệm từ nhật ký
  List<MemoryQuizQuestion> generateMemoryQuiz({int count = 5}) {
    final entries = _soulGarden.entries;
    if (entries.length < count) return [];

    final questions = <MemoryQuizQuestion>[];
    final shuffled = List<JournalEntry>.from(entries)..shuffle();

    for (int i = 0; i < count && i < shuffled.length; i++) {
      final entry = shuffled[i];

      // Tạo câu hỏi về ngày
      final wrongDates = entries
          .where((e) => e.id != entry.id)
          .take(3)
          .map((e) => '${e.date.day}/${e.date.month}')
          .toList();

      questions.add(MemoryQuizQuestion(
        question: 'Bạn đã viết nhật ký này vào ngày nào?',
        correctAnswer: '${entry.date.day}/${entry.date.month}',
        options: [...wrongDates, '${entry.date.day}/${entry.date.month}']
          ..shuffle(),
        relatedEntry: entry,
      ));
    }

    return questions;
  }
}

/// Kết quả On This Day
class OnThisDayResult {
  final bool hasMemory;
  final List<JournalEntry> memories;
  final String message;

  const OnThisDayResult({
    required this.hasMemory,
    required this.memories,
    required this.message,
  });
}

/// Memory Highlight
class MemoryHighlight {
  final JournalEntry entry;
  final HighlightType highlightType;
  final String suggestedTitle;

  const MemoryHighlight({
    required this.entry,
    required this.highlightType,
    required this.suggestedTitle,
  });
}

enum HighlightType {
  family,
  achievement,
  fitness,
  gratitude,
  joyful,
  peaceful,
}

/// Daily Memory Reminder
class DailyMemoryReminder {
  final ReminderType type;
  final String title;
  final String message;
  final dynamic data;

  const DailyMemoryReminder({
    required this.type,
    required this.title,
    required this.message,
    required this.data,
  });
}

enum ReminderType {
  memoryCapsule,
  onThisDay,
  positiveMemory,
  gratitude,
}

/// Memory Quiz Question
class MemoryQuizQuestion {
  final String question;
  final String correctAnswer;
  final List<String> options;
  final JournalEntry relatedEntry;

  const MemoryQuizQuestion({
    required this.question,
    required this.correctAnswer,
    required this.options,
    required this.relatedEntry,
  });
}
