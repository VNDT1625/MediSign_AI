import 'package:flutter/material.dart';

import 'auth_theme.dart';
import 'verify_otp_page.dart';
import '../../../core/validators/auth_validators.dart';
import '../../../core/services/auth_service.dart';

/// Register page — Apple-style glassmorphism.
/// Gradient bg → glass form card → frosted inputs → glass checkboxes → CTA.
class RegisterPage extends StatefulWidget {
  const RegisterPage({super.key, required this.onAuthComplete});

  final VoidCallback onAuthComplete;

  @override
  State<RegisterPage> createState() => _RegisterPageState();
}

class _RegisterPageState extends State<RegisterPage> {
  final _nameCtrl = TextEditingController();
  final _emailCtrl = TextEditingController();
  final _phoneCtrl = TextEditingController();
  final _passCtrl = TextEditingController();
  final _confirmCtrl = TextEditingController();
  bool _obscurePass = true;
  bool _obscureConfirm = true;
  bool _agreeTerms = false;
  bool _agreeDisclaimer = false;
  bool _isLoading = false;

  // Validation errors
  String? _nameError;
  String? _emailError;
  String? _phoneError;
  String? _passError;
  String? _confirmError;
  int _passwordStrength = 0;

  @override
  void dispose() {
    _nameCtrl.dispose();
    _emailCtrl.dispose();
    _phoneCtrl.dispose();
    _passCtrl.dispose();
    _confirmCtrl.dispose();
    super.dispose();
  }

  bool get _canRegister => _agreeTerms && _agreeDisclaimer;

  void _onPasswordChanged(String value) {
    setState(() {
      _passwordStrength = AuthValidators.getPasswordStrength(value);
      if (_passError != null && value.length >= 8) {
        _passError = null;
      }
    });
  }

  bool _validate() {
    final errors = <String, String?>{};

    setState(() {
      // Validate full name
      _nameError = AuthValidators.validateFullName(_nameCtrl.text.trim());
      errors['name'] = _nameError;

      // Validate email
      _emailError = AuthValidators.validateEmail(_emailCtrl.text.trim());
      errors['email'] = _emailError;

      // Validate phone
      _phoneError = AuthValidators.validatePhone(_phoneCtrl.text.trim());
      errors['phone'] = _phoneError;

      // Validate password
      _passError = AuthValidators.validatePassword(_passCtrl.text);
      errors['pass'] = _passError;

      // Validate confirm password
      _confirmError = AuthValidators.validateConfirmPassword(
        _confirmCtrl.text,
        _passCtrl.text,
      );
      errors['confirm'] = _confirmError;
    });

    return !errors.values.any((e) => e != null);
  }

  Future<void> _onRegister() async {
    if (!_canRegister) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Vui lòng đồng ý với điều khoản sử dụng'),
          backgroundColor: Colors.orange,
        ),
      );
      return;
    }

    if (!_validate()) return;

    setState(() => _isLoading = true);

    // Use AuthService
    final authService = AuthService();
    final result = await authService.register(
      email: _emailCtrl.text.trim(),
      phone: _phoneCtrl.text.trim(),
      username: _emailCtrl.text.trim().split('@').first,
      fullName: _nameCtrl.text.trim(),
      password: _passCtrl.text,
    );

    if (!mounted) return;

    setState(() => _isLoading = false);

    if (result.success) {
      // Navigate to OTP verification
      Navigator.of(context).pushReplacement(
        MaterialPageRoute(
          builder: (_) => VerifyOtpPage(
            email: _emailCtrl.text.trim(),
            onAuthComplete: widget.onAuthComplete,
          ),
        ),
      );
    } else {
      // Show error
      final errorMsg =
          result.errors?.join('\n') ?? result.message ?? 'Đăng ký thất bại';
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(errorMsg),
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
                const SizedBox(height: 20),

                // ── Title ──
                const Text('Tạo tài khoản', style: AuthTheme.h2),
                const SizedBox(height: 6),
                const Text(
                  'Đăng ký để bắt đầu chăm sóc sức khỏe cùng MediSign AI',
                  style: AuthTheme.subtitle,
                ),
                const SizedBox(height: 28),

                // ── Glass form card ──
                AuthTheme.glassCard(
                  padding: const EdgeInsets.all(24),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      // ── Fields ──
                      AuthTheme.fieldLabel('Họ và tên',
                          icon: Icons.person_outline),
                      AuthTheme.inputField(
                        controller: _nameCtrl,
                        hint: 'Nguyễn Văn A',
                        textInputAction: TextInputAction.next,
                        errorText: _nameError,
                        onChanged: (_) {
                          if (_nameError != null) {
                            setState(() => _nameError = null);
                          }
                        },
                      ),
                      const SizedBox(height: 16),

                      AuthTheme.fieldLabel('Email', icon: Icons.email_outlined),
                      AuthTheme.inputField(
                        controller: _emailCtrl,
                        hint: 'email@example.com',
                        keyboardType: TextInputType.emailAddress,
                        textInputAction: TextInputAction.next,
                        errorText: _emailError,
                        onChanged: (_) {
                          if (_emailError != null) {
                            setState(() => _emailError = null);
                          }
                        },
                      ),
                      const SizedBox(height: 16),

                      AuthTheme.fieldLabel('Số điện thoại',
                          icon: Icons.phone_outlined),
                      AuthTheme.inputField(
                        controller: _phoneCtrl,
                        hint: '0912 345 678',
                        keyboardType: TextInputType.phone,
                        textInputAction: TextInputAction.next,
                        errorText: _phoneError,
                        onChanged: (_) {
                          if (_phoneError != null) {
                            setState(() => _phoneError = null);
                          }
                        },
                      ),
                      const SizedBox(height: 16),

                      AuthTheme.fieldLabel('Mật khẩu',
                          icon: Icons.lock_outline),
                      AuthTheme.inputField(
                        controller: _passCtrl,
                        hint: 'Ít nhất 8 ký tự',
                        obscure: _obscurePass,
                        textInputAction: TextInputAction.next,
                        errorText: _passError,
                        onChanged: _onPasswordChanged,
                        suffix: _visibilityToggle(
                          obscure: _obscurePass,
                          onTap: () =>
                              setState(() => _obscurePass = !_obscurePass),
                        ),
                      ),
                      const SizedBox(height: 16),

                      const Text('Xác nhận mật khẩu', style: AuthTheme.label),
                      const SizedBox(height: 8),
                      AuthTheme.inputField(
                        controller: _confirmCtrl,
                        hint: 'Nhập lại mật khẩu',
                        obscure: _obscureConfirm,
                        textInputAction: TextInputAction.done,
                        errorText: _confirmError,
                        onChanged: (_) {
                          if (_confirmError != null) {
                            setState(() => _confirmError = null);
                          }
                        },
                        suffix: _visibilityToggle(
                          obscure: _obscureConfirm,
                          onTap: () => setState(
                              () => _obscureConfirm = !_obscureConfirm),
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 20),

                // Password strength indicator
                if (_passwordStrength > 0) ...[
                  _buildPasswordStrengthIndicator(strength: _passwordStrength),
                  const SizedBox(height: 16),
                ],

                // ── Terms checkbox — glass style ──
                _buildGlassCheckbox(
                  value: _agreeTerms,
                  onChanged: (v) => setState(() => _agreeTerms = v ?? false),
                  child: const Text.rich(
                    TextSpan(
                      style: TextStyle(
                        fontFamily: AuthTheme.fontFamily,
                        fontSize: 13,
                        color: AuthTheme.textOnGlassSecondary,
                      ),
                      children: [
                        TextSpan(text: 'Tôi đồng ý với '),
                        TextSpan(
                          text: 'Điều khoản sử dụng',
                          style: TextStyle(
                            color: AuthTheme.primaryLight,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                        TextSpan(text: ' và '),
                        TextSpan(
                          text: 'Chính sách bảo mật',
                          style: TextStyle(
                            color: AuthTheme.primaryLight,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
                const SizedBox(height: 8),

                // ── Medical disclaimer checkbox ──
                _buildGlassCheckbox(
                  value: _agreeDisclaimer,
                  onChanged: (v) =>
                      setState(() => _agreeDisclaimer = v ?? false),
                  child: const Text.rich(
                    TextSpan(
                      style: TextStyle(
                        fontFamily: AuthTheme.fontFamily,
                        fontSize: 13,
                        color: AuthTheme.textOnGlassSecondary,
                      ),
                      children: [
                        TextSpan(text: 'Tôi hiểu rằng MediSign AI '),
                        TextSpan(
                          text: 'KHÔNG thay thế bác sĩ',
                          style: TextStyle(
                            color: Color(0xFFFF6B6B),
                            fontWeight: FontWeight.w700,
                          ),
                        ),
                        TextSpan(text: ', chỉ hỗ trợ tham khảo'),
                      ],
                    ),
                  ),
                ),
                const SizedBox(height: 24),

                // ── Register button ──
                AuthTheme.primaryButton(
                  text: 'Đăng ký',
                  onPressed: _canRegister ? _onRegister : null,
                  isLoading: _isLoading,
                ),
                const SizedBox(height: 20),

                // ── Footer ──
                Center(
                  child: GestureDetector(
                    onTap: () => Navigator.of(context).pop(),
                    child: const Text.rich(
                      TextSpan(
                        style: AuthTheme.subtitle,
                        children: [
                          TextSpan(text: 'Đã có tài khoản? '),
                          TextSpan(
                            text: 'Đăng nhập',
                            style: AuthTheme.link,
                          ),
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

  Widget _visibilityToggle({
    required bool obscure,
    required VoidCallback onTap,
  }) {
    return GestureDetector(
      onTap: onTap,
      child: Icon(
        obscure ? Icons.visibility_off_outlined : Icons.visibility_outlined,
        color: AuthTheme.textOnGlassMuted,
        size: 20,
      ),
    );
  }

  Widget _buildGlassCheckbox({
    required bool value,
    required ValueChanged<bool?> onChanged,
    required Widget child,
  }) {
    return GestureDetector(
      onTap: () => onChanged(!value),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          AnimatedContainer(
            duration: const Duration(milliseconds: 200),
            width: 22,
            height: 22,
            margin: const EdgeInsets.only(top: 2, right: 10),
            decoration: BoxDecoration(
              color: value
                  ? AuthTheme.primary
                  : Colors.white.withValues(alpha: 0.08),
              borderRadius: BorderRadius.circular(6),
              border: value
                  ? Border.all(
                      color: AuthTheme.primaryLight.withValues(alpha: 0.5),
                      width: 1)
                  : Border.all(color: AuthTheme.glassBorder, width: 1.5),
              boxShadow: value
                  ? [
                      BoxShadow(
                        color: AuthTheme.primary.withValues(alpha: 0.3),
                        blurRadius: 8,
                      ),
                    ]
                  : null,
            ),
            child: value
                ? const Icon(Icons.check, size: 15, color: Colors.white)
                : null,
          ),
          Expanded(child: child),
        ],
      ),
    );
  }

  /// Password strength indicator widget
  Widget _buildPasswordStrengthIndicator({required int strength}) {
    final labels = ['Yếu', 'Trung bình', 'Khá', 'Mạnh', 'Rất mạnh'];
    final colors = [
      Colors.red,
      Colors.orange,
      Colors.yellow.shade700,
      Colors.lightGreen,
      Colors.green,
    ];
    final color =
        strength > 0 ? colors[(strength - 1).clamp(0, 4)] : Colors.grey;
    final label = strength > 0 ? labels[(strength - 1).clamp(0, 4)] : '';
    final progress = strength / 4;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Expanded(
              child: ClipRRect(
                borderRadius: BorderRadius.circular(4),
                child: LinearProgressIndicator(
                  value: progress,
                  backgroundColor: Colors.white.withValues(alpha: 0.1),
                  valueColor: AlwaysStoppedAnimation<Color>(color),
                  minHeight: 6,
                ),
              ),
            ),
            const SizedBox(width: 12),
            Text(
              label,
              style: TextStyle(
                fontFamily: AuthTheme.fontFamily,
                fontSize: 12,
                fontWeight: FontWeight.w500,
                color: color,
              ),
            ),
          ],
        ),
      ],
    );
  }
}
