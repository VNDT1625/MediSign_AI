import 'package:flutter/material.dart';
import 'package:video_player/video_player.dart';
import '../../../../core/services/vsl_parser.dart';

/// ══════════════════════════════════════════════════════════════
/// VSL OUTPUT WIDGET — Seamless Sign Language Video Stitcher
/// ══════════════════════════════════════════════════════════════
///
/// Widget này hiển thị câu trả lời y tế của AI dưới dạng Ngôn ngữ ký hiệu
/// Việt Nam thời gian thực bằng cách ghép chuỗi video cử chỉ offline.
///
/// Các tính năng nổi bật:
/// 1. Tự động dịch văn bản tiếng Việt sang chuỗi tokens bằng VslParser.
/// 2. Kỹ thuật đệm kép (Double-Buffering): Controller A phát, Controller B nạp trước.
/// 3. Cross-Fade transition: Mờ chồng mượt mà khi chuyển video y tế để xóa vệt đen.
/// 4. Độc lập an toàn: Tự động chạy giả lập chữ chạy nếu thiếu file video vật lý.
class VslOutputWidget extends StatefulWidget {
  const VslOutputWidget({
    super.key,
    required this.text,
    this.onCompleted,
  });

  /// Văn bản y khoa từ AI cần múa ký hiệu lại
  final String text;

  /// Callback kích hoạt khi toàn bộ câu ký hiệu đã phát xong
  final VoidCallback? onCompleted;

  @override
  State<VslOutputWidget> createState() => _VslOutputWidgetState();
}

class _VslOutputWidgetState extends State<VslOutputWidget> {
  List<String> _tokens = [];
  int _currentIndex = 0;

  // Double Buffering controllers
  VideoPlayerController? _controllerA;
  VideoPlayerController? _controllerB;

  bool _isControllerAActive = true;
  double _opacityA = 1.0;
  double _opacityB = 0.0;

  String _currentWord = '';
  bool _isPlaying = false;
  bool _hasError = false;

  // Từ điển ánh xạ Token sang tên hiển thị (Tiếng Việt)
  static const Map<String, String> _tokenLabels = {
    'ban': 'Bạn',
    'bac_si': 'Bác sĩ',
    'uong': 'Uống',
    'thuoc': 'Thuốc',
    'sot': 'Sốt',
    'ho': 'Ho',
    'dau': 'Đau',
    'dau_dau': 'Đau đầu',
    'bung': 'Bụng',
    'kho_tho': 'Khó thở',
    'chong_mat': 'Chóng mặt',
    'khan_cap': 'Khẩn cấp',
    'nghi_ngoi': 'Nghỉ ngơi',
    'uong_nuoc': 'Uống nước',
  };

  @override
  void initState() {
    super.initState();
    _processTextAndStart();
  }

  @override
  void didUpdateWidget(covariant VslOutputWidget oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.text != widget.text) {
      _cleanupControllers();
      _processTextAndStart();
    }
  }

  @override
  void dispose() {
    _cleanupControllers();
    super.dispose();
  }

  void _cleanupControllers() {
    _controllerA?.removeListener(_onVideoAPlaybackProgress);
    _controllerB?.removeListener(_onVideoBPlaybackProgress);
    _controllerA?.dispose();
    _controllerB?.dispose();
    _controllerA = null;
    _controllerB = null;
    _isPlaying = false;
  }

  /// Phân tích câu chữ và bắt đầu tiến trình phát cử chỉ
  void _processTextAndStart() {
    setState(() {
      _tokens = VslParser.parseText(widget.text);
      _currentIndex = 0;
      _isControllerAActive = true;
      _opacityA = 1.0;
      _opacityB = 0.0;
      _hasError = false;
    });

    if (_tokens.isNotEmpty) {
      _startPlayback();
    } else {
      widget.onCompleted?.call();
    }
  }

  Future<void> _startPlayback() async {
    _isPlaying = true;
    _currentWord = _tokenLabels[_tokens[_currentIndex]] ?? _tokens[_currentIndex].toUpperCase();

    // Khởi tạo Controller A (Active)
    _controllerA = await _initializeControllerForToken(_tokens[_currentIndex]);
    if (!mounted) return;

    if (_controllerA != null) {
      _controllerA!.addListener(_onVideoAPlaybackProgress);
      setState(() {});
      _controllerA!.play();

      // Nạp trước Controller B (Background) nếu có token tiếp theo
      if (_currentIndex + 1 < _tokens.length) {
        _preloadNextController(isA: false, token: _tokens[_currentIndex + 1]);
      }
    } else {
      // Hồi quy an toàn nếu không nạp được video (Chạy chế độ giả lập)
      _runFallbackMockPlayback();
    }
  }

  /// Nạp trước video cho bộ đệm tiếp theo ở chế độ ẩn
  Future<void> _preloadNextController({required bool isA, required String token}) async {
    final controller = await _initializeControllerForToken(token);
    if (!mounted) return;

    if (isA) {
      _controllerA?.dispose();
      _controllerA = controller;
      if (_controllerA != null) {
        _controllerA!.addListener(_onVideoAPlaybackProgress);
      }
    } else {
      _controllerB?.dispose();
      _controllerB = controller;
      if (_controllerB != null) {
        _controllerB!.addListener(_onVideoBPlaybackProgress);
      }
    }
    setState(() {});
  }

  /// Khởi tạo một controller từ assets
  Future<VideoPlayerController?> _initializeControllerForToken(String token) async {
    final assetPath = 'assets/signs/$token.mp4';
    final controller = VideoPlayerController.asset(assetPath);

    try {
      // Thử nạp video asset
      await controller.initialize();
      controller.setLooping(false);
      return controller;
    } catch (e) {
      // Vì đang trong môi trường phát triển, nếu thiếu file vật lý, trả về null để chạy Mock mode
      print("⚠️ VslOutputWidget: Không tìm thấy video y tế: $assetPath. Sử dụng trình diễn giả lập.");
      controller.dispose();
      return null;
    }
  }

  /// Lắng nghe tiến độ phát video của Controller A
  void _onVideoAPlaybackProgress() {
    if (!mounted || !_isPlaying || !_isControllerAActive) return;

    final val = _controllerA!.value;
    if (val.position >= val.duration - const Duration(milliseconds: 150)) {
      // Gần hết video A, kích hoạt mờ chồng sang B
      _transitionToNextSign();
    }
  }

  /// Lắng nghe tiến độ phát video của Controller B
  void _onVideoBPlaybackProgress() {
    if (!mounted || !_isPlaying || _isControllerAActive) return;

    final val = _controllerB!.value;
    if (val.position >= val.duration - const Duration(milliseconds: 150)) {
      // Gần hết video B, kích hoạt mờ chồng sang A
      _transitionToNextSign();
    }
  }

  /// Thực hiện quá trình mờ chồng (Cross-Fade) đệm kép sang cử chỉ tiếp theo
  void _transitionToNextSign() {
    if (_currentIndex + 1 >= _tokens.length) {
      // Đã phát xong toàn bộ câu
      _finishPlayback();
      return;
    }

    _currentIndex++;
    final nextToken = _tokens[_currentIndex];
    _currentWord = _tokenLabels[nextToken] ?? nextToken.toUpperCase();

    setState(() {
      if (_isControllerAActive) {
        // Chuyển A ──> B
        _isControllerAActive = false;
        _opacityA = 0.0;
        _opacityB = 1.0;
        _controllerB?.play();
      } else {
        // Chuyển B ──> A
        _isControllerAActive = true;
        _opacityA = 1.0;
        _opacityB = 0.0;
        _controllerA?.play();
      }
    });

    // Tải trước token sau nữa vào controller vừa giải phóng
    if (_currentIndex + 1 < _tokens.length) {
      _preloadNextController(
        isA: _isControllerAActive, // Nếu A đang active thì pre-load vào B và ngược lại
        token: _tokens[_currentIndex + 1],
      );
    }
  }

  void _finishPlayback() {
    setState(() {
      _isPlaying = false;
    });
    _cleanupControllers();
    widget.onCompleted?.call();
  }

  /// Chạy cơ chế giả lập chuyển từ nếu thiếu file video vật lý .mp4
  Future<void> _runFallbackMockPlayback() async {
    print("🚀 VslOutputWidget: Bắt đầu chế độ hiển thị giả lập y khoa...");
    while (mounted && _currentIndex < _tokens.length && _isPlaying) {
      setState(() {
        _currentWord = _tokenLabels[_tokens[_currentIndex]] ?? _tokens[_currentIndex].toUpperCase();
      });
      // Giả lập mỗi cử chỉ múa kéo dài 1.5 giây
      await Future.delayed(const Duration(milliseconds: 1500));
      if (!mounted || !_isPlaying) return;
      _currentIndex++;
    }
    _finishPlayback();
  }

  @override
  Widget build(BuildContext context) {
    final activeController = _isControllerAActive ? _controllerA : _controllerB;
    final isUsingVideo = _controllerA != null || _controllerB != null;

    return Semantics(
      label: 'Màn hình múa ký hiệu y tế thời gian thực. Từ đang hiển thị: $_currentWord',
      child: Container(
        margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: const Color(0xFF1E293B),
          borderRadius: BorderRadius.circular(24),
          border: Border.all(color: Colors.white.withOpacity(0.06)),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.3),
              blurRadius: 16,
              offset: const Offset(0, 8),
            ),
          ],
        ),
        child: Column(
          children: [
            // Header
            Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: const Color(0xFF8B5CF6).withOpacity(0.15),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: const Text('🤟', style: TextStyle(fontSize: 20)),
                ),
                const SizedBox(width: 10),
                const Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Diễn tả lại bằng ký hiệu',
                        style: TextStyle(
                          fontFamily: 'Outfit',
                          fontSize: 15,
                          fontWeight: FontWeight.w700,
                          color: Colors.white,
                        ),
                      ),
                      Text(
                        'Hệ thống phản hồi y khoa cho người câm điếc',
                        style: TextStyle(
                          fontFamily: 'Outfit',
                          fontSize: 11,
                          color: Colors.white38,
                        ),
                      ),
                    ],
                  ),
                ),
                // Play / replay button
                if (!_isPlaying)
                  Semantics(
                    label: 'Phát lại chuỗi ký hiệu',
                    button: true,
                    child: IconButton(
                      onPressed: () {
                        _cleanupControllers();
                        _processTextAndStart();
                      },
                      icon: const Icon(Icons.replay_rounded),
                      color: const Color(0xFF8B5CF6),
                      iconSize: 26,
                    ),
                  )
                else
                  Container(
                    width: 10,
                    height: 10,
                    decoration: const BoxDecoration(
                      color: Color(0xFF10B981),
                      shape: BoxShape.circle,
                    ),
                  ),
              ],
            ),
            const SizedBox(height: 16),

            // Video / Animation viewport
            AspectRatio(
              aspectRatio: 16 / 9,
              child: ClipRRect(
                borderRadius: BorderRadius.circular(16),
                child: Container(
                  color: const Color(0xFF0F172A),
                  child: Stack(
                    alignment: Alignment.center,
                    children: [
                      // Video layers
                      if (isUsingVideo) ...[
                        // Controller A Layer
                        if (_controllerA != null && _controllerA!.value.isInitialized)
                          Opacity(
                            opacity: _opacityA,
                            child: VideoPlayer(_controllerA!),
                          ),
                        // Controller B Layer
                        if (_controllerB != null && _controllerB!.value.isInitialized)
                          Opacity(
                            opacity: _opacityB,
                            child: VideoPlayer(_controllerB!),
                          ),
                      ] else ...[
                        // Fallback avatar/Lottie placeholder with futuristic pulses
                        _buildFuturisticPlaceholder(),
                      ],

                      // Subtitle Overlay at the bottom
                      Positioned(
                        bottom: 12,
                        left: 12,
                        right: 12,
                        child: Container(
                          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                          decoration: BoxDecoration(
                            color: Colors.black.withOpacity(0.7),
                            borderRadius: BorderRadius.circular(12),
                            border: Border.all(color: Colors.white.withOpacity(0.15)),
                          ),
                          child: Text(
                            _currentWord,
                            textAlign: Alignment.center.x == 0 ? TextAlign.center : TextAlign.left,
                            style: const TextStyle(
                              fontFamily: 'Outfit',
                              fontSize: 18,
                              fontWeight: FontWeight.w800,
                              color: Color(0xFFC4B5FD),
                              letterSpacing: 0.5,
                            ),
                          ),
                        ),
                      ),

                      // Loading state
                      if (_isPlaying && isUsingVideo && activeController != null && !activeController.value.isInitialized)
                        Container(
                          color: Colors.black45,
                          child: const CircularProgressIndicator(
                            valueColor: AlwaysStoppedAnimation<Color>(Color(0xFF8B5CF6)),
                          ),
                        ),
                    ],
                  ),
                ),
              ),
            ),
            const SizedBox(height: 12),

            // Tokens trackbar (Progress)
            _buildTokenTrackbar(),
          ],
        ),
      ),
    );
  }

  Widget _buildFuturisticPlaceholder() {
    return Column(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        AnimatedContainer(
          duration: const Duration(milliseconds: 600),
          width: _isPlaying ? 80 : 70,
          height: _isPlaying ? 80 : 70,
          decoration: BoxDecoration(
            shape: BoxShape.circle,
            color: const Color(0xFF8B5CF6).withOpacity(0.12),
            border: Border.all(
              color: const Color(0xFF8B5CF6).withOpacity(_isPlaying ? 0.6 : 0.2),
              width: 2,
            ),
          ),
          child: const Center(
            child: Text(
              '🤟',
              style: TextStyle(fontSize: 36),
            ),
          ),
        ),
        const SizedBox(height: 12),
        const Text(
          'Độ phân giải VSL 3D Offline',
          style: TextStyle(
            fontFamily: 'Outfit',
            fontSize: 12,
            fontWeight: FontWeight.w600,
            color: Colors.white54,
          ),
        ),
      ],
    );
  }

  Widget _buildTokenTrackbar() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.04),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        children: [
          const Text(
            'Tiến độ:',
            style: TextStyle(
              fontFamily: 'Outfit',
              fontSize: 12,
              color: Colors.white30,
            ),
          ),
          const SizedBox(width: 10),
          Expanded(
            child: SingleChildScrollView(
              scrollDirection: Axis.horizontal,
              child: Row(
                children: List.generate(_tokens.length, (index) {
                  final isPassed = index < _currentIndex;
                  final isCurrent = index == _currentIndex && _isPlaying;
                  
                  return Container(
                    margin: const EdgeInsets.only(right: 6),
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    decoration: BoxDecoration(
                      color: isCurrent
                          ? const Color(0xFF8B5CF6).withOpacity(0.2)
                          : isPassed
                              ? Colors.white.withOpacity(0.08)
                              : Colors.transparent,
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(
                        color: isCurrent
                            ? const Color(0xFF8B5CF6).withOpacity(0.5)
                            : isPassed
                                ? Colors.white.withOpacity(0.1)
                                : Colors.white.withOpacity(0.03),
                      ),
                    ),
                    child: Text(
                      _tokenLabels[_tokens[index]] ?? _tokens[index],
                      style: TextStyle(
                        fontFamily: 'Outfit',
                        fontSize: 11,
                        fontWeight: isCurrent || isPassed ? FontWeight.w600 : FontWeight.w400,
                        color: isCurrent
                            ? const Color(0xFFC4B5FD)
                            : isPassed
                                ? Colors.white70
                                : Colors.white24,
                      ),
                    ),
                  );
                }),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
