import 'dart:async';
import 'dart:math' as math;

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import '../../../core/services/model_download_service.dart';
import '../../../core/theme/glass_theme.dart';

/// ══════════════════════════════════════════════════════════════
/// DOCTOR HUB — Màn hình tương tác 3D kiểu Talking Tom
/// ══════════════════════════════════════════════════════════════
///
/// Layout: Bác sĩ 3D đứng giữa màn hình, xung quanh là các nút
/// điều hướng tới các tính năng chính của app.
///
/// Đặc điểm:
/// - Model 3D bác sĩ (lazy-download, không đi kèm app)
/// - Sign language: bác sĩ dùng cử chỉ để giao tiếp
/// - Nhại giọng nói (như Talking Tom)
/// - Phù hợp trẻ em + người khuyết tật
/// - Buttons xung quanh model dẫn đến các tính năng
///
/// TODO cho user:
/// - Tạo model 3D bác sĩ (.glb format)
/// - Tạo animation set (idle, wave, sign language, talk)
/// - Tích hợp model_viewer_plus hoặc flutter_3d_controller
/// ══════════════════════════════════════════════════════════════

class DoctorHubPage extends StatefulWidget {
  const DoctorHubPage({
    super.key,
    this.onBack,
    this.onNavigate,
  });

  final VoidCallback? onBack;
  final void Function(String route)? onNavigate;

  @override
  State<DoctorHubPage> createState() => _DoctorHubPageState();
}

class _DoctorHubPageState extends State<DoctorHubPage>
    with TickerProviderStateMixin {
  final ModelDownloadService _downloadService = ModelDownloadService();

  bool _modelReady = false;
  bool _isDownloading = false;
  DownloadProgress? _downloadProgress;
  String _doctorMessage =
      'Xin chào! Tôi là bác sĩ AI.\nChạm vào tôi để nói chuyện! 👋';

  late AnimationController _breatheController;
  late AnimationController _bounceController;
  late Animation<double> _breatheAnimation;
  late Animation<double> _bounceAnimation;

  @override
  void initState() {
    super.initState();

    _breatheController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 2500),
    )..repeat(reverse: true);

    _bounceController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 600),
    );

    _breatheAnimation = Tween<double>(begin: 0.97, end: 1.03).animate(
      CurvedAnimation(parent: _breatheController, curve: Curves.easeInOut),
    );

    _bounceAnimation = Tween<double>(begin: 0.0, end: -15.0).animate(
      CurvedAnimation(parent: _bounceController, curve: Curves.easeOut),
    );

    _checkModelStatus();
  }

  @override
  void dispose() {
    _breatheController.dispose();
    _bounceController.dispose();
    super.dispose();
  }

  Future<void> _checkModelStatus() async {
    final ready = await _downloadService.isModelDownloaded('doctor_hub_3d');
    if (mounted) setState(() => _modelReady = ready);
  }

  Future<void> _startDownload() async {
    setState(() => _isDownloading = true);

    await for (final progress
        in _downloadService.downloadModel('doctor_hub_3d')) {
      if (!mounted) return;
      setState(() => _downloadProgress = progress);

      if (progress.status == ModelDownloadStatus.ready) {
        setState(() {
          _modelReady = true;
          _isDownloading = false;
          _doctorMessage =
              'Tuyệt vời! Model đã sẵn sàng.\nHãy chạm vào tôi! 🎉';
        });
      } else if (progress.status == ModelDownloadStatus.error) {
        setState(() {
          _isDownloading = false;
          _doctorMessage = 'Có lỗi khi tải. Thử lại nhé! 😅';
        });
      }
    }
  }

  void _onDoctorTap() {
    HapticFeedback.mediumImpact();
    _bounceController.forward().then((_) => _bounceController.reverse());

    final messages = [
      'Bạn có khỏe không? 😊',
      'Nhấn nút xung quanh để khám phá! 🔍',
      'Tôi có thể giúp gì cho bạn? 🩺',
      'Hãy chăm sóc sức khỏe mỗi ngày nhé! 💪',
      'Muốn tập thể dục không? 🏋️',
      'Đừng quên kiểm tra thuốc nhé! 💊',
    ];
    setState(() {
      _doctorMessage = messages[math.Random().nextInt(messages.length)];
    });
  }

  @override
  Widget build(BuildContext context) {
    return GlassTheme.scaffoldBackground(
      child: SafeArea(
        child: Column(
          children: [
            _buildAppBar(),
            Expanded(child: _buildHubContent()),
          ],
        ),
      ),
    );
  }

  Widget _buildAppBar() {
    return Padding(
      padding: const EdgeInsets.fromLTRB(8, 8, 8, 0),
      child: Row(
        children: [
          GlassTheme.glassIconButton(
            icon: Icons.arrow_back_ios_new_rounded,
            onPressed: () {
              HapticFeedback.lightImpact();
              if (widget.onBack != null) {
                widget.onBack!();
              } else {
                Navigator.of(context).pop();
              }
            },
            size: 44,
          ),
          const Expanded(
            child: Text(
              'Bác sĩ AI',
              textAlign: TextAlign.center,
              style: GlassTheme.h3,
            ),
          ),
          GlassTheme.glassIconButton(
            icon: Icons.settings_outlined,
            onPressed: () {
              _showModelSettings(context);
            },
            size: 44,
          ),
        ],
      ),
    );
  }

  Widget _buildHubContent() {
    if (!_modelReady && !_isDownloading) {
      return _buildDownloadPrompt();
    }
    if (_isDownloading) {
      return _buildDownloadingView();
    }
    return _buildInteractiveHub();
  }

  // ── Download Prompt: Lần đầu mở, chưa có model ──
  Widget _buildDownloadPrompt() {
    return Padding(
      padding: const EdgeInsets.all(24),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Text('🏥', style: TextStyle(fontSize: 80)),
          const SizedBox(height: 24),
          const Text(
            'Bác sĩ 3D chưa được tải',
            style: GlassTheme.h2,
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 12),
          const Text(
            'Tải model bác sĩ 3D để trải nghiệm tương tác trực quan.\n'
            'Phù hợp cho trẻ em và người khuyết tật.',
            style: GlassTheme.body,
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 8),
          GlassTheme.glassCard(
            padding: const EdgeInsets.all(16),
            child: Column(
              children: [
                _infoRow('📦', 'Dung lượng', '~25 MB'),
                const SizedBox(height: 8),
                _infoRow('🌐', 'Yêu cầu', 'Kết nối mạng'),
                const SizedBox(height: 8),
                _infoRow('💾', 'Lưu trữ', 'Cache trên máy'),
              ],
            ),
          ),
          const SizedBox(height: 24),
          GlassTheme.primaryButton(
            text: 'Tải Bác sĩ 3D',
            icon: Icons.download_rounded,
            onPressed: _startDownload,
          ),
          const SizedBox(height: 12),
          GlassTheme.secondaryButton(
            text: 'Dùng phiên bản đơn giản',
            onPressed: () {
              setState(() {
                _modelReady = true;
                _doctorMessage =
                    'Đang dùng phiên bản đơn giản.\nTải model 3D để trải nghiệm tốt hơn! 📱';
              });
            },
          ),
        ],
      ),
    );
  }

  Widget _infoRow(String emoji, String label, String value) {
    return Row(
      children: [
        Text(emoji, style: const TextStyle(fontSize: 18)),
        const SizedBox(width: 10),
        Text(label, style: GlassTheme.label),
        const Spacer(),
        Text(value, style: GlassTheme.body.copyWith(color: Colors.white)),
      ],
    );
  }

  // ── Downloading View ──
  Widget _buildDownloadingView() {
    final dp = _downloadProgress;
    return Padding(
      padding: const EdgeInsets.all(24),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Text('⏳', style: TextStyle(fontSize: 64)),
          const SizedBox(height: 24),
          const Text('Đang tải Bác sĩ 3D...', style: GlassTheme.h3),
          const SizedBox(height: 16),
          if (dp != null) ...[
            GlassTheme.progressBar(value: dp.progress, height: 8),
            const SizedBox(height: 12),
            Text(
              dp.progressText,
              style: GlassTheme.caption,
            ),
            const SizedBox(height: 4),
            Text(
              _downloadStatusLabel(dp.status),
              style: GlassTheme.body,
            ),
          ],
        ],
      ),
    );
  }

  String _downloadStatusLabel(ModelDownloadStatus status) {
    switch (status) {
      case ModelDownloadStatus.checking:
        return 'Đang kiểm tra...';
      case ModelDownloadStatus.downloading:
        return 'Đang tải xuống...';
      case ModelDownloadStatus.verifying:
        return 'Đang xác minh...';
      case ModelDownloadStatus.ready:
        return 'Hoàn tất!';
      case ModelDownloadStatus.error:
        return 'Có lỗi xảy ra';
      default:
        return '';
    }
  }

  // ── Interactive Hub: Doctor + buttons ──
  Widget _buildInteractiveHub() {
    return LayoutBuilder(
      builder: (context, constraints) {
        final centerX = constraints.maxWidth / 2;
        final centerY = constraints.maxHeight / 2 - 20;
        final radius = math.min(centerX, centerY) * 0.72;

        // Navigation buttons arranged in a circle
        final hubActions = [
          const _HubAction('🩺', 'Hỏi bệnh', 'consult', Color(0xFF0D9488)),
          const _HubAction('💊', 'Quét thuốc', 'medicine', Color(0xFF2563EB)),
          const _HubAction('🏋️', 'Tập thể dục', 'fitness', Color(0xFFF59E0B)),
          const _HubAction(
              '🌱', 'Vườn Tâm Hồn', 'soul_garden', Color(0xFF7C3AED)),
          const _HubAction(
              '🏆', 'Thành tựu', 'achievements', Color(0xFFEF4444)),
          const _HubAction('👤', 'Hồ sơ', 'profile', Color(0xFF6366F1)),
        ];

        return Stack(
          children: [
            // Speech bubble
            Positioned(
              top: 16,
              left: 24,
              right: 24,
              child: _buildSpeechBubble(),
            ),

            // Action buttons arranged in circle
            ...List.generate(hubActions.length, (i) {
              final angle = (2 * math.pi * i / hubActions.length) - math.pi / 2;
              final x = centerX + radius * math.cos(angle) - 36;
              final y = centerY + radius * math.sin(angle) - 36;

              return Positioned(
                left: x,
                top: y,
                child: _buildHubButton(hubActions[i]),
              );
            }),

            // Doctor avatar (center) — placeholder until real 3D model
            Positioned(
              left: centerX - 60,
              top: centerY - 60,
              child: _buildDoctorAvatar(),
            ),

            // Sign language indicator
            Positioned(
              bottom: 16,
              left: 0,
              right: 0,
              child: _buildSignLanguageBar(),
            ),
          ],
        );
      },
    );
  }

  Widget _buildSpeechBubble() {
    return GlassTheme.glassCard(
      padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 14),
      fillColor: GlassTheme.glassFillMedium,
      child: Row(
        children: [
          const Text('💬', style: TextStyle(fontSize: 20)),
          const SizedBox(width: 10),
          Expanded(
            child: Text(
              _doctorMessage,
              style: GlassTheme.body.copyWith(
                color: Colors.white,
                fontSize: 14,
                height: 1.4,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildDoctorAvatar() {
    return GestureDetector(
      onTap: _onDoctorTap,
      child: AnimatedBuilder(
        animation: Listenable.merge([_breatheAnimation, _bounceAnimation]),
        builder: (context, child) {
          return Transform.translate(
            offset: Offset(0, _bounceAnimation.value),
            child: Transform.scale(
              scale: _breatheAnimation.value,
              child: child,
            ),
          );
        },
        child: Semantics(
          label: 'Bác sĩ AI. Chạm để nói chuyện.',
          button: true,
          child: Container(
            width: 120,
            height: 120,
            decoration: BoxDecoration(
              gradient: const LinearGradient(
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
                colors: [Color(0xFF0D9488), Color(0xFF059669)],
              ),
              shape: BoxShape.circle,
              boxShadow: [
                BoxShadow(
                  color: const Color(0xFF059669).withOpacity(0.4),
                  blurRadius: 30,
                  offset: const Offset(0, 8),
                ),
              ],
              border: Border.all(
                color: Colors.white.withOpacity(0.3),
                width: 3,
              ),
            ),
            child: const Center(
              // TODO: Replace with real 3D model viewer widget
              // Khi có model .glb, thay thế bằng:
              //   ModelViewer(
              //     src: localModelPath,
              //     autoRotate: true,
              //     cameraControls: true,
              //   )
              child: Text('🩺', style: TextStyle(fontSize: 52)),
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildHubButton(_HubAction action) {
    return GestureDetector(
      onTap: () {
        HapticFeedback.mediumImpact();
        widget.onNavigate?.call(action.route);
      },
      child: Semantics(
        label: action.label,
        button: true,
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              width: 72,
              height: 72,
              decoration: BoxDecoration(
                color: action.color.withOpacity(0.15),
                shape: BoxShape.circle,
                border: Border.all(
                  color: action.color.withOpacity(0.4),
                  width: 2,
                ),
                boxShadow: [
                  BoxShadow(
                    color: action.color.withOpacity(0.2),
                    blurRadius: 12,
                    offset: const Offset(0, 4),
                  ),
                ],
              ),
              child: Center(
                child: Text(
                  action.emoji,
                  style: const TextStyle(fontSize: 32),
                ),
              ),
            ),
            const SizedBox(height: 6),
            Text(
              action.label,
              style: const TextStyle(
                fontFamily: 'Outfit',
                fontSize: 11,
                fontWeight: FontWeight.w600,
                color: Colors.white70,
              ),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSignLanguageBar() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 24),
      child: GlassTheme.glassCard(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        child: Row(
          children: [
            const Text('🤟', style: TextStyle(fontSize: 22)),
            const SizedBox(width: 10),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Ngôn ngữ ký hiệu',
                    style: GlassTheme.label.copyWith(fontSize: 12),
                  ),
                  Text(
                    'Bác sĩ sẽ dùng cử chỉ để giao tiếp',
                    style: GlassTheme.caption.copyWith(fontSize: 11),
                  ),
                ],
              ),
            ),
            GlassTheme.badge(
              text: 'Beta',
              backgroundColor: const Color(0xFFF59E0B).withOpacity(0.15),
              textColor: const Color(0xFFF59E0B),
            ),
          ],
        ),
      ),
    );
  }

  void _showModelSettings(BuildContext context) {
    showModalBottomSheet(
      context: context,
      backgroundColor: const Color(0xFF0A2540),
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      builder: (ctx) {
        return Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Center(
                child: Container(
                  width: 40,
                  height: 4,
                  decoration: BoxDecoration(
                    color: Colors.white24,
                    borderRadius: BorderRadius.circular(2),
                  ),
                ),
              ),
              const SizedBox(height: 20),
              const Text('Cài đặt Bác sĩ 3D', style: GlassTheme.h3),
              const SizedBox(height: 16),
              ListTile(
                leading: const Text('📦', style: TextStyle(fontSize: 24)),
                title: Text('Quản lý model',
                    style: GlassTheme.body.copyWith(color: Colors.white)),
                subtitle: Text(
                  _modelReady ? 'Đã tải (v1.0.0)' : 'Chưa tải',
                  style: GlassTheme.caption,
                ),
                trailing: _modelReady
                    ? TextButton(
                        onPressed: () async {
                          await _downloadService.deleteModel('doctor_hub_3d');
                          if (mounted) {
                            setState(() => _modelReady = false);
                            Navigator.pop(ctx);
                          }
                        },
                        child: const Text('Xóa',
                            style: TextStyle(color: Color(0xFFEF4444))),
                      )
                    : null,
              ),
              ListTile(
                leading: const Text('🤟', style: TextStyle(fontSize: 24)),
                title: Text('Ngôn ngữ ký hiệu',
                    style: GlassTheme.body.copyWith(color: Colors.white)),
                subtitle: const Text('Bật/tắt hoạt ảnh sign language',
                    style: GlassTheme.caption),
                trailing: Switch(
                  value: true,
                  onChanged: (v) {},
                  activeThumbColor: GlassTheme.primaryGreen,
                ),
              ),
              ListTile(
                leading: const Text('🔊', style: TextStyle(fontSize: 24)),
                title: Text('Nhại giọng nói',
                    style: GlassTheme.body.copyWith(color: Colors.white)),
                subtitle: const Text('Bác sĩ lặp lại giọng bạn',
                    style: GlassTheme.caption),
                trailing: Switch(
                  value: false,
                  onChanged: (v) {},
                  activeThumbColor: GlassTheme.primaryGreen,
                ),
              ),
              const SizedBox(height: 16),
            ],
          ),
        );
      },
    );
  }
}

class _HubAction {
  final String emoji;
  final String label;
  final String route;
  final Color color;
  const _HubAction(this.emoji, this.label, this.route, this.color);
}
