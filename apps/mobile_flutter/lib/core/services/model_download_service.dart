import 'dart:async';

import 'package:shared_preferences/shared_preferences.dart';

/// ══════════════════════════════════════════════════════════════
/// MODEL DOWNLOAD SERVICE — Lazy-load 3D assets on demand
/// ══════════════════════════════════════════════════════════════
///
/// Kiến trúc tải model theo yêu cầu (giống tải map PUBG):
/// - App không đóng gói sẵn model 3D → giảm dung lượng cài đặt
/// - Khi người dùng bật Doctor Hub lần đầu → tải model về máy
/// - Model được cache local → lần sau không cần tải lại
/// - Hỗ trợ kiểm tra version để cập nhật model mới
///
/// FLOW:
///   1. User mở Doctor Hub
///   2. Check local cache → có model? → load trực tiếp
///   3. Không có → hiển thị UI download + progress bar
///   4. Tải từ CDN/server → lưu vào app directory
///   5. Verify checksum → sẵn sàng sử dụng
///
/// TODO cho user: Cung cấp URL thực tế và model files
/// ══════════════════════════════════════════════════════════════

/// Trạng thái tải model
enum ModelDownloadStatus {
  notDownloaded,
  checking,
  downloading,
  verifying,
  ready,
  error,
}

/// Thông tin về một model asset
class ModelAssetInfo {
  const ModelAssetInfo({
    required this.id,
    required this.name,
    required this.description,
    required this.downloadUrl,
    required this.version,
    required this.sizeBytes,
    this.checksum,
  });

  final String id;
  final String name;
  final String description;
  final String downloadUrl;
  final String version;
  final int sizeBytes;
  final String? checksum;

  String get sizeMB => '${(sizeBytes / (1024 * 1024)).toStringAsFixed(1)} MB';
}

/// Tiến trình tải
class DownloadProgress {
  const DownloadProgress({
    required this.status,
    required this.progress,
    this.errorMessage,
    this.bytesDownloaded = 0,
    this.totalBytes = 0,
  });

  final ModelDownloadStatus status;
  final double progress; // 0.0 - 1.0
  final String? errorMessage;
  final int bytesDownloaded;
  final int totalBytes;

  String get progressText {
    if (totalBytes == 0) return '';
    final dlMB = (bytesDownloaded / (1024 * 1024)).toStringAsFixed(1);
    final totalMB = (totalBytes / (1024 * 1024)).toStringAsFixed(1);
    return '$dlMB / $totalMB MB';
  }
}

/// Service quản lý tải và cache model 3D
class ModelDownloadService {
  static const _versionKeyPrefix = 'model_version_';
  static const _pathKeyPrefix = 'model_path_';

  SharedPreferences? _prefs;

  /// Danh sách model có sẵn để tải
  static const List<ModelAssetInfo> availableModels = [
    ModelAssetInfo(
      id: 'doctor_hub_3d',
      name: 'Bác sĩ 3D',
      description: 'Model 3D bác sĩ tương tác — hỗ trợ ngôn ngữ ký hiệu, '
          'hoạt ảnh và điều hướng bằng cử chỉ.',
      downloadUrl: '', // TODO: Set real CDN URL
      version: '1.0.0',
      sizeBytes: 25 * 1024 * 1024, // ~25 MB estimate
    ),
    ModelAssetInfo(
      id: 'sign_language_anim',
      name: 'Hoạt ảnh ngôn ngữ ký hiệu',
      description: 'Bộ hoạt ảnh ngôn ngữ ký hiệu Việt Nam cho model bác sĩ.',
      downloadUrl: '', // TODO: Set real CDN URL
      version: '1.0.0',
      sizeBytes: 15 * 1024 * 1024, // ~15 MB estimate
    ),
  ];

  Future<void> _ensureInit() async {
    _prefs ??= await SharedPreferences.getInstance();
  }

  /// Kiểm tra model đã tải chưa
  Future<bool> isModelDownloaded(String modelId) async {
    await _ensureInit();
    final path = _prefs!.getString('$_pathKeyPrefix$modelId');
    return path != null && path.isNotEmpty;
  }

  /// Lấy version model đã tải
  Future<String?> getDownloadedVersion(String modelId) async {
    await _ensureInit();
    return _prefs!.getString('$_versionKeyPrefix$modelId');
  }

  /// Kiểm tra có cần cập nhật không
  Future<bool> needsUpdate(String modelId) async {
    final downloadedVersion = await getDownloadedVersion(modelId);
    if (downloadedVersion == null) return true;

    final info = availableModels.firstWhere(
      (m) => m.id == modelId,
      orElse: () => throw Exception('Model $modelId not found'),
    );

    return downloadedVersion != info.version;
  }

  /// Lấy đường dẫn model local (null nếu chưa tải)
  Future<String?> getModelPath(String modelId) async {
    await _ensureInit();
    final path = _prefs!.getString('$_pathKeyPrefix$modelId');
    return path != null && path.isNotEmpty ? path : null;
  }

  /// Tải model — trả về stream progress
  /// TODO: Implement real HTTP download khi có CDN URL
  Stream<DownloadProgress> downloadModel(String modelId) async* {
    await _ensureInit();

    final info = availableModels.firstWhere(
      (m) => m.id == modelId,
      orElse: () => throw Exception('Model $modelId not found'),
    );

    // ── Step 1: Checking ──
    yield const DownloadProgress(
      status: ModelDownloadStatus.checking,
      progress: 0.0,
    );
    await Future.delayed(const Duration(milliseconds: 500));

    // ── Step 2: Download (MOCK — replace with real HTTP) ──
    // TODO: Replace mock with real download using dio:
    //
    //   final response = await Dio().download(
    //     info.downloadUrl,
    //     localPath,
    //     onReceiveProgress: (received, total) {
    //       yield DownloadProgress(
    //         status: ModelDownloadStatus.downloading,
    //         progress: received / total,
    //         bytesDownloaded: received,
    //         totalBytes: total,
    //       );
    //     },
    //   );

    const totalSteps = 20;
    for (int i = 1; i <= totalSteps; i++) {
      await Future.delayed(const Duration(milliseconds: 150));
      yield DownloadProgress(
        status: ModelDownloadStatus.downloading,
        progress: i / totalSteps,
        bytesDownloaded: (info.sizeBytes * i / totalSteps).round(),
        totalBytes: info.sizeBytes,
      );
    }

    // ── Step 3: Verify ──
    yield const DownloadProgress(
      status: ModelDownloadStatus.verifying,
      progress: 1.0,
    );
    await Future.delayed(const Duration(milliseconds: 300));

    // ── Step 4: Save metadata ──
    // TODO: Use actual file path from download
    final mockPath = '/data/models/$modelId/${info.version}/model.glb';
    await _prefs!.setString('$_pathKeyPrefix$modelId', mockPath);
    await _prefs!.setString('$_versionKeyPrefix$modelId', info.version);

    yield const DownloadProgress(
      status: ModelDownloadStatus.ready,
      progress: 1.0,
    );
  }

  /// Xóa model đã tải để giải phóng bộ nhớ
  Future<void> deleteModel(String modelId) async {
    await _ensureInit();
    await _prefs!.remove('$_pathKeyPrefix$modelId');
    await _prefs!.remove('$_versionKeyPrefix$modelId');
  }

  /// Tổng dung lượng model đã tải
  Future<int> totalDownloadedSize() async {
    int total = 0;
    for (final model in availableModels) {
      if (await isModelDownloaded(model.id)) {
        total += model.sizeBytes;
      }
    }
    return total;
  }
}
