import 'dart:async';

/// ══════════════════════════════════════════════════════════════
/// SPEECH SERVICE — Skeleton for Speech-to-Text (STT) & Text-to-Speech (TTS)
/// ══════════════════════════════════════════════════════════════
///
/// HOW TO INTEGRATE REAL AI:
/// 1. Add packages to pubspec.yaml:
///    - speech_to_text: ^6.6.0    (STT)
///    - flutter_tts: ^4.0.2       (TTS)
///
/// 2. Create `RealSpeechService` that implements `SpeechService`
///
/// 3. In app.dart or your DI setup, replace:
///    MockSpeechService() → RealSpeechService()
///
/// That's it! All widgets already use the SpeechService interface.
/// ══════════════════════════════════════════════════════════════

/// Callback types for speech events.
typedef OnSpeechResult = void Function(String transcript, bool isFinal);
typedef OnSpeechError = void Function(String error);

/// Abstract interface for speech services.
/// Implement this to swap in your real AI.
abstract class SpeechService {
  // ── STT (Speech-to-Text) ──

  /// Initialize STT engine. Call once at app start or before first use.
  Future<bool> initSTT();

  /// Is the STT engine currently listening?
  bool get isListening;

  /// Is STT available on this device?
  Future<bool> get isSTTAvailable;

  /// Start listening to microphone.
  /// [onResult] fires each time a partial or final transcript is ready.
  /// [onError] fires if something goes wrong.
  /// [localeId] — language code, e.g. 'vi_VN' for Vietnamese.
  Future<void> startListening({
    required OnSpeechResult onResult,
    OnSpeechError? onError,
    String localeId = 'vi_VN',
  });

  /// Stop listening.
  Future<void> stopListening();

  /// Cancel listening (discard partial results).
  Future<void> cancelListening();

  // ── TTS (Text-to-Speech) ──

  /// Initialize TTS engine. Call once at app start or before first use.
  Future<bool> initTTS();

  /// Is the TTS engine currently speaking?
  bool get isSpeaking;

  /// Speak the given text aloud.
  /// [language] — language code, e.g. 'vi-VN' for Vietnamese.
  /// [rate] — speech rate, 0.0 to 1.0 (default 0.5).
  /// [pitch] — voice pitch, 0.5 to 2.0 (default 1.0).
  Future<void> speak(
    String text, {
    String language = 'vi-VN',
    double rate = 0.5,
    double pitch = 1.0,
  });

  /// Stop speaking immediately.
  Future<void> stopSpeaking();

  /// Get list of available languages.
  Future<List<String>> getAvailableLanguages();

  /// Release all resources.
  void dispose();
}

/// ══════════════════════════════════════════════════════════════
/// MOCK IMPLEMENTATION — Replace with RealSpeechService later.
/// ══════════════════════════════════════════════════════════════
class MockSpeechService implements SpeechService {
  bool _isListening = false;
  bool _isSpeaking = false;
  Timer? _mockTimer;

  // ── STT ──

  @override
  Future<bool> initSTT() async {
    // TODO: Replace with real STT initialization
    // Example with speech_to_text package:
    //   final speech = stt.SpeechToText();
    //   return await speech.initialize();
    await Future.delayed(const Duration(milliseconds: 200));
    return true;
  }

  @override
  bool get isListening => _isListening;

  @override
  Future<bool> get isSTTAvailable async => true;

  @override
  Future<void> startListening({
    required OnSpeechResult onResult,
    OnSpeechError? onError,
    String localeId = 'vi_VN',
  }) async {
    _isListening = true;

    // TODO: Replace with real STT
    // Example with speech_to_text package:
    //   await _speech.listen(
    //     onResult: (result) {
    //       onResult(result.recognizedWords, result.finalResult);
    //     },
    //     localeId: localeId,
    //     listenMode: stt.ListenMode.dictation,
    //   );

    // ── Mock: simulate partial results then final result ──
    final mockPhrases = [
      'Tôi bị',
      'Tôi bị đau đầu',
      'Tôi bị đau đầu và sốt',
      'Tôi bị đau đầu và sốt từ hôm qua',
      'Tôi bị đau đầu và sốt từ hôm qua, kèm theo ho và mệt mỏi',
    ];

    int i = 0;
    _mockTimer = Timer.periodic(const Duration(milliseconds: 800), (timer) {
      if (i < mockPhrases.length - 1) {
        onResult(mockPhrases[i], false); // partial
        i++;
      } else {
        onResult(mockPhrases[i], true); // final
        timer.cancel();
        _isListening = false;
      }
    });
  }

  @override
  Future<void> stopListening() async {
    _mockTimer?.cancel();
    _isListening = false;

    // TODO: Replace with real STT
    // await _speech.stop();
  }

  @override
  Future<void> cancelListening() async {
    _mockTimer?.cancel();
    _isListening = false;

    // TODO: Replace with real STT
    // await _speech.cancel();
  }

  // ── TTS ──

  @override
  Future<bool> initTTS() async {
    // TODO: Replace with real TTS initialization
    // Example with flutter_tts package:
    //   _tts = FlutterTts();
    //   await _tts.setLanguage('vi-VN');
    //   await _tts.setSpeechRate(0.5);
    //   await _tts.setPitch(1.0);
    await Future.delayed(const Duration(milliseconds: 100));
    return true;
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
    _isSpeaking = true;

    // TODO: Replace with real TTS
    // Example with flutter_tts package:
    //   await _tts.setLanguage(language);
    //   await _tts.setSpeechRate(rate);
    //   await _tts.setPitch(pitch);
    //   await _tts.speak(text);

    // ── Mock: simulate speaking duration based on text length ──
    final duration = Duration(milliseconds: text.length * 50);
    await Future.delayed(duration);
    _isSpeaking = false;
  }

  @override
  Future<void> stopSpeaking() async {
    _isSpeaking = false;

    // TODO: Replace with real TTS
    // await _tts.stop();
  }

  @override
  Future<List<String>> getAvailableLanguages() async {
    // TODO: Replace with real TTS
    // return await _tts.getLanguages;
    return ['vi-VN', 'en-US'];
  }

  @override
  void dispose() {
    _mockTimer?.cancel();

    // TODO: Replace with real cleanup
    // _speech.cancel();
    // _tts.stop();
  }
}
