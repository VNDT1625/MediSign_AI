import 'dart:async';

import 'package:flutter/foundation.dart';
import 'package:speech_to_text/speech_to_text.dart' as stt;
import 'package:flutter_tts/flutter_tts.dart';

import 'voice_intents.dart';

/// Trang thai cua VoiceController.
enum VoiceMode { off, wake, command, executing }

/// Callback khi co intent — handler tra ve cau noi cuoi cung de TTS doc.
typedef VoiceIntentHandler = String Function(VoiceIntent intent);

/// Controller dieu khien giong noi cho ca mobile lan desktop.
///
/// Vong doi:
///   1. start()       -> mode = wake, lang nghe lien tuc.
///   2. nghe wake     -> mode = command, ghi am cau lenh.
///   3. final command -> mode = executing, goi handler, doc reply bang TTS.
///   4. TTS xong      -> quay ve wake.
///
/// Tat ca xu ly local (intent matcher), KHONG goi backend AI.
class VoiceController extends ChangeNotifier {
  VoiceController({required this.onIntent});

  final VoiceIntentHandler onIntent;

  final stt.SpeechToText _stt = stt.SpeechToText();
  final FlutterTts _tts = FlutterTts();

  VoiceMode _mode = VoiceMode.off;
  String _transcript = '';
  String _lastReply = '';
  String _lastCommand = '';
  String? _error;
  bool _sttReady = false;
  bool _ttsReady = false;
  bool _isSpeaking = false;
  bool _handled = false;
  Timer? _restartTimer;
  String? _lastIntentKey;
  DateTime? _lastIntentAt;

  VoiceMode get mode => _mode;
  String get transcript => _transcript;
  String get lastReply => _lastReply;
  String get lastCommand => _lastCommand;
  String? get error => _error;
  bool get isSpeaking => _isSpeaking;
  bool get isSupported => _sttReady;

  Future<bool> _ensureInit() async {
    if (!_sttReady) {
      _sttReady = await _stt.initialize(
        onError: (e) {
          _error = e.errorMsg;
          notifyListeners();
        },
        onStatus: (s) {
          // Khi STT bao "done"/"notListening" o wake mode -> tu khoi dong lai
          if ((s == 'done' || s == 'notListening') && _mode == VoiceMode.wake) {
            _scheduleRestart();
          }
        },
      );
    }
    if (!_ttsReady) {
      try {
        await _tts.setLanguage('vi-VN');
        await _tts.setSpeechRate(0.45);
        await _tts.setPitch(1.0);
        _tts.setCompletionHandler(() {
          _isSpeaking = false;
          notifyListeners();
          if (_mode == VoiceMode.executing) {
            // Nho mot khoanh khac roi quay ve wake
            Future.delayed(const Duration(milliseconds: 300), () {
              if (_mode == VoiceMode.executing) _enterWake();
            });
          }
        });
        _tts.setCancelHandler(() {
          _isSpeaking = false;
          notifyListeners();
        });
        _tts.setErrorHandler((msg) {
          _isSpeaking = false;
          _error = 'TTS: $msg';
          notifyListeners();
        });
        _ttsReady = true;
      } catch (e) {
        _error = 'TTS init fail: $e';
      }
    }
    return _sttReady;
  }

  /// Bat controller — vao wake mode.
  Future<void> start() async {
    if (_mode != VoiceMode.off) return;
    final ok = await _ensureInit();
    if (!ok) {
      _error = 'STT khong kha dung tren thiet bi nay.';
      notifyListeners();
      return;
    }
    _enterWake();
  }

  /// Tat hoan toan.
  Future<void> stop() async {
    _restartTimer?.cancel();
    _restartTimer = null;
    _mode = VoiceMode.off;
    await _stt.cancel();
    await _tts.stop();
    _isSpeaking = false;
    notifyListeners();
  }

  /// Phat 1 cau bang TTS (vd: read_page / repeat).
  Future<void> say(String text) async {
    if (text.trim().isEmpty) return;
    await _ensureInit();
    _isSpeaking = true;
    notifyListeners();
    await _tts.speak(text);
  }

  /// Bo qua wake word, vao thang command mode.
  Future<void> beginCommand() async {
    if (!_sttReady) {
      final ok = await _ensureInit();
      if (!ok) return;
    }
    await _stt.cancel();
    await Future.delayed(const Duration(milliseconds: 80));
    _enterCommand();
  }

  void _scheduleRestart() {
    _restartTimer?.cancel();
    _restartTimer = Timer(const Duration(milliseconds: 500), () {
      if (_mode == VoiceMode.wake && !_stt.isListening) {
        _startWakeListen();
      }
    });
  }

  void _enterWake() {
    _mode = VoiceMode.wake;
    _transcript = '';
    _handled = false;
    _error = null;
    notifyListeners();
    _startWakeListen();
  }

  void _enterCommand() {
    _mode = VoiceMode.command;
    _transcript = '';
    _handled = false;
    notifyListeners();
    _startCommandListen();
  }

  Future<void> _startWakeListen() async {
    if (!_sttReady) return;
    if (_stt.isListening) return;
    _transcript = '';
    notifyListeners();
    await _stt.listen(
      onResult: (r) {
        _transcript = r.recognizedWords;
        notifyListeners();
        if (_mode == VoiceMode.wake &&
            !_handled &&
            containsWakeWord(_transcript)) {
          _handled = true;
          final tail = stripWakeWord(_transcript);
          _stt.stop();
          if (tail.isNotEmpty) {
            // Lenh di cung wake word
            _lastCommand = tail;
            _runIntent(matchIntent(tail));
          } else {
            _speak('Mình đang nghe.');
            Future.delayed(const Duration(milliseconds: 350), () {
              if (_mode == VoiceMode.wake) _enterCommand();
            });
          }
        }
      },
      localeId: 'vi_VN',
      listenFor: const Duration(seconds: 30),
      pauseFor: const Duration(seconds: 5),
      listenOptions: stt.SpeechListenOptions(
        partialResults: true,
        cancelOnError: false,
        listenMode: stt.ListenMode.dictation,
      ),
    );
  }

  Future<void> _startCommandListen() async {
    if (!_sttReady) return;
    if (_stt.isListening) await _stt.cancel();
    _transcript = '';
    notifyListeners();
    await _stt.listen(
      onResult: (r) {
        _transcript = r.recognizedWords;
        notifyListeners();
        if (_mode == VoiceMode.command && r.finalResult && !_handled) {
          _handled = true;
          final text = _transcript.trim();
          if (text.isEmpty) {
            _enterWake();
            return;
          }
          _lastCommand = text;
          _runIntent(matchIntent(text));
        }
      },
      localeId: 'vi_VN',
      listenFor: const Duration(seconds: 8),
      pauseFor: const Duration(seconds: 3),
      listenOptions: stt.SpeechListenOptions(
        partialResults: true,
        cancelOnError: true,
        listenMode: stt.ListenMode.dictation,
      ),
    );
  }

  void _runIntent(VoiceIntent intent) {
    final now = DateTime.now();
    final key = '${intent.kind.name}:${intent.normalized}';
    final lastAt = _lastIntentAt;
    if (_lastIntentKey == key &&
        lastAt != null &&
        now.difference(lastAt) < const Duration(seconds: 3)) {
      _enterWake();
      return;
    }
    _lastIntentKey = key;
    _lastIntentAt = now;

    _mode = VoiceMode.executing;
    notifyListeners();
    final reply = onIntent(intent);
    _lastReply = reply;
    notifyListeners();
    _speak(reply);
  }

  Future<void> _speak(String text) async {
    if (!_ttsReady) await _ensureInit();
    if (!_ttsReady || text.trim().isEmpty) {
      // Khong noi duoc -> nhay quay lai wake luon
      if (_mode == VoiceMode.executing) {
        Future.delayed(const Duration(milliseconds: 200), () {
          if (_mode == VoiceMode.executing) _enterWake();
        });
      }
      return;
    }
    _isSpeaking = true;
    notifyListeners();
    await _tts.speak(text);
  }

  @override
  void dispose() {
    _restartTimer?.cancel();
    _stt.cancel();
    _tts.stop();
    super.dispose();
  }
}
