import 'dart:ui';

import 'package:flutter/material.dart';

import 'auth_theme.dart';

/// Security verification page — Apple-style glassmorphism.
/// Gradient bg → glass shield → 3 glass method cards → glass CTAs.
class VerifySecurityPage extends StatefulWidget {
  const VerifySecurityPage({super.key, required this.onAuthComplete});

  final VoidCallback onAuthComplete;

  @override
  State<VerifySecurityPage> createState() => _VerifySecurityPageState();
}

class _VerifySecurityPageState extends State<VerifySecurityPage> {
  int _selectedIndex = 0; // 0: biometrics, 1: authenticator, 2: recovery
  bool _isActivating = false;

  void _activate() {
    setState(() => _isActivating = true);
    Future.delayed(const Duration(milliseconds: 800), () {
      if (!mounted) return;
      widget.onAuthComplete();
    });
  }

  void _skip() {
    widget.onAuthComplete();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: AuthTheme.gradientBackground(
        child: SafeArea(
          child: Padding(
            padding: const EdgeInsets.fromLTRB(24, 16, 24, 24),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // ── Back button ──
                AuthTheme.backButton(context),
                const SizedBox(height: 20),

                // ── Glass shield icon ──
                _buildGlassIcon(
                  icon: Icons.verified_user_rounded,
                  color: AuthTheme.primaryLight,
                ),
                const SizedBox(height: 20),

                // ── Title ──
                const Text('Xác thực 2 bước', style: AuthTheme.h2),
                const SizedBox(height: 6),
                const Text(
                  'Chọn phương thức xác thực để bảo vệ tài khoản',
                  style: AuthTheme.subtitle,
                ),
                const SizedBox(height: 6),

                // ── Optional badge — glass styled ──
                ClipRRect(
                  borderRadius: BorderRadius.circular(8),
                  child: BackdropFilter(
                    filter: ImageFilter.blur(sigmaX: 8, sigmaY: 8),
                    child: Container(
                      padding: const EdgeInsets.symmetric(
                          horizontal: 10, vertical: 4),
                      decoration: BoxDecoration(
                        color: const Color(0xFFF59E0B).withOpacity(0.15),
                        borderRadius: BorderRadius.circular(8),
                        border: Border.all(
                          color: const Color(0xFFF59E0B).withOpacity(0.3),
                          width: 1,
                        ),
                      ),
                      child: const Text(
                        'Không bắt buộc — có thể bỏ qua',
                        style: TextStyle(
                          fontFamily: AuthTheme.fontFamily,
                          fontSize: 11,
                          fontWeight: FontWeight.w600,
                          color: Color(0xFFFCD34D),
                        ),
                      ),
                    ),
                  ),
                ),
                const SizedBox(height: 24),

                // ── Glass method cards ──
                _buildMethodCard(
                  index: 0,
                  icon: Icons.fingerprint,
                  iconColor: AuthTheme.primaryLight,
                  title: 'Sinh trắc học',
                  subtitle: 'Vân tay hoặc khuôn mặt',
                ),
                const SizedBox(height: 10),
                _buildMethodCard(
                  index: 1,
                  icon: Icons.vpn_key_outlined,
                  iconColor: const Color(0xFFD8B4FE),
                  title: 'Authenticator 2FA',
                  subtitle: 'Google / Microsoft Authenticator',
                ),
                const SizedBox(height: 10),
                _buildMethodCard(
                  index: 2,
                  icon: Icons.key_outlined,
                  iconColor: const Color(0xFFFCD34D),
                  title: 'Recovery Key',
                  subtitle: 'Nhập cụm từ khôi phục',
                ),

                const Spacer(),

                // ── Activate CTA ──
                AuthTheme.primaryButton(
                  text: 'Xác nhận',
                  onPressed: _activate,
                  isLoading: _isActivating,
                ),
                const SizedBox(height: 12),

                // ── Skip button ──
                AuthTheme.outlineButton(
                  text: 'Bỏ qua, thiết lập sau',
                  icon: Icons.arrow_forward_rounded,
                  onPressed: _skip,
                ),
                const SizedBox(height: 12),

                // ── Hint ──
                const Center(
                  child: Text(
                    'Bạn có thể bật bất cứ lúc nào trong Cài đặt > Bảo mật',
                    textAlign: TextAlign.center,
                    style: AuthTheme.caption,
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  /// Glass icon container
  Widget _buildGlassIcon({
    required IconData icon,
    required Color color,
  }) {
    return ClipRRect(
      borderRadius: BorderRadius.circular(16),
      child: BackdropFilter(
        filter: ImageFilter.blur(sigmaX: 16, sigmaY: 16),
        child: Container(
          width: 56,
          height: 56,
          decoration: BoxDecoration(
            color: AuthTheme.glassFillLight,
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: AuthTheme.glassBorder, width: 1),
          ),
          child: Icon(icon, size: 28, color: color),
        ),
      ),
    );
  }

  /// Frosted glass method card with colored icon
  Widget _buildMethodCard({
    required int index,
    required IconData icon,
    required Color iconColor,
    required String title,
    required String subtitle,
  }) {
    final isActive = _selectedIndex == index;
    return GestureDetector(
      onTap: () => setState(() => _selectedIndex = index),
      child: AuthTheme.glassCard(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 16),
        borderRadius: 16,
        isActive: isActive,
        child: Row(
          children: [
            AnimatedContainer(
              duration: const Duration(milliseconds: 200),
              width: 48,
              height: 48,
              decoration: BoxDecoration(
                color: isActive
                    ? iconColor.withOpacity(0.2)
                    : Colors.white.withOpacity(0.06),
                borderRadius: BorderRadius.circular(14),
              ),
              child: Icon(
                icon,
                size: 24,
                color: isActive ? iconColor : AuthTheme.textOnGlassMuted,
              ),
            ),
            const SizedBox(width: 14),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: const TextStyle(
                      fontFamily: AuthTheme.fontFamily,
                      fontSize: 15,
                      fontWeight: FontWeight.w600,
                      color: AuthTheme.textOnGlass,
                    ),
                  ),
                  const SizedBox(height: 2),
                  Text(subtitle, style: AuthTheme.caption),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
