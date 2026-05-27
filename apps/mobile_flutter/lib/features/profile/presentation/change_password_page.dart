import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import '../../../core/services/auth_service.dart';

// Light theme tokens (đồng bộ ProfilePage).
const _kBg = Color(0xFFF8FAFC);
const _kBorder = Color(0xFFE2E8F0);
const _kInk = Color(0xFF0F172A);
const _kInkSoft = Color(0xFF475569);
const _kInkMuted = Color(0xFF94A3B8);
const _kBrand = Color(0xFF16A34A);
const _kDanger = Color(0xFFDC2626);
const _kSuccess = Color(0xFF10B981);

/// Đổi mật khẩu — gọi `AuthService.changePassword` với 3 ô:
/// mật khẩu hiện tại, mật khẩu mới, xác nhận mật khẩu mới.
class ChangePasswordPage extends StatefulWidget {
  const ChangePasswordPage({super.key, required this.authService});

  final AuthService authService;

  @override
  State<ChangePasswordPage> createState() => _ChangePasswordPageState();
}

class _ChangePasswordPageState extends State<ChangePasswordPage> {
  final _formKey = GlobalKey<FormState>();
  final _currentCtrl = TextEditingController();
  final _newCtrl = TextEditingController();
  final _confirmCtrl = TextEditingController();

  bool _showCurrent = false;
  bool _showNew = false;
  bool _showConfirm = false;
  bool _submitting = false;
  String? _serverError;

  @override
  void dispose() {
    _currentCtrl.dispose();
    _newCtrl.dispose();
    _confirmCtrl.dispose();
    super.dispose();
  }

  String? _validatePassword(String? v) {
    if (v == null || v.isEmpty) return 'Vui lòng nhập mật khẩu';
    if (v.length < 8) return 'Mật khẩu phải có ít nhất 8 ký tự';
    return null;
  }

  String? _validateConfirm(String? v) {
    final base = _validatePassword(v);
    if (base != null) return base;
    if (v != _newCtrl.text) return 'Mật khẩu xác nhận không khớp';
    return null;
  }

  Future<void> _submit() async {
    if (_submitting) return;
    if (!(_formKey.currentState?.validate() ?? false)) return;
    if (_currentCtrl.text == _newCtrl.text) {
      setState(() {
        _serverError = 'Mật khẩu mới phải khác mật khẩu hiện tại.';
      });
      return;
    }

    setState(() {
      _submitting = true;
      _serverError = null;
    });
    HapticFeedback.lightImpact();

    final result = await widget.authService.changePassword(
      currentPassword: _currentCtrl.text,
      newPassword: _newCtrl.text,
    );

    if (!mounted) return;
    setState(() => _submitting = false);

    if (result.success) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Đổi mật khẩu thành công.'),
          backgroundColor: _kSuccess,
        ),
      );
      Navigator.of(context).pop(true);
    } else {
      setState(() {
        _serverError = result.message ?? 'Đổi mật khẩu thất bại.';
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: _kBg,
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0,
        scrolledUnderElevation: 0,
        foregroundColor: _kInk,
        title: const Text(
          'Đổi mật khẩu',
          style: TextStyle(
            fontFamily: 'Outfit',
            fontWeight: FontWeight.w700,
            fontSize: 18,
            color: _kInk,
          ),
        ),
      ),
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.fromLTRB(16, 16, 16, 24),
          children: [
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: const Color(0xFFF0FDF4),
                borderRadius: BorderRadius.circular(14),
                border: Border.all(color: const Color(0xFFBBF7D0)),
              ),
              child: const Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Icon(Icons.shield_outlined, color: _kBrand, size: 20),
                  SizedBox(width: 10),
                  Expanded(
                    child: Text(
                      'Mật khẩu mới phải có ít nhất 8 ký tự. Sau khi đổi thành công, bạn cần đăng nhập lại trên các thiết bị khác.',
                      style: TextStyle(
                        fontFamily: 'Outfit',
                        fontSize: 12.5,
                        color: _kInkSoft,
                        height: 1.4,
                      ),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 16),
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(20),
                border: Border.all(color: _kBorder),
              ),
              child: Form(
                key: _formKey,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    _PasswordField(
                      controller: _currentCtrl,
                      label: 'Mật khẩu hiện tại',
                      obscure: !_showCurrent,
                      onToggle: () => setState(() => _showCurrent = !_showCurrent),
                      validator: _validatePassword,
                      enabled: !_submitting,
                    ),
                    const SizedBox(height: 12),
                    _PasswordField(
                      controller: _newCtrl,
                      label: 'Mật khẩu mới',
                      obscure: !_showNew,
                      onToggle: () => setState(() => _showNew = !_showNew),
                      validator: _validatePassword,
                      enabled: !_submitting,
                    ),
                    const SizedBox(height: 12),
                    _PasswordField(
                      controller: _confirmCtrl,
                      label: 'Xác nhận mật khẩu mới',
                      obscure: !_showConfirm,
                      onToggle: () =>
                          setState(() => _showConfirm = !_showConfirm),
                      validator: _validateConfirm,
                      enabled: !_submitting,
                    ),
                    if (_serverError != null) ...[
                      const SizedBox(height: 12),
                      Container(
                        padding: const EdgeInsets.symmetric(
                            horizontal: 12, vertical: 10),
                        decoration: BoxDecoration(
                          color: const Color(0xFFFEF2F2),
                          borderRadius: BorderRadius.circular(10),
                          border: Border.all(color: const Color(0xFFFECACA)),
                        ),
                        child: Row(
                          children: [
                            const Icon(Icons.error_outline,
                                size: 18, color: _kDanger),
                            const SizedBox(width: 8),
                            Expanded(
                              child: Text(
                                _serverError!,
                                style: const TextStyle(
                                  fontFamily: 'Outfit',
                                  fontSize: 12.5,
                                  color: _kDanger,
                                ),
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],
                    const SizedBox(height: 16),
                    SizedBox(
                      height: 48,
                      child: ElevatedButton(
                        onPressed: _submitting ? null : _submit,
                        style: ElevatedButton.styleFrom(
                          backgroundColor: _kBrand,
                          foregroundColor: Colors.white,
                          disabledBackgroundColor: _kInkMuted,
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(12),
                          ),
                        ),
                        child: _submitting
                            ? const SizedBox(
                                width: 20,
                                height: 20,
                                child: CircularProgressIndicator(
                                  strokeWidth: 2,
                                  color: Colors.white,
                                ),
                              )
                            : const Text(
                                'Cập nhật mật khẩu',
                                style: TextStyle(
                                  fontFamily: 'Outfit',
                                  fontWeight: FontWeight.w700,
                                  fontSize: 14.5,
                                ),
                              ),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _PasswordField extends StatelessWidget {
  const _PasswordField({
    required this.controller,
    required this.label,
    required this.obscure,
    required this.onToggle,
    required this.validator,
    required this.enabled,
  });

  final TextEditingController controller;
  final String label;
  final bool obscure;
  final VoidCallback onToggle;
  final FormFieldValidator<String> validator;
  final bool enabled;

  @override
  Widget build(BuildContext context) {
    return TextFormField(
      controller: controller,
      obscureText: obscure,
      enabled: enabled,
      autocorrect: false,
      enableSuggestions: false,
      style: const TextStyle(
        fontFamily: 'Outfit',
        fontSize: 14,
        color: _kInk,
      ),
      decoration: InputDecoration(
        labelText: label,
        labelStyle: const TextStyle(
          fontFamily: 'Outfit',
          color: _kInkSoft,
          fontSize: 13.5,
        ),
        filled: true,
        fillColor: const Color(0xFFF8FAFC),
        suffixIcon: IconButton(
          tooltip: obscure ? 'Hiện mật khẩu' : 'Ẩn mật khẩu',
          onPressed: onToggle,
          icon: Icon(
            obscure ? Icons.visibility_outlined : Icons.visibility_off_outlined,
            size: 20,
            color: _kInkSoft,
          ),
        ),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: _kBorder),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: _kBorder),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: _kBrand, width: 1.5),
        ),
        errorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: _kDanger),
        ),
      ),
      validator: validator,
    );
  }
}
