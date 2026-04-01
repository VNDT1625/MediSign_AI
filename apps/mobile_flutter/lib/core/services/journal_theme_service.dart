import 'package:shared_preferences/shared_preferences.dart';
import '../models/journal_theme.dart';
import 'soul_garden_service.dart';

/// Journal Theme Service - Quan ly theme cho nhap nhat ky
class JournalThemeService {
  JournalThemeService._();
  static final instance = JournalThemeService._();

  static const String _selectedThemeKey = 'journal_selected_theme';
  static const String _unlockedThemesKey = 'journal_unlocked_themes';

  SharedPreferences? _prefs;

  final SoulGardenService _soulGarden = SoulGardenService.instance;

  Future<void> init() async {
    _prefs = await SharedPreferences.getInstance();
  }

  /// Get current theme
  JournalTheme get currentTheme {
    final themeId = _prefs?.getString(_selectedThemeKey) ?? 'glass';
    return JournalThemes.all.firstWhere(
      (t) => t.id == themeId,
      orElse: () => JournalThemes.glassmorphism,
    );
  }

  /// Set current theme
  Future<void> setCurrentTheme(String themeId) async {
    final theme = JournalThemes.all.firstWhere(
      (t) => t.id == themeId,
      orElse: () => JournalThemes.glassmorphism,
    );
    if (theme.isUnlocked) {
      await _prefs?.setString(_selectedThemeKey, themeId);
    }
  }

  /// Get all themes with unlock status
  List<JournalTheme> getAllThemes() {
    final unlockedIds = _prefs?.getStringList(_unlockedThemesKey) ?? ['glass'];

    return JournalThemes.all.map((theme) {
      final isUnlocked = unlockedIds.contains(theme.id) || theme.id == 'glass';
      return theme.copyWith(isUnlocked: isUnlocked);
    }).toList();
  }

  /// Unlock a theme
  Future<void> unlockTheme(String themeId) async {
    final unlockedIds = _prefs?.getStringList(_unlockedThemesKey) ?? ['glass'];
    if (!unlockedIds.contains(themeId)) {
      unlockedIds.add(themeId);
      await _prefs?.setStringList(_unlockedThemesKey, unlockedIds);
    }
  }

  /// Check and unlock themes based on achievements
  Future<void> checkAndUnlockThemes() async {
    final unlockedIds = _prefs?.getStringList(_unlockedThemesKey) ?? ['glass'];
    final entries = _soulGarden.entries.length;
    final streak = _soulGarden.streak;
    final achievements = _soulGarden.unlockedAchievements.length;

    // Unlock conditions
    if (entries >= 3 && !unlockedIds.contains('paper')) {
      unlockedIds.add('paper');
    }
    if (entries >= 7 && !unlockedIds.contains('notebook')) {
      unlockedIds.add('notebook');
    }
    if (streak >= 3 && !unlockedIds.contains('floral')) {
      unlockedIds.add('floral');
    }
    if (streak >= 7 && !unlockedIds.contains('cute')) {
      unlockedIds.add('cute');
    }
    if (achievements >= 3 && !unlockedIds.contains('polaroid')) {
      unlockedIds.add('polaroid');
    }
    if (entries >= 30 && !unlockedIds.contains('vintage')) {
      unlockedIds.add('vintage');
    }
    if (streak >= 14 && !unlockedIds.contains('dark')) {
      unlockedIds.add('dark');
    }

    await _prefs?.setStringList(_unlockedThemesKey, unlockedIds);
  }

  /// Get themes available for download (from server)
  Future<List<JournalTheme>> getDownloadableThemes() async {
    // TODO: Fetch from server
    // Placeholder downloadable themes
    return [
      JournalTheme(
        id: 'spiderman_download',
        name: 'Spider-Man',
        emoji: '\u{1F577}\u{FE0F}',
        description: 'Spider-Man theme',
        background: JournalThemes.spiderman.background,
        cardStyle: JournalThemes.spiderman.cardStyle,
        textStyle: JournalThemes.spiderman.textStyle,
        isDownloadable: true,
        downloadUrl: 'https://example.com/themes/spiderman.json',
        isUnlocked: false,
        unlockRequirement: 'Tai ve',
      ),
    ];
  }

  /// Download a theme from server
  Future<JournalTheme?> downloadTheme(String themeId) async {
    // TODO: Implement download
    // 1. Download theme JSON from downloadUrl
    // 2. Parse and save to local storage
    // 3. Unlock theme
    return null;
  }
}
