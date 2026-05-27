import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import '../../../core/models/consult_mode.dart';
import '../../../core/network/api_contracts.dart';

// ── Light theme tokens (cục bộ cho Home để không đụng glass_theme dark) ──
const _kBrand = Color(0xFF0284C7);
const _kBrandLight = Color(0xFF38BDF8);
const _kBrandSoft = Color(0xFFE0F2FE);
const _kBrandSofter = Color(0xFFF0F9FF);
const _kBg = Color(0xFFF8FAFC);
const _kBorder = Color(0xFFE2E8F0);
const _kInk = Color(0xFF0F172A);
const _kInkSoft = Color(0xFF475569);
const _kInkMuted = Color(0xFF94A3B8);
const _kSuccess = Color(0xFF10B981);
const _kDanger = Color(0xFFEF4444);

/// Trang Home mobile — light theme, layout đúng screenshot.
/// Các props legacy [mode], [consultApi], [onOpenMedicine], ... được giữ
/// để không phá call site hiện có; phần lớn không dùng trong layout mới
/// nhưng có thể trigger từ FAB/menu nếu cần.
class DashboardPage extends StatelessWidget {
  const DashboardPage({
    super.key,
    this.userName = 'Minh An',
    // Tab navigation hooks (mới)
    this.onOpenChat,
    this.onOpenMedicineCabinet,
    this.onOpenSoulGarden,
    this.onOpenProfile,
    // Header / search hooks
    this.onShowMenu,
    this.onShowNotifications,
    this.onMic,
    this.onCamera,
    this.onSearchSubmit,
    // Card actions
    this.onSeeReminders,
    this.onSeeHealthSummary,
    this.onSuggestionTap,
    // Legacy (không dùng trực tiếp trong layout này — giữ để tương thích)
    this.mode,
    this.consultApi,
    this.onOpenMedicine,
    this.onOpenDoctorHub,
    this.onOpenAchievements,
    this.onOpenCommunity,
  });

  final String userName;

  final VoidCallback? onOpenChat;
  final VoidCallback? onOpenMedicineCabinet;
  final VoidCallback? onOpenSoulGarden;
  final VoidCallback? onOpenProfile;

  final VoidCallback? onShowMenu;
  final VoidCallback? onShowNotifications;
  final VoidCallback? onMic;
  final VoidCallback? onCamera;
  final ValueChanged<String>? onSearchSubmit;

  final VoidCallback? onSeeReminders;
  final VoidCallback? onSeeHealthSummary;
  final ValueChanged<String>? onSuggestionTap;

  // Legacy
  final ConsultMode? mode;
  final ConsultApi? consultApi;
  final VoidCallback? onOpenMedicine;
  final VoidCallback? onOpenDoctorHub;
  final VoidCallback? onOpenAchievements;
  final VoidCallback? onOpenCommunity;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: _kBg,
      body: SafeArea(
        bottom: false,
        child: Column(
          children: [
            _Header(
              onShowMenu: onShowMenu,
              onShowNotifications: onShowNotifications,
              onOpenProfile: onOpenProfile,
            ),
            Expanded(
              child: ListView(
                padding: const EdgeInsets.fromLTRB(16, 12, 16, 24),
                physics: const BouncingScrollPhysics(),
                children: [
                  _HeroCard(
                    userName: userName,
                    onOpenChat: onOpenChat,
                    onOpenProfile: onOpenProfile,
                  ),
                  const SizedBox(height: 14),
                  _SearchBar(
                    onSubmit: onSearchSubmit,
                    onMic: onMic,
                    onCamera: onCamera,
                  ),
                  const SizedBox(height: 14),
                  _QuickGrid(
                    onChat: onOpenChat,
                    onMedicine: onOpenMedicineCabinet,
                    onSoulGarden: onOpenSoulGarden,
                    onProfile: onOpenProfile,
                  ),
                  const SizedBox(height: 22),
                  _SectionHeader(
                    title: 'Chăm sóc hôm nay',
                    onSeeAll: onSeeReminders,
                  ),
                  const SizedBox(height: 10),
                  _ReminderCard(onTap: onSeeReminders),
                  const SizedBox(height: 10),
                  _HealthSummaryCard(onTap: onSeeHealthSummary),
                  const SizedBox(height: 22),
                  Padding(
                    padding: const EdgeInsets.only(left: 4),
                    child: Text(
                      'Gợi ý hữu ích',
                      style: const TextStyle(
                        fontFamily: 'Outfit',
                        fontSize: 15,
                        fontWeight: FontWeight.w600,
                        color: _kInk,
                      ),
                    ),
                  ),
                  const SizedBox(height: 10),
                  _SuggestionsRow(onTap: onSuggestionTap),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

// ───────────────────────── HEADER ─────────────────────────

class _Header extends StatelessWidget {
  const _Header({
    required this.onShowMenu,
    required this.onShowNotifications,
    required this.onOpenProfile,
  });

  final VoidCallback? onShowMenu;
  final VoidCallback? onShowNotifications;
  final VoidCallback? onOpenProfile;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(8, 4, 8, 8),
      child: Row(
        children: [
          _IconBtn(
            icon: Icons.menu_rounded,
            onTap: onShowMenu,
            tooltip: 'Mở menu',
          ),
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
                  children: [
                    Container(
                      width: 6,
                      height: 6,
                      decoration: const BoxDecoration(
                        color: _kSuccess,
                        shape: BoxShape.circle,
                      ),
                    ),
                    const SizedBox(width: 6),
                    const Text(
                      'Chăm sóc sức khỏe mỗi ngày',
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
          _IconBtn(
            icon: Icons.notifications_outlined,
            onTap: onShowNotifications,
            tooltip: 'Thông báo',
            badge: true,
          ),
          const SizedBox(width: 6),
          _AvatarBtn(onTap: onOpenProfile),
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
      child: const Icon(
        Icons.medical_services_rounded,
        color: Colors.white,
        size: 18,
      ),
    );
  }
}

class _IconBtn extends StatelessWidget {
  const _IconBtn({
    required this.icon,
    required this.onTap,
    this.tooltip,
    this.badge = false,
  });

  final IconData icon;
  final VoidCallback? onTap;
  final String? tooltip;
  final bool badge;

  @override
  Widget build(BuildContext context) {
    final btn = InkResponse(
      onTap: onTap,
      radius: 24,
      child: Container(
        width: 40,
        height: 40,
        decoration: BoxDecoration(
          border: Border.all(color: _kBorder),
          borderRadius: BorderRadius.circular(20),
          color: Colors.white,
        ),
        child: Stack(
          alignment: Alignment.center,
          children: [
            Icon(icon, size: 20, color: _kInkSoft),
            if (badge)
              Positioned(
                top: 8,
                right: 10,
                child: Container(
                  width: 8,
                  height: 8,
                  decoration: BoxDecoration(
                    color: _kDanger,
                    shape: BoxShape.circle,
                    border: Border.all(color: Colors.white, width: 1.5),
                  ),
                ),
              ),
          ],
        ),
      ),
    );
    return tooltip != null ? Tooltip(message: tooltip!, child: btn) : btn;
  }
}

class _AvatarBtn extends StatelessWidget {
  const _AvatarBtn({required this.onTap});
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    return InkResponse(
      onTap: onTap,
      radius: 24,
      child: Container(
        width: 40,
        height: 40,
        decoration: BoxDecoration(
          shape: BoxShape.circle,
          border: Border.all(color: _kBorder),
          color: _kBrandSofter,
        ),
        child: const Icon(Icons.person_outline, size: 20, color: _kInkSoft),
      ),
    );
  }
}

// ───────────────────────── HERO CARD ─────────────────────────

class _HeroCard extends StatelessWidget {
  const _HeroCard({
    required this.userName,
    required this.onOpenChat,
    required this.onOpenProfile,
  });

  final String userName;
  final VoidCallback? onOpenChat;
  final VoidCallback? onOpenProfile;

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [Color(0xFFE0F2FE), Color(0xFFDBEAFE)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(24),
        border: Border.all(color: Colors.white, width: 1.5),
      ),
      padding: const EdgeInsets.fromLTRB(16, 14, 16, 16),
      child: Stack(
        clipBehavior: Clip.none,
        children: [
          // Doctor 3D placeholder — circle gradient bên phải
          Positioned(
            right: -8,
            top: -4,
            bottom: -8,
            child: _DoctorPlaceholder(),
          ),
          Padding(
            padding: const EdgeInsets.only(right: 110),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _ChipBadge(
                  icon: Icons.shield_outlined,
                  text: 'An toàn · Dễ dùng',
                ),
                const SizedBox(height: 12),
                RichText(
                  text: TextSpan(
                    style: const TextStyle(
                      fontFamily: 'Outfit',
                      fontSize: 16,
                      fontWeight: FontWeight.w600,
                      color: _kInk,
                      height: 1.2,
                    ),
                    children: [
                      const TextSpan(text: 'Xin chào, '),
                      TextSpan(
                        text: userName,
                        style: const TextStyle(
                          color: _kBrand,
                          fontWeight: FontWeight.w800,
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 4),
                const Text(
                  'Bạn muốn được hỗ trợ\ngì hôm nay?',
                  style: TextStyle(
                    fontFamily: 'Outfit',
                    fontSize: 18,
                    fontWeight: FontWeight.w800,
                    color: _kInk,
                    height: 1.25,
                  ),
                ),
                const SizedBox(height: 14),
                _PrimaryCTA(
                  icon: Icons.chat_bubble_outline_rounded,
                  label: 'Hỏi Chat AI',
                  onTap: onOpenChat,
                ),
                const SizedBox(height: 8),
                _OutlineCTA(
                  icon: Icons.assignment_outlined,
                  label: 'Xem hồ sơ',
                  onTap: onOpenProfile,
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _DoctorPlaceholder extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Container(
      width: 130,
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [_kBrandSoft, _kBrandLight.withOpacity(0.55)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: const BorderRadius.only(
          topRight: Radius.circular(22),
          bottomRight: Radius.circular(22),
          topLeft: Radius.circular(60),
          bottomLeft: Radius.circular(60),
        ),
      ),
      child: const Center(
        child: Icon(
          Icons.health_and_safety_rounded,
          color: Colors.white,
          size: 56,
        ),
      ),
    );
  }
}

class _ChipBadge extends StatelessWidget {
  const _ChipBadge({required this.icon, required this.text});
  final IconData icon;
  final String text;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.85),
        borderRadius: BorderRadius.circular(999),
        border: Border.all(color: Colors.white),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 13, color: _kBrand),
          const SizedBox(width: 5),
          Text(
            text,
            style: const TextStyle(
              fontFamily: 'Outfit',
              fontSize: 11.5,
              fontWeight: FontWeight.w600,
              color: _kBrand,
            ),
          ),
        ],
      ),
    );
  }
}

class _PrimaryCTA extends StatelessWidget {
  const _PrimaryCTA({required this.icon, required this.label, this.onTap});
  final IconData icon;
  final String label;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    return Material(
      color: _kBrand,
      borderRadius: BorderRadius.circular(14),
      elevation: 0,
      child: InkWell(
        onTap: () {
          HapticFeedback.lightImpact();
          onTap?.call();
        },
        borderRadius: BorderRadius.circular(14),
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 11),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(icon, size: 18, color: Colors.white),
              const SizedBox(width: 8),
              const Text(
                'Hỏi Chat AI',
                style: TextStyle(
                  fontFamily: 'Outfit',
                  fontSize: 14,
                  fontWeight: FontWeight.w700,
                  color: Colors.white,
                ),
              ),
              const SizedBox(width: 8),
              const Icon(Icons.chevron_right_rounded,
                  size: 20, color: Colors.white),
            ],
          ),
        ),
      ),
    );
  }
}

class _OutlineCTA extends StatelessWidget {
  const _OutlineCTA({required this.icon, required this.label, this.onTap});
  final IconData icon;
  final String label;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    return Material(
      color: Colors.white,
      borderRadius: BorderRadius.circular(14),
      child: InkWell(
        onTap: () {
          HapticFeedback.lightImpact();
          onTap?.call();
        },
        borderRadius: BorderRadius.circular(14),
        child: Container(
          decoration: BoxDecoration(
            border: Border.all(color: _kBorder),
            borderRadius: BorderRadius.circular(14),
          ),
          padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(icon, size: 18, color: _kInkSoft),
              const SizedBox(width: 8),
              Text(
                label,
                style: const TextStyle(
                  fontFamily: 'Outfit',
                  fontSize: 14,
                  fontWeight: FontWeight.w600,
                  color: _kInk,
                ),
              ),
              const SizedBox(width: 8),
              const Icon(Icons.chevron_right_rounded,
                  size: 20, color: _kInkMuted),
            ],
          ),
        ),
      ),
    );
  }
}

// ───────────────────────── SEARCH BAR ─────────────────────────

class _SearchBar extends StatefulWidget {
  const _SearchBar({this.onSubmit, this.onMic, this.onCamera});
  final ValueChanged<String>? onSubmit;
  final VoidCallback? onMic;
  final VoidCallback? onCamera;

  @override
  State<_SearchBar> createState() => _SearchBarState();
}

class _SearchBarState extends State<_SearchBar> {
  final _controller = TextEditingController();

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: _kBorder),
      ),
      padding: const EdgeInsets.fromLTRB(12, 6, 6, 6),
      child: Row(
        children: [
          const Icon(Icons.auto_awesome_rounded, size: 18, color: _kBrand),
          const SizedBox(width: 8),
          Expanded(
            child: TextField(
              controller: _controller,
              onSubmitted: widget.onSubmit,
              style: const TextStyle(
                fontFamily: 'Outfit',
                fontSize: 13.5,
                color: _kInk,
              ),
              decoration: const InputDecoration(
                hintText: 'Nhập triệu chứng hoặc câu hỏi sức khỏe...',
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
          _SquareBtn(
            icon: Icons.mic_none_rounded,
            onTap: widget.onMic,
            tooltip: 'Hỏi bằng giọng nói',
          ),
          const SizedBox(width: 6),
          _SquareBtn(
            icon: Icons.camera_alt_outlined,
            onTap: widget.onCamera,
            tooltip: 'Chụp ảnh thuốc / triệu chứng',
          ),
        ],
      ),
    );
  }
}

class _SquareBtn extends StatelessWidget {
  const _SquareBtn({required this.icon, this.onTap, this.tooltip});
  final IconData icon;
  final VoidCallback? onTap;
  final String? tooltip;

  @override
  Widget build(BuildContext context) {
    final btn = Material(
      color: _kBrandSofter,
      borderRadius: BorderRadius.circular(10),
      child: InkWell(
        onTap: () {
          HapticFeedback.selectionClick();
          onTap?.call();
        },
        borderRadius: BorderRadius.circular(10),
        child: SizedBox(
          width: 36,
          height: 36,
          child: Icon(icon, size: 18, color: _kBrand),
        ),
      ),
    );
    return tooltip != null ? Tooltip(message: tooltip!, child: btn) : btn;
  }
}

// ───────────────────────── QUICK GRID 2x2 ─────────────────────────

class _QuickGrid extends StatelessWidget {
  const _QuickGrid({
    required this.onChat,
    required this.onMedicine,
    required this.onSoulGarden,
    required this.onProfile,
  });

  final VoidCallback? onChat;
  final VoidCallback? onMedicine;
  final VoidCallback? onSoulGarden;
  final VoidCallback? onProfile;

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Row(
          children: [
            Expanded(
              child: _QuickCard(
                icon: Icons.chat_bubble_outline_rounded,
                color: _kBrand,
                title: 'Chat AI',
                subtitle: 'Tư vấn nhanh',
                onTap: onChat,
              ),
            ),
            const SizedBox(width: 10),
            Expanded(
              child: _QuickCard(
                icon: Icons.medical_services_outlined,
                color: const Color(0xFF14B8A6),
                title: 'Tủ thuốc',
                subtitle: 'Quản lý thuốc',
                onTap: onMedicine,
              ),
            ),
          ],
        ),
        const SizedBox(height: 10),
        Row(
          children: [
            Expanded(
              child: _QuickCard(
                icon: Icons.spa_outlined,
                color: const Color(0xFF8B5CF6),
                title: 'Soul Garden',
                subtitle: 'Theo dõi cảm xúc',
                onTap: onSoulGarden,
              ),
            ),
            const SizedBox(width: 10),
            Expanded(
              child: _QuickCard(
                icon: Icons.person_outline_rounded,
                color: const Color(0xFFF59E0B),
                title: 'Hồ sơ',
                subtitle: 'Thông tin sức khỏe',
                onTap: onProfile,
              ),
            ),
          ],
        ),
      ],
    );
  }
}

class _QuickCard extends StatelessWidget {
  const _QuickCard({
    required this.icon,
    required this.color,
    required this.title,
    required this.subtitle,
    this.onTap,
  });

  final IconData icon;
  final Color color;
  final String title;
  final String subtitle;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    return Material(
      color: Colors.white,
      borderRadius: BorderRadius.circular(16),
      child: InkWell(
        onTap: () {
          HapticFeedback.selectionClick();
          onTap?.call();
        },
        borderRadius: BorderRadius.circular(16),
        child: Container(
          padding: const EdgeInsets.fromLTRB(12, 12, 8, 12),
          decoration: BoxDecoration(
            border: Border.all(color: _kBorder),
            borderRadius: BorderRadius.circular(16),
          ),
          child: Row(
            children: [
              Container(
                width: 40,
                height: 40,
                decoration: BoxDecoration(
                  color: color.withOpacity(0.12),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Icon(icon, size: 20, color: color),
              ),
              const SizedBox(width: 10),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Text(
                      title,
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
                      subtitle,
                      style: const TextStyle(
                        fontFamily: 'Outfit',
                        fontSize: 11,
                        color: _kInkSoft,
                        height: 1.2,
                      ),
                    ),
                  ],
                ),
              ),
              const Icon(Icons.chevron_right_rounded,
                  size: 18, color: _kInkMuted),
            ],
          ),
        ),
      ),
    );
  }
}

// ───────────────────────── SECTION HEADER ─────────────────────────

class _SectionHeader extends StatelessWidget {
  const _SectionHeader({required this.title, this.onSeeAll});
  final String title;
  final VoidCallback? onSeeAll;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 4),
      child: Row(
        children: [
          Expanded(
            child: Text(
              title,
              style: const TextStyle(
                fontFamily: 'Outfit',
                fontSize: 15,
                fontWeight: FontWeight.w700,
                color: _kInk,
              ),
            ),
          ),
          if (onSeeAll != null)
            InkWell(
              onTap: onSeeAll,
              borderRadius: BorderRadius.circular(8),
              child: Padding(
                padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 4),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: const [
                    Text(
                      'Xem tất cả',
                      style: TextStyle(
                        fontFamily: 'Outfit',
                        fontSize: 12.5,
                        fontWeight: FontWeight.w600,
                        color: _kBrand,
                      ),
                    ),
                    Icon(Icons.chevron_right_rounded,
                        size: 16, color: _kBrand),
                  ],
                ),
              ),
            ),
        ],
      ),
    );
  }
}

// ───────────────────────── REMINDER CARD ─────────────────────────

class _ReminderCard extends StatelessWidget {
  const _ReminderCard({this.onTap});
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    return Material(
      color: Colors.white,
      borderRadius: BorderRadius.circular(16),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(16),
        child: Container(
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            border: Border.all(color: _kBorder),
            borderRadius: BorderRadius.circular(16),
          ),
          child: Row(
            children: [
              Container(
                width: 38,
                height: 38,
                decoration: BoxDecoration(
                  color: _kBrandSofter,
                  borderRadius: BorderRadius.circular(12),
                ),
                child: const Icon(Icons.notifications_active_outlined,
                    size: 19, color: _kBrand),
              ),
              const SizedBox(width: 10),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: const [
                    Text(
                      'Nhắc uống thuốc',
                      style: TextStyle(
                        fontFamily: 'Outfit',
                        fontSize: 13.5,
                        fontWeight: FontWeight.w700,
                        color: _kInk,
                        height: 1.2,
                      ),
                    ),
                    SizedBox(height: 2),
                    Text(
                      'Đừng quên uống thuốc đúng giờ',
                      style: TextStyle(
                        fontFamily: 'Outfit',
                        fontSize: 11.5,
                        color: _kInkSoft,
                        height: 1.2,
                      ),
                    ),
                  ],
                ),
              ),
              const _TimeChip('08:00'),
              const SizedBox(width: 6),
              const _TimeChip('13:00'),
              const SizedBox(width: 4),
              const Icon(Icons.chevron_right_rounded,
                  size: 18, color: _kInkMuted),
            ],
          ),
        ),
      ),
    );
  }
}

class _TimeChip extends StatelessWidget {
  const _TimeChip(this.text);
  final String text;
  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: _kBrandSofter,
        borderRadius: BorderRadius.circular(8),
      ),
      child: Text(
        text,
        style: const TextStyle(
          fontFamily: 'Outfit',
          fontSize: 11,
          fontWeight: FontWeight.w600,
          color: _kBrand,
        ),
      ),
    );
  }
}

// ───────────────────────── HEALTH SUMMARY ─────────────────────────

class _HealthSummaryCard extends StatelessWidget {
  const _HealthSummaryCard({this.onTap});
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    return Material(
      color: Colors.white,
      borderRadius: BorderRadius.circular(16),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(16),
        child: Container(
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            border: Border.all(color: _kBorder),
            borderRadius: BorderRadius.circular(16),
          ),
          child: Row(
            children: [
              Container(
                width: 38,
                height: 38,
                decoration: BoxDecoration(
                  color: _kBrandSofter,
                  borderRadius: BorderRadius.circular(12),
                ),
                child: const Icon(Icons.monitor_heart_outlined,
                    size: 19, color: _kBrand),
              ),
              const SizedBox(width: 10),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: const [
                    Text(
                      'Tóm tắt sức khỏe',
                      style: TextStyle(
                        fontFamily: 'Outfit',
                        fontSize: 13.5,
                        fontWeight: FontWeight.w700,
                        color: _kInk,
                        height: 1.2,
                      ),
                    ),
                    SizedBox(height: 2),
                    Text(
                      'Cập nhật chỉ số mới nhất',
                      style: TextStyle(
                        fontFamily: 'Outfit',
                        fontSize: 11.5,
                        color: _kInkSoft,
                        height: 1.2,
                      ),
                    ),
                  ],
                ),
              ),
              const _MiniStat(label: 'Nhiệt độ', value: '37.8°C'),
              const SizedBox(width: 6),
              const _MiniStat(label: 'Nhịp tim', value: '78'),
              const SizedBox(width: 6),
              const _MiniStat(label: 'SpO₂', value: '98%'),
              const SizedBox(width: 4),
              const Icon(Icons.chevron_right_rounded,
                  size: 18, color: _kInkMuted),
            ],
          ),
        ),
      ),
    );
  }
}

class _MiniStat extends StatelessWidget {
  const _MiniStat({required this.label, required this.value});
  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        Text(
          label,
          style: const TextStyle(
            fontFamily: 'Outfit',
            fontSize: 9.5,
            color: _kInkSoft,
            height: 1.0,
          ),
        ),
        const SizedBox(height: 2),
        Text(
          value,
          style: const TextStyle(
            fontFamily: 'Outfit',
            fontSize: 11.5,
            fontWeight: FontWeight.w800,
            color: _kInk,
            height: 1.0,
          ),
        ),
      ],
    );
  }
}

// ───────────────────────── SUGGESTIONS ─────────────────────────

class _SuggestionsRow extends StatelessWidget {
  const _SuggestionsRow({this.onTap});
  final ValueChanged<String>? onTap;

  @override
  Widget build(BuildContext context) {
    final items = const [
      _SugItem('Viêm họng', Icons.sentiment_dissatisfied_rounded,
          Color(0xFF10B981), Color(0xFFD1FAE5)),
      _SugItem('Dinh dưỡng', Icons.local_dining_rounded, Color(0xFFEF4444),
          Color(0xFFFEE2E2)),
      _SugItem('Giấc ngủ', Icons.nightlight_round, Color(0xFF8B5CF6),
          Color(0xFFEDE9FE)),
    ];
    return Row(
      children: items
          .map((it) => Expanded(
                child: Padding(
                  padding: EdgeInsets.only(
                    right: it == items.last ? 0 : 8,
                  ),
                  child: _SuggestionPill(
                    label: it.label,
                    icon: it.icon,
                    iconColor: it.iconColor,
                    bg: it.bg,
                    onTap: () => onTap?.call(it.label),
                  ),
                ),
              ))
          .toList(),
    );
  }
}

class _SugItem {
  final String label;
  final IconData icon;
  final Color iconColor;
  final Color bg;
  const _SugItem(this.label, this.icon, this.iconColor, this.bg);
}

class _SuggestionPill extends StatelessWidget {
  const _SuggestionPill({
    required this.label,
    required this.icon,
    required this.iconColor,
    required this.bg,
    this.onTap,
  });

  final String label;
  final IconData icon;
  final Color iconColor;
  final Color bg;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    return Material(
      color: Colors.white,
      borderRadius: BorderRadius.circular(999),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(999),
        child: Container(
          padding: const EdgeInsets.fromLTRB(8, 6, 10, 6),
          decoration: BoxDecoration(
            border: Border.all(color: _kBorder),
            borderRadius: BorderRadius.circular(999),
          ),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Container(
                width: 26,
                height: 26,
                decoration:
                    BoxDecoration(color: bg, shape: BoxShape.circle),
                child: Icon(icon, size: 14, color: iconColor),
              ),
              const SizedBox(width: 6),
              Flexible(
                child: Text(
                  label,
                  overflow: TextOverflow.ellipsis,
                  style: const TextStyle(
                    fontFamily: 'Outfit',
                    fontSize: 12,
                    fontWeight: FontWeight.w600,
                    color: _kInk,
                  ),
                ),
              ),
              const SizedBox(width: 2),
              const Icon(Icons.chevron_right_rounded,
                  size: 14, color: _kInkMuted),
            ],
          ),
        ),
      ),
    );
  }
}
