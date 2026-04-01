import 'package:flutter/material.dart';
import '../../../../core/services/social_service.dart';
import '../../../../core/services/service_locator.dart';
import '../../../../core/theme/glass_theme.dart';

/// ══════════════════════════════════════════════════════════════
/// MODERATION DASHBOARD — Admin panel for content moderation
/// GlassTheme version
/// ══════════════════════════════════════════════════════════════

class ModerationScreen extends StatefulWidget {
  const ModerationScreen({super.key});

  @override
  State<ModerationScreen> createState() => _ModerationScreenState();
}

class _ModerationScreenState extends State<ModerationScreen> {
  final _social = ServiceLocator.instance.social;

  List<CommunityPost> _pendingPosts = [];
  ModerationStats? _stats;
  bool _isLoading = true;
  int _currentTab = 0;

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    setState(() => _isLoading = true);
    final pending = await _social.getPendingPosts();
    final stats = await _social.getModerationStats();
    setState(() {
      _pendingPosts = pending;
      _stats = stats;
      _isLoading = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    return GlassTheme.scaffoldBackground(
      child: SafeArea(
        child: Column(
          children: [
            // App bar
            GlassTheme.appBar(
              title: 'Quản lý nội dung',
              showBackButton: true,
              onBack: () => Navigator.of(context).pop(),
            ),
            const SizedBox(height: 12),

            // Tab bar
            _buildTabBar(),
            const SizedBox(height: 16),

            // Content
            Expanded(
              child: _isLoading
                  ? GlassTheme.loadingIndicator()
                  : IndexedStack(
                      index: _currentTab,
                      children: [
                        _buildPendingTab(),
                        _buildStatsTab(),
                        _buildWarningsTab(),
                      ],
                    ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildTabBar() {
    final tabs = ['Chờ duyệt', 'Thống kê', 'Cảnh báo'];
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 20),
      child: Row(
        children: List.generate(tabs.length, (i) {
          final isSelected = _currentTab == i;
          return Expanded(
            child: GestureDetector(
              onTap: () => setState(() => _currentTab = i),
              child: AnimatedContainer(
                duration: const Duration(milliseconds: 200),
                padding: const EdgeInsets.symmetric(vertical: 10),
                margin: EdgeInsets.only(right: i < tabs.length - 1 ? 8 : 0),
                decoration: BoxDecoration(
                  color: isSelected
                      ? GlassTheme.primaryGreen.withValues(alpha: 0.2)
                      : GlassTheme.glassFill,
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(
                    color: isSelected
                        ? GlassTheme.primaryGreenLight.withValues(alpha: 0.5)
                        : GlassTheme.glassBorderLight,
                  ),
                ),
                child: Center(
                  child: Text(
                    tabs[i],
                    style: TextStyle(
                      fontFamily: 'Outfit',
                      fontSize: 13,
                      fontWeight:
                          isSelected ? FontWeight.w600 : FontWeight.w400,
                      color: isSelected
                          ? GlassTheme.primaryGreenLight
                          : GlassTheme.textMuted,
                    ),
                  ),
                ),
              ),
            ),
          );
        }),
      ),
    );
  }

  // ═══════════════════════════════════════════
  //  TAB: PENDING POSTS
  // ═══════════════════════════════════════════

  Widget _buildPendingTab() {
    if (_pendingPosts.isEmpty) {
      return GlassTheme.emptyState(
        emoji: '✅',
        title: 'Không có nội dung chờ duyệt',
        subtitle: 'Tất cả bài viết đã được xử lý',
      );
    }

    return ListView.builder(
      padding: const EdgeInsets.fromLTRB(20, 0, 20, 40),
      itemCount: _pendingPosts.length,
      itemBuilder: (context, index) {
        return _buildPendingCard(_pendingPosts[index]);
      },
    );
  }

  Widget _buildPendingCard(CommunityPost post) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: GlassTheme.glassCard(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Status + category
            Row(
              children: [
                Container(
                  padding:
                      const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(
                    color: post.status == PostStatus.pending
                        ? const Color(0xFFF59E0B).withValues(alpha: 0.15)
                        : const Color(0xFFEF4444).withValues(alpha: 0.15),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Text(
                    post.status == PostStatus.pending ? '⏳ Chờ duyệt' : '🚩 Bị flag',
                    style: TextStyle(
                      fontFamily: 'Outfit',
                      fontSize: 11,
                      fontWeight: FontWeight.w600,
                      color: post.status == PostStatus.pending
                          ? const Color(0xFFFBBF24)
                          : const Color(0xFFF87171),
                    ),
                  ),
                ),
                const Spacer(),
                Text('${post.category.emoji} ${post.category.label}',
                    style: GlassTheme.caption.copyWith(fontSize: 12)),
              ],
            ),

            const SizedBox(height: 12),

            // Content
            Text(
              post.content,
              maxLines: 4,
              overflow: TextOverflow.ellipsis,
              style: GlassTheme.body.copyWith(
                color: Colors.white.withValues(alpha: 0.9),
                fontSize: 14,
              ),
            ),

            const SizedBox(height: 8),

            // Tags
            if (post.tags.isNotEmpty)
              Wrap(
                spacing: 6,
                children: post.tags.map((t) => Text(
                      '#$t',
                      style: GlassTheme.caption.copyWith(fontSize: 11),
                    )).toList(),
              ),

            const SizedBox(height: 14),

            // Actions
            Row(
              children: [
                Expanded(
                  child: GestureDetector(
                    onTap: () => _rejectPost(post),
                    child: Container(
                      padding: const EdgeInsets.symmetric(vertical: 10),
                      decoration: BoxDecoration(
                        color: const Color(0xFFEF4444).withValues(alpha: 0.12),
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(
                            color: const Color(0xFFEF4444).withValues(alpha: 0.3)),
                      ),
                      child: const Center(
                        child: Text(
                          '✕ Từ chối',
                          style: TextStyle(
                            fontFamily: 'Outfit',
                            fontSize: 13,
                            fontWeight: FontWeight.w600,
                            color: Color(0xFFF87171),
                          ),
                        ),
                      ),
                    ),
                  ),
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: GestureDetector(
                    onTap: () => _approvePost(post),
                    child: Container(
                      padding: const EdgeInsets.symmetric(vertical: 10),
                      decoration: BoxDecoration(
                        color: GlassTheme.primaryGreen.withValues(alpha: 0.15),
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(
                            color: GlassTheme.primaryGreen.withValues(alpha: 0.4)),
                      ),
                      child: const Center(
                        child: Text(
                          '✓ Duyệt',
                          style: TextStyle(
                            fontFamily: 'Outfit',
                            fontSize: 13,
                            fontWeight: FontWeight.w600,
                            color: GlassTheme.primaryGreenLight,
                          ),
                        ),
                      ),
                    ),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  // ═══════════════════════════════════════════
  //  TAB: STATS
  // ═══════════════════════════════════════════

  Widget _buildStatsTab() {
    if (_stats == null) {
      return GlassTheme.emptyState(emoji: '📊', title: 'Không có dữ liệu');
    }

    return SingleChildScrollView(
      padding: const EdgeInsets.fromLTRB(20, 0, 20, 40),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Overview
          Row(
            children: [
              _glassStatCard('📝', 'Tổng bài', '${_stats!.totalPosts}',
                  const Color(0xFF2563EB)),
              const SizedBox(width: 10),
              _glassStatCard('⏳', 'Chờ duyệt', '${_stats!.pendingReview}',
                  const Color(0xFFF59E0B)),
            ],
          ),
          const SizedBox(height: 10),
          Row(
            children: [
              _glassStatCard('✅', 'Hôm nay duyệt', '${_stats!.approvedToday}',
                  GlassTheme.primaryGreen),
              const SizedBox(width: 10),
              _glassStatCard('❌', 'Hôm nay từ chối', '${_stats!.rejectedToday}',
                  const Color(0xFFEF4444)),
            ],
          ),

          const SizedBox(height: 24),

          // Flags
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
              Text('Loại vi phạm', style: GlassTheme.h3.copyWith(fontSize: 16)),
            ],
          ),
          const SizedBox(height: 12),

          ..._stats!.flagsByType.entries.map((entry) {
            return Padding(
              padding: const EdgeInsets.only(bottom: 8),
              child: GlassTheme.glassCard(
                padding:
                    const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                child: Row(
                  children: [
                    Text(_getFlagEmoji(entry.key),
                        style: const TextStyle(fontSize: 18)),
                    const SizedBox(width: 12),
                    Expanded(
                        child: Text(_getFlagLabel(entry.key),
                            style: GlassTheme.body
                                .copyWith(color: Colors.white, fontSize: 14))),
                    Container(
                      padding: const EdgeInsets.symmetric(
                          horizontal: 10, vertical: 4),
                      decoration: BoxDecoration(
                        color: GlassTheme.glassFillMedium,
                        borderRadius: BorderRadius.circular(10),
                      ),
                      child: Text(
                        '${entry.value}',
                        style: const TextStyle(
                          fontFamily: 'Outfit',
                          fontWeight: FontWeight.w700,
                          fontSize: 14,
                          color: Colors.white,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            );
          }),
        ],
      ),
    );
  }

  Widget _glassStatCard(
      String emoji, String title, String value, Color color) {
    return Expanded(
      child: GlassTheme.glassCard(
        padding: const EdgeInsets.all(14),
        fillColor: color.withValues(alpha: 0.08),
        borderColor: color.withValues(alpha: 0.2),
        child: Column(
          children: [
            Text(emoji, style: const TextStyle(fontSize: 24)),
            const SizedBox(height: 6),
            Text(
              value,
              style: TextStyle(
                fontFamily: 'Outfit',
                fontSize: 24,
                fontWeight: FontWeight.w800,
                color: color,
              ),
            ),
            Text(title,
                style: GlassTheme.caption.copyWith(fontSize: 11)),
          ],
        ),
      ),
    );
  }

  // ═══════════════════════════════════════════
  //  TAB: WARNINGS
  // ═══════════════════════════════════════════

  Widget _buildWarningsTab() {
    final warnings = _social.getActiveWarnings();
    if (warnings.isEmpty) {
      return GlassTheme.emptyState(
        emoji: '🛡️',
        title: 'Không có cảnh báo',
        subtitle: 'Hệ thống đang hoạt động bình thường',
      );
    }

    return ListView.builder(
      padding: const EdgeInsets.fromLTRB(20, 0, 20, 40),
      itemCount: warnings.length,
      itemBuilder: (context, index) => _buildWarningCard(warnings[index]),
    );
  }

  Widget _buildWarningCard(LegalWarning warning) {
    final color = _getWarningColor(warning.type);
    return Padding(
      padding: const EdgeInsets.only(bottom: 10),
      child: GlassTheme.glassCard(
        padding: const EdgeInsets.all(14),
        fillColor: color.withValues(alpha: 0.08),
        borderColor: color.withValues(alpha: 0.2),
        child: Row(
          children: [
            Text(_getWarningEmoji(warning.type),
                style: const TextStyle(fontSize: 22)),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    warning.title,
                    style: TextStyle(
                      fontFamily: 'Outfit',
                      fontWeight: FontWeight.w600,
                      fontSize: 14,
                      color: color,
                    ),
                  ),
                  const SizedBox(height: 2),
                  Text(
                    warning.message,
                    style: GlassTheme.caption.copyWith(fontSize: 12),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  // ═══════════════════════════════════════════
  //  ACTIONS
  // ═══════════════════════════════════════════

  Future<void> _approvePost(CommunityPost post) async {
    await _social.approvePost(post.id);
    _loadData();
    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: const Text('✅ Đã duyệt bài viết'),
          backgroundColor: const Color(0xFF0A2540),
          behavior: SnackBarBehavior.floating,
          shape:
              RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        ),
      );
    }
  }

  Future<void> _rejectPost(CommunityPost post) async {
    final reasonController = TextEditingController();

    final reason = await showDialog<String>(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: const Color(0xFF0A2540),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
        title: const Text(
          'Từ chối bài viết',
          style: TextStyle(
            fontFamily: 'Outfit',
            color: Colors.white,
            fontWeight: FontWeight.w700,
          ),
        ),
        content: Container(
          decoration: BoxDecoration(
            color: GlassTheme.glassFill,
            borderRadius: BorderRadius.circular(14),
            border: Border.all(color: GlassTheme.glassBorderLight),
          ),
          padding: const EdgeInsets.symmetric(horizontal: 14),
          child: TextField(
            controller: reasonController,
            style: GlassTheme.body.copyWith(color: Colors.white, fontSize: 14),
            decoration: InputDecoration(
              hintText: 'Nhập lý do từ chối...',
              hintStyle: GlassTheme.caption.copyWith(fontSize: 13),
              border: InputBorder.none,
            ),
            maxLines: 3,
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('Hủy',
                style: TextStyle(color: GlassTheme.textMuted)),
          ),
          TextButton(
            onPressed: () => Navigator.pop(ctx, reasonController.text),
            child: const Text('Từ chối',
                style: TextStyle(color: Color(0xFFF87171))),
          ),
        ],
      ),
    );

    if (reason != null && reason.isNotEmpty) {
      await _social.rejectPost(post.id, reason);
      _loadData();
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: const Text('❌ Đã từ chối bài viết'),
            backgroundColor: const Color(0xFF0A2540),
            behavior: SnackBarBehavior.floating,
            shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12)),
          ),
        );
      }
    }
  }

  // ═══════════════════════════════════════════
  //  HELPERS
  // ═══════════════════════════════════════════

  String _getFlagEmoji(ModerationFlagType type) {
    switch (type) {
      case ModerationFlagType.scam:
        return '🚨';
      case ModerationFlagType.spam:
        return '📢';
      case ModerationFlagType.pii:
        return '🔒';
      case ModerationFlagType.medicalClaim:
        return '💊';
      case ModerationFlagType.harassment:
        return '🚫';
      case ModerationFlagType.inappropriate:
        return '⚠️';
      case ModerationFlagType.protectedGroup:
        return '🛡️';
    }
  }

  String _getFlagLabel(ModerationFlagType type) {
    switch (type) {
      case ModerationFlagType.scam:
        return 'Lừa đảo';
      case ModerationFlagType.spam:
        return 'Spam';
      case ModerationFlagType.pii:
        return 'Thông tin cá nhân';
      case ModerationFlagType.medicalClaim:
        return 'Tuyên bố y tế';
      case ModerationFlagType.harassment:
        return 'Quấy rối';
      case ModerationFlagType.inappropriate:
        return 'Không phù hợp';
      case ModerationFlagType.protectedGroup:
        return 'Phân biệt đối xử';
    }
  }

  String _getWarningEmoji(WarningType type) {
    switch (type) {
      case WarningType.medicalDisclaimer:
        return '🏥';
      case WarningType.privacy:
        return '🔐';
      case WarningType.scam:
        return '🚨';
      case WarningType.communityGuideline:
        return '📋';
      case WarningType.emergency:
        return '🚑';
    }
  }

  Color _getWarningColor(WarningType type) {
    switch (type) {
      case WarningType.medicalDisclaimer:
        return const Color(0xFFF59E0B);
      case WarningType.privacy:
        return const Color(0xFF2563EB);
      case WarningType.scam:
        return const Color(0xFFEF4444);
      case WarningType.communityGuideline:
        return const Color(0xFF7C3AED);
      case WarningType.emergency:
        return const Color(0xFFEF4444);
    }
  }
}
