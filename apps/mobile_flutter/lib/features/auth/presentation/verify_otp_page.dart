import 'dart:async';
import 'dart:ui';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import 'auth_theme.dart';
import 'verify_security_page.dart';

/// OTP Verification page — Apple-style glassmorphism.
/// Gradient bg → glass shield → glass method cards → frosted OTP boxes → CTA.
class VerifyOtpPage extends StatefulWidget {
  const VerifyOtpPage({
    super.key,
    required this.email,
    required this.onAuthComplete,
  });

  final String email;
  final VoidCallback onAuthComplete;

  @override
  State<VerifyOtpPage> createState() => _VerifyOtpPageState();
}

enum _OtpMethod { email, sms }

class _VerifyOtpPageState extends State<VerifyOtpPage> {
  _OtpMethod _method = _OtpMethod.email;
  final List<TextEditingController> _controllers =
      List.generate(6, (_) => TextEditingController());
  final List<FocusNode> _focusNodes = List.generate(6, (_) => FocusNode());
  bool _isVerifying = false;
  int _countdown = 60;
  Timer? _timer;

  @override
  void initState() {
    super.initState();
    _startCountdown();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _focusNodes[0].requestFocus();
    });
  }

  void _startCountdown() {
    _countdown = 60;
    _timer?.cancel();
    _timer = Timer.periodic(const Duration(seconds: 1), (t) {
      if (_countdown <= 0) {
        t.cancel();
      } else {
        setState(() => _countdown--);
      }
    });
  }

  @override
  void dispose() {
    _timer?.cancel();
    for (final c in _controllers) {
      c.dispose();
    }
    for (final f in _focusNodes) {
      f.dispose();
    }
    super.dispose();
  }

  void _onOtpChanged(String value, int index) {
    if (value.length == 1 && index < 5) {
      _focusNodes[index + 1].requestFocus();
    } else if (value.isEmpty && index > 0) {
      _focusNodes[index - 1].requestFocus();
    }
    if (_controllers.every((c) => c.text.isNotEmpty)) {
      _verify();
    }
  }

  void _verify() {
    setState(() => _isVerifying = true);
    Future.delayed(const Duration(milliseconds: 800), () {
      if (!mounted) return;
      setState(() => _isVerifying = false);
      Navigator.of(context).pushReplacement(
        MaterialPageRoute(
          builder: (_) =>
              VerifySecurityPage(onAuthComplete: widget.onAuthComplete),
        ),
      );
    });
  }

  void _resendOtp() {
    if (_countdown > 0) return;
    _startCountdown();
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(
          _method == _OtpMethod.email
              ? 'Đã gửi lại mã qua Email'
              : 'Đã gửi lại mã qua SMS',
          style: const TextStyle(fontFamily: AuthTheme.fontFamily),
        ),
        backgroundColor: AuthTheme.primary,
        behavior: SnackBarBehavior.floating,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      ),
    );
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
                const SizedBox(height: 24),

                // ── Glass method cards ──
                _buildMethodCard(
                  method: _OtpMethod.email,
                  icon: Icons.email_outlined,
                  title: 'Mã OTP qua Email',
                  subtitle: 'Gửi mã xác thực qua hộp thư của bạn',
                ),
                const SizedBox(height: 10),
                _buildMethodCard(
                  method: _OtpMethod.sms,
                  icon: Icons.sms_outlined,
                  title: 'Mã OTP qua SMS',
                  subtitle: 'Gửi mã 6 số qua tin nhắn',
                ),
                const SizedBox(height: 24),

                // ── OTP input heading ──
                const Text('Nhập mã OTP', style: AuthTheme.label),
                const SizedBox(height: 10),

                // ── 6 glass OTP boxes ──
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: List.generate(6, (i) => _buildOtpBox(i)),
                ),
                const SizedBox(height: 14),

                // ── Timer / Resend ──
                Center(
                  child: GestureDetector(
                    onTap: _resendOtp,
                    child: Text(
                      _countdown > 0
                          ? 'Gửi lại mã sau ${_countdown}s'
                          : 'Gửi lại mã',
                      style: TextStyle(
                        fontFamily: AuthTheme.fontFamily,
                        fontSize: 13,
                        color: _countdown > 0
                            ? AuthTheme.textOnGlassMuted
                            : AuthTheme.primaryLight,
                        fontWeight: _countdown > 0
                            ? FontWeight.normal
                            : FontWeight.w600,
                      ),
                    ),
                  ),
                ),

                const Spacer(),

                // ── Verify CTA ──
                AuthTheme.primaryButton(
                  text: 'Xác nhận',
                  onPressed: _verify,
                  isLoading: _isVerifying,
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

  /// Frosted glass method selection card
  Widget _buildMethodCard({
    required _OtpMethod method,
    required IconData icon,
    required String title,
    required String subtitle,
  }) {
    final isActive = _method == method;
    return GestureDetector(
      onTap: () => setState(() => _method = method),
      child: AuthTheme.glassCard(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 16),
        borderRadius: 16,
        isActive: isActive,
        child: Row(
          children: [
            Container(
              width: 44,
              height: 44,
              decoration: BoxDecoration(
                color: isActive
                    ? AuthTheme.primary.withOpacity(0.2)
                    : Colors.white.withOpacity(0.06),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Icon(
                icon,
                size: 22,
                color: isActive
                    ? AuthTheme.primaryLight
                    : AuthTheme.textOnGlassMuted,
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
            // Glass radio indicator
            AnimatedContainer(
              duration: const Duration(milliseconds: 200),
              width: 22,
              height: 22,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                border: Border.all(
                  color: isActive
                      ? AuthTheme.primaryLight
                      : AuthTheme.glassBorder,
                  width: isActive ? 6 : 1.5,
                ),
                boxShadow: isActive
                    ? [
                        BoxShadow(
                          color: AuthTheme.primary.withOpacity(0.3),
                          blurRadius: 8,
                        ),
                      ]
                    : null,
              ),
            ),
          ],
        ),
      ),
    );
  }

  /// Frosted glass OTP digit box
  Widget _buildOtpBox(int index) {
    final hasValue = _controllers[index].text.isNotEmpty;
    return SizedBox(
      width: 50,
      height: 58,
      child: ClipRRect(
        borderRadius: BorderRadius.circular(14),
        child: BackdropFilter(
          filter: ImageFilter.blur(sigmaX: 10, sigmaY: 10),
          child: AnimatedContainer(
            duration: const Duration(milliseconds: 200),
            decoration: BoxDecoration(
              color: hasValue
                  ? AuthTheme.primary.withOpacity(0.15)
                  : AuthTheme.glassInputFill,
              borderRadius: BorderRadius.circular(14),
              border: Border.all(
                color: hasValue
                    ? AuthTheme.primaryLight.withOpacity(0.6)
                    : AuthTheme.glassBorder,
                width: hasValue ? 1.5 : 1,
              ),
              boxShadow: hasValue
                  ? [
                      BoxShadow(
                        color: AuthTheme.primary.withOpacity(0.2),
                        blurRadius: 8,
                      ),
                    ]
                  : null,
            ),
            child: TextField(
              controller: _controllers[index],
              focusNode: _focusNodes[index],
              textAlign: TextAlign.center,
              keyboardType: TextInputType.number,
              maxLength: 1,
              onChanged: (v) => _onOtpChanged(v, index),
              inputFormatters: [FilteringTextInputFormatter.digitsOnly],
              style: const TextStyle(
                fontFamily: AuthTheme.fontFamily,
                fontSize: 24,
                fontWeight: FontWeight.w700,
                color: AuthTheme.textOnGlass,
              ),
              cursorColor: AuthTheme.primaryLight,
              decoration: const InputDecoration(
                counterText: '',
                border: InputBorder.none,
                contentPadding: EdgeInsets.symmetric(vertical: 14),
              ),
            ),
          ),
        ),
      ),
    );
  }
}
