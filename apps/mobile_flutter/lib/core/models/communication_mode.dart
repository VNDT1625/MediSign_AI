import 'dart:ui';

/// Communication methods available in MediSign AI.
/// Users can select ONE or MORE methods during onboarding.
/// The app adapts its entire UI based on the selected combination.
enum CommunicationMethod {
  /// 🎤 Voice — speak to interact. Best for: blind, low-vision, elderly.
  voice,

  /// 🤟 Sign Language — use VSL hand signs via front camera.
  /// Best for: deaf, mute, deaf+mute.
  sign,

  /// 👆 Tap/Icon — tap icons and pictograms on screen.
  /// Best for: illiterate, deaf+mute+illiterate, elderly.
  tap,

  /// ⌨️ Text — type text via keyboard.
  /// Best for: standard users with full literacy.
  text,
}

/// Extension to provide display info for each method.
extension CommunicationMethodX on CommunicationMethod {
  String get icon {
    switch (this) {
      case CommunicationMethod.voice:
        return '🎤';
      case CommunicationMethod.sign:
        return '🤟';
      case CommunicationMethod.tap:
        return '👆';
      case CommunicationMethod.text:
        return '⌨️';
    }
  }

  String get label {
    switch (this) {
      case CommunicationMethod.voice:
        return 'Nói';
      case CommunicationMethod.sign:
        return 'Ký hiệu';
      case CommunicationMethod.tap:
        return 'Chạm';
      case CommunicationMethod.text:
        return 'Gõ chữ';
    }
  }

  String get description {
    switch (this) {
      case CommunicationMethod.voice:
        return 'Nói chuyện bằng giọng nói';
      case CommunicationMethod.sign:
        return 'Dùng ngôn ngữ ký hiệu';
      case CommunicationMethod.tap:
        return 'Chạm icon trên màn hình';
      case CommunicationMethod.text:
        return 'Gõ chữ bằng bàn phím';
    }
  }
}

/// Represents the body region a user can select on the body map.
enum BodyRegion {
  head,
  throat,
  chestLeft,
  chestRight,
  stomach,
  abdomenLeft,
  abdomenRight,
  leftArm,
  rightArm,
  leftLeg,
  rightLeg,
  back,
  lowerBack,
}

extension BodyRegionX on BodyRegion {
  String get label {
    switch (this) {
      case BodyRegion.head:
        return 'Đầu';
      case BodyRegion.throat:
        return 'Cổ / Họng';
      case BodyRegion.chestLeft:
        return 'Ngực trái';
      case BodyRegion.chestRight:
        return 'Ngực phải';
      case BodyRegion.stomach:
        return 'Dạ dày';
      case BodyRegion.abdomenLeft:
        return 'Bụng trái';
      case BodyRegion.abdomenRight:
        return 'Bụng phải';
      case BodyRegion.leftArm:
        return 'Tay trái';
      case BodyRegion.rightArm:
        return 'Tay phải';
      case BodyRegion.leftLeg:
        return 'Chân trái';
      case BodyRegion.rightLeg:
        return 'Chân phải';
      case BodyRegion.back:
        return 'Lưng trên';
      case BodyRegion.lowerBack:
        return 'Lưng dưới';
    }
  }

  String get emoji {
    switch (this) {
      case BodyRegion.head:
        return '🤕';
      case BodyRegion.throat:
        return '🤒';
      case BodyRegion.chestLeft:
      case BodyRegion.chestRight:
        return '💗';
      case BodyRegion.stomach:
        return '🤢';
      case BodyRegion.abdomenLeft:
      case BodyRegion.abdomenRight:
        return '😣';
      case BodyRegion.leftArm:
      case BodyRegion.rightArm:
        return '💪';
      case BodyRegion.leftLeg:
      case BodyRegion.rightLeg:
        return '🦵';
      case BodyRegion.back:
      case BodyRegion.lowerBack:
        return '🔙';
    }
  }
}

/// Symptom categories with icon-first design.
/// Each symptom can be understood WITHOUT reading text.
enum SymptomIcon {
  fever,
  headache,
  cough,
  sorethroat,
  nausea,
  vomiting,
  diarrhea,
  dizzy,
  fatigue,
  rash,
  breathless,
  chestPain,
  bleeding,
  swelling,
  insomnia,
  anxiety,
}

extension SymptomIconX on SymptomIcon {
  String get emoji {
    switch (this) {
      case SymptomIcon.fever:
        return '🌡️';
      case SymptomIcon.headache:
        return '🤕';
      case SymptomIcon.cough:
        return '😷';
      case SymptomIcon.sorethroat:
        return '🤒';
      case SymptomIcon.nausea:
        return '🤢';
      case SymptomIcon.vomiting:
        return '🤮';
      case SymptomIcon.diarrhea:
        return '🚽';
      case SymptomIcon.dizzy:
        return '😵';
      case SymptomIcon.fatigue:
        return '😴';
      case SymptomIcon.rash:
        return '🔴';
      case SymptomIcon.breathless:
        return '😤';
      case SymptomIcon.chestPain:
        return '💔';
      case SymptomIcon.bleeding:
        return '🩸';
      case SymptomIcon.swelling:
        return '🫧';
      case SymptomIcon.insomnia:
        return '🌙';
      case SymptomIcon.anxiety:
        return '😰';
    }
  }

  String get label {
    switch (this) {
      case SymptomIcon.fever:
        return 'Sốt';
      case SymptomIcon.headache:
        return 'Đau đầu';
      case SymptomIcon.cough:
        return 'Ho';
      case SymptomIcon.sorethroat:
        return 'Đau họng';
      case SymptomIcon.nausea:
        return 'Buồn nôn';
      case SymptomIcon.vomiting:
        return 'Nôn';
      case SymptomIcon.diarrhea:
        return 'Tiêu chảy';
      case SymptomIcon.dizzy:
        return 'Chóng mặt';
      case SymptomIcon.fatigue:
        return 'Mệt mỏi';
      case SymptomIcon.rash:
        return 'Phát ban';
      case SymptomIcon.breathless:
        return 'Khó thở';
      case SymptomIcon.chestPain:
        return 'Đau ngực';
      case SymptomIcon.bleeding:
        return 'Chảy máu';
      case SymptomIcon.swelling:
        return 'Sưng';
      case SymptomIcon.insomnia:
        return 'Mất ngủ';
      case SymptomIcon.anxiety:
        return 'Lo lắng';
    }
  }
}

/// Severity level — expressed as emoji faces (no text needed).
enum Severity {
  mild,
  moderate,
  severe,
  critical,
}

extension SeverityX on Severity {
  String get emoji {
    switch (this) {
      case Severity.mild:
        return '😊';
      case Severity.moderate:
        return '😟';
      case Severity.severe:
        return '😣';
      case Severity.critical:
        return '😭';
    }
  }

  String get label {
    switch (this) {
      case Severity.mild:
        return 'Nhẹ';
      case Severity.moderate:
        return 'Vừa';
      case Severity.severe:
        return 'Nặng';
      case Severity.critical:
        return 'Rất nặng';
    }
  }

  Color get color {
    switch (this) {
      case Severity.mild:
        return const Color(0xFF22C55E);
      case Severity.moderate:
        return const Color(0xFFF59E0B);
      case Severity.severe:
        return const Color(0xFFEF4444);
      case Severity.critical:
        return const Color(0xFF991B1B);
    }
  }
}

/// Duration of symptoms — expressed with icon cards.
enum SymptomDuration {
  today,
  twoDays,
  oneWeek,
  moreThanWeek,
}

extension SymptomDurationX on SymptomDuration {
  String get emoji {
    switch (this) {
      case SymptomDuration.today:
        return '📅';
      case SymptomDuration.twoDays:
        return '📆';
      case SymptomDuration.oneWeek:
        return '🗓️';
      case SymptomDuration.moreThanWeek:
        return '📋';
    }
  }

  String get label {
    switch (this) {
      case SymptomDuration.today:
        return 'Hôm nay';
      case SymptomDuration.twoDays:
        return '2–3 ngày';
      case SymptomDuration.oneWeek:
        return '~1 tuần';
      case SymptomDuration.moreThanWeek:
        return '> 1 tuần';
    }
  }

  String get visualLabel {
    switch (this) {
      case SymptomDuration.today:
        return '1';
      case SymptomDuration.twoDays:
        return '2-3';
      case SymptomDuration.oneWeek:
        return '7';
      case SymptomDuration.moreThanWeek:
        return '7+';
    }
  }
}

/// Triage level returned by AI — traffic light system.
enum TriageLevel {
  green,
  yellow,
  red,
}

extension TriageLevelX on TriageLevel {
  String get emoji {
    switch (this) {
      case TriageLevel.green:
        return '🟢';
      case TriageLevel.yellow:
        return '🟡';
      case TriageLevel.red:
        return '🔴';
    }
  }

  String get label {
    switch (this) {
      case TriageLevel.green:
        return 'Nhẹ — Tự xử lý';
      case TriageLevel.yellow:
        return 'Trung bình — Nên đi khám';
      case TriageLevel.red:
        return 'Khẩn cấp — Đi viện ngay';
    }
  }

  Color get color {
    switch (this) {
      case TriageLevel.green:
        return const Color(0xFF22C55E);
      case TriageLevel.yellow:
        return const Color(0xFFF59E0B);
      case TriageLevel.red:
        return const Color(0xFFEF4444);
    }
  }

  String get actionIcon {
    switch (this) {
      case TriageLevel.green:
        return '🏠';
      case TriageLevel.yellow:
        return '🏥';
      case TriageLevel.red:
        return '🚑';
    }
  }

  String get actionLabel {
    switch (this) {
      case TriageLevel.green:
        return 'Nghỉ ngơi tại nhà';
      case TriageLevel.yellow:
        return 'Tìm bệnh viện gần nhất';
      case TriageLevel.red:
        return 'Gọi 115 NGAY';
    }
  }
}
