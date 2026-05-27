import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import '../../../core/models/consult_mode.dart';
import '../../../core/models/communication_mode.dart';
import '../../../core/network/api_contracts.dart';
import '../../../core/network/api_models.dart';
import '../../../core/voice/voice_intents.dart';
import '../../../core/voice/voice_shell_events.dart';
import '../../../core/voice/voice_shell_scope.dart';
import 'accessible_consult_page.dart';

// ── Light theme tokens (đồng bộ với dashboard_page.dart) ──
const _kBrand = Color(0xFF0284C7);
const _kBrandLight = Color(0xFF38BDF8);
const _kBrandSoft = Color(0xFFE0F2FE);
const _kBrandSofter = Color(0xFFF0F9FF);
const _kBg = Color(0xFFF8FAFC);
const _kBorder = Color(0xFFE2E8F0);
const _kBorderSoft = Color(0xFFF1F5F9);
const _kInk = Color(0xFF0F172A);
const _kInkSoft = Color(0xFF475569);
const _kInkMuted = Color(0xFF94A3B8);
const _kSuccess = Color(0xFF10B981);

class _ChatMessage {
  const _ChatMessage({
    required this.text,
    required this.isUser,
    required this.time,
    this.triageResult,
  });

  final String text;
  final bool isUser;
  final String time;
  final TriageResult? triageResult;
}

enum _ChatMode { text, voice, click, sign }

/// Chat AI page — light theme, layout đúng screenshot.
/// Giữ signature [mode] / [consultApi] để không vỡ call site cũ; nội dung
/// hiện đang dùng dữ liệu mock để demo, sẽ wire vào API sau.
class ConsultPage extends StatefulWidget {
  const ConsultPage({
    super.key,
    required this.mode,
    required this.consultApi,
  });

  final ConsultMode mode;
  final ConsultApi consultApi;

  @override
  State<ConsultPage> createState() => _ConsultPageState();
}

class _ConsultPageState extends State<ConsultPage> {
  bool _summaryOpen = true;
  _ChatMode _chatMode = _ChatMode.text;
  final _inputController = TextEditingController();
  final _scrollController = ScrollController();

  final List<_ChatMessage> _messages = [];
  bool _isTyping = false;
  TriageResult? _latestTriage;

  VoiceShellEvents? _voiceEvents;
  int _lastVoiceSeq = -1;

  @override
  void initState() {
    super.initState();
    _messages.add(
      _ChatMessage(
        text:
            'Chào bạn, tôi là MediSign AI - Trợ lý y tế AI của bạn. Hãy mô tả triệu chứng hoặc cảm giác khó chịu của bạn để tôi có thể hỗ trợ phân loại và đưa ra lời khuyên phù hợp nhé!',
        isUser: false,
        time: _formatTime(DateTime.now()),
      ),
    );
  }

  String _formatTime(DateTime dt) {
    final hour = dt.hour.toString().padLeft(2, '0');
    final minute = dt.minute.toString().padLeft(2, '0');
    return '$hour:$minute';
  }

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    final events = VoiceShellScope.maybeOf(context);
    if (events != _voiceEvents) {
      _voiceEvents?.removeListener(_onVoiceIntent);
      _voiceEvents = events;
      _voiceEvents?.addListener(_onVoiceIntent);
    }
  }

  void _onVoiceIntent() {
    final events = _voiceEvents;
    if (events == null) return;
    if (events.seq == _lastVoiceSeq) return;
    _lastVoiceSeq = events.seq;
    final intent = events.last;
    if (intent == null) return;
    switch (intent.kind) {
      case VoiceIntentKind.uiDictate:
        final t = intent.text ?? '';
        setState(() {
          _inputController.text = t;
          _inputController.selection =
              TextSelection.collapsed(offset: t.length);
        });
        break;
      case VoiceIntentKind.uiClear:
        setState(() => _inputController.clear());
        break;
      case VoiceIntentKind.uiSubmit:
        _submitMessage();
        break;
      case VoiceIntentKind.chatMode:
        if (intent.chatMode != null) {
          final newMode = switch (intent.chatMode!) {
            VoiceChatMode.text => _ChatMode.text,
            VoiceChatMode.voice => _ChatMode.voice,
            VoiceChatMode.click => _ChatMode.click,
            VoiceChatMode.sign => _ChatMode.sign,
          };
          setState(() => _chatMode = newMode);
          // If switching to voice/sign/click via voice command, open the
          // accessible page immediately so the mode is actually functional.
          if (newMode != _ChatMode.text) {
            _openAccessiblePage(newMode);
          }
        }
        break;
      case VoiceIntentKind.scroll:
        _voiceScroll(intent.scrollAction);
        break;
      default:
        break;
    }
  }

  void _submitMessage() async {
    final text = _inputController.text.trim();
    if (text.isEmpty) return;

    HapticFeedback.lightImpact();
    _inputController.clear();

    final now = DateTime.now();
    final timeStr = _formatTime(now);

    setState(() {
      _messages.add(_ChatMessage(text: text, isUser: true, time: timeStr));
      _isTyping = true;
    });

    _scrollToBottom();

    try {
      final result = await widget.consultApi.triage(
        symptomText: text,
        mode: widget.mode,
      );

      setState(() {
        _latestTriage = result;
        _isTyping = false;
        _messages.add(
          _ChatMessage(
            text: result.summary,
            isUser: false,
            time: _formatTime(DateTime.now()),
            triageResult: result,
          ),
        );
      });
    } catch (e) {
      setState(() {
        _isTyping = false;
        _messages.add(
          _ChatMessage(
            text:
                'Đã xảy ra lỗi khi kết nối với máy chủ AI. Vui lòng thử lại sau.\nChi tiết: $e',
            isUser: false,
            time: _formatTime(DateTime.now()),
          ),
        );
      });
    }

    _scrollToBottom();
  }

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  void _voiceScroll(VoiceScrollAction? a) {
    if (!_scrollController.hasClients) return;
    final pos = _scrollController.position;
    final dy = MediaQuery.of(context).size.height * 0.6;
    switch (a) {
      case VoiceScrollAction.up:
        _scrollController.animateTo(
            (pos.pixels - dy).clamp(pos.minScrollExtent, pos.maxScrollExtent),
            duration: const Duration(milliseconds: 250),
            curve: Curves.easeOut);
        break;
      case VoiceScrollAction.down:
        _scrollController.animateTo(
            (pos.pixels + dy).clamp(pos.minScrollExtent, pos.maxScrollExtent),
            duration: const Duration(milliseconds: 250),
            curve: Curves.easeOut);
        break;
      case VoiceScrollAction.top:
        _scrollController.animateTo(pos.minScrollExtent,
            duration: const Duration(milliseconds: 300), curve: Curves.easeOut);
        break;
      case VoiceScrollAction.bottom:
        _scrollController.animateTo(pos.maxScrollExtent,
            duration: const Duration(milliseconds: 300), curve: Curves.easeOut);
        break;
      case null:
        break;
    }
  }

  @override
  void dispose() {
    _voiceEvents?.removeListener(_onVoiceIntent);
    _inputController.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  /// Open [AccessibleConsultPage] as a full-screen route.
  /// Used when the user taps Voice / Click / Sign mode tabs, or switches via
  /// voice command — those modes have real implementations there.
  void _openAccessiblePage([_ChatMode? targetMode]) {
    final method = switch (targetMode ?? _ChatMode.click) {
      _ChatMode.text => CommunicationMethod.text,
      _ChatMode.voice => CommunicationMethod.voice,
      _ChatMode.click => CommunicationMethod.tap,
      _ChatMode.sign => CommunicationMethod.sign,
    };
    Navigator.of(context).push(
      MaterialPageRoute(
        builder: (_) => AccessibleConsultPage(
          initialMethod: method,
          onBack: () => Navigator.of(context).pop(),
        ),
      ),
    );
  }

  /// Called by the mic button in the input bar — opens the voice mode of
  /// [AccessibleConsultPage] directly.
  void _openVoiceMode() => _openAccessiblePage(_ChatMode.voice);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: _kBg,
      body: SafeArea(
        bottom: false,
        child: Column(
          children: [
            const _ChatHeader(),
            _SummaryCard(
              open: _summaryOpen,
              onToggle: () => setState(() => _summaryOpen = !_summaryOpen),
              latestTriage: _latestTriage,
            ),
            Expanded(
              child: ListView.builder(
                controller: _scrollController,
                padding: const EdgeInsets.fromLTRB(12, 8, 12, 4),
                physics: const BouncingScrollPhysics(),
                itemCount: _messages.length + (_isTyping ? 1 : 0),
                itemBuilder: (context, index) {
                  if (index == _messages.length) {
                    return const _TypingBubble();
                  }
                  final msg = _messages[index];
                  if (msg.isUser) {
                    return Column(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        if (index == 0) ...[
                          const _DateChip('Hôm nay'),
                          const SizedBox(height: 10),
                        ],
                        _UserBubble(text: msg.text, time: msg.time),
                        const SizedBox(height: 12),
                      ],
                    );
                  } else {
                    return Column(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        if (index == 0) ...[
                          const _DateChip('Hôm nay'),
                          const SizedBox(height: 10),
                        ],
                        _AiBubble(
                          child: _AiResponseContent(message: msg),
                        ),
                        const SizedBox(height: 12),
                      ],
                    );
                  }
                },
              ),
            ),
            _SuggestionChipsRow(
              onSelect: (val) {
                _inputController.text = val;
                _submitMessage();
              },
            ),
            _ModeTabs(
              selected: _chatMode,
              onChanged: (m) {
                setState(() => _chatMode = m);
                // Voice / Click / Sign modes are fully implemented in
                // AccessibleConsultPage — open it immediately.
                if (m != _ChatMode.text) {
                  _openAccessiblePage(m);
                }
              },
            ),
            _InputBar(
              controller: _inputController,
              onAttach: () {},
              onMic: _openVoiceMode,
              onSend: _submitMessage,
            ),
          ],
        ),
      ),
    );
  }
}

// ───────────────────────── HEADER ─────────────────────────

class _ChatHeader extends StatelessWidget {
  const _ChatHeader();

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(8, 4, 8, 8),
      child: Row(
        children: [
          _SquareIconBtn(icon: Icons.menu_rounded, onTap: () {}),
          const SizedBox(width: 6),
          _ShieldLogo(),
          const SizedBox(width: 8),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'MediSign AI',
                  style: TextStyle(
                    fontFamily: 'Outfit',
                    fontSize: 18,
                    fontWeight: FontWeight.w800,
                    color: _kInk,
                    height: 1.1,
                  ),
                ),
                const SizedBox(height: 2),
                Row(
                  children: const [
                    _Dot(color: _kSuccess),
                    SizedBox(width: 6),
                    Text(
                      'Trợ lý y tế AI của bạn',
                      style: TextStyle(
                        fontFamily: 'Outfit',
                        fontSize: 11,
                        color: _kInkSoft,
                        height: 1.1,
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
          _SquareIconBtn(icon: Icons.history_rounded, onTap: () {}),
          const SizedBox(width: 6),
          _SquareIconBtn(icon: Icons.more_vert_rounded, onTap: () {}),
        ],
      ),
    );
  }
}

class _ShieldLogo extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Container(
      width: 32,
      height: 32,
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [_kBrand, _kBrandLight],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(8),
        boxShadow: [
          BoxShadow(
            color: _kBrand.withOpacity(0.25),
            blurRadius: 6,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: const Icon(Icons.medical_services_rounded,
          color: Colors.white, size: 18),
    );
  }
}

class _SquareIconBtn extends StatelessWidget {
  const _SquareIconBtn({required this.icon, required this.onTap});
  final IconData icon;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return InkResponse(
      onTap: () {
        HapticFeedback.selectionClick();
        onTap();
      },
      radius: 24,
      child: SizedBox(
        width: 40,
        height: 40,
        child: Icon(icon, size: 20, color: _kInkSoft),
      ),
    );
  }
}

class _Dot extends StatelessWidget {
  const _Dot({required this.color});
  final Color color;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 6,
      height: 6,
      decoration: BoxDecoration(color: color, shape: BoxShape.circle),
    );
  }
}

// ───────────────────────── SUMMARY CARD (collapsible) ─────────────────────────

class _SummaryCard extends StatelessWidget {
  const _SummaryCard({
    required this.open,
    required this.onToggle,
    required this.latestTriage,
  });

  final bool open;
  final VoidCallback onToggle;
  final TriageResult? latestTriage;

  @override
  Widget build(BuildContext context) {
    final String symptomsText =
        latestTriage != null ? 'Đã phân tích' : 'Chưa cập nhật';
    final String assessmentText = latestTriage != null
        ? _mapUrgencyTitle(latestTriage!.urgencyLevel)
        : 'Chưa đánh giá';
    final String recommendationText =
        latestTriage != null && latestTriage!.recommendations.isNotEmpty
            ? latestTriage!.recommendations.first
            : 'Chờ phân loại...';

    return Padding(
      padding: const EdgeInsets.fromLTRB(12, 0, 12, 8),
      child: Container(
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: _kBorder),
        ),
        padding: const EdgeInsets.fromLTRB(12, 10, 12, 12),
        child: Column(
          children: [
            // Header
            InkWell(
              onTap: onToggle,
              borderRadius: BorderRadius.circular(8),
              child: Padding(
                padding: const EdgeInsets.symmetric(vertical: 2),
                child: Row(
                  children: [
                    Container(
                      width: 26,
                      height: 26,
                      decoration: BoxDecoration(
                        color: _kBrandSofter,
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: const Icon(Icons.assignment_outlined,
                          size: 15, color: _kBrand),
                    ),
                    const SizedBox(width: 8),
                    const Text(
                      'Tóm tắt nhanh',
                      style: TextStyle(
                        fontFamily: 'Outfit',
                        fontSize: 13.5,
                        fontWeight: FontWeight.w700,
                        color: _kInk,
                      ),
                    ),
                    const Spacer(),
                    AnimatedRotation(
                      turns: open ? 0 : 0.5,
                      duration: const Duration(milliseconds: 200),
                      child: const Icon(Icons.keyboard_arrow_up_rounded,
                          size: 22, color: _kInkSoft),
                    ),
                  ],
                ),
              ),
            ),
            AnimatedCrossFade(
              firstChild: Padding(
                padding: const EdgeInsets.only(top: 10),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Expanded(
                      child: _SummaryItem(
                        icon: Icons.assignment_outlined,
                        title: 'Triệu chứng',
                        body: symptomsText,
                      ),
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: _SummaryItem(
                        icon: Icons.psychology_outlined,
                        title: 'Đánh giá sơ bộ',
                        body: assessmentText,
                      ),
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: _SummaryItem(
                        icon: Icons.local_hospital_outlined,
                        title: 'Khuyến nghị',
                        body: recommendationText,
                      ),
                    ),
                  ],
                ),
              ),
              secondChild: const SizedBox.shrink(),
              crossFadeState:
                  open ? CrossFadeState.showFirst : CrossFadeState.showSecond,
              duration: const Duration(milliseconds: 200),
            ),
          ],
        ),
      ),
    );
  }

  String _mapUrgencyTitle(String level) {
    switch (level.toLowerCase()) {
      case 'emergency':
        return 'Cấp cứu 🚨';
      case 'urgent':
        return 'Khẩn cấp ⚠️';
      case 'non_emergency':
      default:
        return 'Tại nhà ✅';
    }
  }
}

class _SummaryItem extends StatelessWidget {
  const _SummaryItem({
    required this.icon,
    required this.title,
    required this.body,
  });
  final IconData icon;
  final String title;
  final String body;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Icon(icon, size: 13, color: _kBrand),
            const SizedBox(width: 4),
            Flexible(
              child: Text(
                title,
                overflow: TextOverflow.ellipsis,
                style: const TextStyle(
                  fontFamily: 'Outfit',
                  fontSize: 11.5,
                  fontWeight: FontWeight.w700,
                  color: _kInk,
                ),
              ),
            ),
          ],
        ),
        const SizedBox(height: 4),
        Text(
          body,
          style: const TextStyle(
            fontFamily: 'Outfit',
            fontSize: 10.5,
            color: _kInkSoft,
            height: 1.3,
          ),
        ),
      ],
    );
  }
}

// ───────────────────────── DATE CHIP ─────────────────────────

class _DateChip extends StatelessWidget {
  const _DateChip(this.text);
  final String text;

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
        decoration: BoxDecoration(
          color: _kBorderSoft,
          borderRadius: BorderRadius.circular(999),
        ),
        child: Text(
          text,
          style: const TextStyle(
            fontFamily: 'Outfit',
            fontSize: 11,
            fontWeight: FontWeight.w600,
            color: _kInkSoft,
          ),
        ),
      ),
    );
  }
}

// ───────────────────────── USER BUBBLE ─────────────────────────

class _UserBubble extends StatelessWidget {
  const _UserBubble({
    required this.text,
    required this.time,
    this.attachment,
  });

  final String text;
  final String time;
  final Widget? attachment;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(left: 56),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.end,
        children: [
          Container(
            decoration: BoxDecoration(
              color: _kBrandSoft,
              borderRadius: const BorderRadius.only(
                topLeft: Radius.circular(18),
                topRight: Radius.circular(18),
                bottomLeft: Radius.circular(18),
                bottomRight: Radius.circular(4),
              ),
            ),
            padding: const EdgeInsets.fromLTRB(14, 10, 14, 10),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  text,
                  style: const TextStyle(
                    fontFamily: 'Outfit',
                    fontSize: 13.5,
                    color: _kInk,
                    height: 1.45,
                  ),
                ),
                if (attachment != null) ...[
                  const SizedBox(height: 8),
                  attachment!,
                ],
              ],
            ),
          ),
          const SizedBox(height: 4),
          Padding(
            padding: const EdgeInsets.only(right: 4),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                Text(
                  time,
                  style: const TextStyle(
                    fontFamily: 'Outfit',
                    fontSize: 10.5,
                    color: _kInkMuted,
                  ),
                ),
                const SizedBox(width: 4),
                const Icon(Icons.done_all_rounded, size: 13, color: _kBrand),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _AttachmentPreview extends StatelessWidget {
  const _AttachmentPreview({
    required this.filename,
    required this.size,
    required this.ext,
  });

  final String filename;
  final String size;
  final String ext;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(8),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: _kBorder),
      ),
      child: Row(
        children: [
          Container(
            width: 44,
            height: 44,
            decoration: BoxDecoration(
              color: _kInk,
              borderRadius: BorderRadius.circular(8),
            ),
            child:
                const Icon(Icons.image_outlined, size: 22, color: _kBrandLight),
          ),
          const SizedBox(width: 10),
          Expanded(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  filename,
                  overflow: TextOverflow.ellipsis,
                  style: const TextStyle(
                    fontFamily: 'Outfit',
                    fontSize: 12,
                    fontWeight: FontWeight.w700,
                    color: _kInk,
                    height: 1.2,
                  ),
                ),
                const SizedBox(height: 2),
                Text(
                  '$size · $ext',
                  style: const TextStyle(
                    fontFamily: 'Outfit',
                    fontSize: 10.5,
                    color: _kInkSoft,
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(width: 8),
          Container(
            width: 22,
            height: 22,
            decoration: const BoxDecoration(
              color: _kSuccess,
              shape: BoxShape.circle,
            ),
            child:
                const Icon(Icons.check_rounded, size: 14, color: Colors.white),
          ),
        ],
      ),
    );
  }
}

// ───────────────────────── AI BUBBLE ─────────────────────────

class _AiBubble extends StatelessWidget {
  const _AiBubble({required this.child});
  final Widget child;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(right: 36),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const _AiAvatar(),
          const SizedBox(width: 8),
          Flexible(
            child: Container(
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: const BorderRadius.only(
                  topLeft: Radius.circular(4),
                  topRight: Radius.circular(18),
                  bottomLeft: Radius.circular(18),
                  bottomRight: Radius.circular(18),
                ),
                border: Border.all(color: _kBorder),
              ),
              padding: const EdgeInsets.fromLTRB(14, 12, 14, 12),
              child: child,
            ),
          ),
        ],
      ),
    );
  }
}

class _AiAvatar extends StatelessWidget {
  const _AiAvatar();

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 32,
      height: 32,
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [_kBrand, _kBrandLight],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(10),
      ),
      child: const Icon(Icons.medical_services_rounded,
          size: 16, color: Colors.white),
    );
  }
}

class _FirstAiResponse extends StatelessWidget {
  const _FirstAiResponse();

  @override
  Widget build(BuildContext context) {
    const items = [
      'Nhiệt độ cơ thể hiện tại là bao nhiêu (°C)?',
      'Có đau đầu, mệt mỏi hoặc sổ mũi, ho có đờm không?',
      'Đã sử dụng thuốc hoặc biện pháp nào chưa?',
      'Tiền sử dị ứng hoặc bệnh lý nền (nếu có)?',
    ];
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Chào bạn Minh An, cảm ơn bạn đã chia sẻ triệu chứng.',
          style: TextStyle(
            fontFamily: 'Outfit',
            fontSize: 13.5,
            color: _kInk,
            height: 1.45,
          ),
        ),
        const SizedBox(height: 6),
        const Text(
          'Dựa trên mô tả ban đầu, đây có thể là viêm họng do virus.\n'
          'Để đánh giá chính xác hơn, bạn có thể cung cấp thêm\n'
          'thông tin:',
          style: TextStyle(
            fontFamily: 'Outfit',
            fontSize: 13.5,
            color: _kInk,
            height: 1.45,
          ),
        ),
        const SizedBox(height: 8),
        ...items.map((t) => Padding(
              padding: const EdgeInsets.only(bottom: 4, left: 4),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Padding(
                    padding: EdgeInsets.only(top: 7),
                    child: _BulletDot(),
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      t,
                      style: const TextStyle(
                        fontFamily: 'Outfit',
                        fontSize: 13,
                        color: _kInk,
                        height: 1.5,
                      ),
                    ),
                  ),
                ],
              ),
            )),
        const SizedBox(height: 4),
        Align(
          alignment: Alignment.centerRight,
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: const [
              Text(
                '10:24',
                style: TextStyle(
                  fontFamily: 'Outfit',
                  fontSize: 10.5,
                  color: _kInkMuted,
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }
}

class _BulletDot extends StatelessWidget {
  const _BulletDot();
  @override
  Widget build(BuildContext context) {
    return Container(
      width: 4,
      height: 4,
      decoration: const BoxDecoration(
        color: _kInk,
        shape: BoxShape.circle,
      ),
    );
  }
}

class _AssessmentCard extends StatelessWidget {
  const _AssessmentCard();

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Đánh giá & gợi ý',
          style: TextStyle(
            fontFamily: 'Outfit',
            fontSize: 14,
            fontWeight: FontWeight.w800,
            color: _kInk,
          ),
        ),
        const SizedBox(height: 10),
        const _CheckRow(
          label: 'Nhiệt độ',
          value: '37.8°C (sốt nhẹ)',
        ),
        const _CheckRow(
          label: 'Triệu chứng',
          value: 'Đau họng, ho khan, mệt nhẹ',
        ),
        const _CheckRow(
          label: 'X-quang phổi',
          value: 'Không thấy tổn thương rõ rệt',
        ),
        const SizedBox(height: 10),
        Container(
          padding: const EdgeInsets.all(10),
          decoration: BoxDecoration(
            color: _kBrandSofter,
            borderRadius: BorderRadius.circular(10),
            border: Border.all(color: _kBrandSoft),
          ),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: const [
              Icon(Icons.info_outline_rounded, size: 14, color: _kBrand),
              SizedBox(width: 6),
              Expanded(
                child: Text(
                  'Dựa trên thông tin hiện tại, bạn có thể bị viêm họng do virus. '
                  'Hãy nghỉ ngơi và theo dõi thêm trong 1–2 ngày.',
                  style: TextStyle(
                    fontFamily: 'Outfit',
                    fontSize: 11.5,
                    color: _kInkSoft,
                    height: 1.4,
                  ),
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }
}

class _CheckRow extends StatelessWidget {
  const _CheckRow({required this.label, required this.value});
  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 4),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            width: 16,
            height: 16,
            margin: const EdgeInsets.only(top: 2),
            decoration: const BoxDecoration(
              color: _kSuccess,
              shape: BoxShape.circle,
            ),
            child:
                const Icon(Icons.check_rounded, size: 11, color: Colors.white),
          ),
          const SizedBox(width: 8),
          Expanded(
            child: RichText(
              text: TextSpan(
                style: const TextStyle(
                  fontFamily: 'Outfit',
                  fontSize: 12.5,
                  color: _kInk,
                  height: 1.45,
                ),
                children: [
                  TextSpan(
                    text: '$label: ',
                    style: const TextStyle(fontWeight: FontWeight.w700),
                  ),
                  TextSpan(text: value),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}

// ───────────────────────── SUGGESTION CHIPS ─────────────────────────

class _SuggestionChipsRow extends StatelessWidget {
  const _SuggestionChipsRow({required this.onSelect});
  final ValueChanged<String> onSelect;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(12, 8, 12, 4),
      child: Row(
        children: [
          Expanded(
            child: _SuggestionChip(
              icon: Icons.water_drop_outlined,
              label: 'Đau ngực dữ dội khó thở',
              onTap: () =>
                  onSelect('Tôi bị đau ngực dữ dội và khó thở, ngực đè nặng'),
            ),
          ),
          const SizedBox(width: 8),
          Expanded(
            child: _SuggestionChip(
              icon: Icons.healing_outlined,
              label: 'Bị sốt nhẹ ho khan',
              onTap: () =>
                  onSelect('Tôi bị sốt nhẹ, đau họng và ho khan 2 ngày nay'),
            ),
          ),
        ],
      ),
    );
  }
}

class _SuggestionChip extends StatelessWidget {
  const _SuggestionChip({
    required this.icon,
    required this.label,
    required this.onTap,
  });

  final IconData icon;
  final String label;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Material(
      color: Colors.white,
      borderRadius: BorderRadius.circular(999),
      child: InkWell(
        onTap: () {
          HapticFeedback.selectionClick();
          onTap();
        },
        borderRadius: BorderRadius.circular(999),
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
          decoration: BoxDecoration(
            border: Border.all(color: _kBorder),
            borderRadius: BorderRadius.circular(999),
          ),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(icon, size: 14, color: _kBrand),
              const SizedBox(width: 6),
              Flexible(
                child: Text(
                  label,
                  overflow: TextOverflow.ellipsis,
                  textAlign: TextAlign.center,
                  style: const TextStyle(
                    fontFamily: 'Outfit',
                    fontSize: 12,
                    fontWeight: FontWeight.w600,
                    color: _kInk,
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

// ───────────────────────── MODE TABS ─────────────────────────

class _ModeTabs extends StatelessWidget {
  const _ModeTabs({required this.selected, required this.onChanged});
  final _ChatMode selected;
  final ValueChanged<_ChatMode> onChanged;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(12, 6, 12, 4),
      child: Row(
        children: [
          Expanded(
            child: _ModeBtn(
              icon: Icons.chat_bubble_outline_rounded,
              label: 'Text',
              active: selected == _ChatMode.text,
              onTap: () => onChanged(_ChatMode.text),
            ),
          ),
          const SizedBox(width: 6),
          Expanded(
            child: _ModeBtn(
              icon: Icons.graphic_eq_rounded,
              label: 'Voice',
              active: selected == _ChatMode.voice,
              onTap: () => onChanged(_ChatMode.voice),
            ),
          ),
          const SizedBox(width: 6),
          Expanded(
            child: _ModeBtn(
              icon: Icons.touch_app_outlined,
              label: 'Click',
              active: selected == _ChatMode.click,
              onTap: () => onChanged(_ChatMode.click),
            ),
          ),
          const SizedBox(width: 6),
          Expanded(
            child: _ModeBtn(
              icon: Icons.sign_language_outlined,
              label: 'Ký hiệu',
              active: selected == _ChatMode.sign,
              onTap: () => onChanged(_ChatMode.sign),
            ),
          ),
        ],
      ),
    );
  }
}

class _ModeBtn extends StatelessWidget {
  const _ModeBtn({
    required this.icon,
    required this.label,
    required this.active,
    required this.onTap,
  });

  final IconData icon;
  final String label;
  final bool active;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Material(
      color: active ? _kBrand : Colors.white,
      borderRadius: BorderRadius.circular(999),
      child: InkWell(
        onTap: () {
          HapticFeedback.selectionClick();
          onTap();
        },
        borderRadius: BorderRadius.circular(999),
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 8),
          decoration: BoxDecoration(
            border: Border.all(
              color: active ? _kBrand : _kBorder,
            ),
            borderRadius: BorderRadius.circular(999),
          ),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(
                icon,
                size: 14,
                color: active ? Colors.white : _kInkSoft,
              ),
              const SizedBox(width: 5),
              Flexible(
                child: Text(
                  label,
                  overflow: TextOverflow.ellipsis,
                  style: TextStyle(
                    fontFamily: 'Outfit',
                    fontSize: 12,
                    fontWeight: FontWeight.w700,
                    color: active ? Colors.white : _kInkSoft,
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

// ───────────────────────── INPUT BAR ─────────────────────────

class _InputBar extends StatelessWidget {
  const _InputBar({
    required this.controller,
    required this.onAttach,
    required this.onMic,
    required this.onSend,
  });

  final TextEditingController controller;
  final VoidCallback onAttach;
  final VoidCallback onMic;
  final VoidCallback onSend;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(12, 4, 12, 8),
      child: Container(
        padding: const EdgeInsets.fromLTRB(8, 6, 6, 6),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(999),
          border: Border.all(color: _kBorder),
        ),
        child: Row(
          children: [
            InkResponse(
              onTap: onAttach,
              radius: 22,
              child: const SizedBox(
                width: 36,
                height: 36,
                child:
                    Icon(Icons.attach_file_rounded, size: 18, color: _kInkSoft),
              ),
            ),
            Expanded(
              child: TextField(
                controller: controller,
                style: const TextStyle(
                  fontFamily: 'Outfit',
                  fontSize: 13.5,
                  color: _kInk,
                ),
                decoration: const InputDecoration(
                  hintText: 'Hỏi triệu chứng, gửi kết quả xét nghiệm...',
                  hintStyle: TextStyle(
                    fontFamily: 'Outfit',
                    fontSize: 13.5,
                    color: _kInkMuted,
                  ),
                  isDense: true,
                  border: InputBorder.none,
                ),
              ),
            ),
            InkResponse(
              onTap: onMic,
              radius: 22,
              child: const SizedBox(
                width: 36,
                height: 36,
                child: Icon(Icons.mic_none_rounded, size: 18, color: _kInkSoft),
              ),
            ),
            const SizedBox(width: 4),
            Material(
              color: _kBrand,
              shape: const CircleBorder(),
              child: InkWell(
                onTap: () {
                  HapticFeedback.lightImpact();
                  onSend();
                },
                customBorder: const CircleBorder(),
                child: const SizedBox(
                  width: 36,
                  height: 36,
                  child:
                      Icon(Icons.send_rounded, size: 16, color: Colors.white),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _AiResponseContent extends StatelessWidget {
  const _AiResponseContent({required this.message});
  final _ChatMessage message;

  @override
  Widget build(BuildContext context) {
    final result = message.triageResult;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          message.text,
          style: const TextStyle(
            fontFamily: 'Outfit',
            fontSize: 13.5,
            color: _kInk,
            height: 1.45,
          ),
        ),
        if (result != null) ...[
          const SizedBox(height: 12),
          _DynamicAssessmentCard(result: result),
        ],
        const SizedBox(height: 4),
        Align(
          alignment: Alignment.centerRight,
          child: Text(
            message.time,
            style: const TextStyle(
              fontFamily: 'Outfit',
              fontSize: 10.5,
              color: _kInkMuted,
            ),
          ),
        ),
      ],
    );
  }
}

class _DynamicAssessmentCard extends StatelessWidget {
  const _DynamicAssessmentCard({required this.result});
  final TriageResult result;

  @override
  Widget build(BuildContext context) {
    final isEmergency = result.urgencyLevel.toLowerCase() == 'emergency';
    final isUrgent = result.urgencyLevel.toLowerCase() == 'urgent';

    final Color statusColor = isEmergency
        ? const Color(0xFFEF4444) // Red
        : isUrgent
            ? const Color(0xFFF59E0B) // Yellow/Orange
            : const Color(0xFF10B981); // Green

    final Color bgColor = isEmergency
        ? const Color(0xFFFEF2F2)
        : isUrgent
            ? const Color(0xFFFFFBEB)
            : const Color(0xFFECFDF5);

    final Color borderColor = isEmergency
        ? const Color(0xFFFEE2E2)
        : isUrgent
            ? const Color(0xFFFEF3C7)
            : const Color(0xFFD1FAE5);

    final String urgencyLabel = isEmergency
        ? '🚨 Cấp cứu y tế'
        : isUrgent
            ? '⚠️ Khẩn cấp / Cần đi khám'
            : '✅ Theo dõi tại nhà';

    return Container(
      decoration: BoxDecoration(
        color: bgColor,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: borderColor, width: 1.5),
      ),
      padding: const EdgeInsets.all(12),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding:
                    const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                decoration: BoxDecoration(
                  color: statusColor,
                  borderRadius: BorderRadius.circular(20),
                ),
                child: Text(
                  urgencyLabel,
                  style: const TextStyle(
                    fontFamily: 'Outfit',
                    fontSize: 12,
                    fontWeight: FontWeight.w800,
                    color: Colors.white,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 10),
          const Text(
            'Khuyến nghị y tế từ trợ lý AI:',
            style: TextStyle(
              fontFamily: 'Outfit',
              fontSize: 12.5,
              fontWeight: FontWeight.w700,
              color: _kInk,
            ),
          ),
          const SizedBox(height: 6),
          ...result.recommendations.map((rec) => Padding(
                padding: const EdgeInsets.only(bottom: 6),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Container(
                      margin: const EdgeInsets.only(top: 6),
                      width: 5,
                      height: 5,
                      decoration: BoxDecoration(
                        color: statusColor,
                        shape: BoxShape.circle,
                      ),
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        rec,
                        style: const TextStyle(
                          fontFamily: 'Outfit',
                          fontSize: 12,
                          color: _kInkSoft,
                          height: 1.4,
                        ),
                      ),
                    ),
                  ],
                ),
              )),
        ],
      ),
    );
  }
}

class _TypingBubble extends StatefulWidget {
  const _TypingBubble();

  @override
  State<_TypingBubble> createState() => _TypingBubbleState();
}

class _TypingBubbleState extends State<_TypingBubble>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1000),
    )..repeat();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(right: 36, bottom: 12),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const _AiAvatar(),
          const SizedBox(width: 8),
          Container(
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: const BorderRadius.only(
                topLeft: Radius.circular(4),
                topRight: Radius.circular(18),
                bottomLeft: Radius.circular(18),
                bottomRight: Radius.circular(18),
              ),
              border: Border.all(color: _kBorder),
            ),
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: List.generate(3, (i) {
                return AnimatedBuilder(
                  animation: _controller,
                  builder: (context, child) {
                    final delay = i * 0.2;
                    double value = _controller.value - delay;
                    if (value < 0) value += 1.0;
                    value = (value * 2).clamp(0.0, 1.0);
                    if (value > 0.5) value = 1.0 - value;
                    value *= 2.0;

                    return Container(
                      margin: const EdgeInsets.symmetric(horizontal: 2),
                      width: 6,
                      height: 6,
                      decoration: BoxDecoration(
                        color: _kBrand.withOpacity(0.3 + (value * 0.7)),
                        shape: BoxShape.circle,
                      ),
                    );
                  },
                );
              }),
            ),
          ),
        ],
      ),
    );
  }
}
