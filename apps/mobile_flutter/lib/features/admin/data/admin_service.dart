/// Admin service - API calls for admin panel.
library;
import 'dart:convert';
import 'package:dio/dio.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../data/admin_models.dart';

class AdminService {
  late final Dio _dio;
  String? _accessToken;

  AdminService() {
    _dio = Dio(BaseOptions(
      baseUrl: 'http://10.0.2.2:8000/api/v1',
      connectTimeout: const Duration(seconds: 30),
      headers: {'Content-Type': 'application/json'},
    ));
    _loadToken();
  }

  Future<void> _loadToken() async {
    final prefs = await SharedPreferences.getInstance();
    final tokenJson = prefs.getString('auth_tokens');
    if (tokenJson != null) {
      final tokens = jsonDecode(tokenJson);
      _accessToken = tokens['access_token'];
    }
  }

  Map<String, String> get _headers => {
    'Content-Type': 'application/json',
    if (_accessToken != null) 'Authorization': 'Bearer $_accessToken',
  };

  /// Get dashboard stats
  Future<AdminStats> getStats() async {
    try {
      final response = await _dio.get('/admin/stats', options: Options(headers: _headers));
      return AdminStats.fromJson(response.data);
    } catch (e) {
      throw Exception('Failed to load stats: $e');
    }
  }

  /// Get all users
  Future<List<AdminUser>> getUsers({int page = 1, int limit = 20, String? search}) async {
    try {
      final response = await _dio.get(
        '/admin/users',
        queryParameters: {'page': page, 'limit': limit, if (search != null) 'search': search},
        options: Options(headers: _headers),
      );
      return (response.data as List).map((e) => AdminUser.fromJson(e)).toList();
    } catch (e) {
      throw Exception('Failed to load users: $e');
    }
  }

  /// Get user by ID
  Future<AdminUser> getUser(String userId) async {
    try {
      final response = await _dio.get('/admin/users/$userId', options: Options(headers: _headers));
      return AdminUser.fromJson(response.data);
    } catch (e) {
      throw Exception('Failed to load user: $e');
    }
  }

  /// Update user
  Future<AdminUser> updateUser(String userId, Map<String, dynamic> data) async {
    try {
      final response = await _dio.patch('/admin/users/$userId', data: data, options: Options(headers: _headers));
      return AdminUser.fromJson(response.data);
    } catch (e) {
      throw Exception('Failed to update user: $e');
    }
  }

  /// Toggle user active status
  Future<bool> toggleUserActive(String userId) async {
    try {
      final response = await _dio.get('/admin/users/$userId/toggle-active', options: Options(headers: _headers));
      return response.data['is_active'] ?? false;
    } catch (e) {
      throw Exception('Failed to toggle user: $e');
    }
  }

  /// Delete (deactivate) user
  Future<void> deleteUser(String userId) async {
    try {
      await _dio.delete('/admin/users/$userId', options: Options(headers: _headers));
    } catch (e) {
      throw Exception('Failed to delete user: $e');
    }
  }

  /// Get all medicines
  Future<List<AdminMedicine>> getMedicines({int page = 1, int limit = 20, String? search}) async {
    try {
      final response = await _dio.get(
        '/admin/medicines',
        queryParameters: {'page': page, 'limit': limit, if (search != null) 'search': search},
        options: Options(headers: _headers),
      );
      return (response.data as List).map((e) => AdminMedicine.fromJson(e)).toList();
    } catch (e) {
      throw Exception('Failed to load medicines: $e');
    }
  }

  /// Create medicine
  Future<AdminMedicine> createMedicine(Map<String, dynamic> data) async {
    try {
      final response = await _dio.post('/admin/medicines', data: data, options: Options(headers: _headers));
      return AdminMedicine.fromJson(response.data);
    } catch (e) {
      throw Exception('Failed to create medicine: $e');
    }
  }

  /// Update medicine
  Future<AdminMedicine> updateMedicine(String regNumber, Map<String, dynamic> data) async {
    try {
      final response = await _dio.patch('/admin/medicines/$regNumber', data: data, options: Options(headers: _headers));
      return AdminMedicine.fromJson(response.data);
    } catch (e) {
      throw Exception('Failed to update medicine: $e');
    }
  }

  /// Delete medicine
  Future<void> deleteMedicine(String regNumber) async {
    try {
      await _dio.delete('/admin/medicines/$regNumber', options: Options(headers: _headers));
    } catch (e) {
      throw Exception('Failed to delete medicine: $e');
    }
  }

  /// Get all hospitals
  Future<List<AdminHospital>> getHospitals({int page = 1, int limit = 20, String? search}) async {
    try {
      final response = await _dio.get(
        '/admin/hospitals',
        queryParameters: {'page': page, 'limit': limit, if (search != null) 'search': search},
        options: Options(headers: _headers),
      );
      return (response.data as List).map((e) => AdminHospital.fromJson(e)).toList();
    } catch (e) {
      throw Exception('Failed to load hospitals: $e');
    }
  }

  /// Create hospital
  Future<AdminHospital> createHospital(Map<String, dynamic> data) async {
    try {
      final response = await _dio.post('/admin/hospitals', data: data, options: Options(headers: _headers));
      return AdminHospital.fromJson(response.data);
    } catch (e) {
      throw Exception('Failed to create hospital: $e');
    }
  }

  /// Update hospital
  Future<AdminHospital> updateHospital(int id, Map<String, dynamic> data) async {
    try {
      final response = await _dio.patch('/admin/hospitals/$id', data: data, options: Options(headers: _headers));
      return AdminHospital.fromJson(response.data);
    } catch (e) {
      throw Exception('Failed to update hospital: $e');
    }
  }

  /// Delete hospital
  Future<void> deleteHospital(int id) async {
    try {
      await _dio.delete('/admin/hospitals/$id', options: Options(headers: _headers));
    } catch (e) {
      throw Exception('Failed to delete hospital: $e');
    }
  }
}

