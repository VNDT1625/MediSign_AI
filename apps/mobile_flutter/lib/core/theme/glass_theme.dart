import 'dart:ui';

import 'package:flutter/material.dart';

/// Unified Glassmorphism Theme for MediSign AI
/// Consistent design system across all pages with accessibility in mind.
/// Large fonts and high contrast for users with poor eyesight.
class GlassTheme {
  GlassTheme._();

  // ═══════════════════════════════════════════════
  //  PRIMARY COLORS
  // ═══════════════════════════════════════════════

  static const Color primaryGreen = Color(0xFF0D9B6B);
  static const Color primaryGreenLight = Color(0xFF34D399);
  static const Color primaryGreenDark = Color(0xFF064E3B);

  static const Color accentBlue = Color(0xFF2563EB);
  static const Color accentPurple = Color(0xFF7C3AED);
  static const Color accentOrange = Color(0xFFF59E0B);
  static const Color accentRed = Color(0xFFEF4444);

  // ── Extended palette (used across features) ──
  static const Color tealPrimary = Color(0xFF0D9488);
  static const Color tealLight = Color(0xFF14B8A6);
  static const Color tealCyan = Color(0xFF5EEAD4);
  static const Color tealDark = Color(0xFF0F766E);
  static const Color successGreen = Color(0xFF22C55E);
  static const Color communicationBadge = Color(0xFF52B788);
  static const Color navBackground = Color(0xFF0A2540);
  static const Color emergencyRed = Color(0xFFDC2626);
  static const Color emergencyRedLight = Color(0xFFFCA5A5);

  // ═══════════════════════════════════════════════
  //  GLASS COLORS (with opacity)
  // ═══════════════════════════════════════════════

  /// Glass fill - white with low opacity
  static const Color glassFill = Color(0x1EFFFFFF); // 12% white
  static const Color glassFillLight = Color(0x29FFFFFF); // 16% white
  static const Color glassFillMedium = Color(0x33FFFFFF); // 20% white

  /// Glass border
  static const Color glassBorder = Color(0x33FFFFFF); // 20%
  static const Color glassBorderLight = Color(0x1AFFFFFF); // 10%
  static const Color glassBorderStrong = Color(0x4DFFFFFF); // 30%

  /// Input field background
  static const Color inputFill = Color(0x14FFFFFF); // 8%

  // ═══════════════════════════════════════════════
  //  TEXT COLORS - HIGH CONTRAST FOR ACCESSIBILITY
  // ═══════════════════════════════════════════════

  /// Primary text - pure white for maximum contrast on dark backgrounds
  static const Color textPrimary = Color(0xFFFFFFFF);
  static const Color textSecondary = Color(0xB3FFFFFF); // 70%
  static const Color textMuted =
      Color(0xA6FFFFFF); // 65% — meets WCAG AA on dark bg
  static const Color textDisabled = Color(0x66FFFFFF); // 40%

  /// Text on light backgrounds
  static const Color textOnLight = Color(0xFF1F2937);
  static const Color textOnLightSecondary = Color(0xFF6B7280);

  // ═══════════════════════════════════════════════
  //  BACKGROUND COLORS
  // ═══════════════════════════════════════════════

  /// Dark gradient colors
  static const Color bgDark1 = Color(0xFF064E3B);
  static const Color bgDark2 = Color(0xFF0A6B52);
  static const Color bgDark3 = Color(0xFF0F766E);
  static const Color bgDark4 = Color(0xFF1A5C4A);
  static const Color bgDark5 = Color(0xFF1E3A5F);

  // ═══════════════════════════════════════════════
  //  TYPOGRAPHY - LARGE FOR ACCESSIBILITY
  // ═══════════════════════════════════════════════

  static const String fontFamily = 'Outfit';

  /// Large heading - for main titles
  static const TextStyle h1 = TextStyle(
    fontFamily: fontFamily,
    fontSize: 28,
    fontWeight: FontWeight.w800,
    color: textPrimary,
    height: 1.2,
    letterSpacing: -0.5,
  );

  /// Section heading
  static const TextStyle h2 = TextStyle(
    fontFamily: fontFamily,
    fontSize: 22,
    fontWeight: FontWeight.w700,
    color: textPrimary,
    height: 1.3,
  );

  /// Card title
  static const TextStyle h3 = TextStyle(
    fontFamily: fontFamily,
    fontSize: 18,
    fontWeight: FontWeight.w700,
    color: textPrimary,
    height: 1.4,
  );

  /// Body text - LARGE for accessibility
  static const TextStyle bodyLarge = TextStyle(
    fontFamily: fontFamily,
    fontSize: 17,
    fontWeight: FontWeight.w400,
    color: textPrimary,
    height: 1.5,
  );

  static const TextStyle body = TextStyle(
    fontFamily: fontFamily,
    fontSize: 15,
    fontWeight: FontWeight.w400,
    color: textSecondary,
    height: 1.5,
  );

  /// Button text
  static const TextStyle button = TextStyle(
    fontFamily: fontFamily,
    fontSize: 16,
    fontWeight: FontWeight.w600,
    color: textPrimary,
    letterSpacing: 0.3,
  );

  /// Caption - LARGER than usual for accessibility
  static const TextStyle caption = TextStyle(
    fontFamily: fontFamily,
    fontSize: 14,
    fontWeight: FontWeight.w400,
    color: textMuted,
    height: 1.4,
  );

  /// Small label
  static const TextStyle label = TextStyle(
    fontFamily: fontFamily,
    fontSize: 13,
    fontWeight: FontWeight.w600,
    color: textSecondary,
    letterSpacing: 0.3,
  );

  // ═══════════════════════════════════════════════
  //  GRADIENT BACKGROUNDS
  // ═══════════════════════════════════════════════

  /// Main app gradient - teal/green medical theme
  static const BoxDecoration gradientBackground = BoxDecoration(
    gradient: LinearGradient(
      begin: Alignment.topLeft,
      end: Alignment.bottomRight,
      colors: [bgDark1, bgDark2, bgDark3, bgDark4, Color(0xFF2D3A4F)],
      stops: [0.0, 0.25, 0.5, 0.75, 1.0],
    ),
  );

  /// Green gradient for primary actions
  static const BoxDecoration greenGradient = BoxDecoration(
    gradient: LinearGradient(
      begin: Alignment.topLeft,
      end: Alignment.bottomRight,
      colors: [primaryGreen, Color(0xFF059669), Color(0xFF10B981)],
    ),
    borderRadius: BorderRadius.all(Radius.circular(16)),
  );

  /// Blue gradient
  static const BoxDecoration blueGradient = BoxDecoration(
    gradient: LinearGradient(
      begin: Alignment.topLeft,
      end: Alignment.bottomRight,
      colors: [accentBlue, Color(0xFF0EA5E9)],
    ),
    borderRadius: BorderRadius.all(Radius.circular(16)),
  );

  // ═══════════════════════════════════════════════
  //  GLASSMORPHISM COMPONENTS
  // ═══════════════════════════════════════════════

  /// Full screen gradient background with decorative orbs
  static Widget scaffoldBackground({required Widget child}) {
    return Container(
      decoration: gradientBackground,
      child: Stack(
        children: [
          // Decorative orbs for ambient light effect
          Positioned(
            top: -100,
            right: -80,
            child: _decorativeOrb(
              color: primaryGreenLight,
              opacity: 0.12,
              size: 280,
            ),
          ),
          Positioned(
            bottom: -120,
            left: -100,
            child: _decorativeOrb(
              color: accentPurple,
              opacity: 0.08,
              size: 320,
            ),
          ),
          Positioned(
            top: 200,
            right: -60,
            child: _decorativeOrb(
              color: primaryGreenLight,
              opacity: 0.06,
              size: 180,
            ),
          ),
          child,
        ],
      ),
    );
  }

  static Widget _decorativeOrb({
    required Color color,
    required double opacity,
    required double size,
  }) {
    return Container(
      width: size,
      height: size,
      decoration: BoxDecoration(
        shape: BoxShape.circle,
        gradient: RadialGradient(
          colors: [color.withOpacity(opacity), color.withOpacity(0)],
        ),
      ),
    );
  }

  /// Glass card with blur effect - main component
  static Widget glassCard({
    required Widget child,
    EdgeInsets? padding,
    EdgeInsets? margin,
    double borderRadius = 20,
    double blurSigma = 20,
    Color? fillColor,
    Color? borderColor,
    bool isActive = false,
    Color activeColor = primaryGreen,
  }) {
    return Container(
      margin: margin,
      child: ClipRRect(
        borderRadius: BorderRadius.circular(borderRadius),
        child: BackdropFilter(
          filter: ImageFilter.blur(sigmaX: blurSigma, sigmaY: blurSigma),
          child: AnimatedContainer(
            duration: const Duration(milliseconds: 200),
            curve: Curves.easeOut,
            padding: padding ?? const EdgeInsets.all(20),
            decoration: BoxDecoration(
              color: fillColor ?? glassFill,
              borderRadius: BorderRadius.circular(borderRadius),
              border: Border.all(
                color: isActive
                    ? activeColor.withOpacity(0.5)
                    : (borderColor ?? glassBorder),
                width: isActive ? 1.5 : 1,
              ),
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withOpacity(0.1),
                  blurRadius: 30,
                  offset: const Offset(0, 8),
                ),
              ],
            ),
            child: child,
          ),
        ),
      ),
    );
  }

  /// Solid glass card - no blur, better for readability
  static Widget solidCard({
    required Widget child,
    EdgeInsets? padding,
    EdgeInsets? margin,
    double borderRadius = 20,
    Color? backgroundColor,
    Color? borderColor,
  }) {
    return Container(
      margin: margin,
      padding: padding ?? const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: backgroundColor ?? glassFillMedium,
        borderRadius: BorderRadius.circular(borderRadius),
        border: Border.all(
          color: borderColor ?? glassBorder,
          width: 1,
        ),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.08),
            blurRadius: 20,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: child,
    );
  }

  // ═══════════════════════════════════════════════
  //  BUTTONS
  // ═══════════════════════════════════════════════

  /// Primary gradient button - LARGE for accessibility
  static Widget primaryButton({
    required String text,
    required VoidCallback? onPressed,
    bool isLoading = false,
    IconData? icon,
    Color? backgroundColor,
    double height = 56,
  }) {
    return SizedBox(
      width: double.infinity,
      height: height,
      child: DecoratedBox(
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(16),
          gradient: backgroundColor == null
              ? const LinearGradient(
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                  colors: [primaryGreen, Color(0xFF059669)],
                )
              : null,
          color: backgroundColor,
          boxShadow: [
            BoxShadow(
              color: (backgroundColor ?? primaryGreen).withOpacity(0.3),
              blurRadius: 16,
              offset: const Offset(0, 6),
            ),
          ],
        ),
        child: ElevatedButton(
          onPressed: isLoading ? null : onPressed,
          style: ElevatedButton.styleFrom(
            backgroundColor: Colors.transparent,
            shadowColor: Colors.transparent,
            disabledBackgroundColor: Colors.transparent,
            foregroundColor: Colors.white,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(16),
            ),
          ),
          child: isLoading
              ? const SizedBox(
                  width: 24,
                  height: 24,
                  child: CircularProgressIndicator(
                    strokeWidth: 2.5,
                    color: Colors.white,
                  ),
                )
              : Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    if (icon != null) ...[
                      Icon(icon, size: 22, color: Colors.white),
                      const SizedBox(width: 10),
                    ],
                    Text(text, style: button.copyWith(color: Colors.white)),
                  ],
                ),
        ),
      ),
    );
  }

  /// Secondary glass button
  static Widget secondaryButton({
    required String text,
    required VoidCallback onPressed,
    IconData? icon,
    double height = 52,
  }) {
    return SizedBox(
      width: double.infinity,
      height: height,
      child: ClipRRect(
        borderRadius: BorderRadius.circular(14),
        child: BackdropFilter(
          filter: ImageFilter.blur(sigmaX: 10, sigmaY: 10),
          child: OutlinedButton(
            onPressed: onPressed,
            style: OutlinedButton.styleFrom(
              foregroundColor: textPrimary,
              backgroundColor: glassFillLight,
              side: const BorderSide(color: glassBorder, width: 1),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(14),
              ),
            ),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                if (icon != null) ...[
                  Icon(icon, size: 20, color: textPrimary),
                  const SizedBox(width: 8),
                ],
                Text(text, style: button),
              ],
            ),
          ),
        ),
      ),
    );
  }

  /// Icon button with glass effect
  static Widget glassIconButton({
    required IconData icon,
    required VoidCallback onPressed,
    Color? iconColor,
    double size = 48,
    String? tooltip,
  }) {
    return ClipRRect(
      borderRadius: BorderRadius.circular(size / 2),
      child: BackdropFilter(
        filter: ImageFilter.blur(sigmaX: 8, sigmaY: 8),
        child: Material(
          color: glassFillLight,
          borderRadius: BorderRadius.circular(size / 2),
          child: InkWell(
            onTap: onPressed,
            borderRadius: BorderRadius.circular(size / 2),
            child: Container(
              width: size,
              height: size,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                border: Border.all(color: glassBorderLight),
              ),
              child: Icon(
                icon,
                size: size * 0.45,
                color: iconColor ?? textPrimary,
              ),
            ),
          ),
        ),
      ),
    );
  }

  // ═══════════════════════════════════════════════
  //  INPUT FIELDS
  // ═══════════════════════════════════════════════

  /// Glass text field - LARGE for accessibility
  static Widget textField({
    required TextEditingController controller,
    required String hint,
    IconData? prefixIcon,
    IconData? suffixIcon,
    VoidCallback? onSuffixTap,
    bool obscure = false,
    TextInputType? keyboardType,
    int maxLines = 1,
    String? errorText,
    ValueChanged<String>? onChanged,
  }) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        ClipRRect(
          borderRadius: BorderRadius.circular(16),
          child: BackdropFilter(
            filter: ImageFilter.blur(sigmaX: 8, sigmaY: 8),
            child: Container(
              decoration: BoxDecoration(
                color: inputFill,
                borderRadius: BorderRadius.circular(16),
                border: Border.all(
                  color: errorText != null
                      ? accentRed.withOpacity(0.5)
                      : glassBorder,
                  width: errorText != null ? 1.5 : 1,
                ),
              ),
              child: TextField(
                controller: controller,
                obscureText: obscure,
                keyboardType: keyboardType,
                maxLines: maxLines,
                onChanged: onChanged,
                style: bodyLarge.copyWith(
                  color: textPrimary,
                  fontSize: 16,
                ),
                cursorColor: primaryGreenLight,
                decoration: InputDecoration(
                  hintText: hint,
                  hintStyle: body.copyWith(
                    color: textMuted,
                    fontSize: 15,
                  ),
                  prefixIcon: prefixIcon != null
                      ? Icon(prefixIcon, size: 22, color: textMuted)
                      : null,
                  suffixIcon: suffixIcon != null
                      ? GestureDetector(
                          onTap: onSuffixTap,
                          child: Icon(suffixIcon, size: 22, color: textMuted),
                        )
                      : null,
                  border: InputBorder.none,
                  contentPadding: const EdgeInsets.symmetric(
                    horizontal: 18,
                    vertical: 16,
                  ),
                ),
              ),
            ),
          ),
        ),
        if (errorText != null)
          Padding(
            padding: const EdgeInsets.only(top: 8, left: 4),
            child: Text(
              errorText,
              style: caption.copyWith(color: accentRed),
            ),
          ),
      ],
    );
  }

  // ═══════════════════════════════════════════════
  //  NAVIGATION
  // ═══════════════════════════════════════════════

  /// Bottom navigation bar - glass style
  static Widget bottomNavBar({
    required int selectedIndex,
    required List<BottomNavItem> items,
    required ValueChanged<int> onTap,
    double height = 80,
  }) {
    return Container(
      decoration: const BoxDecoration(
        color: glassFillMedium,
        border: Border(
          top: BorderSide(color: glassBorder, width: 0.5),
        ),
      ),
      child: SafeArea(
        top: false,
        child: SizedBox(
          height: height,
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: items.asMap().entries.map((entry) {
              final index = entry.key;
              final item = entry.value;
              final isSelected = index == selectedIndex;

              return Expanded(
                child: GestureDetector(
                  onTap: () => onTap(index),
                  behavior: HitTestBehavior.opaque,
                  child: SizedBox(
                    height: height,
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        AnimatedContainer(
                          duration: const Duration(milliseconds: 200),
                          padding: const EdgeInsets.symmetric(
                            horizontal: 16,
                            vertical: 6,
                          ),
                          decoration: BoxDecoration(
                            color: isSelected
                                ? primaryGreen.withOpacity(0.15)
                                : Colors.transparent,
                            borderRadius: BorderRadius.circular(20),
                          ),
                          child: Icon(
                            isSelected ? item.selectedIcon : item.icon,
                            size: 26,
                            color: isSelected ? primaryGreen : textMuted,
                          ),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          item.label,
                          style: TextStyle(
                            fontFamily: fontFamily,
                            fontSize: 12,
                            fontWeight:
                                isSelected ? FontWeight.w600 : FontWeight.w400,
                            color: isSelected ? primaryGreen : textMuted,
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              );
            }).toList(),
          ),
        ),
      ),
    );
  }

  /// App bar with glass effect
  static Widget appBar({
    required String title,
    Widget? leading,
    List<Widget>? actions,
    bool showBackButton = true,
    VoidCallback? onBack,
  }) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(8, 8, 8, 0),
      child: Row(
        children: [
          if (showBackButton && onBack != null)
            glassIconButton(
              icon: Icons.arrow_back_ios_new_rounded,
              onPressed: onBack,
              size: 44,
            )
          else if (leading != null)
            leading
          else
            const SizedBox(width: 44),
          Expanded(
            child: Text(
              title,
              textAlign: TextAlign.center,
              style: h3,
            ),
          ),
          if (actions != null) ...actions else const SizedBox(width: 44),
        ],
      ),
    );
  }

  // ═══════════════════════════════════════════════
  //  LOADING & EMPTY STATES
  // ═══════════════════════════════════════════════

  /// Loading indicator
  static Widget loadingIndicator({String? message}) {
    return Center(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          const SizedBox(
            width: 48,
            height: 48,
            child: CircularProgressIndicator(
              strokeWidth: 3,
              color: primaryGreenLight,
            ),
          ),
          if (message != null) ...[
            const SizedBox(height: 16),
            Text(message, style: body),
          ],
        ],
      ),
    );
  }

  /// Empty state with icon and message
  static Widget emptyState({
    required String emoji,
    required String title,
    String? subtitle,
    Widget? action,
  }) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(emoji, style: const TextStyle(fontSize: 64)),
            const SizedBox(height: 16),
            Text(title, style: h3, textAlign: TextAlign.center),
            if (subtitle != null) ...[
              const SizedBox(height: 8),
              Text(subtitle, style: body, textAlign: TextAlign.center),
            ],
            if (action != null) ...[
              const SizedBox(height: 24),
              action,
            ],
          ],
        ),
      ),
    );
  }

  // ═══════════════════════════════════════════════
  //  CARDS & LIST ITEMS
  // ═══════════════════════════════════════════════

  /// Feature card for dashboard
  static Widget featureCard({
    required String title,
    required String subtitle,
    required IconData icon,
    required Color iconColor,
    required VoidCallback onTap,
  }) {
    return glassCard(
      padding: const EdgeInsets.all(16),
      margin: const EdgeInsets.only(bottom: 12),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(20),
        child: Row(
          children: [
            Container(
              width: 56,
              height: 56,
              decoration: BoxDecoration(
                color: iconColor.withOpacity(0.15),
                borderRadius: BorderRadius.circular(16),
              ),
              child: Icon(icon, size: 28, color: iconColor),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(title, style: h3.copyWith(fontSize: 16)),
                  const SizedBox(height: 4),
                  Text(subtitle, style: body.copyWith(fontSize: 13)),
                ],
              ),
            ),
            const Icon(
              Icons.chevron_right_rounded,
              color: textMuted,
              size: 28,
            ),
          ],
        ),
      ),
    );
  }

  /// Menu item for settings/lists
  static Widget menuItem({
    required String emoji,
    required String title,
    String? subtitle,
    required VoidCallback onTap,
    Widget? trailing,
  }) {
    return glassCard(
      padding: const EdgeInsets.all(16),
      margin: const EdgeInsets.only(bottom: 10),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(20),
        child: Row(
          children: [
            Text(emoji, style: const TextStyle(fontSize: 26)),
            const SizedBox(width: 14),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(title, style: button.copyWith(fontSize: 15)),
                  if (subtitle != null) Text(subtitle, style: caption),
                ],
              ),
            ),
            trailing ??
                const Icon(
                  Icons.chevron_right_rounded,
                  color: textMuted,
                  size: 24,
                ),
          ],
        ),
      ),
    );
  }

  // ═══════════════════════════════════════════════
  //  BADGES & TAGS
  // ═══════════════════════════════════════════════

  /// Badge chip
  static Widget badge({
    required String text,
    Color? backgroundColor,
    Color? textColor,
    IconData? icon,
  }) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: backgroundColor ?? primaryGreen.withOpacity(0.15),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(
          color: (backgroundColor ?? primaryGreen).withOpacity(0.3),
        ),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          if (icon != null) ...[
            Icon(icon, size: 16, color: textColor ?? primaryGreen),
            const SizedBox(width: 6),
          ],
          Text(
            text,
            style: TextStyle(
              fontFamily: fontFamily,
              fontSize: 13,
              fontWeight: FontWeight.w600,
              color: textColor ?? primaryGreen,
            ),
          ),
        ],
      ),
    );
  }

  /// Status indicator (for urgency levels)
  static Widget statusBadge({
    required String text,
    required Color color,
  }) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 6),
      decoration: BoxDecoration(
        color: color.withOpacity(0.15),
        borderRadius: BorderRadius.circular(20),
      ),
      child: Text(
        text,
        style: TextStyle(
          fontFamily: fontFamily,
          fontSize: 13,
          fontWeight: FontWeight.w600,
          color: color,
        ),
      ),
    );
  }

  // ═══════════════════════════════════════════════
  //  PROGRESS INDICATORS
  // ═══════════════════════════════════════════════

  /// Progress dots for wizard steps
  static Widget progressDots({
    required int total,
    required int current,
    Color activeColor = primaryGreen,
    Color inactiveColor = const Color(0x33FFFFFF),
  }) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: List.generate(total, (index) {
        final isActive = index <= current;
        return AnimatedContainer(
          duration: const Duration(milliseconds: 300),
          margin: const EdgeInsets.symmetric(horizontal: 4),
          width: isActive ? 24 : 8,
          height: 8,
          decoration: BoxDecoration(
            color: isActive ? activeColor : inactiveColor,
            borderRadius: BorderRadius.circular(4),
          ),
        );
      }),
    );
  }

  /// Linear progress bar
  static Widget progressBar({
    required double value,
    Color? backgroundColor,
    Color? progressColor,
    double height = 6,
  }) {
    return ClipRRect(
      borderRadius: BorderRadius.circular(height / 2),
      child: Container(
        height: height,
        decoration: BoxDecoration(
          color: backgroundColor ?? const Color(0x33FFFFFF),
          borderRadius: BorderRadius.circular(height / 2),
        ),
        child: FractionallySizedBox(
          alignment: Alignment.centerLeft,
          widthFactor: value.clamp(0.0, 1.0),
          child: Container(
            decoration: BoxDecoration(
              gradient: const LinearGradient(
                colors: [primaryGreen, primaryGreenLight],
              ),
              borderRadius: BorderRadius.circular(height / 2),
            ),
          ),
        ),
      ),
    );
  }

  // ═══════════════════════════════════════════════
  //  PAGE TRANSITIONS
  // ═══════════════════════════════════════════════

  /// Smooth fade+slide page route — use instead of MaterialPageRoute
  static Route<T> route<T>(Widget page, {Duration? duration}) {
    return PageRouteBuilder<T>(
      pageBuilder: (_, __, ___) => page,
      transitionsBuilder: (_, animation, __, child) {
        return FadeTransition(
          opacity: CurvedAnimation(
            parent: animation,
            curve: Curves.easeOut,
          ),
          child: SlideTransition(
            position: Tween<Offset>(
              begin: const Offset(0.04, 0),
              end: Offset.zero,
            ).animate(CurvedAnimation(
              parent: animation,
              curve: Curves.easeOutCubic,
            )),
            child: child,
          ),
        );
      },
      transitionDuration: duration ?? const Duration(milliseconds: 350),
    );
  }

  // ═══════════════════════════════════════════════
  //  GLASS DIALOG & SNACKBAR
  // ═══════════════════════════════════════════════

  /// Dark glass-themed confirmation dialog
  static Future<bool?> showGlassDialog({
    required BuildContext context,
    required String title,
    required String content,
    String confirmText = 'Xác nhận',
    String cancelText = 'Hủy',
    bool isDestructive = false,
  }) {
    return showDialog<bool>(
      context: context,
      builder: (_) => Dialog(
        backgroundColor: Colors.transparent,
        child: ClipRRect(
          borderRadius: BorderRadius.circular(24),
          child: BackdropFilter(
            filter: ImageFilter.blur(sigmaX: 30, sigmaY: 30),
            child: Container(
              padding: const EdgeInsets.all(24),
              decoration: BoxDecoration(
                color: const Color(0xFF0A2540).withOpacity(0.92),
                borderRadius: BorderRadius.circular(24),
                border: Border.all(color: glassBorder),
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withOpacity(0.3),
                    blurRadius: 30,
                    offset: const Offset(0, 10),
                  ),
                ],
              ),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text(title, style: h3, textAlign: TextAlign.center),
                  const SizedBox(height: 12),
                  Text(content, style: body, textAlign: TextAlign.center),
                  const SizedBox(height: 24),
                  Row(
                    children: [
                      Expanded(
                        child: secondaryButton(
                          text: cancelText,
                          onPressed: () => Navigator.pop(context, false),
                          height: 46,
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: primaryButton(
                          text: confirmText,
                          onPressed: () => Navigator.pop(context, true),
                          height: 46,
                          backgroundColor:
                              isDestructive ? accentRed : null,
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }

  /// Dark glass-themed snackbar
  static void showGlassSnackBar(
    BuildContext context,
    String message, {
    Duration duration = const Duration(seconds: 3),
    String? emoji,
  }) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Row(
          children: [
            if (emoji != null) ...[
              Text(emoji, style: const TextStyle(fontSize: 18)),
              const SizedBox(width: 10),
            ],
            Expanded(
              child: Text(
                message,
                style: const TextStyle(
                  fontFamily: fontFamily,
                  fontSize: 14,
                  color: Colors.white,
                ),
              ),
            ),
          ],
        ),
        backgroundColor: navBackground.withOpacity(0.95),
        behavior: SnackBarBehavior.floating,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16),
          side: BorderSide(color: glassBorderLight),
        ),
        margin: const EdgeInsets.fromLTRB(16, 0, 16, 16),
        duration: duration,
      ),
    );
  }

  // ═══════════════════════════════════════════════
  //  SKELETON LOADING
  // ═══════════════════════════════════════════════

  /// Shimmer skeleton card matching glass style
  static Widget skeletonCard({
    double height = 80,
    EdgeInsets? margin,
  }) {
    return Container(
      height: height,
      margin: margin ?? const EdgeInsets.only(bottom: 12),
      decoration: BoxDecoration(
        color: glassFill,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: glassBorderLight),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          children: [
            Container(
              width: 48,
              height: 48,
              decoration: BoxDecoration(
                color: glassFillLight,
                borderRadius: BorderRadius.circular(14),
              ),
            ),
            const SizedBox(width: 14),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Container(
                    width: 120,
                    height: 14,
                    decoration: BoxDecoration(
                      color: glassFillLight,
                      borderRadius: BorderRadius.circular(7),
                    ),
                  ),
                  const SizedBox(height: 8),
                  Container(
                    width: 180,
                    height: 10,
                    decoration: BoxDecoration(
                      color: glassFill,
                      borderRadius: BorderRadius.circular(5),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

/// Data class for bottom navigation items
class BottomNavItem {
  final IconData icon;
  final IconData selectedIcon;
  final String label;

  const BottomNavItem({
    required this.icon,
    required this.selectedIcon,
    required this.label,
  });
}
