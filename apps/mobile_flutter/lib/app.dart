import 'package:flutter/material.dart';

import 'core/models/health_profile.dart';
import 'core/network/api_contracts.dart';
import 'core/network/api_scope.dart';
import 'core/network/http_api.dart';
import 'core/network/mock_api.dart';
import 'core/services/accessibility_config.dart';
import 'core/services/auth_service.dart';
import 'core/services/soul_garden_service.dart';
import 'features/auth/presentation/welcome_auth_page.dart';
import 'features/home/presentation/home_shell.dart';
import 'features/onboarding/presentation/health_survey_page.dart';

class MediSignApp extends StatefulWidget {
  const MediSignApp({super.key});

  @override
  State<MediSignApp> createState() => _MediSignAppState();
}

class _MediSignAppState extends State<MediSignApp> {
  // Build-time switch — pass `--dart-define=USE_MOCK_API=true` to keep the
  // old offline behaviour when the backend is not running. Defaults to the
  // real HTTP client so production builds talk to FastAPI by default.
  static const bool _useMockApi = bool.fromEnvironment(
    'USE_MOCK_API',
    defaultValue: false,
  );

  /// Single auth instance shared across the app. Owns the access/refresh
  /// tokens and exposes [tokens?.accessToken] for HTTP API providers.
  late final AuthService _auth = AuthService();

  /// Lazy bearer-token provider used by HTTP APIs. Returns `null` when the
  /// user isn't authenticated yet, so the helper omits `Authorization`.
  String? _accessToken() => _auth.tokens?.accessToken;

  late final ConsultApi _consultApi = _useMockApi
      ? MockConsultApi()
      : HttpConsultApi(accessTokenProvider: _accessToken);
  late final MedicineApi _medicineApi = _useMockApi
      ? MockMedicineApi()
      : HttpMedicineApi(accessTokenProvider: _accessToken);
  late final CabinetApi _cabinetApi =
      HttpCabinetApi(accessTokenProvider: _accessToken);
  late final JournalApi _journalApi =
      HttpJournalApi(accessTokenProvider: _accessToken);

  bool _authComplete = false;
  bool _surveyComplete = false;

  // Populated after health survey
  HealthProfile _healthProfile = const HealthProfile();

  @override
  void initState() {
    super.initState();
    // React to auth state changes: bootstrap or detach Soul Garden sync.
    _auth.addListener(_handleAuthChange);
    // Best-effort hydrate if there's a stored session from a previous run.
    _auth.initialize();
  }

  @override
  void dispose() {
    _auth.removeListener(_handleAuthChange);
    super.dispose();
  }

  void _handleAuthChange() {
    if (_useMockApi) return;
    if (_auth.isAuthenticated) {
      SoulGardenService.instance.bindBackend(_journalApi);
      // Fire-and-forget: refresh from cloud in the background.
      SoulGardenService.instance.bootstrap();
    } else {
      SoulGardenService.instance.bindBackend(null);
    }

    // Gate: chỉ user đã đăng nhập mới được vào trang chủ (HomeShell).
    // - Cold start với session đã lưu → tự bật `_authComplete = true` để
    //   không bắt user đi qua màn welcome lần nữa.
    // - Logout / token hết hạn không refresh được → ép `_authComplete = false`
    //   và `_surveyComplete = false` để đẩy về welcome page ngay.
    if (mounted) {
      setState(() {
        if (_auth.isAuthenticated) {
          _authComplete = true;
        } else {
          _authComplete = false;
          _surveyComplete = false;
        }
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return ApiScope(
      cabinet: _cabinetApi,
      journal: _journalApi,
      child: MaterialApp(
        title: 'MediSign AI',
        debugShowCheckedModeBanner: false,
        theme: ThemeData(
          colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xFF3D8A5A)),
          fontFamily: 'Outfit',
          useMaterial3: true,
        ),
        home: _buildHome(),
      ),
    );
  }

  Widget _buildHome() {
    // Flow gate: AUTH → SURVEY → HOME.
    //
    // Trang chủ (HomeShell) chỉ truy cập được khi user đã đăng nhập. Cả 2
    // điều kiện dưới đây phải đồng thời true:
    //   1. `_authComplete` — user đã hoàn thành luồng welcome/login/register
    //      (hoặc cold start có session khôi phục được, set bởi
    //      `_handleAuthChange`).
    //   2. `_auth.isAuthenticated` — token còn hiệu lực. Khi token hết hạn
    //      mà refresh fail, AuthService gọi `logout()` → notifyListeners()
    //      → `_handleAuthChange` reset `_authComplete=false` → user về
    //      welcome page ngay lập tức.
    //
    // Trong mock mode (`USE_MOCK_API=true`), bỏ qua check
    // `_auth.isAuthenticated` để dev offline test UI mà không cần backend.
    final authPassed = _useMockApi || _auth.isAuthenticated;

    // Step 1: Authentication
    if (!_authComplete || !authPassed) {
      return WelcomeAuthPage(
        authService: _auth,
        onAuthComplete: () {
          setState(() => _authComplete = true);
        },
      );
    }

    // Step 2: Health Survey (consolidates old onboarding + communication setup)
    if (!_surveyComplete) {
      return HealthSurveyPage(
        onBack: () {
          setState(() => _authComplete = false);
        },
        onComplete: (profile) {
          AccessibilityConfig.instance.update(profile.difficulties);
          setState(() {
            _healthProfile = profile;
            _surveyComplete = true;
          });
        },
      );
    }

    // Step 3: Main app with 4-tab navigation
    return HomeShell(
      mode: _healthProfile.consultMode,
      communicationMethods: _healthProfile.communicationMethods,
      healthProfile: _healthProfile,
      consultApi: _consultApi,
      medicineApi: _medicineApi,
      authService: _auth,
      onResetOnboarding: () {
        setState(() => _surveyComplete = false);
      },
      onResetCommunication: () {
        setState(() => _surveyComplete = false);
      },
      onLoggedOut: () {
        setState(() {
          _authComplete = false;
          _surveyComplete = false;
          _healthProfile = const HealthProfile();
        });
      },
    );
  }
}
