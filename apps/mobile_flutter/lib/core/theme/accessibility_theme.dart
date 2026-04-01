import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

/// Accessibility-focused theme extension for MediSign AI.
///
/// Provides comprehensive accessibility features following:
/// - WCAG 2.1 AA Guidelines
/// - iOS Accessibility Guidelines
/// - Android Accessibility Guidelines
///
/// Features:
/// - Minimum touch targets (48x48dp)
/// - Semantic labels for screen readers
/// - Font scaling support
/// - High contrast support
/// - Haptic feedback
class MediSignAccessibility {
  MediSignAccessibility._();

  // TOUCH TARGETS (WCAG 2.1 - 2.5.5)
  static const double minTouchTarget = 48.0;
  static const double touchTargetLarge = 56.0;
  static const double iconButtonSize = 48.0;

  // FONT SIZES (WCAG 2.1 - 1.4.4)
  static const double fontSizeBase = 17.0;
  static const double fontSizeMin = 15.0;
  static const double fontSizeTitle = 24.0;
  static const double fontSizeLargeTitle = 28.0;
  static const double fontSizeCaption = 13.0;

  // SPACING
  static const double spacingXS = 4.0;
  static const double spacingS = 8.0;
  static const double spacingM = 12.0;
  static const double spacingL = 16.0;
  static const double spacingXL = 24.0;
  static const double spacingXXL = 32.0;

  // SEMANTIC HELPERS
  static Widget label({
    required String label,
    required Widget child,
    bool isHeader = false,
    bool isSelected = false,
    bool isEnabled = true,
    bool isButton = false,
    bool isTextField = false,
  }) {
    return Semantics(
      label: label,
      header: isHeader,
      selected: isSelected,
      enabled: isEnabled,
      button: isButton,
      textField: isTextField,
      child: child,
    );
  }

  static Widget button({
    required String label,
    required Widget child,
    bool isEnabled = true,
  }) {
    return Semantics(
      label: label,
      button: true,
      enabled: isEnabled,
      child: child,
    );
  }

  // ACCESSIBLE WIDGETS

  /// Accessible text field with proper labels
  static Widget textField({
    required String label,
    required String hint,
    required TextEditingController controller,
    TextInputType keyboardType = TextInputType.text,
    bool obscureText = false,
    String? errorText,
    Widget? prefixIcon,
    Widget? suffix,
    ValueChanged<String>? onChanged,
    ValueChanged<String>? onSubmitted,
    bool autofocus = false,
    int maxLines = 1,
    bool enabled = true,
  }) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      mainAxisSize: MainAxisSize.min,
      children: [
        Semantics(
          label: '$label, text field',
          textField: true,
          child: Text(
            label,
            style: const TextStyle(
              fontSize: fontSizeBase,
              fontWeight: FontWeight.w600,
              color: Colors.black87,
            ),
          ),
        ),
        const SizedBox(height: spacingS),
        Semantics(
          label: '$label: $hint',
          textField: true,
          enabled: enabled,
          child: TextField(
            controller: controller,
            keyboardType: keyboardType,
            obscureText: obscureText,
            autofocus: autofocus,
            maxLines: maxLines,
            enabled: enabled,
            style: const TextStyle(fontSize: fontSizeBase),
            onChanged: onChanged,
            onSubmitted: onSubmitted,
            decoration: InputDecoration(
              hintText: hint,
              errorText: errorText,
              prefixIcon: prefixIcon,
              suffix: suffix,
              filled: true,
              fillColor: enabled ? Colors.grey.shade50 : Colors.grey.shade100,
              contentPadding: const EdgeInsets.symmetric(
                horizontal: spacingL,
                vertical: spacingM,
              ),
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
                borderSide: BorderSide(color: Colors.grey.shade300),
              ),
              enabledBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
                borderSide: BorderSide(color: Colors.grey.shade300),
              ),
              focusedBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
                borderSide:
                    const BorderSide(color: Color(0xFF0D9488), width: 2),
              ),
              errorBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
                borderSide: const BorderSide(color: Colors.red),
              ),
            ),
          ),
        ),
        if (errorText != null) ...[
          const SizedBox(height: spacingXS),
          Semantics(
            label: 'Error: $errorText',
            child: Text(
              errorText,
              style: const TextStyle(
                fontSize: fontSizeCaption,
                color: Colors.red,
              ),
            ),
          ),
        ],
      ],
    );
  }

  /// Accessible primary button
  static Widget primaryButton({
    required String label,
    required VoidCallback? onPressed,
    bool isLoading = false,
    Widget? icon,
    Widget? child,
  }) {
    final buttonChild = isLoading
        ? const SizedBox(
            width: 24,
            height: 24,
            child: CircularProgressIndicator(
              strokeWidth: 2.5,
              color: Colors.white,
            ),
          )
        : child ??
            Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                if (icon != null) ...[
                  icon,
                  const SizedBox(width: spacingS),
                ],
                Text(
                  label,
                  style: const TextStyle(
                    fontSize: fontSizeBase,
                    fontWeight: FontWeight.w600,
                    color: Colors.white,
                  ),
                ),
              ],
            );

    return Semantics(
      label: label,
      button: true,
      enabled: onPressed != null && !isLoading,
      child: SizedBox(
        height: touchTargetLarge,
        child: ElevatedButton(
          onPressed: onPressed != null && !isLoading
              ? () {
                  HapticFeedback.mediumImpact();
                  onPressed();
                }
              : null,
          style: ElevatedButton.styleFrom(
            backgroundColor: const Color(0xFF0D9488),
            foregroundColor: Colors.white,
            disabledBackgroundColor: Colors.grey.shade300,
            elevation: 0,
            padding: const EdgeInsets.symmetric(horizontal: spacingXL),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(12),
            ),
          ),
          child: buttonChild,
        ),
      ),
    );
  }

  /// Accessible secondary button
  static Widget secondaryButton({
    required String label,
    required VoidCallback? onPressed,
    Widget? icon,
    Color? color,
  }) {
    final buttonColor = color ?? const Color(0xFF0D9488);

    return Semantics(
      label: label,
      button: true,
      enabled: onPressed != null,
      child: SizedBox(
        height: minTouchTarget,
        child: OutlinedButton(
          onPressed: onPressed != null
              ? () {
                  HapticFeedback.lightImpact();
                  onPressed();
                }
              : null,
          style: OutlinedButton.styleFrom(
            foregroundColor: buttonColor,
            side: BorderSide(color: buttonColor, width: 1.5),
            padding: const EdgeInsets.symmetric(horizontal: spacingL),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(12),
            ),
          ),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              if (icon != null) ...[
                icon,
                const SizedBox(width: spacingS),
              ],
              Text(
                label,
                style: TextStyle(
                  fontSize: fontSizeBase,
                  fontWeight: FontWeight.w600,
                  color: buttonColor,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  /// Accessible text button
  static Widget textButton({
    required String label,
    required VoidCallback? onPressed,
    Color? color,
  }) {
    final buttonColor = color ?? const Color(0xFF0D9488);

    return Semantics(
      label: label,
      button: true,
      enabled: onPressed != null,
      child: TextButton(
        onPressed: onPressed != null
            ? () {
                HapticFeedback.selectionClick();
                onPressed();
              }
            : null,
        child: Text(
          label,
          style: TextStyle(
            fontSize: fontSizeBase,
            fontWeight: FontWeight.w600,
            color: buttonColor,
          ),
        ),
      ),
    );
  }

  /// Accessible icon button
  static Widget iconButton({
    required String semanticLabel,
    required IconData icon,
    VoidCallback? onPressed,
    Color? color,
    double size = 24,
    String? tooltip,
  }) {
    final button = Semantics(
      label: semanticLabel,
      button: true,
      enabled: onPressed != null,
      child: IconButton(
        onPressed: onPressed != null
            ? () {
                HapticFeedback.lightImpact();
                onPressed();
              }
            : null,
        icon: Icon(icon, size: size),
        color: color ?? Colors.black87,
        constraints: const BoxConstraints(
          minWidth: iconButtonSize,
          minHeight: iconButtonSize,
        ),
      ),
    );

    if (tooltip != null) {
      return Tooltip(
        message: tooltip,
        child: button,
      );
    }

    return button;
  }

  /// Accessible list tile
  static Widget listTile({
    required String title,
    String? subtitle,
    String? hint,
    VoidCallback? onTap,
    Widget? leading,
    Widget? trailing,
    bool isSelected = false,
    bool enabled = true,
  }) {
    final labelList = <String>[title];
    if (subtitle != null) labelList.add(subtitle);
    if (hint != null) labelList.add(hint);
    final labelStr = labelList.join(', ');

    return Semantics(
      label: labelStr,
      button: onTap != null,
      selected: isSelected,
      enabled: enabled,
      child: ListTile(
        onTap: enabled && onTap != null
            ? () {
                HapticFeedback.selectionClick();
                onTap();
              }
            : null,
        enabled: enabled,
        selected: isSelected,
        contentPadding: const EdgeInsets.symmetric(
          horizontal: spacingL,
          vertical: spacingS,
        ),
        leading: leading,
        title: Text(
          title,
          style: TextStyle(
            fontSize: fontSizeBase,
            fontWeight: FontWeight.w500,
            color: enabled ? Colors.black87 : Colors.grey,
          ),
        ),
        subtitle: subtitle != null
            ? Text(
                subtitle,
                style: TextStyle(
                  fontSize: fontSizeCaption,
                  color: enabled ? Colors.grey.shade600 : Colors.grey,
                ),
              )
            : null,
        trailing: trailing,
      ),
    );
  }

  /// Accessible checkbox
  static Widget checkbox({
    required String label,
    required bool value,
    required ValueChanged<bool?> onChanged,
    bool enabled = true,
  }) {
    return Semantics(
      label: label,
      checked: value,
      enabled: enabled,
      child: CheckboxListTile(
        value: value,
        onChanged: enabled
            ? (newValue) {
                HapticFeedback.selectionClick();
                onChanged(newValue);
              }
            : null,
        title: Text(
          label,
          style: TextStyle(
            fontSize: fontSizeBase,
            color: enabled ? Colors.black87 : Colors.grey,
          ),
        ),
        controlAffinity: ListTileControlAffinity.leading,
        contentPadding: EdgeInsets.zero,
      ),
    );
  }

  /// Accessible switch
  static Widget switchTile({
    required String label,
    required bool value,
    required ValueChanged<bool> onChanged,
    String? subtitle,
    bool enabled = true,
  }) {
    return Semantics(
      label: label,
      enabled: enabled,
      child: SwitchListTile(
        value: value,
        onChanged: enabled
            ? (newValue) {
                HapticFeedback.selectionClick();
                onChanged(newValue);
              }
            : null,
        title: Text(
          label,
          style: TextStyle(
            fontSize: fontSizeBase,
            fontWeight: FontWeight.w500,
            color: enabled ? Colors.black87 : Colors.grey,
          ),
        ),
        subtitle: subtitle != null
            ? Text(
                subtitle,
                style: TextStyle(
                  fontSize: fontSizeCaption,
                  color: enabled ? Colors.grey.shade600 : Colors.grey,
                ),
              )
            : null,
        contentPadding: EdgeInsets.zero,
      ),
    );
  }

  // TITLE WIDGETS
  static Widget largeTitle(
    String text, {
    FontWeight fontWeight = FontWeight.bold,
    Color? color,
  }) {
    return Semantics(
      header: true,
      child: Text(
        text,
        style: TextStyle(
          fontSize: fontSizeLargeTitle,
          fontWeight: fontWeight,
          color: color ?? Colors.black87,
          height: 1.2,
        ),
      ),
    );
  }

  static Widget title(
    String text, {
    FontWeight fontWeight = FontWeight.w600,
    Color? color,
  }) {
    return Semantics(
      header: true,
      child: Text(
        text,
        style: TextStyle(
          fontSize: fontSizeTitle,
          fontWeight: fontWeight,
          color: color ?? Colors.black87,
          height: 1.3,
        ),
      ),
    );
  }

  static Widget body(
    String text, {
    Color? color,
    TextAlign? textAlign,
  }) {
    return Semantics(
      child: Text(
        text,
        style: TextStyle(
          fontSize: fontSizeBase,
          color: color ?? Colors.black87,
          height: 1.5,
        ),
        textAlign: textAlign,
      ),
    );
  }

  static Widget caption(
    String text, {
    Color? color,
  }) {
    return Semantics(
      child: Text(
        text,
        style: TextStyle(
          fontSize: fontSizeCaption,
          color: color ?? Colors.grey.shade600,
        ),
      ),
    );
  }

  // STATUS INDICATORS
  static Widget statusBadge({
    required String label,
    required Color color,
    Color? backgroundColor,
  }) {
    return Semantics(
      label: 'Status: $label',
      child: Container(
        padding: const EdgeInsets.symmetric(
          horizontal: spacingM,
          vertical: spacingXS,
        ),
        decoration: BoxDecoration(
          color: backgroundColor ?? color.withValues(alpha: 0.12),
          borderRadius: BorderRadius.circular(999),
        ),
        child: Text(
          label,
          style: TextStyle(
            fontSize: fontSizeCaption,
            fontWeight: FontWeight.w600,
            color: color,
          ),
        ),
      ),
    );
  }

  static Widget loading({
    double size = 40,
    String? label,
  }) {
    return Semantics(
      label: label ?? 'Loading',
      liveRegion: true,
      child: SizedBox(
        width: size,
        height: size,
        child: const CircularProgressIndicator(
          strokeWidth: 3,
          color: Color(0xFF0D9488),
        ),
      ),
    );
  }

  // FORMATTED TEXT
  static Widget link({
    required String text,
    required VoidCallback? onPressed,
    Color? color,
  }) {
    return Semantics(
      label: 'Link: $text',
      button: true,
      enabled: onPressed != null,
      child: InkWell(
        onTap: onPressed != null
            ? () {
                HapticFeedback.selectionClick();
                onPressed();
              }
            : null,
        child: Text(
          text,
          style: TextStyle(
            fontSize: fontSizeBase,
            fontWeight: FontWeight.w600,
            color: color ?? const Color(0xFF0D9488),
            decoration: TextDecoration.underline,
          ),
        ),
      ),
    );
  }
}
