import 'soul_garden_service.dart';
import 'memory_recall_service.dart';

/// Comfort AI Service - AI an ui thong minh dua tren Soul Garden
/// Khi user buon, AI se tim trong nhat ky nhung khoanh khac vui de an ui
class ComfortAIService {
  ComfortAIService._();
  static final instance = ComfortAIService._();

  final SoulGardenService _soulGarden = SoulGardenService.instance;
  // ignore: unused_field
  final MemoryRecallService _memoryRecall = MemoryRecallService.instance;

  /// Lay comforting message dua tren context hien tai
  String getComfortingMessage({String? userMessage}) {
    // 1. Neu user chia se dien gi do
    if (userMessage != null) {
      return _generateContextualComfort(userMessage);
    }

    // 2. Lay message dua tren mood stats
    return _soulGarden.getComfortingMessage();
  }

  /// Tao comforting message dua tren noi dung user chia se
  String _generateContextualComfort(String userMessage) {
    final messageLower = userMessage.toLowerCase();

    // Phat hien loai van de
    if (messageLower.contains('buon') || messageLower.contains('chan')) {
      return _comfortSad();
    }
    if (messageLower.contains('stress') || messageLower.contains('cang')) {
      return _comfortStressed();
    }
    if (messageLower.contains('met') || messageLower.contains('kiet')) {
      return _comfortTired();
    }
    if (messageLower.contains('lo') || messageLower.contains('lo lang')) {
      return _comfortAnxious();
    }
    if (messageLower.contains('co don') || messageLower.contains('mot minh')) {
      return _comfortLonely();
    }
    if (messageLower.contains('tuc gian') || messageLower.contains('buc')) {
      return _comfortAngry();
    }

    // Mac dinh
    return _soulGarden.getComfortingMessage();
  }

  /// An ui khi buon
  String _comfortSad() {
    final positives = _soulGarden.getPositiveMemories(limit: 3);
    final grateful = _soulGarden.getGratefulMemories(limit: 2);

    if (positives.isNotEmpty) {
      final memory = positives.first;
      return 'Toi hieu ban dang buon... Nhung hay nho lai khoanh khac nay: "${memory.content}". Moi ngay deu co nhung dieu tich cuc dang cho doi.';
    }

    if (grateful.isNotEmpty) {
      return 'Toi hieu... Hay cung nhau nhin lai dieu biet on: "${grateful.first.content}".';
    }

    return 'Toi o day voi ban. Ke cho toi nghe dieu gi khien ban buon duoc khong?';
  }

  /// An ui khi stress
  String _comfortStressed() {
    return 'Toi biet ban dang cang mong... Hay thu hit thon sau 3 lan, di bo 5 phut ngoai troi. Moi chuyen roi se qua thoi.';
  }

  /// An ui khi met
  String _comfortTired() {
    return 'Ban dang met moi... Hay nghi giai mot chut, uong du nuoc, ngu du giac. Hay cham soc ban than nhe!';
  }

  /// An ui khi lo lang
  String _comfortAnxious() {
    return 'Toi hieu ban dang lo lang... Hay viet ra nhung gi ban lo lang, tap trung vao hoi tho. Ban muon chia se dien gi?';
  }

  /// An ui khi co don
  String _comfortLonely() {
    final family = _soulGarden.getFamilyMemories(limit: 2);
    if (family.isNotEmpty) {
      return 'Ban dang cam thay co don... Hay nho lai khoanh khac ben nguoi than: "${family.first.content}". Hay lien he voi ho nhe!';
    }
    return 'Toi hieu cam giac co don... Hay goi dien cho nguoi than hoac tham gia hoat dong cong dong. Ban khong co don dau!';
  }

  /// An ui khi tuc gian
  String _comfortAngry() {
    return 'Toi hieu ban dang tuc gian... Khi tuc gian, hay thu hit thon sau, dem den 10, di bo mot vong. Roi moi thu se on thoi.';
  }

  /// Tao prompt cho AI de tich hop vao consult flow
  String getComfortingPromptContext() {
    final buffer = StringBuffer();
    final stats = _soulGarden.statsForDays(7);
    buffer.writeln('## User Mood Context');
    buffer
        .writeln('- Average mood: ${stats.averageScore.toStringAsFixed(1)}/5');

    final positives = _soulGarden.getPositiveMemories(days: 30, limit: 3);
    if (positives.isNotEmpty) {
      buffer.writeln('\n## Positive Memories');
      for (final p in positives) {
        buffer.writeln('- ${p.date.day}/${p.date.month}: ${p.content}');
      }
    }

    return buffer.toString();
  }

  /// Kiem tra xem co can chuyen sang chuyen gia khong
  bool shouldRecommendProfessional() {
    final stats = _soulGarden.statsForDays(14);
    final negStreak = _soulGarden.negativeStreak;

    if (stats.averageScore < 1.5 && stats.totalEntries >= 7) {
      return true;
    }
    if (negStreak >= 7) {
      return true;
    }
    return false;
  }

  /// Lay loi khuyen chuyen gia
  String getProfessionalRecommendation() {
    return 'Toi lo lang cho ban. Qua nhat ky, toi thay ban dang trai qua giai doan kho khan. Toi khuyen ban nen noi chuyen voi chuyen gia tam ly hoac goi dien cho nguoi than. Ban co muon toi giup dat lich hen khong?';
  }
}
