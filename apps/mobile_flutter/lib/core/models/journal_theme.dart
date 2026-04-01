import 'dart:ui';

/// Background configuration for a journal theme.
class JournalBackground {
  final List<Color> colors;
  final String? imageAsset;

  const JournalBackground({
    required this.colors,
    this.imageAsset,
  });
}

/// Card style configuration for a journal theme.
class JournalCardStyle {
  final Color backgroundColor;
  final Color borderColor;
  final double borderRadius;
  final double opacity;

  const JournalCardStyle({
    required this.backgroundColor,
    required this.borderColor,
    this.borderRadius = 16.0,
    this.opacity = 0.9,
  });
}

/// Text style configuration for a journal theme.
class JournalTextStyle {
  final Color titleColor;
  final Color bodyColor;
  final Color hintColor;
  final String? fontFamily;

  const JournalTextStyle({
    required this.titleColor,
    required this.bodyColor,
    required this.hintColor,
    this.fontFamily,
  });
}

/// A journal theme definition.
class JournalTheme {
  final String id;
  final String name;
  final String emoji;
  final String description;
  final JournalBackground background;
  final JournalCardStyle cardStyle;
  final JournalTextStyle textStyle;
  final bool isUnlocked;
  final bool isDownloadable;
  final String? downloadUrl;
  final String? unlockRequirement;

  const JournalTheme({
    required this.id,
    required this.name,
    required this.emoji,
    required this.description,
    required this.background,
    required this.cardStyle,
    required this.textStyle,
    this.isUnlocked = false,
    this.isDownloadable = false,
    this.downloadUrl,
    this.unlockRequirement,
  });

  JournalTheme copyWith({
    String? id,
    String? name,
    String? emoji,
    String? description,
    JournalBackground? background,
    JournalCardStyle? cardStyle,
    JournalTextStyle? textStyle,
    bool? isUnlocked,
    bool? isDownloadable,
    String? downloadUrl,
    String? unlockRequirement,
  }) {
    return JournalTheme(
      id: id ?? this.id,
      name: name ?? this.name,
      emoji: emoji ?? this.emoji,
      description: description ?? this.description,
      background: background ?? this.background,
      cardStyle: cardStyle ?? this.cardStyle,
      textStyle: textStyle ?? this.textStyle,
      isUnlocked: isUnlocked ?? this.isUnlocked,
      isDownloadable: isDownloadable ?? this.isDownloadable,
      downloadUrl: downloadUrl ?? this.downloadUrl,
      unlockRequirement: unlockRequirement ?? this.unlockRequirement,
    );
  }
}

/// Predefined journal themes.
class JournalThemes {
  JournalThemes._();

  static const glassmorphism = JournalTheme(
    id: 'glass',
    name: 'Glassmorphism',
    emoji: '🪟',
    description: 'Giao diện kính mờ hiện đại',
    background: JournalBackground(
        colors: [Color(0xFF1B4332), Color(0xFF2D6A4F), Color(0xFF40916C)]),
    cardStyle: JournalCardStyle(
      backgroundColor: Color(0x33FFFFFF),
      borderColor: Color(0x55FFFFFF),
      borderRadius: 20.0,
      opacity: 0.15,
    ),
    textStyle: JournalTextStyle(
      titleColor: Color(0xFFFFFFFF),
      bodyColor: Color(0xCCFFFFFF),
      hintColor: Color(0x88FFFFFF),
    ),
    isUnlocked: true,
    unlockRequirement: 'Mặc định',
  );

  static const paper = JournalTheme(
    id: 'paper',
    name: 'Giấy cổ điển',
    emoji: '📜',
    description: 'Phong cách giấy viết tay',
    background:
        JournalBackground(colors: [Color(0xFFF5F0E1), Color(0xFFE8DCC8)]),
    cardStyle: JournalCardStyle(
      backgroundColor: Color(0xFFFFFDF5),
      borderColor: Color(0xFFD4C5A9),
      borderRadius: 8.0,
      opacity: 1.0,
    ),
    textStyle: JournalTextStyle(
      titleColor: Color(0xFF3E2723),
      bodyColor: Color(0xFF4E342E),
      hintColor: Color(0xFF8D6E63),
      fontFamily: 'serif',
    ),
    unlockRequirement: 'Viết 3 bài nhật ký',
  );

  static const notebook = JournalTheme(
    id: 'notebook',
    name: 'Sổ tay',
    emoji: '📓',
    description: 'Phong cách sổ tay kẻ dòng',
    background:
        JournalBackground(colors: [Color(0xFFE3F2FD), Color(0xFFBBDEFB)]),
    cardStyle: JournalCardStyle(
      backgroundColor: Color(0xFFFFFFFF),
      borderColor: Color(0xFF90CAF9),
      borderRadius: 4.0,
      opacity: 1.0,
    ),
    textStyle: JournalTextStyle(
      titleColor: Color(0xFF1565C0),
      bodyColor: Color(0xFF212121),
      hintColor: Color(0xFF9E9E9E),
    ),
    unlockRequirement: 'Viết 7 bài nhật ký',
  );

  static const floral = JournalTheme(
    id: 'floral',
    name: 'Hoa lá',
    emoji: '🌺',
    description: 'Hoa văn thiên nhiên nhẹ nhàng',
    background: JournalBackground(
        colors: [Color(0xFFFCE4EC), Color(0xFFF8BBD0), Color(0xFFF48FB1)]),
    cardStyle: JournalCardStyle(
      backgroundColor: Color(0xE6FFFFFF),
      borderColor: Color(0xFFF48FB1),
      borderRadius: 16.0,
      opacity: 0.9,
    ),
    textStyle: JournalTextStyle(
      titleColor: Color(0xFFC2185B),
      bodyColor: Color(0xFF880E4F),
      hintColor: Color(0xFFE91E63),
    ),
    unlockRequirement: 'Streak 3 ngày',
  );

  static const cute = JournalTheme(
    id: 'cute',
    name: 'Dễ thương',
    emoji: '🧸',
    description: 'Phong cách kawaii dễ thương',
    background:
        JournalBackground(colors: [Color(0xFFFFF3E0), Color(0xFFFFE0B2)]),
    cardStyle: JournalCardStyle(
      backgroundColor: Color(0xFFFFF8E1),
      borderColor: Color(0xFFFFCC80),
      borderRadius: 24.0,
      opacity: 1.0,
    ),
    textStyle: JournalTextStyle(
      titleColor: Color(0xFFE65100),
      bodyColor: Color(0xFF4E342E),
      hintColor: Color(0xFFBCAAA4),
    ),
    unlockRequirement: 'Streak 7 ngày',
  );

  static const polaroid = JournalTheme(
    id: 'polaroid',
    name: 'Polaroid',
    emoji: '📸',
    description: 'Phong cách ảnh polaroid',
    background:
        JournalBackground(colors: [Color(0xFF263238), Color(0xFF37474F)]),
    cardStyle: JournalCardStyle(
      backgroundColor: Color(0xFFFAFAFA),
      borderColor: Color(0xFFE0E0E0),
      borderRadius: 4.0,
      opacity: 1.0,
    ),
    textStyle: JournalTextStyle(
      titleColor: Color(0xFF212121),
      bodyColor: Color(0xFF424242),
      hintColor: Color(0xFF9E9E9E),
    ),
    unlockRequirement: 'Mở 3 thành tựu',
  );

  static const vintage = JournalTheme(
    id: 'vintage',
    name: 'Vintage',
    emoji: '🎞️',
    description: 'Phong cách hoài cổ',
    background: JournalBackground(
        colors: [Color(0xFF3E2723), Color(0xFF4E342E), Color(0xFF5D4037)]),
    cardStyle: JournalCardStyle(
      backgroundColor: Color(0xFFF5F0E1),
      borderColor: Color(0xFFBCAAA4),
      borderRadius: 8.0,
      opacity: 0.95,
    ),
    textStyle: JournalTextStyle(
      titleColor: Color(0xFF3E2723),
      bodyColor: Color(0xFF5D4037),
      hintColor: Color(0xFF8D6E63),
      fontFamily: 'serif',
    ),
    unlockRequirement: 'Viết 30 bài nhật ký',
  );

  static const dark = JournalTheme(
    id: 'dark',
    name: 'Tối',
    emoji: '🌙',
    description: 'Giao diện tối dịu mắt',
    background:
        JournalBackground(colors: [Color(0xFF121212), Color(0xFF1E1E1E)]),
    cardStyle: JournalCardStyle(
      backgroundColor: Color(0xFF2C2C2C),
      borderColor: Color(0xFF424242),
      borderRadius: 16.0,
      opacity: 1.0,
    ),
    textStyle: JournalTextStyle(
      titleColor: Color(0xFFE0E0E0),
      bodyColor: Color(0xFFBDBDBD),
      hintColor: Color(0xFF757575),
    ),
    unlockRequirement: 'Streak 14 ngày',
  );

  static const spiderman = JournalTheme(
    id: 'spiderman',
    name: 'Spider-Man',
    emoji: '🕷️',
    description: 'Theme Spider-Man',
    background:
        JournalBackground(colors: [Color(0xFFB71C1C), Color(0xFF1A237E)]),
    cardStyle: JournalCardStyle(
      backgroundColor: Color(0xE6FFFFFF),
      borderColor: Color(0xFFD32F2F),
      borderRadius: 12.0,
      opacity: 0.9,
    ),
    textStyle: JournalTextStyle(
      titleColor: Color(0xFFB71C1C),
      bodyColor: Color(0xFF212121),
      hintColor: Color(0xFF757575),
    ),
    isDownloadable: true,
    unlockRequirement: 'Tải về',
  );

  static const List<JournalTheme> all = [
    glassmorphism,
    paper,
    notebook,
    floral,
    cute,
    polaroid,
    vintage,
    dark,
    spiderman,
  ];
}
