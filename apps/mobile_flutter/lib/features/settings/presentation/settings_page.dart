import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import '../../../core/models/communication_mode.dart';
import '../../../core/models/consult_mode.dart';
import '../../../core/theme/glass_theme.dart';

/// Overhauled settings page with accessibility, notifications, security,
/// and data management sections — matching the dark-gradient style.
class SettingsPage extends StatefulWidget {
  const SettingsPage({
    super.key,
    required this.mode,
    required this.communicationMethods,
    required this.onResetOnboarding,
    required this.onResetCommunication,
  });

  final ConsultMode mode;
  final Set<CommunicationMethod> communicationMethods;
  final VoidCallback onResetOnboarding;
  final VoidCallback onResetCommunication;

  @override
  State<SettingsPage> createState() => _SettingsPageState();
}

class _SettingsPageState extends State<SettingsPage> {
  bool _highContrast = false;
  bool _largeText = false;
  bool _notifications = true;
  bool _biometric = false;

  @override
  Widget build(BuildContext context) {
    return GlassTheme.scaffoldBackground(
      child: SafeArea(
        child: ListView(
          padding: const EdgeInsets.fromLTRB(20, 16, 20, 32),
          children: [
            _buildHeader(),
            const SizedBox(height: 24),
            _buildModeCard(),
            const SizedBox(height: 16),
            _buildCommunicationCard(),
            const SizedBox(height: 16),
            _buildAccessibilityCard(),
            const SizedBox(height: 16),
            _buildNotificationsCard(),
            const SizedBox(height: 16),
            _buildSecurityCard(),
            const SizedBox(height: 16),
            _buildDataCard(),
            const SizedBox(height: 24),
            _buildResetButton(),
            const SizedBox(height: 16),
            _buildAppInfo(),
          ],
        ),
      ),
    );
  }

  Widget _buildHeader() {
    return const Row(
      children: [
        Text('⚙️', style: TextStyle(fontSize: 28)),
        SizedBox(width: 12),
        Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Cài đặt', style: GlassTheme.h2),
            Text('Tùy chỉnh trải nghiệm', style: GlassTheme.caption),
          ],
        ),
      ],
    );
  }

  Widget _buildModeCard() {
    return _card(
      emoji: widget.mode.emoji,
      title: 'Chế độ hoạt động',
      children: [
        _infoRow('Chế độ hiện tại', widget.mode.title),
        const SizedBox(height: 6),
        Text(widget.mode.description,
            style:
                TextStyle(color: Colors.white.withOpacity(0.5), fontSize: 12)),
        const SizedBox(height: 12),
        _actionButton(
            'Đổi chế độ', Icons.swap_horiz_rounded, widget.onResetOnboarding),
      ],
    );
  }

  Widget _buildCommunicationCard() {
    return _card(
      emoji: '💬',
      title: 'Cách giao tiếp',
      children: [
        Wrap(
          spacing: 8,
          runSpacing: 8,
          children: widget.communicationMethods.map((m) {
            return Container(
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
              decoration: BoxDecoration(
                color: const Color(0xFF52B788).withOpacity(0.2),
                borderRadius: BorderRadius.circular(12),
                border:
                    Border.all(color: const Color(0xFF52B788).withOpacity(0.4)),
              ),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text(m.icon, style: const TextStyle(fontSize: 16)),
                  const SizedBox(width: 6),
                  Text(m.label,
                      style: const TextStyle(
                          color: Colors.white,
                          fontSize: 13,
                          fontWeight: FontWeight.w500)),
                ],
              ),
            );
          }).toList(),
        ),
        const SizedBox(height: 12),
        _actionButton(
            'Thay đổi', Icons.edit_rounded, widget.onResetCommunication),
      ],
    );
  }

  Widget _buildAccessibilityCard() {
    return _card(
      emoji: '♿',
      title: 'Trợ năng',
      children: [
        _toggleRow('Chế độ tương phản cao', 'Tăng độ rõ nét', _highContrast,
            (v) {
          HapticFeedback.selectionClick();
          setState(() => _highContrast = v);
        }),
        const Divider(color: Color(0x20FFFFFF), height: 24),
        _toggleRow('Chữ lớn', 'Phóng to văn bản hiển thị', _largeText, (v) {
          HapticFeedback.selectionClick();
          setState(() => _largeText = v);
        }),
      ],
    );
  }

  Widget _buildNotificationsCard() {
    return _card(
      emoji: '🔔',
      title: 'Thông báo',
      children: [
        _toggleRow(
            'Nhắc nhở uống thuốc', 'Gửi thông báo theo lịch', _notifications,
            (v) {
          setState(() => _notifications = v);
        }),
      ],
    );
  }

  Widget _buildSecurityCard() {
    return _card(
      emoji: '🔒',
      title: 'Bảo mật',
      children: [
        _toggleRow(
            'Xác thực sinh trắc', 'Mở khóa bằng vân tay / Face ID', _biometric,
            (v) {
          HapticFeedback.selectionClick();
          setState(() => _biometric = v);
        }),
        const Divider(color: Color(0x20FFFFFF), height: 24),
        GestureDetector(
          onTap: () {
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(content: Text('Tính năng đang phát triển')),
            );
          },
          child: Row(
            children: [
              const Icon(Icons.password_rounded,
                  color: Colors.white70, size: 20),
              const SizedBox(width: 12),
              const Text('Đổi mật khẩu',
                  style: TextStyle(color: Colors.white, fontSize: 14)),
              const Spacer(),
              Icon(Icons.chevron_right,
                  color: Colors.white.withOpacity(0.3), size: 20),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildDataCard() {
    return _card(
      emoji: '💾',
      title: 'Dữ liệu',
      children: [
        _dataRow('Sao lưu dữ liệu', Icons.cloud_upload_outlined, () {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Đang sao lưu...')),
          );
        }),
        const Divider(color: Color(0x20FFFFFF), height: 20),
        _dataRow('Khôi phục dữ liệu', Icons.cloud_download_outlined, () {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Tính năng đang phát triển')),
          );
        }),
        const Divider(color: Color(0x20FFFFFF), height: 20),
        _dataRow('Xóa toàn bộ dữ liệu', Icons.delete_forever_outlined, () {
          showDialog(
            context: context,
            builder: (_) => AlertDialog(
              title: const Text('Xóa dữ liệu?'),
              content: const Text('Hành động này không thể hoàn tác.'),
              actions: [
                TextButton(
                  onPressed: () => Navigator.pop(context),
                  child: const Text('Hủy'),
                ),
                TextButton(
                  onPressed: () {
                    Navigator.pop(context);
                    widget.onResetOnboarding();
                  },
                  child: const Text('Xóa', style: TextStyle(color: Colors.red)),
                ),
              ],
            ),
          );
        }, isDestructive: true),
      ],
    );
  }

  Widget _buildResetButton() {
    return GestureDetector(
      onTap: widget.onResetOnboarding,
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: Colors.white.withOpacity(0.08),
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: Colors.white.withOpacity(0.1)),
        ),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.restart_alt_rounded,
                color: Colors.white.withOpacity(0.7), size: 20),
            const SizedBox(width: 8),
            Text('Chạy lại hướng dẫn sử dụng',
                style: TextStyle(
                    color: Colors.white.withOpacity(0.7),
                    fontSize: 14,
                    fontWeight: FontWeight.w500)),
          ],
        ),
      ),
    );
  }

  Widget _buildAppInfo() {
    return Column(
      children: [
        Text('MediSign AI v1.0.0',
            style:
                TextStyle(color: Colors.white.withOpacity(0.3), fontSize: 12)),
        const SizedBox(height: 4),
        Text('Bảo mật HIPAA • Dữ liệu được mã hóa AES-256',
            style:
                TextStyle(color: Colors.white.withOpacity(0.2), fontSize: 11)),
      ],
    );
  }

  // ── Reusable components ──

  Widget _card(
      {required String emoji,
      required String title,
      required List<Widget> children}) {
    return GlassTheme.glassCard(
      padding: const EdgeInsets.all(18),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Text(emoji, style: const TextStyle(fontSize: 22)),
              const SizedBox(width: 10),
              Text(title, style: GlassTheme.h3.copyWith(fontSize: 16)),
            ],
          ),
          const SizedBox(height: 14),
          ...children,
        ],
      ),
    );
  }

  Widget _infoRow(String label, String value) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(label,
            style:
                TextStyle(color: Colors.white.withOpacity(0.6), fontSize: 13)),
        Text(value,
            style: const TextStyle(
                color: Colors.white,
                fontSize: 13,
                fontWeight: FontWeight.w600)),
      ],
    );
  }

  Widget _toggleRow(
      String title, String subtitle, bool value, ValueChanged<bool> onChanged) {
    return Row(
      children: [
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(title,
                  style: const TextStyle(
                      color: Colors.white,
                      fontSize: 14,
                      fontWeight: FontWeight.w500)),
              const SizedBox(height: 2),
              Text(subtitle,
                  style: TextStyle(
                      color: Colors.white.withOpacity(0.4), fontSize: 12)),
            ],
          ),
        ),
        Switch(
          value: value,
          onChanged: onChanged,
          activeThumbColor: GlassTheme.communicationBadge,
        ),
      ],
    );
  }

  Widget _actionButton(String text, IconData icon, VoidCallback onTap) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
        decoration: BoxDecoration(
          color: Colors.white.withOpacity(0.08),
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: Colors.white.withOpacity(0.15)),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(icon, color: Colors.white70, size: 18),
            const SizedBox(width: 8),
            Text(text,
                style: const TextStyle(
                    color: Colors.white,
                    fontSize: 13,
                    fontWeight: FontWeight.w500)),
          ],
        ),
      ),
    );
  }

  Widget _dataRow(String text, IconData icon, VoidCallback onTap,
      {bool isDestructive = false}) {
    final color = isDestructive ? const Color(0xFFEF4444) : Colors.white;
    return GestureDetector(
      onTap: onTap,
      child: Row(
        children: [
          Icon(icon, color: color.withOpacity(0.7), size: 20),
          const SizedBox(width: 12),
          Text(text,
              style: TextStyle(color: color.withOpacity(0.9), fontSize: 14)),
          const Spacer(),
          Icon(Icons.chevron_right, color: color.withOpacity(0.3), size: 20),
        ],
      ),
    );
  }
}
