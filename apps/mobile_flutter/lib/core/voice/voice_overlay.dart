import 'package:flutter/material.dart';

import 'voice_controller.dart';

/// Overlay panel hien thi trang thai voice controller + nut bat/tat.
class VoiceOverlay extends StatelessWidget {
  const VoiceOverlay({super.key, required this.controller, required this.onClose});

  final VoiceController controller;
  final VoidCallback onClose;

  String _statusText() {
    switch (controller.mode) {
      case VoiceMode.off:
        return 'Đã tắt. Bấm "Bật nghe" để dùng wake-word "Bác sĩ ơi".';
      case VoiceMode.wake:
        return 'Đang chờ wake-word "Bác sĩ ơi"...';
      case VoiceMode.command:
        return 'Mình đang nghe. Hãy nói lệnh của bạn.';
      case VoiceMode.executing:
        return controller.lastReply.isNotEmpty
            ? controller.lastReply
            : 'Đang xử lý...';
    }
  }

  @override
  Widget build(BuildContext context) {
    return Material(
      color: Colors.transparent,
      child: SafeArea(
        child: Align(
          alignment: Alignment.bottomRight,
          child: Container(
            margin: const EdgeInsets.fromLTRB(12, 12, 12, 96),
            constraints: const BoxConstraints(maxWidth: 360),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(20),
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withValues(alpha: 0.18),
                  blurRadius: 24,
                  offset: const Offset(0, 8),
                ),
              ],
            ),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                _Header(onClose: onClose),
                Padding(
                  padding: const EdgeInsets.fromLTRB(16, 14, 16, 16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      _StatusBanner(text: _statusText()),
                      if (controller.transcript.isNotEmpty) ...[
                        const SizedBox(height: 10),
                        _Bubble(
                          label: 'Bạn vừa nói',
                          text: controller.transcript,
                          color: const Color(0xFFF1F5F9),
                          textColor: const Color(0xFF0F172A),
                        ),
                      ],
                      if (controller.lastReply.isNotEmpty) ...[
                        const SizedBox(height: 10),
                        _Bubble(
                          label: 'Trợ lý',
                          text: controller.lastReply,
                          color: const Color(0xFFECFDF5),
                          textColor: const Color(0xFF065F46),
                        ),
                      ],
                      if (controller.error != null) ...[
                        const SizedBox(height: 10),
                        _Bubble(
                          label: 'Lỗi',
                          text: controller.error!,
                          color: const Color(0xFFFEF2F2),
                          textColor: const Color(0xFF991B1B),
                        ),
                      ],
                      const SizedBox(height: 14),
                      Row(
                        children: [
                          Expanded(
                            child: _PrimaryButton(
                              label: controller.mode == VoiceMode.off
                                  ? 'Bật nghe'
                                  : 'Tắt nghe',
                              color: controller.mode == VoiceMode.off
                                  ? const Color(0xFF0284C7)
                                  : const Color(0xFFE11D48),
                              onTap: () {
                                if (controller.mode == VoiceMode.off) {
                                  controller.start();
                                } else {
                                  controller.stop();
                                }
                              },
                            ),
                          ),
                          const SizedBox(width: 8),
                          Expanded(
                            child: _SecondaryButton(
                              label: 'Nói lệnh ngay',
                              enabled: controller.mode != VoiceMode.off,
                              onTap: controller.beginCommand,
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 10),
                      const _CommandHints(),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class _Header extends StatelessWidget {
  const _Header({required this.onClose});
  final VoidCallback onClose;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.fromLTRB(16, 12, 8, 12),
      decoration: const BoxDecoration(
        gradient: LinearGradient(
          colors: [Color(0xFF0284C7), Color(0xFF0369A1)],
        ),
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      child: Row(
        children: [
          const Icon(Icons.mic_rounded, color: Colors.white, size: 18),
          const SizedBox(width: 8),
          const Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisSize: MainAxisSize.min,
              children: [
                Text('MediSign Voice',
                    style: TextStyle(
                        fontFamily: 'Outfit',
                        color: Colors.white,
                        fontWeight: FontWeight.w800,
                        fontSize: 14)),
                Text('Điều khiển bằng giọng nói',
                    style: TextStyle(
                        fontFamily: 'Outfit',
                        color: Colors.white70,
                        fontSize: 11)),
              ],
            ),
          ),
          IconButton(
            icon: const Icon(Icons.close_rounded, color: Colors.white),
            onPressed: onClose,
            tooltip: 'Đóng',
          ),
        ],
      ),
    );
  }
}

class _StatusBanner extends StatelessWidget {
  const _StatusBanner({required this.text});
  final String text;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
      decoration: BoxDecoration(
        color: const Color(0xFFEFF6FF),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Text(
        text,
        style: const TextStyle(
            fontFamily: 'Outfit', fontSize: 13, color: Color(0xFF1E3A8A)),
      ),
    );
  }
}

class _Bubble extends StatelessWidget {
  const _Bubble({
    required this.label,
    required this.text,
    required this.color,
    required this.textColor,
  });
  final String label;
  final String text;
  final Color color;
  final Color textColor;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
      decoration: BoxDecoration(
        color: color,
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisSize: MainAxisSize.min,
        children: [
          Text(
            label.toUpperCase(),
            style: TextStyle(
              fontFamily: 'Outfit',
              fontSize: 10,
              letterSpacing: 0.6,
              color: textColor.withValues(alpha: 0.7),
              fontWeight: FontWeight.w700,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            text,
            style: TextStyle(
                fontFamily: 'Outfit', fontSize: 13, color: textColor),
          ),
        ],
      ),
    );
  }
}

class _PrimaryButton extends StatelessWidget {
  const _PrimaryButton({required this.label, required this.onTap, required this.color});
  final String label;
  final VoidCallback onTap;
  final Color color;
  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(999),
      child: Container(
        height: 40,
        alignment: Alignment.center,
        decoration: BoxDecoration(
            color: color, borderRadius: BorderRadius.circular(999)),
        child: Text(
          label,
          style: const TextStyle(
              fontFamily: 'Outfit',
              color: Colors.white,
              fontWeight: FontWeight.w800,
              fontSize: 13),
        ),
      ),
    );
  }
}

class _SecondaryButton extends StatelessWidget {
  const _SecondaryButton({required this.label, required this.onTap, required this.enabled});
  final String label;
  final VoidCallback onTap;
  final bool enabled;
  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: enabled ? onTap : null,
      borderRadius: BorderRadius.circular(999),
      child: Container(
        height: 40,
        alignment: Alignment.center,
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(999),
          border: Border.all(color: const Color(0xFFE2E8F0)),
        ),
        child: Text(
          label,
          style: TextStyle(
              fontFamily: 'Outfit',
              color: enabled ? const Color(0xFF334155) : const Color(0xFFCBD5E1),
              fontWeight: FontWeight.w700,
              fontSize: 13),
        ),
      ),
    );
  }
}

class _CommandHints extends StatelessWidget {
  const _CommandHints();
  @override
  Widget build(BuildContext context) {
    const items = [
      '"Bác sĩ ơi, mở chat"',
      '"Bác sĩ ơi, mở tủ thuốc"',
      '"Bác sĩ ơi, mở hồ sơ"',
      '"Cuộn xuống" / "Quay lại"',
    ];
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
      decoration: BoxDecoration(
        color: const Color(0xFFF8FAFC),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: const Color(0xFFE2E8F0)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisSize: MainAxisSize.min,
        children: [
          const Text('Lệnh mẫu',
              style: TextStyle(
                  fontFamily: 'Outfit',
                  fontSize: 11,
                  fontWeight: FontWeight.w700,
                  color: Color(0xFF475569))),
          const SizedBox(height: 4),
          for (final s in items)
            Text(s,
                style: const TextStyle(
                    fontFamily: 'Outfit',
                    fontSize: 12,
                    color: Color(0xFF64748B))),
        ],
      ),
    );
  }
}

/// Floating Action Button toan cuc — bam de mo overlay + bat controller.
class VoiceFab extends StatelessWidget {
  const VoiceFab({super.key, required this.active, required this.onTap});
  final bool active;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: 56,
      height: 56,
      child: FloatingActionButton(
        heroTag: 'voice_fab',
        onPressed: onTap,
        backgroundColor: active ? const Color(0xFFE11D48) : const Color(0xFF0284C7),
        tooltip: 'Điều khiển bằng giọng nói',
        child: const Icon(Icons.mic_rounded, color: Colors.white),
      ),
    );
  }
}


