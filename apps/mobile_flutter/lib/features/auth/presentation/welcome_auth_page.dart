import 'dart:ui';

import 'package:flutter/material.dart';

import 'auth_theme.dart';
import 'login_page.dart';
import 'register_page.dart';
import '../../../core/services/auth_service.dart';

/// Welcome screen — Apple-style glassmorphism.
/// Gradient background + floating orbs → frosted glass logo → title → CTAs.
class WelcomeAuthPage extends StatefulWidget {
  const WelcomeAuthPage({
    super.key,
    required this.onAuthComplete,
    required this.authService,
  });

  final VoidCallback onAuthComplete;
  /// The single [AuthService] instance owned by [MediSignApp].
  /// Passed down so Login/Register pages mutate the same token store.
  final AuthService authService;

  @override
  State<WelcomeAuthPage> createState() => _WelcomeAuthPageState();
}

class _WelcomeAuthPageState extends State<WelcomeAuthPage>
    with SingleTickerProviderStateMixin {
  late AnimationController _pulseCtrl;
  late Animation<double> _pulseAnim;

  @override
  void initState() {
    super.initState();
    _pulseCtrl = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 2400),
    )..repeat(reverse: true);
    _pulseAnim = Tween<double>(begin: 0.9, end: 1.08).animate(
      CurvedAnimation(parent: _pulseCtrl, curve: Curves.easeInOut),
    );
  }

  @override
  void dispose() {
    _pulseCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: AuthTheme.gradientBackground(
        child: SafeArea(
          child: LayoutBuilder(
            builder: (context, constraints) {
              return SingleChildScrollView(
                padding: const EdgeInsets.fromLTRB(28, 40, 28, 28),
                child: ConstrainedBox(
                  constraints: BoxConstraints(minHeight: constraints.maxHeight - 80),
                  child: IntrinsicHeight(
                    child: Column(
                      children: [
                        const Spacer(flex: 2),

                        // ── Glass logo with pulse animation ──
                        AnimatedBuilder(
                          animation: _pulseAnim,
                          builder: (_, __) => Transform.scale(
                            scale: _pulseAnim.value,
                            child: _buildGlassLogo(),
                          ),
                        ),
                        const SizedBox(height: 40),

                        // ── Title ──
                        const Text(
                          'MediSign AI',
                          textAlign: TextAlign.center,
                          style: AuthTheme.h1,
                        ),
                        const SizedBox(height: 8),

                        // ── Subtitle ──
                        const Padding(
                          padding: EdgeInsets.symmetric(horizontal: 12),
                          child: Text(
                            'Chào mừng bạn đến với MediSign AI. Hãy tạo tài khoản để bắt đầu hành trình chăm sóc sức khỏe thông minh.',
                            textAlign: TextAlign.center,
                            style: AuthTheme.subtitle,
                          ),
                        ),

                        const Spacer(flex: 3),

                        // ── Create Account CTA ──
                        AuthTheme.primaryButton(
                          text: 'Tạo tài khoản mới',
                          icon: Icons.person_add_alt_1_outlined,
                          onPressed: () => _navigateTo(
                            context,
                            RegisterPage(
                              authService: widget.authService,
                              onAuthComplete: () {
                                Navigator.of(context).popUntil((route) => route.isFirst);
                                widget.onAuthComplete();
                              },
                            ),
                          ),
                        ),
                        const SizedBox(height: 16),

                        // ── "hoặc" divider ──
                        AuthTheme.orDivider(),
                        const SizedBox(height: 16),

                        // ── Login outline button ──
                        AuthTheme.outlineButton(
                          text: 'Đăng nhập',
                          icon: Icons.login_rounded,
                          onPressed: () => _navigateTo(
                            context,
                            LoginPage(
                              authService: widget.authService,
                              onAuthComplete: () {
                                Navigator.of(context).popUntil((route) => route.isFirst);
                                widget.onAuthComplete();
                              },
                            ),
                          ),
                        ),
                        const SizedBox(height: 28),

                        // ── Footer badges ──
                        AuthTheme.footerBadges(),
                      ],
                    ),
                  ),
                ),
              );
            },
          ),
        ),
      ),
    );
  }

  Widget _buildGlassLogo() {
    return ClipOval(
      child: BackdropFilter(
        filter: ImageFilter.blur(sigmaX: 20, sigmaY: 20),
        child: Container(
          width: 130,
          height: 130,
          decoration: BoxDecoration(
            shape: BoxShape.circle,
            color: AuthTheme.glassFillLight,
            border: Border.all(color: AuthTheme.glassBorderStrong, width: 1.5),
            boxShadow: [
              BoxShadow(
                color: AuthTheme.primary.withOpacity(0.25),
                blurRadius: 40,
                spreadRadius: 5,
              ),
            ],
          ),
          child: const Center(
            child: Icon(
              Icons.medical_services_outlined,
              size: 56,
              color: AuthTheme.primaryLight,
            ),
          ),
        ),
      ),
    );
  }

  void _navigateTo(BuildContext context, Widget page) {
    Navigator.of(context).push(
      PageRouteBuilder(
        pageBuilder: (_, __, ___) => page,
        transitionsBuilder: (_, animation, __, child) {
          return FadeTransition(
            opacity: CurvedAnimation(
              parent: animation,
              curve: Curves.easeOut,
            ),
            child: SlideTransition(
              position: Tween<Offset>(
                begin: const Offset(0.05, 0),
                end: Offset.zero,
              ).animate(CurvedAnimation(
                parent: animation,
                curve: Curves.easeOutCubic,
              )),
              child: child,
            ),
          );
        },
        transitionDuration: const Duration(milliseconds: 400),
      ),
    );
  }
}
