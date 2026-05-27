/// Real HTTP-backed implementations of [ConsultApi] and [MedicineApi].
///
/// These speak to the FastAPI backend exposed at `BACKEND_API_BASE_URL`
/// (which defaults to the same value [ApiConfig.baseUrl] uses for auth).
///
/// The constructors accept optional [accessTokenProvider] and [httpClient]
/// hooks so production code can plug in [AuthService] tokens (cabinet
/// endpoints require auth) and tests can inject a mock client.

import 'dart:convert';

import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;

import '../models/consult_mode.dart';
import '../services/auth_service.dart' show ApiConfig;
import 'api_contracts.dart';
import 'api_models.dart';

typedef AccessTokenProvider = String? Function();

/// Lightweight wrapper around `package:http` used by both API implementations.
class _HttpHelper {
  _HttpHelper({
    http.Client? client,
    this.accessTokenProvider,
    Duration? timeout,
  })  : _client = client ?? http.Client(),
        _timeout = timeout ?? ApiConfig.timeout;

  final http.Client _client;
  final AccessTokenProvider? accessTokenProvider;
  final Duration _timeout;

  Map<String, String> _headers() {
    final token = accessTokenProvider?.call();
    return {
      ...ApiConfig.headers,
      if (token != null && token.isNotEmpty) 'Authorization': 'Bearer $token',
    };
  }

  Future<Map<String, dynamic>> postJson(
    String path,
    Map<String, dynamic> body,
  ) async {
    final url = Uri.parse('${ApiConfig.baseUrl}$path');
    try {
      final response = await _client
          .post(url, headers: _headers(), body: jsonEncode(body))
          .timeout(_timeout);
      return _decode(response, url);
    } catch (e) {
      if (kDebugMode) debugPrint('[HttpApi] POST $url failed: $e');
      rethrow;
    }
  }

  /// Variant of [postJson] that returns the raw `data` payload — used when
  /// the backend response is a JSON array (e.g. `/journal` listings nested
  /// under `items`).
  Future<dynamic> getRaw(
    String path, {
    Map<String, String>? query,
  }) async {
    var url = Uri.parse('${ApiConfig.baseUrl}$path');
    if (query != null && query.isNotEmpty) {
      url = url.replace(queryParameters: query);
    }
    try {
      final response =
          await _client.get(url, headers: _headers()).timeout(_timeout);
      return _decodeRaw(response, url);
    } catch (e) {
      if (kDebugMode) debugPrint('[HttpApi] GET $url failed: $e');
      rethrow;
    }
  }

  Future<dynamic> patchJson(
    String path,
    Map<String, dynamic> body,
  ) async {
    final url = Uri.parse('${ApiConfig.baseUrl}$path');
    try {
      final response = await _client
          .patch(url, headers: _headers(), body: jsonEncode(body))
          .timeout(_timeout);
      return _decodeRaw(response, url);
    } catch (e) {
      if (kDebugMode) debugPrint('[HttpApi] PATCH $url failed: $e');
      rethrow;
    }
  }

  Future<dynamic> postRaw(
    String path,
    Map<String, dynamic>? body,
  ) async {
    final url = Uri.parse('${ApiConfig.baseUrl}$path');
    try {
      final response = await _client
          .post(
            url,
            headers: _headers(),
            body: body == null ? null : jsonEncode(body),
          )
          .timeout(_timeout);
      return _decodeRaw(response, url);
    } catch (e) {
      if (kDebugMode) debugPrint('[HttpApi] POST $url failed: $e');
      rethrow;
    }
  }

  Future<void> delete(String path) async {
    final url = Uri.parse('${ApiConfig.baseUrl}$path');
    try {
      final response =
          await _client.delete(url, headers: _headers()).timeout(_timeout);
      final status = response.statusCode;
      if (status < 200 || status >= 300) {
        throw HttpApiException(
          statusCode: status,
          message: 'Request to $url failed (HTTP $status)',
          body: response.body,
        );
      }
    } catch (e) {
      if (kDebugMode) debugPrint('[HttpApi] DELETE $url failed: $e');
      rethrow;
    }
  }

  Map<String, dynamic> _decode(http.Response response, Uri url) {
    final status = response.statusCode;
    if (status < 200 || status >= 300) {
      throw HttpApiException(
        statusCode: status,
        message: 'Request to $url failed (HTTP $status)',
        body: response.body,
      );
    }
    if (response.body.isEmpty) return <String, dynamic>{};
    final decoded = jsonDecode(response.body);
    if (decoded is Map<String, dynamic>) return decoded;
    return <String, dynamic>{'data': decoded};
  }

  /// Like [_decode] but returns the raw decoded JSON (object OR list) so
  /// callers can handle both shapes.
  dynamic _decodeRaw(http.Response response, Uri url) {
    final status = response.statusCode;
    if (status < 200 || status >= 300) {
      throw HttpApiException(
        statusCode: status,
        message: 'Request to $url failed (HTTP $status)',
        body: response.body,
      );
    }
    if (response.body.isEmpty) return null;
    return jsonDecode(response.body);
  }

  void close() => _client.close();
}

class HttpApiException implements Exception {
  HttpApiException({
    required this.statusCode,
    required this.message,
    this.body,
  });

  final int statusCode;
  final String message;
  final String? body;

  @override
  String toString() => 'HttpApiException($statusCode): $message';
}

/// Real consult API talking to `POST /consult/triage`.
class HttpConsultApi implements ConsultApi {
  HttpConsultApi({http.Client? client, AccessTokenProvider? accessTokenProvider})
      : _http = _HttpHelper(
          client: client,
          accessTokenProvider: accessTokenProvider,
        );

  final _HttpHelper _http;

  @override
  Future<TriageResult> triage({
    required String symptomText,
    required ConsultMode mode,
  }) async {
    final json = await _http.postJson('/consult/triage', {
      'symptom_text': symptomText,
      'mode': mode.name,
    });

    return TriageResult(
      urgencyLevel: (json['urgency_level'] ?? 'non_emergency') as String,
      summary: (json['summary'] ?? '') as String,
      recommendations: List<String>.from(
        (json['recommendations'] as List<dynamic>? ?? const []).map(
          (e) => e.toString(),
        ),
      ),
    );
  }

  void close() => _http.close();
}

/// Real medicine API talking to `POST /medicine/scan`.
class HttpMedicineApi implements MedicineApi {
  HttpMedicineApi({http.Client? client, AccessTokenProvider? accessTokenProvider})
      : _http = _HttpHelper(
          client: client,
          accessTokenProvider: accessTokenProvider,
        );

  final _HttpHelper _http;

  @override
  Future<MedicineScanResult> scan({
    required String extractedText,
    List<String> currentMedications = const [],
  }) async {
    final json = await _http.postJson('/medicine/scan', {
      'extracted_text': extractedText,
      'current_medications': currentMedications,
    });

    return MedicineScanResult(
      normalizedName: (json['normalized_name'] ?? extractedText) as String,
      riskLevel: (json['risk_level'] ?? 'low') as String,
      warnings: List<String>.from(
        (json['warnings'] as List<dynamic>? ?? const []).map(
          (e) => e.toString(),
        ),
      ),
      guidance: (json['guidance'] ?? '') as String,
    );
  }

  void close() => _http.close();
}

/// Real cabinet API talking to `/medicine/cabinet/*`.
///
/// All operations require an auth token; the constructor takes an
/// [AccessTokenProvider] supplied by `AuthService.tokens?.accessToken`.
class HttpCabinetApi implements CabinetApi {
  HttpCabinetApi({
    http.Client? client,
    AccessTokenProvider? accessTokenProvider,
  }) : _http = _HttpHelper(
          client: client,
          accessTokenProvider: accessTokenProvider,
        );

  final _HttpHelper _http;

  @override
  Future<List<CabinetItem>> list() async {
    final raw = await _http.getRaw('/medicine/cabinet');
    if (raw is Map<String, dynamic>) {
      final items = raw['items'];
      if (items is List) {
        return items
            .whereType<Map<String, dynamic>>()
            .map(CabinetItem.fromJson)
            .toList();
      }
    }
    return const [];
  }

  @override
  Future<CabinetItem> add(CabinetItemInput input) async {
    final body = input.toJson();
    final raw = await _http.postRaw('/medicine/cabinet', body);
    if (raw is Map<String, dynamic>) {
      return CabinetItem.fromJson(raw);
    }
    throw HttpApiException(
      statusCode: 500,
      message: 'Unexpected payload from POST /medicine/cabinet',
    );
  }

  @override
  Future<CabinetItem> update(String itemId, CabinetItemInput patch) async {
    final raw =
        await _http.patchJson('/medicine/cabinet/$itemId', patch.toJson());
    if (raw is Map<String, dynamic>) {
      return CabinetItem.fromJson(raw);
    }
    throw HttpApiException(
      statusCode: 500,
      message: 'Unexpected payload from PATCH /medicine/cabinet/$itemId',
    );
  }

  @override
  Future<void> remove(String itemId) {
    return _http.delete('/medicine/cabinet/$itemId');
  }

  @override
  Future<CabinetItem> recordDose(String itemId) async {
    final raw = await _http.postRaw('/medicine/cabinet/$itemId/dose', null);
    if (raw is Map<String, dynamic>) {
      return CabinetItem.fromJson(raw);
    }
    throw HttpApiException(
      statusCode: 500,
      message: 'Unexpected payload from POST /medicine/cabinet/$itemId/dose',
    );
  }

  void close() => _http.close();
}

/// Real journal API talking to `/journal/*` (Soul Garden).
class HttpJournalApi implements JournalApi {
  HttpJournalApi({
    http.Client? client,
    AccessTokenProvider? accessTokenProvider,
  }) : _http = _HttpHelper(
          client: client,
          accessTokenProvider: accessTokenProvider,
        );

  final _HttpHelper _http;

  @override
  Future<List<JournalRecord>> list({
    DateTime? from,
    DateTime? to,
    int page = 1,
    int pageSize = 50,
  }) async {
    String fmt(DateTime d) => d.toIso8601String().substring(0, 10);
    final query = <String, String>{
      'page': '$page',
      'page_size': '$pageSize',
      if (from != null) 'from_date': fmt(from),
      if (to != null) 'to_date': fmt(to),
    };
    final raw = await _http.getRaw('/journal', query: query);
    if (raw is Map<String, dynamic>) {
      final items = raw['items'];
      if (items is List) {
        return items
            .whereType<Map<String, dynamic>>()
            .map(JournalRecord.fromJson)
            .toList();
      }
    }
    return const [];
  }

  @override
  Future<JournalRecord> create(JournalInput input) async {
    final raw = await _http.postRaw('/journal', input.toJson(isCreate: true));
    if (raw is Map<String, dynamic>) {
      return JournalRecord.fromJson(raw);
    }
    throw HttpApiException(
      statusCode: 500,
      message: 'Unexpected payload from POST /journal',
    );
  }

  @override
  Future<JournalRecord> update(String entryId, JournalInput patch) async {
    final raw = await _http.patchJson('/journal/$entryId', patch.toJson());
    if (raw is Map<String, dynamic>) {
      return JournalRecord.fromJson(raw);
    }
    throw HttpApiException(
      statusCode: 500,
      message: 'Unexpected payload from PATCH /journal/$entryId',
    );
  }

  @override
  Future<void> remove(String entryId) {
    return _http.delete('/journal/$entryId');
  }

  void close() => _http.close();
}
