// Auth Service - Handle login, register, logout, token management
// Connects to FastAPI backend with PostgreSQL

import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import '../validators/auth_validators.dart';

/// API Configuration
class ApiConfig {
  // API base URL configuration:
  //   - Android emulator : 10.0.2.2  → maps to host machine's localhost
  //   - iOS simulator / desktop / web: localhost
  //   - Physical device  : set FLUTTER_API_BASE_URL env var at build time,
  //     e.g. `flutter run --dart-define=FLUTTER_API_BASE_URL=http://192.168.1.x:8000/api/v1`
  //     Falls back to LAN IP placeholder so it fails loudly instead of silently.
  static const String _envBaseUrl = String.fromEnvironment(
    'FLUTTER_API_BASE_URL',
    defaultValue: '',
  );

  static String get baseUrl {
    // Prefer explicit override (physical device / staging / prod)
    if (_envBaseUrl.isNotEmpty) return _envBaseUrl;

    if (kIsWeb ||
        defaultTargetPlatform == TargetPlatform.iOS ||
        defaultTargetPlatform == TargetPlatform.macOS ||
        defaultTargetPlatform == TargetPlatform.windows ||
        defaultTargetPlatform == TargetPlatform.linux) {
      return 'http://localhost:8000/api/v1';
    }
    // Android emulator: 10.0.2.2 maps to host machine localhost
    return 'http://10.0.2.2:8000/api/v1';
  }

  static const Duration timeout = Duration(seconds: 30);

  static Map<String, String> get headers => {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      };

  static Map<String, String> authHeaders(String? accessToken) => {
        ...headers,
        if (accessToken != null) 'Authorization': 'Bearer $accessToken',
      };
}

/// User model
class User {
  final String id;
  final String email;
  final String? phone;
  final String username;
  final String fullName;
  final bool isEmailVerified;
  final bool isPhoneVerified;
  final String accountType;
  final DateTime? createdAt;
  final DateTime? updatedAt;

  User({
    required this.id,
    required this.email,
    this.phone,
    required this.username,
    required this.fullName,
    this.isEmailVerified = false,
    this.isPhoneVerified = false,
    this.accountType = 'user',
    this.createdAt,
    this.updatedAt,
  });

  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id'] ?? '',
      email: json['email'] ?? '',
      phone: json['phone'],
      username: json['username'] ?? '',
      fullName: json['full_name'] ?? '',
      isEmailVerified: json['is_email_verified'] ?? false,
      isPhoneVerified: json['is_phone_verified'] ?? false,
      accountType: json['account_type'] ?? 'user',
      createdAt: json['created_at'] != null
          ? DateTime.tryParse(json['created_at'])
          : null,
      updatedAt: json['updated_at'] != null
          ? DateTime.tryParse(json['updated_at'])
          : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'email': email,
      'phone': phone,
      'username': username,
      'full_name': fullName,
      'is_email_verified': isEmailVerified,
      'is_phone_verified': isPhoneVerified,
      'account_type': accountType,
      'created_at': createdAt?.toIso8601String(),
      'updated_at': updatedAt?.toIso8601String(),
    };
  }
}

/// Auth tokens
class AuthTokens {
  final String accessToken;
  final String refreshToken;
  final String tokenType;
  final int expiresIn;
  final DateTime expiresAt;

  AuthTokens({
    required this.accessToken,
    required this.refreshToken,
    this.tokenType = 'bearer',
    this.expiresIn = 3600,
  }) : expiresAt = DateTime.now().add(Duration(seconds: expiresIn));

  bool get isExpired => DateTime.now().isAfter(expiresAt);

  factory AuthTokens.fromJson(Map<String, dynamic> json) {
    final expiresIn = json['expires_in'] as int? ?? 3600;
    return AuthTokens(
      accessToken: json['access_token'] ?? '',
      refreshToken: json['refresh_token'] ?? '',
      tokenType: json['token_type'] ?? 'bearer',
      expiresIn: expiresIn,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'access_token': accessToken,
      'refresh_token': refreshToken,
      'token_type': tokenType,
      'expires_in': expiresIn,
    };
  }
}

/// Auth result
class AuthResult {
  final bool success;
  final String? message;
  final User? user;
  final AuthTokens? tokens;
  final List<String>? errors;
  final int? statusCode;

  AuthResult({
    required this.success,
    this.message,
    this.user,
    this.tokens,
    this.errors,
    this.statusCode,
  });
}

/// Auth service state
enum AuthState { initial, loading, authenticated, unauthenticated, error }

/// Auth Service - connects to FastAPI backend
class AuthService extends ChangeNotifier {
  AuthState _state = AuthState.initial;
  User? _currentUser;
  AuthTokens? _tokens;
  String? _errorMessage;

  AuthState get state => _state;
  User? get currentUser => _currentUser;
  AuthTokens? get tokens => _tokens;
  String? get errorMessage => _errorMessage;
  bool get isAuthenticated =>
      _state == AuthState.authenticated && _tokens != null;

  /// Make HTTP request to backend
  Future<http.Response> _makeRequest(
    String endpoint, {
    Map<String, dynamic>? body,
    String? accessToken,
  }) async {
    final uri = Uri.parse('${ApiConfig.baseUrl}$endpoint');
    try {
      return await http
          .post(
            uri,
            headers: ApiConfig.authHeaders(accessToken),
            body: body != null ? jsonEncode(body) : null,
          )
          .timeout(ApiConfig.timeout);
    } catch (e) {
      throw Exception('Network error: $e');
    }
  }

  /// Initialize - load stored tokens
  Future<void> initialize() async {
    _state = AuthState.loading;
    notifyListeners();
    try {
      final prefs = await SharedPreferences.getInstance();
      final tokenJson = prefs.getString('auth_tokens');
      final userJson = prefs.getString('auth_user');
      if (tokenJson != null && userJson != null) {
        final tokens = AuthTokens.fromJson(jsonDecode(tokenJson));
        if (!tokens.isExpired) {
          _tokens = tokens;
          _currentUser = User.fromJson(jsonDecode(userJson));
          _state = AuthState.authenticated;
        } else {
          final refreshResult = await refreshToken();
          if (!refreshResult.success) {
            await _clearStorage();
            _state = AuthState.unauthenticated;
          }
        }
      } else {
        _state = AuthState.unauthenticated;
      }
    } catch (e) {
      debugPrint('Auth init error: $e');
      _state = AuthState.unauthenticated;
    }
    notifyListeners();
  }

  /// Login with email/phone and password
  Future<AuthResult> login(
      {required String identifier, required String password}) async {
    _state = AuthState.loading;
    _errorMessage = null;
    notifyListeners();
    try {
      final errors = <String>[];
      final isEmail = identifier.contains('@');
      if (isEmail) {
        final emailError = AuthValidators.validateEmail(identifier);
        if (emailError != null) errors.add(emailError);
      } else {
        final phoneError = AuthValidators.validatePhone(identifier);
        if (phoneError != null) errors.add(phoneError);
      }
      if (password.isEmpty) errors.add('Vui lòng nhập mật khẩu');
      if (errors.isNotEmpty) {
        _state = AuthState.unauthenticated;
        notifyListeners();
        return AuthResult(success: false, errors: errors);
      }
      final body = isEmail
          ? {'email': identifier, 'password': password}
          : {'phone': identifier, 'password': password};
      final response = await _makeRequest('/auth/login', body: body);
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        final tokens = AuthTokens.fromJson(data['tokens']);
        final user = User.fromJson(data['user']);
        await _saveAuth(tokens, user);
        _currentUser = user;
        _tokens = tokens;
        _state = AuthState.authenticated;
        notifyListeners();
        return AuthResult(
            success: true,
            message: 'Đăng nhập thành công',
            user: user,
            tokens: tokens);
      } else {
        final errorData = jsonDecode(response.body);
        final errorDetail = errorData['detail'];
        String errorMsg = 'Đăng nhập thất bại';
        if (errorDetail is Map) {
          errorMsg = errorDetail['message'] ?? errorDetail.toString();
        } else if (errorDetail is String) errorMsg = errorDetail;
        _state = AuthState.unauthenticated;
        _errorMessage = errorMsg;
        notifyListeners();
        return AuthResult(
            success: false, message: errorMsg, statusCode: response.statusCode);
      }
    } catch (e) {
      _state = AuthState.error;
      _errorMessage = 'Lỗi kết nối: ${e.toString()}';
      notifyListeners();
      return AuthResult(success: false, message: _errorMessage);
    }
  }

  /// Register new user
  Future<AuthResult> register({
    required String email,
    required String phone,
    required String username,
    required String fullName,
    required String password,
  }) async {
    _state = AuthState.loading;
    _errorMessage = null;
    notifyListeners();
    try {
      final errors = <String>[];
      final emailError = AuthValidators.validateEmail(email);
      if (emailError != null) errors.add(emailError);
      final phoneError = AuthValidators.validatePhone(phone);
      if (phoneError != null) errors.add(phoneError);
      final usernameError = AuthValidators.validateUsername(username);
      if (usernameError != null) errors.add(usernameError);
      final nameError = AuthValidators.validateFullName(fullName);
      if (nameError != null) errors.add(nameError);
      final passwordError = AuthValidators.validatePassword(password);
      if (passwordError != null) errors.add(passwordError);
      if (errors.isNotEmpty) {
        _state = AuthState.unauthenticated;
        notifyListeners();
        return AuthResult(success: false, errors: errors);
      }
      final body = {
        'email': email,
        'phone': phone,
        'username': username,
        'full_name': fullName,
        'password': password
      };
      final response = await _makeRequest('/auth/register', body: body);
      if (response.statusCode == 200 || response.statusCode == 201) {
        final data = jsonDecode(response.body);
        final tokens = AuthTokens.fromJson(data['tokens']);
        final user = User.fromJson(data['user']);
        await _saveAuth(tokens, user);
        _currentUser = user;
        _tokens = tokens;
        _state = AuthState.authenticated;
        notifyListeners();
        return AuthResult(
            success: true,
            message: data['message'] ?? 'Đăng ký thành công',
            user: user,
            tokens: tokens);
      } else {
        final errorData = jsonDecode(response.body);
        final errorDetail = errorData['detail'];
        String errorMsg = 'Đăng ký thất bại';
        if (errorDetail is Map) {
          errorMsg = errorDetail['message'] ?? errorDetail.toString();
        } else if (errorDetail is String) errorMsg = errorDetail;
        _state = AuthState.unauthenticated;
        _errorMessage = errorMsg;
        notifyListeners();
        return AuthResult(
            success: false, message: errorMsg, statusCode: response.statusCode);
      }
    } catch (e) {
      _state = AuthState.error;
      _errorMessage = 'Lỗi kết nối: ${e.toString()}';
      notifyListeners();
      return AuthResult(success: false, message: _errorMessage);
    }
  }

  /// Logout
  Future<void> logout() async {
    _state = AuthState.loading;
    notifyListeners();
    try {
      if (_tokens?.accessToken != null) {
        await _makeRequest('/auth/logout', accessToken: _tokens?.accessToken);
      }
    } catch (e) {
      debugPrint('Logout API error: $e');
    }
    try {
      await _clearStorage();
    } catch (e) {
      debugPrint('Logout storage error: $e');
    }
    _currentUser = null;
    _tokens = null;
    _state = AuthState.unauthenticated;
    notifyListeners();
  }

  /// Refresh token
  Future<AuthResult> refreshToken() async {
    if (_tokens == null || _tokens!.refreshToken.isEmpty) {
      return AuthResult(success: false, message: 'Không có refresh token');
    }
    try {
      final response = await _makeRequest('/auth/refresh',
          body: {'refresh_token': _tokens!.refreshToken});
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        final tokens = AuthTokens.fromJson(data);
        await _saveAuth(tokens, _currentUser);
        _tokens = tokens;
        _state = AuthState.authenticated;
        notifyListeners();
        return AuthResult(success: true, tokens: tokens);
      } else {
        await logout();
        return AuthResult(success: false, message: 'Phiên đã hết hạn');
      }
    } catch (e) {
      await logout();
      return AuthResult(success: false, message: 'Lỗi làm mới token');
    }
  }

  /// Change password
  Future<AuthResult> changePassword(
      {required String currentPassword, required String newPassword}) async {
    if (_tokens == null) {
      return AuthResult(success: false, message: 'Chưa đăng nhập');
    }
    try {
      final response = await _makeRequest('/auth/change-password',
          accessToken: _tokens!.accessToken,
          body: {
            'current_password': currentPassword,
            'new_password': newPassword
          });
      if (response.statusCode == 200) {
        return AuthResult(success: true, message: 'Đổi mật khẩu thành công');
      } else {
        final errorData = jsonDecode(response.body);
        final errorMsg =
            errorData['detail']?['message'] ?? 'Đổi mật khẩu thất bại';
        return AuthResult(success: false, message: errorMsg);
      }
    } catch (e) {
      return AuthResult(success: false, message: 'Lỗi kết nối: $e');
    }
  }

  /// Get current user from API
  Future<AuthResult> fetchCurrentUser() async {
    if (_tokens == null) {
      return AuthResult(success: false, message: 'Chưa đăng nhập');
    }
    try {
      final uri = Uri.parse('${ApiConfig.baseUrl}/auth/me');
      final response = await http
          .get(uri, headers: ApiConfig.authHeaders(_tokens!.accessToken))
          .timeout(ApiConfig.timeout);
      if (response.statusCode == 200) {
        final user = User.fromJson(jsonDecode(response.body));
        _currentUser = user;
        final prefs = await SharedPreferences.getInstance();
        await prefs.setString('auth_user', jsonEncode(user.toJson()));
        notifyListeners();
        return AuthResult(success: true, user: user);
      } else {
        return AuthResult(
            success: false, message: 'Không lấy được thông tin user');
      }
    } catch (e) {
      return AuthResult(success: false, message: 'Lỗi kết nối: $e');
    }
  }

  /// Save auth data to storage
  Future<void> _saveAuth(AuthTokens tokens, User? user) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('auth_tokens', jsonEncode(tokens.toJson()));
    if (user != null) {
      await prefs.setString('auth_user', jsonEncode(user.toJson()));
    }
  }

  /// Clear auth storage
  Future<void> _clearStorage() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('auth_tokens');
    await prefs.remove('auth_user');
  }
}
