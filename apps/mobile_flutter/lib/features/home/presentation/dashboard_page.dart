import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import '../../../core/models/achievement_model.dart';
import '../../../core/models/consult_mode.dart';
import '../../../core/network/api_contracts.dart';
import '../../../core/services/achievement_service.dart';
import '../../../core/services/accessibility_config.dart';
import '../../../core/services/emergency_service.dart';
import '../../../core/theme/glass_theme.dart';
import '../../consult/presentation/accessible_consult_page.dart';
import '../../consult/presentation/consult_page.dart';

class DashboardPage extends StatefulWidget {
  const DashboardPage({
    super.key,
    required this.mode,
    required this.consultApi,
    required this.onOpenMedicine,
    this.onOpenDoctorHub,
    this.onOpenAchievements,
    this.onOpenCommunity,
  });

  final ConsultMode mode;
  final ConsultApi consultApi;
  final VoidCallback onOpenMedicine;
  final VoidCallback? onOpenDoctorHub;
  final VoidCallback? onOpenAchievements;
  final VoidCallback? onOpenCommunity;

  @override
  State<DashboardPage> createState() => _DashboardPageState();
}

class _DashboardPageState extends State<DashboardPage> {
  final AchievementService _achievementService = AchievementService();
  List<ActivityStreak> _streaks = [];

  @override
  void initState() {
    super.initState();
    _loadStreaks();
  }

  Future<void> _loadStreaks() async {
    final summary = await _achievementService.getSummary();
    if (mounted) {
      setState(() => _streaks = summary.streaks);
    }
  }

  Color _modeColor() {
    switch (widget.mode) {
      case ConsultMode.hybrid:
        return GlassTheme.primaryGreen;
      case ConsultMode.local:
        return GlassTheme.accentBlue;
      case ConsultMode.cloud:
        return GlassTheme.accentPurple;
    }
  }

  void _openAccessibleConsult(BuildContext context) {
    HapticFeedback.mediumImpact();
    Navigator.of(context).push(GlassTheme.route(
      AccessibleConsultPage(
        onBack: () => Navigator.of(context).pop(),
      ),
    ));
  }

  @override
  Widget build(BuildContext context) {
    final modeColor = _modeColor();
    return GlassTheme.scaffoldBackground(
      child: SafeArea(
        child: RefreshIndicator(
          color: GlassTheme.primaryGreenLight,
          backgroundColor: GlassTheme.navBackground,
          onRefresh: _loadStreaks,
          child: ListView(
            padding: const EdgeInsets.fromLTRB(20, 16, 20, 24),
            children: [
              _buildHeader(modeColor),
              const SizedBox(height: 24),

              // ── ZONE 1: Primary action (one clear CTA — Hick’s Law) ──
              _buildBigConsultButton(context, modeColor),
              const SizedBox(height: 28),

              // ── ZONE 2: Daily momentum (streaks — dopamine feedback) ──
              if (_streaks.any((s) => s.currentStreak > 0)) ...[
                _buildStreaksRow(),
                const SizedBox(height: 28)
              ],

              // ── ZONE 3: Feature grid (grouped — Gestalt proximity) ──
              _buildSectionLabel('Tính năng chính'),
              const SizedBox(height: 14),

              _buildFeatureCard(
                context: context,
                title: 'Hỏi bệnh (Text)',
                subtitle: 'Gõ chữ mô tả triệu chứng',
                emoji: '💬',
                iconColor: GlassTheme.primaryGreen,
                onTap: () {
                  Navigator.of(context).push(GlassTheme.route(
                    ConsultPage(
                        mode: widget.mode, consultApi: widget.consultApi),
                  ));
                },
              ),

              _buildFeatureCard(
                context: context,
                title: 'Quét thuốc',
                subtitle: 'Đọc OCR và kiểm tra rủi ro',
                emoji: '💊',
                iconColor: GlassTheme.accentBlue,
                onTap: widget.onOpenMedicine,
              ),

              _buildFeatureCard(
                context: context,
                title: 'Thành tựu',
                subtitle: 'Xem chuỗi hoạt động và huy chương',
                emoji: '🏆',
                iconColor: GlassTheme.accentOrange,
                onTap: () => widget.onOpenAchievements?.call(),
              ),
              const SizedBox(height: 24),

              // ── ZONE 4: Khám phá thêm (Progressive Disclosure) ──
              _buildSectionLabel('Khám phá thêm'),
              const SizedBox(height: 14),

              _buildDoctorHubBanner(),
              const SizedBox(height: 12),

              _buildFeatureCard(
                context: context,
                title: 'Nhật ký sức khỏe',
                subtitle: 'Theo dõi tâm trạng và thói quen',
                emoji: '📝',
                iconColor: GlassTheme.accentPurple,
                onTap: () => _showComingSoon(context, 'Nhật ký sức khỏe'),
              ),

              _buildFeatureCard(
                context: context,
                title: 'Cộng đồng lạc quan',
                subtitle: 'Chia sẻ & kết nối — chống cô đơn',
                emoji: '🤗',
                iconColor: GlassTheme.accentOrange,
                onTap: () => widget.onOpenCommunity?.call(),
              ),

              const SizedBox(height: 24),

              // ── ZONE 5: Summary ──
              _buildSummaryCard(modeColor),
            ],
          ),
        ),
      ),
    );
  }

  // ── Doctor Hub Banner ──
  Widget _buildDoctorHubBanner() {
    return GestureDetector(
      onTap: () {
        HapticFeedback.mediumImpact();
        widget.onOpenDoctorHub?.call();
      },
      child: GlassTheme.glassCard(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
        fillColor: GlassTheme.accentPurple.withOpacity(0.12),
        borderColor: GlassTheme.accentPurple.withOpacity(0.3),
        child: Row(
          children: [
            Container(
              width: 48,
              height: 48,
              decoration: BoxDecoration(
                color: GlassTheme.accentPurple.withOpacity(0.2),
                borderRadius: BorderRadius.circular(14),
              ),
              child: const Center(
                child: Text('🏥', style: TextStyle(fontSize: 26)),
              ),
            ),
            const SizedBox(width: 14),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'Bác sĩ 3D',
                    style: TextStyle(
                      fontFamily: 'Outfit',
                      fontSize: 16,
                      fontWeight: FontWeight.w700,
                      color: Colors.white,
                    ),
                  ),
                  Text(
                    'Tương tác trực quan + ngôn ngữ ký hiệu',
                    style: TextStyle(
                      fontFamily: 'Outfit',
                      fontSize: 13,
                      color: Colors.white.withOpacity(0.7),
                    ),
                  ),
                ],
              ),
            ),
            GlassTheme.badge(
              text: 'Mới',
              backgroundColor: GlassTheme.accentPurple.withOpacity(0.25),
              textColor: const Color(0xFFA78BFA),
            ),
          ],
        ),
      ),
    );
  }

  // ── Streaks Row ──
  Widget _buildStreaksRow() {
    final active = _streaks.where((s) => s.currentStreak > 0).toList();
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            const Text('🔥', style: TextStyle(fontSize: 18)),
            const SizedBox(width: 6),
            Text('Chuỗi hoạt động',
                style: GlassTheme.h3.copyWith(fontSize: 16)),
          ],
        ),
        const SizedBox(height: 10),
        SizedBox(
          height: 80,
          child: ListView.separated(
            scrollDirection: Axis.horizontal,
            itemCount: active.length,
            separatorBuilder: (_, __) => const SizedBox(width: 10),
            itemBuilder: (_, i) {
              final s = active[i];
              return GlassTheme.glassCard(
                padding:
                    const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Text(s.category.emoji,
                        style: const TextStyle(fontSize: 24)),
                    const SizedBox(width: 10),
                    Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          '${s.currentStreak} ngày',
                          style: const TextStyle(
                            fontFamily: GlassTheme.fontFamily,
                            fontSize: 18,
                            fontWeight: FontWeight.w800,
                            color: GlassTheme.accentOrange,
                          ),
                        ),
                        Text(
                          s.category.label,
                          style: GlassTheme.caption.copyWith(fontSize: 11),
                        ),
                      ],
                    ),
                    if (s.isActiveToday) ...[
                      const SizedBox(width: 8),
                      const Text('✅', style: TextStyle(fontSize: 14)),
                    ],
                  ],
                ),
              );
            },
          ),
        ),
      ],
    );
  }

  // ── Section Label (Gestalt grouping) ──
  Widget _buildSectionLabel(String text) {
    return Row(
      children: [
        Container(
          width: 4,
          height: 20,
          decoration: BoxDecoration(
            color: GlassTheme.primaryGreen,
            borderRadius: BorderRadius.circular(2),
          ),
        ),
        const SizedBox(width: 10),
        Text(text, style: GlassTheme.h3.copyWith(fontSize: 16)),
      ],
    );
  }

  Widget _buildHeader(Color modeColor) {
    return Row(
      children: [
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text('Xin chào 👋', style: GlassTheme.caption),
              const SizedBox(height: 4),
              const Text('MediSign AI', style: GlassTheme.h1),
              const SizedBox(height: 4),
              Text(
                'đồng hành cùng bạn',
                style: GlassTheme.body.copyWith(color: Colors.white70),
              ),
            ],
          ),
        ),
        // Emergency button — serious medical design
        Semantics(
          label: 'Gọi cấp cứu 115',
          button: true,
          child: GestureDetector(
            onTap: () {
              HapticFeedback.heavyImpact();
              EmergencyService().triggerEmergency(context);
            },
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
              decoration: BoxDecoration(
                color: GlassTheme.emergencyRed.withOpacity(0.12),
                borderRadius: BorderRadius.circular(16),
                border: Border.all(
                  color: GlassTheme.emergencyRed.withOpacity(0.35),
                  width: 1.5,
                ),
              ),
              child: const Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(Icons.emergency_rounded,
                      color: GlassTheme.emergencyRedLight, size: 20),
                  SizedBox(width: 6),
                  Text(
                    '115',
                    style: TextStyle(
                      fontFamily: GlassTheme.fontFamily,
                      fontSize: 15,
                      fontWeight: FontWeight.w800,
                      color: GlassTheme.emergencyRedLight,
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      ],
    );
  }

  /// Large accessible "Bác sĩ ơi" button — the PRIMARY entry point
  Widget _buildBigConsultButton(BuildContext context, Color modeColor) {
    return Semantics(
      label: 'Bác sĩ ơi. Nhấn để hỏi bệnh bằng hình ảnh, không cần gõ chữ.',
      button: true,
      child: GestureDetector(
        onTap: () => _openAccessibleConsult(context),
        behavior: HitTestBehavior.opaque,
        child: Container(
          padding: const EdgeInsets.all(20),
          decoration: BoxDecoration(
            gradient: const LinearGradient(
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
              colors: [GlassTheme.tealPrimary, GlassTheme.tealDark],
            ),
            borderRadius: BorderRadius.circular(24),
            boxShadow: [
              BoxShadow(
                color: GlassTheme.tealPrimary.withOpacity(0.35),
                blurRadius: 20,
                offset: const Offset(0, 8),
              ),
            ],
          ),
          child: Row(
            children: [
              // Large icon
              Container(
                width: 80,
                height: 80,
                decoration: BoxDecoration(
                  color: Colors.white.withOpacity(0.15),
                  borderRadius: BorderRadius.circular(24),
                ),
                child: const Center(
                  child: Text('🩺', style: TextStyle(fontSize: 42)),
                ),
              ),
              const SizedBox(width: 18),
              // Text content
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      'Bác sĩ ơi',
                      style: TextStyle(
                        fontFamily: GlassTheme.fontFamily,
                        fontSize: 26,
                        fontWeight: FontWeight.w800,
                        color: Colors.white,
                      ),
                    ),
                    const SizedBox(height: 6),
                    Text(
                      'Chạm hình chỉ vùng đau — không cần gõ chữ',
                      style: TextStyle(
                        fontFamily: GlassTheme.fontFamily,
                        fontSize: 14,
                        color: Colors.white.withOpacity(0.85),
                      ),
                    ),
                    const SizedBox(height: 10),
                    // Accessibility badges
                    Row(
                      children: [
                        _accessBadge('👆'),
                        const SizedBox(width: 8),
                        _accessBadge('🤟'),
                        const SizedBox(width: 8),
                        _accessBadge('🎤'),
                      ],
                    ),
                  ],
                ),
              ),
              const Icon(
                Icons.arrow_forward_rounded,
                color: Colors.white70,
                size: 32,
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _accessBadge(String emoji) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.15),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Text(emoji, style: const TextStyle(fontSize: 16)),
    );
  }

  Widget _buildFeatureCard({
    required BuildContext context,
    required String title,
    required String subtitle,
    required String emoji,
    required Color iconColor,
    required VoidCallback onTap,
  }) {
    final a11y = AccessibilityConfig.instance;
    final iconSize = 56.0 * a11y.iconScale;
    final emojiSize = 28.0 * a11y.iconScale;
    final titleSize = 17.0 * a11y.fontScale;
    final subSize = 14.0 * a11y.fontScale;

    return GlassTheme.glassCard(
      padding: EdgeInsets.all(a11y.elementSpacing + 4),
      margin: EdgeInsets.only(bottom: a11y.elementSpacing),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(20),
        child: Row(
          children: [
            Container(
              width: iconSize,
              height: iconSize,
              decoration: BoxDecoration(
                color: iconColor.withOpacity(a11y.highContrast ? 0.25 : 0.15),
                borderRadius: BorderRadius.circular(16),
              ),
              child: Center(
                child: Text(emoji, style: TextStyle(fontSize: emojiSize)),
              ),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: TextStyle(
                      fontFamily: 'Outfit',
                      fontSize: titleSize,
                      fontWeight: FontWeight.w700,
                      color: Colors.white,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    subtitle,
                    style: TextStyle(
                      fontFamily: 'Outfit',
                      fontSize: subSize,
                      color: Colors.white
                          .withOpacity(a11y.highContrast ? 0.85 : 0.7),
                    ),
                  ),
                ],
              ),
            ),
            Icon(
              Icons.chevron_right_rounded,
              color: Colors.white.withOpacity(0.5),
              size: 28,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSummaryCard(Color modeColor) {
    return GlassTheme.glassCard(
      padding: const EdgeInsets.all(18),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Text('📋', style: TextStyle(fontSize: 22)),
              const SizedBox(width: 10),
              Text('Tóm tắt hôm nay',
                  style: GlassTheme.h3.copyWith(fontSize: 16)),
            ],
          ),
          const SizedBox(height: 16),
          _summaryRow(
            icon: '⚙️',
            label: 'Chế độ hoạt động',
            value: widget.mode.title,
            color: modeColor,
          ),
          const SizedBox(height: 12),
          _summaryRow(
            icon: '💊',
            label: 'Nhắc nhở',
            value: 'Kiểm tra tương tác thuốc trước khi dùng',
            color: GlassTheme.accentBlue,
          ),
        ],
      ),
    );
  }

  Widget _summaryRow({
    required String icon,
    required String label,
    required String value,
    required Color color,
  }) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(icon, style: const TextStyle(fontSize: 18)),
        const SizedBox(width: 10),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                label,
                style: TextStyle(
                  fontFamily: 'Outfit',
                  fontWeight: FontWeight.w600,
                  color: Colors.white.withOpacity(0.6),
                  fontSize: 13,
                ),
              ),
              const SizedBox(height: 2),
              Text(
                value,
                style: TextStyle(
                  fontFamily: 'Outfit',
                  color: Colors.white.withOpacity(0.9),
                  fontSize: 14,
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  void _showComingSoon(BuildContext context, String feature) {
    GlassTheme.showGlassSnackBar(
      context,
      '$feature sẽ được hoàn thiện ở bước tiếp theo.',
      emoji: '🔜',
    );
  }
}
