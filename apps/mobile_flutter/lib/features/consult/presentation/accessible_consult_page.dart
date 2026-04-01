
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import '../../../core/models/communication_mode.dart';
import '../../../core/services/emergency_service.dart';
import 'widgets/body_map_widget.dart';
import 'widgets/sign_language_widget.dart';
import 'widgets/symptom_pickers.dart';
import 'widgets/triage_result_view.dart';
import 'widgets/voice_consult_widget.dart';

/// Accessible Consult Page — Multi-modal symptom consultation.
///
/// Adapts to user's selected communication method:
/// - 👆 TAP: Body Map → Symptom Icons → Severity → Duration → Result
/// - 🎤 VOICE: Mic → STT → AI → TTS result
/// - 🤟 SIGN: Camera → Sign recognition → AI → Pictogram result
///
/// Users can switch modes at any time via the mode selector bar.
class AccessibleConsultPage extends StatefulWidget {
  const AccessibleConsultPage({
    super.key,
    required this.onBack,
  });

  final VoidCallback onBack;

  @override
  State<AccessibleConsultPage> createState() => _AccessibleConsultPageState();
}

class _AccessibleConsultPageState extends State<AccessibleConsultPage>
    with TickerProviderStateMixin {
  // ── Active mode ──
  _ConsultMode _activeMode = _ConsultMode.tap;

  // ── TAP mode state ──
  int _currentStep = 0;
  static const int _totalSteps = 4;
  final Set<BodyRegion> _selectedRegions = {};
  final Set<SymptomIcon> _selectedSymptoms = {};
  Severity? _severity;
  SymptomDuration? _duration;

  // ── Processing / result state ──
  bool _isProcessing = false;
  bool _showResult = false;

  // ── Animation ──
  late AnimationController _pulseCtrl;
  late Animation<double> _pulseAnim;

  @override
  void initState() {
    super.initState();
    _pulseCtrl = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1200),
    )..repeat(reverse: true);
    _pulseAnim = Tween<double>(begin: 0.95, end: 1.05).animate(
      CurvedAnimation(parent: _pulseCtrl, curve: Curves.easeInOut),
    );
  }

  @override
  void dispose() {
    _pulseCtrl.dispose();
    super.dispose();
  }

  // ── TAP mode helpers ──

  bool get _canProceed {
    switch (_currentStep) {
      case 0:
        return _selectedRegions.isNotEmpty;
      case 1:
        return _selectedSymptoms.isNotEmpty;
      case 2:
        return _severity != null;
      case 3:
        return _duration != null;
      default:
        return false;
    }
  }

  void _nextStep() {
    if (!_canProceed) return;
    HapticFeedback.mediumImpact();
    if (_currentStep < _totalSteps - 1) {
      setState(() => _currentStep++);
    } else {
      _processConsultation();
    }
  }

  void _prevStep() {
    HapticFeedback.lightImpact();
    if (_currentStep > 0) {
      setState(() => _currentStep--);
    } else {
      widget.onBack();
    }
  }

  Future<void> _processConsultation() async {
    setState(() => _isProcessing = true);
    await Future.delayed(const Duration(milliseconds: 2500));
    if (!mounted) return;
    setState(() {
      _isProcessing = false;
      _showResult = true;
    });
  }

  TriageLevel _calculateTriage() {
    if (_severity == Severity.critical ||
        _selectedSymptoms.contains(SymptomIcon.chestPain) ||
        _selectedSymptoms.contains(SymptomIcon.bleeding) ||
        _selectedSymptoms.contains(SymptomIcon.breathless)) {
      return TriageLevel.red;
    }
    if (_severity == Severity.severe ||
        _selectedSymptoms.length >= 4 ||
        _duration == SymptomDuration.moreThanWeek) {
      return TriageLevel.yellow;
    }
    return TriageLevel.green;
  }

  List<AdviceItem> _generateAdvice() {
    final level = _calculateTriage();
    switch (level) {
      case TriageLevel.green:
        return const [
          AdviceItem(
              emoji: '💧',
              title: 'Uống nhiều nước',
              description: 'Ít nhất 2 lít mỗi ngày',
              color: Color(0xFF22C55E)),
          AdviceItem(
              emoji: '😴',
              title: 'Nghỉ ngơi đầy đủ',
              description: 'Ngủ 7-8 tiếng mỗi đêm',
              color: Color(0xFF8B5CF6)),
          AdviceItem(
              emoji: '🌡️',
              title: 'Theo dõi nhiệt độ',
              description: 'Đo 2 lần/ngày, sáng và tối',
              color: Color(0xFFF59E0B)),
          AdviceItem(
              emoji: '📅',
              title: 'Theo dõi thêm 2-3 ngày',
              description: 'Nếu không đỡ, hãy đi khám',
              color: Color(0xFF3B82F6)),
        ];
      case TriageLevel.yellow:
        return const [
          AdviceItem(
              emoji: '🏥',
              title: 'Nên đi khám bác sĩ',
              description: 'Trong 1-2 ngày tới',
              color: Color(0xFFF59E0B)),
          AdviceItem(
              emoji: '💊',
              title: 'Uống thuốc hạ sốt nếu sốt',
              description: 'Paracetamol theo đúng liều',
              color: Color(0xFF3B82F6)),
          AdviceItem(
              emoji: '📝',
              title: 'Ghi lại triệu chứng',
              description: 'Để kể bác sĩ khi đi khám',
              color: Color(0xFF8B5CF6)),
        ];
      case TriageLevel.red:
        return const [
          AdviceItem(
              emoji: '🚑',
              title: 'ĐI VIỆN NGAY',
              description: 'Gọi 115 hoặc nhờ người đưa đi cấp cứu',
              color: Color(0xFFEF4444)),
          AdviceItem(
              emoji: '📞',
              title: 'Gọi người thân',
              description: 'Nhờ ai đó ở bên cạnh hỗ trợ',
              color: Color(0xFFF59E0B)),
          AdviceItem(
              emoji: '⚠️',
              title: 'KHÔNG tự ý uống thuốc',
              description: 'Chờ bác sĩ chỉ định',
              color: Color(0xFFEF4444)),
        ];
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [Color(0xFF0F172A), Color(0xFF1E293B), Color(0xFF0F172A)],
          ),
        ),
        child: SafeArea(
          child: _showResult
              ? _buildResult()
              : _isProcessing
                  ? _buildProcessing()
                  : Column(
                      children: [
                        // ── Top bar (always visible) ──
                        _buildTopBar(),

                        // ── Mode selector (always visible) ──
                        _buildModeSelector(),
                        const SizedBox(height: 4),

                        // ── Mode content ──
                        Expanded(
                          child: AnimatedSwitcher(
                            duration: const Duration(milliseconds: 300),
                            child: _buildModeContent(),
                          ),
                        ),
                      ],
                    ),
        ),
      ),
    );
  }

  // ══════════════════════════════════════════════════════
  //  TOP BAR
  // ══════════════════════════════════════════════════════

  Widget _buildTopBar() {
    return Padding(
      padding: const EdgeInsets.fromLTRB(8, 8, 8, 0),
      child: Row(
        children: [
          Semantics(
            label: 'Quay lại',
            button: true,
            child: IconButton(
              onPressed: _activeMode == _ConsultMode.tap && _currentStep > 0
                  ? _prevStep
                  : widget.onBack,
              icon: const Icon(Icons.arrow_back_rounded),
              color: Colors.white70,
              iconSize: 28,
            ),
          ),
          const Spacer(),
          // Title
          const Text(
            '🩺 Hỏi bệnh',
            style: TextStyle(
              fontFamily: 'Outfit',
              fontSize: 18,
              fontWeight: FontWeight.w700,
              color: Colors.white,
            ),
          ),
          const Spacer(),
          // Emergency (always visible)
          Semantics(
            label: 'Gọi cấp cứu 115',
            button: true,
            child: GestureDetector(
              onTap: () {
                HapticFeedback.heavyImpact();
                EmergencyService().triggerEmergency(context);
              },
              child: Container(
                padding:
                    const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                decoration: BoxDecoration(
                  color: const Color(0xFFEF4444).withOpacity(0.15),
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(
                      color: const Color(0xFFEF4444).withOpacity(0.3)),
                ),
                child: const Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Text('🆘', style: TextStyle(fontSize: 16)),
                    SizedBox(width: 4),
                    Text('115',
                        style: TextStyle(
                            fontFamily: 'Outfit',
                            fontSize: 13,
                            fontWeight: FontWeight.w700,
                            color: Color(0xFFFCA5A5))),
                  ],
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  // ══════════════════════════════════════════════════════
  //  MODE SELECTOR BAR
  // ══════════════════════════════════════════════════════

  Widget _buildModeSelector() {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      padding: const EdgeInsets.all(4),
      decoration: BoxDecoration(
        color: const Color(0xFF1E293B),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.white.withOpacity(0.06)),
      ),
      child: Row(
        children: _ConsultMode.values.map((mode) {
          final isActive = _activeMode == mode;
          return Expanded(
            child: Semantics(
              label:
                  '${mode.label}. ${isActive ? "Đang dùng" : "Nhấn để chuyển"}.',
              button: true,
              selected: isActive,
              child: GestureDetector(
                onTap: () {
                  HapticFeedback.lightImpact();
                  setState(() => _activeMode = mode);
                },
                child: AnimatedContainer(
                  duration: const Duration(milliseconds: 200),
                  padding: const EdgeInsets.symmetric(vertical: 10),
                  decoration: BoxDecoration(
                    color: isActive
                        ? mode.color.withOpacity(0.2)
                        : Colors.transparent,
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(
                      color: isActive
                          ? mode.color.withOpacity(0.5)
                          : Colors.transparent,
                      width: 1.5,
                    ),
                  ),
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Text(mode.emoji, style: const TextStyle(fontSize: 22)),
                      const SizedBox(height: 2),
                      Text(
                        mode.label,
                        style: TextStyle(
                          fontFamily: 'Outfit',
                          fontSize: 11,
                          fontWeight: FontWeight.w600,
                          color: isActive ? mode.color : Colors.white38,
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
          );
        }).toList(),
      ),
    );
  }

  // ══════════════════════════════════════════════════════
  //  MODE CONTENT ROUTER
  // ══════════════════════════════════════════════════════

  Widget _buildModeContent() {
    switch (_activeMode) {
      case _ConsultMode.tap:
        return _buildTapMode(key: const ValueKey('tap'));
      case _ConsultMode.voice:
        return _buildVoiceMode(key: const ValueKey('voice'));
      case _ConsultMode.sign:
        return _buildSignMode(key: const ValueKey('sign'));
      case _ConsultMode.text:
        return _buildTextMode(key: const ValueKey('text'));
    }
  }

  // ──────────────────────────────────────────────────────
  // 👆 TAP MODE — Body Map wizard
  // ──────────────────────────────────────────────────────

  Widget _buildTapMode({Key? key}) {
    return Column(
      key: key,
      children: [
        _buildProgressDots(),
        const SizedBox(height: 4),
        _buildStepTitle(),
        const SizedBox(height: 8),
        Expanded(child: _buildStepContent()),
        _buildBottomNav(),
      ],
    );
  }

  Widget _buildProgressDots() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 40, vertical: 4),
      child: Row(
        children: List.generate(_totalSteps, (i) {
          final isActive = i == _currentStep;
          final isDone = i < _currentStep;
          return Expanded(
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 3),
              child: AnimatedContainer(
                duration: const Duration(milliseconds: 300),
                height: 5,
                decoration: BoxDecoration(
                  borderRadius: BorderRadius.circular(3),
                  color: isDone
                      ? const Color(0xFF14B8A6)
                      : isActive
                          ? const Color(0xFF14B8A6).withOpacity(0.6)
                          : Colors.white.withOpacity(0.1),
                ),
              ),
            ),
          );
        }),
      ),
    );
  }

  Widget _buildStepTitle() {
    final titles = [
      ('🫵', 'Đau ở đâu?', 'Chạm vào vùng bị đau'),
      ('🤒', 'Triệu chứng gì?', 'Chọn các triệu chứng'),
      ('😣', 'Đau cỡ nào?', 'Chọn mức độ'),
      ('📅', 'Bao lâu rồi?', 'Chọn thời gian'),
    ];
    final (emoji, title, subtitle) = titles[_currentStep];
    return Semantics(
      header: true,
      label: '$title. $subtitle',
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 24),
        child: Column(
          children: [
            Text(emoji, style: const TextStyle(fontSize: 36)),
            const SizedBox(height: 4),
            Text(title,
                style: const TextStyle(
                    fontFamily: 'Outfit',
                    fontSize: 20,
                    fontWeight: FontWeight.w700,
                    color: Colors.white)),
            const SizedBox(height: 2),
            Text(subtitle,
                style: const TextStyle(
                    fontFamily: 'Outfit', fontSize: 13, color: Colors.white54)),
          ],
        ),
      ),
    );
  }

  Widget _buildStepContent() {
    switch (_currentStep) {
      case 0:
        return BodyMapWidget(
          selectedRegions: _selectedRegions,
          onRegionsChanged: (r) => setState(() {
            _selectedRegions
              ..clear()
              ..addAll(r);
          }),
        );
      case 1:
        return SymptomIconPicker(
          selectedSymptoms: _selectedSymptoms,
          onSymptomsChanged: (s) => setState(() {
            _selectedSymptoms
              ..clear()
              ..addAll(s);
          }),
        );
      case 2:
        return Center(
            child: SeverityPicker(
                selected: _severity,
                onChanged: (s) => setState(() => _severity = s)));
      case 3:
        return Center(
            child: DurationPicker(
                selected: _duration,
                onChanged: (d) => setState(() => _duration = d)));
      default:
        return const SizedBox.shrink();
    }
  }

  Widget _buildBottomNav() {
    return Padding(
      padding: const EdgeInsets.fromLTRB(20, 8, 20, 12),
      child: Row(
        children: [
          Semantics(
            label: 'Quay lại bước trước',
            button: true,
            child: GestureDetector(
              onTap: _prevStep,
              child: Container(
                width: 52,
                height: 52,
                decoration: BoxDecoration(
                  color: Colors.white.withOpacity(0.06),
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(color: Colors.white.withOpacity(0.1)),
                ),
                child: const Icon(Icons.arrow_back_rounded,
                    color: Colors.white54, size: 24),
              ),
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Semantics(
              label: _currentStep == _totalSteps - 1
                  ? 'Gửi để nhận kết quả'
                  : 'Tiếp tục',
              button: true,
              enabled: _canProceed,
              child: GestureDetector(
                onTap: _canProceed ? _nextStep : null,
                child: AnimatedContainer(
                  duration: const Duration(milliseconds: 200),
                  height: 52,
                  decoration: BoxDecoration(
                    gradient: _canProceed
                        ? const LinearGradient(
                            colors: [Color(0xFF0D9488), Color(0xFF14B8A6)])
                        : null,
                    color: _canProceed ? null : Colors.white.withOpacity(0.06),
                    borderRadius: BorderRadius.circular(16),
                    boxShadow: _canProceed
                        ? [
                            BoxShadow(
                                color: const Color(0xFF14B8A6).withOpacity(0.3),
                                blurRadius: 12,
                                offset: const Offset(0, 4))
                          ]
                        : [],
                  ),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Text(_currentStep == _totalSteps - 1 ? '✅' : '👉',
                          style: const TextStyle(fontSize: 20)),
                      const SizedBox(width: 8),
                      Text(
                        _currentStep == _totalSteps - 1
                            ? 'Xem kết quả'
                            : 'Tiếp tục',
                        style: TextStyle(
                            fontFamily: 'Outfit',
                            fontSize: 16,
                            fontWeight: FontWeight.w700,
                            color: _canProceed
                                ? Colors.white
                                : Colors.white.withOpacity(0.3)),
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  // ──────────────────────────────────────────────────────
  // 🎤 VOICE MODE
  // ──────────────────────────────────────────────────────

  Widget _buildVoiceMode({Key? key}) {
    return VoiceConsultWidget(
      key: key,
      onResult: (result) {
        // Voice mode handles its own result display internally
      },
    );
  }

  // ──────────────────────────────────────────────────────
  // 🤟 SIGN LANGUAGE MODE
  // ──────────────────────────────────────────────────────

  Widget _buildSignMode({Key? key}) {
    return SignLanguageConsultWidget(
      key: key,
      onSymptomsRecognized: (symptoms) {
        // After sign recognition, show triage result
        setState(() {
          _isProcessing = true;
        });
        Future.delayed(const Duration(seconds: 2), () {
          if (!mounted) return;
          setState(() {
            _isProcessing = false;
            _showResult = true;
            // Default values for sign-recognized consultation
            _severity = Severity.moderate;
            _duration = SymptomDuration.twoDays;
          });
        });
      },
    );
  }

  // ══════════════════════════════════════════════════════
  //  PROCESSING
  // ══════════════════════════════════════════════════════

  Widget _buildProcessing() {
    return Center(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          AnimatedBuilder(
            animation: _pulseAnim,
            builder: (_, __) => Transform.scale(
              scale: _pulseAnim.value,
              child: Container(
                width: 100,
                height: 100,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: const Color(0xFF14B8A6).withOpacity(0.15),
                  border: Border.all(
                      color: const Color(0xFF14B8A6).withOpacity(0.4),
                      width: 2),
                  boxShadow: [
                    BoxShadow(
                        color: const Color(0xFF14B8A6).withOpacity(0.2),
                        blurRadius: 30,
                        spreadRadius: 5)
                  ],
                ),
                child: const Center(
                    child: Text('🩺', style: TextStyle(fontSize: 44))),
              ),
            ),
          ),
          const SizedBox(height: 24),
          const Text('Đang phân tích...',
              style: TextStyle(
                  fontFamily: 'Outfit',
                  fontSize: 18,
                  fontWeight: FontWeight.w600,
                  color: Colors.white70)),
          const SizedBox(height: 8),
          SizedBox(
            width: 180,
            child: ClipRRect(
              borderRadius: BorderRadius.circular(4),
              child: const LinearProgressIndicator(
                  backgroundColor: Color(0xFF1E293B),
                  valueColor: AlwaysStoppedAnimation(Color(0xFF14B8A6))),
            ),
          ),
        ],
      ),
    );
  }

  // ══════════════════════════════════════════════════════
  //  RESULT
  // ══════════════════════════════════════════════════════

  Widget _buildResult() {
    final level = _calculateTriage();
    return Column(
      children: [
        Padding(
          padding: const EdgeInsets.fromLTRB(8, 8, 8, 0),
          child: Row(
            children: [
              Semantics(
                label: 'Quay lại',
                button: true,
                child: IconButton(
                  onPressed: widget.onBack,
                  icon: const Icon(Icons.arrow_back_rounded),
                  color: Colors.white70,
                  iconSize: 28,
                ),
              ),
              const Spacer(),
              const Text('📋 Kết quả',
                  style: TextStyle(
                      fontFamily: 'Outfit',
                      fontSize: 18,
                      fontWeight: FontWeight.w700,
                      color: Colors.white)),
              const Spacer(),
              const SizedBox(width: 48),
            ],
          ),
        ),
        Expanded(
          child: TriageResultView(
            level: level,
            selectedRegions: _selectedRegions,
            selectedSymptoms: _selectedSymptoms,
            severity: _severity,
            duration: _duration,
            adviceItems: _generateAdvice(),
            onGoHome: widget.onBack,
            onCallEmergency: () => EmergencyService().triggerEmergency(context),
          ),
        ),
      ],
    );
  }

  // ──────────────────────────────────────────────────────
  // ⌨️ TEXT MODE — Simple text input
  // ──────────────────────────────────────────────────────

  Widget _buildTextMode({Key? key}) {
    return _TextModeContent(
      key: key,
      onSubmit: (text) {
        setState(() => _isProcessing = true);
        Future.delayed(const Duration(seconds: 2), () {
          if (!mounted) return;
          setState(() {
            _severity ??= Severity.moderate;
            _duration ??= SymptomDuration.twoDays;
            _isProcessing = false;
            _showResult = true;
          });
        });
      },
    );
  }
}

/// Internal consultation mode — NOT the same as CommunicationMethod.
/// This is specific to how the consult page routes content.
enum _ConsultMode {
  tap,
  voice,
  sign,
  text,
}

extension _ConsultModeX on _ConsultMode {
  String get emoji {
    switch (this) {
      case _ConsultMode.tap:
        return '👆';
      case _ConsultMode.voice:
        return '🎤';
      case _ConsultMode.sign:
        return '🤟';
      case _ConsultMode.text:
        return '⌨️';
    }
  }

  String get label {
    switch (this) {
      case _ConsultMode.tap:
        return 'Chạm';
      case _ConsultMode.voice:
        return 'Nói';
      case _ConsultMode.sign:
        return 'Ký hiệu';
      case _ConsultMode.text:
        return 'Gõ chữ';
    }
  }

  Color get color {
    switch (this) {
      case _ConsultMode.tap:
        return const Color(0xFF14B8A6);
      case _ConsultMode.voice:
        return const Color(0xFF3B82F6);
      case _ConsultMode.sign:
        return const Color(0xFF8B5CF6);
      case _ConsultMode.text:
        return const Color(0xFFF59E0B);
    }
  }
}

/// Stateful widget for text input mode.
class _TextModeContent extends StatefulWidget {
  const _TextModeContent({super.key, required this.onSubmit});
  final ValueChanged<String> onSubmit;

  @override
  State<_TextModeContent> createState() => _TextModeContentState();
}

class _TextModeContentState extends State<_TextModeContent> {
  final _controller = TextEditingController();

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 20),
      child: Column(
        children: [
          const SizedBox(height: 16),
          // Title
          const Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Text('⌨️', style: TextStyle(fontSize: 32)),
              SizedBox(width: 10),
              Text(
                'Mô tả triệu chứng',
                style: TextStyle(
                  fontFamily: 'Outfit',
                  fontSize: 20,
                  fontWeight: FontWeight.w700,
                  color: Colors.white,
                ),
              ),
            ],
          ),
          const SizedBox(height: 6),
          const Text(
            'Gõ triệu chứng bạn đang gặp',
            style: TextStyle(
              fontFamily: 'Outfit',
              fontSize: 13,
              color: Colors.white54,
            ),
          ),
          const SizedBox(height: 20),

          // Text field
          Expanded(
            child: Container(
              decoration: BoxDecoration(
                color: Colors.white.withOpacity(0.06),
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: Colors.white.withOpacity(0.1)),
              ),
              child: TextField(
                controller: _controller,
                maxLines: null,
                expands: true,
                textAlignVertical: TextAlignVertical.top,
                style: const TextStyle(
                  fontFamily: 'Outfit',
                  fontSize: 15,
                  color: Colors.white,
                  height: 1.5,
                ),
                cursorColor: const Color(0xFF14B8A6),
                decoration: InputDecoration(
                  hintText:
                      'Ví dụ: Em bị đau đầu 2 ngày, sốt nhẹ, mệt mỏi, ho khan...',
                  hintStyle: TextStyle(
                    fontFamily: 'Outfit',
                    fontSize: 14,
                    color: Colors.white.withOpacity(0.25),
                  ),
                  border: InputBorder.none,
                  contentPadding: const EdgeInsets.all(16),
                ),
              ),
            ),
          ),
          const SizedBox(height: 12),

          // Submit button
          SizedBox(
            width: double.infinity,
            height: 52,
            child: GestureDetector(
              onTap: () {
                final text = _controller.text.trim();
                if (text.length >= 3) {
                  HapticFeedback.mediumImpact();
                  widget.onSubmit(text);
                }
              },
              child: Container(
                decoration: BoxDecoration(
                  gradient: const LinearGradient(
                    colors: [Color(0xFF0D9488), Color(0xFF14B8A6)],
                  ),
                  borderRadius: BorderRadius.circular(16),
                  boxShadow: [
                    BoxShadow(
                      color: const Color(0xFF14B8A6).withOpacity(0.3),
                      blurRadius: 12,
                      offset: const Offset(0, 4),
                    ),
                  ],
                ),
                child: const Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Text('✅', style: TextStyle(fontSize: 20)),
                    SizedBox(width: 8),
                    Text(
                      'Phân tích ngay',
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
          const SizedBox(height: 12),
        ],
      ),
    );
  }
}
