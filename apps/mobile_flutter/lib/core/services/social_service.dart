import 'dart:async';

/// ══════════════════════════════════════════════════════════════
/// SOCIAL SERVICE — Community features with moderation & safety
/// ══════════════════════════════════════════════════════════════
///
/// Features:
/// - Anonymous posting with optional condition tags
/// - Content moderation (AI + manual review queue)
/// - Legal warnings about medical adviceDisclaimer
/// - Privacy protection (no personal info exposure)
/// - Report system for harmful content
/// - Community engagement (likes, comments)
/// - Admin dashboard for moderators
///
/// Safety measures:
/// - Medical disclaimer required on all health posts
/// - No personal identifiable information (PII) detection
/// - Scam/fraud warning system
/// - Age-appropriate content filtering

/// ══════════════════════════════════════════════════════════════
/// MODELS
/// ══════════════════════════════════════════════════════════════

/// Content categories for community posts
enum PostCategory {
  general,
  healthShare,
  treatmentExperience,
  emotionalSupport,
  lifestyleTips,
  question,
  gratitude,
  encouragement,
}

/// Extension for PostCategory
extension PostCategoryX on PostCategory {
  String get label {
    switch (this) {
      case PostCategory.general:
        return 'Chung';
      case PostCategory.healthShare:
        return 'Chia sẻ sức khỏe';
      case PostCategory.treatmentExperience:
        return 'Kinh nghiệm điều trị';
      case PostCategory.emotionalSupport:
        return 'Hỗ trợ tâm lý';
      case PostCategory.lifestyleTips:
        return 'Mẹo sinh hoạt';
      case PostCategory.question:
        return 'Hỏi đáp';
      case PostCategory.gratitude:
        return 'Biết ơn';
      case PostCategory.encouragement:
        return 'Động viên';
    }
  }

  String get emoji {
    switch (this) {
      case PostCategory.general:
        return '💬';
      case PostCategory.healthShare:
        return '💊';
      case PostCategory.treatmentExperience:
        return '🏥';
      case PostCategory.emotionalSupport:
        return '💛';
      case PostCategory.lifestyleTips:
        return '🌿';
      case PostCategory.question:
        return '❓';
      case PostCategory.gratitude:
        return '🙏';
      case PostCategory.encouragement:
        return '💪';
    }
  }

  bool get requiresMedicalDisclaimer {
    return this == PostCategory.healthShare ||
        this == PostCategory.treatmentExperience ||
        this == PostCategory.question;
  }
}

/// Post status for moderation workflow
enum PostStatus {
  pending, // Awaiting AI moderation
  approved, // Approved and visible
  rejected, // Rejected (with reason)
  flagged, // Flagged for manual review
  hidden, // Temporarily hidden
}

/// Moderation result from AI/rule-based check
class ModerationResult {
  final bool isApproved;
  final List<ModerationFlag> flags;
  final String? rejectionReason;
  final double? spamScore;
  final double? scamScore;

  const ModerationResult({
    required this.isApproved,
    this.flags = const [],
    this.rejectionReason,
    this.spamScore,
    this.scamScore,
  });

  bool get needsManualReview =>
      flags.any((f) => f.severity == ModerationSeverity.high);
}

/// Types of moderation flags
enum ModerationFlagType {
  spam,
  scam,
  pii, // Personal Identifiable Information
  medicalClaim, // Unverified medical claim
  harassment,
  inappropriate,
  protectedGroup, // Hate speech targeting protected groups
}

/// Severity levels for flags
enum ModerationSeverity {
  low,
  medium,
  high,
  critical,
}

/// A single moderation flag
class ModerationFlag {
  final ModerationFlagType type;
  final ModerationSeverity severity;
  final String message;
  final String? suggestion;

  const ModerationFlag({
    required this.type,
    required this.severity,
    required this.message,
    this.suggestion,
  });
}

/// A community post
class CommunityPost {
  final String id;
  final String authorId;
  final String? authorName; // Can be anonymous
  final bool isAnonymous;
  final String content;
  final PostCategory category;
  final List<String> tags;
  final DateTime createdAt;
  final DateTime? updatedAt;
  final PostStatus status;
  final int likes;
  final int commentsCount;
  final bool isLikedByUser;
  final bool isBookmarked;
  final bool hasMedicalDisclaimer;

  const CommunityPost({
    required this.id,
    required this.authorId,
    this.authorName,
    required this.isAnonymous,
    required this.content,
    required this.category,
    this.tags = const [],
    required this.createdAt,
    this.updatedAt,
    required this.status,
    this.likes = 0,
    this.commentsCount = 0,
    this.isLikedByUser = false,
    this.isBookmarked = false,
    this.hasMedicalDisclaimer = false,
  });

  CommunityPost copyWith({
    String? id,
    String? authorId,
    String? authorName,
    bool? isAnonymous,
    String? content,
    PostCategory? category,
    List<String>? tags,
    DateTime? createdAt,
    DateTime? updatedAt,
    PostStatus? status,
    int? likes,
    int? commentsCount,
    bool? isLikedByUser,
    bool? isBookmarked,
    bool? hasMedicalDisclaimer,
  }) {
    return CommunityPost(
      id: id ?? this.id,
      authorId: authorId ?? this.authorId,
      authorName: authorName ?? this.authorName,
      isAnonymous: isAnonymous ?? this.isAnonymous,
      content: content ?? this.content,
      category: category ?? this.category,
      tags: tags ?? this.tags,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
      status: status ?? this.status,
      likes: likes ?? this.likes,
      commentsCount: commentsCount ?? this.commentsCount,
      isLikedByUser: isLikedByUser ?? this.isLikedByUser,
      isBookmarked: isBookmarked ?? this.isBookmarked,
      hasMedicalDisclaimer: hasMedicalDisclaimer ?? this.hasMedicalDisclaimer,
    );
  }
}

/// A comment on a post
class Comment {
  final String id;
  final String postId;
  final String authorId;
  final String? authorName;
  final bool isAnonymous;
  final String content;
  final DateTime createdAt;
  final int likes;
  final bool isLikedByUser;

  const Comment({
    required this.id,
    required this.postId,
    required this.authorId,
    this.authorName,
    required this.isAnonymous,
    required this.content,
    required this.createdAt,
    this.likes = 0,
    this.isLikedByUser = false,
  });

  Comment copyWith({
    String? id,
    String? postId,
    String? authorId,
    String? authorName,
    bool? isAnonymous,
    String? content,
    DateTime? createdAt,
    int? likes,
    bool? isLikedByUser,
  }) {
    return Comment(
      id: id ?? this.id,
      postId: postId ?? this.postId,
      authorId: authorId ?? this.authorId,
      authorName: authorName ?? this.authorName,
      isAnonymous: isAnonymous ?? this.isAnonymous,
      content: content ?? this.content,
      createdAt: createdAt ?? this.createdAt,
      likes: likes ?? this.likes,
      isLikedByUser: isLikedByUser ?? this.isLikedByUser,
    );
  }
}

/// Report types
enum ReportType {
  scam,
  misinformation,
  harassment,
  inappropriate,
  privacy,
  spam,
  other,
}

/// A user report
class Report {
  final String id;
  final String postId;
  final String reporterId;
  final ReportType type;
  final String description;
  final DateTime createdAt;
  final bool isResolved;

  const Report({
    required this.id,
    required this.postId,
    required this.reporterId,
    required this.type,
    required this.description,
    required this.createdAt,
    this.isResolved = false,
  });
}

/// Moderation dashboard stats
class ModerationStats {
  final int totalPosts;
  final int pendingReview;
  final int approvedToday;
  final int rejectedToday;
  final int flaggedContent;
  final Map<ModerationFlagType, int> flagsByType;

  const ModerationStats({
    required this.totalPosts,
    required this.pendingReview,
    required this.approvedToday,
    required this.rejectedToday,
    required this.flaggedContent,
    required this.flagsByType,
  });
}

/// Legal warning messages
class LegalWarning {
  final String id;
  final String title;
  final String message;
  final WarningType type;
  final bool isDismissible;
  final DateTime? expiresAt;

  const LegalWarning({
    required this.id,
    required this.title,
    required this.message,
    required this.type,
    this.isDismissible = true,
    this.expiresAt,
  });
}

enum WarningType {
  medicalDisclaimer,
  privacy,
  scam,
  communityGuideline,
  emergency,
}

/// Mental wellness support resource
class MoodSupportResource {
  final String emoji;
  final String title;
  final String description;
  final String? phoneNumber;
  final String? url;

  const MoodSupportResource({
    required this.emoji,
    required this.title,
    required this.description,
    this.phoneNumber,
    this.url,
  });
}

/// Community profile — anonymous identity on the platform
class CommunityProfile {
  final String id;           // unique internal ID
  final String displayId;    // visible short code e.g. #LQ2024
  final String nickname;     // user-chosen display name
  final String avatarEmoji;  // emoji avatar e.g. 🌸
  final DateTime joinedAt;
  final int postCount;
  final int friendCount;

  const CommunityProfile({
    required this.id,
    required this.displayId,
    required this.nickname,
    required this.avatarEmoji,
    required this.joinedAt,
    this.postCount = 0,
    this.friendCount = 0,
  });
}

/// Message type for chat
enum MessageType { text, system, emoji }

/// Chat group — persistent private group
class ChatGroup {
  final String id;
  final String name;
  final String description;
  final String avatarEmoji;
  final String creatorId;
  final List<String> memberIds;
  final DateTime createdAt;
  final String? lastMessage;
  final DateTime? lastMessageAt;
  final int memberCount;

  const ChatGroup({
    required this.id,
    required this.name,
    this.description = '',
    this.avatarEmoji = '👥',
    required this.creatorId,
    this.memberIds = const [],
    required this.createdAt,
    this.lastMessage,
    this.lastMessageAt,
    this.memberCount = 0,
  });
}

/// Chat room — temporary public room, destroyed when empty
class ChatRoom {
  final String id;
  final String name;
  final String topic;
  final String avatarEmoji;
  final String creatorId;
  final String creatorNickname;
  final DateTime createdAt;
  final int memberCount;
  final int maxMembers;
  final bool isActive; // false when everyone leaves

  const ChatRoom({
    required this.id,
    required this.name,
    this.topic = '',
    this.avatarEmoji = '💬',
    required this.creatorId,
    this.creatorNickname = 'Ẩn danh',
    required this.createdAt,
    this.memberCount = 0,
    this.maxMembers = 50,
    this.isActive = true,
  });
}

/// Chat message — used for both Group and Room
class ChatMessage {
  final String id;
  final String chatId; // groupId or roomId
  final String senderId;
  final String senderNickname;
  final String senderEmoji;
  final String content;
  final DateTime createdAt;
  final MessageType type;

  const ChatMessage({
    required this.id,
    required this.chatId,
    required this.senderId,
    required this.senderNickname,
    this.senderEmoji = '🌸',
    required this.content,
    required this.createdAt,
    this.type = MessageType.text,
  });
}

/// ══════════════════════════════════════════════════════════════
/// SOCIAL SERVICE INTERFACE
/// ══════════════════════════════════════════════════════════════

abstract class SocialService {
  /// Initialize the service
  Future<bool> initialize();

  /// Whether the service is ready
  bool get isReady;

  // ─── POSTS ───

  /// Create a new post (goes through moderation first)
  Future<CommunityPost> createPost({
    required String content,
    required PostCategory category,
    List<String> tags = const [],
    bool isAnonymous = true,
    bool includeMedicalDisclaimer = false,
  });

  /// Get feed of approved posts
  Future<List<CommunityPost>> getFeed({
    PostCategory? category,
    int page = 1,
    int limit = 20,
  });

  /// Get a single post by ID
  Future<CommunityPost?> getPost(String postId);

  /// Delete own post
  Future<void> deletePost(String postId);

  // ─── INTERACTIONS ───

  /// Like a post
  Future<void> likePost(String postId);

  /// Unlike a post
  Future<void> unlikePost(String postId);

  /// Bookmark a post
  Future<void> bookmarkPost(String postId);

  /// Remove bookmark
  Future<void> unbookmarkPost(String postId);

  // ─── COMMENTS ───

  /// Get comments for a post
  Future<List<Comment>> getComments(String postId);

  /// Add a comment
  Future<Comment> addComment({
    required String postId,
    required String content,
    bool isAnonymous = true,
  });

  /// Delete own comment
  Future<void> deleteComment(String commentId);

  /// Like a comment
  Future<void> likeComment(String commentId);

  // ─── REPORTING ───

  /// Report a post
  Future<void> reportPost({
    required String postId,
    required ReportType type,
    required String description,
  });

  // ─── MODERATION (Admin) ───

  /// Get posts pending review
  Future<List<CommunityPost>> getPendingPosts();

  /// Approve a post
  Future<void> approvePost(String postId);

  /// Reject a post with reason
  Future<void> rejectPost(String postId, String reason);

  /// Get moderation dashboard stats
  Future<ModerationStats> getModerationStats();

  // ─── SAFETY ───

  /// Get active legal warnings
  List<LegalWarning> getActiveWarnings();

  /// Dismiss a warning
  Future<void> dismissWarning(String warningId);

  /// Check content before posting (preview moderation result)
  Future<ModerationResult> previewModeration(String content);

  // ─── COMMUNITY PROFILE ───

  /// Get current user's community profile
  CommunityProfile getCurrentProfile();

  // ─── MENTAL WELLNESS ───

  /// Get daily affirmation message
  String getDailyAffirmation();

  /// Get mood support resources (hotlines, articles)
  List<MoodSupportResource> getMoodSupportResources();

  // ─── USER CONTENT ───

  /// Get user's own posts
  Future<List<CommunityPost>> getMyPosts();

  /// Get bookmarked posts
  Future<List<CommunityPost>> getBookmarkedPosts();

  // ─── GROUP CHAT ───

  /// Get groups the current user belongs to
  Future<List<ChatGroup>> getMyGroups();

  /// Create a new group
  Future<ChatGroup> createGroup({
    required String name,
    String description,
    String avatarEmoji,
  });

  /// Get messages in a group
  Future<List<ChatMessage>> getGroupMessages(String groupId);

  /// Send a message in a group
  Future<ChatMessage> sendGroupMessage({
    required String groupId,
    required String content,
  });

  /// Invite a user to a group by their display ID
  Future<bool> inviteToGroup(String groupId, String displayId);

  /// Leave a group
  Future<void> leaveGroup(String groupId);

  // ─── ROOM CHAT ───

  /// Get all active public rooms
  Future<List<ChatRoom>> getPublicRooms();

  /// Create a new public room
  Future<ChatRoom> createRoom({
    required String name,
    String topic,
    String avatarEmoji,
    int maxMembers,
  });

  /// Join a room
  Future<bool> joinRoom(String roomId);

  /// Leave a room (if last person → room is destroyed)
  Future<void> leaveRoom(String roomId);

  /// Get messages in a room
  Future<List<ChatMessage>> getRoomMessages(String roomId);

  /// Send a message in a room
  Future<ChatMessage> sendRoomMessage({
    required String roomId,
    required String content,
  });

  /// Dispose resources
  void dispose();
}

/// ══════════════════════════════════════════════════════════════
///
// MOCK IMPLEMENTATION — Replace with RealSocialService later
///
/// This includes:
/// - Rule-based content moderation
/// - Sample data for testing
/// - Simulated async operations
/// ══════════════════════════════════════════════════════════════

class MockSocialService implements SocialService {
  bool _isReady = false;
  final List<CommunityPost> _posts = [];
  final List<Comment> _comments = [];
  final List<Report> _reports = [];
  final List<LegalWarning> _warnings = [];
  final Set<String> _likedPosts = {};
  final Set<String> _bookmarkedPosts = {};
  final Set<String> _likedComments = {};

  final CommunityProfile _currentProfile = CommunityProfile(
    id: 'current_user',
    displayId: '#LQ2024',
    nickname: 'Người lạc quan',
    avatarEmoji: '🌸',
    joinedAt: DateTime(2024, 1, 15),
    postCount: 12,
    friendCount: 5,
  );

  // ─── PII DETECTION PATTERNS ───
  static final _piiPatterns = [
    RegExp(r'\b\d{9,12}\b'), // Phone numbers
    RegExp(r'\b[\w.-]+@[\w.-]+\.\w+\b'), // Emails
    RegExp(r'\b\d{1,2}/\d{1,2}/\d{2,4}\b'), // Dates (DOB)
    RegExp(r'(?:địa chỉ|addr|address)[:\s]+', caseSensitive: false),
    RegExp(r'(?:số CMND|số CCCD|số passport)[:\s]+', caseSensitive: false),
  ];

  // ─── SCAM PATTERNS ───
  static final _scamPatterns = [
    RegExp(r'(?:mua|ban|đặt)[\s]+(thuốc|thuoc)[\s]+(?:online|trực tuyến)',
        caseSensitive: false),
    RegExp(r'chữa khỏi', caseSensitive: false),
    RegExp(r'tuyệt đối|100%', caseSensitive: false),
    RegExp(r'(?:gian lận|lừa đảo|scam)', caseSensitive: false),
    RegExp(r'(?:đảm bảo|guarantee)[\s]+(?:hiệu quả|ket qua)',
        caseSensitive: false),
    RegExp(r'không cần[\s]+(?:bác sĩ|bac si)', caseSensitive: false),
  ];

  // ─── MEDICAL CLAIM PATTERNS ───
  static final _medicalClaimPatterns = [
    RegExp(r'(?:chữa|trị|điều trị)[\s]+(?:khỏi|het)', caseSensitive: false),
    RegExp(r'(?:thuốc|thuoc)[\s]+(?:duy nhất|best|top 1)',
        caseSensitive: false),
    RegExp(r'(?:bệnh ung thư|ung thư|cancer)[\s]+(?:khỏi|het)',
        caseSensitive: false),
  ];

  @override
  bool get isReady => _isReady;

  @override
  Future<bool> initialize() async {
    // Seed sample data
    _seedSampleData();
    _initWarnings();
    await Future.delayed(const Duration(milliseconds: 300));
    _isReady = true;
    return true;
  }

  void _initWarnings() {
    _warnings.addAll([
      const LegalWarning(
        id: 'medical_disclaimer_1',
        title: 'Cảnh báo y tế',
        message:
            'Nội dung trên chỉ mang tính chất tham khảo. Không thay thế lời khuyên của bác sĩ. Luôn consult chuyên gia y tế trước khi áp dụng.',
        type: WarningType.medicalDisclaimer,
      ),
      const LegalWarning(
        id: 'privacy_warning_1',
        title: 'Bảo mật thông tin',
        message:
            'KHÔNG chia sẻ thông tin cá nhân như số điện thoại, địa chỉ, CMND/CCCD trên diễn đàn. Chúng tôi không chịu trách nhiệm về việc lộ thông tin.',
        type: WarningType.privacy,
      ),
      const LegalWarning(
        id: 'scam_warning_1',
        title: 'Cảnh báo lừa đảo',
        message:
            'CẢNH BÁO: Không mua thuốc/treatment từ nguồn không rõ. Không chuyển tiền cho người lạ. Báo cáo ngay nếu phát hiện hành vi lừa đảo.',
        type: WarningType.scam,
      ),
    ]);
  }

  void _seedSampleData() {
    final now = DateTime.now();

    _posts.addAll([
      CommunityPost(
        id: 'post_1',
        authorId: 'user_1',
        authorName: 'Người chia sẻ',
        isAnonymous: true,
        content:
            'Mình đã chiến thắng bệnh tiểu đường type 2 sau 6 tháng thay đổi lối sống. Ăn uống lành mạnh, tập thể dục đều đặn mỗi ngày. Quan trọng là kiên trì! 💪',
        category: PostCategory.treatmentExperience,
        tags: ['tiểu đường', 'lối sống', 'type 2'],
        createdAt: now.subtract(const Duration(hours: 2)),
        status: PostStatus.approved,
        likes: 45,
        commentsCount: 12,
        hasMedicalDisclaimer: true,
      ),
      CommunityPost(
        id: 'post_2',
        authorId: 'user_2',
        isAnonymous: true,
        content:
            'Ai bị mất ngủ như mình không? Đã thử nhiều cách mà không hiệu quả. Có ai có kinh nghiệm gì chia sẻ được không? 😔',
        category: PostCategory.question,
        tags: ['mất ngủ', 'giấc ngủ'],
        createdAt: now.subtract(const Duration(hours: 5)),
        status: PostStatus.approved,
        likes: 23,
        commentsCount: 8,
        hasMedicalDisclaimer: false,
      ),
      CommunityPost(
        id: 'post_3',
        authorId: 'user_3',
        authorName: 'Người điều trị',
        isAnonymous: false,
        content:
            'Hôm nay đi khám định kỳ, bác sĩ nói sức khỏe đã tốt hơn rất nhiều! 🥰 Cảm ơn mọi người đã động viên trong thời gian qua.',
        category: PostCategory.healthShare,
        tags: ['sức khỏe', 'khám định kỳ'],
        createdAt: now.subtract(const Duration(days: 1)),
        status: PostStatus.approved,
        likes: 67,
        commentsCount: 15,
        hasMedicalDisclaimer: true,
      ),
      CommunityPost(
        id: 'post_4',
        authorId: 'user_4',
        isAnonymous: true,
        content:
            'Mẹo nhỏ: Uống nước ấm pha chanh mật ong mỗi sáng giúp cải thiện hệ tiêu hóa rất tốt! Mình áp dụng thấy hiệu quả.',
        category: PostCategory.lifestyleTips,
        tags: ['sức khỏe', 'mẹo hay', 'nước chanh'],
        createdAt: now.subtract(const Duration(days: 1, hours: 3)),
        status: PostStatus.approved,
        likes: 89,
        commentsCount: 20,
        hasMedicalDisclaimer: false,
      ),
      CommunityPost(
        id: 'post_5',
        authorId: 'user_5',
        isAnonymous: true,
        content:
            'Hôm nay mình cảm thấy cô đơn quá. Ai online chat cùng mình được không? 💛',
        category: PostCategory.emotionalSupport,
        tags: ['cô đơn', 'tâm sự'],
        createdAt: now.subtract(const Duration(hours: 8)),
        status: PostStatus.approved,
        likes: 34,
        commentsCount: 25,
        hasMedicalDisclaimer: false,
      ),
      // ─── POSITIVE / GRATITUDE POSTS ───
      CommunityPost(
        id: 'post_7',
        authorId: 'user_7',
        authorName: 'Người lạc quan',
        isAnonymous: false,
        content:
            'Hôm nay mình biết ơn vì được thức dậy, được nhìn thấy ánh nắng buổi sáng. Những điều nhỏ nhặt nhưng thật sự quý giá 🌅✨',
        category: PostCategory.gratitude,
        tags: ['biết ơn', 'lạc quan', 'ngày mới'],
        createdAt: now.subtract(const Duration(hours: 1)),
        status: PostStatus.approved,
        likes: 72,
        commentsCount: 18,
        hasMedicalDisclaimer: false,
      ),
      CommunityPost(
        id: 'post_8',
        authorId: 'user_8',
        isAnonymous: true,
        content:
            'Gửi đến bạn đang đọc dòng này: Bạn thật mạnh mẽ! Dù hôm nay có khó khăn thế nào, bạn đã vượt qua rồi đó 💪🌈',
        category: PostCategory.encouragement,
        tags: ['động viên', 'mạnh mẽ', 'hy vọng'],
        createdAt: now.subtract(const Duration(hours: 3)),
        status: PostStatus.approved,
        likes: 156,
        commentsCount: 42,
        hasMedicalDisclaimer: false,
      ),
      CommunityPost(
        id: 'post_9',
        authorId: 'user_9',
        authorName: 'Bạn đồng hành',
        isAnonymous: false,
        content:
            'Mình từng trải qua giai đoạn rất cô đơn, nhưng nhờ cộng đồng này mình cảm thấy ấm lòng hơn. Cảm ơn mọi người đã lắng nghe và chia sẻ 🤗💛',
        category: PostCategory.emotionalSupport,
        tags: ['cô đơn', 'cộng đồng', 'chia sẻ'],
        createdAt: now.subtract(const Duration(hours: 6)),
        status: PostStatus.approved,
        likes: 98,
        commentsCount: 35,
        hasMedicalDisclaimer: false,
      ),
      CommunityPost(
        id: 'post_10',
        authorId: 'user_10',
        isAnonymous: true,
        content:
            '3 điều mình biết ơn hôm nay:\n1. Được ăn bữa cơm ngon với gia đình 🍚\n2. Con mèo nhà hàng xóm chạy qua chơi 🐱\n3. Trời hôm nay thật đẹp ☀️\nBạn có muốn chia sẻ 3 điều bạn biết ơn không?',
        category: PostCategory.gratitude,
        tags: ['biết ơn', '3 điều tốt đẹp'],
        createdAt: now.subtract(const Duration(days: 1, hours: 1)),
        status: PostStatus.approved,
        likes: 134,
        commentsCount: 56,
        hasMedicalDisclaimer: false,
      ),
      // Pending post for moderation demo
      CommunityPost(
        id: 'post_6',
        authorId: 'user_6',
        isAnonymous: false,
        content:
            'Mua thuốc chữa bệnh xương khớp giá rẻ liên hệ ZALO: 0912345678',
        category: PostCategory.general,
        tags: ['thuốc'],
        createdAt: now.subtract(const Duration(minutes: 30)),
        status: PostStatus.pending,
        likes: 0,
        commentsCount: 0,
        hasMedicalDisclaimer: false,
      ),
    ]);

    // Sample comments
    _comments.addAll([
      Comment(
        id: 'comment_1',
        postId: 'post_2',
        authorId: 'user_7',
        isAnonymous: true,
        content:
            'Mình cũng bị từng đó. Bạn thử tập yoga hoặc thiền xem? Mình thấy có giảm đi phần nào.',
        createdAt: now.subtract(const Duration(hours: 4)),
        likes: 5,
      ),
      Comment(
        id: 'comment_2',
        postId: 'post_2',
        authorId: 'user_8',
        authorName: 'Bác sĩ tình nguyện',
        isAnonymous: false,
        content:
            'Mất ngủ kéo dài cần khám chuyên khoa. Bạn nên đặt lịch với bác sĩ để được tư vấn cụ thể nhé.',
        createdAt: now.subtract(const Duration(hours: 3)),
        likes: 12,
      ),
    ]);
  }

  // ─── POSTS ───

  @override
  Future<CommunityPost> createPost({
    required String content,
    required PostCategory category,
    List<String> tags = const [],
    bool isAnonymous = true,
    bool includeMedicalDisclaimer = false,
  }) async {
    // Run moderation first
    final moderationResult = await previewModeration(content);

    final now = DateTime.now();
    final post = CommunityPost(
      id: 'post_${now.millisecondsSinceEpoch}',
      authorId: 'current_user',
      authorName: isAnonymous ? null : 'User',
      isAnonymous: isAnonymous,
      content: content,
      category: category,
      tags: tags,
      createdAt: now,
      status: moderationResult.isApproved
          ? PostStatus.approved
          : PostStatus.flagged,
      hasMedicalDisclaimer:
          includeMedicalDisclaimer || category.requiresMedicalDisclaimer,
    );

    _posts.insert(0, post);
    return post;
  }

  @override
  Future<List<CommunityPost>> getFeed({
    PostCategory? category,
    int page = 1,
    int limit = 20,
  }) async {
    await Future.delayed(const Duration(milliseconds: 200));

    var filtered = _posts.where((p) => p.status == PostStatus.approved);

    if (category != null) {
      filtered = filtered.where((p) => p.category == category);
    }

    final start = (page - 1) * limit;
    final end = start + limit;

    if (start >= filtered.length) return [];

    return filtered
        .toList()
        .sublist(
          start,
          end.clamp(0, filtered.length),
        )
        .map((p) => p.copyWith(
              isLikedByUser: _likedPosts.contains(p.id),
              isBookmarked: _bookmarkedPosts.contains(p.id),
            ))
        .toList();
  }

  @override
  Future<CommunityPost?> getPost(String postId) async {
    final post = _posts.cast<CommunityPost?>().firstWhere(
          (p) => p!.id == postId,
          orElse: () => null,
        );
    if (post == null) return null;
    return post.copyWith(
      isLikedByUser: _likedPosts.contains(post.id),
      isBookmarked: _bookmarkedPosts.contains(post.id),
    );
  }

  @override
  Future<void> deletePost(String postId) async {
    _posts.removeWhere((p) => p.id == postId && p.authorId == 'current_user');
  }

  // ─── INTERACTIONS ───

  @override
  Future<void> likePost(String postId) async {
    _likedPosts.add(postId);
    final index = _posts.indexWhere((p) => p.id == postId);
    if (index != -1) {
      _posts[index] = _posts[index].copyWith(
        likes: _posts[index].likes + 1,
      );
    }
  }

  @override
  Future<void> unlikePost(String postId) async {
    _likedPosts.remove(postId);
    final index = _posts.indexWhere((p) => p.id == postId);
    if (index != -1) {
      _posts[index] = _posts[index].copyWith(
        likes: _posts[index].likes - 1,
      );
    }
  }

  @override
  Future<void> bookmarkPost(String postId) async {
    _bookmarkedPosts.add(postId);
  }

  @override
  Future<void> unbookmarkPost(String postId) async {
    _bookmarkedPosts.remove(postId);
  }

  // ─── COMMENTS ───

  @override
  Future<List<Comment>> getComments(String postId) async {
    return _comments
        .where((c) => c.postId == postId)
        .map((c) => c.copyWith(
              isLikedByUser: _likedComments.contains(c.id),
            ))
        .toList();
  }

  @override
  Future<Comment> addComment({
    required String postId,
    required String content,
    bool isAnonymous = true,
  }) async {
    final comment = Comment(
      id: 'comment_${DateTime.now().millisecondsSinceEpoch}',
      postId: postId,
      authorId: 'current_user',
      isAnonymous: isAnonymous,
      content: content,
      createdAt: DateTime.now(),
    );
    _comments.add(comment);

    // Update comment count
    final postIndex = _posts.indexWhere((p) => p.id == postId);
    if (postIndex != -1) {
      _posts[postIndex] = _posts[postIndex].copyWith(
        commentsCount: _posts[postIndex].commentsCount + 1,
      );
    }

    return comment;
  }

  @override
  Future<void> deleteComment(String commentId) async {
    final comment = _comments.cast<Comment?>().firstWhere(
          (c) => c!.id == commentId,
          orElse: () => null,
        );
    if (comment != null) {
      _comments.remove(comment);
      final postIndex = _posts.indexWhere((p) => p.id == comment.postId);
      if (postIndex != -1) {
        _posts[postIndex] = _posts[postIndex].copyWith(
          commentsCount: _posts[postIndex].commentsCount - 1,
        );
      }
    }
  }

  @override
  Future<void> likeComment(String commentId) async {
    _likedComments.add(commentId);
    final index = _comments.indexWhere((c) => c.id == commentId);
    if (index != -1) {
      _comments[index] = _comments[index].copyWith(
        likes: _comments[index].likes + 1,
      );
    }
  }

  // ─── REPORTING ───

  @override
  Future<void> reportPost({
    required String postId,
    required ReportType type,
    required String description,
  }) async {
    final report = Report(
      id: 'report_${DateTime.now().millisecondsSinceEpoch}',
      postId: postId,
      reporterId: 'current_user',
      type: type,
      description: description,
      createdAt: DateTime.now(),
    );
    _reports.add(report);

    // Flag the post for review
    final index = _posts.indexWhere((p) => p.id == postId);
    if (index != -1) {
      _posts[index] = _posts[index].copyWith(status: PostStatus.flagged);
    }
  }

  // ─── MODERATION ───

  @override
  Future<List<CommunityPost>> getPendingPosts() async {
    return _posts
        .where((p) =>
            p.status == PostStatus.pending || p.status == PostStatus.flagged)
        .toList();
  }

  @override
  Future<void> approvePost(String postId) async {
    final index = _posts.indexWhere((p) => p.id == postId);
    if (index != -1) {
      _posts[index] = _posts[index].copyWith(status: PostStatus.approved);
    }
  }

  @override
  Future<void> rejectPost(String postId, String reason) async {
    final index = _posts.indexWhere((p) => p.id == postId);
    if (index != -1) {
      _posts[index] = _posts[index].copyWith(status: PostStatus.rejected);
    }
  }

  @override
  Future<ModerationStats> getModerationStats() async {
    final now = DateTime.now();
    final today = DateTime(now.year, now.month, now.day);

    return ModerationStats(
      totalPosts: _posts.length,
      pendingReview: _posts
          .where((p) =>
              p.status == PostStatus.pending || p.status == PostStatus.flagged)
          .length,
      approvedToday: _posts
          .where((p) =>
              p.status == PostStatus.approved && p.createdAt.isAfter(today))
          .length,
      rejectedToday: _posts
          .where((p) =>
              p.status == PostStatus.rejected && p.createdAt.isAfter(today))
          .length,
      flaggedContent:
          _posts.where((p) => p.status == PostStatus.flagged).length,
      flagsByType: {
        ModerationFlagType.scam: 2,
        ModerationFlagType.pii: 1,
        ModerationFlagType.spam: 3,
      },
    );
  }

  // ─── SAFETY ───

  @override
  List<LegalWarning> getActiveWarnings() {
    return List.unmodifiable(_warnings);
  }

  @override
  Future<void> dismissWarning(String warningId) async {
    // In real implementation, track dismissed warnings per user
  }

  @override
  Future<ModerationResult> previewModeration(String content) async {
    final flags = <ModerationFlag>[];

    // Check for PII
    for (final pattern in _piiPatterns) {
      if (pattern.hasMatch(content)) {
        flags.add(const ModerationFlag(
          type: ModerationFlagType.pii,
          severity: ModerationSeverity.high,
          message: 'Phát hiện thông tin cá nhân trong nội dung',
          suggestion: 'Vui lòng không chia sẻ SĐT, email, CMND hoặc địa chỉ',
        ));
        break;
      }
    }

    // Check for scam patterns
    for (final pattern in _scamPatterns) {
      if (pattern.hasMatch(content)) {
        flags.add(const ModerationFlag(
          type: ModerationFlagType.scam,
          severity: ModerationSeverity.critical,
          message: 'Nội dung có dấu hiệu lừa đảo hoặc bán hàng trái phép',
          suggestion: 'Nội dung này sẽ được duyệt thủ công',
        ));
        break;
      }
    }

    // Check for unverified medical claims
    for (final pattern in _medicalClaimPatterns) {
      if (pattern.hasMatch(content)) {
        flags.add(const ModerationFlag(
          type: ModerationFlagType.medicalClaim,
          severity: ModerationSeverity.medium,
          message: 'Phát hiện tuyên bố y tế chưa được xác minh',
          suggestion:
              'Thêm disclaimer: "Theo kinh nghiệm cá nhân, cần tham khảo bác sĩ"',
        ));
        break;
      }
    }

    // Auto-approve if no high/critical flags
    final hasBlockingFlag = flags.any((f) =>
        f.severity == ModerationSeverity.high ||
        f.severity == ModerationSeverity.critical);

    return ModerationResult(
      isApproved: !hasBlockingFlag,
      flags: flags,
      rejectionReason: hasBlockingFlag ? flags.first.message : null,
    );
  }

  // ─── USER CONTENT ───

  @override
  Future<List<CommunityPost>> getMyPosts() async {
    return _posts.where((p) => p.authorId == 'current_user').toList();
  }

  @override
  Future<List<CommunityPost>> getBookmarkedPosts() async {
    return _posts.where((p) => _bookmarkedPosts.contains(p.id)).toList();
  }

  // ─── COMMUNITY PROFILE ───

  @override
  CommunityProfile getCurrentProfile() => _currentProfile;

  // ─── MENTAL WELLNESS ───

  static const _affirmations = [
    'Bạn không đơn độc. Chúng tôi ở đây cùng bạn 💛',
    'Mỗi ngày là một cơ hội mới để yêu thương bản thân 🌸',
    'Bạn xứng đáng được hạnh phúc và yêu thương 🌈',
    'Từng bước nhỏ cũng là tiến bộ. Hãy tự hào về mình! 🌟',
    'Hít thở sâu. Bạn đang làm rất tốt rồi 🍃',
    'Cô đơn chỉ là tạm thời. Kết nối đang chờ bạn ở đây 🤝',
    'Mỉm cười đi — bạn có sức mạnh hơn bạn nghĩ 💪',
    'Hôm nay, hãy dành 1 phút để nói "Cảm ơn" với bản thân 🙏',
    'Bạn là ánh sáng cho ai đó. Đừng quên điều đó ✨',
    'Chia sẻ là cách tuyệt vời để chữa lành. Bạn sẵn sàng chưa? 🌻',
    'Mỗi khoảnh khắc đau buồn sẽ qua — hãy kiên nhẫn với chính mình 🦋',
    'Bạn không cần phải hoàn hảo. Bạn chỉ cần là chính bạn 💕',
  ];

  @override
  String getDailyAffirmation() {
    final dayOfYear = DateTime.now().difference(
      DateTime(DateTime.now().year, 1, 1),
    ).inDays;
    return _affirmations[dayOfYear % _affirmations.length];
  }

  @override
  List<MoodSupportResource> getMoodSupportResources() {
    return const [
      MoodSupportResource(
        emoji: '📞',
        title: 'Đường dây tư vấn tâm lý',
        description: 'Tổng đài tư vấn sức khỏe tâm thần quốc gia',
        phoneNumber: '1800-599-920',
      ),
      MoodSupportResource(
        emoji: '🏥',
        title: 'Tư vấn tâm lý trực tuyến',
        description: 'Nói chuyện với chuyên gia tâm lý ngay',
        url: 'https://www.tuvantamly.vn',
      ),
      MoodSupportResource(
        emoji: '🧘',
        title: 'Bài tập thở & thiền',
        description: 'Giảm stress với bài tập hít thở 4-7-8',
      ),
      MoodSupportResource(
        emoji: '💬',
        title: 'Cộng đồng hỗ trợ',
        description: 'Chia sẻ và lắng nghe — bạn không đơn độc',
      ),
    ];
  }

  // ─── GROUP CHAT ───

  final List<ChatGroup> _groups = [
    ChatGroup(
      id: 'g1',
      name: 'Hội những người lạc quan',
      description: 'Chia sẻ niềm vui mỗi ngày',
      avatarEmoji: '🌻',
      creatorId: 'user_2',
      memberIds: ['current_user', 'user_2', 'user_3'],
      createdAt: DateTime.now().subtract(const Duration(days: 30)),
      lastMessage: 'Hôm nay mình đi bộ 5km! 💪',
      lastMessageAt: DateTime.now().subtract(const Duration(hours: 2)),
      memberCount: 3,
    ),
    ChatGroup(
      id: 'g2',
      name: 'Đồng hành trị liệu',
      description: 'Chia sẻ kinh nghiệm điều trị',
      avatarEmoji: '💊',
      creatorId: 'current_user',
      memberIds: ['current_user', 'user_4'],
      createdAt: DateTime.now().subtract(const Duration(days: 14)),
      lastMessage: 'Cảm ơn mọi người đã lắng nghe 🙏',
      lastMessageAt: DateTime.now().subtract(const Duration(hours: 5)),
      memberCount: 2,
    ),
  ];

  final List<ChatRoom> _rooms = [
    ChatRoom(
      id: 'r1',
      name: 'Góc tâm sự đêm khuya',
      topic: 'Nơi chia sẻ khi không ngủ được',
      avatarEmoji: '🌙',
      creatorId: 'user_5',
      creatorNickname: 'Ánh trăng',
      createdAt: DateTime.now().subtract(const Duration(hours: 1)),
      memberCount: 8,
    ),
    ChatRoom(
      id: 'r2',
      name: 'Cùng nhau vượt qua',
      topic: 'Động viên và chia sẻ giải pháp',
      avatarEmoji: '🤝',
      creatorId: 'user_6',
      creatorNickname: 'Bạn đồng hành',
      createdAt: DateTime.now().subtract(const Duration(minutes: 30)),
      memberCount: 4,
    ),
    ChatRoom(
      id: 'r3',
      name: 'Thiền và hít thở',
      topic: 'Thực hành mindfulness cùng nhau',
      avatarEmoji: '🧘',
      creatorId: 'user_7',
      creatorNickname: 'An nhiên',
      createdAt: DateTime.now().subtract(const Duration(minutes: 10)),
      memberCount: 12,
    ),
  ];

  final Map<String, List<ChatMessage>> _chatMessages = {};

  @override
  Future<List<ChatGroup>> getMyGroups() async {
    await Future.delayed(const Duration(milliseconds: 200));
    return List.unmodifiable(_groups);
  }

  @override
  Future<ChatGroup> createGroup({
    required String name,
    String description = '',
    String avatarEmoji = '👥',
  }) async {
    final group = ChatGroup(
      id: 'g_${DateTime.now().millisecondsSinceEpoch}',
      name: name,
      description: description,
      avatarEmoji: avatarEmoji,
      creatorId: 'current_user',
      memberIds: ['current_user'],
      createdAt: DateTime.now(),
      memberCount: 1,
    );
    _groups.add(group);
    _chatMessages[group.id] = [
      ChatMessage(
        id: 'msg_sys_${group.id}',
        chatId: group.id,
        senderId: 'system',
        senderNickname: 'Hệ thống',
        senderEmoji: '🤖',
        content: '${_currentProfile.nickname} đã tạo nhóm "$name"',
        createdAt: DateTime.now(),
        type: MessageType.system,
      ),
    ];
    return group;
  }

  @override
  Future<List<ChatMessage>> getGroupMessages(String groupId) async {
    await Future.delayed(const Duration(milliseconds: 150));
    return _chatMessages[groupId] ?? _generateSeedMessages(groupId);
  }

  @override
  Future<ChatMessage> sendGroupMessage({
    required String groupId,
    required String content,
  }) async {
    final msg = ChatMessage(
      id: 'msg_${DateTime.now().millisecondsSinceEpoch}',
      chatId: groupId,
      senderId: 'current_user',
      senderNickname: _currentProfile.nickname,
      senderEmoji: _currentProfile.avatarEmoji,
      content: content,
      createdAt: DateTime.now(),
    );
    _chatMessages.putIfAbsent(groupId, () => []);
    _chatMessages[groupId]!.add(msg);
    return msg;
  }

  @override
  Future<bool> inviteToGroup(String groupId, String displayId) async {
    await Future.delayed(const Duration(milliseconds: 300));
    return true; // Mock: always succeed
  }

  @override
  Future<void> leaveGroup(String groupId) async {
    _groups.removeWhere((g) => g.id == groupId);
  }

  @override
  Future<List<ChatRoom>> getPublicRooms() async {
    await Future.delayed(const Duration(milliseconds: 200));
    return _rooms.where((r) => r.isActive).toList();
  }

  @override
  Future<ChatRoom> createRoom({
    required String name,
    String topic = '',
    String avatarEmoji = '💬',
    int maxMembers = 50,
  }) async {
    final room = ChatRoom(
      id: 'r_${DateTime.now().millisecondsSinceEpoch}',
      name: name,
      topic: topic,
      avatarEmoji: avatarEmoji,
      creatorId: 'current_user',
      creatorNickname: _currentProfile.nickname,
      createdAt: DateTime.now(),
      memberCount: 1,
      maxMembers: maxMembers,
      isActive: true,
    );
    _rooms.add(room);
    _chatMessages[room.id] = [
      ChatMessage(
        id: 'msg_sys_${room.id}',
        chatId: room.id,
        senderId: 'system',
        senderNickname: 'Hệ thống',
        senderEmoji: '🤖',
        content: '${_currentProfile.nickname} đã tạo phòng "$name"',
        createdAt: DateTime.now(),
        type: MessageType.system,
      ),
    ];
    return room;
  }

  @override
  Future<bool> joinRoom(String roomId) async {
    final index = _rooms.indexWhere((r) => r.id == roomId);
    if (index == -1 || !_rooms[index].isActive) return false;
    _rooms[index] = ChatRoom(
      id: _rooms[index].id,
      name: _rooms[index].name,
      topic: _rooms[index].topic,
      avatarEmoji: _rooms[index].avatarEmoji,
      creatorId: _rooms[index].creatorId,
      creatorNickname: _rooms[index].creatorNickname,
      createdAt: _rooms[index].createdAt,
      memberCount: _rooms[index].memberCount + 1,
      maxMembers: _rooms[index].maxMembers,
      isActive: true,
    );
    return true;
  }

  @override
  Future<void> leaveRoom(String roomId) async {
    final index = _rooms.indexWhere((r) => r.id == roomId);
    if (index == -1) return;
    final newCount = _rooms[index].memberCount - 1;
    if (newCount <= 0) {
      // Last person left → destroy room
      _rooms[index] = ChatRoom(
        id: _rooms[index].id,
        name: _rooms[index].name,
        topic: _rooms[index].topic,
        avatarEmoji: _rooms[index].avatarEmoji,
        creatorId: _rooms[index].creatorId,
        creatorNickname: _rooms[index].creatorNickname,
        createdAt: _rooms[index].createdAt,
        memberCount: 0,
        maxMembers: _rooms[index].maxMembers,
        isActive: false,
      );
    } else {
      _rooms[index] = ChatRoom(
        id: _rooms[index].id,
        name: _rooms[index].name,
        topic: _rooms[index].topic,
        avatarEmoji: _rooms[index].avatarEmoji,
        creatorId: _rooms[index].creatorId,
        creatorNickname: _rooms[index].creatorNickname,
        createdAt: _rooms[index].createdAt,
        memberCount: newCount,
        maxMembers: _rooms[index].maxMembers,
        isActive: true,
      );
    }
  }

  @override
  Future<List<ChatMessage>> getRoomMessages(String roomId) async {
    await Future.delayed(const Duration(milliseconds: 150));
    return _chatMessages[roomId] ?? _generateSeedMessages(roomId);
  }

  @override
  Future<ChatMessage> sendRoomMessage({
    required String roomId,
    required String content,
  }) async {
    final msg = ChatMessage(
      id: 'msg_${DateTime.now().millisecondsSinceEpoch}',
      chatId: roomId,
      senderId: 'current_user',
      senderNickname: _currentProfile.nickname,
      senderEmoji: _currentProfile.avatarEmoji,
      content: content,
      createdAt: DateTime.now(),
    );
    _chatMessages.putIfAbsent(roomId, () => []);
    _chatMessages[roomId]!.add(msg);
    return msg;
  }

  List<ChatMessage> _generateSeedMessages(String chatId) {
    final msgs = [
      ChatMessage(
        id: 'seed_1',
        chatId: chatId,
        senderId: 'user_2',
        senderNickname: 'Ánh sáng',
        senderEmoji: '🌟',
        content: 'Xin chào mọi người! 👋',
        createdAt: DateTime.now().subtract(const Duration(minutes: 30)),
      ),
      ChatMessage(
        id: 'seed_2',
        chatId: chatId,
        senderId: 'user_3',
        senderNickname: 'Bình yên',
        senderEmoji: '🌿',
        content: 'Rất vui được ở đây cùng mọi người 😊',
        createdAt: DateTime.now().subtract(const Duration(minutes: 20)),
      ),
      ChatMessage(
        id: 'seed_3',
        chatId: chatId,
        senderId: 'user_4',
        senderNickname: 'Hy vọng',
        senderEmoji: '🦋',
        content: 'Hôm nay mọi người thế nào?',
        createdAt: DateTime.now().subtract(const Duration(minutes: 10)),
      ),
    ];
    _chatMessages[chatId] = msgs;
    return msgs;
  }

  @override
  void dispose() {
    _posts.clear();
    _comments.clear();
    _reports.clear();
    _warnings.clear();
    _groups.clear();
    _rooms.clear();
    _chatMessages.clear();
  }
}
