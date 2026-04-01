
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import '../../../../core/services/service_locator.dart';

/// Sign Language Consult Widget — for DEAF/MUTE users.
///
/// Flow:
/// 1. Camera preview (front camera) → user performs sign language
/// 2. AI recognizes signs → shows recognized word/phrase as pictogram
/// 3. User confirms or adjusts → builds a visual "sentence"
/// 4. AI processes → pictogram-first result
///
/// Design principles:
/// - NO AUDIO (deaf users can't hear)
/// - Visual-only feedback: animations, colors, icons
/// - Recognized signs shown as EMOJI + large text
/// - Haptic feedback for confirmation
/// - Camera viewfinder with hand tracking overlay
class SignLanguageConsultWidget extends StatefulWidget {
  const SignLanguageConsultWidget({
    super.key,
    required this.onSymptomsRecognized,
  });

  final ValueChanged<List<String>> onSymptomsRecognized;

  @override
  State<SignLanguageConsultWidget> createState() =>
      _SignLanguageConsultWidgetState();
}

class _SignLanguageConsultWidgetState extends State<SignLanguageConsultWidget>
    with TickerProviderStateMixin {
  // ignore: unused_field - used for future state tracking
  _SignState _state = _SignState.ready;
  final List<RecognizedSign> _recognizedSigns = [];
  RecognizedSign? _currentSign;
  bool _isRecording = false;

  // Service — from ServiceLocator (swap mock→real in service_locator.dart)
  final _signService = ServiceLocator.instance.signLanguage;

  // Animations
  late AnimationController _scanCtrl;
  late Animation<double> _scanAnim;
  late AnimationController _confirmCtrl;

  @override
  void initState() {
    super.initState();

    _scanCtrl = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 2000),
    )..repeat();

    _scanAnim = Tween<double>(begin: 0.0, end: 1.0).animate(_scanCtrl);

    _confirmCtrl = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 300),
    );
  }

  @override
  void dispose() {
    _scanCtrl.dispose();
    _confirmCtrl.dispose();
    _signService.stopRecognition();
    super.dispose();
  }

  void _startRecording() {
    HapticFeedback.heavyImpact();
    setState(() {
      _state = _SignState.recording;
      _isRecording = true;
    });

    // Use SignLanguageService for recognition
    _signService.startRecognition(
      onSignRecognized: (result) {
        if (!mounted) return;
        HapticFeedback.mediumImpact();
        setState(() {
          _currentSign = RecognizedSign(
            emoji: result.emoji,
            label: result.sign,
            confidence: result.confidence,
          );
          _state = _SignState.recognized;
        });
      },
    );
  }

  void _confirmSign() {
    if (_currentSign == null) return;
    HapticFeedback.lightImpact();

    setState(() {
      _recognizedSigns.add(_currentSign!);
      _currentSign = null;
      _state = _SignState.recording;
    });

    // Check if we have enough signs
    if (_recognizedSigns.length >= 3) {
      // Show "done" option more prominently
    }
  }

  void _rejectSign() {
    HapticFeedback.lightImpact();
    setState(() {
      _currentSign = null;
      _state = _SignState.recording;
    });
  }

  void _removeSign(int index) {
    HapticFeedback.lightImpact();
    setState(() {
      _recognizedSigns.removeAt(index);
    });
  }

  void _submitSigns() {
    if (_recognizedSigns.isEmpty) return;
    HapticFeedback.heavyImpact();
    _signService.stopRecognition();

    setState(() {
      _isRecording = false;
      _state = _SignState.processing;
    });

    // Return recognized symptoms
    Future.delayed(const Duration(seconds: 1), () {
      if (!mounted) return;
      widget.onSymptomsRecognized(
        _recognizedSigns.map((s) => s.label).toList(),
      );
    });
  }

  void _stopRecording() {
    _signService.stopRecognition();
    setState(() {
      _isRecording = false;
      _state = _SignState.ready;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        // ── Camera preview area ──
        Expanded(
          flex: 3,
          child: _buildCameraArea(),
        ),

        // ── Recognized sign (current) ──
        if (_currentSign != null) _buildCurrentSignCard(),

        // ── Recognized signs sentence ──
        if (_recognizedSigns.isNotEmpty) ...[
          const SizedBox(height: 8),
          _buildSignSentence(),
        ],

        const SizedBox(height: 8),

        // ── Controls ──
        _buildControls(),
        const SizedBox(height: 12),
      ],
    );
  }

  Widget _buildCameraArea() {
    return Semantics(
      label: _isRecording
          ? 'Camera đang quay. Thực hiện ký hiệu tay trước camera.'
          : 'Camera chưa bật. Nhấn nút bên dưới để bắt đầu.',
      child: Container(
        margin: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: const Color(0xFF0F172A),
          borderRadius: BorderRadius.circular(24),
          border: Border.all(
            color: _isRecording
                ? const Color(0xFF14B8A6).withOpacity(0.5)
                : Colors.white.withOpacity(0.08),
            width: _isRecording ? 2 : 1,
          ),
        ),
        child: ClipRRect(
          borderRadius: BorderRadius.circular(23),
          child: Stack(
            fit: StackFit.expand,
            children: [
              // Placeholder for actual camera preview
              Container(
                color: const Color(0xFF1E293B),
                child: Center(
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Icon(
                        _isRecording
                            ? Icons.videocam_rounded
                            : Icons.videocam_off_rounded,
                        size: 48,
                        color: _isRecording
                            ? const Color(0xFF14B8A6)
                            : Colors.white24,
                      ),
                      const SizedBox(height: 8),
                      Text(
                        _isRecording
                            ? '📹 Camera đang quay'
                            : '📷 Camera chưa bật',
                        style: TextStyle(
                          fontFamily: 'Outfit',
                          fontSize: 14,
                          color: _isRecording
                              ? const Color(0xFF5EEAD4)
                              : Colors.white30,
                        ),
                      ),
                      if (_isRecording) ...[
                        const SizedBox(height: 4),
                        const Text(
                          '🤟 Thực hiện ký hiệu tay',
                          style: TextStyle(
                            fontFamily: 'Outfit',
                            fontSize: 16,
                            fontWeight: FontWeight.w600,
                            color: Colors.white60,
                          ),
                        ),
                      ],
                    ],
                  ),
                ),
              ),

              // Scanning overlay animation
              if (_isRecording)
                AnimatedBuilder(
                  animation: _scanAnim,
                  builder: (_, __) {
                    return Positioned(
                      top: _scanAnim.value *
                          (MediaQuery.of(context).size.height * 0.4),
                      left: 0,
                      right: 0,
                      child: Container(
                        height: 3,
                        decoration: BoxDecoration(
                          gradient: LinearGradient(
                            colors: [
                              Colors.transparent,
                              const Color(0xFF14B8A6).withOpacity(0.6),
                              Colors.transparent,
                            ],
                          ),
                        ),
                      ),
                    );
                  },
                ),

              // Recording indicator
              if (_isRecording)
                Positioned(
                  top: 12,
                  right: 12,
                  child: Container(
                    padding:
                        const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
                    decoration: BoxDecoration(
                      color: const Color(0xFFEF4444).withOpacity(0.2),
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(
                        color: const Color(0xFFEF4444).withOpacity(0.4),
                      ),
                    ),
                    child: const Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Icon(Icons.circle, size: 10, color: Color(0xFFEF4444)),
                        SizedBox(width: 4),
                        Text(
                          'REC',
                          style: TextStyle(
                            fontFamily: 'Outfit',
                            fontSize: 11,
                            fontWeight: FontWeight.w700,
                            color: Color(0xFFFCA5A5),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),

              // Hand guide overlay
              if (_isRecording && _currentSign == null)
                Center(
                  child: Container(
                    width: 180,
                    height: 180,
                    decoration: BoxDecoration(
                      borderRadius: BorderRadius.circular(20),
                      border: Border.all(
                        color: const Color(0xFF14B8A6).withOpacity(0.3),
                        width: 2,
                      ),
                    ),
                    child: const Center(
                      child: Text(
                        '🖐️',
                        style: TextStyle(fontSize: 60),
                      ),
                    ),
                  ),
                ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildCurrentSignCard() {
    return Semantics(
      label:
          'Đã nhận ra ký hiệu: ${_currentSign!.label}. Độ chính xác: ${(_currentSign!.confidence * 100).toInt()} phần trăm. Nhấn dấu tích để xác nhận.',
      child: Container(
        margin: const EdgeInsets.symmetric(horizontal: 16),
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        decoration: BoxDecoration(
          color: const Color(0xFF14B8A6).withOpacity(0.15),
          borderRadius: BorderRadius.circular(16),
          border: Border.all(
            color: const Color(0xFF14B8A6).withOpacity(0.4),
            width: 2,
          ),
          boxShadow: [
            BoxShadow(
              color: const Color(0xFF14B8A6).withOpacity(0.2),
              blurRadius: 12,
            ),
          ],
        ),
        child: Row(
          children: [
            // Recognized emoji
            Text(
              _currentSign!.emoji,
              style: const TextStyle(fontSize: 36),
            ),
            const SizedBox(width: 12),
            // Label + confidence
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    _currentSign!.label,
                    style: const TextStyle(
                      fontFamily: 'Outfit',
                      fontSize: 20,
                      fontWeight: FontWeight.w700,
                      color: Color(0xFF5EEAD4),
                    ),
                  ),
                  const SizedBox(height: 2),
                  // Confidence bar
                  Row(
                    children: [
                      Expanded(
                        child: ClipRRect(
                          borderRadius: BorderRadius.circular(4),
                          child: LinearProgressIndicator(
                            value: _currentSign!.confidence,
                            backgroundColor: Colors.white.withOpacity(0.1),
                            valueColor: const AlwaysStoppedAnimation(
                              Color(0xFF14B8A6),
                            ),
                            minHeight: 4,
                          ),
                        ),
                      ),
                      const SizedBox(width: 8),
                      Text(
                        '${(_currentSign!.confidence * 100).toInt()}%',
                        style: const TextStyle(
                          fontFamily: 'Outfit',
                          fontSize: 12,
                          color: Colors.white54,
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
            const SizedBox(width: 8),
            // Accept ✓
            Semantics(
              label: 'Xác nhận',
              button: true,
              child: GestureDetector(
                onTap: _confirmSign,
                child: Container(
                  width: 44,
                  height: 44,
                  decoration: BoxDecoration(
                    color: const Color(0xFF22C55E).withOpacity(0.2),
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(
                      color: const Color(0xFF22C55E).withOpacity(0.4),
                    ),
                  ),
                  child: const Icon(
                    Icons.check_rounded,
                    color: Color(0xFF22C55E),
                    size: 24,
                  ),
                ),
              ),
            ),
            const SizedBox(width: 6),
            // Reject ✗
            Semantics(
              label: 'Sai, thử lại',
              button: true,
              child: GestureDetector(
                onTap: _rejectSign,
                child: Container(
                  width: 44,
                  height: 44,
                  decoration: BoxDecoration(
                    color: const Color(0xFFEF4444).withOpacity(0.15),
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(
                      color: const Color(0xFFEF4444).withOpacity(0.3),
                    ),
                  ),
                  child: const Icon(
                    Icons.close_rounded,
                    color: Color(0xFFEF4444),
                    size: 24,
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSignSentence() {
    return Semantics(
      label: 'Câu ký hiệu: ${_recognizedSigns.map((s) => s.label).join(', ')}',
      child: Container(
        height: 50,
        margin: const EdgeInsets.symmetric(horizontal: 16),
        child: ListView.separated(
          scrollDirection: Axis.horizontal,
          itemCount: _recognizedSigns.length,
          separatorBuilder: (_, __) => const Padding(
            padding: EdgeInsets.symmetric(horizontal: 4),
            child: Center(
              child: Text('→',
                  style: TextStyle(color: Colors.white24, fontSize: 16)),
            ),
          ),
          itemBuilder: (context, index) {
            final sign = _recognizedSigns[index];
            return Semantics(
              label: '${sign.label}. Nhấn để xóa.',
              button: true,
              child: GestureDetector(
                onTap: () => _removeSign(index),
                child: Container(
                  padding:
                      const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                  decoration: BoxDecoration(
                    color: const Color(0xFF8B5CF6).withOpacity(0.15),
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(
                      color: const Color(0xFF8B5CF6).withOpacity(0.3),
                    ),
                  ),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Text(sign.emoji, style: const TextStyle(fontSize: 22)),
                      const SizedBox(width: 4),
                      Text(
                        sign.label,
                        style: const TextStyle(
                          fontFamily: 'Outfit',
                          fontSize: 14,
                          fontWeight: FontWeight.w600,
                          color: Color(0xFFC4B5FD),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            );
          },
        ),
      ),
    );
  }

  Widget _buildControls() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16),
      child: Row(
        children: [
          if (!_isRecording)
            // Start recording
            Expanded(
              child: Semantics(
                label: 'Bắt đầu quay ký hiệu',
                button: true,
                child: GestureDetector(
                  onTap: _startRecording,
                  child: Container(
                    height: 52,
                    decoration: BoxDecoration(
                      gradient: const LinearGradient(
                        colors: [Color(0xFF8B5CF6), Color(0xFF7C3AED)],
                      ),
                      borderRadius: BorderRadius.circular(16),
                      boxShadow: [
                        BoxShadow(
                          color: const Color(0xFF8B5CF6).withOpacity(0.3),
                          blurRadius: 12,
                          offset: const Offset(0, 4),
                        ),
                      ],
                    ),
                    child: const Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Text('🤟', style: TextStyle(fontSize: 22)),
                        SizedBox(width: 8),
                        Text(
                          'Bắt đầu ký hiệu',
                          style: TextStyle(
                            fontFamily: 'Outfit',
                            fontSize: 16,
                            fontWeight: FontWeight.w700,
                            color: Colors.white,
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            )
          else ...[
            // Stop recording
            Semantics(
              label: 'Dừng quay',
              button: true,
              child: GestureDetector(
                onTap: _stopRecording,
                child: Container(
                  width: 52,
                  height: 52,
                  decoration: BoxDecoration(
                    color: const Color(0xFFEF4444).withOpacity(0.15),
                    borderRadius: BorderRadius.circular(16),
                    border: Border.all(
                      color: const Color(0xFFEF4444).withOpacity(0.4),
                    ),
                  ),
                  child: const Icon(
                    Icons.stop_rounded,
                    color: Color(0xFFEF4444),
                    size: 28,
                  ),
                ),
              ),
            ),
            const SizedBox(width: 8),
            // Submit signs
            Expanded(
              child: Semantics(
                label: 'Gửi ${_recognizedSigns.length} ký hiệu để nhận kết quả',
                button: true,
                enabled: _recognizedSigns.isNotEmpty,
                child: GestureDetector(
                  onTap: _recognizedSigns.isNotEmpty ? _submitSigns : null,
                  child: AnimatedContainer(
                    duration: const Duration(milliseconds: 200),
                    height: 52,
                    decoration: BoxDecoration(
                      gradient: _recognizedSigns.isNotEmpty
                          ? const LinearGradient(
                              colors: [
                                Color(0xFF0D9488),
                                Color(0xFF14B8A6),
                              ],
                            )
                          : null,
                      color: _recognizedSigns.isEmpty
                          ? Colors.white.withOpacity(0.06)
                          : null,
                      borderRadius: BorderRadius.circular(16),
                    ),
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Text(
                          _recognizedSigns.isNotEmpty ? '✅' : '❓',
                          style: const TextStyle(fontSize: 20),
                        ),
                        const SizedBox(width: 8),
                        Text(
                          _recognizedSigns.isNotEmpty
                              ? 'Gửi (${_recognizedSigns.length})'
                              : 'Chờ ký hiệu...',
                          style: TextStyle(
                            fontFamily: 'Outfit',
                            fontSize: 15,
                            fontWeight: FontWeight.w700,
                            color: _recognizedSigns.isNotEmpty
                                ? Colors.white
                                : Colors.white38,
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            ),
          ],
        ],
      ),
    );
  }
}

enum _SignState {
  ready,
  recording,
  recognized,
  processing,
}

/// Data class for a recognized sign language gesture.
class RecognizedSign {
  const RecognizedSign({
    required this.emoji,
    required this.label,
    required this.confidence,
  });

  final String emoji;
  final String label;
  final double confidence;
}
