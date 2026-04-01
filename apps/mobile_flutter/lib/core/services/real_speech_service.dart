import 'package:flutter_tts/flutter_tts.dart';
import 'package:speech_to_text/speech_to_text.dart' as stt;
import 'speech_service.dart';

/// ══════════════════════════════════════════════════════════════
/// REAL SPEECH SERVICE — Production implementation using:
///   - speech_to_text ^6.6.0 for STT
///   - flutter_tts ^4.0.0 for TTS
/// ══════════════════════════════════════════════════════════════

class RealSpeechService implements SpeechService {
  stt.SpeechToText? _speech;
  FlutterTts? _tts;

  // Callbacks
  OnSpeechResult? _onResult;
  OnSpeechError? _onError;

  // State
  bool _isListening = false;
  bool _isSpeaking = false;
  bool _sttInitialized = false;
  bool _ttsInitialized = false;

  // ── STT (Speech-to-Text) ──

  @override
  Future<bool> initSTT() async {
    if (_sttInitialized) return true;

    try {
      _speech = stt.SpeechToText();
      final available = await _speech!.initialize(
        onError: (error) {
          _onError?.call(error.errorMsg);
          _isListening = false;
        },
        onStatus: (status) {
          if (status == 'done' || status == 'notListening') {
            _isListening = false;
          }
        },
      );
      _sttInitialized = available;
      return available;
    } catch (e) {
      _onError?.call('Failed to initialize STT: $e');
      return false;
    }
  }

  @override
  bool get isListening => _isListening;

  @override
  Future<bool> get isSTTAvailable async {
    if (!_sttInitialized) {
      await initSTT();
    }
    return _sttInitialized && (_speech?.isAvailable ?? false);
  }

  @override
  Future<void> startListening({
    required OnSpeechResult onResult,
    OnSpeechError? onError,
    String localeId = 'vi_VN',
  }) async {
    if (!_sttInitialized) {
      final initialized = await initSTT();
      if (!initialized) {
        onError?.call('STT not initialized');
        return;
      }
    }

    _onResult = onResult;
    _onError = onError;

    // Check available locales and fall back if needed
    final locales = await _speech?.locales() ?? [];
    final hasLocale = locales.any((l) => l.localeId == localeId);

    final effectiveLocale = hasLocale ? localeId : 'en_US';

    _isListening = true;

    await _speech!.listen(
      onResult: (result) {
        _onResult?.call(result.recognizedWords, result.finalResult);
        if (result.finalResult) {
          _isListening = false;
        }
      },
      localeId: effectiveLocale,
      listenMode: stt.ListenMode.dictation,
      listenFor: const Duration(seconds: 30),
      pauseFor: const Duration(seconds: 3),
      partialResults: true,
      cancelOnError: true,
      listenOptions: stt.SpeechListenOptions(
        partialResults: true,
        cancelOnError: true,
      ),
    );
  }

  @override
  Future<void> stopListening() async {
    await _speech?.stop();
    _isListening = false;
  }

  @override
  Future<void> cancelListening() async {
    await _speech?.cancel();
    _isListening = false;
  }

  // ── TTS (Text-to-Speech) ──

  @override
  Future<bool> initTTS() async {
    if (_ttsInitialized) return true;

    try {
      _tts = FlutterTts();

      // Configure for Vietnamese
      await _tts!.setLanguage('vi-VN');
      await _tts!.setSpeechRate(0.4); // Slower for medical context
      await _tts!.setPitch(1.0);
      await _tts!.setVolume(1.0);

      // Set up completion handler
      _tts!.setCompletionHandler(() {
        _isSpeaking = false;
      });

      _tts!.setCancelHandler(() {
        _isSpeaking = false;
      });

      _tts!.setErrorHandler((msg) {
        _isSpeaking = false;
        _onError?.call('TTS Error: $msg');
      });

      _ttsInitialized = true;
      return true;
    } catch (e) {
      _onError?.call('Failed to initialize TTS: $e');
      return false;
    }
  }

  @override
  bool get isSpeaking => _isSpeaking;

  @override
  Future<void> speak(
    String text, {
    String language = 'vi-VN',
    double rate = 0.5,
    double pitch = 1.0,
  }) async {
    if (!_ttsInitialized) {
      await initTTS();
    }

    // Re-apply settings (may have been reset)
    await _tts?.setLanguage(language);
    await _tts?.setSpeechRate(rate);
    await _tts?.setPitch(pitch);

    _isSpeaking = true;
    await _tts?.speak(text);
  }

  @override
  Future<void> stopSpeaking() async {
    await _tts?.stop();
    _isSpeaking = false;
  }

  @override
  Future<List<String>> getAvailableLanguages() async {
    if (_tts == null) {
      await initTTS();
    }

    final languages = await _tts?.getLanguages;
    return languages?.cast<String>() ?? [];
  }

  @override
  void dispose() {
    _speech?.cancel();
    _speech = null;
    _tts?.stop();
    _tts = null;
    _sttInitialized = false;
    _ttsInitialized = false;
  }
}
