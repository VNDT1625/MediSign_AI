import '../models/garden_item.dart';
import '../models/journal_entry.dart';

/// Achievement definition.
class Achievement {
  final String id;
  final String emoji;
  final String title;
  final String description;
  final bool Function(SoulGardenService svc) check;

  const Achievement({
    required this.id,
    required this.emoji,
    required this.title,
    required this.description,
    required this.check,
  });
}

/// Mood statistics over a time range.
class MoodStats {
  final Map<Mood, int> distribution;
  final double averageScore;
  final double? previousAverageScore;
  final Map<EmotionTag, int> tagFrequency;
  final int totalEntries;

  const MoodStats({
    required this.distribution,
    required this.averageScore,
    this.previousAverageScore,
    required this.tagFrequency,
    required this.totalEntries,
  });

  /// Trend percentage vs previous period.
  double? get trendPercent {
    if (previousAverageScore == null || previousAverageScore == 0) return null;
    return ((averageScore - previousAverageScore!) / previousAverageScore!) *
        100;
  }

  /// Number of consecutive negative days (latest).
  int get negativeStreak {
    // This is computed externally; included for convenience.
    return 0;
  }
}

/// Tree state derived from journal data.
class TreeState {
  final int level;
  final String emoji;
  final String name;
  final String description;

  const TreeState({
    required this.level,
    required this.emoji,
    required this.name,
    required this.description,
  });
}

/// Soul Garden service — in-memory storage, ready for SQLite swap.
class SoulGardenService {
  SoulGardenService._() {
    _seedSampleDataIfEmpty();
  }
  static final instance = SoulGardenService._();

  final List<JournalEntry> _entries = [];

  // ─── SAMPLE DATA ──────────────────────────────

  void _seedSampleDataIfEmpty() {
    if (_entries.isNotEmpty) return;
    final now = DateTime.now();
    final samples = <JournalEntry>[
      JournalEntry(
        id: 'seed_1',
        date: now.subtract(const Duration(days: 13)),
        mood: Mood.good,
        content:
            'Hôm nay đi dạo công viên buổi sáng, không khí trong lành quá. Cảm thấy đầu óc thư thái hơn hẳn sau mấy ngày ngồi máy tính.',
        tags: {EmotionTag.peaceful, EmotionTag.grateful},
      ),
      JournalEntry(
        id: 'seed_2',
        date: now.subtract(const Duration(days: 12)),
        mood: Mood.awesome,
        content:
            'Được khen trong buổi thuyết trình! Mấy tháng chuẩn bị cuối cùng cũng được đền đáp. Tối nay ăn mừng với bạn bè.',
        tags: {EmotionTag.happy, EmotionTag.motivated},
      ),
      JournalEntry(
        id: 'seed_3',
        date: now.subtract(const Duration(days: 11)),
        mood: Mood.neutral,
        content: 'Ngày bình thường, đi làm rồi về. Nấu ăn tối xong xem phim.',
        tags: {EmotionTag.peaceful},
      ),
      JournalEntry(
        id: 'seed_4',
        date: now.subtract(const Duration(days: 9)),
        mood: Mood.sad,
        content:
            'Mất ngủ đêm qua, sáng dậy mệt mỏi. Áp lực deadline đang đè nặng. Cần sắp xếp lại thời gian.',
        tags: {EmotionTag.stressed, EmotionTag.tired},
      ),
      JournalEntry(
        id: 'seed_5',
        date: now.subtract(const Duration(days: 8)),
        mood: Mood.sad,
        content:
            'Vẫn chưa ngủ được tốt. Thử tập thở trước khi ngủ nhưng đầu óc cứ nghĩ lung tung.',
        tags: {EmotionTag.anxious, EmotionTag.tired},
      ),
      JournalEntry(
        id: 'seed_6',
        date: now.subtract(const Duration(days: 7)),
        mood: Mood.good,
        content:
            'Cuối cùng cũng hoàn thành deadline! Ngủ được 8 tiếng luôn. Cảm thấy nhẹ nhõm hơn nhiều.',
        tags: {EmotionTag.happy, EmotionTag.grateful},
      ),
      JournalEntry(
        id: 'seed_7',
        date: now.subtract(const Duration(days: 5)),
        mood: Mood.awesome,
        content:
            'Cuối tuần đi picnic cùng gia đình. Thời tiết đẹp, các con vui lắm. Cần dành thời gian cho gia đình nhiều hơn.',
        tags: {EmotionTag.happy, EmotionTag.loved},
      ),
      JournalEntry(
        id: 'seed_8',
        date: now.subtract(const Duration(days: 3)),
        mood: Mood.neutral,
        content:
            'Làm việc bình thường. Bắt đầu dự án mới, hơi lo lắng nhưng cũng háo hức.',
        tags: {EmotionTag.anxious, EmotionTag.motivated},
      ),
      JournalEntry(
        id: 'seed_9',
        date: now.subtract(const Duration(days: 1)),
        mood: Mood.good,
        content:
            'Tập gym xong cảm thấy khỏe khoắn. Nấu bữa tối healthy. Đọc sách trước khi ngủ.',
        tags: {EmotionTag.motivated, EmotionTag.peaceful},
      ),
      JournalEntry(
        id: 'seed_10',
        date: now,
        mood: Mood.good,
        content: 'Sáng dậy sớm thiền 10 phút. Ngày mới tràn đầy năng lượng!',
        tags: {EmotionTag.grateful, EmotionTag.peaceful, EmotionTag.happy},
      ),
    ];
    _entries.addAll(samples);
  }

  // ─── CRUD ─────────────────────────────────────

  List<JournalEntry> get entries => List.unmodifiable(_entries);

  void addEntry(JournalEntry entry) {
    _entries.insert(0, entry);
  }

  void deleteEntry(String id) {
    _entries.removeWhere((e) => e.id == id);
  }

  void updateEntry(JournalEntry updatedEntry) {
    final index = _entries.indexWhere((e) => e.id == updatedEntry.id);
    if (index != -1) {
      _entries[index] = updatedEntry;
    }
  }

  /// Search entries by content
  List<JournalEntry> searchEntries(String query) {
    if (query.isEmpty) return entries;
    final queryLower = query.toLowerCase();
    return _entries.where((e) {
      return e.content.toLowerCase().contains(queryLower) ||
          e.mood.label.toLowerCase().contains(queryLower) ||
          e.tags.any((t) => t.label.toLowerCase().contains(queryLower));
    }).toList();
  }

  /// Search entries by mood
  List<JournalEntry> searchByMood(Mood mood) {
    return _entries.where((e) => e.mood == mood).toList();
  }

  /// Search entries by tag
  List<JournalEntry> searchByTag(EmotionTag tag) {
    return _entries.where((e) => e.tags.contains(tag)).toList();
  }

  /// Search entries by date range
  List<JournalEntry> searchByDateRange(DateTime from, DateTime to) {
    return entriesInRange(from, to);
  }

  List<JournalEntry> entriesForMonth(int year, int month) {
    return _entries
        .where((e) => e.date.year == year && e.date.month == month)
        .toList();
  }

  List<JournalEntry> entriesInRange(DateTime from, DateTime to) {
    return _entries
        .where((e) =>
            e.date.isAfter(from) &&
            e.date.isBefore(to.add(const Duration(days: 1))))
        .toList();
  }

  // ─── STREAK ───────────────────────────────────

  int get streak {
    int s = 0;
    final now = DateTime.now();
    for (int i = 0; i < 365; i++) {
      final day = now.subtract(Duration(days: i));
      if (_entries.any((e) =>
          e.date.year == day.year &&
          e.date.month == day.month &&
          e.date.day == day.day)) {
        s++;
      } else {
        break;
      }
    }
    return s;
  }

  int get negativeStreak {
    int s = 0;
    final now = DateTime.now();
    for (int i = 0; i < 30; i++) {
      final day = now.subtract(Duration(days: i));
      final entry = _entries.cast<JournalEntry?>().firstWhere(
            (e) =>
                e!.date.year == day.year &&
                e.date.month == day.month &&
                e.date.day == day.day,
            orElse: () => null,
          );
      if (entry != null && entry.mood.isNegative) {
        s++;
      } else {
        break;
      }
    }
    return s;
  }

  // ─── ANALYTICS ────────────────────────────────

  MoodStats statsForDays(int days) {
    final now = DateTime.now();
    final from = now.subtract(Duration(days: days));
    final prevFrom = now.subtract(Duration(days: days * 2));

    final currentEntries = entriesInRange(from, now);
    final previousEntries = entriesInRange(prevFrom, from);

    // Distribution
    final dist = <Mood, int>{};
    for (final m in Mood.values) {
      dist[m] = 0;
    }
    for (final e in currentEntries) {
      dist[e.mood] = (dist[e.mood] ?? 0) + 1;
    }

    // Average score
    double avg = 0;
    if (currentEntries.isNotEmpty) {
      avg = currentEntries.map((e) => e.mood.score).reduce((a, b) => a + b) /
          currentEntries.length;
    }

    double? prevAvg;
    if (previousEntries.isNotEmpty) {
      prevAvg =
          previousEntries.map((e) => e.mood.score).reduce((a, b) => a + b) /
              previousEntries.length;
    }

    // Tag frequency
    final tagFreq = <EmotionTag, int>{};
    for (final e in currentEntries) {
      for (final t in e.tags) {
        tagFreq[t] = (tagFreq[t] ?? 0) + 1;
      }
    }

    return MoodStats(
      distribution: dist,
      averageScore: avg,
      previousAverageScore: prevAvg,
      tagFrequency: tagFreq,
      totalEntries: currentEntries.length,
    );
  }

  /// AI-style insight text list.
  List<String> getInsights(int days) {
    final stats = statsForDays(days);
    final insights = <String>[];

    // Trend
    final trend = stats.trendPercent;
    if (trend != null) {
      if (trend > 0) {
        insights.add(
            '📈 Bạn vui hơn ${trend.abs().toStringAsFixed(0)}% so với kỳ trước');
      } else if (trend < -10) {
        insights.add(
            '📉 Tâm trạng giảm ${trend.abs().toStringAsFixed(0)}% — hãy chăm sóc bản thân nhé');
      }
    }

    // Most common tag
    if (stats.tagFrequency.isNotEmpty) {
      final topTag = stats.tagFrequency.entries
          .reduce((a, b) => a.value > b.value ? a : b);
      insights.add(
          '🏷️ Tag phổ biến nhất: ${topTag.key.emoji} ${topTag.key.label} (${topTag.value} lần)');
    }

    // Negative streak warning
    final negStreak = negativeStreak;
    if (negStreak >= 5) {
      insights.add(
          '⚠️ Bạn có $negStreak ngày tâm trạng tiêu cực liên tiếp. Hãy cân nhắc nói chuyện với chuyên gia.');
    } else if (negStreak >= 3) {
      insights.add(
          '💛 $negStreak ngày tâm trạng không tốt — thử bài tập thở để thư giãn nhé');
    }

    // Overall
    if (stats.totalEntries == 0) {
      insights.add('✍️ Hãy bắt đầu viết nhật ký để xem phân tích');
    } else if (stats.averageScore >= 4) {
      insights.add('🌟 Tâm trạng của bạn rất tích cực — tuyệt vời!');
    }

    return insights;
  }

  // ─── TREE STATE ───────────────────────────────

  TreeState get treeState {
    final level = (_entries.length / 3).floor().clamp(0, 10);
    final recent7 = statsForDays(7);

    // Mood-based evolution
    if (_entries.isEmpty) {
      return const TreeState(
          level: 0,
          emoji: '🌱',
          name: 'Hạt giống',
          description: 'Hãy bắt đầu viết nhật ký');
    }

    if (recent7.averageScore >= 4.0) {
      // Positive → blooming
      final treeList = [
        const TreeState(
            level: 1,
            emoji: '🌱',
            name: 'Mầm non',
            description: 'Cây đang nảy mầm'),
        const TreeState(
            level: 2,
            emoji: '🌿',
            name: 'Cây con',
            description: 'Cây đang lớn dần'),
        const TreeState(
            level: 3,
            emoji: '🪴',
            name: 'Cây trưởng thành',
            description: 'Cây khỏe mạnh'),
        const TreeState(
            level: 4,
            emoji: '🌳',
            name: 'Đại thụ',
            description: 'Cây vững vàng'),
        const TreeState(
            level: 5,
            emoji: '🌸',
            name: 'Nở hoa',
            description: 'Tâm hồn rực rỡ!'),
      ];
      return treeList[level.clamp(0, treeList.length - 1)];
    } else if (recent7.averageScore <= 2.0) {
      // Negative → wilting
      return TreeState(
          level: level,
          emoji: '🍂',
          name: 'Cây héo',
          description: 'Hãy chăm sóc bản thân nhé');
    } else {
      // Neutral/mixed
      final treeList = [
        const TreeState(
            level: 1,
            emoji: '🌱',
            name: 'Mầm non',
            description: 'Cây đang nảy mầm'),
        const TreeState(
            level: 2,
            emoji: '🌿',
            name: 'Cây con',
            description: 'Cây đang lớn dần'),
        const TreeState(
            level: 3,
            emoji: '🪴',
            name: 'Cây trưởng thành',
            description: 'Cây khỏe mạnh'),
        const TreeState(
            level: 4,
            emoji: '🌳',
            name: 'Đại thụ',
            description: 'Cây vững vàng'),
        const TreeState(
            level: 5,
            emoji: '🌲',
            name: 'Cây xanh tốt',
            description: 'Cây bình yên'),
      ];
      return treeList[level.clamp(0, treeList.length - 1)];
    }
  }

  // ─── ACHIEVEMENTS ─────────────────────────────

  static final List<Achievement> _allAchievements = [
    Achievement(
      id: 'first_entry',
      emoji: '✍️',
      title: 'Bước đầu tiên',
      description: 'Viết nhật ký lần đầu',
      check: (s) => s._entries.isNotEmpty,
    ),
    Achievement(
      id: 'streak_3',
      emoji: '🔥',
      title: '3 ngày liên tiếp',
      description: 'Viết nhật ký 3 ngày liên tục',
      check: (s) => s.streak >= 3,
    ),
    Achievement(
      id: 'streak_7',
      emoji: '⭐',
      title: '7 ngày liên tiếp',
      description: 'Viết nhật ký 1 tuần liên tục',
      check: (s) => s.streak >= 7,
    ),
    Achievement(
      id: 'streak_30',
      emoji: '🏆',
      title: '30 ngày liên tiếp',
      description: 'Viết nhật ký 1 tháng liên tục!',
      check: (s) => s.streak >= 30,
    ),
    Achievement(
      id: 'entries_10',
      emoji: '📚',
      title: '10 bài viết',
      description: 'Đã viết 10 bài nhật ký',
      check: (s) => s._entries.length >= 10,
    ),
    Achievement(
      id: 'entries_50',
      emoji: '📖',
      title: '50 bài viết',
      description: 'Đã viết 50 bài nhật ký',
      check: (s) => s._entries.length >= 50,
    ),
    Achievement(
      id: 'positive_week',
      emoji: '🌸',
      title: 'Tuần tích cực',
      description: '7 ngày toàn mood tốt',
      check: (s) {
        final stats = s.statsForDays(7);
        return stats.totalEntries >= 7 && stats.averageScore >= 4.0;
      },
    ),
    Achievement(
      id: 'blooming',
      emoji: '🌺',
      title: 'Cây nở hoa',
      description: 'Đạt level 5 — cây nở hoa!',
      check: (s) => s.treeState.level >= 5,
    ),
    Achievement(
      id: 'all_tags',
      emoji: '🏷️',
      title: 'Giàu cảm xúc',
      description: 'Sử dụng tất cả emotion tags',
      check: (s) {
        final used = <EmotionTag>{};
        for (final e in s._entries) {
          used.addAll(e.tags);
        }
        return used.length >= EmotionTag.values.length;
      },
    ),
  ];

  List<Achievement> get unlockedAchievements =>
      _allAchievements.where((a) => a.check(this)).toList();

  List<Achievement> get lockedAchievements =>
      _allAchievements.where((a) => !a.check(this)).toList();

  List<Achievement> get allAchievements => List.unmodifiable(_allAchievements);

  // ─── TREE COLLECTION ──────────────────────────

  /// Unlockable tree types based on total entries.
  static const List<Map<String, String>> allTrees = [
    {'emoji': '🌱', 'name': 'Mầm non', 'requirement': '0 bài viết'},
    {'emoji': '🌿', 'name': 'Cây con', 'requirement': '3 bài viết'},
    {'emoji': '🪴', 'name': 'Cây trưởng thành', 'requirement': '9 bài viết'},
    {'emoji': '🌳', 'name': 'Đại thụ', 'requirement': '15 bài viết'},
    {'emoji': '🌲', 'name': 'Cây thông', 'requirement': '21 bài viết'},
    {'emoji': '🌸', 'name': 'Hoa anh đào', 'requirement': '30 bài viết'},
    {'emoji': '🌺', 'name': 'Hoa hibiscus', 'requirement': '50 bài viết'},
    {'emoji': '🌻', 'name': 'Hoa hướng dương', 'requirement': '75 bài viết'},
    {'emoji': '🏔️', 'name': 'Núi rừng', 'requirement': '100 bài viết'},
  ];

  static const List<int> _treeThresholds = [0, 3, 9, 15, 21, 30, 50, 75, 100];

  int get unlockedTreeCount {
    int count = 0;
    for (final t in _treeThresholds) {
      if (_entries.length >= t) count++;
    }
    return count;
  }

  // ─── GARDEN SHOP ──────────────────────────────

  /// Currently equipped items per category.
  final Map<GardenCategory, String> _equipped = {
    GardenCategory.tree: 'tree_sprout',
    GardenCategory.pot: 'pot_basic',
    GardenCategory.accessory: '',
    GardenCategory.background: 'bg_day',
  };

  /// Equip an item by its ID.
  void equip(String itemId) {
    final item = gardenCatalog.cast<GardenItem?>().firstWhere(
          (i) => i!.id == itemId,
          orElse: () => null,
        );
    if (item == null) return;
    _equipped[item.category] = itemId;
  }

  /// Unequip an accessory (set to empty).
  void unequipAccessory() {
    _equipped[GardenCategory.accessory] = '';
  }

  String equippedId(GardenCategory cat) => _equipped[cat] ?? '';

  GardenItem? equippedItem(GardenCategory cat) {
    final id = _equipped[cat];
    if (id == null || id.isEmpty) return null;
    return gardenCatalog.cast<GardenItem?>().firstWhere(
          (i) => i!.id == id,
          orElse: () => null,
        );
  }

  /// Check if an item is unlocked for the current user.
  bool isItemUnlocked(GardenItem item) {
    if (item.isDefault) return true;
    final check = _unlockChecks[item.id];
    return check != null && check(this);
  }

  /// All unlocked item IDs.
  Set<String> get unlockedItemIds =>
      gardenCatalog.where((i) => isItemUnlocked(i)).map((i) => i.id).toSet();

  /// Progress hint for a locked item (how close user is).
  String progressHint(GardenItem item) {
    return item.unlockHint;
  }

  // ─── ITEM CATALOG ─────────────────────────────

  static final List<GardenItem> gardenCatalog = [
    // ── Trees ──
    const GardenItem(
        id: 'tree_sprout',
        category: GardenCategory.tree,
        emoji: '🌱',
        name: 'Mầm non',
        unlockHint: 'Mặc định',
        isDefault: true),
    const GardenItem(
        id: 'tree_herb',
        category: GardenCategory.tree,
        emoji: '🌿',
        name: 'Cây con',
        unlockHint: 'Viết 3 bài nhật ký'),
    const GardenItem(
        id: 'tree_potted',
        category: GardenCategory.tree,
        emoji: '🪴',
        name: 'Cây trưởng thành',
        unlockHint: 'Viết 9 bài nhật ký'),
    const GardenItem(
        id: 'tree_oak',
        category: GardenCategory.tree,
        emoji: '🌳',
        name: 'Đại thụ',
        unlockHint: 'Viết 15 bài nhật ký'),
    const GardenItem(
        id: 'tree_pine',
        category: GardenCategory.tree,
        emoji: '🌲',
        name: 'Cây thông',
        unlockHint: 'Viết 21 bài nhật ký'),
    const GardenItem(
        id: 'tree_cherry',
        category: GardenCategory.tree,
        emoji: '🌸',
        name: 'Hoa anh đào',
        unlockHint: 'Viết 30 bài nhật ký'),
    const GardenItem(
        id: 'tree_palm',
        category: GardenCategory.tree,
        emoji: '🌴',
        name: 'Cây dừa',
        unlockHint: 'Streak 14 ngày'),
    const GardenItem(
        id: 'tree_bamboo',
        category: GardenCategory.tree,
        emoji: '🎋',
        name: 'Tre trúc',
        unlockHint: 'Streak 30 ngày'),

    // ── Pots ──
    const GardenItem(
        id: 'pot_basic',
        category: GardenCategory.pot,
        emoji: '🟤',
        name: 'Chậu đất',
        unlockHint: 'Mặc định',
        isDefault: true),
    const GardenItem(
        id: 'pot_vase',
        category: GardenCategory.pot,
        emoji: '🏺',
        name: 'Bình gốm',
        unlockHint: 'Streak 3 ngày'),
    const GardenItem(
        id: 'pot_jar',
        category: GardenCategory.pot,
        emoji: '🫙',
        name: 'Lọ thủy tinh',
        unlockHint: 'Streak 7 ngày'),
    const GardenItem(
        id: 'pot_bucket',
        category: GardenCategory.pot,
        emoji: '🪣',
        name: 'Xô gỗ',
        unlockHint: 'Viết 20 bài'),
    const GardenItem(
        id: 'pot_gift',
        category: GardenCategory.pot,
        emoji: '🎁',
        name: 'Hộp quà',
        unlockHint: 'Mở 5 thành tựu'),
    const GardenItem(
        id: 'pot_trophy',
        category: GardenCategory.pot,
        emoji: '🏆',
        name: 'Cúp vàng',
        unlockHint: 'Mở tất cả thành tựu'),

    // ── Accessories ──
    const GardenItem(
        id: 'acc_butterfly',
        category: GardenCategory.accessory,
        emoji: '🦋',
        name: 'Bướm',
        unlockHint: 'Dùng ≥5 emotion tags'),
    const GardenItem(
        id: 'acc_bee',
        category: GardenCategory.accessory,
        emoji: '🐝',
        name: 'Ong mật',
        unlockHint: 'Viết 10 bài nhật ký'),
    const GardenItem(
        id: 'acc_rainbow',
        category: GardenCategory.accessory,
        emoji: '🌈',
        name: 'Cầu vồng',
        unlockHint: 'Tâm trạng cải thiện từ buồn→vui'),
    const GardenItem(
        id: 'acc_cloud',
        category: GardenCategory.accessory,
        emoji: '☁️',
        name: 'Mây trắng',
        unlockHint: 'Hoàn thành 1 bài thở'),
    const GardenItem(
        id: 'acc_star',
        category: GardenCategory.accessory,
        emoji: '⭐',
        name: 'Ngôi sao',
        unlockHint: 'Streak 7 ngày'),
    const GardenItem(
        id: 'acc_windchime',
        category: GardenCategory.accessory,
        emoji: '🎐',
        name: 'Chuông gió',
        unlockHint: 'Streak 14 ngày'),
    const GardenItem(
        id: 'acc_flower',
        category: GardenCategory.accessory,
        emoji: '🪻',
        name: 'Hoa lavender',
        unlockHint: 'Tuần toàn mood tốt'),
    const GardenItem(
        id: 'acc_mushroom',
        category: GardenCategory.accessory,
        emoji: '🍄',
        name: 'Nấm',
        unlockHint: 'Viết 30 bài nhật ký'),
    const GardenItem(
        id: 'acc_bird',
        category: GardenCategory.accessory,
        emoji: '🐦',
        name: 'Chim',
        unlockHint: 'Viết 50 bài nhật ký'),
    const GardenItem(
        id: 'acc_moon',
        category: GardenCategory.accessory,
        emoji: '🌙',
        name: 'Trăng',
        unlockHint: 'Dùng tất cả emotion tags'),

    // ── Backgrounds ──
    const GardenItem(
        id: 'bg_day',
        category: GardenCategory.background,
        emoji: '☀️',
        name: 'Ban ngày',
        unlockHint: 'Mặc định',
        isDefault: true),
    const GardenItem(
        id: 'bg_sunset',
        category: GardenCategory.background,
        emoji: '🌅',
        name: 'Hoàng hôn',
        unlockHint: 'Viết 7 bài nhật ký'),
    const GardenItem(
        id: 'bg_night',
        category: GardenCategory.background,
        emoji: '🌙',
        name: 'Đêm trăng',
        unlockHint: 'Streak 7 ngày'),
    const GardenItem(
        id: 'bg_rain',
        category: GardenCategory.background,
        emoji: '🌧️',
        name: 'Mưa',
        unlockHint: 'Viết khi buồn 3 lần'),
    const GardenItem(
        id: 'bg_snow',
        category: GardenCategory.background,
        emoji: '❄️',
        name: 'Tuyết rơi',
        unlockHint: 'Streak 21 ngày'),
    const GardenItem(
        id: 'bg_galaxy',
        category: GardenCategory.background,
        emoji: '🌌',
        name: 'Ngân hà',
        unlockHint: 'Mở khóa ≥20 vật phẩm'),
  ];

  // ─── UNLOCK CHECKS ────────────────────────────

  static final Map<String, bool Function(SoulGardenService)> _unlockChecks = {
    // Trees
    'tree_sprout': (_) => true,
    'tree_herb': (s) => s._entries.length >= 3,
    'tree_potted': (s) => s._entries.length >= 9,
    'tree_oak': (s) => s._entries.length >= 15,
    'tree_pine': (s) => s._entries.length >= 21,
    'tree_cherry': (s) => s._entries.length >= 30,
    'tree_palm': (s) => s.streak >= 14,
    'tree_bamboo': (s) => s.streak >= 30,

    // Pots
    'pot_basic': (_) => true,
    'pot_vase': (s) => s.streak >= 3,
    'pot_jar': (s) => s.streak >= 7,
    'pot_bucket': (s) => s._entries.length >= 20,
    'pot_gift': (s) => s.unlockedAchievements.length >= 5,
    'pot_trophy': (s) => s.lockedAchievements.isEmpty,

    // Accessories
    'acc_butterfly': (s) {
      final usedTags = <EmotionTag>{};
      for (final e in s._entries) {
        usedTags.addAll(e.tags);
      }
      return usedTags.length >= 5;
    },
    'acc_bee': (s) => s._entries.length >= 10,
    'acc_rainbow': (s) {
      // Had sad→good mood improvement within 3 days
      for (int i = 1; i < s._entries.length; i++) {
        final prev = s._entries[i];
        final curr = s._entries[i - 1];
        if ((prev.mood == Mood.sad || prev.mood == Mood.awful) &&
            (curr.mood == Mood.good || curr.mood == Mood.awesome) &&
            curr.date.difference(prev.date).inDays.abs() <= 3) {
          return true;
        }
      }
      return false;
    },
    'acc_cloud': (s) =>
        s._entries.length >= 5, // Proxy: 5 entries (breathing not tracked yet)
    'acc_star': (s) => s.streak >= 7,
    'acc_windchime': (s) => s.streak >= 14,
    'acc_flower': (s) {
      final stats = s.statsForDays(7);
      return stats.totalEntries >= 7 && stats.averageScore >= 4.0;
    },
    'acc_mushroom': (s) => s._entries.length >= 30,
    'acc_bird': (s) => s._entries.length >= 50,
    'acc_moon': (s) {
      final usedTags = <EmotionTag>{};
      for (final e in s._entries) {
        usedTags.addAll(e.tags);
      }
      return usedTags.length >= EmotionTag.values.length;
    },

    // Backgrounds
    'bg_day': (_) => true,
    'bg_sunset': (s) => s._entries.length >= 7,
    'bg_rain': (s) {
      int sadCount = 0;
      for (final e in s._entries) {
        if (e.mood == Mood.sad || e.mood == Mood.awful) sadCount++;
      }
      return sadCount >= 3;
    },
    'bg_night': (s) => s.streak >= 7,
    'bg_snow': (s) => s.streak >= 21,
    'bg_galaxy': (s) {
      int unlocked = 0;
      for (final item in gardenCatalog) {
        final check = _unlockChecks[item.id];
        if (item.isDefault || (check != null && check(s))) unlocked++;
      }
      return unlocked >= 20;
    },
  };

  // ═══════════════════════════════════════════════════════════════════════════
  // MEMORY RECALL FEATURES - Gợi nhớ kỷ niệm đẹp, hỗ trợ trí nhớ
  // ═══════════════════════════════════════════════════════════════════════════

  /// Lấy kỷ niệm đẹp từ ngày trong quá khứ (time capsule)
  List<JournalEntry> getMemoriesFromExactlyOneYearAgo() {
    final now = DateTime.now();
    final targetYear = now.year - 1;
    final targetMonth = now.month;
    final targetDay = now.day;

    return _entries.where((e) {
      return e.date.year == targetYear &&
          e.date.month == targetMonth &&
          e.date.day == targetDay;
    }).toList();
  }

  /// Lấy kỷ niệm từ N ngày trước (tuỳ chọn)
  List<JournalEntry> getMemoriesFromDaysAgo(int daysAgo, {int? exactDay}) {
    final now = DateTime.now();
    final target = now.subtract(Duration(days: daysAgo));

    return _entries.where((e) {
      final matchesDate = exactDay != null
          ? e.date.day == exactDay
          : e.date.month == target.month && e.date.day == target.day;
      return e.date.year == target.year && matchesDate;
    }).toList();
  }

  /// Lấy các entry tích cực nhất (mood tốt) trong tháng qua
  List<JournalEntry> getPositiveMemories({int days = 30, int limit = 5}) {
    final now = DateTime.now();
    final from = now.subtract(Duration(days: days));

    final positiveEntries = _entries.where((e) {
      return e.date.isAfter(from) && e.mood.isPositive && e.content.isNotEmpty;
    }).toList();

    // Sắp xếp theo mood score giảm dần
    positiveEntries.sort((a, b) => b.mood.score.compareTo(a.mood.score));
    return positiveEntries.take(limit).toList();
  }

  /// Lấy các câu biết ơn (grateful) từ nhật ký
  List<JournalEntry> getGratefulMemories({int limit = 5}) {
    final gratefulEntries = _entries.where((e) {
      return e.tags.contains(EmotionTag.grateful) && e.content.isNotEmpty;
    }).toList();

    // Sắp xếp theo ngày mới nhất
    gratefulEntries.sort((a, b) => b.date.compareTo(a.date));
    return gratefulEntries.take(limit).toList();
  }

  /// Lấy kỷ niệm về gia đình/bạn bè
  List<JournalEntry> getFamilyMemories({int limit = 5}) {
    final familyKeywords = [
      'gia đình',
      'bố',
      'mẹ',
      'anh',
      'chị',
      'em',
      'con',
      'vợ',
      'chồng',
      'bạn bè',
      'bạn',
      'người yêu',
      'picnic',
      'summer',
      'noel',
      'tết',
      'sinh nhật'
    ];

    final familyEntries = _entries.where((e) {
      final contentLower = e.content.toLowerCase();
      return familyKeywords.any((k) => contentLower.contains(k));
    }).toList();

    familyEntries.sort((a, b) => b.date.compareTo(a.date));
    return familyEntries.take(limit).toList();
  }

  /// Lấy kỷ niệm về thành tựu/thành công
  List<AchievementEntry> getAchievementMemories({int limit = 5}) {
    final achievementKeywords = [
      'được khen',
      'thành công',
      'hoàn thành',
      'đạt được',
      'giải thưởng',
      'bằng',
      'chứng chỉ',
      'xong deadline',
      'ra mắt',
      'thăng tiến'
    ];

    final achievementEntries = _entries.where((e) {
      final contentLower = e.content.toLowerCase();
      return achievementKeywords.any((k) => contentLower.contains(k));
    }).toList();

    achievementEntries.sort((a, b) => b.date.compareTo(a.date));
    return achievementEntries.take(limit).toList();
  }

  /// Tạo memory capsule - lưu trữ khoảnh khắc đặc biệt
  /// Dùng cho tính năng "nhắc nhở kỷ niệm đẹp"
  MemoryCapsule createMemoryCapsule({
    required String title,
    required String content,
    Mood? mood,
  }) {
    return MemoryCapsule(
      id: 'capsule_${DateTime.now().millisecondsSinceEpoch}',
      title: title,
      content: content,
      mood: mood ?? Mood.good,
      createdAt: DateTime.now(),
      remindedAt: null,
    );
  }

  /// Lấy tất cả memory capsules
  final List<MemoryCapsule> _capsules = [];

  List<MemoryCapsule> get capsules => List.unmodifiable(_capsules);

  void addCapsule(MemoryCapsule capsule) {
    _capsules.insert(0, capsule);
  }

  void deleteCapsule(String id) {
    _capsules.removeWhere((c) => c.id == id);
  }

  /// Lấy capsules cần nhắc nhở hôm nay
  List<MemoryCapsule> getTodaysCapsules() {
    final now = DateTime.now();
    return _capsules.where((c) {
      if (c.remindedAt != null) return false;
      // Nhắc sau 1 tháng
      final shouldRemind = now.difference(c.createdAt).inDays >= 30;
      return shouldRemind;
    }).toList();
  }

  /// Lấy tất cả các ngày có nhật ký (để highlight trên calendar)
  Set<DateTime> getJournalDates({int? year, int? month}) {
    return _entries
        .where((e) {
          if (year != null && e.date.year != year) return false;
          if (month != null && e.date.month != month) return false;
          return true;
        })
        .map((e) => DateTime(e.date.year, e.date.month, e.date.day))
        .toSet();
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // AI MEMORY CONTEXT - Cung cấp context cho AI
  // ═══════════════════════════════════════════════════════════════════════════

  /// Tạo context summary cho AI (dùng trong prompt)
  String getAIMemoryContext() {
    if (_entries.isEmpty) {
      return 'Người dùng chưa có nhật ký Soul Garden.';
    }

    final recent7 = statsForDays(7);
    final recent30 = statsForDays(30);

    final buffer = StringBuffer();
    buffer.writeln('## Soul Garden Context');

    // Xu hướng tâm trạng
    buffer.writeln('- Xu hướng 7 ngày: ${recent7.averageScore.toStringAsFixed(1)}/5');
    if (recent7.trendPercent != null) {
      final trend = recent7.trendPercent!;
      buffer.writeln('- So với kỳ trước: ${trend > 0 ? "tích cực" : "cần chú ý"} (${trend.abs().toStringAsFixed(0)}%)');
    }

    // Tags phổ biến
    if (recent30.tagFrequency.isNotEmpty) {
      final topTags = recent30.tagFrequency.entries.toList()
        ..sort((a, b) => b.value.compareTo(a.value));
      final top3 = topTags.take(3).map((e) => '${e.key.emoji} ${e.key.label}').join(', ');
      buffer.writeln('- Tags phổ biến: $top3');
    }

    // Streak
    buffer.writeln('- Streak hiện tại: $streak ngày');

    // Kỷ niệm gần đây
    final recentEntries = _entries.take(3).toList();
    if (recentEntries.isNotEmpty) {
      buffer.writeln('- Nhật ký gần đây:');
      for (final e in recentEntries) {
        buffer.writeln('  * ${e.date.day}/${e.date.month}: ${e.content.substring(0, e.content.length.clamp(0, 50))}...');
      }
    }

    return buffer.toString();
  }

  /// Lấy comforting message dựa trên mood hiện tại
  String getComfortingMessage() {
    final recent7 = statsForDays(7);
    final avg = recent7.averageScore;

    if (avg >= 4.0) {
      // Tâm trạng tốt - khích lệ
      final positives = getPositiveMemories(limit: 1);
      if (positives.isNotEmpty) {
        return '🌟 Bạn đang làm rất tốt! Nhớ lại "${positives.first.content.substring(0, positives.first.content.length.clamp(0, 30))}..." - đó là khoảnh khắc tuyệt vời!';
      }
      return '🌟 Tâm trạng của bạn rất tích cực! Tiếp tục giữ nhé!';
    } else if (avg >= 3.0) {
      return '💪 Mọi thứ sẽ ổn thôi. Hãy nhớ rằng mỗi ngày đều có ý nghĩa.';
    } else if (avg >= 2.0) {
      // Mood không tốt lắm - an ủi
      final grateful = getGratefulMemories(limit: 1);
      if (grateful.isNotEmpty) {
        return '💛 Tôi hiểu bạn đang khó khăn. Nhưng hãy nhớ lại điều bạn từng biết ơn: "${grateful.first.content.substring(0, grateful.first.content.length.clamp(0, 30))}..."';
      }
      return '💛 Tôi hiểu. Hãy chia sẻ với tôi điều gì đang khiến bạn buồn nhé.';
    } else {
      // Mood rất thấp - khuyên chuyên gia
      return '❤️ Tôi lo lắng cho bạn. Bạn có muốn nói chuyện với chuyên gia không? Hoặc hãy gọi điện cho người thân. Bạn không cô đơn.';
    }
  }

  /// Lấy memory để AI an ủi
  String getComfortingMemoryContext() {
    final buffer = StringBuffer();
    buffer.writeln('### Khoảnh khắc tích cực trong nhật ký:');

    final positives = getPositiveMemories(days: 30, limit: 3);
    if (positives.isEmpty) {
      buffer.writeln('- Chưa có kỷ niệm tích cực gần đây');
    } else {
      for (final p in positives) {
        buffer.writeln('- ${p.date.day}/${p.date.month}: ${p.content}');
      }
    }

    buffer.writeln('\n### Những điều biết ơn:');
    final grateful = getGratefulMemories(limit: 2);
    if (grateful.isEmpty) {
      buffer.writeln('- Chưa có');
    } else {
      for (final g in grateful) {
        buffer.writeln('- ${g.content}');
      }
    }

    return buffer.toString();
  }
}

/// Memory Capsule - Lưu trữ khoảnh khắc đặc biệt để nhắc nhở sau
class MemoryCapsule {
  final String id;
  final String title;
  final String content;
  final Mood mood;
  final DateTime createdAt;
  final DateTime? remindedAt;

  const MemoryCapsule({
    required this.id,
    required this.title,
    required this.content,
    required this.mood,
    required this.createdAt,
    this.remindedAt,
  });

  MemoryCapsule copyWith({
    String? id,
    String? title,
    String? content,
    Mood? mood,
    DateTime? createdAt,
    DateTime? remindedAt,
  }) {
    return MemoryCapsule(
      id: id ?? this.id,
      title: title ?? this.title,
      content: content ?? this.content,
      mood: mood ?? this.mood,
      createdAt: createdAt ?? this.createdAt,
      remindedAt: remindedAt ?? this.remindedAt,
    );
  }
}

/// Achievement entry wrapper for memory recall
typedef AchievementEntry = JournalEntry;
