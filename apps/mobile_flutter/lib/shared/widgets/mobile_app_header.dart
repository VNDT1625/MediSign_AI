import 'package:flutter/material.dart';

/// Header dùng chung cho các tab chính của Mobile App.
///
/// Theo screenshot mẫu (UI_Mau/mobile/home.png):
///   • Hamburger trái (mở drawer / menu phụ)
///   • Logo shield+plus + "MediSign AI" + tagline "Chăm sóc sức khoẻ mỗi ngày"
///   • Bell có badge thông báo
///   • Avatar tròn (KHÔNG có tên — khác desktop)
///
/// Khác với desktop header ở chỗ: không hiển thị tên user, không có pill nav giữa
/// (mobile dùng [MobileBottomNav] ở đáy).
class MobileAppHeader extends StatelessWidget implements PreferredSizeWidget {
  const MobileAppHeader({
    super.key,
    this.onMenuPressed,
    this.onNotificationPressed,
    this.onAvatarPressed,
    this.notificationCount = 0,
    this.avatarUrl,
  });

  final VoidCallback? onMenuPressed;
  final VoidCallback? onNotificationPressed;
  final VoidCallback? onAvatarPressed;
  final int notificationCount;
  final String? avatarUrl;

  static const double _height = 64;

  // Brand colors — đồng bộ với web (web_next/tailwind.config.ts: brand=#0284C7)
  static const Color _brand = Color(0xFF0284C7);
  static const Color _brandDark = Color(0xFF0369A1);
  static const Color _accent = Color(0xFFF97316);
  static const Color _success = Color(0xFF22C55E);
  static const Color _ink900 = Color(0xFF0F172A);
  static const Color _ink500 = Color(0xFF64748B);
  static const Color _ink200 = Color(0xFFE2E8F0);

  @override
  Size get preferredSize => const Size.fromHeight(_height);

  @override
  Widget build(BuildContext context) {
    return Material(
      color: Colors.white,
      elevation: 0,
      child: SafeArea(
        bottom: false,
        child: SizedBox(
          height: _height,
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 12),
            child: Row(
              children: [
                // ── Hamburger ──
                _IconButton(
                  semanticsLabel: 'Mở menu',
                  icon: const _MenuIcon(),
                  onTap: onMenuPressed,
                ),
                const SizedBox(width: 4),

                // ── Logo + tagline ──
                Expanded(
                  child: Row(
                    children: [
                      Container(
                        width: 36,
                        height: 36,
                        decoration: BoxDecoration(
                          gradient: const LinearGradient(
                            begin: Alignment.topLeft,
                            end: Alignment.bottomRight,
                            colors: [_brand, _brandDark],
                          ),
                          borderRadius: BorderRadius.circular(10),
                          boxShadow: [
                            BoxShadow(
                              color: _brand.withOpacity(0.25),
                              blurRadius: 8,
                              offset: const Offset(0, 2),
                            ),
                          ],
                        ),
                        child: const _ShieldPlusIcon(size: 20),
                      ),
                      const SizedBox(width: 10),
                      Expanded(
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            RichText(
                              maxLines: 1,
                              overflow: TextOverflow.ellipsis,
                              text: const TextSpan(
                                style: TextStyle(
                                  fontSize: 17,
                                  fontWeight: FontWeight.w800,
                                  color: _ink900,
                                  letterSpacing: -0.2,
                                  height: 1.1,
                                ),
                                children: [
                                  TextSpan(text: 'MediSign '),
                                  TextSpan(
                                    text: 'AI',
                                    style: TextStyle(color: _brand),
                                  ),
                                ],
                              ),
                            ),
                            const SizedBox(height: 2),
                            Row(
                              children: const [
                                _Dot(color: _success, size: 6),
                                SizedBox(width: 4),
                                Flexible(
                                  child: Text(
                                    'Chăm sóc sức khoẻ mỗi ngày',
                                    maxLines: 1,
                                    overflow: TextOverflow.ellipsis,
                                    style: TextStyle(
                                      fontSize: 11,
                                      fontWeight: FontWeight.w500,
                                      color: _ink500,
                                      height: 1.1,
                                    ),
                                  ),
                                ),
                              ],
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),

                // ── Bell ──
                _IconButton(
                  semanticsLabel: notificationCount > 0
                      ? 'Thông báo, $notificationCount chưa đọc'
                      : 'Thông báo',
                  icon: Stack(
                    clipBehavior: Clip.none,
                    children: [
                      const _BellIcon(),
                      if (notificationCount > 0)
                        Positioned(
                          right: -2,
                          top: -2,
                          child: Container(
                            constraints: const BoxConstraints(
                              minWidth: 14,
                              minHeight: 14,
                            ),
                            padding: const EdgeInsets.symmetric(horizontal: 3),
                            decoration: BoxDecoration(
                              color: _accent,
                              borderRadius: BorderRadius.circular(7),
                              border: Border.all(
                                color: Colors.white,
                                width: 1.5,
                              ),
                            ),
                            child: Center(
                              child: Text(
                                notificationCount > 9
                                    ? '9+'
                                    : '$notificationCount',
                                style: const TextStyle(
                                  fontSize: 9,
                                  fontWeight: FontWeight.w700,
                                  color: Colors.white,
                                  height: 1.1,
                                ),
                              ),
                            ),
                          ),
                        ),
                    ],
                  ),
                  onTap: onNotificationPressed,
                ),
                const SizedBox(width: 4),

                // ── Avatar (chỉ hình tròn, không tên) ──
                Semantics(
                  label: 'Hồ sơ của tôi',
                  button: true,
                  child: InkWell(
                    onTap: onAvatarPressed,
                    customBorder: const CircleBorder(),
                    child: Container(
                      width: 40,
                      height: 40,
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        border: Border.all(color: _ink200, width: 1),
                        image: avatarUrl != null
                            ? DecorationImage(
                                image: NetworkImage(avatarUrl!),
                                fit: BoxFit.cover,
                              )
                            : null,
                      ),
                      child: avatarUrl == null
                          ? const Icon(
                              Icons.person_outline_rounded,
                              size: 22,
                              color: _ink500,
                            )
                          : null,
                    ),
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

/* ────────────────── Helpers ────────────────── */

class _IconButton extends StatelessWidget {
  const _IconButton({
    required this.icon,
    required this.semanticsLabel,
    this.onTap,
  });

  final Widget icon;
  final String semanticsLabel;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    return Semantics(
      label: semanticsLabel,
      button: true,
      child: InkWell(
        onTap: onTap,
        customBorder: const CircleBorder(),
        child: SizedBox(
          width: 44, // WCAG touch target
          height: 44,
          child: Center(child: icon),
        ),
      ),
    );
  }
}

class _Dot extends StatelessWidget {
  const _Dot({required this.color, this.size = 6});
  final Color color;
  final double size;
  @override
  Widget build(BuildContext context) => Container(
        width: size,
        height: size,
        decoration: BoxDecoration(color: color, shape: BoxShape.circle),
      );
}

/* ────────────────── Icons ────────────────── */

class _MenuIcon extends StatelessWidget {
  const _MenuIcon();
  @override
  Widget build(BuildContext context) => const Icon(
        Icons.menu_rounded,
        size: 24,
        color: MobileAppHeader._ink900,
      );
}

class _BellIcon extends StatelessWidget {
  const _BellIcon();
  @override
  Widget build(BuildContext context) => const Icon(
        Icons.notifications_none_rounded,
        size: 24,
        color: MobileAppHeader._ink500,
      );
}

class _ShieldPlusIcon extends StatelessWidget {
  const _ShieldPlusIcon({this.size = 20});
  final double size;
  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: size,
      height: size,
      child: CustomPaint(painter: _ShieldPlusPainter()),
    );
  }
}

class _ShieldPlusPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final w = size.width;
    final h = size.height;

    // Shield path
    final shield = Path()
      ..moveTo(w * 0.5, h * 0.12)
      ..lineTo(w * 0.85, h * 0.27)
      ..lineTo(w * 0.85, h * 0.55)
      ..cubicTo(w * 0.85, h * 0.78, w * 0.7, h * 0.92, w * 0.5, h)
      ..cubicTo(w * 0.3, h * 0.92, w * 0.15, h * 0.78, w * 0.15, h * 0.55)
      ..lineTo(w * 0.15, h * 0.27)
      ..close();

    final fill = Paint()..color = const Color(0x33FFFFFF);
    canvas.drawPath(shield, fill);

    // Plus
    final plus = Paint()
      ..color = Colors.white
      ..strokeWidth = w * 0.12
      ..strokeCap = StrokeCap.round;

    canvas.drawLine(
      Offset(w * 0.5, h * 0.36),
      Offset(w * 0.5, h * 0.7),
      plus,
    );
    canvas.drawLine(
      Offset(w * 0.32, h * 0.53),
      Offset(w * 0.68, h * 0.53),
      plus,
    );
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}
