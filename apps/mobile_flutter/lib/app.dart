import 'package:flutter/material.dart';

import 'core/models/health_profile.dart';
import 'core/network/mock_api.dart';
import 'core/services/accessibility_config.dart';
import 'features/auth/presentation/welcome_auth_page.dart';
import 'features/home/presentation/home_shell.dart';
import 'features/onboarding/presentation/health_survey_page.dart';

class MediSignApp extends StatefulWidget {
  const MediSignApp({super.key});

  @override
  State<MediSignApp> createState() => _MediSignAppState();
}

class _MediSignAppState extends State<MediSignApp> {
  final _consultApi = MockConsultApi();
  final _medicineApi = MockMedicineApi();

  bool _authComplete = false;
  bool _surveyComplete = false;

  // Populated after health survey
  HealthProfile _healthProfile = const HealthProfile();

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'MediSign AI',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xFF3D8A5A)),
        fontFamily: 'Outfit',
        useMaterial3: true,
      ),
      home: _buildHome(),
    );
  }

  Widget _buildHome() {
    // Flow: Auth → Health Survey (7 steps) → Home

    // Step 1: Authentication
    if (!_authComplete) {
      return WelcomeAuthPage(
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
      onResetOnboarding: () {
        setState(() => _surveyComplete = false);
      },
      onResetCommunication: () {
        setState(() => _surveyComplete = false);
      },
    );
  }
}
