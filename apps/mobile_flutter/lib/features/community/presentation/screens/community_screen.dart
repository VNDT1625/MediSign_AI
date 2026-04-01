import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../../../../core/services/social_service.dart';
import '../../../../core/services/service_locator.dart';
import '../../../../core/theme/glass_theme.dart';
import 'create_post_screen.dart';
import 'post_detail_screen.dart';
import 'group_chat_screen.dart';
import 'room_chat_screen.dart';

/// ══════════════════════════════════════════════════════════════
/// COMMUNITY SCREEN — Cộng đồng lạc quan
/// Tạo không gian chia sẻ tích cực, hỗ trợ tâm lý cho người
/// dùng cô đơn — hướng đến sức khỏe tinh thần.
/// ══════════════════════════════════════════════════════════════

class CommunityScreen extends StatefulWidget {
  const CommunityScreen({super.key});

  @override
  State<CommunityScreen> createState() => _CommunityScreenState();
}

class _CommunityScreenState extends State<CommunityScreen>
    with SingleTickerProviderStateMixin {
  final _social = ServiceLocator.instance.social;
  List<CommunityPost> _posts = [];
  List<ChatGroup> _groups = [];
  List<ChatRoom> _rooms = [];
  bool _isLoading = true;
  PostCategory? _selectedCategory;
  late AnimationController _shimmerCtrl;
  int _currentTab = 0; // 0=Feed, 1=Groups, 2=Rooms

  @override
  void initState() {
    super.initState();
    _shimmerCtrl = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 3),
    )..repeat();
    _loadPosts();
  }

  @override
  void dispose() {
    _shimmerCtrl.dispose();
    super.dispose();
  }

  Future<void> _loadPosts() async {
    setState(() => _isLoading = true);
    final posts = await _social.getFeed(
      category: _selectedCategory,
      page: 1,
      limit: 20,
    );
    final groups = await _social.getMyGroups();
    final rooms = await _social.getPublicRooms();
    setState(() {
      _posts = posts;
      _groups = groups;
      _rooms = rooms;
      _isLoading = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    return GlassTheme.scaffoldBackground(
      child: SafeArea(
        child: Column(
          children: [
            // ── HEADER ──
            _buildHeader(),

            // ── TABS: Bảng tin | Nhóm | Phòng ──
            _buildMainTabs(),
            const SizedBox(height: 8),

            // ── CONTENT ──
            Expanded(
              child: _isLoading
                  ? GlassTheme.loadingIndicator(
                      message: 'Đang tải cộng đồng...')
                  : IndexedStack(
                      index: _currentTab,
                      children: [
                        _buildFeedTab(),
                        _buildGroupsTab(),
                        _buildRoomsTab(),
                      ],
                    ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildMainTabs() {
    final tabs = ['📰 Bảng tin', '👥 Nhóm', '💬 Phòng'];
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
                      fontWeight: isSelected ? FontWeight.w600 : FontWeight.w400,
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

  Widget _buildFeedTab() {
    return RefreshIndicator(
      color: GlassTheme.primaryGreenLight,
      backgroundColor: const Color(0xFF0A2540),
      onRefresh: _loadPosts,
      child: ListView(
        padding: const EdgeInsets.fromLTRB(20, 8, 20, 100),
        children: [
          _buildAffirmationBanner(),
          const SizedBox(height: 20),
          _buildMoodCheckIn(),
          const SizedBox(height: 24),
          _buildCategoryFilter(),
          const SizedBox(height: 16),
          if (_posts.isEmpty)
            _buildEmptyState()
          else
            ..._posts.map(_buildPostCard),
          const SizedBox(height: 20),
          _buildLonelinessSupportSection(),
        ],
      ),
    );
  }

  // ═══════════════════════════════════════════
  //  GROUPS TAB
  // ═══════════════════════════════════════════

  Widget _buildGroupsTab() {
    return ListView(
      padding: const EdgeInsets.fromLTRB(20, 8, 20, 100),
      children: [
        // Create group button
        GestureDetector(
          onTap: _showCreateGroupDialog,
          child: GlassTheme.glassCard(
            padding: const EdgeInsets.all(14),
            fillColor: GlassTheme.primaryGreen.withValues(alpha: 0.08),
            borderColor: GlassTheme.primaryGreen.withValues(alpha: 0.2),
            child: Row(
              children: [
                Container(
                  width: 40,
                  height: 40,
                  decoration: BoxDecoration(
                    color: GlassTheme.primaryGreen.withValues(alpha: 0.2),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: const Icon(Icons.add_rounded, color: GlassTheme.primaryGreenLight),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text('Tạo nhóm mới',
                          style: TextStyle(
                            fontFamily: 'Outfit', fontSize: 15,
                            fontWeight: FontWeight.w600, color: GlassTheme.primaryGreenLight)),
                      Text('Chat riêng tư với bạn bè',
                          style: GlassTheme.caption.copyWith(fontSize: 12)),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ),
        const SizedBox(height: 16),

        // Group list
        if (_groups.isEmpty)
          GlassTheme.emptyState(
            emoji: '👥',
            title: 'Chưa có nhóm nào',
            subtitle: 'Tạo nhóm để trò chuyện cùng bạn bè!',
          )
        else
          ..._groups.map(_buildGroupCard),
      ],
    );
  }

  Widget _buildGroupCard(ChatGroup group) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 10),
      child: GestureDetector(
        onTap: () => Navigator.push(context,
          MaterialPageRoute(builder: (_) => GroupChatScreen(group: group))),
        child: GlassTheme.glassCard(
          padding: const EdgeInsets.all(14),
          child: Row(
            children: [
              Container(
                width: 48, height: 48,
                decoration: BoxDecoration(
                  color: GlassTheme.glassFillMedium,
                  borderRadius: BorderRadius.circular(14),
                ),
                child: Center(child: Text(group.avatarEmoji, style: const TextStyle(fontSize: 24))),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(group.name,
                        style: const TextStyle(fontFamily: 'Outfit', fontSize: 15,
                            fontWeight: FontWeight.w600, color: Colors.white)),
                    const SizedBox(height: 2),
                    if (group.lastMessage != null)
                      Text(group.lastMessage!,
                          maxLines: 1, overflow: TextOverflow.ellipsis,
                          style: GlassTheme.caption.copyWith(fontSize: 12)),
                    Text('${group.memberCount} thành viên',
                        style: GlassTheme.caption.copyWith(fontSize: 11)),
                  ],
                ),
              ),
              const Icon(Icons.chevron_right_rounded, color: GlassTheme.textMuted, size: 22),
            ],
          ),
        ),
      ),
    );
  }

  // ═══════════════════════════════════════════
  //  ROOMS TAB
  // ═══════════════════════════════════════════

  Widget _buildRoomsTab() {
    return ListView(
      padding: const EdgeInsets.fromLTRB(20, 8, 20, 100),
      children: [
        // Create room button
        GestureDetector(
          onTap: _showCreateRoomDialog,
          child: GlassTheme.glassCard(
            padding: const EdgeInsets.all(14),
            fillColor: const Color(0xFFF59E0B).withValues(alpha: 0.08),
            borderColor: const Color(0xFFF59E0B).withValues(alpha: 0.2),
            child: Row(
              children: [
                Container(
                  width: 40, height: 40,
                  decoration: BoxDecoration(
                    color: const Color(0xFFF59E0B).withValues(alpha: 0.2),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: const Icon(Icons.add_rounded, color: Color(0xFFFBBF24)),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text('Tạo phòng mới',
                          style: TextStyle(fontFamily: 'Outfit', fontSize: 15,
                              fontWeight: FontWeight.w600, color: Color(0xFFFBBF24))),
                      Text('Công khai — tự hủy khi hết người',
                          style: GlassTheme.caption.copyWith(fontSize: 12)),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ),
        const SizedBox(height: 16),

        // Room list
        if (_rooms.isEmpty)
          GlassTheme.emptyState(
            emoji: '💬',
            title: 'Không có phòng nào',
            subtitle: 'Tạo phòng để nói chuyện ngay!',
          )
        else
          ..._rooms.map(_buildRoomCard),
      ],
    );
  }

  Widget _buildRoomCard(ChatRoom room) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 10),
      child: GestureDetector(
        onTap: () async {
          await Navigator.push(context,
            MaterialPageRoute(builder: (_) => RoomChatScreen(room: room)));
          _loadPosts(); // Refresh rooms after returning
        },
        child: GlassTheme.glassCard(
          padding: const EdgeInsets.all(14),
          child: Row(
            children: [
              Container(
                width: 48, height: 48,
                decoration: BoxDecoration(
                  color: GlassTheme.glassFillMedium,
                  borderRadius: BorderRadius.circular(14),
                ),
                child: Center(child: Text(room.avatarEmoji, style: const TextStyle(fontSize: 24))),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(room.name,
                        style: const TextStyle(fontFamily: 'Outfit', fontSize: 15,
                            fontWeight: FontWeight.w600, color: Colors.white)),
                    if (room.topic.isNotEmpty)
                      Text(room.topic, maxLines: 1, overflow: TextOverflow.ellipsis,
                          style: GlassTheme.caption.copyWith(fontSize: 12)),
                    Text('by ${room.creatorNickname}',
                        style: GlassTheme.caption.copyWith(fontSize: 11)),
                  ],
                ),
              ),
              // Online badge
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                decoration: BoxDecoration(
                  color: GlassTheme.primaryGreen.withValues(alpha: 0.15),
                  borderRadius: BorderRadius.circular(10),
                ),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Container(
                      width: 6, height: 6,
                      decoration: const BoxDecoration(
                        shape: BoxShape.circle,
                        color: GlassTheme.primaryGreenLight,
                      ),
                    ),
                    const SizedBox(width: 4),
                    Text('${room.memberCount}',
                        style: const TextStyle(fontFamily: 'Outfit', fontSize: 12,
                            fontWeight: FontWeight.w600, color: GlassTheme.primaryGreenLight)),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  // ═══════════════════════════════════════════
  //  CREATE DIALOGS
  // ═══════════════════════════════════════════

  void _showCreateGroupDialog() {
    final nameCtrl = TextEditingController();
    final descCtrl = TextEditingController();
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: const Color(0xFF0A2540),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
        title: const Text('Tạo nhóm mới',
            style: TextStyle(fontFamily: 'Outfit', color: Colors.white, fontWeight: FontWeight.w700)),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            _dialogTextField(nameCtrl, 'Tên nhóm'),
            const SizedBox(height: 10),
            _dialogTextField(descCtrl, 'Mô tả (tùy chọn)'),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('Hủy', style: TextStyle(color: GlassTheme.textMuted)),
          ),
          TextButton(
            onPressed: () async {
              if (nameCtrl.text.isNotEmpty) {
                await _social.createGroup(name: nameCtrl.text, description: descCtrl.text);
                if (ctx.mounted) Navigator.pop(ctx);
                _loadPosts();
              }
            },
            child: const Text('Tạo', style: TextStyle(color: GlassTheme.primaryGreenLight)),
          ),
        ],
      ),
    );
  }

  void _showCreateRoomDialog() {
    final nameCtrl = TextEditingController();
    final topicCtrl = TextEditingController();
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: const Color(0xFF0A2540),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
        title: const Text('Tạo phòng mới',
            style: TextStyle(fontFamily: 'Outfit', color: Colors.white, fontWeight: FontWeight.w700)),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            _dialogTextField(nameCtrl, 'Tên phòng'),
            const SizedBox(height: 10),
            _dialogTextField(topicCtrl, 'Chủ đề (tùy chọn)'),
            const SizedBox(height: 8),
            Text('⚡ Phòng sẽ tự hủy khi tất cả rời đi',
                style: GlassTheme.caption.copyWith(fontSize: 11)),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('Hủy', style: TextStyle(color: GlassTheme.textMuted)),
          ),
          TextButton(
            onPressed: () async {
              if (nameCtrl.text.isNotEmpty) {
                await _social.createRoom(name: nameCtrl.text, topic: topicCtrl.text);
                if (ctx.mounted) Navigator.pop(ctx);
                _loadPosts();
              }
            },
            child: const Text('Tạo', style: TextStyle(color: Color(0xFFFBBF24))),
          ),
        ],
      ),
    );
  }

  Widget _dialogTextField(TextEditingController ctrl, String hint) {
    return Container(
      decoration: BoxDecoration(
        color: GlassTheme.glassFill,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: GlassTheme.glassBorderLight),
      ),
      padding: const EdgeInsets.symmetric(horizontal: 14),
      child: TextField(
        controller: ctrl,
        style: GlassTheme.body.copyWith(color: Colors.white, fontSize: 14),
        decoration: InputDecoration(
          hintText: hint,
          hintStyle: GlassTheme.caption.copyWith(fontSize: 13),
          border: InputBorder.none,
        ),
      ),
    );
  }

  // ═══════════════════════════════════════════
  //  HEADER
  // ═══════════════════════════════════════════

  Widget _buildHeader() {
    final profile = _social.getCurrentProfile();
    return Padding(
      padding: const EdgeInsets.fromLTRB(20, 12, 20, 8),
      child: Row(
        children: [
          Container(
            width: 40,
            height: 40,
            decoration: BoxDecoration(
              color: GlassTheme.primaryGreen.withValues(alpha: 0.2),
              borderRadius: BorderRadius.circular(14),
            ),
            child: Center(
              child: Text(profile.avatarEmoji,
                  style: const TextStyle(fontSize: 22)),
            ),
          ),
          const SizedBox(width: 10),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text('Cộng đồng lạc quan', style: GlassTheme.h2),
                Text(
                  '${profile.nickname} • ${profile.displayId}',
                  style: GlassTheme.caption,
                ),
              ],
            ),
          ),
          GlassTheme.glassIconButton(
            icon: Icons.add_rounded,
            onPressed: _openCreatePost,
            tooltip: 'Đăng bài mới',
          ),
        ],
      ),
    );
  }

  // ═══════════════════════════════════════════
  //  DAILY AFFIRMATION BANNER
  // ═══════════════════════════════════════════

  Widget _buildAffirmationBanner() {
    final affirmation = _social.getDailyAffirmation();

    return AnimatedBuilder(
      animation: _shimmerCtrl,
      builder: (context, child) {
        final shimmerValue = _shimmerCtrl.value;
        return GlassTheme.glassCard(
          padding: const EdgeInsets.all(20),
          fillColor: Color.lerp(
            const Color(0xFFF59E0B).withOpacity(0.12),
            const Color(0xFFEF4444).withOpacity(0.08),
            (shimmerValue * 2 - 1).abs(),
          ),
          borderColor: const Color(0xFFF59E0B).withOpacity(0.3),
          child: child!,
        );
      },
      child: Column(
        children: [
          Row(
            children: [
              const Text('✨', style: TextStyle(fontSize: 20)),
              const SizedBox(width: 8),
              Text(
                'Lời nhắn hôm nay',
                style: GlassTheme.label.copyWith(
                  color: const Color(0xFFFBBF24),
                  letterSpacing: 1,
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Text(
            affirmation,
            style: GlassTheme.bodyLarge.copyWith(
              fontWeight: FontWeight.w600,
              height: 1.6,
            ),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  // ═══════════════════════════════════════════
  //  MOOD CHECK-IN
  // ═══════════════════════════════════════════

  Widget _buildMoodCheckIn() {
    return GlassTheme.glassCard(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Text('💭', style: TextStyle(fontSize: 18)),
              const SizedBox(width: 8),
              Text(
                'Hôm nay bạn cảm thấy thế nào?',
                style: GlassTheme.h3.copyWith(fontSize: 15),
              ),
            ],
          ),
          const SizedBox(height: 14),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: [
              _moodButton('😢', 'Buồn'),
              _moodButton('😟', 'Lo lắng'),
              _moodButton('😐', 'Bình thường'),
              _moodButton('🙂', 'Vui'),
              _moodButton('😊', 'Tuyệt vời'),
            ],
          ),
        ],
      ),
    );
  }

  Widget _moodButton(String emoji, String label) {
    return GestureDetector(
      onTap: () {
        HapticFeedback.lightImpact();
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('$emoji Cảm ơn bạn đã chia sẻ!'),
            backgroundColor: const Color(0xFF0A2540),
            behavior: SnackBarBehavior.floating,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(12),
            ),
          ),
        );
      },
      child: Column(
        children: [
          Container(
            width: 52,
            height: 52,
            decoration: BoxDecoration(
              color: GlassTheme.glassFillLight,
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: GlassTheme.glassBorderLight),
            ),
            child: Center(
              child: Text(emoji, style: const TextStyle(fontSize: 28)),
            ),
          ),
          const SizedBox(height: 6),
          Text(
            label,
            style: GlassTheme.caption.copyWith(fontSize: 11),
          ),
        ],
      ),
    );
  }

  // ═══════════════════════════════════════════
  //  CATEGORY FILTER
  // ═══════════════════════════════════════════

  Widget _buildCategoryFilter() {
    final categories = [
      null, // "All"
      PostCategory.gratitude,
      PostCategory.encouragement,
      PostCategory.emotionalSupport,
      PostCategory.lifestyleTips,
      PostCategory.healthShare,
      PostCategory.question,
      PostCategory.general,
    ];

    return SizedBox(
      height: 40,
      child: ListView.separated(
        scrollDirection: Axis.horizontal,
        itemCount: categories.length,
        separatorBuilder: (_, __) => const SizedBox(width: 8),
        itemBuilder: (context, index) {
          final cat = categories[index];
          final isSelected = _selectedCategory == cat;
          final label =
              cat == null ? 'Tất cả' : '${cat.emoji} ${cat.label}';

          return GestureDetector(
            onTap: () {
              HapticFeedback.selectionClick();
              setState(() => _selectedCategory = cat);
              _loadPosts();
            },
            child: AnimatedContainer(
              duration: const Duration(milliseconds: 200),
              padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
              decoration: BoxDecoration(
                color: isSelected
                    ? GlassTheme.primaryGreen.withOpacity(0.25)
                    : GlassTheme.glassFill,
                borderRadius: BorderRadius.circular(20),
                border: Border.all(
                  color: isSelected
                      ? GlassTheme.primaryGreenLight.withOpacity(0.5)
                      : GlassTheme.glassBorderLight,
                ),
              ),
              child: Text(
                label,
                style: TextStyle(
                  fontFamily: 'Outfit',
                  fontSize: 13,
                  fontWeight: isSelected ? FontWeight.w600 : FontWeight.w400,
                  color: isSelected
                      ? GlassTheme.primaryGreenLight
                      : GlassTheme.textSecondary,
                ),
              ),
            ),
          );
        },
      ),
    );
  }

  // ═══════════════════════════════════════════
  //  POST FEED
  // ═══════════════════════════════════════════

  Widget _buildEmptyState() {
    return GlassTheme.emptyState(
      emoji: '🌱',
      title: 'Chưa có bài viết nào',
      subtitle: 'Hãy là người đầu tiên chia sẻ điều tích cực!',
      action: GlassTheme.primaryButton(
        text: 'Chia sẻ ngay',
        icon: Icons.add_rounded,
        onPressed: _openCreatePost,
        height: 48,
      ),
    );
  }

  Widget _buildPostCard(CommunityPost post) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 14),
      child: GestureDetector(
        onTap: () => _openPostDetail(post),
        child: GlassTheme.glassCard(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Author row
              Row(
                children: [
                  _buildAvatar(post),
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
                            fontSize: 14,
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
                  _buildCategoryBadge(post.category),
                ],
              ),

              const SizedBox(height: 12),

              // Content
              Text(
                post.content,
                maxLines: 4,
                overflow: TextOverflow.ellipsis,
                style: GlassTheme.body.copyWith(
                  color: Colors.white.withOpacity(0.9),
                  height: 1.5,
                ),
              ),

              // Tags
              if (post.tags.isNotEmpty) ...[
                const SizedBox(height: 10),
                Wrap(
                  spacing: 6,
                  runSpacing: 4,
                  children: post.tags.map((tag) {
                    return Container(
                      padding: const EdgeInsets.symmetric(
                          horizontal: 10, vertical: 4),
                      decoration: BoxDecoration(
                        color: GlassTheme.glassFill,
                        borderRadius: BorderRadius.circular(12),
                        border:
                            Border.all(color: GlassTheme.glassBorderLight),
                      ),
                      child: Text(
                        '#$tag',
                        style: GlassTheme.caption.copyWith(fontSize: 11),
                      ),
                    );
                  }).toList(),
                ),
              ],

              // Medical disclaimer
              if (post.hasMedicalDisclaimer) ...[
                const SizedBox(height: 10),
                Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: const Color(0xFFF59E0B).withOpacity(0.1),
                    borderRadius: BorderRadius.circular(10),
                    border: Border.all(
                      color: const Color(0xFFF59E0B).withOpacity(0.2),
                    ),
                  ),
                  child: Row(
                    children: [
                      Icon(Icons.info_outline,
                          size: 14,
                          color: const Color(0xFFF59E0B).withOpacity(0.8)),
                      const SizedBox(width: 6),
                      Expanded(
                        child: Text(
                          'Tham khảo, không thay thế lời khuyên bác sĩ',
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

              const SizedBox(height: 12),

              // Actions row
              Row(
                children: [
                  _actionChip(
                    icon: post.isLikedByUser
                        ? Icons.favorite
                        : Icons.favorite_border,
                    label: '${post.likes}',
                    color: post.isLikedByUser
                        ? const Color(0xFFEF4444)
                        : null,
                    onTap: () => _toggleLike(post),
                  ),
                  const SizedBox(width: 12),
                  _actionChip(
                    icon: Icons.chat_bubble_outline,
                    label: '${post.commentsCount}',
                    onTap: () => _openPostDetail(post),
                  ),
                  const Spacer(),
                  _actionChip(
                    icon: post.isBookmarked
                        ? Icons.bookmark
                        : Icons.bookmark_border,
                    onTap: () => _toggleBookmark(post),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildAvatar(CommunityPost post) {
    final bgColor = post.isAnonymous
        ? GlassTheme.glassFillMedium
        : GlassTheme.primaryGreen.withOpacity(0.2);
    final textColor = post.isAnonymous
        ? GlassTheme.textMuted
        : GlassTheme.primaryGreenLight;

    return Container(
      width: 40,
      height: 40,
      decoration: BoxDecoration(
        color: bgColor,
        borderRadius: BorderRadius.circular(14),
      ),
      child: Center(
        child: Text(
          post.isAnonymous ? '?' : (post.authorName?[0] ?? 'U'),
          style: TextStyle(
            fontFamily: 'Outfit',
            fontSize: 16,
            fontWeight: FontWeight.w700,
            color: textColor,
          ),
        ),
      ),
    );
  }

  Widget _buildCategoryBadge(PostCategory category) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: GlassTheme.glassFill,
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: GlassTheme.glassBorderLight),
      ),
      child: Text(
        category.emoji,
        style: const TextStyle(fontSize: 14),
      ),
    );
  }

  Widget _actionChip({
    required IconData icon,
    String? label,
    Color? color,
    required VoidCallback onTap,
  }) {
    return GestureDetector(
      onTap: () {
        HapticFeedback.lightImpact();
        onTap();
      },
      child: Row(
        children: [
          Icon(
            icon,
            size: 20,
            color: color ?? GlassTheme.textMuted,
          ),
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

  // ═══════════════════════════════════════════
  //  LONELINESS SUPPORT SECTION
  // ═══════════════════════════════════════════

  Widget _buildLonelinessSupportSection() {
    final resources = _social.getMoodSupportResources();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Section header
        Row(
          children: [
            Container(
              width: 4,
              height: 20,
              decoration: BoxDecoration(
                color: const Color(0xFFF59E0B),
                borderRadius: BorderRadius.circular(2),
              ),
            ),
            const SizedBox(width: 10),
            Text(
              'Bạn cần hỗ trợ?',
              style: GlassTheme.h3.copyWith(fontSize: 16),
            ),
          ],
        ),
        const SizedBox(height: 6),
        Text(
          'Bạn không đơn độc — chúng tôi ở đây cùng bạn',
          style: GlassTheme.caption.copyWith(fontSize: 13),
        ),
        const SizedBox(height: 14),

        // Support resource cards
        ...resources.map((resource) => Padding(
              padding: const EdgeInsets.only(bottom: 10),
              child: GlassTheme.glassCard(
                padding:
                    const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
                fillColor: const Color(0xFF7C3AED).withOpacity(0.08),
                borderColor: const Color(0xFF7C3AED).withOpacity(0.2),
                child: Row(
                  children: [
                    Container(
                      width: 42,
                      height: 42,
                      decoration: BoxDecoration(
                        color: const Color(0xFF7C3AED).withOpacity(0.15),
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: Center(
                        child: Text(resource.emoji,
                            style: const TextStyle(fontSize: 22)),
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            resource.title,
                            style: const TextStyle(
                              fontFamily: 'Outfit',
                              fontSize: 14,
                              fontWeight: FontWeight.w600,
                              color: Colors.white,
                            ),
                          ),
                          const SizedBox(height: 2),
                          Text(
                            resource.description,
                            style: GlassTheme.caption.copyWith(fontSize: 12),
                          ),
                        ],
                      ),
                    ),
                    if (resource.phoneNumber != null)
                      Icon(Icons.phone_rounded,
                          size: 20,
                          color: const Color(0xFFA78BFA).withOpacity(0.7)),
                    if (resource.url != null)
                      Icon(Icons.open_in_new_rounded,
                          size: 20,
                          color: const Color(0xFFA78BFA).withOpacity(0.7)),
                  ],
                ),
              ),
            )),
      ],
    );
  }

  // ═══════════════════════════════════════════
  //  NAVIGATION HELPERS
  // ═══════════════════════════════════════════

  void _openCreatePost() {
    HapticFeedback.mediumImpact();
    Navigator.of(context).push(
      MaterialPageRoute(builder: (_) => const CreatePostScreen()),
    );
  }

  void _openPostDetail(CommunityPost post) {
    Navigator.of(context).push(
      MaterialPageRoute(builder: (_) => PostDetailScreen(postId: post.id)),
    );
  }

  Future<void> _toggleLike(CommunityPost post) async {
    if (post.isLikedByUser) {
      await _social.unlikePost(post.id);
    } else {
      await _social.likePost(post.id);
    }
    _loadPosts();
  }

  Future<void> _toggleBookmark(CommunityPost post) async {
    if (post.isBookmarked) {
      await _social.unbookmarkPost(post.id);
    } else {
      await _social.bookmarkPost(post.id);
    }
    _loadPosts();
  }

  String _formatTime(DateTime date) {
    final diff = DateTime.now().difference(date);
    if (diff.inMinutes < 60) return '${diff.inMinutes} phút trước';
    if (diff.inHours < 24) return '${diff.inHours} giờ trước';
    if (diff.inDays < 7) return '${diff.inDays} ngày trước';
    return '${date.day}/${date.month}/${date.year}';
  }
}
