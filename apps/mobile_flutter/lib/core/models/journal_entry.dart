import 'dart:ui';

/// Mood levels for journal entries — emoji-first design.
enum Mood {
  awesome,
  good,
  neutral,
  sad,
  awful,
}

extension MoodX on Mood {
  String get emoji {
    switch (this) {
      case Mood.awesome:
        return '🤩';
      case Mood.good:
        return '😊';
      case Mood.neutral:
        return '😐';
      case Mood.sad:
        return '😢';
      case Mood.awful:
        return '😭';
    }
  }

  String get label {
    switch (this) {
      case Mood.awesome:
        return 'Tuyệt vời';
      case Mood.good:
        return 'Tốt';
      case Mood.neutral:
        return 'Bình thường';
      case Mood.sad:
        return 'Buồn';
      case Mood.awful:
        return 'Rất tệ';
    }
  }

  Color get color {
    switch (this) {
      case Mood.awesome:
        return const Color(0xFF22C55E);
      case Mood.good:
        return const Color(0xFF60A5FA);
      case Mood.neutral:
        return const Color(0xFFA78BFA);
      case Mood.sad:
        return const Color(0xFFF59E0B);
      case Mood.awful:
        return const Color(0xFFEF4444);
    }
  }

  /// Numeric score: awesome=5 … awful=1
  int get score {
    switch (this) {
      case Mood.awesome:
        return 5;
      case Mood.good:
        return 4;
      case Mood.neutral:
        return 3;
      case Mood.sad:
        return 2;
      case Mood.awful:
        return 1;
    }
  }

  bool get isPositive => this == Mood.awesome || this == Mood.good;
  bool get isNegative => this == Mood.sad || this == Mood.awful;
}

/// Emotion tags to attach to a journal entry.
enum EmotionTag {
  grateful,
  stressed,
  happy,
  anxious,
  tired,
  motivated,
  lonely,
  loved,
  angry,
  peaceful,
}

extension EmotionTagX on EmotionTag {
  String get label {
    switch (this) {
      case EmotionTag.grateful:
        return 'Biết ơn';
      case EmotionTag.stressed:
        return 'Căng thẳng';
      case EmotionTag.happy:
        return 'Vui vẻ';
      case EmotionTag.anxious:
        return 'Lo lắng';
      case EmotionTag.tired:
        return 'Mệt mỏi';
      case EmotionTag.motivated:
        return 'Có động lực';
      case EmotionTag.lonely:
        return 'Cô đơn';
      case EmotionTag.loved:
        return 'Được yêu thương';
      case EmotionTag.angry:
        return 'Tức giận';
      case EmotionTag.peaceful:
        return 'Bình yên';
    }
  }

  String get emoji {
    switch (this) {
      case EmotionTag.grateful:
        return '🙏';
      case EmotionTag.stressed:
        return '😰';
      case EmotionTag.happy:
        return '😄';
      case EmotionTag.anxious:
        return '😟';
      case EmotionTag.tired:
        return '😴';
      case EmotionTag.motivated:
        return '💪';
      case EmotionTag.lonely:
        return '🥺';
      case EmotionTag.loved:
        return '🥰';
      case EmotionTag.angry:
        return '😡';
      case EmotionTag.peaceful:
        return '☮️';
    }
  }
}

/// A single journal entry in Soul Garden.
class JournalEntry {
  final String id;
  final DateTime date;
  final Mood mood;
  final String content;
  final Set<EmotionTag> tags;

  const JournalEntry({
    required this.id,
    required this.date,
    required this.mood,
    this.content = '',
    this.tags = const {},
  });

  JournalEntry copyWith({
    String? id,
    DateTime? date,
    Mood? mood,
    String? content,
    Set<EmotionTag>? tags,
  }) {
    return JournalEntry(
      id: id ?? this.id,
      date: date ?? this.date,
      mood: mood ?? this.mood,
      content: content ?? this.content,
      tags: tags ?? this.tags,
    );
  }
}
