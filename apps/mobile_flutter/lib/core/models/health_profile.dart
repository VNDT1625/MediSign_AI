import 'communication_mode.dart';
import 'consult_mode.dart';

/// Gender options for health profile.
enum Gender { male, female, other }

extension GenderX on Gender {
  String get label {
    switch (this) {
      case Gender.male:
        return 'Nam';
      case Gender.female:
        return 'Nữ';
      case Gender.other:
        return 'Khác';
    }
  }

  String get emoji {
    switch (this) {
      case Gender.male:
        return '👨';
      case Gender.female:
        return '👩';
      case Gender.other:
        return '🧑';
    }
  }
}

/// Difficulty/disability categories for accessibility adaptation.
enum Difficulty {
  vision,
  hearing,
  speech,
  mobility,
  cognitive,
  none,
}

extension DifficultyX on Difficulty {
  String get label {
    switch (this) {
      case Difficulty.vision:
        return 'Thị giác';
      case Difficulty.hearing:
        return 'Thính giác';
      case Difficulty.speech:
        return 'Ngôn ngữ / Nói';
      case Difficulty.mobility:
        return 'Vận động';
      case Difficulty.cognitive:
        return 'Nhận thức / Trí nhớ';
      case Difficulty.none:
        return 'Không có';
    }
  }

  String get emoji {
    switch (this) {
      case Difficulty.vision:
        return '👁️';
      case Difficulty.hearing:
        return '👂';
      case Difficulty.speech:
        return '🗣️';
      case Difficulty.mobility:
        return '🦽';
      case Difficulty.cognitive:
        return '🧠';
      case Difficulty.none:
        return '✅';
    }
  }
}

/// Common pre-existing conditions.
enum PreCondition {
  diabetes,
  hypertension,
  heartDisease,
  asthma,
  kidney,
  liver,
  cancer,
  hiv,
  none,
}

extension PreConditionX on PreCondition {
  String get label {
    switch (this) {
      case PreCondition.diabetes:
        return 'Tiểu đường';
      case PreCondition.hypertension:
        return 'Cao huyết áp';
      case PreCondition.heartDisease:
        return 'Bệnh tim';
      case PreCondition.asthma:
        return 'Hen suyễn';
      case PreCondition.kidney:
        return 'Bệnh thận';
      case PreCondition.liver:
        return 'Bệnh gan';
      case PreCondition.cancer:
        return 'Ung thư';
      case PreCondition.hiv:
        return 'HIV/AIDS';
      case PreCondition.none:
        return 'Không có';
    }
  }

  String get emoji {
    switch (this) {
      case PreCondition.diabetes:
        return '🩸';
      case PreCondition.hypertension:
        return '💓';
      case PreCondition.heartDisease:
        return '❤️‍🩹';
      case PreCondition.asthma:
        return '🫁';
      case PreCondition.kidney:
        return '🫘';
      case PreCondition.liver:
        return '🟤';
      case PreCondition.cancer:
        return '🎗️';
      case PreCondition.hiv:
        return '🔬';
      case PreCondition.none:
        return '✅';
    }
  }
}

/// Health profile collected during onboarding survey (7 steps).
class HealthProfile {
  final int? age;
  final Gender? gender;
  final List<String> drugAllergies;
  final Set<PreCondition> preConditions;
  final Set<Difficulty> difficulties;
  final ConsultMode consultMode;
  final Set<CommunicationMethod> communicationMethods;

  const HealthProfile({
    this.age,
    this.gender,
    this.drugAllergies = const [],
    this.preConditions = const {},
    this.difficulties = const {},
    this.consultMode = ConsultMode.hybrid,
    this.communicationMethods = const {CommunicationMethod.tap},
  });

  HealthProfile copyWith({
    int? age,
    Gender? gender,
    List<String>? drugAllergies,
    Set<PreCondition>? preConditions,
    Set<Difficulty>? difficulties,
    ConsultMode? consultMode,
    Set<CommunicationMethod>? communicationMethods,
  }) {
    return HealthProfile(
      age: age ?? this.age,
      gender: gender ?? this.gender,
      drugAllergies: drugAllergies ?? this.drugAllergies,
      preConditions: preConditions ?? this.preConditions,
      difficulties: difficulties ?? this.difficulties,
      consultMode: consultMode ?? this.consultMode,
      communicationMethods: communicationMethods ?? this.communicationMethods,
    );
  }
}
