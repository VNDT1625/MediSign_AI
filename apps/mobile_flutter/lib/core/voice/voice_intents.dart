/// Intent matcher cho voice command tren Flutter app (mobile + desktop).
/// KHONG goi AI. Tat ca lenh duoc parse local theo regex/keyword tieng Viet.
library;

enum VoiceIntentKind {
  navigateTab,
  scroll,
  back,
  openScan,        // mo trang scan thuoc
  openSettings,    // mo trang cai dat
  authLogin,
  authLogout,
  chatMode,
  elderlyToggle,
  fontSize,
  uiSubmit,
  uiDictate,
  uiClear,
  readPage,
  repeat,
  help,
  close,
  stop,
  unknown,
}

enum HomeTab { home, chat, medicine, soulGarden, profile }
enum VoiceScrollAction { up, down, top, bottom }
enum VoiceChatMode { text, voice, click, sign }
enum VoiceFontDir { increase, decrease, reset }

class VoiceIntent {
  const VoiceIntent({
    required this.kind,
    required this.reply,
    required this.normalized,
    this.tab,
    this.scrollAction,
    this.chatMode,
    this.fontDir,
    this.text,
    this.label,
  });

  final VoiceIntentKind kind;
  final String reply;
  final String normalized;
  final HomeTab? tab;
  final VoiceScrollAction? scrollAction;
  final VoiceChatMode? chatMode;
  final VoiceFontDir? fontDir;
  final String? text;
  final String? label;
}

String normalizeText(String text) {
  const map = {
    'a': 'àáảãạăằắẳẵặâầấẩẫậ',
    'e': 'èéẻẽẹêềếểễệ',
    'i': 'ìíỉĩị',
    'o': 'òóỏõọôồốổỗộơờớởỡợ',
    'u': 'ùúủũụưừứửữự',
    'y': 'ỳýỷỹỵ',
    'd': 'đ',
  };
  var s = text.toLowerCase();
  map.forEach((base, accents) {
    for (final ch in accents.split('')) {
      s = s.replaceAll(ch, base);
    }
  });
  s = s.replaceAll(RegExp(r'[^a-z0-9\s]'), ' ');
  s = s.replaceAll(RegExp(r'\s+'), ' ').trim();
  return s;
}

const List<String> kWakeWords = [
  'bac si oi',
  'bac sy oi',
  'bacsi oi',
  'bac si',
];

bool containsWakeWord(String transcript) {
  final n = normalizeText(transcript);
  return kWakeWords.any((w) => n.contains(w));
}

String stripWakeWord(String transcript) {
  final n = normalizeText(transcript);
  for (final w in kWakeWords) {
    final i = n.indexOf(w);
    if (i >= 0) return n.substring(i + w.length).trim();
  }
  return n;
}

const _kTabKeys = <HomeTab, List<String>>{
  HomeTab.home: ['trang chu', 'home', 'man hinh chinh', 'dashboard'],
  HomeTab.chat: ['chat', 'tro chuyen', 'hoi bac si', 'tu van', 'bac si ai'],
  HomeTab.medicine: ['tu thuoc', 'thuoc', 'medicine', 'don thuoc', 'kho thuoc'],
  HomeTab.soulGarden: ['soul garden', 'vuon tinh than', 'vuon', 'thien', 'thu gian'],
  HomeTab.profile: ['ho so', 'profile', 'tai khoan', 'ca nhan'],
};

VoiceIntent matchIntent(String rawTranscript) {
  final n = normalizeText(rawTranscript);
  final original = rawTranscript.trim();

  if (n.isEmpty) {
    return VoiceIntent(
      kind: VoiceIntentKind.unknown,
      reply: 'Mình chưa nghe rõ, bạn nói lại giúp nhé.',
      normalized: n,
    );
  }

  if (RegExp(r'(dung lai|dung nghe|tat mic|stop)').hasMatch(n)) {
    return VoiceIntent(
      kind: VoiceIntentKind.stop,
      reply: 'Đã dừng nghe.',
      normalized: n,
    );
  }
  if (RegExp(r'(^|\s)(dong|tat overlay|huy bo)(\s|$)').hasMatch(n)) {
    return VoiceIntent(
      kind: VoiceIntentKind.close,
      reply: 'Đã đóng trợ lý giọng nói.',
      normalized: n,
    );
  }
  if (RegExp(r'(giup|tro giup|huong dan|lam gi duoc|menu lenh)').hasMatch(n)) {
    return VoiceIntent(
      kind: VoiceIntentKind.help,
      reply:
          'Bạn có thể nói: "mở chat", "mở tủ thuốc", "quét thuốc", '
          '"cài đặt", "đăng xuất", "cuộn xuống", "viết là <nội dung>", '
          '"gửi", "đọc trang", hoặc "nói lại".',
      normalized: n,
    );
  }

  if (RegExp(r'(noi lai|doc lai|nhac lai|repeat)').hasMatch(n)) {
    return VoiceIntent(
      kind: VoiceIntentKind.repeat,
      reply: '',
      normalized: n,
    );
  }
  if (RegExp(r'(doc trang|doc giup|doc noi dung trang)').hasMatch(n)) {
    return VoiceIntent(
      kind: VoiceIntentKind.readPage,
      reply: 'Mình đọc nội dung trang.',
      normalized: n,
    );
  }

  if (RegExp(r'(quet thuoc|chup thuoc|scan thuoc|mo may anh)').hasMatch(n)) {
    return VoiceIntent(
      kind: VoiceIntentKind.openScan,
      reply: 'Đang mở quét thuốc.',
      normalized: n,
    );
  }
  if (RegExp(r'(cai dat|cai|setting|tuy chinh)').hasMatch(n)) {
    return VoiceIntent(
      kind: VoiceIntentKind.openSettings,
      reply: 'Đang mở cài đặt.',
      normalized: n,
    );
  }

  if (RegExp(r'(dang nhap|login|sign in)').hasMatch(n)) {
    return VoiceIntent(
      kind: VoiceIntentKind.authLogin,
      reply: 'Đang mở đăng nhập.',
      normalized: n,
    );
  }
  if (RegExp(r'(dang xuat|logout|sign out|thoat tai khoan)').hasMatch(n)) {
    return VoiceIntent(
      kind: VoiceIntentKind.authLogout,
      reply: 'Đang đăng xuất.',
      normalized: n,
    );
  }

  final modeMatch = RegExp(
          r'che do (van ban|text|giong noi|voice|am thanh|chon|click|tap|ngon ngu ky hieu|ky hieu|sign)')
      .firstMatch(n);
  if (modeMatch != null) {
    final m = modeMatch.group(1)!;
    final mode = RegExp(r'text|van ban').hasMatch(m)
        ? VoiceChatMode.text
        : RegExp(r'voice|giong|am thanh').hasMatch(m)
            ? VoiceChatMode.voice
            : RegExp(r'click|chon|tap').hasMatch(m)
                ? VoiceChatMode.click
                : VoiceChatMode.sign;
    final replyMap = {
      VoiceChatMode.text: 'Đã chuyển sang chế độ văn bản.',
      VoiceChatMode.voice: 'Đã chuyển sang chế độ giọng nói.',
      VoiceChatMode.click: 'Đã chuyển sang chế độ chọn nhanh.',
      VoiceChatMode.sign: 'Đã chuyển sang chế độ ngôn ngữ ký hiệu.',
    };
    return VoiceIntent(
      kind: VoiceIntentKind.chatMode,
      chatMode: mode,
      reply: replyMap[mode]!,
      normalized: n,
    );
  }

  if (RegExp(r'(che do nguoi (cao tuoi|gia)|elderly|chu to|man hinh lon)').hasMatch(n)) {
    return VoiceIntent(
      kind: VoiceIntentKind.elderlyToggle,
      reply: 'Đã chuyển chế độ thân thiện cho người cao tuổi.',
      normalized: n,
    );
  }

  if (RegExp(r'(tang co chu|chu to hon|phong to chu|to chu)').hasMatch(n)) {
    return VoiceIntent(
      kind: VoiceIntentKind.fontSize,
      fontDir: VoiceFontDir.increase,
      reply: 'Đã tăng cỡ chữ.',
      normalized: n,
    );
  }
  if (RegExp(r'(giam co chu|chu nho hon|thu nho chu|nho chu)').hasMatch(n)) {
    return VoiceIntent(
      kind: VoiceIntentKind.fontSize,
      fontDir: VoiceFontDir.decrease,
      reply: 'Đã giảm cỡ chữ.',
      normalized: n,
    );
  }
  if (RegExp(r'(co chu mac dinh|chu mac dinh|reset font)').hasMatch(n)) {
    return VoiceIntent(
      kind: VoiceIntentKind.fontSize,
      fontDir: VoiceFontDir.reset,
      reply: 'Đã đặt lại cỡ chữ mặc định.',
      normalized: n,
    );
  }

  if (RegExp(r'(quay lai|tro lai|back|thoat ra)').hasMatch(n)) {
    return VoiceIntent(
      kind: VoiceIntentKind.back,
      reply: 'Quay lại màn hình trước.',
      normalized: n,
    );
  }

  if (RegExp(r'len dau|ve dau|len tren cung').hasMatch(n)) {
    return VoiceIntent(
      kind: VoiceIntentKind.scroll,
      scrollAction: VoiceScrollAction.top,
      reply: 'Cuộn lên đầu.',
      normalized: n,
    );
  }
  if (RegExp(r'cuoi trang|xuong duoi cung|het trang').hasMatch(n)) {
    return VoiceIntent(
      kind: VoiceIntentKind.scroll,
      scrollAction: VoiceScrollAction.bottom,
      reply: 'Cuộn xuống cuối.',
      normalized: n,
    );
  }
  if (RegExp(r'cuon len|keo len|len tren').hasMatch(n)) {
    return VoiceIntent(
      kind: VoiceIntentKind.scroll,
      scrollAction: VoiceScrollAction.up,
      reply: 'Cuộn lên.',
      normalized: n,
    );
  }
  if (RegExp(r'cuon xuong|keo xuong|xuong duoi').hasMatch(n)) {
    return VoiceIntent(
      kind: VoiceIntentKind.scroll,
      scrollAction: VoiceScrollAction.down,
      reply: 'Cuộn xuống.',
      normalized: n,
    );
  }

  if (RegExp(r'(xoa noi dung|xoa o nhap|xoa input|clear)').hasMatch(n)) {
    return VoiceIntent(
      kind: VoiceIntentKind.uiClear,
      reply: 'Đã xóa nội dung ô nhập.',
      normalized: n,
    );
  }
  if (RegExp(r'^(gui|gui di|submit|enter|gui tin nhan)$').hasMatch(n)) {
    return VoiceIntent(
      kind: VoiceIntentKind.uiSubmit,
      reply: 'Đã gửi.',
      normalized: n,
    );
  }

  // Dictation: "viet la <noi dung>"
  final dictateNorm = RegExp(r'^(?:viet la|ghi la|nhap|nhap noi dung|go la|ghi rang)\s+(.+)$').firstMatch(n);
  if (dictateNorm != null) {
    final origMatch = RegExp(r'^(?:viết là|ghi là|nhập(?:\s+(?:nội dung|rằng))?|gõ là|ghi rằng)\s+(.+)$', caseSensitive: false).firstMatch(original);
    final text = (origMatch?.group(1) ?? dictateNorm.group(1)!).trim();
    final preview = text.length > 40 ? '${text.substring(0, 40)}...' : text;
    return VoiceIntent(
      kind: VoiceIntentKind.uiDictate,
      text: text,
      reply: 'Đã nhập: "$preview".',
      normalized: n,
    );
  }

  for (final entry in _kTabKeys.entries) {
    if (entry.value.any((k) => n.contains(k))) {
      final replyMap = {
        HomeTab.home: 'Đang mở trang chủ.',
        HomeTab.chat: 'Đang mở chat AI.',
        HomeTab.medicine: 'Đang mở tủ thuốc.',
        HomeTab.soulGarden: 'Đang mở Soul Garden.',
        HomeTab.profile: 'Đang mở hồ sơ.',
      };
      return VoiceIntent(
        kind: VoiceIntentKind.navigateTab,
        tab: entry.key,
        reply: replyMap[entry.key]!,
        normalized: n,
      );
    }
  }

  return VoiceIntent(
    kind: VoiceIntentKind.unknown,
    reply: 'Mình chưa hiểu lệnh đó. Nói "giúp" để xem các lệnh hỗ trợ.',
    normalized: n,
  );
}
