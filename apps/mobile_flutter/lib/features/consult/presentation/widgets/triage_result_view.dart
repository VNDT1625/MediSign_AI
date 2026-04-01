import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import '../../../../core/models/communication_mode.dart';

/// Triage Result View — displays AI consultation results using
/// PICTOGRAM-FIRST design. Traffic light system (🟢🟡🔴) + action icons.
///
/// Designed for ALL users:
/// - Deaf/mute/illiterate: Understand via COLOR + ICON + EMOJI
/// - Blind: Full Semantics labels for TalkBack/VoiceOver
/// - Standard: Text details available
class TriageResultView extends StatelessWidget {
  const TriageResultView({
    super.key,
    required this.level,
    required this.selectedRegions,
    required this.selectedSymptoms,
    required this.severity,
    required this.duration,
    required this.adviceItems,
    required this.onGoHome,
    required this.onCallEmergency,
  });

  final TriageLevel level;
  final Set<BodyRegion> selectedRegions;
  final Set<SymptomIcon> selectedSymptoms;
  final Severity? severity;
  final SymptomDuration? duration;
  final List<AdviceItem> adviceItems;
  final VoidCallback onGoHome;
  final VoidCallback onCallEmergency;

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.fromLTRB(20, 16, 20, 32),
      child: Column(
        children: [
          // ── Traffic Light Card ──
          _buildTriageBadge(),
          const SizedBox(height: 20),

          // ── Your Symptoms Summary (emoji only) ──
          _buildSymptomSummary(),
          const SizedBox(height: 20),

          // ── Action Card ──
          _buildActionCard(),
          const SizedBox(height: 16),

          // ── Advice Cards (pictogram-first) ──
          ...adviceItems.map((a) => Padding(
                padding: const EdgeInsets.only(bottom: 10),
                child: _buildAdviceCard(a),
              )),
          const SizedBox(height: 16),

          // ── Emergency button (always visible) ──
          _buildEmergencyButton(),
          const SizedBox(height: 12),

          // ── Home button ──
          _buildHomeButton(),
        ],
      ),
    );
  }

  Widget _buildTriageBadge() {
    return Semantics(
      label: 'Kết quả đánh giá: ${level.label}',
      child: Container(
        width: double.infinity,
        padding: const EdgeInsets.symmetric(vertical: 28, horizontal: 24),
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [
              level.color.withOpacity(0.25),
              level.color.withOpacity(0.08),
            ],
          ),
          borderRadius: BorderRadius.circular(24),
          border: Border.all(
            color: level.color.withOpacity(0.5),
            width: 2,
          ),
          boxShadow: [
            BoxShadow(
              color: level.color.withOpacity(0.3),
              blurRadius: 24,
              spreadRadius: 2,
            ),
          ],
        ),
        child: Column(
          children: [
            // Big traffic light emoji
            Text(
              level.emoji,
              style: const TextStyle(fontSize: 64),
            ),
            const SizedBox(height: 12),

            // Level text
            Text(
              level.label,
              textAlign: TextAlign.center,
              style: TextStyle(
                fontFamily: 'Outfit',
                fontSize: 20,
                fontWeight: FontWeight.w700,
                color: level.color,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSymptomSummary() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF1E293B),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.white.withOpacity(0.06)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header with icon
          const Row(
            children: [
              Text('📋', style: TextStyle(fontSize: 20)),
              SizedBox(width: 8),
              Text(
                'Triệu chứng của bạn',
                style: TextStyle(
                  fontFamily: 'Outfit',
                  fontSize: 15,
                  fontWeight: FontWeight.w600,
                  color: Colors.white70,
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),

          // Region emojis
          if (selectedRegions.isNotEmpty) ...[
            Wrap(
              spacing: 8,
              runSpacing: 6,
              children: selectedRegions.map((r) {
                return Semantics(
                  label: r.label,
                  child: Container(
                    padding:
                        const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                    decoration: BoxDecoration(
                      color: const Color(0xFFEF4444).withOpacity(0.12),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Text(r.emoji, style: const TextStyle(fontSize: 18)),
                        const SizedBox(width: 4),
                        Text(
                          r.label,
                          style: const TextStyle(
                            fontFamily: 'Outfit',
                            fontSize: 12,
                            color: Color(0xFFFCA5A5),
                          ),
                        ),
                      ],
                    ),
                  ),
                );
              }).toList(),
            ),
            const SizedBox(height: 8),
          ],

          // Symptom emojis
          if (selectedSymptoms.isNotEmpty)
            Wrap(
              spacing: 8,
              runSpacing: 6,
              children: selectedSymptoms.map((s) {
                return Semantics(
                  label: s.label,
                  child: Container(
                    padding:
                        const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                    decoration: BoxDecoration(
                      color: const Color(0xFF14B8A6).withOpacity(0.12),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Text(s.emoji, style: const TextStyle(fontSize: 18)),
                        const SizedBox(width: 4),
                        Text(
                          s.label,
                          style: const TextStyle(
                            fontFamily: 'Outfit',
                            fontSize: 12,
                            color: Color(0xFF5EEAD4),
                          ),
                        ),
                      ],
                    ),
                  ),
                );
              }).toList(),
            ),

          // Severity + Duration
          if (severity != null || duration != null) ...[
            const SizedBox(height: 8),
            Row(
              children: [
                if (severity != null) ...[
                  Text(severity!.emoji, style: const TextStyle(fontSize: 22)),
                  const SizedBox(width: 4),
                  Text(
                    severity!.label,
                    style: TextStyle(
                      fontFamily: 'Outfit',
                      fontSize: 13,
                      color: severity!.color,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  const SizedBox(width: 16),
                ],
                if (duration != null) ...[
                  Text(duration!.emoji, style: const TextStyle(fontSize: 22)),
                  const SizedBox(width: 4),
                  Text(
                    duration!.label,
                    style: const TextStyle(
                      fontFamily: 'Outfit',
                      fontSize: 13,
                      color: Color(0xFF93C5FD),
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ],
              ],
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildActionCard() {
    return Semantics(
      label: 'Hành động: ${level.actionLabel}',
      child: GestureDetector(
        onTap: () {
          HapticFeedback.mediumImpact();
          if (level == TriageLevel.red) {
            onCallEmergency();
          }
        },
        child: Container(
          width: double.infinity,
          padding: const EdgeInsets.all(20),
          decoration: BoxDecoration(
            gradient: LinearGradient(
              colors: [
                level.color.withOpacity(0.2),
                level.color.withOpacity(0.08),
              ],
            ),
            borderRadius: BorderRadius.circular(20),
            border: Border.all(
              color: level.color.withOpacity(0.4),
              width: 1.5,
            ),
          ),
          child: Row(
            children: [
              // Action icon
              Container(
                width: 56,
                height: 56,
                decoration: BoxDecoration(
                  color: level.color.withOpacity(0.2),
                  borderRadius: BorderRadius.circular(16),
                ),
                child: Center(
                  child: Text(
                    level.actionIcon,
                    style: const TextStyle(fontSize: 28),
                  ),
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      level.actionLabel,
                      style: TextStyle(
                        fontFamily: 'Outfit',
                        fontSize: 16,
                        fontWeight: FontWeight.w700,
                        color: level.color,
                      ),
                    ),
                    if (level == TriageLevel.red) ...[
                      const SizedBox(height: 4),
                      const Text(
                        '📞 Nhấn để gọi ngay',
                        style: TextStyle(
                          fontFamily: 'Outfit',
                          fontSize: 13,
                          color: Color(0xFFFCA5A5),
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ],
                  ],
                ),
              ),
              if (level == TriageLevel.red)
                const Icon(
                  Icons.call,
                  color: Color(0xFFEF4444),
                  size: 28,
                ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildAdviceCard(AdviceItem advice) {
    return Semantics(
      label: '${advice.title}. ${advice.description}',
      child: Container(
        width: double.infinity,
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: const Color(0xFF1E293B),
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: Colors.white.withOpacity(0.06)),
        ),
        child: Row(
          children: [
            // Icon
            Container(
              width: 48,
              height: 48,
              decoration: BoxDecoration(
                color: advice.color.withOpacity(0.15),
                borderRadius: BorderRadius.circular(14),
              ),
              child: Center(
                child: Text(
                  advice.emoji,
                  style: const TextStyle(fontSize: 24),
                ),
              ),
            ),
            const SizedBox(width: 14),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    advice.title,
                    style: const TextStyle(
                      fontFamily: 'Outfit',
                      fontSize: 14,
                      fontWeight: FontWeight.w600,
                      color: Colors.white,
                    ),
                  ),
                  const SizedBox(height: 2),
                  Text(
                    advice.description,
                    style: const TextStyle(
                      fontFamily: 'Outfit',
                      fontSize: 12,
                      color: Colors.white54,
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

  Widget _buildEmergencyButton() {
    return Semantics(
      label: 'Gọi cấp cứu 115',
      button: true,
      child: GestureDetector(
        onTap: () {
          HapticFeedback.heavyImpact();
          onCallEmergency();
        },
        child: Container(
          width: double.infinity,
          padding: const EdgeInsets.symmetric(vertical: 16),
          decoration: BoxDecoration(
            color: const Color(0xFFEF4444).withOpacity(0.15),
            borderRadius: BorderRadius.circular(16),
            border: Border.all(
              color: const Color(0xFFEF4444).withOpacity(0.4),
              width: 1.5,
            ),
          ),
          child: const Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Text('🆘', style: TextStyle(fontSize: 22)),
              SizedBox(width: 8),
              Text(
                'Gọi 115',
                style: TextStyle(
                  fontFamily: 'Outfit',
                  fontSize: 16,
                  fontWeight: FontWeight.w700,
                  color: Color(0xFFFCA5A5),
                ),
              ),
              SizedBox(width: 8),
              Icon(Icons.call, color: Color(0xFFFCA5A5), size: 20),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildHomeButton() {
    return Semantics(
      label: 'Về trang chủ',
      button: true,
      child: GestureDetector(
        onTap: () {
          HapticFeedback.lightImpact();
          onGoHome();
        },
        child: Container(
          width: double.infinity,
          padding: const EdgeInsets.symmetric(vertical: 14),
          decoration: BoxDecoration(
            color: Colors.white.withOpacity(0.06),
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: Colors.white.withOpacity(0.1)),
          ),
          child: const Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Text('🏠', style: TextStyle(fontSize: 20)),
              SizedBox(width: 8),
              Text(
                'Về trang chủ',
                style: TextStyle(
                  fontFamily: 'Outfit',
                  fontSize: 15,
                  fontWeight: FontWeight.w600,
                  color: Colors.white70,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

/// Data class for advice items in triage results.
class AdviceItem {
  const AdviceItem({
    required this.emoji,
    required this.title,
    required this.description,
    required this.color,
  });

  final String emoji;
  final String title;
  final String description;
  final Color color;
}
