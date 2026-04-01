import 'package:shared_preferences/shared_preferences.dart';
import 'dart:convert';

import '../models/achievement_model.dart';

/// ══════════════════════════════════════════════════════════════
/// ACHIEVEMENT SERVICE — Quản lý thành tựu và chuỗi hoạt động
/// Lưu trữ local bằng SharedPreferences (offline-first)
/// ══════════════════════════════════════════════════════════════
class AchievementService {
  static const _streakKey = 'achievement_streaks';
  static const _progressKey = 'achievement_progress';
  static const _xpKey = 'achievement_total_xp';

  SharedPreferences? _prefs;

  Future<void> _ensureInit() async {
    _prefs ??= await SharedPreferences.getInstance();
  }

  // ── STREAKS ──

  Future<List<ActivityStreak>> getStreaks() async {
    await _ensureInit();
    final raw = _prefs!.getString(_streakKey);
    if (raw == null) return _defaultStreaks();

    final List<dynamic> list = jsonDecode(raw);
    return list.map((e) => _streakFromJson(e)).toList();
  }

  Future<ActivityStreak> recordActivity(AchievementCategory category) async {
    await _ensureInit();
    final streaks = await getStreaks();
    final index = streaks.indexWhere((s) => s.category == category);

    final now = DateTime.now();
    final today = DateTime(now.year, now.month, now.day);

    ActivityStreak updated;

    if (index == -1) {
      updated = ActivityStreak(
        category: category,
        currentStreak: 1,
        longestStreak: 1,
        lastActivityDate: today,
        totalActivities: 1,
      );
      streaks.add(updated);
    } else {
      final existing = streaks[index];
      final lastDate = DateTime(
        existing.lastActivityDate.year,
        existing.lastActivityDate.month,
        existing.lastActivityDate.day,
      );

      if (lastDate == today) {
        return existing;
      }

      final dayDiff = today.difference(lastDate).inDays;
      final newStreak = dayDiff == 1 ? existing.currentStreak + 1 : 1;
      final newLongest =
          newStreak > existing.longestStreak ? newStreak : existing.longestStreak;

      updated = existing.copyWith(
        currentStreak: newStreak,
        longestStreak: newLongest,
        lastActivityDate: today,
        totalActivities: existing.totalActivities + 1,
      );
      streaks[index] = updated;
    }

    await _saveStreaks(streaks);
    await _checkStreakAchievements(category, updated);
    return updated;
  }

  // ── ACHIEVEMENTS ──

  Future<List<AchievementProgress>> getAllProgress() async {
    await _ensureInit();
    final raw = _prefs!.getString(_progressKey);
    if (raw == null) {
      return AchievementDatabase.all
          .map((d) => AchievementProgress(
                definitionId: d.id,
                currentCount: 0,
                isUnlocked: false,
              ))
          .toList();
    }
    final List<dynamic> list = jsonDecode(raw);
    return list.map((e) => _progressFromJson(e)).toList();
  }

  Future<AchievementProgress> incrementProgress(String achievementId,
      {int amount = 1}) async {
    await _ensureInit();
    final allProgress = await getAllProgress();
    final index = allProgress.indexWhere((p) => p.definitionId == achievementId);
    final def = AchievementDatabase.findById(achievementId);
    if (def == null) {
      return AchievementProgress(
        definitionId: achievementId,
        currentCount: 0,
        isUnlocked: false,
      );
    }

    AchievementProgress updated;

    if (index == -1) {
      final newCount = amount.clamp(0, def.targetCount);
      updated = AchievementProgress(
        definitionId: achievementId,
        currentCount: newCount,
        isUnlocked: newCount >= def.targetCount,
        unlockedAt: newCount >= def.targetCount ? DateTime.now() : null,
      );
      allProgress.add(updated);
    } else {
      final existing = allProgress[index];
      if (existing.isUnlocked) return existing;

      final newCount = (existing.currentCount + amount).clamp(0, def.targetCount);
      final justUnlocked = newCount >= def.targetCount;
      updated = existing.copyWith(
        currentCount: newCount,
        isUnlocked: justUnlocked,
        unlockedAt: justUnlocked ? DateTime.now() : null,
      );
      allProgress[index] = updated;

      if (justUnlocked) {
        await _addXp(def.rewardXp);
      }
    }

    await _saveProgress(allProgress);
    return updated;
  }

  // ── SUMMARY ──

  Future<UserAchievementSummary> getSummary() async {
    await _ensureInit();
    final progress = await getAllProgress();
    final streaks = await getStreaks();
    final xp = _prefs!.getInt(_xpKey) ?? 0;

    final unlockedCount = progress.where((p) => p.isUnlocked).length;

    return UserAchievementSummary(
      totalXp: xp,
      level: (xp / 100).floor() + 1,
      unlockedCount: unlockedCount,
      totalCount: AchievementDatabase.all.length,
      streaks: streaks,
    );
  }

  Future<int> getTotalXp() async {
    await _ensureInit();
    return _prefs!.getInt(_xpKey) ?? 0;
  }

  // ── INTERNAL ──

  Future<void> _checkStreakAchievements(
      AchievementCategory category, ActivityStreak streak) async {
    if (category == AchievementCategory.fitness) {
      if (streak.totalActivities >= 1) {
        await incrementProgress('fitness_first');
      }
      if (streak.currentStreak >= 3) {
        await incrementProgress('fitness_streak_3', amount: streak.currentStreak);
      }
      if (streak.currentStreak >= 7) {
        await incrementProgress('fitness_streak_7', amount: streak.currentStreak);
      }
      if (streak.currentStreak >= 30) {
        await incrementProgress('fitness_streak_30', amount: streak.currentStreak);
      }
      if (streak.totalActivities >= 10) {
        await incrementProgress('fitness_total_10', amount: streak.totalActivities);
      }
    } else if (category == AchievementCategory.health) {
      if (streak.currentStreak >= 7) {
        await incrementProgress('health_checkin_7', amount: streak.currentStreak);
      }
      if (streak.currentStreak >= 30) {
        await incrementProgress('health_checkin_30', amount: streak.currentStreak);
      }
    } else if (category == AchievementCategory.soulGarden) {
      if (streak.totalActivities >= 1) {
        await incrementProgress('garden_first_entry');
      }
      if (streak.currentStreak >= 7) {
        await incrementProgress('garden_streak_7', amount: streak.currentStreak);
      }
      if (streak.currentStreak >= 30) {
        await incrementProgress('garden_streak_30', amount: streak.currentStreak);
      }
    } else if (category == AchievementCategory.consult) {
      if (streak.totalActivities >= 1) {
        await incrementProgress('consult_first');
      }
      if (streak.totalActivities >= 5) {
        await incrementProgress('consult_5', amount: streak.totalActivities);
      }
    } else if (category == AchievementCategory.medicine) {
      if (streak.totalActivities >= 1) {
        await incrementProgress('medicine_first_scan');
      }
      if (streak.totalActivities >= 10) {
        await incrementProgress('medicine_scan_10', amount: streak.totalActivities);
      }
    }
  }

  Future<void> _addXp(int amount) async {
    await _ensureInit();
    final current = _prefs!.getInt(_xpKey) ?? 0;
    await _prefs!.setInt(_xpKey, current + amount);
  }

  Future<void> _saveStreaks(List<ActivityStreak> streaks) async {
    final json = streaks.map((s) => _streakToJson(s)).toList();
    await _prefs!.setString(_streakKey, jsonEncode(json));
  }

  Future<void> _saveProgress(List<AchievementProgress> progress) async {
    final json = progress.map((p) => _progressToJson(p)).toList();
    await _prefs!.setString(_progressKey, jsonEncode(json));
  }

  List<ActivityStreak> _defaultStreaks() {
    return [
      ActivityStreak(
        category: AchievementCategory.fitness,
        currentStreak: 0,
        longestStreak: 0,
        lastActivityDate: DateTime(2000),
        totalActivities: 0,
      ),
      ActivityStreak(
        category: AchievementCategory.health,
        currentStreak: 0,
        longestStreak: 0,
        lastActivityDate: DateTime(2000),
        totalActivities: 0,
      ),
      ActivityStreak(
        category: AchievementCategory.soulGarden,
        currentStreak: 0,
        longestStreak: 0,
        lastActivityDate: DateTime(2000),
        totalActivities: 0,
      ),
    ];
  }

  // ── JSON helpers ──

  Map<String, dynamic> _streakToJson(ActivityStreak s) => {
        'category': s.category.id,
        'currentStreak': s.currentStreak,
        'longestStreak': s.longestStreak,
        'lastActivityDate': s.lastActivityDate.toIso8601String(),
        'totalActivities': s.totalActivities,
      };

  ActivityStreak _streakFromJson(Map<String, dynamic> j) => ActivityStreak(
        category: AchievementCategory.values
            .firstWhere((c) => c.id == j['category'],
                orElse: () => AchievementCategory.general),
        currentStreak: j['currentStreak'] ?? 0,
        longestStreak: j['longestStreak'] ?? 0,
        lastActivityDate:
            DateTime.tryParse(j['lastActivityDate'] ?? '') ?? DateTime(2000),
        totalActivities: j['totalActivities'] ?? 0,
      );

  Map<String, dynamic> _progressToJson(AchievementProgress p) => {
        'definitionId': p.definitionId,
        'currentCount': p.currentCount,
        'isUnlocked': p.isUnlocked,
        'unlockedAt': p.unlockedAt?.toIso8601String(),
      };

  AchievementProgress _progressFromJson(Map<String, dynamic> j) =>
      AchievementProgress(
        definitionId: j['definitionId'] ?? '',
        currentCount: j['currentCount'] ?? 0,
        isUnlocked: j['isUnlocked'] ?? false,
        unlockedAt: j['unlockedAt'] != null
            ? DateTime.tryParse(j['unlockedAt'])
            : null,
      );
}
