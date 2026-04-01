import 'package:shared_preferences/shared_preferences.dart';
import 'soul_garden_service.dart';
import 'memory_recall_service.dart';

/// Notification Service for daily journal reminders
/// Requires: flutter_local_notifications package
/// Add to pubspec.yaml: flutter_local_notifications: ^17.0.0
class NotificationService {
  NotificationService._();
  static final instance = NotificationService._();

  static const String _reminderEnabledKey = 'journal_reminder_enabled';
  static const String _reminderHourKey = 'journal_reminder_hour';
  static const String _reminderMinuteKey = 'journal_reminder_minute';

  SharedPreferences? _prefs;

  Future<void> init() async {
    _prefs = await SharedPreferences.getInstance();
  }

  /// Check if reminder is enabled
  bool get isReminderEnabled => _prefs?.getBool(_reminderEnabledKey) ?? false;

  /// Get reminder time
  ReminderTimeOfDay get reminderTime => ReminderTimeOfDay(
    hour: _prefs?.getInt(_reminderHourKey) ?? 20,
    minute: _prefs?.getInt(_reminderMinuteKey) ?? 0,
  );

  /// Enable/disable daily reminder
  Future<void> setReminderEnabled(bool enabled) async {
    await _prefs?.setBool(_reminderEnabledKey, enabled);
    if (enabled) {
      await _scheduleDailyReminder();
    } else {
      await _cancelAllNotifications();
    }
  }

  /// Set reminder time
  Future<void> setReminderTime(int hour, int minute) async {
    await _prefs?.setInt(_reminderHourKey, hour);
    await _prefs?.setInt(_reminderMinuteKey, minute);
    if (isReminderEnabled) {
      await _scheduleDailyReminder();
    }
  }

  /// Schedule daily notification at configured time
  Future<void> _scheduleDailyReminder() async {
    // TODO: Implement with flutter_local_notifications
    // Example:
    // final now = DateTime.now();
    // var scheduledDate = DateTime(now.year, now.month, now.day, reminderTime.hour, reminderTime.minute);
    // if (scheduledDate.isBefore(now)) {
    //   scheduledDate = scheduledDate.add(Duration(days: 1));
    // }
    // await flutterLocalNotificationsPlugin.zonedSchedule(
    //   0,
    //   "Nhật ký hôm nay",
    //   "Hãy ghi lại cảm xúc của bạn",
    //   scheduledDate.toUtc(),
    //   NotificationDetails(...),
    //   androidScheduleMode: AndroidScheduleMode.inexactAllowWhileIdle,
    // );
  }

  Future<void> _cancelAllNotifications() async {
    // TODO: Cancel all scheduled notifications
  }

  /// Show immediate notification (for memory recall, etc)
  Future<void> showNotification({
    required String title,
    required String body,
    int id = 0,
  }) async {
    // TODO: Implement with flutter_local_notifications
  }

  /// Check and show daily memory reminder
  Future<void> checkDailyMemoryReminder() async {
    final soulGarden = SoulGardenService.instance;
    final memoryRecall = MemoryRecallService.instance;

    // Check if user has journaled today
    final today = DateTime.now();
    final hasJournaledToday = soulGarden.entries.any((e) =>
      e.date.year == today.year &&
      e.date.month == today.month &&
      e.date.day == today.day
    );

    if (!hasJournaledToday) {
      // Show reminder
      await showNotification(
        title: 'Viết nhật ký nhé',
        body: 'Hãy ghi lại cảm xúc hôm nay',
      );
    }

    // Check memory capsule reminders
    final capsules = memoryRecall.getUpcomingReminders();
    for (final capsule in capsules.take(3)) {
      await showNotification(
        title: 'Kỷ niệm của bạn',
        body: capsule.content.length > 50 
          ? '${capsule.content.substring(0, 50)}...'
          : capsule.content,
      );
    }
  }
}

/// Time of day helper class
class ReminderTimeOfDay {
  final int hour;
  final int minute;

  const ReminderTimeOfDay({required this.hour, required this.minute});

  String get formatted => '${hour.toString().padLeft(2, '0')}:${minute.toString().padLeft(2, '0')}';
}
