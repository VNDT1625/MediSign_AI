import 'dart:ui';

import 'package:flutter/material.dart';

import 'auth_theme.dart';
import 'register_page.dart';
import '../../../core/validators/auth_validators.dart';
import '../../../core/services/auth_service.dart';

/// Login page — Apple-style glassmorphism.
/// Gradient bg → glass form card → frosted inputs → glass CTA.
class LoginPage extends StatefulWidget {
  const LoginPage({super.key, required this.onAuthComplete});

  final VoidCallback onAuthComplete;

  @override
  State<LoginPage> createState() => _LoginPageState();
}

enum _LoginMethod { email, phone }

class _LoginPageState extends State<LoginPage> {
  final _emailCtrl = TextEditingController();
  final _phoneCtrl = TextEditingController();
  final _passCtrl = TextEditingController();
  bool _obscurePass = true;
  bool _isLoading = false;
  _LoginMethod _method = _LoginMethod.email;

  // Validation
  String? _identifierError;
  String? _passwordError;

  @override
  void dispose() {
    _emailCtrl.dispose();
    _phoneCtrl.dispose();
    _passCtrl.dispose();
    super.dispose();
  }

  bool _validate() {
    bool isValid = true;

    setState(() {
      // Validate identifier (email or phone)
      final identifier = _method == _LoginMethod.email
          ? _emailCtrl.text.trim()
          : _phoneCtrl.text.trim();

      if (_method == _LoginMethod.email) {
        _identifierError = AuthValidators.validateEmail(identifier);
      } else {
        _identifierError = AuthValidators.validatePhone(identifier);
      }

      // Validate password
      if (_passCtrl.text.isEmpty) {
        _passwordError = 'Vui lòng nhập mật khẩu';
      } else {
        _passwordError = null;
      }

      if (_identifierError != null || _passwordError != null) {
        isValid = false;
      }
    });

    return isValid;
  }

  Future<void> _onLogin() async {
    if (!_validate()) return;

    setState(() => _isLoading = true);

    final identifier = _method == _LoginMethod.email
        ? _emailCtrl.text.trim()
        : _phoneCtrl.text.trim();

    // Use AuthService
    final authService = AuthService();
    final result = await authService.login(
      identifier: identifier,
      password: _passCtrl.text,
    );

    if (!mounted) return;

    setState(() => _isLoading = false);

    if (result.success) {
      widget.onAuthComplete();
    } else {
      // Show error
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(result.message ?? 'Đăng nhập thất bại'),
          backgroundColor: Colors.red.shade600,
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: AuthTheme.gradientBackground(
        child: SafeArea(
          child: SingleChildScrollView(
            padding: const EdgeInsets.fromLTRB(24, 16, 24, 28),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // ── Back button ──
                AuthTheme.backButton(context),
                const SizedBox(height: 24),

                // ── Title ──
                const Text('Đăng nhập', style: AuthTheme.h2),
                const SizedBox(height: 6),
                Text(
                  'Chào mừng bạn quay lại MediSign AI',
                  style: AuthTheme.subtitle.copyWith(
                    color: AuthTheme.primaryLight,
                  ),
                ),
                const SizedBox(height: 28),

                // ── Glass form card ──
                AuthTheme.glassCard(
                  padding: const EdgeInsets.all(24),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      // ── Email / Phone toggle ──
                      _buildMethodToggle(),
                      const SizedBox(height: 24),

                      // ── Input fields ──
                      if (_method == _LoginMethod.email) ...[
                        const Text('Email', style: AuthTheme.label),
                        const SizedBox(height: 8),
                        AuthTheme.inputField(
                          controller: _emailCtrl,
                          hint: 'email@example.com',
                          prefixIcon: Icons.email_outlined,
                          keyboardType: TextInputType.emailAddress,
                          textInputAction: TextInputAction.next,
                          errorText: _identifierError,
                          onChanged: (_) {
                            if (_identifierError != null) {
                              setState(() => _identifierError = null);
                            }
                          },
                        ),
                      ] else ...[
                        const Text('Số điện thoại', style: AuthTheme.label),
                        const SizedBox(height: 8),
                        AuthTheme.inputField(
                          controller: _phoneCtrl,
                          hint: '0912 345 678',
                          prefixIcon: Icons.phone_outlined,
                          keyboardType: TextInputType.phone,
                          textInputAction: TextInputAction.next,
                          errorText: _identifierError,
                          onChanged: (_) {
                            if (_identifierError != null) {
                              setState(() => _identifierError = null);
                            }
                          },
                        ),
                      ],
                      const SizedBox(height: 18),

                      const Text('Mật khẩu', style: AuthTheme.label),
                      const SizedBox(height: 8),
                      AuthTheme.inputField(
                        controller: _passCtrl,
                        hint: 'Ít nhất 8 ký tự',
                        obscure: _obscurePass,
                        textInputAction: TextInputAction.done,
                        errorText: _passwordError,
                        onChanged: (_) {
                          if (_passwordError != null) {
                            setState(() => _passwordError = null);
                          }
                        },
                        suffix: GestureDetector(
                          onTap: () =>
                              setState(() => _obscurePass = !_obscurePass),
                          child: Icon(
                            _obscurePass
                                ? Icons.visibility_off_outlined
                                : Icons.visibility_outlined,
                            color: AuthTheme.textOnGlassMuted,
                            size: 20,
                          ),
                        ),
                      ),
                      const SizedBox(height: 12),

                      // ── Forgot password ──
                      Align(
                        alignment: Alignment.centerRight,
                        child: GestureDetector(
                          onTap: () {},
                          child: Text(
                            'Quên mật khẩu?',
                            style: AuthTheme.link.copyWith(fontSize: 14),
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 32),

                // ── Login CTA ──
                AuthTheme.primaryButton(
                  text: 'Đăng nhập',
                  onPressed: _onLogin,
                  isLoading: _isLoading,
                ),
                const SizedBox(height: 24),

                // ── Footer link ──
                Center(
                  child: GestureDetector(
                    onTap: () {
                      Navigator.of(context).pushReplacement(
                        MaterialPageRoute(
                          builder: (_) => RegisterPage(
                              onAuthComplete: widget.onAuthComplete),
                        ),
                      );
                    },
                    child: const Text.rich(
                      TextSpan(
                        style: AuthTheme.subtitle,
                        children: [
                          TextSpan(text: 'Chưa có tài khoản? '),
                          TextSpan(text: 'Đăng ký', style: AuthTheme.link),
                        ],
                      ),
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

  /// Email / Phone pill toggle — frosted glass
  Widget _buildMethodToggle() {
    return ClipRRect(
      borderRadius: BorderRadius.circular(25),
      child: BackdropFilter(
        filter: ImageFilter.blur(sigmaX: 10, sigmaY: 10),
        child: Container(
          height: 50,
          decoration: BoxDecoration(
            color: AuthTheme.glassInputFill,
            borderRadius: BorderRadius.circular(25),
            border: Border.all(color: AuthTheme.glassBorder, width: 1),
          ),
          padding: const EdgeInsets.all(4),
          child: Row(
            children: [
              _toggleTab(
                label: 'Email',
                icon: Icons.email_outlined,
                isActive: _method == _LoginMethod.email,
                onTap: () => setState(() => _method = _LoginMethod.email),
              ),
              _toggleTab(
                label: 'Số điện thoại',
                icon: Icons.phone_outlined,
                isActive: _method == _LoginMethod.phone,
                onTap: () => setState(() => _method = _LoginMethod.phone),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _toggleTab({
    required String label,
    required IconData icon,
    required bool isActive,
    required VoidCallback onTap,
  }) {
    return Expanded(
      child: GestureDetector(
        onTap: onTap,
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 200),
          curve: Curves.easeOut,
          height: double.infinity,
          decoration: BoxDecoration(
            color: isActive
                ? Colors.white.withValues(alpha: 0.18)
                : Colors.transparent,
            borderRadius: BorderRadius.circular(22),
          ),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(
                icon,
                size: 17,
                color: isActive
                    ? AuthTheme.textOnGlass
                    : AuthTheme.textOnGlassMuted,
              ),
              const SizedBox(width: 6),
              Text(
                label,
                style: TextStyle(
                  fontFamily: AuthTheme.fontFamily,
                  fontSize: 14,
                  fontWeight: isActive ? FontWeight.w600 : FontWeight.w400,
                  color: isActive
                      ? AuthTheme.textOnGlass
                      : AuthTheme.textOnGlassMuted,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
