/// ══════════════════════════════════════════════════════════════
/// ACHIEVEMENT & STREAK MODELS
/// Hệ thống thành tựu và chuỗi hoạt động cho MediSign AI
/// ══════════════════════════════════════════════════════════════
library;

/// Loại thành tựu
enum AchievementCategory {
  fitness('fitness', 'Tập thể dục', '🏋️'),
  health('health', 'Sức khỏe', '❤️'),
  consult('consult', 'Hỏi bệnh', '🩺'),
  medicine('medicine', 'Thuốc', '💊'),
  soulGarden('soul_garden', 'Vườn Tâm Hồn', '🌱'),
  profile('profile', 'Hồ sơ', '👤'),
  general('general', 'Chung', '⭐');

  final String id;
  final String label;
  final String emoji;
  const AchievementCategory(this.id, this.label, this.emoji);
}

/// Mức độ thành tựu
enum AchievementTier {
  bronze('bronze', 'Đồng', '🥉', 1),
  silver('silver', 'Bạc', '🥈', 2),
  gold('gold', 'Vàng', '🥇', 3),
  diamond('diamond', 'Kim cương', '💎', 4);

  final String id;
  final String label;
  final String emoji;
  final int level;
  const AchievementTier(this.id, this.label, this.emoji, this.level);
}

/// Định nghĩa một thành tựu
class AchievementDefinition {
  const AchievementDefinition({
    required this.id,
    required this.title,
    required this.description,
    required this.category,
    required this.tier,
    required this.targetCount,
    required this.emoji,
    this.rewardXp = 0,
  });

  final String id;
  final String title;
  final String description;
  final AchievementCategory category;
  final AchievementTier tier;
  final int targetCount;
  final String emoji;
  final int rewardXp;
}

/// Tiến trình đạt thành tựu của người dùng
class AchievementProgress {
  const AchievementProgress({
    required this.definitionId,
    required this.currentCount,
    required this.isUnlocked,
    this.unlockedAt,
  });

  final String definitionId;
  final int currentCount;
  final bool isUnlocked;
  final DateTime? unlockedAt;

  double progressPercent(int targetCount) =>
      targetCount > 0 ? (currentCount / targetCount).clamp(0.0, 1.0) : 0.0;

  AchievementProgress copyWith({
    int? currentCount,
    bool? isUnlocked,
    DateTime? unlockedAt,
  }) {
    return AchievementProgress(
      definitionId: definitionId,
      currentCount: currentCount ?? this.currentCount,
      isUnlocked: isUnlocked ?? this.isUnlocked,
      unlockedAt: unlockedAt ?? this.unlockedAt,
    );
  }
}

/// Thông tin chuỗi (streak) hoạt động
class ActivityStreak {
  const ActivityStreak({
    required this.category,
    required this.currentStreak,
    required this.longestStreak,
    required this.lastActivityDate,
    required this.totalActivities,
  });

  final AchievementCategory category;
  final int currentStreak;
  final int longestStreak;
  final DateTime lastActivityDate;
  final int totalActivities;

  bool get isActiveToday {
    final now = DateTime.now();
    return lastActivityDate.year == now.year &&
        lastActivityDate.month == now.month &&
        lastActivityDate.day == now.day;
  }

  bool get isStreakBroken {
    final now = DateTime.now();
    final diff = now.difference(lastActivityDate).inDays;
    return diff > 1;
  }

  ActivityStreak copyWith({
    int? currentStreak,
    int? longestStreak,
    DateTime? lastActivityDate,
    int? totalActivities,
  }) {
    return ActivityStreak(
      category: category,
      currentStreak: currentStreak ?? this.currentStreak,
      longestStreak: longestStreak ?? this.longestStreak,
      lastActivityDate: lastActivityDate ?? this.lastActivityDate,
      totalActivities: totalActivities ?? this.totalActivities,
    );
  }
}

/// Tổng hợp thông tin người dùng
class UserAchievementSummary {
  const UserAchievementSummary({
    required this.totalXp,
    required this.level,
    required this.unlockedCount,
    required this.totalCount,
    required this.streaks,
  });

  final int totalXp;
  final int level;
  final int unlockedCount;
  final int totalCount;
  final List<ActivityStreak> streaks;

  double get progressToNextLevel {
    final xpForCurrentLevel = level * 100;
    final xpForNextLevel = (level + 1) * 100;
    return ((totalXp - xpForCurrentLevel) /
            (xpForNextLevel - xpForCurrentLevel))
        .clamp(0.0, 1.0);
  }
}

/// ══════════════════════════════════════════════════════════════
/// PREDEFINED ACHIEVEMENTS
/// ══════════════════════════════════════════════════════════════
class AchievementDatabase {
  static const List<AchievementDefinition> all = [
    // ── Fitness Streaks ──
    AchievementDefinition(
      id: 'fitness_first',
      title: 'Bước đầu tiên',
      description: 'Hoàn thành bài tập đầu tiên',
      category: AchievementCategory.fitness,
      tier: AchievementTier.bronze,
      targetCount: 1,
      emoji: '🏃',
      rewardXp: 10,
    ),
    AchievementDefinition(
      id: 'fitness_streak_3',
      title: 'Chuỗi 3 ngày',
      description: 'Tập thể dục 3 ngày liên tiếp',
      category: AchievementCategory.fitness,
      tier: AchievementTier.bronze,
      targetCount: 3,
      emoji: '🔥',
      rewardXp: 30,
    ),
    AchievementDefinition(
      id: 'fitness_streak_7',
      title: 'Chuỗi 7 ngày',
      description: 'Tập thể dục 7 ngày liên tiếp',
      category: AchievementCategory.fitness,
      tier: AchievementTier.silver,
      targetCount: 7,
      emoji: '💪',
      rewardXp: 70,
    ),
    AchievementDefinition(
      id: 'fitness_streak_30',
      title: 'Chiến binh 30 ngày',
      description: 'Tập thể dục 30 ngày liên tiếp',
      category: AchievementCategory.fitness,
      tier: AchievementTier.gold,
      targetCount: 30,
      emoji: '🏆',
      rewardXp: 300,
    ),
    AchievementDefinition(
      id: 'fitness_total_10',
      title: '10 bài tập',
      description: 'Hoàn thành tổng cộng 10 bài tập',
      category: AchievementCategory.fitness,
      tier: AchievementTier.silver,
      targetCount: 10,
      emoji: '🎯',
      rewardXp: 50,
    ),

    // ── Health Profile ──
    AchievementDefinition(
      id: 'profile_complete',
      title: 'Hồ sơ đầy đủ',
      description: 'Điền đầy đủ hồ sơ sức khỏe',
      category: AchievementCategory.profile,
      tier: AchievementTier.bronze,
      targetCount: 1,
      emoji: '📋',
      rewardXp: 20,
    ),
    AchievementDefinition(
      id: 'health_checkin_7',
      title: 'Chuỗi sức khỏe 7 ngày',
      description: 'Cập nhật sức khỏe 7 ngày liên tiếp',
      category: AchievementCategory.health,
      tier: AchievementTier.silver,
      targetCount: 7,
      emoji: '📊',
      rewardXp: 70,
    ),
    AchievementDefinition(
      id: 'health_checkin_30',
      title: 'Bậc thầy sức khỏe',
      description: 'Cập nhật sức khỏe 30 ngày liên tiếp',
      category: AchievementCategory.health,
      tier: AchievementTier.gold,
      targetCount: 30,
      emoji: '🌟',
      rewardXp: 300,
    ),

    // ── Consult ──
    AchievementDefinition(
      id: 'consult_first',
      title: 'Lần đầu hỏi bệnh',
      description: 'Hoàn thành cuộc tư vấn đầu tiên',
      category: AchievementCategory.consult,
      tier: AchievementTier.bronze,
      targetCount: 1,
      emoji: '🩺',
      rewardXp: 15,
    ),
    AchievementDefinition(
      id: 'consult_5',
      title: 'Người chăm lo sức khỏe',
      description: 'Hoàn thành 5 cuộc tư vấn',
      category: AchievementCategory.consult,
      tier: AchievementTier.silver,
      targetCount: 5,
      emoji: '💬',
      rewardXp: 50,
    ),

    // ── Medicine ──
    AchievementDefinition(
      id: 'medicine_first_scan',
      title: 'Quét thuốc đầu tiên',
      description: 'Quét thuốc bằng camera lần đầu',
      category: AchievementCategory.medicine,
      tier: AchievementTier.bronze,
      targetCount: 1,
      emoji: '📸',
      rewardXp: 15,
    ),
    AchievementDefinition(
      id: 'medicine_scan_10',
      title: 'Dược sĩ nhí',
      description: 'Quét 10 loại thuốc',
      category: AchievementCategory.medicine,
      tier: AchievementTier.silver,
      targetCount: 10,
      emoji: '💊',
      rewardXp: 50,
    ),

    // ── Soul Garden ──
    AchievementDefinition(
      id: 'garden_first_entry',
      title: 'Hạt giống đầu tiên',
      description: 'Viết nhật ký tâm trạng lần đầu',
      category: AchievementCategory.soulGarden,
      tier: AchievementTier.bronze,
      targetCount: 1,
      emoji: '🌱',
      rewardXp: 10,
    ),
    AchievementDefinition(
      id: 'garden_streak_7',
      title: 'Vườn 7 ngày',
      description: 'Viết nhật ký 7 ngày liên tiếp',
      category: AchievementCategory.soulGarden,
      tier: AchievementTier.silver,
      targetCount: 7,
      emoji: '🌸',
      rewardXp: 70,
    ),
    AchievementDefinition(
      id: 'garden_streak_30',
      title: 'Vườn trăm hoa',
      description: 'Viết nhật ký 30 ngày liên tiếp',
      category: AchievementCategory.soulGarden,
      tier: AchievementTier.gold,
      targetCount: 30,
      emoji: '🌺',
      rewardXp: 300,
    ),
  ];

  static List<AchievementDefinition> byCategory(AchievementCategory cat) =>
      all.where((a) => a.category == cat).toList();

  static AchievementDefinition? findById(String id) {
    try {
      return all.firstWhere((a) => a.id == id);
    } catch (_) {
      return null;
    }
  }
}
