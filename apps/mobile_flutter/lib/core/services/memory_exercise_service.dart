import 'dart:math';
import '../models/journal_entry.dart';
import 'soul_garden_service.dart';

enum ExerciseType { recallDate, recallMood, gratitude, reflection }

class Exercise {
  final String id;
  final String title;
  final String description;
  final String emoji;
  final ExerciseType type;
  const Exercise({
    required this.id,
    required this.title,
    required this.description,
    required this.emoji,
    required this.type,
  });
}

class MemoryExerciseService {
  MemoryExerciseService._();
  static final instance = MemoryExerciseService._();
  final SoulGardenService _soulGarden = SoulGardenService.instance;
  final Random _random = Random();

  static const List<Exercise> availableExercises = [
    Exercise(
      id: 'recall_date',
      title: 'Nho lai ngay',
      description: 'Ban hay cho biet ngay viet nhat ky?',
      emoji: '\u{1F4C5}',
      type: ExerciseType.recallDate,
    ),
    Exercise(
      id: 'recall_mood',
      title: 'Nho lai tam trang',
      description: 'Tam trang khi viet nhat ky?',
      emoji: '\u{1F60A}',
      type: ExerciseType.recallMood,
    ),
    Exercise(
      id: 'gratitude',
      title: 'Bai tap biet on',
      description: 'Ke 3 dieu ban biet on?',
      emoji: '\u{1F64F}',
      type: ExerciseType.gratitude,
    ),
  ];

  Exercise getRandomExercise() =>
      availableExercises[_random.nextInt(availableExercises.length)];

  List<Exercise> getAllExercises() => availableExercises;

  int calculateMemoryScore() {
    final entries = _soulGarden.entries;
    if (entries.isEmpty) return 0;
    int score = 0;
    score += (entries.length * 2).clamp(0, 30);
    score += (_soulGarden.streak * 3).clamp(0, 30);
    final tags = <EmotionTag>{};
    for (final e in entries) {
      tags.addAll(e.tags);
    }
    score += (tags.length * 4).clamp(0, 20);
    return score.clamp(0, 100);
  }

  List<String> getMemoryImprovementTips() {
    final tips = <String>[];
    if (_soulGarden.entries.length < 7) {
      tips.add('Hay viet nhat ky thuong xuyen');
    }
    tips.add('Lam bai tap tri nho hang ngay');
    return tips;
  }
}
