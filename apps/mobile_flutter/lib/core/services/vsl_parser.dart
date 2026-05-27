import 'dart:math';

/// ══════════════════════════════════════════════════════════════
/// VSL PARSER — Vietnamese Sign Language Text-to-Sign Parser
/// ══════════════════════════════════════════════════════════════
///
/// Lớp này chịu trách nhiệm dịch câu văn bản y tế từ AI y khoa thành
/// hàng đợi các từ khóa cử chỉ (Sign Tokens) để hiển thị múa ký hiệu.
/// Sử dụng phương pháp lọc Stopwords, chuẩn hóa tiếng Việt không dấu
/// và khớp mẫu từ điển thông minh theo ngữ pháp tối giản VSL.
class VslParser {
  VslParser._();

  /// Danh sách các từ khóa cử chỉ được hỗ trợ bởi hệ thống offline
  static const Map<String, String> dictionary = {
    'ban': 'ban',         // Bạn
    'bac_si': 'bac_si',   // Bác sĩ
    'uong': 'uong',       // Uống
    'thuoc': 'thuoc',     // Thuốc
    'sot': 'sot',         // Sốt
    'ho': 'ho',           // Ho
    'dau': 'dau',         // Đau
    'dau_dau': 'dau_dau', // Đau đầu
    'bung': 'bung',       // Bụng
    'kho_tho': 'kho_tho', // Khó thở
    'chong_mat': 'chong_mat', // Chóng mặt
    'khan_cap': 'khan_cap',   // Khẩn cấp
    'nghi_ngoi': 'nghi_ngoi', // Nghỉ ngơi
    'uong_nuoc': 'uong_nuoc', // Uống nước
  };

  /// Ánh xạ từ khoá không dấu sang Token ký hiệu
  static const Map<String, String> _phraseMapping = {
    'bac si': 'bac_si',
    'kham': 'bac_si',
    'uong thuoc': 'uong,thuoc',
    'don thuoc': 'thuoc',
    'thuoc': 'thuoc',
    'uong': 'uong',
    'sot': 'sot',
    'nhiet do cao': 'sot',
    'nong': 'sot',
    'ho khan': 'ho',
    'ho': 'ho',
    'dau dau': 'dau_dau',
    'nhuc dau': 'dau_dau',
    'dau bung': 'dau,bung',
    'da day': 'bung',
    'thien vi': 'bung',
    'bung': 'bung',
    'dau': 'dau',
    'kho tho': 'kho_tho',
    'ngat': 'kho_tho',
    'khong tho': 'kho_tho',
    'chong mat': 'chong_mat',
    'quay cuong': 'chong_mat',
    'xay xam': 'chong_mat',
    'khan cap': 'khan_cap',
    'cap cuu': 'khan_cap',
    '115': 'khan_cap',
    'nghi ngoi': 'nghi_ngoi',
    'nam nghi': 'nghi_ngoi',
    'thu gian': 'nghi_ngoi',
    'uong nuoc': 'uong_nuoc',
    'nhieu nuoc': 'uong_nuoc',
    'nuoc am': 'uong_nuoc',
    'ban': 'ban',
    'benh nhan': 'ban',
    'anh chi': 'ban',
  };

  /// Loại bỏ dấu tiếng Việt để so sánh chuỗi chính xác tuyệt đối
  static String removeDiacritics(String text) {
    const withDiacritics =
        'àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđÀÁẠẢÃÂẦẤẬẨẪĂẰẮẶẲẴÈÉẸẺẼÊỀẾỆỂỄÌÍỊỈĨÒÓỌỎÕÔỒỐỘỔỖƠỜỚỢỞỠÙÚỤỦŨƯỪỨỰỬỮỲÝỴỶỸĐ';
    const withoutDiacritics =
        'aaaaaaaaaaaaaaaaaeeeeeeeeeeeiiiiiooooooooooooooooouuuuuuuuuuuyyyyydAAAAAAAAAAAAAAAAAEEEEEEEEEEEIIIIIOOOOOOOOOOOOOOOOOUUUUUUUUUUUYYYYYD';

    String result = text;
    for (int i = 0; i < withDiacritics.length; i++) {
      result = result.replaceAll(withDiacritics[i], withoutDiacritics[i]);
    }
    return result.toLowerCase();
  }

  /// Dịch chuỗi văn bản y tế thành chuỗi tokens ký hiệu y khoa
  static List<String> parseText(String text) {
    if (text.isEmpty) return [];

    final String normalized = removeDiacritics(text);
    final List<_MatchInfo> matches = [];
    final Set<int> matchedIndices = {};

    // Sắp xếp các cụm từ trong mapping theo độ dài giảm dần để ưu tiên khớp từ dài trước (greedy matching)
    // Ví dụ: Ưu tiên khớp "dau dau" trước khi khớp đơn lẻ "dau"
    final List<String> phrases = _phraseMapping.keys.toList()
      ..sort((a, b) => b.length.compareTo(a.length));

    final RegExp alphanumeric = RegExp(r'[a-zA-Z0-9_]');

    bool isWordBoundary(int index, int length) {
      if (index > 0) {
        final String before = normalized[index - 1];
        if (alphanumeric.hasMatch(before)) {
          return false;
        }
      }
      if (index + length < normalized.length) {
        final String after = normalized[index + length];
        if (alphanumeric.hasMatch(after)) {
          return false;
        }
      }
      return true;
    }

    for (final phrase in phrases) {
      int startSearch = 0;
      while (true) {
        final int index = normalized.indexOf(phrase, startSearch);
        if (index == -1) break;

        final int length = phrase.length;

        // Chỉ khớp nếu đây là ranh giới từ đầy đủ (không trùng khớp bán phần, VD: 'ho' khớp trong 'khoe')
        if (isWordBoundary(index, length)) {
          // Kiểm tra xem vị trí này đã được bao phủ bởi một cụm từ khớp dài hơn trước đó chưa
          bool alreadyMatched = false;
          for (int i = index; i < index + length; i++) {
            if (matchedIndices.contains(i)) {
              alreadyMatched = true;
              break;
            }
          }

          if (!alreadyMatched) {
            // Thêm các vị trí này vào tập hợp đã khớp
            for (int i = index; i < index + length; i++) {
              matchedIndices.add(i);
            }

            final String targetTokens = _phraseMapping[phrase]!;
            final List<String> phraseTokens = targetTokens.contains(',')
                ? targetTokens.split(',')
                : [targetTokens];

            matches.add(_MatchInfo(index, index + length, phraseTokens));
          }
        }

        startSearch = index + 1;
      }
    }

    // Sắp xếp các cụm khớp theo vị trí xuất hiện ban đầu trong câu để giữ nguyên thứ tự ngữ nghĩa tự nhiên
    matches.sort((a, b) => a.start.compareTo(b.start));

    // Thu thập tất cả các tokens theo thứ tự xuất hiện
    final List<String> matchedTokens = [];
    for (final match in matches) {
      matchedTokens.addAll(match.tokens);
    }

    // Tối ưu hóa chuỗi tokens: Loại bỏ trùng lặp liên tục để tránh lặp lại ký hiệu vô ích
    // VD: ["ban", "dau", "dau", "sot"] -> ["ban", "dau", "sot"]
    final List<String> optimizedTokens = [];
    for (final token in matchedTokens) {
      if (optimizedTokens.isEmpty || optimizedTokens.last != token) {
        optimizedTokens.add(token);
      }
    }

    // Đảm bảo có ít nhất từ khóa 'ban' hoặc cử chỉ thông thường nếu rỗng để không bị đứng màn hình
    if (optimizedTokens.isEmpty) {
      if (normalized.contains('khan') || normalized.contains('cap')) {
        return ['khan_cap'];
      }
      return ['ban', 'bac_si'];
    }

    return optimizedTokens;
  }
}

/// Helper class to represent a match interval with its mapped VSL tokens
class _MatchInfo {
  final int start;
  final int end;
  final List<String> tokens;

  _MatchInfo(this.start, this.end, this.tokens);
}
