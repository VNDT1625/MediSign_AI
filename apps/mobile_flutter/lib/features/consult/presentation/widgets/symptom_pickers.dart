import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import '../../../../core/models/communication_mode.dart';

/// Symptom Icon Picker — grid of large, tappable pictogram icons.
/// Designed for deaf/mute/illiterate users: understand symptoms through
/// EMOJI + COLOR, zero text reading required.
///
/// Features:
/// - Large emoji icons (≥ 64px tap targets)
/// - Multi-select with visual check mark
/// - Haptic feedback on selection
/// - Semantics labels for screen readers
/// - Color-coded categories
class SymptomIconPicker extends StatelessWidget {
  const SymptomIconPicker({
    super.key,
    required this.selectedSymptoms,
    required this.onSymptomsChanged,
  });

  final Set<SymptomIcon> selectedSymptoms;
  final ValueChanged<Set<SymptomIcon>> onSymptomsChanged;

  void _toggleSymptom(SymptomIcon symptom) {
    HapticFeedback.lightImpact();
    final updated = Set<SymptomIcon>.from(selectedSymptoms);
    if (updated.contains(symptom)) {
      updated.remove(symptom);
    } else {
      updated.add(symptom);
    }
    onSymptomsChanged(updated);
  }

  @override
  Widget build(BuildContext context) {
    return GridView.builder(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 4,
        mainAxisSpacing: 10,
        crossAxisSpacing: 10,
        childAspectRatio: 0.85,
      ),
      itemCount: SymptomIcon.values.length,
      itemBuilder: (context, index) {
        final symptom = SymptomIcon.values[index];
        final isSelected = selectedSymptoms.contains(symptom);

        return Semantics(
          label: '${symptom.label}. ${isSelected ? "Đã chọn" : "Chưa chọn"}.',
          button: true,
          child: GestureDetector(
            onTap: () => _toggleSymptom(symptom),
            child: AnimatedContainer(
              duration: const Duration(milliseconds: 200),
              curve: Curves.easeOut,
              decoration: BoxDecoration(
                color: isSelected
                    ? const Color(0xFF0D9488).withOpacity(0.25)
                    : const Color(0xFF1E293B),
                borderRadius: BorderRadius.circular(16),
                border: Border.all(
                  color: isSelected
                      ? const Color(0xFF14B8A6)
                      : Colors.white.withOpacity(0.08),
                  width: isSelected ? 2 : 1,
                ),
                boxShadow: isSelected
                    ? [
                        BoxShadow(
                          color: const Color(0xFF14B8A6).withOpacity(0.3),
                          blurRadius: 12,
                          spreadRadius: 1,
                        ),
                      ]
                    : [],
              ),
              child: Stack(
                children: [
                  Center(
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Text(
                          symptom.emoji,
                          style: const TextStyle(fontSize: 32),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          symptom.label,
                          textAlign: TextAlign.center,
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                          style: TextStyle(
                            fontFamily: 'Outfit',
                            fontSize: 11,
                            fontWeight: FontWeight.w500,
                            color: isSelected
                                ? const Color(0xFF5EEAD4)
                                : Colors.white60,
                          ),
                        ),
                      ],
                    ),
                  ),

                  // Check mark when selected
                  if (isSelected)
                    Positioned(
                      top: 4,
                      right: 4,
                      child: Container(
                        width: 20,
                        height: 20,
                        decoration: const BoxDecoration(
                          color: Color(0xFF14B8A6),
                          shape: BoxShape.circle,
                        ),
                        child: const Icon(
                          Icons.check,
                          size: 14,
                          color: Colors.white,
                        ),
                      ),
                    ),
                ],
              ),
            ),
          ),
        );
      },
    );
  }
}

/// Severity Picker — 4 large emoji faces representing pain levels.
/// Zero text required. Universal understanding through facial expressions.
class SeverityPicker extends StatelessWidget {
  const SeverityPicker({
    super.key,
    required this.selected,
    required this.onChanged,
  });

  final Severity? selected;
  final ValueChanged<Severity> onChanged;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 20),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceEvenly,
        children: Severity.values.map((s) {
          final isActive = selected == s;
          return Semantics(
            label: '${s.label}. ${isActive ? "Đã chọn" : "Chưa chọn"}.',
            button: true,
            child: GestureDetector(
              onTap: () {
                HapticFeedback.mediumImpact();
                onChanged(s);
              },
              child: AnimatedContainer(
                duration: const Duration(milliseconds: 200),
                width: 72,
                height: 90,
                decoration: BoxDecoration(
                  color: isActive
                      ? s.color.withOpacity(0.2)
                      : const Color(0xFF1E293B),
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(
                    color: isActive ? s.color : Colors.white.withOpacity(0.08),
                    width: isActive ? 2.5 : 1,
                  ),
                  boxShadow: isActive
                      ? [
                          BoxShadow(
                            color: s.color.withOpacity(0.35),
                            blurRadius: 16,
                            spreadRadius: 2,
                          ),
                        ]
                      : [],
                ),
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Text(
                      s.emoji,
                      style: TextStyle(fontSize: isActive ? 36 : 30),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      s.label,
                      style: TextStyle(
                        fontFamily: 'Outfit',
                        fontSize: 11,
                        fontWeight: FontWeight.w600,
                        color: isActive ? s.color : Colors.white54,
                      ),
                    ),
                  ],
                ),
              ),
            ),
          );
        }).toList(),
      ),
    );
  }
}

/// Duration Picker — visual cards showing how long symptoms have lasted.
/// Uses numbers + calendar emoji, minimal text.
class DurationPicker extends StatelessWidget {
  const DurationPicker({
    super.key,
    required this.selected,
    required this.onChanged,
  });

  final SymptomDuration? selected;
  final ValueChanged<SymptomDuration> onChanged;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16),
      child: Row(
        children: SymptomDuration.values.map((d) {
          final isActive = selected == d;
          return Expanded(
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 4),
              child: Semantics(
                label: '${d.label}. ${isActive ? "Đã chọn" : "Chưa chọn"}.',
                button: true,
                child: GestureDetector(
                  onTap: () {
                    HapticFeedback.lightImpact();
                    onChanged(d);
                  },
                  child: AnimatedContainer(
                    duration: const Duration(milliseconds: 200),
                    height: 88,
                    decoration: BoxDecoration(
                      color: isActive
                          ? const Color(0xFF3B82F6).withOpacity(0.2)
                          : const Color(0xFF1E293B),
                      borderRadius: BorderRadius.circular(16),
                      border: Border.all(
                        color: isActive
                            ? const Color(0xFF3B82F6)
                            : Colors.white.withOpacity(0.08),
                        width: isActive ? 2 : 1,
                      ),
                      boxShadow: isActive
                          ? [
                              BoxShadow(
                                color: const Color(0xFF3B82F6).withOpacity(0.3),
                                blurRadius: 12,
                              ),
                            ]
                          : [],
                    ),
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        // Big number or emoji
                        Text(
                          d.visualLabel,
                          style: TextStyle(
                            fontFamily: 'Outfit',
                            fontSize: 22,
                            fontWeight: FontWeight.w800,
                            color: isActive
                                ? const Color(0xFF93C5FD)
                                : Colors.white70,
                          ),
                        ),
                        const SizedBox(height: 2),
                        Text(
                          d.emoji,
                          style: const TextStyle(fontSize: 16),
                        ),
                        const SizedBox(height: 2),
                        Text(
                          d.label,
                          textAlign: TextAlign.center,
                          style: TextStyle(
                            fontFamily: 'Outfit',
                            fontSize: 10,
                            fontWeight: FontWeight.w500,
                            color: isActive
                                ? const Color(0xFF93C5FD)
                                : Colors.white38,
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            ),
          );
        }).toList(),
      ),
    );
  }
}
