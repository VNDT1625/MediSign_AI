
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import '../../../../core/models/communication_mode.dart';

/// Interactive Body Map — users TAP on body regions to indicate pain locations.
/// Designed for deaf/mute/illiterate users: ZERO text input required.
///
/// Features:
/// - Front & back toggle (swipe or tap)
/// - Large tappable regions with emoji labels
/// - Red glow highlight when selected
/// - Haptic feedback on tap
/// - Semantics labels for screen readers (blind users)
class BodyMapWidget extends StatefulWidget {
  const BodyMapWidget({
    super.key,
    required this.selectedRegions,
    required this.onRegionsChanged,
  });

  final Set<BodyRegion> selectedRegions;
  final ValueChanged<Set<BodyRegion>> onRegionsChanged;

  @override
  State<BodyMapWidget> createState() => _BodyMapWidgetState();
}

class _BodyMapWidgetState extends State<BodyMapWidget> {
  bool _showFront = true;

  void _toggleRegion(BodyRegion region) {
    HapticFeedback.mediumImpact();
    final updated = Set<BodyRegion>.from(widget.selectedRegions);
    if (updated.contains(region)) {
      updated.remove(region);
    } else {
      updated.add(region);
    }
    widget.onRegionsChanged(updated);
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        // Front / Back toggle
        _buildViewToggle(),
        const SizedBox(height: 12),

        // Body illustration with tappable regions
        Expanded(
          child: AnimatedSwitcher(
            duration: const Duration(milliseconds: 300),
            child: _showFront
                ? _buildFrontBody(key: const ValueKey('front'))
                : _buildBackBody(key: const ValueKey('back')),
          ),
        ),

        const SizedBox(height: 8),

        // Selected regions summary (emoji only)
        if (widget.selectedRegions.isNotEmpty) _buildSelectedSummary(),
      ],
    );
  }

  Widget _buildViewToggle() {
    return Container(
      padding: const EdgeInsets.all(4),
      decoration: BoxDecoration(
        color: const Color(0xFF1A2332),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          _toggleButton(
            label: 'Trước',
            emoji: '🧍',
            isActive: _showFront,
            onTap: () => setState(() => _showFront = true),
          ),
          _toggleButton(
            label: 'Sau',
            emoji: '🔙',
            isActive: !_showFront,
            onTap: () => setState(() => _showFront = false),
          ),
        ],
      ),
    );
  }

  Widget _toggleButton({
    required String label,
    required String emoji,
    required bool isActive,
    required VoidCallback onTap,
  }) {
    return Semantics(
      label: 'Xem mặt $label',
      selected: isActive,
      child: GestureDetector(
        onTap: onTap,
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 200),
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 10),
          decoration: BoxDecoration(
            color: isActive ? const Color(0xFF0D9488) : Colors.transparent,
            borderRadius: BorderRadius.circular(12),
          ),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(emoji, style: const TextStyle(fontSize: 20)),
              const SizedBox(width: 6),
              Text(
                label,
                style: TextStyle(
                  fontFamily: 'Outfit',
                  fontSize: 14,
                  fontWeight: FontWeight.w600,
                  color: isActive ? Colors.white : Colors.white54,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildFrontBody({Key? key}) {
    return _BodyLayout(
      key: key,
      regions: const [
        _RegionData(BodyRegion.head, 0.5, 0.06, 56),
        _RegionData(BodyRegion.throat, 0.5, 0.16, 40),
        _RegionData(BodyRegion.chestLeft, 0.37, 0.26, 50),
        _RegionData(BodyRegion.chestRight, 0.63, 0.26, 50),
        _RegionData(BodyRegion.stomach, 0.5, 0.38, 50),
        _RegionData(BodyRegion.abdomenLeft, 0.37, 0.48, 46),
        _RegionData(BodyRegion.abdomenRight, 0.63, 0.48, 46),
        _RegionData(BodyRegion.leftArm, 0.15, 0.32, 44),
        _RegionData(BodyRegion.rightArm, 0.85, 0.32, 44),
        _RegionData(BodyRegion.leftLeg, 0.37, 0.72, 52),
        _RegionData(BodyRegion.rightLeg, 0.63, 0.72, 52),
      ],
      selectedRegions: widget.selectedRegions,
      onToggle: _toggleRegion,
      bodyEmoji: '🧍',
    );
  }

  Widget _buildBackBody({Key? key}) {
    return _BodyLayout(
      key: key,
      regions: const [
        _RegionData(BodyRegion.head, 0.5, 0.06, 56),
        _RegionData(BodyRegion.back, 0.5, 0.28, 60),
        _RegionData(BodyRegion.lowerBack, 0.5, 0.45, 56),
        _RegionData(BodyRegion.leftArm, 0.15, 0.32, 44),
        _RegionData(BodyRegion.rightArm, 0.85, 0.32, 44),
        _RegionData(BodyRegion.leftLeg, 0.37, 0.72, 52),
        _RegionData(BodyRegion.rightLeg, 0.63, 0.72, 52),
      ],
      selectedRegions: widget.selectedRegions,
      onToggle: _toggleRegion,
      bodyEmoji: '🧍',
    );
  }

  Widget _buildSelectedSummary() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16),
      child: Wrap(
        spacing: 8,
        runSpacing: 6,
        alignment: WrapAlignment.center,
        children: widget.selectedRegions.map((r) {
          return Semantics(
            label: '${r.label} đã chọn. Nhấn để bỏ chọn.',
            child: GestureDetector(
              onTap: () => _toggleRegion(r),
              child: Container(
                padding:
                    const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                decoration: BoxDecoration(
                  color: const Color(0xFFEF4444).withOpacity(0.15),
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(
                    color: const Color(0xFFEF4444).withOpacity(0.4),
                  ),
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
                        fontWeight: FontWeight.w600,
                        color: Color(0xFFFCA5A5),
                      ),
                    ),
                    const SizedBox(width: 4),
                    const Icon(Icons.close, size: 14, color: Color(0xFFFCA5A5)),
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

/// Layout for body regions — positions tappable circles on a body silhouette.
class _BodyLayout extends StatelessWidget {
  const _BodyLayout({
    super.key,
    required this.regions,
    required this.selectedRegions,
    required this.onToggle,
    required this.bodyEmoji,
  });

  final List<_RegionData> regions;
  final Set<BodyRegion> selectedRegions;
  final ValueChanged<BodyRegion> onToggle;
  final String bodyEmoji;

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        final w = constraints.maxWidth;
        final h = constraints.maxHeight;

        return Stack(
          children: [
            // Body silhouette background
            Positioned.fill(
              child: CustomPaint(
                painter: _BodySilhouettePainter(
                  selectedRegions: selectedRegions,
                  regions: regions,
                ),
              ),
            ),

            // Tappable region circles
            ...regions.map((r) {
              final isSelected = selectedRegions.contains(r.region);
              final x = r.relX * w - r.size / 2;
              final y = r.relY * h - r.size / 2;

              return Positioned(
                left: x,
                top: y,
                width: r.size,
                height: r.size,
                child: Semantics(
                  label:
                      '${r.region.label}. ${isSelected ? "Đã chọn" : "Chưa chọn"}. Nhấn đúp để ${isSelected ? "bỏ chọn" : "chọn"}.',
                  button: true,
                  child: GestureDetector(
                    onTap: () => onToggle(r.region),
                    child: AnimatedContainer(
                      duration: const Duration(milliseconds: 250),
                      curve: Curves.easeOut,
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        color: isSelected
                            ? const Color(0xFFEF4444).withOpacity(0.35)
                            : Colors.white.withOpacity(0.08),
                        border: Border.all(
                          color: isSelected
                              ? const Color(0xFFEF4444)
                              : Colors.white.withOpacity(0.25),
                          width: isSelected ? 2.5 : 1.5,
                        ),
                        boxShadow: isSelected
                            ? [
                                BoxShadow(
                                  color:
                                      const Color(0xFFEF4444).withOpacity(0.4),
                                  blurRadius: 16,
                                  spreadRadius: 2,
                                ),
                              ]
                            : [],
                      ),
                      child: Center(
                        child: Column(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            Text(
                              r.region.emoji,
                              style: TextStyle(
                                fontSize: r.size * 0.38,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                  ),
                ),
              );
            }),
          ],
        );
      },
    );
  }
}

/// Simple body silhouette painter — draws connecting lines between regions.
class _BodySilhouettePainter extends CustomPainter {
  _BodySilhouettePainter({
    required this.selectedRegions,
    required this.regions,
  });

  final Set<BodyRegion> selectedRegions;
  final List<_RegionData> regions;

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = Colors.white.withOpacity(0.06)
      ..strokeWidth = 2
      ..style = PaintingStyle.stroke;

    // Draw a simple body outline
    final path = Path();
    final cx = size.width * 0.5;

    // Head
    path.addOval(Rect.fromCircle(
      center: Offset(cx, size.height * 0.06),
      radius: 22,
    ));

    // Neck
    path.moveTo(cx, size.height * 0.09);
    path.lineTo(cx, size.height * 0.14);

    // Shoulders
    path.moveTo(size.width * 0.22, size.height * 0.18);
    path.lineTo(size.width * 0.78, size.height * 0.18);

    // Torso
    path.moveTo(size.width * 0.3, size.height * 0.18);
    path.lineTo(size.width * 0.3, size.height * 0.55);
    path.moveTo(size.width * 0.7, size.height * 0.18);
    path.lineTo(size.width * 0.7, size.height * 0.55);

    // Hips
    path.moveTo(size.width * 0.3, size.height * 0.55);
    path.lineTo(size.width * 0.7, size.height * 0.55);

    // Arms
    path.moveTo(size.width * 0.22, size.height * 0.18);
    path.lineTo(size.width * 0.12, size.height * 0.45);
    path.moveTo(size.width * 0.78, size.height * 0.18);
    path.lineTo(size.width * 0.88, size.height * 0.45);

    // Legs
    path.moveTo(size.width * 0.38, size.height * 0.55);
    path.lineTo(size.width * 0.35, size.height * 0.92);
    path.moveTo(size.width * 0.62, size.height * 0.55);
    path.lineTo(size.width * 0.65, size.height * 0.92);

    canvas.drawPath(path, paint);
  }

  @override
  bool shouldRepaint(covariant _BodySilhouettePainter oldDelegate) {
    return oldDelegate.selectedRegions != selectedRegions;
  }
}

/// Data for positioning a body region on the layout.
class _RegionData {
  const _RegionData(this.region, this.relX, this.relY, this.size);

  final BodyRegion region;
  final double relX; // 0.0–1.0 horizontal position
  final double relY; // 0.0–1.0 vertical position
  final double size; // diameter in logical pixels
}
