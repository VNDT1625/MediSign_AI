import 'dart:ui';

import 'package:flutter/material.dart';

import '../../../core/theme/glass_theme.dart';

/// Auth-specific theme — thin proxy delegating to [GlassTheme].
///
/// Auth screens use slightly larger border radii (28 vs 16 for buttons)
/// and stronger shadows for the "hero" feel, but all base colors and
/// typography come from the unified GlassTheme.
class AuthTheme {
  AuthTheme._();

  // ── Colors (delegates to GlassTheme) ──
  static const Color primaryDark = GlassTheme.primaryGreenDark;
  static const Color primary = GlassTheme.primaryGreen;
  static const Color primaryLight = GlassTheme.primaryGreenLight;
  static Color get primaryBg => GlassTheme.primaryGreenLight.withOpacity(0.12);

  // Glass-specific
  static const Color glassFill = GlassTheme.glassFill;
  static const Color glassFillLight = GlassTheme.glassFillLight;
  static const Color glassBorder = GlassTheme.glassBorder;
  static const Color glassBorderStrong = GlassTheme.glassBorderStrong;
  static const Color glassInputFill = GlassTheme.inputFill;

  // Text on glass
  static const Color textOnGlass = GlassTheme.textPrimary;
  static const Color textOnGlassSecondary = GlassTheme.textSecondary;
  static const Color textOnGlassMuted = Color(0x80FFFFFF); // 50%

  // ── Typography (unified via GlassTheme, auth-specific sizes) ──
  static const String fontFamily = GlassTheme.fontFamily;

  static const TextStyle h1 = TextStyle(
    fontFamily: fontFamily,
    fontSize: 32,
    fontWeight: FontWeight.w800,
    color: textOnGlass,
    height: 1.15,
    letterSpacing: -0.5,
  );

  static const TextStyle h2 = TextStyle(
    fontFamily: fontFamily,
    fontSize: 24,
    fontWeight: FontWeight.w700,
    color: textOnGlass,
    height: 1.2,
  );

  static const TextStyle subtitle = TextStyle(
    fontFamily: fontFamily,
    fontSize: 15,
    fontWeight: FontWeight.w400,
    color: textOnGlassSecondary,
    height: 1.5,
  );

  static const TextStyle body = TextStyle(
    fontFamily: fontFamily,
    fontSize: 15,
    fontWeight: FontWeight.w400,
    color: textOnGlass,
    height: 1.4,
  );

  static const TextStyle label = TextStyle(
    fontFamily: fontFamily,
    fontSize: 14,
    fontWeight: FontWeight.w600,
    color: textOnGlass,
  );

  static const TextStyle caption = TextStyle(
    fontFamily: fontFamily,
    fontSize: 12,
    fontWeight: FontWeight.w400,
    color: textOnGlassMuted,
  );

  static const TextStyle link = TextStyle(
    fontFamily: fontFamily,
    fontSize: 15,
    fontWeight: FontWeight.w600,
    color: primaryLight,
  );

  static const TextStyle buttonText = TextStyle(
    fontFamily: fontFamily,
    fontSize: 16,
    fontWeight: FontWeight.w700,
    color: Colors.white,
    letterSpacing: 0.3,
  );

  // ══════════════════════════════════════════════
  //  GLASSMORPHISM FOUNDATION — delegates to GlassTheme
  // ══════════════════════════════════════════════

  /// Gradient background — delegates to [GlassTheme.scaffoldBackground].
  static Widget gradientBackground({required Widget child}) {
    return GlassTheme.scaffoldBackground(child: child);
  }

  /// Frosted glass card — delegates to [GlassTheme.glassCard] with auth-specific defaults.
  static Widget glassCard({
    required Widget child,
    EdgeInsets? padding,
    double borderRadius = 24,
    double blurSigma = 24,
    Color? fillColor,
    Color? borderColor,
    bool isActive = false,
    Color activeColor = primary,
  }) {
    return GlassTheme.glassCard(
      padding: padding,
      borderRadius: borderRadius,
      blurSigma: blurSigma,
      fillColor: fillColor,
      borderColor: borderColor,
      isActive: isActive,
      activeColor: activeColor,
      child: child,
    );
  }

  // ══════════════════════════════════════════════
  //  AUTH-SPECIFIC WIDGETS
  // ══════════════════════════════════════════════

  /// Back button — frosted glass circle
  static Widget backButton(BuildContext context) {
    return GlassTheme.glassIconButton(
      icon: Icons.arrow_back_ios_new_rounded,
      onPressed: () => Navigator.of(context).pop(),
      size: 44,
    );
  }

  /// Primary CTA button — glass overlay with gradient fill (larger radius for auth)
  static Widget primaryButton({
    required String text,
    required VoidCallback? onPressed,
    bool isLoading = false,
    IconData? icon,
  }) {
    return SizedBox(
      width: double.infinity,
      height: 56,
      child: DecoratedBox(
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(28),
          gradient: const LinearGradient(
            colors: [
              GlassTheme.primaryGreen,
              Color(0xFF059669),
              Color(0xFF10B981),
            ],
          ),
          boxShadow: [
            BoxShadow(
              color: GlassTheme.primaryGreen.withOpacity(0.35),
              blurRadius: 20,
              offset: const Offset(0, 8),
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
            elevation: 0,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(28),
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
                      Icon(icon, size: 20, color: Colors.white),
                      const SizedBox(width: 10),
                    ],
                    Text(text, style: buttonText),
                  ],
                ),
        ),
      ),
    );
  }

  /// Outline button — frosted glass pill
  static Widget outlineButton({
    required String text,
    required VoidCallback onPressed,
    IconData? icon,
  }) {
    return SizedBox(
      width: double.infinity,
      height: 52,
      child: ClipRRect(
        borderRadius: BorderRadius.circular(26),
        child: BackdropFilter(
          filter: ImageFilter.blur(sigmaX: 12, sigmaY: 12),
          child: OutlinedButton(
            onPressed: onPressed,
            style: OutlinedButton.styleFrom(
              foregroundColor: textOnGlass,
              backgroundColor: glassFill,
              elevation: 0,
              side: const BorderSide(color: glassBorder, width: 1),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(26),
              ),
            ),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                if (icon != null) ...[
                  Icon(icon, size: 18, color: textOnGlass),
                  const SizedBox(width: 8),
                ],
                Text(
                  text,
                  style: const TextStyle(
                    fontFamily: fontFamily,
                    fontSize: 15,
                    fontWeight: FontWeight.w600,
                    color: textOnGlass,
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  /// Input field — frosted glass style
  static Widget inputField({
    required TextEditingController controller,
    required String hint,
    IconData? prefixIcon,
    bool obscure = false,
    Widget? suffix,
    TextInputType? keyboardType,
    TextInputAction? textInputAction,
    String? errorText,
    ValueChanged<String>? onChanged,
  }) {
    final hasError = errorText != null && errorText.isNotEmpty;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        ClipRRect(
          borderRadius: BorderRadius.circular(16),
          child: BackdropFilter(
            filter: ImageFilter.blur(sigmaX: 10, sigmaY: 10),
            child: Container(
              height: 54,
              decoration: BoxDecoration(
                color: glassInputFill,
                borderRadius: BorderRadius.circular(16),
                border: Border.all(
                  color: hasError
                      ? GlassTheme.accentRed.withOpacity(0.7)
                      : glassBorder,
                  width: hasError ? 1.5 : 1,
                ),
              ),
              child: TextField(
                controller: controller,
                obscureText: obscure,
                keyboardType: keyboardType,
                textInputAction: textInputAction,
                onChanged: onChanged,
                style: const TextStyle(
                  fontFamily: fontFamily,
                  fontSize: 15,
                  color: textOnGlass,
                ),
                cursorColor: primaryLight,
                decoration: InputDecoration(
                  hintText: hint,
                  hintStyle: const TextStyle(
                    fontFamily: fontFamily,
                    fontSize: 15,
                    color: textOnGlassMuted,
                  ),
                  border: InputBorder.none,
                  prefixIcon: prefixIcon != null
                      ? Icon(prefixIcon, size: 20, color: textOnGlassMuted)
                      : null,
                  suffixIcon: suffix,
                  contentPadding: EdgeInsets.symmetric(
                    horizontal: prefixIcon != null ? 0 : 18,
                    vertical: 16,
                  ),
                ),
              ),
            ),
          ),
        ),
        if (hasError) ...[
          const SizedBox(height: 6),
          Text(
            errorText,
            style: TextStyle(
              fontFamily: fontFamily,
              fontSize: 12,
              fontWeight: FontWeight.w500,
              color: GlassTheme.accentRed.withOpacity(0.9),
            ),
          ),
        ],
      ],
    );
  }

  /// "hoặc" divider — glass style
  static Widget orDivider() {
    return const Row(
      children: [
        Expanded(
          child: Divider(color: glassBorder, thickness: 1),
        ),
        Padding(
          padding: EdgeInsets.symmetric(horizontal: 16),
          child: Text(
            'hoặc',
            style: TextStyle(
              fontFamily: fontFamily,
              fontSize: 13,
              fontWeight: FontWeight.w500,
              color: textOnGlassMuted,
            ),
          ),
        ),
        Expanded(
          child: Divider(color: glassBorder, thickness: 1),
        ),
      ],
    );
  }

  /// Label with icon
  static Widget fieldLabel(String text, {IconData? icon}) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Row(
        children: [
          if (icon != null) ...[
            Icon(icon, size: 16, color: textOnGlassSecondary),
            const SizedBox(width: 6),
          ],
          Text(text, style: label),
        ],
      ),
    );
  }

  /// Footer badges — glass style
  static Widget footerBadges() {
    return const Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        Icon(Icons.shield_outlined, size: 15, color: textOnGlassMuted),
        SizedBox(width: 5),
        Text('Bảo mật HIPAA', style: caption),
        SizedBox(width: 20),
        Icon(Icons.favorite_outline, size: 15, color: textOnGlassMuted),
        SizedBox(width: 5),
        Text('Miễn phí sử dụng', style: caption),
      ],
    );
  }
}
