import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

/// Guided 4-7-8 breathing exercise with animated circle and haptic feedback.
class BreathingExercisePage extends StatefulWidget {
  const BreathingExercisePage({super.key});

  @override
  State<BreathingExercisePage> createState() => _BreathingExercisePageState();
}

class _BreathingExercisePageState extends State<BreathingExercisePage>
    with TickerProviderStateMixin {
  late AnimationController _breathController;
  late AnimationController _pulseController;

  bool _isRunning = false;
  int _completedCycles = 0;
  static const _totalCycles = 4;

  // 4-7-8 pattern (seconds)
  static const _inhale = 4;
  static const _hold = 7;
  static const _exhale = 8;
  static const _cycleDuration = _inhale + _hold + _exhale; // 19s

  String _phaseLabel = 'Sẵn sàng?';
  String _phaseEmoji = '🧘';
  Color _phaseColor = const Color(0xFF52B788);

  @override
  void initState() {
    super.initState();
    _breathController = AnimationController(
      vsync: this,
      duration: const Duration(seconds: _cycleDuration),
    );
    _pulseController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1200),
    )..repeat(reverse: true);

    _breathController.addListener(_updatePhase);
    _breathController.addStatusListener((status) {
      if (status == AnimationStatus.completed) {
        _completedCycles++;
        if (_completedCycles >= _totalCycles) {
          _stop();
        } else {
          _breathController.forward(from: 0);
        }
      }
    });
  }

  void _updatePhase() {
    final progress = _breathController.value * _cycleDuration;
    setState(() {
      if (progress < _inhale) {
        _phaseLabel = 'Hít vào';
        _phaseEmoji = '🌬️';
        _phaseColor = const Color(0xFF60A5FA);
      } else if (progress < _inhale + _hold) {
        _phaseLabel = 'Giữ hơi';
        _phaseEmoji = '⏸️';
        _phaseColor = const Color(0xFFA78BFA);
      } else {
        _phaseLabel = 'Thở ra';
        _phaseEmoji = '💨';
        _phaseColor = const Color(0xFF52B788);
      }
    });
  }

  void _start() {
    HapticFeedback.mediumImpact();
    setState(() {
      _isRunning = true;
      _completedCycles = 0;
    });
    _breathController.forward(from: 0);
  }

  void _stop() {
    _breathController.stop();
    setState(() {
      _isRunning = false;
      _phaseLabel =
          _completedCycles >= _totalCycles ? 'Hoàn thành! 🎉' : 'Đã dừng';
      _phaseEmoji = _completedCycles >= _totalCycles ? '✨' : '🧘';
      _phaseColor = const Color(0xFF52B788);
    });
    if (_completedCycles >= _totalCycles) {
      HapticFeedback.heavyImpact();
    }
  }

  @override
  void dispose() {
    _breathController.dispose();
    _pulseController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    // Animate circle scale: inhale → expand, hold → stay, exhale → shrink
    double circleScale = 0.6;
    if (_isRunning) {
      final progress = _breathController.value * _cycleDuration;
      if (progress < _inhale) {
        circleScale = 0.6 + 0.4 * (progress / _inhale);
      } else if (progress < _inhale + _hold) {
        circleScale = 1.0;
      } else {
        final exhaleProgress = (progress - _inhale - _hold) / _exhale;
        circleScale = 1.0 - 0.4 * exhaleProgress;
      }
    }

    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [Color(0xFF1B4332), Color(0xFF0F3726), Color(0xFF1B4332)],
          ),
        ),
        child: SafeArea(
          child: Column(
            children: [
              // Header
              Padding(
                padding: const EdgeInsets.fromLTRB(8, 8, 16, 0),
                child: Row(
                  children: [
                    IconButton(
                      icon: const Icon(Icons.arrow_back_ios,
                          color: Colors.white70),
                      onPressed: () => Navigator.pop(context),
                    ),
                    const Text('Bài tập thở',
                        style: TextStyle(
                            color: Colors.white,
                            fontSize: 18,
                            fontWeight: FontWeight.w600)),
                  ],
                ),
              ),
              const Spacer(),
              // Main animated circle
              AnimatedBuilder(
                animation:
                    Listenable.merge([_breathController, _pulseController]),
                builder: (_, __) {
                  final idlePulse =
                      _isRunning ? 0.0 : _pulseController.value * 0.05;
                  return Column(
                    children: [
                      Text(_phaseEmoji, style: const TextStyle(fontSize: 48)),
                      const SizedBox(height: 16),
                      Container(
                        width: 220 * (circleScale + idlePulse),
                        height: 220 * (circleScale + idlePulse),
                        decoration: BoxDecoration(
                          shape: BoxShape.circle,
                          gradient: RadialGradient(
                            colors: [
                              _phaseColor.withOpacity(0.3),
                              _phaseColor.withOpacity(0.08),
                            ],
                          ),
                          border: Border.all(
                            color: _phaseColor.withOpacity(0.5),
                            width: 3,
                          ),
                          boxShadow: [
                            BoxShadow(
                              color: _phaseColor.withOpacity(0.2),
                              blurRadius: 40,
                              spreadRadius: 10,
                            ),
                          ],
                        ),
                        child: Center(
                          child: Text(
                            _phaseLabel,
                            style: const TextStyle(
                              color: Colors.white,
                              fontSize: 20,
                              fontWeight: FontWeight.w700,
                            ),
                          ),
                        ),
                      ),
                    ],
                  );
                },
              ),
              const SizedBox(height: 32),
              // Cycle progress
              if (_isRunning)
                Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: List.generate(_totalCycles, (i) {
                    return Container(
                      width: 12,
                      height: 12,
                      margin: const EdgeInsets.symmetric(horizontal: 4),
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        color: i < _completedCycles
                            ? const Color(0xFF52B788)
                            : Colors.white.withOpacity(0.15),
                        border: i == _completedCycles
                            ? Border.all(
                                color: const Color(0xFF52B788), width: 2)
                            : null,
                      ),
                    );
                  }),
                ),
              const Spacer(),
              // Instructions
              Container(
                margin: const EdgeInsets.symmetric(horizontal: 32),
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Colors.white.withOpacity(0.06),
                  borderRadius: BorderRadius.circular(16),
                ),
                child: Column(
                  children: [
                    const Text('Kỹ thuật thở 4-7-8',
                        style: TextStyle(
                            color: Colors.white,
                            fontSize: 15,
                            fontWeight: FontWeight.w600)),
                    const SizedBox(height: 8),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceAround,
                      children: [
                        _phaseInfo(
                            '🌬️', '4s', 'Hít vào', const Color(0xFF60A5FA)),
                        _phaseInfo(
                            '⏸️', '7s', 'Giữ hơi', const Color(0xFFA78BFA)),
                        _phaseInfo(
                            '💨', '8s', 'Thở ra', const Color(0xFF52B788)),
                      ],
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 24),
              // Start/Stop button
              Padding(
                padding: const EdgeInsets.fromLTRB(32, 0, 32, 32),
                child: SizedBox(
                  width: double.infinity,
                  height: 56,
                  child: ElevatedButton(
                    onPressed: _isRunning ? _stop : _start,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: _isRunning
                          ? Colors.white.withOpacity(0.12)
                          : const Color(0xFF52B788),
                      foregroundColor: Colors.white,
                      shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(28)),
                      elevation: _isRunning ? 0 : 4,
                    ),
                    child: Text(_isRunning ? 'Dừng lại' : 'Bắt đầu',
                        style: const TextStyle(
                            fontSize: 16, fontWeight: FontWeight.w700)),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _phaseInfo(String emoji, String duration, String label, Color color) {
    return Column(
      children: [
        Text(emoji, style: const TextStyle(fontSize: 20)),
        const SizedBox(height: 4),
        Text(duration,
            style: TextStyle(
                color: color, fontSize: 16, fontWeight: FontWeight.bold)),
        Text(label,
            style:
                TextStyle(color: Colors.white.withOpacity(0.5), fontSize: 11)),
      ],
    );
  }
}
