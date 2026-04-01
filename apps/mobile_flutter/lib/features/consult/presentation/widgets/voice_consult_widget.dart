import 'dart:async';
import 'dart:math';

import 'package:flutter/material.dart';
import 'package:flutter/rendering.dart';
import 'package:flutter/services.dart';

import '../../../../core/models/communication_mode.dart';
import '../../../../core/services/service_locator.dart';

/// Voice Consult Widget — for BLIND users.
///
/// Flow:
/// 1. Big pulsing MIC button → user speaks symptoms
/// 2. STT converts speech → shows transcript
/// 3. AI processes → result
/// 4. TTS reads result aloud
///
/// Design principles:
/// - MINIMAL visual elements (blind users don't see)
/// - MAXIMUM audio/haptic feedback
/// - Full `Semantics` for TalkBack/VoiceOver
/// - Large tap targets (entire screen = tap to talk)
/// - Auto-reads everything via TTS
class VoiceConsultWidget extends StatefulWidget {
  const VoiceConsultWidget({
    super.key,
    required this.onResult,
  });

  final ValueChanged<VoiceConsultResult> onResult;

  @override
  State<VoiceConsultWidget> createState() => _VoiceConsultWidgetState();
}

class _VoiceConsultWidgetState extends State<VoiceConsultWidget>
    with TickerProviderStateMixin {
  _VoiceState _state = _VoiceState.idle;
  String _transcript = '';
  final List<String> _conversationHistory = [];

  // Services — from ServiceLocator (swap mock→real in service_locator.dart)
  final _speechService = ServiceLocator.instance.speech;
  final _triageService = ServiceLocator.instance.triage;

  // Animations
  late AnimationController _pulseCtrl;
  late Animation<double> _pulseAnim;
  late AnimationController _waveCtrl;

  // Simulated waveform data
  final List<double> _waveData = List.generate(24, (_) => 0.1);
  Timer? _waveTimer;

  @override
  void initState() {
    super.initState();

    _pulseCtrl = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1500),
    )..repeat(reverse: true);

    _pulseAnim = Tween<double>(begin: 1.0, end: 1.15).animate(
      CurvedAnimation(parent: _pulseCtrl, curve: Curves.easeInOut),
    );

    _waveCtrl = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 100),
    );

    // Auto-announce for screen reader
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _announceForScreenReader(
        'Chế độ giọng nói. Nhấn vào bất kỳ đâu trên màn hình để bắt đầu nói. '
        'Hãy mô tả triệu chứng của bạn bằng giọng nói.',
      );
    });
  }

  @override
  void dispose() {
    _pulseCtrl.dispose();
    _waveCtrl.dispose();
    _waveTimer?.cancel();
    _speechService.cancelListening();
    _speechService.stopSpeaking();
    super.dispose();
  }

  void _announceForScreenReader(String message) {
    SemanticsService.announce(message, TextDirection.ltr);
  }

  void _startListening() {
    if (_state == _VoiceState.listening) return;
    HapticFeedback.heavyImpact();
    setState(() => _state = _VoiceState.listening);
    _announceForScreenReader('Đang nghe. Hãy nói triệu chứng của bạn.');

    // Start waveform animation
    _waveTimer = Timer.periodic(const Duration(milliseconds: 80), (_) {
      if (!mounted || _state != _VoiceState.listening) return;
      setState(() {
        for (var i = 0; i < _waveData.length; i++) {
          _waveData[i] = 0.1 + Random().nextDouble() * 0.8;
        }
      });
    });

    // Use SpeechService for STT
    _speechService.startListening(
      onResult: (transcript, isFinal) {
        if (!mounted) return;
        setState(() => _transcript = transcript);
        if (isFinal) {
          _processTranscript();
        }
      },
      onError: (error) {
        if (!mounted) return;
        setState(() => _state = _VoiceState.idle);
        _announceForScreenReader('Lỗi nhận giọng: $error. Thử lại.');
      },
    );
  }

  void _stopListening() {
    HapticFeedback.mediumImpact();
    _waveTimer?.cancel();
    _speechService.stopListening();

    if (_transcript.isNotEmpty) {
      _processTranscript();
    } else {
      setState(() => _state = _VoiceState.idle);
    }
  }

  Future<void> _processTranscript() async {
    setState(() => _state = _VoiceState.processing);
    _announceForScreenReader(
      'Đã nghe xong. Bạn nói: $_transcript. Đang phân tích...',
    );

    // Use TriageService for AI analysis
    final output = await _triageService.analyzeText(_transcript);
    if (!mounted) return;
    _showResult(output.level, output.summary);
  }

  void _showResult(TriageLevel level, String advice) {
    final result = VoiceConsultResult(
      transcript: _transcript,
      level: level,
      spokenAdvice: advice,
    );

    setState(() {
      _state = _VoiceState.result;
      _conversationHistory.add('Bạn: $_transcript');
      _conversationHistory.add('AI: ${result.spokenAdvice}');
    });

    // Use SpeechService for TTS readback
    _speechService.speak(result.spokenAdvice);
    _announceForScreenReader(result.spokenAdvice);
    HapticFeedback.mediumImpact();

    widget.onResult(result);
  }

  void _resetForNewQuestion() {
    HapticFeedback.lightImpact();
    setState(() {
      _state = _VoiceState.idle;
      _transcript = '';
    });
    _announceForScreenReader(
      'Sẵn sàng nghe câu hỏi mới. Nhấn vào màn hình để nói.',
    );
  }

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      // Entire screen is tappable for blind users
      onTap: _state == _VoiceState.idle || _state == _VoiceState.result
          ? _startListening
          : _state == _VoiceState.listening
              ? _stopListening
              : null,
      child: Container(
        color: Colors.transparent,
        child: Column(
          children: [
            const SizedBox(height: 20),

            // ── Instruction text (also for sighted helpers) ──
            _buildInstruction(),
            const SizedBox(height: 12),

            // ── Conversation history ──
            if (_conversationHistory.isNotEmpty)
              Expanded(child: _buildConversationHistory()),

            if (_conversationHistory.isEmpty) const Spacer(),

            // ── Central microphone area ──
            _buildMicArea(),

            const Spacer(),

            // ── Transcript display ──
            if (_transcript.isNotEmpty) _buildTranscript(),
            const SizedBox(height: 12),

            // ── Bottom hint ──
            _buildBottomHint(),
            const SizedBox(height: 16),
          ],
        ),
      ),
    );
  }

  Widget _buildInstruction() {
    String text;
    String emoji;
    switch (_state) {
      case _VoiceState.idle:
        emoji = '🎤';
        text = 'Chạm màn hình để nói';
        break;
      case _VoiceState.listening:
        emoji = '👂';
        text = 'Đang nghe...';
        break;
      case _VoiceState.processing:
        emoji = '🤔';
        text = 'Đang phân tích...';
        break;
      case _VoiceState.result:
        emoji = '📋';
        text = 'Kết quả — Chạm để hỏi tiếp';
        break;
    }

    return Semantics(
      liveRegion: true,
      label: text,
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 24),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(emoji, style: const TextStyle(fontSize: 28)),
            const SizedBox(width: 10),
            Flexible(
              child: Text(
                text,
                textAlign: TextAlign.center,
                style: const TextStyle(
                  fontFamily: 'Outfit',
                  fontSize: 18,
                  fontWeight: FontWeight.w600,
                  color: Colors.white70,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildMicArea() {
    return AnimatedBuilder(
      animation: _pulseAnim,
      builder: (_, __) {
        final scale = _state == _VoiceState.idle ? _pulseAnim.value : 1.0;
        return Transform.scale(
          scale: scale,
          child: Container(
            width: 140,
            height: 140,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              color: _micColor.withOpacity(0.15),
              border: Border.all(
                color: _micColor.withOpacity(0.5),
                width: 3,
              ),
              boxShadow: [
                BoxShadow(
                  color: _micColor.withOpacity(0.25),
                  blurRadius: 30,
                  spreadRadius: 5,
                ),
              ],
            ),
            child: Center(
              child: _state == _VoiceState.listening
                  ? _buildWaveform()
                  : _state == _VoiceState.processing
                      ? const SizedBox(
                          width: 44,
                          height: 44,
                          child: CircularProgressIndicator(
                            strokeWidth: 3,
                            color: Color(0xFF14B8A6),
                          ),
                        )
                      : Icon(
                          _state == _VoiceState.result
                              ? Icons.replay_rounded
                              : Icons.mic_rounded,
                          size: 56,
                          color: _micColor,
                        ),
            ),
          ),
        );
      },
    );
  }

  Color get _micColor {
    switch (_state) {
      case _VoiceState.idle:
        return const Color(0xFF14B8A6);
      case _VoiceState.listening:
        return const Color(0xFFEF4444);
      case _VoiceState.processing:
        return const Color(0xFFF59E0B);
      case _VoiceState.result:
        return const Color(0xFF22C55E);
    }
  }

  Widget _buildWaveform() {
    return SizedBox(
      width: 100,
      height: 50,
      child: Row(
        mainAxisAlignment: MainAxisAlignment.center,
        crossAxisAlignment: CrossAxisAlignment.center,
        children: List.generate(_waveData.length, (i) {
          return AnimatedContainer(
            duration: const Duration(milliseconds: 60),
            width: 3,
            height: 50 * _waveData[i],
            margin: const EdgeInsets.symmetric(horizontal: 0.5),
            decoration: BoxDecoration(
              color: const Color(0xFFEF4444).withOpacity(0.8),
              borderRadius: BorderRadius.circular(2),
            ),
          );
        }),
      ),
    );
  }

  Widget _buildTranscript() {
    return Semantics(
      label: 'Bạn đã nói: $_transcript',
      child: Container(
        margin: const EdgeInsets.symmetric(horizontal: 20),
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: Colors.white.withOpacity(0.06),
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: Colors.white.withOpacity(0.1)),
        ),
        child: Row(
          children: [
            const Text('💬', style: TextStyle(fontSize: 20)),
            const SizedBox(width: 10),
            Expanded(
              child: Text(
                _transcript,
                style: const TextStyle(
                  fontFamily: 'Outfit',
                  fontSize: 14,
                  color: Colors.white70,
                  fontStyle: FontStyle.italic,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildConversationHistory() {
    return ListView.builder(
      padding: const EdgeInsets.symmetric(horizontal: 20),
      itemCount: _conversationHistory.length,
      itemBuilder: (context, index) {
        final msg = _conversationHistory[index];
        final isUser = msg.startsWith('Bạn:');
        return Padding(
          padding: const EdgeInsets.only(bottom: 8),
          child: Semantics(
            label: msg,
            child: Align(
              alignment:
                  isUser ? Alignment.centerRight : Alignment.centerLeft,
              child: Container(
                constraints: BoxConstraints(
                  maxWidth: MediaQuery.of(context).size.width * 0.75,
                ),
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: isUser
                      ? const Color(0xFF14B8A6).withOpacity(0.15)
                      : const Color(0xFF3B82F6).withOpacity(0.12),
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(
                    color: isUser
                        ? const Color(0xFF14B8A6).withOpacity(0.3)
                        : const Color(0xFF3B82F6).withOpacity(0.2),
                  ),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Text(
                          isUser ? '🗣️' : '🩺',
                          style: const TextStyle(fontSize: 14),
                        ),
                        const SizedBox(width: 6),
                        Text(
                          isUser ? 'Bạn' : 'MediSign AI',
                          style: TextStyle(
                            fontFamily: 'Outfit',
                            fontSize: 11,
                            fontWeight: FontWeight.w700,
                            color: isUser
                                ? const Color(0xFF5EEAD4)
                                : const Color(0xFF93C5FD),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 4),
                    Text(
                      msg.replaceFirst(RegExp(r'^(Bạn|AI): '), ''),
                      style: const TextStyle(
                        fontFamily: 'Outfit',
                        fontSize: 14,
                        color: Colors.white70,
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
        );
      },
    );
  }

  Widget _buildBottomHint() {
    if (_state == _VoiceState.result) {
      return Padding(
        padding: const EdgeInsets.symmetric(horizontal: 24),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            // Ask again
            Semantics(
              label: 'Hỏi câu tiếp',
              button: true,
              child: GestureDetector(
                onTap: _resetForNewQuestion,
                child: Container(
                  padding: const EdgeInsets.symmetric(
                      horizontal: 20, vertical: 10),
                  decoration: BoxDecoration(
                    color: const Color(0xFF14B8A6).withOpacity(0.15),
                    borderRadius: BorderRadius.circular(20),
                    border: Border.all(
                      color: const Color(0xFF14B8A6).withOpacity(0.3),
                    ),
                  ),
                  child: const Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Text('🎤', style: TextStyle(fontSize: 18)),
                      SizedBox(width: 6),
                      Text(
                        'Hỏi tiếp',
                        style: TextStyle(
                          fontFamily: 'Outfit',
                          fontSize: 14,
                          fontWeight: FontWeight.w600,
                          color: Color(0xFF5EEAD4),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
            const SizedBox(width: 12),
            // Listen again (TTS)
            Semantics(
              label: 'Nghe lại kết quả',
              button: true,
              child: GestureDetector(
                onTap: () {
                  HapticFeedback.lightImpact();
                  // Use SpeechService TTS to re-read result
                  final lastAI = _conversationHistory.last
                      .replaceFirst(RegExp(r'^AI: '), '');
                  _speechService.speak(lastAI);
                  _announceForScreenReader(lastAI);
                },
                child: Container(
                  padding: const EdgeInsets.symmetric(
                      horizontal: 20, vertical: 10),
                  decoration: BoxDecoration(
                    color: const Color(0xFF3B82F6).withOpacity(0.12),
                    borderRadius: BorderRadius.circular(20),
                    border: Border.all(
                      color: const Color(0xFF3B82F6).withOpacity(0.2),
                    ),
                  ),
                  child: const Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Text('🔊', style: TextStyle(fontSize: 18)),
                      SizedBox(width: 6),
                      Text(
                        'Nghe lại',
                        style: TextStyle(
                          fontFamily: 'Outfit',
                          fontSize: 14,
                          fontWeight: FontWeight.w600,
                          color: Color(0xFF93C5FD),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ],
        ),
      );
    }

    return Semantics(
      label: _state == _VoiceState.idle
          ? 'Nhấn vào bất kỳ đâu trên màn hình để bắt đầu nói'
          : _state == _VoiceState.listening
              ? 'Nhấn lần nữa để dừng thu âm'
              : 'Đang xử lý',
      child: Text(
        _state == _VoiceState.idle
            ? '👆 Chạm bất kỳ đâu để nói'
            : _state == _VoiceState.listening
                ? '✋ Chạm để dừng'
                : '⏳ Đợi giây lát...',
        style: const TextStyle(
          fontFamily: 'Outfit',
          fontSize: 14,
          color: Colors.white38,
        ),
      ),
    );
  }
}

enum _VoiceState {
  idle,
  listening,
  processing,
  result,
}

/// Result from voice consultation.
class VoiceConsultResult {
  const VoiceConsultResult({
    required this.transcript,
    required this.level,
    required this.spokenAdvice,
  });

  final String transcript;
  final TriageLevel level;
  final String spokenAdvice;
}
