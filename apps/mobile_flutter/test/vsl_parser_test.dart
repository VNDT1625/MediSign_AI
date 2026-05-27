import 'package:flutter_test/flutter_test.dart';
import 'package:medisign_mobile/core/services/vsl_parser.dart';

void main() {
  group('VSL Parser NLP Tests', () {
    test('Should remove Vietnamese diacritics and lowercase text', () {
      final input = 'Bác Sĩ khuyên Bạn hãy Uống Thuốc vào buổi Sáng!';
      final expected = 'bac si khuyen ban hay uong thuoc vao buoi sang!';
      expect(VslParser.removeDiacritics(input), expected);
    });

    test('Should parse simple medical phrases into sign tokens', () {
      final text = 'Bác sĩ đang khám bệnh';
      final tokens = VslParser.parseText(text);
      expect(tokens, contains('bac_si'));
    });

    test('Should parse complex sentences and maintain semantic order', () {
      final text = 'Bạn cần uống thuốc giảm đau và nghỉ ngơi nhiều';
      final tokens = VslParser.parseText(text);
      
      // Expected tokens sequence in order:
      // - "Bạn" -> 'ban'
      // - "uống thuốc" -> 'uong', 'thuoc'
      // - "đau" -> 'dau'
      // - "nghỉ ngơi" -> 'nghi_ngoi'
      expect(tokens, containsAllInOrder(['ban', 'uong', 'thuoc', 'dau', 'nghi_ngoi']));
    });

    test('Should handle compound medical symptoms properly', () {
      final text = 'Bệnh nhân bị đau bụng dữ dội và sốt cao kèm ho khan';
      final tokens = VslParser.parseText(text);
      
      expect(tokens, containsAllInOrder(['ban', 'dau', 'bung', 'sot', 'ho']));
    });

    test('Should remove consecutive duplicate tokens', () {
      final text = 'Bạn bị đau đầu nhức đầu nhiều';
      final tokens = VslParser.parseText(text);
      
      // "đau đầu nhức đầu" maps to 'dau_dau', 'dau_dau'. Parser should deduplicate it.
      expect(tokens, containsAllInOrder(['ban', 'dau_dau']));
      expect(tokens.where((t) => t == 'dau_dau').length, equals(1));
    });

    test('Should fallback gracefully to standard greetings/doctors when no match found', () {
      final text = 'Xin chào tôi khỏe mạnh';
      final tokens = VslParser.parseText(text);
      
      expect(tokens, containsAllInOrder(['ban', 'bac_si']));
    });

    test('Should fallback to emergency gesture if critical keywords detected', () {
      final text = 'Gọi cấp cứu 115 ngay lập tức!';
      final tokens = VslParser.parseText(text);
      
      expect(tokens, contains('khan_cap'));
    });
  });
}
