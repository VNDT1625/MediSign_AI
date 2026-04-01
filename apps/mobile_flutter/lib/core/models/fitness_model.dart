// Model for exercise definitions and workout tracking
// Part of Module 6: AI Fitness Coach

class Exercise {
  final String id;
  final String name;
  final String nameVi; // Vietnamese name
  final String description;
  final String descriptionVi;
  final String targetArea; // lower_body, upper_body, core
  final List<String> muscleGroups;
  final ExerciseReference reference;
  final String iconName;

  const Exercise({
    required this.id,
    required this.name,
    required this.nameVi,
    required this.description,
    required this.descriptionVi,
    required this.targetArea,
    required this.muscleGroups,
    required this.reference,
    required this.iconName,
  });
}

class ExerciseReference {
  final Map<String, AngleRange> idealAngles;
  final List<String> commonMistakes;

  const ExerciseReference({
    required this.idealAngles,
    required this.commonMistakes,
  });
}

class AngleRange {
  final double min;
  final double max;

  const AngleRange(this.min, this.max);

  bool isInRange(double angle) => angle >= min && angle <= max;

  double get ideal => (min + max) / 2;
}

class WorkoutSession {
  final String id;
  final String exerciseId;
  final DateTime startTime;
  final DateTime? endTime;
  final int totalReps;
  final int goodReps;
  final double formScore;
  final List<RepData> repHistory;

  const WorkoutSession({
    required this.id,
    required this.exerciseId,
    required this.startTime,
    this.endTime,
    required this.totalReps,
    required this.goodReps,
    required this.formScore,
    required this.repHistory,
  });

  WorkoutSession copyWith({
    String? id,
    String? exerciseId,
    DateTime? startTime,
    DateTime? endTime,
    int? totalReps,
    int? goodReps,
    double? formScore,
    List<RepData>? repHistory,
  }) {
    return WorkoutSession(
      id: id ?? this.id,
      exerciseId: exerciseId ?? this.exerciseId,
      startTime: startTime ?? this.startTime,
      endTime: endTime ?? this.endTime,
      totalReps: totalReps ?? this.totalReps,
      goodReps: goodReps ?? this.goodReps,
      formScore: formScore ?? this.formScore,
      repHistory: repHistory ?? this.repHistory,
    );
  }
}

class RepData {
  final int repNumber;
  final double minAngle;
  final double maxAngle;
  final bool isGoodForm;
  final List<String> mistakes;

  const RepData({
    required this.repNumber,
    required this.minAngle,
    required this.maxAngle,
    required this.isGoodForm,
    required this.mistakes,
  });
}

enum FitnessGoal {
  loseWeight('lose_weight', 'Giảm cân', 'Giảm cân nhanh chóng'),
  buildMuscle('build_muscle', 'Tăng cơ', 'Xây dựng cơ bắp'),
  maintain('maintain', 'Duy trì', 'Giữ dáng khỏe mạnh');

  final String id;
  final String name;
  final String description;

  const FitnessGoal(this.id, this.name, this.description);
}

// Predefined exercises with angle references
class ExerciseDatabase {
  static const List<Exercise> mvpExercises = [
    Exercise(
      id: 'squat',
      name: 'Squat',
      nameVi: 'Ngồi xổm',
      description: 'Lower body exercise - thighs parallel to floor',
      descriptionVi: 'Bài tập phần thân dưới - đùi song song sàn',
      targetArea: 'lower_body',
      muscleGroups: ['Quadriceps', 'Glutes', 'Hamstrings'],
      iconName: 'fitness_center',
      reference: ExerciseReference(
        idealAngles: {
          'knee': AngleRange(85, 95),
          'hip': AngleRange(70, 90),
          'back': AngleRange(30, 60),
        },
        commonMistakes: [
          'knee_valgus',
          'heel_rise',
          'lumbar_flexion',
        ],
      ),
    ),
    Exercise(
      id: 'pushup',
      name: 'Push-up',
      nameVi: 'Chống đẩy',
      description: 'Upper body - chest and arms',
      descriptionVi: 'Bài tập phần thân trên - ngực và tay',
      targetArea: 'upper_body',
      muscleGroups: ['Chest', 'Triceps', 'Shoulders'],
      iconName: 'sports_gymnastics',
      reference: ExerciseReference(
        idealAngles: {
          'elbow': AngleRange(80, 100),
          'body': AngleRange(170, 180),
        },
        commonMistakes: [
          'flared_elbows',
          'sagging_hip',
          'piked_hip',
        ],
      ),
    ),
    Exercise(
      id: 'plank',
      name: 'Plank',
      nameVi: 'Plank',
      description: 'Core exercise - hold body straight',
      descriptionVi: 'Bài tập cơ trung tâm - giữ body thẳng',
      targetArea: 'core',
      muscleGroups: ['Abs', 'Core', 'Shoulders'],
      iconName: 'accessibility_new',
      reference: ExerciseReference(
        idealAngles: {
          'shoulder_hip': AngleRange(170, 180),
          'hip_ankle': AngleRange(170, 180),
        },
        commonMistakes: [
          'sagging_hip',
          'piked_hip',
          'head_up',
        ],
      ),
    ),
    Exercise(
      id: 'lunge',
      name: 'Lunge',
      nameVi: 'Lunge',
      description: 'Lower body - one leg at a time',
      descriptionVi: 'Bài tập thân dưới - từng chân một',
      targetArea: 'lower_body',
      muscleGroups: ['Quadriceps', 'Glutes', 'Hamstrings'],
      iconName: 'directions_walk',
      reference: ExerciseReference(
        idealAngles: {
          'front_knee': AngleRange(85, 95),
          'back_knee': AngleRange(80, 100),
        },
        commonMistakes: [
          'front_heel_up',
          'narrow_stance',
          'torso_forward',
        ],
      ),
    ),
    Exercise(
      id: 'deadlift',
      name: 'Deadlift',
      nameVi: 'Nâng tạ',
      description: 'Full body - hip hinge movement',
      descriptionVi: 'Toàn thân - động tác nghiêng hông',
      targetArea: 'lower_body',
      muscleGroups: ['Back', 'Hamstrings', 'Glutes', 'Core'],
      iconName: 'fitness_center',
      reference: ExerciseReference(
        idealAngles: {
          'hip': AngleRange(45, 70),
          'knee': AngleRange(130, 160),
          'back': AngleRange(-15, 15), // neutral spine
        },
        commonMistakes: [
          'rounded_back',
          'squatting',
          'hyperextension',
        ],
      ),
    ),
  ];

  static Exercise? getById(String id) {
    try {
      return mvpExercises.firstWhere((e) => e.id == id);
    } catch (_) {
      return null;
    }
  }

  static List<Exercise> getByTargetArea(String area) {
    return mvpExercises.where((e) => e.targetArea == area).toList();
  }
}

// Mistake translations for UI
class MistakeTranslations {
  static const Map<String, String> vi = {
    'knee_valgus': 'Đầu gối hướng vào trong',
    'heel_rise': 'Gót chân nhấc lên',
    'lumbar_flexion': 'Lưng quá cong',
    'flared_elbows': 'Khuỷu tay bay ra ngoài quá xa',
    'sagging_hip': 'Mông hạ thấp',
    'piked_hip': 'Mông cao quá',
    'front_heel_up': 'Gót chân trước nhấc',
    'narrow_stance': 'Chân quá hẹp',
    'torso_forward': 'Thân người nghiêng quá',
    'rounded_back': 'Lưng tròn (NGUY HIỂM)',
    'squatting': 'Ngồi xổm thay vì nghiêng hông',
    'hyperextension': 'Quá arch lưng',
    'head_up': 'Đầu ngước lên',
  };

  static String translate(String mistakeKey) {
    return vi[mistakeKey] ?? mistakeKey;
  }
}
