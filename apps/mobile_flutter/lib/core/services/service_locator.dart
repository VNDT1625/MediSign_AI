import 'emergency_service.dart';
import 'real_speech_service.dart';
import 'real_triage_service.dart';
import 'sign_language_service.dart';
import 'social_service.dart';
import 'speech_service.dart';
import 'triage_service.dart';

/// ══════════════════════════════════════════════════════════════
/// SERVICE LOCATOR — Central registry for all AI services.
/// ══════════════════════════════════════════════════════════════
///
/// HOW TO SWAP MOCK → REAL:
/// Just change the implementation in this file. No other changes needed!
///
/// Example — to use real speech service:
///   BEFORE: SpeechService get speech => _speech ??= MockSpeechService();
///   AFTER:  SpeechService get speech => _speech ??= RealSpeechService();
///
/// All widgets use ServiceLocator.instance.speech (etc.), so they
/// automatically pick up the new implementation.
/// ══════════════════════════════════════════════════════════════
class ServiceLocator {
  ServiceLocator._();

  /// Singleton instance.
  static final ServiceLocator instance = ServiceLocator._();

  // ── Lazy-initialized services ──

  SpeechService? _speech;
  SignLanguageService? _signLanguage;
  TriageService? _triage;
  EmergencyService? _emergency;
  SocialService? _social;

  /// 🎤 Speech-to-Text & Text-to-Speech.
  SpeechService get speech => _speech ??= RealSpeechService();

  /// 🤟 Sign language recognition.
  ///
  /// TODO: Replace MockSignLanguageService with your real implementation.
  SignLanguageService get signLanguage =>
      _signLanguage ??= MockSignLanguageService();

  /// 🧠 AI triage analysis.
  TriageService get triage => _triage ??= RealTriageService();

  /// 🆘 Emergency call service.
  EmergencyService get emergency => _emergency ??= EmergencyService();

  /// 👥 Community/Social features.
  SocialService get social => _social ??= MockSocialService();

  /// Initialize all services. Call once at app startup.
  Future<void> initAll() async {
    await Future.wait([
      speech.initSTT(),
      speech.initTTS(),
      signLanguage.initialize(),
      triage.initialize(),
      social.initialize(),
    ]);
  }

  /// Override a service (useful for testing or runtime swapping).
  void overrideSpeech(SpeechService service) {
    _speech?.dispose();
    _speech = service;
  }

  void overrideSignLanguage(SignLanguageService service) {
    _signLanguage?.dispose();
    _signLanguage = service;
  }

  void overrideTriage(TriageService service) {
    _triage?.dispose();
    _triage = service;
  }

  void overrideSocial(SocialService service) {
    _social?.dispose();
    _social = service;
  }

  /// Dispose all services.
  void disposeAll() {
    _speech?.dispose();
    _signLanguage?.dispose();
    _triage?.dispose();
    _social?.dispose();
    _speech = null;
    _signLanguage = null;
    _triage = null;
    _social = null;
    _emergency = null;
  }
}
