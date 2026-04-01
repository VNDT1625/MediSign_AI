import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import '../../../core/models/communication_mode.dart';
import '../../../core/models/consult_mode.dart';
import '../../../core/models/health_profile.dart';
import '../../auth/presentation/auth_theme.dart';

/// 7-step onboarding health survey wizard.
///
/// Steps:
///  1. Tuổi (Age)
///  2. Giới tính (Gender)
///  3. Dị ứng thuốc (Drug allergies)
///  4. Bệnh nền (Pre-existing conditions)
///  5. Khó khăn (Difficulties / disabilities)
///  6. Chế độ hoạt động (Operating mode)
///  7. Phương thức giao tiếp (Communication method)
class HealthSurveyPage extends StatefulWidget {
  const HealthSurveyPage({
    super.key,
    required this.onComplete,
    this.onBack,
  });

  final ValueChanged<HealthProfile> onComplete;
  final VoidCallback? onBack;

  @override
  State<HealthSurveyPage> createState() => _HealthSurveyPageState();
}

class _HealthSurveyPageState extends State<HealthSurveyPage> {
  final _pageController = PageController();
  int _currentStep = 0;
  static const _totalSteps = 7;

  // Step 1: Age
  final _ageController = TextEditingController();

  // Step 2: Gender
  Gender? _selectedGender;

  // Step 3: Drug allergies
  final _allergyController = TextEditingController();
  final List<String> _drugAllergies = [];

  // Step 4: Pre-existing conditions
  final Set<PreCondition> _preConditions = {};

  // Step 5: Difficulties
  final Set<Difficulty> _difficulties = {};

  // Step 6: Consult mode
  ConsultMode _consultMode = ConsultMode.hybrid;

  // Step 7: Communication methods
  final Set<CommunicationMethod> _commMethods = {CommunicationMethod.tap};

  @override
  void dispose() {
    _pageController.dispose();
    _ageController.dispose();
    _allergyController.dispose();
    super.dispose();
  }

  void _goNext() {
    if (_currentStep < _totalSteps - 1) {
      HapticFeedback.lightImpact();
      setState(() => _currentStep++);
      _pageController.nextPage(
        duration: const Duration(milliseconds: 400),
        curve: Curves.easeInOut,
      );
    } else {
      _finish();
    }
  }

  void _goBack() {
    if (_currentStep > 0) {
      setState(() => _currentStep--);
      _pageController.previousPage(
        duration: const Duration(milliseconds: 400),
        curve: Curves.easeInOut,
      );
    } else {
      widget.onBack?.call();
    }
  }

  void _finish() {
    HapticFeedback.mediumImpact();
    final profile = HealthProfile(
      age: int.tryParse(_ageController.text),
      gender: _selectedGender,
      drugAllergies: List.unmodifiable(_drugAllergies),
      preConditions: Set.unmodifiable(_preConditions),
      difficulties: Set.unmodifiable(_difficulties),
      consultMode: _consultMode,
      communicationMethods: Set.unmodifiable(_commMethods),
    );
    widget.onComplete(profile);
  }

  bool get _canProceed {
    switch (_currentStep) {
      case 0:
        return _ageController.text.isNotEmpty;
      case 1:
        return _selectedGender != null;
      case 6:
        return _commMethods.isNotEmpty;
      default:
        return true; // Steps 2-5 can be skipped
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: AuthTheme.gradientBackground(
        child: SafeArea(
          child: Column(
            children: [
              _buildHeader(),
              _buildProgress(),
              Expanded(
                child: PageView(
                  controller: _pageController,
                  physics: const NeverScrollableScrollPhysics(),
                  children: [
                    _buildAgeStep(),
                    _buildGenderStep(),
                    _buildAllergyStep(),
                    _buildConditionsStep(),
                    _buildDifficultiesStep(),
                    _buildModeStep(),
                    _buildCommStep(),
                  ],
                ),
              ),
              _buildBottomButtons(),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildHeader() {
    return Padding(
      padding: const EdgeInsets.fromLTRB(20, 12, 20, 0),
      child: Row(
        children: [
          GestureDetector(
            onTap: _goBack,
            child: const Icon(Icons.arrow_back_ios_new_rounded,
                color: Colors.white70, size: 20),
          ),
          const SizedBox(width: 12),
          Text(
            'Câu hỏi ${_currentStep + 1}/$_totalSteps',
            style: AuthTheme.subtitle,
          ),
          const Spacer(),
          if (_currentStep < _totalSteps - 1 && _currentStep > 1)
            GestureDetector(
              onTap: _goNext,
              child:
                  Text('Bỏ qua', style: AuthTheme.link.copyWith(fontSize: 14)),
            ),
        ],
      ),
    );
  }

  Widget _buildProgress() {
    return Padding(
      padding: const EdgeInsets.fromLTRB(20, 16, 20, 8),
      child: Row(
        children: List.generate(_totalSteps, (i) {
          return Expanded(
            child: Container(
              height: 4,
              margin: const EdgeInsets.symmetric(horizontal: 2),
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(2),
                color: i <= _currentStep
                    ? AuthTheme.primaryLight
                    : Colors.white.withOpacity(0.15),
              ),
            ),
          );
        }),
      ),
    );
  }

  Widget _buildBottomButtons() {
    return Padding(
      padding: const EdgeInsets.fromLTRB(24, 8, 24, 20),
      child: AuthTheme.primaryButton(
        text: _currentStep == _totalSteps - 1 ? 'Hoàn tất' : 'Tiếp tục',
        icon: _currentStep == _totalSteps - 1
            ? Icons.check_rounded
            : Icons.arrow_forward_rounded,
        onPressed: _canProceed ? _goNext : null,
      ),
    );
  }

  // ──────────────────────────────
  // STEP 1: AGE
  // ──────────────────────────────
  Widget _buildAgeStep() {
    return SingleChildScrollView(
      padding: const EdgeInsets.fromLTRB(24, 24, 24, 0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text('🎂', style: TextStyle(fontSize: 48)),
          const SizedBox(height: 16),
          const Text('Bạn bao nhiêu tuổi?', style: AuthTheme.h2),
          const SizedBox(height: 8),
          const Text(
            'Giúp AI đưa lời khuyên phù hợp với độ tuổi',
            style: AuthTheme.subtitle,
          ),
          const SizedBox(height: 32),
          AuthTheme.inputField(
            controller: _ageController,
            hint: 'Nhập tuổi (VD: 25)',
            prefixIcon: Icons.cake_outlined,
            keyboardType: TextInputType.number,
            textInputAction: TextInputAction.done,
          ),
          const SizedBox(height: 16),
          Wrap(
            spacing: 10,
            runSpacing: 10,
            children: [18, 25, 35, 45, 55, 65].map((age) {
              final isSelected = _ageController.text == age.toString();
              return GestureDetector(
                onTap: () {
                  HapticFeedback.selectionClick();
                  _ageController.text = age.toString();
                  setState(() {});
                },
                child: AuthTheme.glassCard(
                  padding:
                      const EdgeInsets.symmetric(horizontal: 20, vertical: 10),
                  borderRadius: 16,
                  isActive: isSelected,
                  child: Text('$age', style: AuthTheme.body),
                ),
              );
            }).toList(),
          ),
        ],
      ),
    );
  }

  // ──────────────────────────────
  // STEP 2: GENDER
  // ──────────────────────────────
  Widget _buildGenderStep() {
    return SingleChildScrollView(
      padding: const EdgeInsets.fromLTRB(24, 24, 24, 0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text('👤', style: TextStyle(fontSize: 48)),
          const SizedBox(height: 16),
          const Text('Giới tính của bạn?', style: AuthTheme.h2),
          const SizedBox(height: 8),
          const Text(
            'Một số triệu chứng khác nhau theo giới tính',
            style: AuthTheme.subtitle,
          ),
          const SizedBox(height: 32),
          ...Gender.values.map((g) => Padding(
                padding: const EdgeInsets.only(bottom: 12),
                child: GestureDetector(
                  onTap: () {
                    HapticFeedback.selectionClick();
                    setState(() => _selectedGender = g);
                  },
                  child: AuthTheme.glassCard(
                    isActive: _selectedGender == g,
                    child: Row(
                      children: [
                        Text(g.emoji, style: const TextStyle(fontSize: 28)),
                        const SizedBox(width: 16),
                        Text(g.label, style: AuthTheme.body),
                        const Spacer(),
                        if (_selectedGender == g)
                          const Icon(Icons.check_circle,
                              color: AuthTheme.primaryLight, size: 24),
                      ],
                    ),
                  ),
                ),
              )),
        ],
      ),
    );
  }

  // ──────────────────────────────
  // STEP 3: DRUG ALLERGIES
  // ──────────────────────────────
  Widget _buildAllergyStep() {
    return SingleChildScrollView(
      padding: const EdgeInsets.fromLTRB(24, 24, 24, 0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text('💊', style: TextStyle(fontSize: 48)),
          const SizedBox(height: 16),
          const Text('Dị ứng thuốc?', style: AuthTheme.h2),
          const SizedBox(height: 8),
          const Text(
            'Nhập tên thuốc bạn bị dị ứng (nếu có)',
            style: AuthTheme.subtitle,
          ),
          const SizedBox(height: 24),
          Row(
            children: [
              Expanded(
                child: AuthTheme.inputField(
                  controller: _allergyController,
                  hint: 'VD: Penicillin',
                  prefixIcon: Icons.medication_outlined,
                  textInputAction: TextInputAction.done,
                ),
              ),
              const SizedBox(width: 12),
              GestureDetector(
                onTap: () {
                  final text = _allergyController.text.trim();
                  if (text.isNotEmpty && !_drugAllergies.contains(text)) {
                    setState(() {
                      _drugAllergies.add(text);
                      _allergyController.clear();
                    });
                  }
                },
                child: AuthTheme.glassCard(
                  padding: const EdgeInsets.all(14),
                  borderRadius: 16,
                  child: const Icon(Icons.add_rounded,
                      color: AuthTheme.primaryLight, size: 24),
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: _drugAllergies
                .map((a) => AuthTheme.glassCard(
                      padding: const EdgeInsets.symmetric(
                          horizontal: 14, vertical: 8),
                      borderRadius: 20,
                      isActive: true,
                      child: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Text(a, style: AuthTheme.body.copyWith(fontSize: 14)),
                          const SizedBox(width: 8),
                          GestureDetector(
                            onTap: () {
                              setState(() => _drugAllergies.remove(a));
                            },
                            child: const Icon(Icons.close,
                                size: 16, color: Colors.white70),
                          ),
                        ],
                      ),
                    ))
                .toList(),
          ),
          if (_drugAllergies.isEmpty) ...[
            const SizedBox(height: 16),
            GestureDetector(
              onTap: _goNext,
              child: AuthTheme.glassCard(
                child: const Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Text('✅', style: TextStyle(fontSize: 24)),
                    SizedBox(width: 12),
                    Text('Không dị ứng thuốc nào', style: AuthTheme.body),
                  ],
                ),
              ),
            ),
          ],
        ],
      ),
    );
  }

  // ──────────────────────────────
  // STEP 4: PRE-EXISTING CONDITIONS
  // ──────────────────────────────
  Widget _buildConditionsStep() {
    return SingleChildScrollView(
      padding: const EdgeInsets.fromLTRB(24, 24, 24, 0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text('🏥', style: TextStyle(fontSize: 48)),
          const SizedBox(height: 16),
          const Text('Bệnh nền hiện có?', style: AuthTheme.h2),
          const SizedBox(height: 8),
          const Text(
            'Chọn các bệnh bạn đang điều trị (có thể chọn nhiều)',
            style: AuthTheme.subtitle,
          ),
          const SizedBox(height: 24),
          ...PreCondition.values.map((c) => Padding(
                padding: const EdgeInsets.only(bottom: 10),
                child: GestureDetector(
                  onTap: () {
                    HapticFeedback.selectionClick();
                    setState(() {
                      if (c == PreCondition.none) {
                        _preConditions.clear();
                        _preConditions.add(PreCondition.none);
                      } else {
                        _preConditions.remove(PreCondition.none);
                        if (_preConditions.contains(c)) {
                          _preConditions.remove(c);
                        } else {
                          _preConditions.add(c);
                        }
                      }
                    });
                  },
                  child: AuthTheme.glassCard(
                    padding: const EdgeInsets.symmetric(
                        horizontal: 16, vertical: 14),
                    isActive: _preConditions.contains(c),
                    child: Row(
                      children: [
                        Text(c.emoji, style: const TextStyle(fontSize: 24)),
                        const SizedBox(width: 14),
                        Text(c.label, style: AuthTheme.body),
                        const Spacer(),
                        if (_preConditions.contains(c))
                          const Icon(Icons.check_circle,
                              color: AuthTheme.primaryLight, size: 22),
                      ],
                    ),
                  ),
                ),
              )),
        ],
      ),
    );
  }

  // ──────────────────────────────
  // STEP 5: DIFFICULTIES
  // ──────────────────────────────
  Widget _buildDifficultiesStep() {
    return SingleChildScrollView(
      padding: const EdgeInsets.fromLTRB(24, 24, 24, 0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text('♿', style: TextStyle(fontSize: 48)),
          const SizedBox(height: 16),
          const Text('Khó khăn trong sinh hoạt?', style: AuthTheme.h2),
          const SizedBox(height: 8),
          const Text(
            'Giúp app điều chỉnh giao diện phù hợp với bạn',
            style: AuthTheme.subtitle,
          ),
          const SizedBox(height: 24),
          ...Difficulty.values.map((d) => Padding(
                padding: const EdgeInsets.only(bottom: 10),
                child: GestureDetector(
                  onTap: () {
                    HapticFeedback.selectionClick();
                    setState(() {
                      if (d == Difficulty.none) {
                        _difficulties.clear();
                        _difficulties.add(Difficulty.none);
                      } else {
                        _difficulties.remove(Difficulty.none);
                        if (_difficulties.contains(d)) {
                          _difficulties.remove(d);
                        } else {
                          _difficulties.add(d);
                        }
                      }
                    });
                  },
                  child: AuthTheme.glassCard(
                    padding: const EdgeInsets.symmetric(
                        horizontal: 16, vertical: 14),
                    isActive: _difficulties.contains(d),
                    child: Row(
                      children: [
                        Text(d.emoji, style: const TextStyle(fontSize: 24)),
                        const SizedBox(width: 14),
                        Expanded(child: Text(d.label, style: AuthTheme.body)),
                        if (_difficulties.contains(d))
                          const Icon(Icons.check_circle,
                              color: AuthTheme.primaryLight, size: 22),
                      ],
                    ),
                  ),
                ),
              )),
        ],
      ),
    );
  }

  // ──────────────────────────────
  // STEP 6: OPERATING MODE
  // ──────────────────────────────
  Widget _buildModeStep() {
    return SingleChildScrollView(
      padding: const EdgeInsets.fromLTRB(24, 24, 24, 0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text('⚙️', style: TextStyle(fontSize: 48)),
          const SizedBox(height: 16),
          const Text('Chế độ hoạt động', style: AuthTheme.h2),
          const SizedBox(height: 8),
          const Text(
            'Chọn cách AI xử lý dữ liệu y tế của bạn',
            style: AuthTheme.subtitle,
          ),
          const SizedBox(height: 24),
          ...ConsultMode.values.map((mode) => Padding(
                padding: const EdgeInsets.only(bottom: 12),
                child: GestureDetector(
                  onTap: () {
                    HapticFeedback.selectionClick();
                    setState(() => _consultMode = mode);
                  },
                  child: AuthTheme.glassCard(
                    isActive: _consultMode == mode,
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            Text(mode.emoji,
                                style: const TextStyle(fontSize: 28)),
                            const SizedBox(width: 12),
                            Expanded(
                              child: Text(mode.title,
                                  style: AuthTheme.body
                                      .copyWith(fontWeight: FontWeight.w600)),
                            ),
                            if (mode.isRecommended)
                              Container(
                                padding: const EdgeInsets.symmetric(
                                    horizontal: 10, vertical: 4),
                                decoration: BoxDecoration(
                                  color: AuthTheme.primary.withOpacity(0.3),
                                  borderRadius: BorderRadius.circular(12),
                                ),
                                child: Text('Gợi ý',
                                    style: AuthTheme.caption.copyWith(
                                        color: AuthTheme.primaryLight)),
                              ),
                          ],
                        ),
                        const SizedBox(height: 6),
                        Padding(
                          padding: const EdgeInsets.only(left: 42),
                          child: Text(mode.description,
                              style: AuthTheme.subtitle.copyWith(fontSize: 13)),
                        ),
                      ],
                    ),
                  ),
                ),
              )),
        ],
      ),
    );
  }

  // ──────────────────────────────
  // STEP 7: COMMUNICATION METHODS
  // ──────────────────────────────
  Widget _buildCommStep() {
    return SingleChildScrollView(
      padding: const EdgeInsets.fromLTRB(24, 24, 24, 0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text('💬', style: TextStyle(fontSize: 48)),
          const SizedBox(height: 16),
          const Text('Cách giao tiếp', style: AuthTheme.h2),
          const SizedBox(height: 8),
          const Text(
            'Chọn cách bạn muốn tương tác với AI (có thể chọn nhiều)',
            style: AuthTheme.subtitle,
          ),
          const SizedBox(height: 24),
          ...CommunicationMethod.values.map((m) => Padding(
                padding: const EdgeInsets.only(bottom: 12),
                child: GestureDetector(
                  onTap: () {
                    HapticFeedback.selectionClick();
                    setState(() {
                      if (_commMethods.contains(m)) {
                        if (_commMethods.length > 1) {
                          _commMethods.remove(m);
                        }
                      } else {
                        _commMethods.add(m);
                      }
                    });
                  },
                  child: AuthTheme.glassCard(
                    isActive: _commMethods.contains(m),
                    child: Row(
                      children: [
                        Text(m.icon, style: const TextStyle(fontSize: 28)),
                        const SizedBox(width: 14),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(m.label,
                                  style: AuthTheme.body
                                      .copyWith(fontWeight: FontWeight.w600)),
                              Text(m.description,
                                  style: AuthTheme.subtitle
                                      .copyWith(fontSize: 12)),
                            ],
                          ),
                        ),
                        if (_commMethods.contains(m))
                          const Icon(Icons.check_circle,
                              color: AuthTheme.primaryLight, size: 24),
                      ],
                    ),
                  ),
                ),
              )),
        ],
      ),
    );
  }
}
