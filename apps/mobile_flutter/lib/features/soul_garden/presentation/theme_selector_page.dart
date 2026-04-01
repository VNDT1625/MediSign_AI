import 'package:flutter/material.dart';
import '../../../core/models/journal_theme.dart';
import '../../../core/services/journal_theme_service.dart';

/// Theme Selector Page - Cho phep nguoi dung chon theme
class ThemeSelectorPage extends StatefulWidget {
  const ThemeSelectorPage({super.key});

  @override
  State<ThemeSelectorPage> createState() => _ThemeSelectorPageState();
}

class _ThemeSelectorPageState extends State<ThemeSelectorPage> {
  final _themeService = JournalThemeService.instance;
  late List<JournalTheme> _themes;
  JournalTheme? _currentTheme;

  @override
  void initState() {
    super.initState();
    _loadThemes();
  }

  void _loadThemes() {
    _themes = _themeService.getAllThemes();
    _currentTheme = _themeService.currentTheme;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [Color(0xFF1B4332), Color(0xFF2D6A4F), Color(0xFF40916C)],
          ),
        ),
        child: SafeArea(
          child: Column(
            children: [
              _buildHeader(),
              Expanded(child: _buildThemeGrid()),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildHeader() {
    return Padding(
      padding: const EdgeInsets.all(20),
      child: Row(
        children: [
          IconButton(
            icon: const Icon(Icons.arrow_back_ios, color: Colors.white70),
            onPressed: () => Navigator.pop(context),
          ),
          const Expanded(
            child: Text(
              'Chon Giao Dien',
              textAlign: TextAlign.center,
              style: TextStyle(
                color: Colors.white,
                fontSize: 20,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
          const SizedBox(width: 48),
        ],
      ),
    );
  }

  Widget _buildThemeGrid() {
    return GridView.builder(
      padding: const EdgeInsets.all(16),
      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 2,
        crossAxisSpacing: 16,
        mainAxisSpacing: 16,
        childAspectRatio: 0.85,
      ),
      itemCount: _themes.length,
      itemBuilder: (context, index) {
        final theme = _themes[index];
        return _ThemeCard(
          theme: theme,
          isSelected: _currentTheme?.id == theme.id,
          onTap: theme.isUnlocked
              ? () => _selectTheme(theme)
              : () => _showUnlockDialog(theme),
        );
      },
    );
  }

  void _selectTheme(JournalTheme theme) {
    _themeService.setCurrentTheme(theme.id);
    setState(() {
      _currentTheme = theme;
    });
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text('Da chon giao dien ${theme.name}'),
        backgroundColor: const Color(0xFF52B788),
      ),
    );
  }

  void _showUnlockDialog(JournalTheme theme) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: const Color(0xFF1B4332),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
        title: Row(
          children: [
            Text(theme.emoji, style: const TextStyle(fontSize: 28)),
            const SizedBox(width: 12),
            Text(
              theme.name,
              style: const TextStyle(color: Colors.white, fontSize: 18),
            ),
          ],
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              theme.description,
              style: TextStyle(color: Colors.white.withOpacity(0.7)),
            ),
            const SizedBox(height: 16),
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.white.withOpacity(0.1),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Row(
                children: [
                  const Icon(Icons.lock, color: Color(0xFFFFB74D), size: 20),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      theme.unlockRequirement ?? 'Chua mo khoa',
                      style: const TextStyle(color: Color(0xFFFFB74D)),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Dong', style: TextStyle(color: Colors.white70)),
          ),
          if (theme.isDownloadable)
            ElevatedButton(
              onPressed: () {
                Navigator.pop(context);
                _downloadTheme(theme);
              },
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF52B788),
              ),
              child: const Text('Tai ve'),
            ),
        ],
      ),
    );
  }

  void _downloadTheme(JournalTheme theme) async {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => const Center(
        child: CircularProgressIndicator(color: Color(0xFF52B788)),
      ),
    );

    final downloaded = await _themeService.downloadTheme(theme.id);

    if (mounted) {
      Navigator.pop(context);
      if (downloaded != null) {
        setState(() {
          _loadThemes();
        });
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Da tai giao dien ${theme.name}'),
            backgroundColor: const Color(0xFF52B788),
          ),
        );
      }
    }
  }
}

class _ThemeCard extends StatelessWidget {
  final JournalTheme theme;
  final bool isSelected;
  final VoidCallback onTap;

  const _ThemeCard({
    required this.theme,
    required this.isSelected,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        decoration: BoxDecoration(
          color: theme.isUnlocked
              ? theme.background.colors.isNotEmpty
                  ? theme.background.colors.first.withOpacity(0.3)
                  : Colors.white.withOpacity(0.2)
              : Colors.black.withOpacity(0.3),
          borderRadius: BorderRadius.circular(20),
          border: Border.all(
            color: isSelected
                ? const Color(0xFF52B788)
                : theme.isUnlocked
                    ? Colors.white.withOpacity(0.2)
                    : Colors.grey.withOpacity(0.3),
            width: isSelected ? 3 : 1,
          ),
        ),
        child: Stack(
          children: [
            Padding(
              padding: const EdgeInsets.all(12),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Center(
                    child: Text(
                      theme.emoji,
                      style: TextStyle(
                        fontSize: 40,
                        color: theme.isUnlocked ? null : Colors.grey,
                      ),
                    ),
                  ),
                  const Spacer(),
                  Text(
                    theme.name,
                    style: TextStyle(
                      color: theme.isUnlocked ? Colors.white : Colors.grey,
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    theme.description,
                    style: TextStyle(
                      color: theme.isUnlocked
                          ? Colors.white.withOpacity(0.6)
                          : Colors.grey.withOpacity(0.5),
                      fontSize: 11,
                    ),
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                  ),
                ],
              ),
            ),
            if (!theme.isUnlocked)
              Positioned.fill(
                child: Container(
                  decoration: BoxDecoration(
                    color: Colors.black.withOpacity(0.5),
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: const Center(
                    child: Icon(Icons.lock, color: Colors.white54, size: 32),
                  ),
                ),
              ),
            if (isSelected)
              Positioned(
                top: 8,
                right: 8,
                child: Container(
                  padding: const EdgeInsets.all(4),
                  decoration: const BoxDecoration(
                    color: Color(0xFF52B788),
                    shape: BoxShape.circle,
                  ),
                  child: const Icon(Icons.check, color: Colors.white, size: 16),
                ),
              ),
            if (theme.isDownloadable && !theme.isUnlocked)
              Positioned(
                top: 8,
                left: 8,
                child: Container(
                  padding: const EdgeInsets.all(4),
                  decoration: BoxDecoration(
                    color: const Color(0xFFFFB74D),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: const Icon(Icons.download, color: Colors.white, size: 14),
                ),
              ),
          ],
        ),
      ),
    );
  }
}
