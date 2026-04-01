import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../../../../core/services/social_service.dart';
import '../../../../core/services/service_locator.dart';
import '../../../../core/theme/glass_theme.dart';

/// ══════════════════════════════════════════════════════════════
/// GROUP CHAT SCREEN — Nhóm chat cố định (persistent)
/// ══════════════════════════════════════════════════════════════

class GroupChatScreen extends StatefulWidget {
  final ChatGroup group;
  const GroupChatScreen({super.key, required this.group});

  @override
  State<GroupChatScreen> createState() => _GroupChatScreenState();
}

class _GroupChatScreenState extends State<GroupChatScreen> {
  final _social = ServiceLocator.instance.social;
  final _msgController = TextEditingController();
  final _scrollController = ScrollController();
  List<ChatMessage> _messages = [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadMessages();
  }

  @override
  void dispose() {
    _msgController.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  Future<void> _loadMessages() async {
    setState(() => _isLoading = true);
    final msgs = await _social.getGroupMessages(widget.group.id);
    setState(() {
      _messages = msgs;
      _isLoading = false;
    });
    _scrollToBottom();
  }

  Future<void> _sendMessage() async {
    if (_msgController.text.trim().isEmpty) return;
    HapticFeedback.lightImpact();
    await _social.sendGroupMessage(
      groupId: widget.group.id,
      content: _msgController.text.trim(),
    );
    _msgController.clear();
    _loadMessages();
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

  void _showInviteDialog() {
    final idController = TextEditingController();
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: const Color(0xFF0A2540),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
        title: const Text(
          'Mời thành viên',
          style: TextStyle(fontFamily: 'Outfit', color: Colors.white, fontWeight: FontWeight.w700),
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text('Nhập mã ID của người muốn mời (VD: #LQ2024)',
                style: GlassTheme.caption),
            const SizedBox(height: 12),
            Container(
              decoration: BoxDecoration(
                color: GlassTheme.glassFill,
                borderRadius: BorderRadius.circular(14),
                border: Border.all(color: GlassTheme.glassBorderLight),
              ),
              padding: const EdgeInsets.symmetric(horizontal: 14),
              child: TextField(
                controller: idController,
                style: GlassTheme.body.copyWith(color: Colors.white, fontSize: 14),
                decoration: InputDecoration(
                  hintText: '#LQ...',
                  hintStyle: GlassTheme.caption,
                  border: InputBorder.none,
                ),
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('Hủy', style: TextStyle(color: GlassTheme.textMuted)),
          ),
          TextButton(
            onPressed: () async {
              if (idController.text.isNotEmpty) {
                await _social.inviteToGroup(widget.group.id, idController.text);
                if (ctx.mounted) Navigator.pop(ctx);
                if (mounted) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(
                      content: const Text('✅ Đã gửi lời mời!'),
                      backgroundColor: const Color(0xFF0A2540),
                      behavior: SnackBarBehavior.floating,
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                    ),
                  );
                }
              }
            },
            child: const Text('Mời', style: TextStyle(color: GlassTheme.primaryGreenLight)),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return GlassTheme.scaffoldBackground(
      child: SafeArea(
        child: Column(
          children: [
            // Header
            GlassTheme.appBar(
              title: widget.group.name,
              showBackButton: true,
              onBack: () => Navigator.of(context).pop(),
              actions: [
                GlassTheme.glassIconButton(
                  icon: Icons.person_add_rounded,
                  onPressed: _showInviteDialog,
                  size: 40,
                  tooltip: 'Mời thành viên',
                ),
              ],
            ),

            // Group info
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 8),
              child: GlassTheme.glassCard(
                padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                child: Row(
                  children: [
                    Text(widget.group.avatarEmoji, style: const TextStyle(fontSize: 24)),
                    const SizedBox(width: 10),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(widget.group.description.isEmpty
                              ? widget.group.name : widget.group.description,
                              style: GlassTheme.caption.copyWith(fontSize: 12)),
                          Text('${widget.group.memberCount} thành viên',
                              style: GlassTheme.caption.copyWith(fontSize: 11)),
                        ],
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
