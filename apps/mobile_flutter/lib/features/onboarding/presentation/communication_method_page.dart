import 'dart:ui';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import '../../../core/models/communication_mode.dart';
import '../../auth/presentation/auth_theme.dart';

/// Communication Method Selection — Onboarding step 3.2b.
///
/// Multi-modal prompt: The question is presented through
/// TEXT + large ICON CARDS simultaneously so that ANY user
/// (deaf, blind, illiterate) can understand at least one channel.
///
/// Users can select MULTIPLE methods. The app then adapts
/// its entire UI based on the combination chosen.
///
/// Design: Apple-style glassmorphism (matching auth screens).
class CommunicationMethodPage extends StatefulWidget {
  const CommunicationMethodPage({
    super.key,
    required this.onComplete,
    this.onBack,
  });

  final ValueChanged<Set<CommunicationMethod>> onComplete;
  final VoidCallback? onBack;

  @override
  State<CommunicationMethodPage> createState() =>
      _CommunicationMethodPageState();
}

class _CommunicationMethodPageState extends State<CommunicationMethodPage>
    with SingleTickerProviderStateMixin {
  final Set<CommunicationMethod> _selected = {};
  late AnimationController _entryCtrl;
  late Animation<double> _fadeAnim;

  @override
  void initState() {
    super.initState();
    _entryCtrl = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 800),
    )..forward();
    _fadeAnim = CurvedAnimation(parent: _entryCtrl, curve: Curves.easeOut);
  }

  @override
  void dispose() {
    _entryCtrl.dispose();
    super.dispose();
  }

  void _toggle(CommunicationMethod method) {
    HapticFeedback.lightImpact();
    setState(() {
      if (_selected.contains(method)) {
        _selected.remove(method);
      } else {
        _selected.add(method);
      }
    });
  }

  void _onContinue() {
    if (_selected.isEmpty) return;
    HapticFeedback.mediumImpact();
    widget.onComplete(Set.from(_selected));
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: AuthTheme.gradientBackground(
        child: SafeArea(
          child: FadeTransition(
            opacity: _fadeAnim,
            child: Padding(
              padding: const EdgeInsets.fromLTRB(24, 16, 24, 24),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // ── Back button ──
                  if (widget.onBack != null)
                    GestureDetector(
                      onTap: widget.onBack,
                      child: Container(
                        width: 44,
                        height: 44,
                        decoration: BoxDecoration(
                          color: Colors.white.withOpacity(0.12),
                          shape: BoxShape.circle,
                          border:
                              Border.all(color: Colors.white.withOpacity(0.2)),
                        ),
                        child: const Icon(
                          Icons.arrow_back_ios_new_rounded,
                          size: 18,
                          color: Colors.white,
                        ),
                      ),
                    ),
                  const SizedBox(height: 20),

                  // ── Question header (multi-modal) ──
                  _buildQuestionHeader(),
                  const SizedBox(height: 24),

                  // ── 4 Method Cards ──
                  Expanded(
                    child: ListView(
                      children: [
                        _buildMethodCard(
                          method: CommunicationMethod.voice,
                          iconData: Icons.mic_rounded,
                          iconColor: const Color(0xFF60A5FA),
                          bgGlow: const Color(0xFF3B82F6),
                        ),
                        const SizedBox(height: 12),
                        _buildMethodCard(
                          method: CommunicationMethod.sign,
                          iconData: Icons.front_hand_rounded,
                          iconColor: const Color(0xFFA78BFA),
                          bgGlow: const Color(0xFF8B5CF6),
                        ),
                        const SizedBox(height: 12),
                        _buildMethodCard(
                          method: CommunicationMethod.tap,
                          iconData: Icons.touch_app_rounded,
                          iconColor: const Color(0xFF34D399),
                          bgGlow: const Color(0xFF10B981),
                        ),
                        const SizedBox(height: 12),
                        _buildMethodCard(
                          method: CommunicationMethod.text,
                          iconData: Icons.keyboard_rounded,
                          iconColor: const Color(0xFFFBBF24),
                          bgGlow: const Color(0xFFF59E0B),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 16),

                  // ── Selected summary ──
                  if (_selected.isNotEmpty) _buildSelectedSummary(),
                  const SizedBox(height: 12),

                  // ── Continue button ──
                  AuthTheme.primaryButton(
                    text: 'Tiếp tục',
                    icon: Icons.arrow_forward_rounded,
                    onPressed: _selected.isNotEmpty ? _onContinue : null,
                  ),
                  const SizedBox(height: 8),

                  // ── Hint ──
                  const Center(
                    child: Text(
                      'Có thể thay đổi sau trong Cài đặt',
                      style: TextStyle(
                        fontFamily: 'Outfit',
                        fontSize: 12,
                        color: Colors.white38,
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildQuestionHeader() {
    return const Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Emoji + Title
        Row(
          children: [
            Text('💬', style: TextStyle(fontSize: 32)),
            SizedBox(width: 12),
            Expanded(
              child: Text(
                'Chúng ta giao tiếp\nqua đâu nhé?',
                style: TextStyle(
                  fontFamily: 'Outfit',
                  fontSize: 24,
                  fontWeight: FontWeight.w800,
                  color: Colors.white,
                  height: 1.2,
                ),
              ),
            ),
          ],
        ),
        SizedBox(height: 8),
        // Subtitle
        Text(
          'Chọn 1 hoặc nhiều cách — app sẽ tự tối ưu cho bạn',
          style: TextStyle(
            fontFamily: 'Outfit',
            fontSize: 14,
            color: Colors.white60,
          ),
        ),
      ],
    );
  }

  Widget _buildMethodCard({
    required CommunicationMethod method,
    required IconData iconData,
    required Color iconColor,
    required Color bgGlow,
  }) {
    final isActive = _selected.contains(method);

    return Semantics(
      label:
          '${method.label}. ${method.description}. ${isActive ? "Đã chọn" : "Chưa chọn"}. Nhấn để ${isActive ? "bỏ chọn" : "chọn"}.',
      button: true,
      child: GestureDetector(
        onTap: () => _toggle(method),
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 250),
          curve: Curves.easeOut,
          padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 16),
          decoration: BoxDecoration(
            color: isActive
                ? bgGlow.withOpacity(0.12)
                : Colors.white.withOpacity(0.04),
            borderRadius: BorderRadius.circular(20),
            border: Border.all(
              color: isActive
                  ? bgGlow.withOpacity(0.5)
                  : Colors.white.withOpacity(0.08),
              width: isActive ? 2 : 1,
            ),
            boxShadow: isActive
                ? [
                    BoxShadow(
                      color: bgGlow.withOpacity(0.2),
                      blurRadius: 16,
                      spreadRadius: 1,
                    ),
                  ]
                : [],
          ),
          child: Row(
            children: [
              // Icon container
              AnimatedContainer(
                duration: const Duration(milliseconds: 200),
                width: 52,
                height: 52,
                decoration: BoxDecoration(
                  color: isActive
                      ? iconColor.withOpacity(0.2)
                      : Colors.white.withOpacity(0.06),
                  borderRadius: BorderRadius.circular(16),
                ),
                child: Icon(
                  iconData,
                  size: 26,
                  color: isActive ? iconColor : Colors.white38,
                ),
              ),
              const SizedBox(width: 16),

              // Text content
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Text(
                          method.icon,
                          style: const TextStyle(fontSize: 18),
                        ),
                        const SizedBox(width: 6),
                        Text(
                          method.label,
                          style: TextStyle(
                            fontFamily: 'Outfit',
                            fontSize: 17,
                            fontWeight: FontWeight.w700,
                            color: isActive ? iconColor : Colors.white70,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 3),
                    Text(
                      method.description,
                      style: TextStyle(
                        fontFamily: 'Outfit',
                        fontSize: 13,
                        color: isActive
                            ? Colors.white60
                            : Colors.white.withOpacity(0.35),
                      ),
                    ),
                  ],
                ),
              ),

              // Check indicator
              AnimatedContainer(
                duration: const Duration(milliseconds: 200),
                width: 28,
                height: 28,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: isActive ? iconColor : Colors.white.withOpacity(0.06),
                  border: Border.all(
                    color:
                        isActive ? iconColor : Colors.white.withOpacity(0.15),
                    width: 2,
                  ),
                ),
                child: isActive
                    ? const Icon(Icons.check, size: 16, color: Colors.white)
                    : null,
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildSelectedSummary() {
    // Show what mode the app will optimize for
    String modeHint;
    if (_selected.length == 1 &&
        _selected.contains(CommunicationMethod.voice)) {
      modeHint = '🎤 Voice full + TTS';
    } else if (_selected.length == 1 &&
        _selected.contains(CommunicationMethod.sign)) {
      modeHint = '🤟 Sign + Pictogram';
    } else if (_selected.length == 1 &&
        _selected.contains(CommunicationMethod.tap)) {
      modeHint = '👆 Icon-only + Pictogram';
    } else if (_selected.length == 1 &&
        _selected.contains(CommunicationMethod.text)) {
      modeHint = '⌨️ Standard text chat';
    } else if (_selected
        .containsAll({CommunicationMethod.voice, CommunicationMethod.tap})) {
      modeHint = '🎤+👆 Voice + Icon lớn';
    } else if (_selected
        .containsAll({CommunicationMethod.sign, CommunicationMethod.tap})) {
      modeHint = '🤟+👆 Sign + Pictogram';
    } else {
      modeHint = '${_selected.map((m) => m.icon).join(' + ')} Đa kênh';
    }

    return ClipRRect(
      borderRadius: BorderRadius.circular(12),
      child: BackdropFilter(
        filter: ImageFilter.blur(sigmaX: 8, sigmaY: 8),
        child: Container(
          width: double.infinity,
          padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
          decoration: BoxDecoration(
            color: const Color(0xFF14B8A6).withOpacity(0.1),
            borderRadius: BorderRadius.circular(12),
            border: Border.all(
              color: const Color(0xFF14B8A6).withOpacity(0.2),
            ),
          ),
          child: Row(
            children: [
              const Text('✨', style: TextStyle(fontSize: 16)),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  'App sẽ tối ưu: $modeHint',
                  style: const TextStyle(
                    fontFamily: 'Outfit',
                    fontSize: 13,
                    fontWeight: FontWeight.w500,
                    color: Color(0xFF5EEAD4),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
