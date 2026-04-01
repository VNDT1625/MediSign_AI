import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../../../../core/services/social_service.dart';
import '../../../../core/services/service_locator.dart';
import '../../../../core/theme/glass_theme.dart';

/// ══════════════════════════════════════════════════════════════
/// CREATE POST SCREEN — Đăng bài chia sẻ lạc quan
/// GlassTheme version with positive prompts
/// ══════════════════════════════════════════════════════════════

class CreatePostScreen extends StatefulWidget {
  const CreatePostScreen({super.key});

  @override
  State<CreatePostScreen> createState() => _CreatePostScreenState();
}

class _CreatePostScreenState extends State<CreatePostScreen> {
  final _contentController = TextEditingController();
  final _tagController = TextEditingController();
  final _social = ServiceLocator.instance.social;

  PostCategory _selectedCategory = PostCategory.gratitude;
  final List<String> _tags = [];
  bool _isAnonymous = true;
  bool _includeDisclaimer = false;
  bool _isSubmitting = false;
  ModerationResult? _previewResult;

  @override
  void dispose() {
    _contentController.dispose();
    _tagController.dispose();
    super.dispose();
  }

  Future<void> _submitPost() async {
    if (_contentController.text.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: const Text('Vui lòng nhập nội dung'),
          backgroundColor: const Color(0xFF0A2540),
          behavior: SnackBarBehavior.floating,
          shape:
              RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        ),
      );
      return;
    }

    setState(() => _isSubmitting = true);

    try {
      final post = await _social.createPost(
        content: _contentController.text,
        category: _selectedCategory,
        tags: _tags,
        isAnonymous: _isAnonymous,
        includeMedicalDisclaimer: _includeDisclaimer,
      );

      if (mounted) {
        HapticFeedback.mediumImpact();
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(post.status == PostStatus.approved
                ? '🎉 Đăng bài thành công!'
                : '⏳ Bài viết đang chờ duyệt'),
            backgroundColor: const Color(0xFF0A2540),
            behavior: SnackBarBehavior.floating,
            shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12)),
          ),
        );
        Navigator.of(context).pop();
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Lỗi: $e')),
        );
      }
    } finally {
      if (mounted) setState(() => _isSubmitting = false);
    }
  }

  Future<void> _previewModeration() async {
    if (_contentController.text.isEmpty) return;
    final result = await _social.previewModeration(_contentController.text);
    setState(() => _previewResult = result);
  }

  void _addTag() {
    final tag = _tagController.text.trim();
    if (tag.isNotEmpty && !_tags.contains(tag)) {
      setState(() {
        _tags.add(tag);
        _tagController.clear();
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return GlassTheme.scaffoldBackground(
      child: SafeArea(
        child: Column(
          children: [
            // App bar
            GlassTheme.appBar(
              title: 'Chia sẻ',
              showBackButton: true,
              onBack: () => Navigator.of(context).pop(),
              actions: [
                GestureDetector(
                  onTap: _isSubmitting ? null : _submitPost,
                  child: Container(
                    padding:
                        const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                    decoration: BoxDecoration(
                      color: _isSubmitting
                          ? GlassTheme.glassFill
                          : GlassTheme.primaryGreen.withOpacity(0.2),
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(
                        color: GlassTheme.primaryGreen.withOpacity(0.4),
                      ),
                    ),
                    child: _isSubmitting
                        ? const SizedBox(
                            width: 18,
                            height: 18,
                            child: CircularProgressIndicator(
                              strokeWidth: 2,
                              color: GlassTheme.primaryGreenLight,
                            ),
                          )
                        : const Text(
                            'Đăng',
                            style: TextStyle(
                              fontFamily: 'Outfit',
                              fontSize: 14,
                              fontWeight: FontWeight.w600,
                              color: GlassTheme.primaryGreenLight,
                            ),
                          ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),

            // Body
            Expanded(
              child: ListView(
                padding: const EdgeInsets.fromLTRB(20, 0, 20, 40),
                children: [
                  // Positive prompt
                  _buildPositivePrompt(),
                  const SizedBox(height: 16),

                  // Category
                  _buildLabel('Chủ đề'),
                  const SizedBox(height: 8),
                  _buildCategorySelector(),
                  const SizedBox(height: 20),

                  // Content
                  _buildLabel('Nội dung'),
                  const SizedBox(height: 8),
                  _buildContentField(),

                  // Moderation preview
                  if (_previewResult != null) ...[
                    const SizedBox(height: 8),
                    _buildModerationPreview(),
                  ],

                  const SizedBox(height: 20),

                  // Tags
                  _buildLabel('Tags'),
                  const SizedBox(height: 8),
                  _buildTagInput(),
                  if (_tags.isNotEmpty) ...[
                    const SizedBox(height: 8),
                    _buildTagChips(),
                  ],

                  const SizedBox(height: 20),

                  // Options
                  _buildOptions(),

                  const SizedBox(height: 24),

                  // Legal notice
                  _buildLegalNotice(),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildPositivePrompt() {
    return GlassTheme.glassCard(
      padding: const EdgeInsets.all(14),
      fillColor: const Color(0xFFF59E0B).withOpacity(0.08),
      borderColor: const Color(0xFFF59E0B).withOpacity(0.2),
      child: Row(
        children: [
          const Text('💡', style: TextStyle(fontSize: 22)),
          const SizedBox(width: 10),
          Expanded(
            child: Text(
              'Chia sẻ điều tốt đẹp hôm nay hoặc gửi lời động viên đến ai đó!',
              style: GlassTheme.body.copyWith(
                color: const Color(0xFFFBBF24),
                fontSize: 13,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildLabel(String text) {
    return Text(
      text,
      style: GlassTheme.label.copyWith(
        fontSize: 14,
        color: GlassTheme.textSecondary,
      ),
    );
  }

  Widget _buildCategorySelector() {
    return Wrap(
      spacing: 8,
      runSpacing: 8,
      children: PostCategory.values.map((cat) {
        final isSelected = _selectedCategory == cat;
        return GestureDetector(
          onTap: () => setState(() => _selectedCategory = cat),
          child: AnimatedContainer(
            duration: const Duration(milliseconds: 200),
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
            decoration: BoxDecoration(
              color: isSelected
                  ? GlassTheme.primaryGreen.withOpacity(0.2)
                  : GlassTheme.glassFill,
              borderRadius: BorderRadius.circular(14),
              border: Border.all(
                color: isSelected
                    ? GlassTheme.primaryGreenLight.withOpacity(0.5)
                    : GlassTheme.glassBorderLight,
              ),
            ),
            child: Text(
              '${cat.emoji} ${cat.label}',
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
      }).toList(),
    );
  }

  Widget _buildContentField() {
    return GlassTheme.textField(
      controller: _contentController,
      hint: _getHintText(),
      maxLines: 6,
      suffixIcon: Icons.preview_rounded,
      onSuffixTap: _previewModeration,
    );
  }

  String _getHintText() {
    switch (_selectedCategory) {
      case PostCategory.gratitude:
        return '3 điều bạn biết ơn hôm nay...';
      case PostCategory.encouragement:
        return 'Gửi lời động viên đến ai đó...';
      case PostCategory.healthShare:
        return 'Chia sẻ về sức khỏe của bạn...';
      case PostCategory.treatmentExperience:
        return 'Kinh nghiệm điều trị của bạn...';
      case PostCategory.emotionalSupport:
        return 'Tâm sự hoặc cần hỗ trợ...';
      case PostCategory.question:
        return 'Đặt câu hỏi cho cộng đồng...';
      case PostCategory.lifestyleTips:
        return 'Mẹo hay muốn chia sẻ...';
      case PostCategory.general:
        return 'Bạn đang nghĩ gì...';
    }
  }

  Widget _buildModerationPreview() {
    final hasIssues = _previewResult!.flags.isNotEmpty;
    final color = hasIssues ? const Color(0xFFF59E0B) : GlassTheme.primaryGreen;

    return GlassTheme.glassCard(
      padding: const EdgeInsets.all(12),
      fillColor: color.withOpacity(0.1),
      borderColor: color.withOpacity(0.3),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(
                hasIssues ? Icons.warning_amber : Icons.check_circle,
                color: hasIssues ? const Color(0xFFF59E0B) : GlassTheme.primaryGreenLight,
                size: 18,
              ),
              const SizedBox(width: 8),
              Text(
                hasIssues ? 'Cần chú ý' : 'Nội dung OK ✅',
                style: TextStyle(
                  fontFamily: 'Outfit',
                  fontWeight: FontWeight.w600,
                  fontSize: 13,
                  color: hasIssues ? const Color(0xFFFBBF24) : GlassTheme.primaryGreenLight,
                ),
              ),
            ],
          ),
          if (_previewResult!.flags.isNotEmpty) ...[
            const SizedBox(height: 8),
            ..._previewResult!.flags.map((flag) => Padding(
                  padding: const EdgeInsets.only(top: 4),
                  child: Text(
                    '• ${flag.message}',
                    style: GlassTheme.caption.copyWith(fontSize: 12),
                  ),
                )),
          ],
        ],
      ),
    );
  }

  Widget _buildTagInput() {
    return Row(
      children: [
        Expanded(
          child: GlassTheme.textField(
            controller: _tagController,
            hint: 'Thêm tag...',
            prefixIcon: Icons.tag,
          ),
        ),
        const SizedBox(width: 8),
        GlassTheme.glassIconButton(
          icon: Icons.add_rounded,
          onPressed: _addTag,
          size: 44,
        ),
      ],
    );
  }

  Widget _buildTagChips() {
    return Wrap(
      spacing: 8,
      runSpacing: 6,
      children: _tags.map((tag) {
        return Container(
          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
          decoration: BoxDecoration(
            color: GlassTheme.glassFill,
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: GlassTheme.glassBorderLight),
          ),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                '#$tag',
                style: GlassTheme.caption.copyWith(fontSize: 12),
              ),
              const SizedBox(width: 4),
              GestureDetector(
                onTap: () => setState(() => _tags.remove(tag)),
                child: const Icon(
                  Icons.close,
                  size: 14,
                  color: GlassTheme.textMuted,
                ),
              ),
            ],
          ),
        );
      }).toList(),
    );
  }

  Widget _buildOptions() {
    return GlassTheme.glassCard(
      padding: const EdgeInsets.symmetric(vertical: 4, horizontal: 8),
      child: Column(
        children: [
          // Forced anonymity — no toggle, always on
          ListTile(
            leading: Icon(
              Icons.visibility_off_rounded,
              color: GlassTheme.primaryGreenLight,
              size: 22,
            ),
            title: const Text(
              'Đăng ẩn danh',
              style: TextStyle(
                fontFamily: 'Outfit',
                fontSize: 15,
                fontWeight: FontWeight.w500,
                color: Colors.white,
              ),
            ),
            subtitle: Text(
              'Tất cả bài viết đều ẩn danh — bảo vệ quyền riêng tư',
              style: GlassTheme.caption.copyWith(fontSize: 12),
            ),
            trailing: Container(
              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
              decoration: BoxDecoration(
                color: GlassTheme.primaryGreen.withValues(alpha: 0.2),
                borderRadius: BorderRadius.circular(10),
              ),
              child: const Text(
                'Luôn bật',
                style: TextStyle(
                  fontFamily: 'Outfit',
                  fontSize: 11,
                  fontWeight: FontWeight.w600,
                  color: GlassTheme.primaryGreenLight,
                ),
              ),
            ),
          ),
          if (_selectedCategory.requiresMedicalDisclaimer) ...[
            const Divider(color: GlassTheme.glassBorderLight, height: 1),
            SwitchListTile(
              activeColor: const Color(0xFFF59E0B),
              title: const Text(
                'Thêm disclaimer y tế',
                style: TextStyle(
                  fontFamily: 'Outfit',
                  fontSize: 15,
                  fontWeight: FontWeight.w500,
                  color: Colors.white,
                ),
              ),
              subtitle: Text(
                'Nội dung yêu cầu cảnh báo y tế',
                style: GlassTheme.caption.copyWith(fontSize: 12),
              ),
              value: _includeDisclaimer,
              onChanged: (v) => setState(() => _includeDisclaimer = v),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildLegalNotice() {
    return GlassTheme.glassCard(
      padding: const EdgeInsets.all(12),
      fillColor: const Color(0xFFEF4444).withOpacity(0.06),
      borderColor: const Color(0xFFEF4444).withOpacity(0.15),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.shield_outlined,
                  size: 16,
                  color: const Color(0xFFEF4444).withOpacity(0.7)),
              const SizedBox(width: 6),
              Text(
                'Quy tắc cộng đồng',
                style: TextStyle(
                  fontFamily: 'Outfit',
                  fontSize: 12,
                  fontWeight: FontWeight.w600,
                  color: const Color(0xFFEF4444).withOpacity(0.8),
                ),
              ),
            ],
          ),
          const SizedBox(height: 6),
          Text(
            '• Không chia sẻ thông tin cá nhân (SĐT, CCCD...)\n'
            '• Không quảng cáo, mua/bán thuốc\n'
            '• Tôn trọng và lan tỏa yêu thương',
            style: TextStyle(
              fontFamily: 'Outfit',
              fontSize: 11,
              color: const Color(0xFFFCA5A5).withOpacity(0.8),
              height: 1.5,
            ),
          ),
        ],
      ),
    );
  }
}
