// Auth Validation - Username, Password, Email, Phone validation rules

class AuthValidators {
  // Email validation
  static String? validateEmail(String? value) {
    if (value == null || value.isEmpty) {
      return 'Vui lòng nhập email';
    }

    // Basic email regex
    final emailRegex = RegExp(
      r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
    );

    if (!emailRegex.hasMatch(value)) {
      return 'Email không hợp lệ';
    }

    if (value.length > 100) {
      return 'Email quá dài (tối đa 100 ký tự)';
    }

    return null;
  }

  // Phone validation (Vietnamese format)
  static String? validatePhone(String? value) {
    if (value == null || value.isEmpty) {
      return 'Vui lòng nhập số điện thoại';
    }

    // Remove spaces and dashes for validation
    final cleanPhone = value.replaceAll(RegExp(r'[\s\-]'), '');

    // Vietnamese phone regex (10 digits, starts with 0, 3, 5, 7, 8, 9)
    final phoneRegex = RegExp(r'^0[3-9]\d{8}$');

    if (!phoneRegex.hasMatch(cleanPhone)) {
      return 'Số điện thoại không hợp lệ (VD: 0912 345 678)';
    }

    return null;
  }

  // Username validation
  static String? validateUsername(String? value) {
    if (value == null || value.isEmpty) {
      return 'Vui lòng nhập tên đăng nhập';
    }

    if (value.length < 3) {
      return 'Tên đăng nhập phải có ít nhất 3 ký tự';
    }

    if (value.length > 30) {
      return 'Tên đăng nhập quá dài (tối đa 30 ký tự)';
    }

    // Username can only contain letters, numbers, underscores
    final usernameRegex = RegExp(r'^[a-zA-Z0-9_]+$');

    if (!usernameRegex.hasMatch(value)) {
      return 'Chỉ chứa chữ cái, số và dấu gạch dưới';
    }

    return null;
  }

  // Full name validation
  static String? validateFullName(String? value) {
    if (value == null || value.isEmpty) {
      return 'Vui lòng nhập họ và tên';
    }

    if (value.length < 2) {
      return 'Tên quá ngắn';
    }

    if (value.length > 50) {
      return 'Tên quá dài (tối đa 50 ký tự)';
    }

    // Name should contain at least one letter
    final nameRegex = RegExp(r'[a-zA-ZÀ-ỹ]');
    if (!nameRegex.hasMatch(value)) {
      return 'Tên phải chứa chữ cái';
    }

    return null;
  }

  // Password validation
  static String? validatePassword(String? value) {
    if (value == null || value.isEmpty) {
      return 'Vui lòng nhập mật khẩu';
    }

    if (value.length < 8) {
      return 'Mật khẩu phải có ít nhất 8 ký tự';
    }

    if (value.length > 128) {
      return 'Mật khẩu quá dài (tối đa 128 ký tự)';
    }

    // Check for at least one uppercase
    if (!RegExp(r'[A-Z]').hasMatch(value)) {
      return 'Phải có ít nhất 1 chữ cái in hoa';
    }

    // Check for at least one lowercase
    if (!RegExp(r'[a-z]').hasMatch(value)) {
      return 'Phải có ít nhất 1 chữ cái thường';
    }

    // Check for at least one number
    if (!RegExp(r'[0-9]').hasMatch(value)) {
      return 'Phải có ít nhất 1 số';
    }

    // Check for at least one special character
    if (!RegExp(r'[!@#$%^&*(),.?":{}|<>]').hasMatch(value)) {
      return r'Phải có ít nhất 1 ký tự đặc biệt (!@#$%^&*...)';
    }

    return null;
  }

  // Confirm password validation
  static String? validateConfirmPassword(String? value, String? password) {
    if (value == null || value.isEmpty) {
      return 'Vui lòng xác nhận mật khẩu';
    }

    if (value != password) {
      return 'Mật khẩu xác nhận không khớp';
    }

    return null;
  }

  // Get password strength (0-100)
  static int getPasswordStrength(String? value) {
    if (value == null || value.isEmpty) return 0;

    int score = 0;

    // Length scoring
    if (value.length >= 8) score += 20;
    if (value.length >= 10) score += 10;
    if (value.length >= 12) score += 10;

    // Character variety scoring
    if (RegExp(r'[a-z]').hasMatch(value)) score += 15;
    if (RegExp(r'[A-Z]').hasMatch(value)) score += 15;
    if (RegExp(r'[0-9]').hasMatch(value)) score += 15;
    if (RegExp(r'[!@#$%^&*(),.?":{}|<>]').hasMatch(value)) score += 15;

    return score.clamp(0, 100);
  }

  // Get password strength label
  static String getPasswordStrengthLabel(int strength) {
    if (strength < 30) return 'Yếu';
    if (strength < 60) return 'Trung bình';
    if (strength < 80) return 'Mạnh';
    return 'Rất mạnh';
  }

  // Get password strength color
  static int getPasswordStrengthColor(int strength) {
    if (strength < 30) return 0xFFE53935; // Red
    if (strength < 60) return 0xFFFFA726; // Orange
    if (strength < 80) return 0xFF66BB6A; // Green
    return 0xFF43A047; // Dark Green
  }
}
