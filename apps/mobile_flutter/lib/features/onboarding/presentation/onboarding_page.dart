import 'package:flutter/material.dart';

import '../../../core/models/consult_mode.dart';
import 'widgets/mode_button.dart';
import 'widgets/onboarding_header.dart';

typedef OnOnboardingComplete = void Function(ConsultMode mode);

/// Onboarding page — Apple-style glassmorphism.
/// Gradient background → glass header → frosted glass mode cards.
class OnboardingPage extends StatefulWidget {
  const OnboardingPage({
    super.key,
    required this.initialMode,
    required this.onComplete,
  });

  final ConsultMode initialMode;
  final OnOnboardingComplete onComplete;

  @override
  State<OnboardingPage> createState() => _OnboardingPageState();
}

class _OnboardingPageState extends State<OnboardingPage> {
  late ConsultMode _selectedMode;
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    _selectedMode = widget.initialMode;
  }

  void _onModeSelected(ConsultMode mode) {
    setState(() {
      _selectedMode = mode;
    });
    _showConfirmation(mode);
  }

  Future<void> _showConfirmation(ConsultMode mode) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: const Color(0xFF1A2E35),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(24)),
        title: Text(
          'Bạn chọn: ${mode.title}',
          style: const TextStyle(
            fontFamily: 'Outfit',
            fontSize: 20,
            fontWeight: FontWeight.w600,
            color: Colors.white,
          ),
        ),
        content: Text(
          '${mode.description}.\n\nBạn có thể đổi lại bất cứ lúc nào trong Cài đặt.',
          style: TextStyle(
            fontFamily: 'Outfit',
            fontSize: 16,
            color: Colors.white.withOpacity(0.7),
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(ctx).pop(false),
            child: Text(
              'Chọn lại',
              style: TextStyle(
                fontFamily: 'Outfit',
                fontSize: 16,
                color: Colors.white.withOpacity(0.6),
              ),
            ),
          ),
          FilledButton(
            onPressed: () => Navigator.of(ctx).pop(true),
            style: FilledButton.styleFrom(
              backgroundColor: const Color(0xFF0D9B6B),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(14),
              ),
              padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
            ),
            child: const Text(
              'Tiếp tục',
              style: TextStyle(
                fontFamily: 'Outfit',
                fontSize: 16,
                fontWeight: FontWeight.w600,
              ),
            ),
          ),
        ],
      ),
    );

    if (confirmed == true && mounted) {
      setState(() => _isLoading = true);
      await Future.delayed(const Duration(milliseconds: 300));
      if (mounted) {
        widget.onComplete(_selectedMode);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [
              Color(0xFF064E3B),
              Color(0xFF0A6B52),
              Color(0xFF0F766E),
              Color(0xFF1A5C4A),
              Color(0xFF1E3A3A),
            ],
            stops: [0.0, 0.15, 0.35, 0.65, 1.0],
          ),
        ),
        child: Stack(
          children: [
            // Decorative orbs
            Positioned(
              bottom: -60,
              left: -50,
              child: Container(
                width: 240,
                height: 240,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  gradient: RadialGradient(
                    colors: [
                      const Color(0xFF6366F1).withOpacity(0.1),
                      const Color(0xFF6366F1).withOpacity(0.0),
                    ],
                  ),
                ),
              ),
            ),
            Positioned(
              top: 200,
              right: -40,
              child: Container(
                width: 180,
                height: 180,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  gradient: RadialGradient(
                    colors: [
                      const Color(0xFF34D399).withOpacity(0.08),
                      const Color(0xFF34D399).withOpacity(0.0),
                    ],
                  ),
                ),
              ),
            ),
            // Main content
            SafeArea(
              top: false,
              child: _isLoading ? _buildLoading() : _buildContent(),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildLoading() {
    return Center(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          const CircularProgressIndicator(
            color: Color(0xFF34D399),
          ),
          const SizedBox(height: 16),
          Text(
            'Đang chuẩn bị...',
            style: TextStyle(
              fontFamily: 'Outfit',
              fontSize: 18,
              color: Colors.white.withOpacity(0.7),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildContent() {
    return LayoutBuilder(
      builder: (context, constraints) {
        return SingleChildScrollView(
          child: ConstrainedBox(
            constraints: BoxConstraints(minHeight: constraints.maxHeight),
            child: IntrinsicHeight(
              child: Column(
                children: [
                  // ── Header ──
                  const OnboardingHeader(),

                  // ── Mode selection body ──
                  Expanded(
                    child: Padding(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 24,
                        vertical: 20,
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Text(
                            'Bạn muốn dùng MediSign như thế nào?',
                            style: TextStyle(
                              fontFamily: 'Outfit',
                              fontSize: 20,
                              fontWeight: FontWeight.bold,
                              color: Colors.white,
                            ),
                          ),
                          const SizedBox(height: 16),

                          // ── Glass mode buttons ──
                          ...ConsultMode.values.map(
                            (mode) => Padding(
                              padding: const EdgeInsets.only(bottom: 12),
                              child: ModeButton(
                                emoji: mode.emoji,
                                title: mode.title,
                                description: mode.description,
                                isSelected: mode == _selectedMode,
                                isRecommended: mode.isRecommended,
                                semanticLabel: mode.semanticLabel,
                                onTap: () => _onModeSelected(mode),
                              ),
                            ),
                          ),

                          const Spacer(),

                          // ── Helper text ──
                          Center(
                            child: Padding(
                              padding: const EdgeInsets.only(top: 8),
                              child: Text.rich(
                                const TextSpan(
                                  children: [
                                    TextSpan(
                                      text: '💡 Không biết chọn gì? Chọn ',
                                    ),
                                    TextSpan(
                                      text: '"Tốt nhất cho tôi"',
                                      style: TextStyle(
                                        fontWeight: FontWeight.w600,
                                        color: Color(0xFF34D399),
                                      ),
                                    ),
                                    TextSpan(text: ' là được!'),
                                  ],
                                ),
                                textAlign: TextAlign.center,
                                style: TextStyle(
                                  fontFamily: 'Outfit',
                                  fontSize: 14,
                                  color: Colors.white.withOpacity(0.6),
                                ),
                              ),
                            ),
                          ),
                          const SizedBox(height: 8),
                          Center(
                            child: Text(
                              'Đổi lại bất cứ lúc nào trong Cài đặt',
                              textAlign: TextAlign.center,
                              style: TextStyle(
                                fontFamily: 'Outfit',
                                fontSize: 12,
                                color: Colors.white.withOpacity(0.4),
                              ),
                            ),
                          ),
                          const SizedBox(height: 16),
                        ],
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
