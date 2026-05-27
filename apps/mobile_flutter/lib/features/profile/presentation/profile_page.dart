import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import '../../../core/models/health_profile.dart';

// ── Light theme tokens (đồng bộ các tab khác) ──
const _kBg = Color(0xFFF8FAFC);
const _kBorder = Color(0xFFE2E8F0);
const _kInk = Color(0xFF0F172A);
const _kInkSoft = Color(0xFF475569);
const _kInkMuted = Color(0xFF94A3B8);
const _kDanger = Color(0xFFDC2626);

// ── Soul Garden palette (light leaf) ──
const _kLeaf = Color(0xFF16A34A);
const _kLeafLight = Color(0xFF22C55E);
const _kLeafSoft = Color(0xFFDCFCE7);
const _kLeafSofter = Color(0xFFF0FDF4);

// ── Stat colors ──
const _kStarPurple = Color(0xFF8B5CF6);
const _kStarPurpleBg = Color(0xFFEDE9FE);
const _kHeartPink = Color(0xFFEC4899);
const _kHeartPinkBg = Color(0xFFFCE7F3);
const _kBadgeYellow = Color(0xFFEAB308);
const _kBadgeYellowBg = Color(0xFFFEF3C7);

/// Profile (Hồ sơ) — chỉ content, không header (theo yêu cầu).
/// Layout đúng screenshot: profile card + 4 stat + menu list + logout.
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
    return Scaffold(
      backgroundColor: _kBg,
      body: SafeArea(
        bottom: false,
        child: ListView(
          padding: const EdgeInsets.fromLTRB(16, 12, 16, 24),
          physics: const BouncingScrollPhysics(),
          children: [
            const _ProfileHeroCard(),
            const SizedBox(height: 14),
            const _StatsGrid(),
            const SizedBox(height: 14),
            _MenuCard(
              onOpenSettings: onOpenSettings,
              onOpenMedicineCabinet: onOpenMedicineCabinet,
            ),
            const SizedBox(height: 12),
            const _LogoutButton(),
          ],
        ),
      ),
    );
  }
}

// ───────────────────────── PROFILE HERO CARD ─────────────────────────

class _ProfileHeroCard extends StatelessWidget {
  const _ProfileHeroCard();

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [_kLeafSofter, Color(0xFFF7FEE7)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: Colors.white, width: 1.5),
      ),
      padding: const EdgeInsets.fromLTRB(16, 16, 16, 16),
      child: Stack(
        clipBehavior: Clip.none,
        children: [
          // Plant illustration bên phải
          Positioned(
            right: -6,
            top: -6,
            bottom: -6,
            child: _PlantPlaceholder(),
          ),
          Padding(
            padding: const EdgeInsets.only(right: 100),
            child: Row(
              children: [
                const _AvatarWithEdit(),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    mainAxisSize: MainAxisSize.min,
                    children: const [
                      Text(
                        'Nguyễn An',
                        style: TextStyle(
                          fontFamily: 'Outfit',
                          fontSize: 20,
                          fontWeight: FontWeight.w800,
                          color: _kInk,
                          height: 1.1,
                        ),
                      ),
                      SizedBox(height: 6),
                      Row(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Padding(
                            padding: EdgeInsets.only(top: 2),
                            child: Icon(Icons.eco_rounded,
                                size: 13, color: _kLeaf),
                          ),
                          SizedBox(width: 4),
                          Expanded(
                            child: Text(
                              'Đang trên hành trình\nchăm sóc tâm hồn',
                              style: TextStyle(
                                fontFamily: 'Outfit',
                                fontSize: 12,
                                color: _kInkSoft,
                                height: 1.35,
                              ),
                            ),
                          ),
                        ],
                      ),
                      SizedBox(height: 8),
                      _MemberBadge(),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _AvatarWithEdit extends StatelessWidget {
  const _AvatarWithEdit();

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: 76,
      height: 76,
      child: Stack(
        clipBehavior: Clip.none,
        children: [
          Container(
            width: 76,
            height: 76,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              border: Border.all(color: Colors.white, width: 3),
              gradient: const LinearGradient(
                colors: [Color(0xFFF1F5F9), Color(0xFFE2E8F0)],
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
              ),
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withOpacity(0.08),
                  blurRadius: 10,
                  offset: const Offset(0, 4),
                ),
              ],
            ),
            child: const Center(
              child: Icon(Icons.person_rounded,
                  size: 38, color: _kInkMuted),
            ),
          ),
          Positioned(
            right: -2,
            bottom: 2,
            child: InkResponse(
              onTap: () => HapticFeedback.lightImpact(),
              radius: 18,
              child: Container(
                width: 26,
                height: 26,
                decoration: BoxDecoration(
                  color: Colors.white,
                  shape: BoxShape.circle,
                  border: Border.all(color: _kBorder),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withOpacity(0.06),
                      blurRadius: 4,
                      offset: const Offset(0, 1),
                    ),
                  ],
                ),
                child: const Icon(Icons.edit_outlined,
                    size: 13, color: _kInkSoft),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _MemberBadge extends StatelessWidget {
  const _MemberBadge();

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
      decoration: BoxDecoration(
        color: _kLeafSoft,
        borderRadius: BorderRadius.circular(999),
        border: Border.all(color: _kLeafLight.withOpacity(0.4)),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: const [
          Icon(Icons.eco_rounded, size: 12, color: _kLeaf),
          SizedBox(width: 4),
          Text(
            'Thành viên Soul Garden',
            style: TextStyle(
              fontFamily: 'Outfit',
              fontSize: 11,
              fontWeight: FontWeight.w700,
              color: _kLeaf,
            ),
          ),
        ],
      ),
    );
  }
}

class _PlantPlaceholder extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Container(
      width: 110,
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [_kLeafSoft, _kLeafLight.withOpacity(0.45)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: const BorderRadius.only(
          topRight: Radius.circular(16),
          bottomRight: Radius.circular(16),
          topLeft: Radius.circular(50),
          bottomLeft: Radius.circular(50),
        ),
      ),
      child: const Center(
        child: Icon(Icons.local_florist_rounded,
            color: Colors.white, size: 48),
      ),
    );
  }
}

// ───────────────────────── 4 STAT GRID ─────────────────────────

class _StatsGrid extends StatelessWidget {
  const _StatsGrid();

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: _kBorder),
      ),
      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 14),
      child: Row(
        children: const [
          Expanded(
            child: _StatItem(
              icon: Icons.eco_rounded,
              iconColor: _kLeaf,
              iconBg: _kLeafSoft,
              value: '28',
              line1: 'Ngày đồng hành',
              line2: 'liên tiếp',
            ),
          ),
          Expanded(
            child: _StatItem(
              icon: Icons.star_rounded,
              iconColor: _kStarPurple,
              iconBg: _kStarPurpleBg,
              value: '156',
              line1: 'Khoảnh khắc',
              line2: 'đã ghi lại',
            ),
          ),
          Expanded(
            child: _StatItem(
              icon: Icons.favorite_rounded,
              iconColor: _kHeartPink,
              iconBg: _kHeartPinkBg,
              value: '78',
              line1: 'Điểm cảm xúc',
              line2: 'trung bình',
            ),
          ),
          Expanded(
            child: _StatItem(
              icon: Icons.emoji_events_rounded,
              iconColor: _kBadgeYellow,
              iconBg: _kBadgeYellowBg,
              value: '12',
              line1: 'Huy hiệu',
              line2: 'đã đạt được',
            ),
          ),
        ],
      ),
    );
  }
}

class _StatItem extends StatelessWidget {
  const _StatItem({
    required this.icon,
    required this.iconColor,
    required this.iconBg,
    required this.value,
    required this.line1,
    required this.line2,
  });

  final IconData icon;
  final Color iconColor;
  final Color iconBg;
  final String value;
  final String line1;
  final String line2;

  @override
  Widget build(BuildContext context) {
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        Container(
          width: 44,
          height: 44,
          decoration: BoxDecoration(
            color: iconBg,
            shape: BoxShape.circle,
          ),
          child: Icon(icon, size: 22, color: iconColor),
        ),
        const SizedBox(height: 8),
        Text(
          value,
          style: const TextStyle(
            fontFamily: 'Outfit',
            fontSize: 22,
            fontWeight: FontWeight.w800,
            color: _kInk,
            height: 1.0,
          ),
        ),
        const SizedBox(height: 4),
        Text(
          line1,
          textAlign: TextAlign.center,
          style: const TextStyle(
            fontFamily: 'Outfit',
            fontSize: 10.5,
            color: _kInkSoft,
            height: 1.2,
          ),
        ),
        Text(
          line2,
          textAlign: TextAlign.center,
          style: const TextStyle(
            fontFamily: 'Outfit',
            fontSize: 10.5,
            color: _kInkSoft,
            height: 1.2,
          ),
        ),
      ],
    );
  }
}

// ───────────────────────── MENU LIST ─────────────────────────

class _MenuCard extends StatelessWidget {
  const _MenuCard({
    required this.onOpenSettings,
    required this.onOpenMedicineCabinet,
  });

  final VoidCallback onOpenSettings;
  final VoidCallback onOpenMedicineCabinet;

  @override
  Widget build(BuildContext context) {
    final items = <_MenuRowData>[
      _MenuRowData(
        icon: Icons.person_outline_rounded,
        iconColor: _kInkSoft,
        iconBg: const Color(0xFFF1F5F9),
        title: 'Thông tin cá nhân',
        sub: 'Cập nhật thông tin của bạn',
        onTap: onOpenSettings,
      ),
      _MenuRowData(
        icon: Icons.eco_rounded,
        iconColor: _kLeaf,
        iconBg: _kLeafSoft,
        title: 'Vườn cây của tôi',
        sub: 'Xem và chăm sóc khu vườn cảm xúc',
      ),
      _MenuRowData(
        icon: Icons.menu_book_rounded,
        iconColor: const Color(0xFF3B82F6),
        iconBg: const Color(0xFFDBEAFE),
        title: 'Nhật ký của tôi',
        sub: 'Xem lại hành trình cảm xúc',
      ),
      _MenuRowData(
        icon: Icons.emoji_events_rounded,
        iconColor: _kBadgeYellow,
        iconBg: _kBadgeYellowBg,
        title: 'Huy hiệu & Thành tựu',
        sub: 'Thành tích trong hành trình chữa lành',
      ),
      _MenuRowData(
        icon: Icons.music_note_rounded,
        iconColor: _kStarPurple,
        iconBg: _kStarPurpleBg,
        title: 'Âm nhạc yêu thích',
        sub: 'Những giai điệu giúp bạn thư giãn',
      ),
      _MenuRowData(
        icon: Icons.lock_outline_rounded,
        iconColor: _kInkSoft,
        iconBg: const Color(0xFFF1F5F9),
        title: 'Quyền riêng tư',
        sub: 'Kiểm soát dữ liệu và quyền riêng tư',
      ),
      _MenuRowData(
        icon: Icons.help_outline_rounded,
        iconColor: const Color(0xFF0EA5E9),
        iconBg: const Color(0xFFE0F2FE),
        title: 'Trung tâm hỗ trợ',
        sub: 'Câu hỏi thường gặp và trợ giúp',
      ),
    ];

    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: _kBorder),
      ),
      child: Column(
        children: List.generate(items.length, (i) {
          final isFirst = i == 0;
          final isLast = i == items.length - 1;
          return _MenuRow(
            data: items[i],
            isFirst: isFirst,
            isLast: isLast,
          );
        }),
      ),
    );
  }
}

class _MenuRowData {
  final IconData icon;
  final Color iconColor;
  final Color iconBg;
  final String title;
  final String sub;
  final VoidCallback? onTap;

  _MenuRowData({
    required this.icon,
    required this.iconColor,
    required this.iconBg,
    required this.title,
    required this.sub,
    this.onTap,
  });
}

class _MenuRow extends StatelessWidget {
  const _MenuRow({
    required this.data,
    required this.isFirst,
    required this.isLast,
  });

  final _MenuRowData data;
  final bool isFirst;
  final bool isLast;

  @override
  Widget build(BuildContext context) {
    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: () {
          HapticFeedback.selectionClick();
          data.onTap?.call();
        },
        borderRadius: BorderRadius.vertical(
          top: isFirst ? const Radius.circular(20) : Radius.zero,
          bottom: isLast ? const Radius.circular(20) : Radius.zero,
        ),
        child: Container(
          decoration: BoxDecoration(
            border: !isLast
                ? const Border(
                    bottom: BorderSide(color: _kBorder, width: 0.6),
                  )
                : null,
          ),
          padding: const EdgeInsets.fromLTRB(14, 12, 14, 12),
          child: Row(
            children: [
              Container(
                width: 36,
                height: 36,
                decoration: BoxDecoration(
                  color: data.iconBg,
                  borderRadius: BorderRadius.circular(10),
                ),
                child: Icon(data.icon, size: 18, color: data.iconColor),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Text(
                      data.title,
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      style: const TextStyle(
                        fontFamily: 'Outfit',
                        fontSize: 14,
                        fontWeight: FontWeight.w700,
                        color: _kInk,
                        height: 1.2,
                      ),
                    ),
                    const SizedBox(height: 2),
                    Text(
                      data.sub,
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      style: const TextStyle(
                        fontFamily: 'Outfit',
                        fontSize: 11.5,
                        color: _kInkSoft,
                        height: 1.2,
                      ),
                    ),
                  ],
                ),
              ),
              const Icon(Icons.chevron_right_rounded,
                  size: 20, color: _kInkMuted),
            ],
          ),
        ),
      ),
    );
  }
}

// ───────────────────────── LOGOUT ─────────────────────────

class _LogoutButton extends StatelessWidget {
  const _LogoutButton();

  @override
  Widget build(BuildContext context) {
    return Material(
      color: Colors.white,
      borderRadius: BorderRadius.circular(20),
      child: InkWell(
        onTap: () => HapticFeedback.lightImpact(),
        borderRadius: BorderRadius.circular(20),
        child: Container(
          padding: const EdgeInsets.fromLTRB(14, 14, 14, 14),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(20),
            border: Border.all(color: _kBorder),
          ),
          child: Row(
            children: [
              Container(
                width: 36,
                height: 36,
                decoration: BoxDecoration(
                  color: _kDanger.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(10),
                ),
                child: const Icon(Icons.logout_rounded,
                    size: 18, color: _kDanger),
              ),
              const SizedBox(width: 12),
              const Text(
                'Đăng xuất',
                style: TextStyle(
                  fontFamily: 'Outfit',
                  fontSize: 14,
                  fontWeight: FontWeight.w700,
                  color: _kDanger,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
