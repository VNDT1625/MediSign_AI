import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../../../../core/services/social_service.dart';
import '../../../../core/services/service_locator.dart';
import '../../../../core/theme/glass_theme.dart';

/// ══════════════════════════════════════════════════════════════
/// ROOM CHAT SCREEN — Phòng chat công khai tạm thời
/// Tự hủy khi tất cả rời phòng
/// ══════════════════════════════════════════════════════════════

class RoomChatScreen extends StatefulWidget {
  final ChatRoom room;
  const RoomChatScreen({super.key, required this.room});

  @override
  State<RoomChatScreen> createState() => _RoomChatScreenState();
}

class _RoomChatScreenState extends State<RoomChatScreen> {
  final _social = ServiceLocator.instance.social;
  final _msgController = TextEditingController();
  final _scrollController = ScrollController();
  List<ChatMessage> _messages = [];
  bool _isLoading = true;
  late int _memberCount;

  @override
  void initState() {
    super.initState();
    _memberCount = widget.room.memberCount;
    _joinAndLoad();
  }

  @override
  void dispose() {
    _msgController.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  Future<void> _joinAndLoad() async {
    await _social.joinRoom(widget.room.id);
    setState(() => _memberCount = _memberCount + 1);
    _loadMessages();
  }

  Future<void> _loadMessages() async {
    setState(() => _isLoading = true);
    final msgs = await _social.getRoomMessages(widget.room.id);
    setState(() {
      _messages = msgs;
      _isLoading = false;
    });
    _scrollToBottom();
  }

  Future<void> _sendMessage() async {
    if (_msgController.text.trim().isEmpty) return;
    HapticFeedback.lightImpact();
    await _social.sendRoomMessage(
      roomId: widget.room.id,
      content: _msgController.text.trim(),
    );
    _msgController.clear();
    _loadMessages();
  }

  Future<void> _leaveRoom() async {
    await _social.leaveRoom(widget.room.id);
    if (mounted) Navigator.of(context).pop();
  }

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return GlassTheme.scaffoldBackground(
      child: SafeArea(
        child: Column(
          children: [
            // Header
            GlassTheme.appBar(
              title: widget.room.name,
              showBackButton: true,
              onBack: _leaveRoom,
              actions: [
                // Online indicator
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                  decoration: BoxDecoration(
                    color: GlassTheme.primaryGreen.withValues(alpha: 0.15),
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(color: GlassTheme.primaryGreen.withValues(alpha: 0.3)),
                  ),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Container(
                        width: 8,
                        height: 8,
                        decoration: const BoxDecoration(
                          shape: BoxShape.circle,
                          color: GlassTheme.primaryGreenLight,
                        ),
                      ),
                      const SizedBox(width: 6),
                      Text(
                        '$_memberCount online',
                        style: const TextStyle(
                          fontFamily: 'Outfit',
                          fontSize: 12,
                          fontWeight: FontWeight.w600,
                          color: GlassTheme.primaryGreenLight,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),

            // Room info
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 8),
              child: GlassTheme.glassCard(
                padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                fillColor: const Color(0xFFF59E0B).withValues(alpha: 0.06),
                borderColor: const Color(0xFFF59E0B).withValues(alpha: 0.15),
                child: Row(
                  children: [
                    Text(widget.room.avatarEmoji, style: const TextStyle(fontSize: 22)),
                    const SizedBox(width: 10),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          if (widget.room.topic.isNotEmpty)
                            Text(widget.room.topic,
                                style: GlassTheme.caption.copyWith(fontSize: 12)),
                          Text(
                            '⚡ Phòng tạm thời — tự hủy khi hết người',
                            style: TextStyle(
                              fontFamily: 'Outfit',
                              fontSize: 10,
                              color: const Color(0xFFFBBF24).withValues(alpha: 0.7),
                            ),
                          ),
                        ],
                      ),
                    ),
                    GestureDetector(
                      onTap: _leaveRoom,
                      child: Container(
                        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                        decoration: BoxDecoration(
                          color: const Color(0xFFEF4444).withValues(alpha: 0.12),
                          borderRadius: BorderRadius.circular(10),
                          border: Border.all(color: const Color(0xFFEF4444).withValues(alpha: 0.3)),
                        ),
                        child: const Text(
                          'Rời',
                          style: TextStyle(
                            fontFamily: 'Outfit',
                            fontSize: 11,
                            fontWeight: FontWeight.w600,
                            color: Color(0xFFF87171),
                          ),
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),

            // Messages
            Expanded(
              child: _isLoading
                  ? GlassTheme.loadingIndicator()
                  : ListView.builder(
                      controller: _scrollController,
                      padding: const EdgeInsets.fromLTRB(20, 8, 20, 8),
                      itemCount: _messages.length,
                      itemBuilder: (_, i) => _buildMessage(_messages[i]),
                    ),
            ),

            // Input
            _buildInput(),
          ],
        ),
      ),
    );
  }

  Widget _buildMessage(ChatMessage msg) {
    final isMe = msg.senderId == 'current_user';
    final isSystem = msg.type == MessageType.system;

    if (isSystem) {
      return Padding(
        padding: const EdgeInsets.symmetric(vertical: 8),
        child: Center(
          child: Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
            decoration: BoxDecoration(
              color: GlassTheme.glassFill,
              borderRadius: BorderRadius.circular(12),
            ),
            child: Text(msg.content,
                style: GlassTheme.caption.copyWith(fontSize: 11)),
          ),
        ),
      );
    }

    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Row(
        mainAxisAlignment: isMe ? MainAxisAlignment.end : MainAxisAlignment.start,
        crossAxisAlignment: CrossAxisAlignment.end,
        children: [
          if (!isMe) ...[
            Container(
              width: 30,
              height: 30,
              decoration: BoxDecoration(
                color: GlassTheme.glassFillMedium,
                borderRadius: BorderRadius.circular(10),
              ),
              child: Center(child: Text(msg.senderEmoji, style: const TextStyle(fontSize: 16))),
            ),
            const SizedBox(width: 8),
          ],
          Flexible(
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
              decoration: BoxDecoration(
                color: isMe
                    ? GlassTheme.primaryGreen.withValues(alpha: 0.2)
                    : GlassTheme.glassFill,
                borderRadius: BorderRadius.only(
                  topLeft: const Radius.circular(16),
                  topRight: const Radius.circular(16),
                  bottomLeft: Radius.circular(isMe ? 16 : 4),
                  bottomRight: Radius.circular(isMe ? 4 : 16),
                ),
                border: Border.all(
                  color: isMe
                      ? GlassTheme.primaryGreen.withValues(alpha: 0.3)
                      : GlassTheme.glassBorderLight,
                ),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  if (!isMe)
                    Text(
                      msg.senderNickname,
                      style: TextStyle(
                        fontFamily: 'Outfit',
                        fontSize: 11,
                        fontWeight: FontWeight.w600,
                        color: isMe ? GlassTheme.primaryGreenLight : GlassTheme.textMuted,
                      ),
                    ),
                  Text(
                    msg.content,
                    style: GlassTheme.body.copyWith(color: Colors.white, fontSize: 14),
                  ),
                  const SizedBox(height: 2),
                  Text(
                    _formatTime(msg.createdAt),
                    style: GlassTheme.caption.copyWith(fontSize: 10),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildInput() {
    return Container(
      padding: const EdgeInsets.fromLTRB(20, 10, 20, 10),
      decoration: const BoxDecoration(
        color: Color(0xE6082035),
        border: Border(top: BorderSide(color: GlassTheme.glassBorderLight, width: 0.5)),
      ),
      child: SafeArea(
        top: false,
        child: Row(
          children: [
            Expanded(
              child: Container(
                padding: const EdgeInsets.symmetric(horizontal: 14),
                decoration: BoxDecoration(
                  color: GlassTheme.glassFill,
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(color: GlassTheme.glassBorderLight),
                ),
                child: TextField(
                  controller: _msgController,
                  style: GlassTheme.body.copyWith(color: Colors.white, fontSize: 14),
                  decoration: InputDecoration(
                    hintText: 'Nhắn tin...',
                    hintStyle: GlassTheme.caption.copyWith(fontSize: 13),
                    border: InputBorder.none,
                    contentPadding: const EdgeInsets.symmetric(vertical: 10),
                  ),
                ),
              ),
            ),
            const SizedBox(width: 8),
            GestureDetector(
              onTap: _sendMessage,
              child: Container(
                width: 40,
                height: 40,
                decoration: BoxDecoration(
                  color: GlassTheme.primaryGreen.withValues(alpha: 0.2),
                  borderRadius: BorderRadius.circular(14),
                  border: Border.all(color: GlassTheme.primaryGreen.withValues(alpha: 0.4)),
                ),
                child: const Icon(Icons.send_rounded, size: 20, color: GlassTheme.primaryGreenLight),
              ),
            ),
          ],
        ),
      ),
    );
  }

  String _formatTime(DateTime date) {
    final diff = DateTime.now().difference(date);
    if (diff.inMinutes < 1) return 'vừa xong';
    if (diff.inMinutes < 60) return '${diff.inMinutes}p';
    if (diff.inHours < 24) return '${diff.inHours}h';
    return '${date.day}/${date.month}';
  }
}
