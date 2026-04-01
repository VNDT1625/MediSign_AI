import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import '../../../core/models/health_profile.dart';
import '../../../core/theme/glass_theme.dart';

/// User profile page — shows health summary and links to sub-features.
class ProfilePage extends StatelessWidget {
  const ProfilePage({
    super.key,
    required this.healthProfile,
    required this.onOpenMedicineCabinet,
    required this.onOpenSettings,
  });

  final HealthProfile healthProfile;
  final VoidCallback onOpenMedicineCabinet;
  final VoidCallback onOpenSettings;

  @override
  Widget build(BuildContext context) {
    return GlassTheme.scaffoldBackground(
      child: SafeArea(
        child: ListView(
          padding: const EdgeInsets.fromLTRB(20, 20, 20, 32),
          children: [
            _buildHeader(),
            const SizedBox(height: 24),
            _buildHealthSummaryCard(),
            const SizedBox(height: 20),
            _buildInfoCards(),
            const SizedBox(height: 20),
            _buildMenuItems(context),
          ],
        ),
      ),
    );
  }

  Widget _buildHeader() {
    return Row(
      children: [
        Container(
          width: 72,
          height: 72,
          decoration: BoxDecoration(
            gradient: const LinearGradient(
              colors: [Color(0xFF60A5FA), Color(0xFF3B82F6)],
            ),
            borderRadius: BorderRadius.circular(24),
            boxShadow: [
              BoxShadow(
                color: const Color(0xFF3B82F6).withOpacity(0.3),
                blurRadius: 16,
                offset: const Offset(0, 6),
              ),
            ],
          ),
          child: Center(
            child: Text(
              healthProfile.gender?.emoji ?? '👤',
              style: const TextStyle(fontSize: 36),
            ),
          ),
        ),
        const SizedBox(width: 18),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text('Hồ sơ cá nhân', style: GlassTheme.h2),
              const SizedBox(height: 4),
              Text(
                _buildSubtitle(),
                style: GlassTheme.body,
              ),
            ],
          ),
        ),
      ],
    );
  }

  String _buildSubtitle() {
    final parts = <String>[];
    if (healthProfile.age != null) parts.add('${healthProfile.age} tuổi');
    if (healthProfile.gender != null) parts.add(healthProfile.gender!.label);
    return parts.isEmpty ? 'Chưa cập nhật' : parts.join(' • ');
  }

  Widget _buildHealthSummaryCard() {
    return GlassTheme.glassCard(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Text('🏥', style: TextStyle(fontSize: 24)),
              const SizedBox(width: 10),
              Text('Tóm tắt sức khỏe',
                  style: GlassTheme.h3.copyWith(fontSize: 16)),
            ],
          ),
          const SizedBox(height: 18),
          Row(
            children: [
              Expanded(
                  child: _summaryItem(
                      '🎂', 'Tuổi', healthProfile.age?.toString() ?? '—')),
              Expanded(
                  child: _summaryItem(healthProfile.gender?.emoji ?? '👤',
                      'Giới tính', healthProfile.gender?.label ?? '—')),
            ],
          ),
          const SizedBox(height: 14),
          Row(
            children: [
              Expanded(
                  child: _summaryItem(
                      '💊',
                      'Dị ứng thuốc',
                      healthProfile.drugAllergies.isEmpty
                          ? 'Không'
                          : '${healthProfile.drugAllergies.length} loại')),
              Expanded(
                  child: _summaryItem(
                      '🏥',
                      'Bệnh nền',
                      healthProfile.preConditions.isEmpty
                          ? 'Không'
                          : '${healthProfile.preConditions.length} bệnh')),
            ],
          ),
        ],
      ),
    );
  }

  Widget _summaryItem(String emoji, String label, String value) {
    return Container(
      padding: const EdgeInsets.all(14),
      margin: const EdgeInsets.symmetric(horizontal: 4),
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.06),
        borderRadius: BorderRadius.circular(14),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(emoji, style: const TextStyle(fontSize: 22)),
          const SizedBox(height: 8),
          Text(label,
              style: TextStyle(
                  color: Colors.white.withOpacity(0.5), fontSize: 12)),
          const SizedBox(height: 2),
          Text(value,
              style: const TextStyle(
                  color: Colors.white,
                  fontSize: 15,
                  fontWeight: FontWeight.w600)),
        ],
      ),
    );
  }

  Widget _buildInfoCards() {
    return Column(
      children: [
        if (healthProfile.drugAllergies.isNotEmpty)
          _infoSection(
              '💊', 'Dị ứng thuốc', healthProfile.drugAllergies.join(', ')),
        if (healthProfile.preConditions.isNotEmpty &&
            !healthProfile.preConditions.contains(PreCondition.none))
          _infoSection('🏥', 'Bệnh nền',
              healthProfile.preConditions.map((c) => c.label).join(', ')),
        if (healthProfile.difficulties.isNotEmpty &&
            !healthProfile.difficulties.contains(Difficulty.none))
          _infoSection('♿', 'Khó khăn',
              healthProfile.difficulties.map((d) => d.label).join(', ')),
      ],
    );
  }

  Widget _infoSection(String emoji, String title, String content) {
    return GlassTheme.glassCard(
      padding: const EdgeInsets.all(16),
      margin: const EdgeInsets.only(bottom: 10),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(emoji, style: const TextStyle(fontSize: 24)),
          const SizedBox(width: 14),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(title, style: GlassTheme.button.copyWith(fontSize: 14)),
                const SizedBox(height: 4),
                Text(content, style: GlassTheme.body.copyWith(fontSize: 13)),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildMenuItems(BuildContext context) {
    return Column(
      children: [
        _menuItem(
          emoji: '💊',
          title: 'Tủ thuốc cá nhân',
          subtitle: 'Quản lý thuốc đang dùng',
          onTap: () {
            HapticFeedback.lightImpact();
            onOpenMedicineCabinet();
          },
        ),
        _menuItem(
          emoji: '📋',
          title: 'Lịch sử tư vấn',
          subtitle: 'Xem lại các lần hỏi bệnh',
          onTap: () {
            HapticFeedback.lightImpact();
            GlassTheme.showGlassSnackBar(
              context,
              'Tính năng đang phát triển',
              emoji: '🔜',
            );
          },
        ),
        _menuItem(
          emoji: '⚙️',
          title: 'Cài đặt',
          subtitle: 'Chế độ hoạt động, trợ năng, bảo mật',
          onTap: () {
            HapticFeedback.lightImpact();
            onOpenSettings();
          },
        ),
      ],
    );
  }

  Widget _menuItem({
    required String emoji,
    required String title,
    required String subtitle,
    required VoidCallback onTap,
  }) {
    return GlassTheme.glassCard(
      padding: const EdgeInsets.all(16),
      margin: const EdgeInsets.only(bottom: 10),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(20),
        child: Row(
          children: [
            Text(emoji, style: const TextStyle(fontSize: 26)),
            const SizedBox(width: 14),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(title, style: GlassTheme.button.copyWith(fontSize: 15)),
                  Text(subtitle, style: GlassTheme.caption),
                ],
              ),
            ),
            Icon(Icons.chevron_right,
                color: Colors.white.withOpacity(0.4), size: 24),
          ],
        ),
      ),
    );
  }
}
