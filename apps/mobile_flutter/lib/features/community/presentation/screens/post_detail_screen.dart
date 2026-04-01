import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../../../../core/services/social_service.dart';
import '../../../../core/services/service_locator.dart';
import '../../../../core/theme/glass_theme.dart';

/// ══════════════════════════════════════════════════════════════
/// POST DETAIL SCREEN — Xem bài viết + bình luận
/// GlassTheme version with encouragement focus
/// ══════════════════════════════════════════════════════════════

class PostDetailScreen extends StatefulWidget {
  final String postId;

  const PostDetailScreen({super.key, required this.postId});

  @override
  State<PostDetailScreen> createState() => _PostDetailScreenState();
}

class _PostDetailScreenState extends State<PostDetailScreen> {
  final _social = ServiceLocator.instance.social;
  final _commentController = TextEditingController();

  CommunityPost? _post;
  List<Comment> _comments = [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  @override
  void dispose() {
    _commentController.dispose();
    super.dispose();
  }

  Future<void> _loadData() async {
    setState(() => _isLoading = true);

    final post = await _social.getPost(widget.postId);
    final comments = await _social.getComments(widget.postId);

    setState(() {
      _post = post;
      _comments = comments;
      _isLoading = false;
    });
  }

  Future<void> _addComment() async {
    if (_commentController.text.isEmpty) return;
    HapticFeedback.lightImpact();

    await _social.addComment(
      postId: widget.postId,
      content: _commentController.text,
      isAnonymous: true,
    );

    _commentController.clear();
    _loadData();
  }

  @override
  Widget build(BuildContext context) {
    return GlassTheme.scaffoldBackground(
      child: SafeArea(
        child: Column(
          children: [
            // App bar
            GlassTheme.appBar(
              title: 'Bài viết',
              showBackButton: true,
              onBack: () => Navigator.of(context).pop(),
            ),
            const SizedBox(height: 8),

            // Content
            Expanded(
              child: _isLoading
                  ? GlassTheme.loadingIndicator()
                  : _post == null
                      ? GlassTheme.emptyState(
                          emoji: '🔍',
                          title: 'Không tìm thấy bài viết',
                        )
                      : SingleChildScrollView(
                          padding: const EdgeInsets.fromLTRB(20, 0, 20, 20),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              // Post content card
                              _buildPostContent(),
                              const SizedBox(height: 20),

                              // Encouragement prompt
                              _buildEncouragementPrompt(),
                              const SizedBox(height: 20),

                              // Comments section
                              _buildCommentsSection(),
                            ],
                          ),
                        ),
            ),

            // Comment input
            if (_post != null) _buildCommentInput(),
          ],
        ),
      ),
    );
  }

  Widget _buildPostContent() {
    final post = _post!;

    return GlassTheme.glassCard(
      padding: const EdgeInsets.all(18),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Author row
          Row(
            children: [
              _buildAvatar(
                post.isAnonymous,
                post.isAnonymous ? '?' : (post.authorName?[0] ?? 'U'),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      post.isAnonymous
                          ? 'Ẩn danh'
                          : (post.authorName ?? 'Người dùng'),
                      style: const TextStyle(
                        fontFamily: 'Outfit',
                        fontWeight: FontWeight.w600,
                        fontSize: 15,
                        color: Colors.white,
                      ),
                    ),
                    Text(
                      _formatTime(post.createdAt),
                      style: GlassTheme.caption.copyWith(fontSize: 12),
                    ),
                  ],
                ),
              ),
              Container(
                padding:
                    const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
                decoration: BoxDecoration(
                  color: GlassTheme.glassFill,
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: GlassTheme.glassBorderLight),
                ),
                child: Text(
                  '${post.category.emoji} ${post.category.label}',
                  style: GlassTheme.caption.copyWith(fontSize: 11),
                ),
              ),
            ],
          ),

          const SizedBox(height: 16),

          // Content
          Text(
            post.content,
            style: GlassTheme.bodyLarge.copyWith(
              color: Colors.white.withOpacity(0.95),
              height: 1.6,
            ),
          ),

          // Medical disclaimer
          if (post.hasMedicalDisclaimer) ...[
            const SizedBox(height: 12),
            Container(
              padding: const EdgeInsets.all(10),
              decoration: BoxDecoration(
                color: const Color(0xFFF59E0B).withOpacity(0.1),
                borderRadius: BorderRadius.circular(10),
                border: Border.all(
                    color: const Color(0xFFF59E0B).withOpacity(0.2)),
              ),
              child: Row(
                children: [
                  Icon(Icons.info_outline,
                      color: const Color(0xFFF59E0B).withOpacity(0.8),
                      size: 16),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      'Nội dung mang tính tham khảo, không thay thế lời khuyên bác sĩ',
                      style: TextStyle(
                        fontFamily: 'Outfit',
                        fontSize: 11,
                        color: const Color(0xFFF59E0B).withOpacity(0.8),
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ],

          // Tags
          if (post.tags.isNotEmpty) ...[
            const SizedBox(height: 12),
            Wrap(
              spacing: 6,
              runSpacing: 4,
              children: post.tags.map((tag) {
                return Container(
                  padding:
                      const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                  decoration: BoxDecoration(
                    color: GlassTheme.glassFill,
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(color: GlassTheme.glassBorderLight),
                  ),
                  child: Text(
                    '#$tag',
                    style: GlassTheme.caption.copyWith(fontSize: 11),
                  ),
                );
              }).toList(),
            ),
          ],

          const SizedBox(height: 16),

          // Actions row
          Row(
            children: [
              _glassAction(
                icon: post.isLikedByUser
                    ? Icons.favorite
                    : Icons.favorite_border,
                label: '${post.likes}',
                color:
                    post.isLikedByUser ? const Color(0xFFEF4444) : null,
                onTap: () async {
                  HapticFeedback.lightImpact();
                  if (post.isLikedByUser) {
                    await _social.unlikePost(post.id);
                  } else {
                    await _social.likePost(post.id);
                  }
                  _loadData();
                },
              ),
              const SizedBox(width: 16),
              _glassAction(
                icon: post.isBookmarked
                    ? Icons.bookmark
                    : Icons.bookmark_border,
                label: 'Lưu',
                onTap: () async {
                  HapticFeedback.lightImpact();
                  if (post.isBookmarked) {
                    await _social.unbookmarkPost(post.id);
                  } else {
                    await _social.bookmarkPost(post.id);
                  }
                  _loadData();
                },
              ),
              const Spacer(),
              _glassAction(
                icon: Icons.flag_outlined,
                label: 'Báo cáo',
                onTap: _showReportDialog,
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildEncouragementPrompt() {
    return GlassTheme.glassCard(
      padding: const EdgeInsets.all(14),
      fillColor: const Color(0xFF0D9B6B).withOpacity(0.1),
      borderColor: const Color(0xFF0D9B6B).withOpacity(0.25),
      child: Row(
        children: [
          const Text('💬', style: TextStyle(fontSize: 20)),
          const SizedBox(width: 10),
          Expanded(
            child: Text(
              'Gửi lời động viên để tạo niềm vui cho mọi người!',
              style: GlassTheme.body.copyWith(
                color: GlassTheme.primaryGreenLight,
                fontSize: 13,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildCommentsSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Container(
              width: 4,
              height: 20,
              decoration: BoxDecoration(
                color: GlassTheme.primaryGreen,
                borderRadius: BorderRadius.circular(2),
              ),
            ),
            const SizedBox(width: 10),
            Text(
              'Bình luận (${_comments.length})',
              style: GlassTheme.h3.copyWith(fontSize: 16),
            ),
          ],
        ),
        const SizedBox(height: 14),

        if (_comments.isEmpty)
          const Center(
            child: Padding(
              padding: EdgeInsets.all(24),
              child: Text(
                'Chưa có bình luận nào — hãy là người đầu tiên! 💬',
                style: GlassTheme.body,
                textAlign: TextAlign.center,
              ),
            ),
          )
        else
          ..._comments.map(_buildCommentCard),
      ],
    );
  }

  Widget _buildCommentCard(Comment comment) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 10),
      child: GlassTheme.glassCard(
        padding: const EdgeInsets.all(14),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildAvatar(
              comment.isAnonymous,
              comment.isAnonymous ? '?' : (comment.authorName?[0] ?? 'U'),
              size: 34,
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Text(
                        comment.isAnonymous
                            ? 'Ẩn danh'
                            : (comment.authorName ?? 'Người dùng'),
                        style: const TextStyle(
                          fontFamily: 'Outfit',
                          fontWeight: FontWeight.w600,
                          fontSize: 13,
                          color: Colors.white,
                        ),
                      ),
                      const SizedBox(width: 8),
                      Text(
                        _formatTimeShort(comment.createdAt),
                        style: GlassTheme.caption.copyWith(fontSize: 11),
                      ),
                    ],
                  ),
                  const SizedBox(height: 4),
                  Text(
                    comment.content,
                    style: GlassTheme.body.copyWith(
                      color: Colors.white.withOpacity(0.9),
                      fontSize: 14,
                    ),
                  ),
                  const SizedBox(height: 6),
                  Row(
                    children: [
                      GestureDetector(
                        onTap: () async {
                          await _social.likeComment(comment.id);
                          _loadData();
                        },
                        child: Row(
                          children: [
                            Icon(
                              comment.isLikedByUser
                                  ? Icons.favorite
                                  : Icons.favorite_border,
                              size: 14,
                              color: comment.isLikedByUser
                                  ? const Color(0xFFEF4444)
                                  : GlassTheme.textMuted,
                            ),
                            const SizedBox(width: 4),
                            Text(
                              '${comment.likes}',
                              style:
                                  GlassTheme.caption.copyWith(fontSize: 11),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildCommentInput() {
    return Container(
      padding: const EdgeInsets.fromLTRB(20, 10, 20, 10),
      decoration: BoxDecoration(
        color: const Color(0xFF0A2540).withOpacity(0.95),
        border: const Border(
          top: BorderSide(color: GlassTheme.glassBorderLight, width: 0.5),
        ),
      ),
      child: SafeArea(
        top: false,
        child: Row(
          children: [
            _buildAvatar(true, '?', size: 34),
            const SizedBox(width: 10),
            Expanded(
              child: Container(
                padding: const EdgeInsets.symmetric(horizontal: 14),
                decoration: BoxDecoration(
                  color: GlassTheme.glassFill,
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(color: GlassTheme.glassBorderLight),
                ),
                child: TextField(
                  controller: _commentController,
                  style: GlassTheme.body.copyWith(
                    color: Colors.white,
                    fontSize: 14,
                  ),
                  decoration: InputDecoration(
                    hintText: 'Gửi lời động viên...',
                    hintStyle: GlassTheme.caption.copyWith(fontSize: 13),
                    border: InputBorder.none,
                    contentPadding:
                        const EdgeInsets.symmetric(vertical: 10),
                  ),
                  maxLines: null,
                ),
              ),
            ),
            const SizedBox(width: 8),
            GestureDetector(
              onTap: _addComment,
              child: Container(
                width: 40,
                height: 40,
                decoration: BoxDecoration(
                  color: GlassTheme.primaryGreen.withOpacity(0.2),
                  borderRadius: BorderRadius.circular(14),
                  border: Border.all(
                    color: GlassTheme.primaryGreen.withOpacity(0.4),
                  ),
                ),
                child: const Icon(
                  Icons.send_rounded,
                  size: 20,
                  color: GlassTheme.primaryGreenLight,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  // ═══════════════════════════════════════════
  //  HELPERS
  // ═══════════════════════════════════════════

  Widget _buildAvatar(bool isAnonymous, String initial, {double size = 40}) {
    final bgColor = isAnonymous
        ? GlassTheme.glassFillMedium
        : GlassTheme.primaryGreen.withOpacity(0.2);
    final textColor =
        isAnonymous ? GlassTheme.textMuted : GlassTheme.primaryGreenLight;

    return Container(
      width: size,
      height: size,
      decoration: BoxDecoration(
        color: bgColor,
        borderRadius: BorderRadius.circular(size * 0.35),
      ),
      child: Center(
        child: Text(
          initial,
          style: TextStyle(
            fontFamily: 'Outfit',
            fontSize: size * 0.4,
            fontWeight: FontWeight.w700,
            color: textColor,
          ),
        ),
      ),
    );
  }

  Widget _glassAction({
    required IconData icon,
    String? label,
    Color? color,
    required VoidCallback onTap,
  }) {
    return GestureDetector(
      onTap: onTap,
      child: Row(
        children: [
          Icon(icon, size: 20, color: color ?? GlassTheme.textMuted),
          if (label != null) ...[
            const SizedBox(width: 4),
            Text(
              label,
              style: TextStyle(
                fontFamily: 'Outfit',
                fontSize: 13,
                color: color ?? GlassTheme.textMuted,
              ),
            ),
          ],
        ],
      ),
    );
  }

  void _showReportDialog() {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: const Color(0xFF0A2540),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
        title: const Text(
          'Báo cáo vi phạm',
          style: TextStyle(
            fontFamily: 'Outfit',
            color: Colors.white,
            fontWeight: FontWeight.w700,
          ),
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: ReportType.values.map((type) {
            return ListTile(
              dense: true,
              title: Text(
                _getReportLabel(type),
                style: const TextStyle(
                  fontFamily: 'Outfit',
                  color: Colors.white70,
                  fontSize: 14,
                ),
              ),
              onTap: () async {
                await _social.reportPost(
                  postId: _post!.id,
                  type: type,
                  description: '',
                );
                if (ctx.mounted) {
                  Navigator.pop(ctx);
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(
                      content: const Text('Đã gửi báo cáo. Cảm ơn bạn!'),
                      backgroundColor: const Color(0xFF0A2540),
                      behavior: SnackBarBehavior.floating,
                      shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(12)),
                    ),
                  );
                }
              },
            );
          }).toList(),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('Hủy',
                style: TextStyle(color: GlassTheme.textMuted)),
          ),
        ],
      ),
    );
  }

  String _getReportLabel(ReportType type) {
    switch (type) {
      case ReportType.scam:
        return 'Lừa đảo';
      case ReportType.misinformation:
        return 'Thông tin sai';
      case ReportType.harassment:
        return 'Quấy rối';
      case ReportType.inappropriate:
        return 'Không phù hợp';
      case ReportType.privacy:
        return 'Vi phạm riêng tư';
      case ReportType.spam:
        return 'Spam';
      case ReportType.other:
        return 'Khác';
    }
  }

  String _formatTime(DateTime date) {
    final diff = DateTime.now().difference(date);
    if (diff.inMinutes < 60) return '${diff.inMinutes} phút trước';
    if (diff.inHours < 24) return '${diff.inHours} giờ trước';
    if (diff.inDays < 7) return '${diff.inDays} ngày trước';
    return '${date.day}/${date.month}/${date.year}';
  }

  String _formatTimeShort(DateTime date) {
    final diff = DateTime.now().difference(date);
    if (diff.inMinutes < 60) return '${diff.inMinutes}p';
    if (diff.inHours < 24) return '${diff.inHours}h';
    if (diff.inDays < 7) return '${diff.inDays}d';
    return '${date.day}/${date.month}';
  }
}
