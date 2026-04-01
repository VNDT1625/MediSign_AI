import 'package:flutter/material.dart';

class RichTextSegment {
  final String text;
  final RichTextStyle style;
  final String? aiContent;

  const RichTextSegment({
    required this.text,
    required this.style,
    this.aiContent,
  });

  String get plainTextForAI => aiContent ?? text;
}

class RichTextStyle {
  final bool isBold;
  final bool isItalic;
  final bool isUnderline;
  final bool isHighlight;
  final double fontSize;
  final Color? highlightColor;
  final Color? textColor;

  const RichTextStyle({
    this.isBold = false,
    this.isItalic = false,
    this.isUnderline = false,
    this.isHighlight = false,
    this.fontSize = 14.0,
    this.highlightColor,
    this.textColor,
  });

  static const normal = RichTextStyle();
  static const bold = RichTextStyle(isBold: true);
  static const highlight =
      RichTextStyle(isHighlight: true, highlightColor: Color(0xFFFFFF00));
  static const heading = RichTextStyle(fontSize: 20.0, isBold: true);
  static const subheading = RichTextStyle(fontSize: 16.0, isBold: true);
  static const small = RichTextStyle(fontSize: 12.0);

  TextStyle toTextStyle(Color defaultColor) {
    return TextStyle(
      fontWeight: isBold ? FontWeight.bold : FontWeight.normal,
      fontStyle: isItalic ? FontStyle.italic : FontStyle.normal,
      decoration: isUnderline ? TextDecoration.underline : null,
      fontSize: fontSize,
      color: textColor ?? defaultColor,
      backgroundColor:
          isHighlight ? (highlightColor ?? const Color(0xFFFFFF00)) : null,
    );
  }
}

class RichJournalContent {
  final List<RichTextSegment> segments;

  const RichJournalContent({required this.segments});

  const RichJournalContent.empty() : segments = const [];

  factory RichJournalContent.fromPlainText(String text) {
    return RichJournalContent(
      segments: [RichTextSegment(text: text, style: RichTextStyle.normal)],
    );
  }

  String get plainTextForAI {
    return segments.map((s) => s.plainTextForAI).join(' ');
  }

  String get plainTextForDisplay {
    return segments.map((s) => s.text).join(' ');
  }

  int get characterCount => segments.fold(0, (sum, s) => sum + s.text.length);
}

class RichTextOption {
  final String icon;
  final String label;
  final RichTextStyle style;

  const RichTextOption({
    required this.icon,
    required this.label,
    required this.style,
  });

  static const List<RichTextOption> options = [
    RichTextOption(icon: 'B', label: 'Dam', style: RichTextStyle.bold),
    RichTextOption(icon: 'H', label: 'ToMau', style: RichTextStyle.highlight),
    RichTextOption(icon: 'T', label: 'TieuDe', style: RichTextStyle.heading),
    RichTextOption(icon: 'S', label: 'Nho', style: RichTextStyle.small),
  ];
}
