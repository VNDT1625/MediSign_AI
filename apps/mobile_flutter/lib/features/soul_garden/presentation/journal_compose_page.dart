import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import '../../../core/models/journal_entry.dart';
import '../../../core/services/soul_garden_service.dart';

// ── Palette (đồng bộ soul_garden_page.dart) ──
const _kLeaf = Color(0xFF16A34A);
const _kLeafSoft = Color(0xFFDCFCE7);
const _kLeafSofter = Color(0xFFF0FDF4);
const _kBg = Color(0xFFF8FAFC);
const _kBorder = Color(0xFFE2E8F0);
const _kInk = Color(0xFF0F172A);
const _kInkSoft = Color(0xFF475569);
const _kInkMuted = Color(0xFF94A3B8);

/// Full-screen journal compose / edit page.
///
/// Pass [entry] to edit an existing entry; leave null to create a new one.
class JournalComposePage extends StatefulWidget {
  const JournalComposePage({super.key, this.entry});

  final JournalEntry? entry;

  @override
  State<JournalComposePage> createState() => _JournalComposePageState();
}

class _JournalComposePageState extends State<JournalComposePage> {
  final _svc = SoulGardenService.instance;
  late Mood _selectedMood;
  late Set<EmotionTag> _selectedTags;
  late final TextEditingController _contentController;
  bool _saving = false;

  @override
  void initState() {
    super.initState();
    final e = widget.entry;
    _selectedMood = e?.mood ?? Mood.good;
    _selectedTags = Set.of(e?.tags ?? const {});
    _contentController = TextEditingController(text: e?.content ?? '');
  }

  @override
  void dispose() {
    _contentController.dispose();
    super.dispose();
  }

  Future<void> _save() async {
    if (_saving) return;
    setState(() => _saving = true);
    HapticFeedback.lightImpact();

    final entry = JournalEntry(
      id: widget.entry?.id ??
          'journal_${DateTime.now().millisecondsSinceEpoch}',
      date: widget.entry?.date ?? DateTime.now(),
      mood: _selectedMood,
      content: _contentController.text.trim(),
      tags: Set.unmodifiable(_selectedTags),
    );

    if (widget.entry == null) {
      _svc.addEntry(entry);
    } else {
      _svc.updateEntry(entry);
    }

    setState(() => _saving = false);

    if (mounted) {
      // Show brief confirmation then pop
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: const Text('Đã lưu nhật ký'),
          behavior: SnackBarBehavior.floating,
          backgroundColor: _kLeaf,
          duration: const Duration(seconds: 2),
          shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(12)),
        ),
      );
      Navigator.of(context).pop(entry);
    }
  }

  void _toggleTag(EmotionTag tag) {
    HapticFeedback.selectionClick();
    setState(() {
      if (_selectedTags.contains(tag)) {
        _selectedTags.remove(tag);
      } else {
        _selectedTags.add(tag);
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    final isEdit = widget.entry != null;
    return Scaffold(
      backgroundColor: _kBg,
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0,
        surfaceTintColor: Colors.transparent,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios_new_rounded,
              size: 20, color: _kInk),
          onPressed: () => Navigator.of(context).pop(),
          tooltip: 'Quay lại',
        ),
        title: Text(
          isEdit ? 'Chỉnh sửa nhật ký' : 'Viết nhật ký mới',
          style: const TextStyle(
            fontFamily: 'Outfit',
            fontSize: 17,
            fontWeight: FontWeight.w700,
            color: _kInk,
          ),
        ),
        actions: [
          Padding(
            padding: const EdgeInsets.only(right: 12),
            child: TextButton(
              onPressed: _saving ? null : _save,
              style: TextButton.styleFrom(
                backgroundColor: _kLeaf,
                foregroundColor: Colors.white,
                shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(999)),
                padding:
                    const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              ),
              child: _saving
                  ? const SizedBox(
                      width: 16,
                      height: 16,
                      child: CircularProgressIndicator(
                          color: Colors.white, strokeWidth: 2),
                    )
                  : const Text(
                      'Lưu',
                      style: TextStyle(
                          fontFamily: 'Outfit',
                          fontSize: 14,
                          fontWeight: FontWeight.w700),
                    ),
            ),
          ),
        ],
        bottom: PreferredSize(
          preferredSize: const Size.fromHeight(1),
          child: Container(height: 1, color: _kBorder),
        ),
      ),
      body: GestureDetector(
        onTap: () => FocusScope.of(context).unfocus(),
        child: ListView(
          padding: const EdgeInsets.all(20),
          children: [
            // ── Date label ──────────────────
            Row(
              children: [
                const Icon(Icons.calendar_today_rounded,
                    size: 14, color: _kInkMuted),
                const SizedBox(width: 6),
                Text(
                  _formatDate(widget.entry?.date ?? DateTime.now()),
                  style: const TextStyle(
                    fontFamily: 'Outfit',
                    fontSize: 13,
                    color: _kInkMuted,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 20),

            // ── Mood selector ────────────────
            const Text(
              'Tâm trạng của bạn',
              style: TextStyle(
                fontFamily: 'Outfit',
                fontSize: 14,
                fontWeight: FontWeight.w700,
                color: _kInk,
              ),
            ),
            const SizedBox(height: 12),
            _MoodSelector(
              selected: _selectedMood,
              onChanged: (m) => setState(() => _selectedMood = m),
            ),
            const SizedBox(height: 24),

            // ── Content input ────────────────
            const Text(
              'Hôm nay bạn nghĩ gì?',
              style: TextStyle(
                fontFamily: 'Outfit',
                fontSize: 14,
                fontWeight: FontWeight.w700,
                color: _kInk,
              ),
            ),
            const SizedBox(height: 10),
            Container(
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: _kBorder),
              ),
              padding: const EdgeInsets.all(14),
              child: TextField(
                controller: _contentController,
                maxLines: null,
                minLines: 6,
                keyboardType: TextInputType.multiline,
                textCapitalization: TextCapitalization.sentences,
                style: const TextStyle(
                  fontFamily: 'Outfit',
                  fontSize: 14.5,
                  color: _kInk,
                  height: 1.6,
                ),
                decoration: const InputDecoration(
                  border: InputBorder.none,
                  hintText:
                      'Chia sẻ cảm xúc, suy nghĩ, hay điều gì đó ý nghĩa hôm nay...',
                  hintStyle: TextStyle(
                    fontFamily: 'Outfit',
                    fontSize: 14,
                    color: _kInkMuted,
                    height: 1.6,
                  ),
                  isDense: true,
                  contentPadding: EdgeInsets.zero,
                ),
              ),
            ),
            const SizedBox(height: 24),

            // ── Emotion tags ─────────────────
            const Text(
              'Cảm xúc nổi bật',
              style: TextStyle(
                fontFamily: 'Outfit',
                fontSize: 14,
                fontWeight: FontWeight.w700,
                color: _kInk,
              ),
            ),
            const SizedBox(height: 4),
            const Text(
              'Chọn một hoặc nhiều nhãn cảm xúc',
              style: TextStyle(
                fontFamily: 'Outfit',
                fontSize: 12,
                color: _kInkMuted,
              ),
            ),
            const SizedBox(height: 12),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: EmotionTag.values.map((tag) {
                final selected = _selectedTags.contains(tag);
                return GestureDetector(
                  onTap: () => _toggleTag(tag),
                  child: AnimatedContainer(
                    duration: const Duration(milliseconds: 150),
                    padding: const EdgeInsets.symmetric(
                        horizontal: 12, vertical: 8),
                    decoration: BoxDecoration(
                      color: selected ? _kLeafSoft : Colors.white,
                      borderRadius: BorderRadius.circular(999),
                      border: Border.all(
                        color: selected ? _kLeaf : _kBorder,
                        width: selected ? 1.5 : 1,
                      ),
                    ),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Text(tag.emoji,
                            style: const TextStyle(fontSize: 15)),
                        const SizedBox(width: 5),
                        Text(
                          tag.label,
                          style: TextStyle(
                            fontFamily: 'Outfit',
                            fontSize: 13,
                            fontWeight: selected
                                ? FontWeight.w700
                                : FontWeight.w500,
                            color: selected ? _kLeaf : _kInkSoft,
                          ),
                        ),
                      ],
                    ),
                  ),
                );
              }).toList(),
            ),
            const SizedBox(height: 32),

            // ── Save button ──────────────────
            SizedBox(
              width: double.infinity,
              height: 52,
              child: ElevatedButton.icon(
                onPressed: _saving ? null : _save,
                icon: _saving
                    ? const SizedBox(
                        width: 18,
                        height: 18,
                        child: CircularProgressIndicator(
                            color: Colors.white, strokeWidth: 2),
                      )
                    : const Icon(Icons.save_rounded, size: 18),
                label: Text(
                  isEdit ? 'Cập nhật nhật ký' : 'Lưu nhật ký',
                  style: const TextStyle(
                    fontFamily: 'Outfit',
                    fontSize: 15,
                    fontWeight: FontWeight.w700,
                  ),
                ),
                style: ElevatedButton.styleFrom(
                  backgroundColor: _kLeaf,
                  foregroundColor: Colors.white,
                  shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(14)),
                  elevation: 2,
                ),
              ),
            ),
            const SizedBox(height: 24),
          ],
        ),
      ),
    );
  }

  String _formatDate(DateTime d) {
    const days = [
      'Thứ Hai',
      'Thứ Ba',
      'Thứ Tư',
      'Thứ Năm',
      'Thứ Sáu',
      'Thứ Bảy',
      'Chủ Nhật',
    ];
    final dayName = days[d.weekday - 1];
    return '$dayName, ${d.day}/${d.month}/${d.year}';
  }
}

// ───────────────────────── MOOD SELECTOR ─────────────────────────

class _MoodSelector extends StatelessWidget {
  const _MoodSelector({required this.selected, required this.onChanged});
  final Mood selected;
  final ValueChanged<Mood> onChanged;

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceAround,
      children: Mood.values.map((mood) {
        final active = mood == selected;
        return GestureDetector(
          onTap: () {
            HapticFeedback.selectionClick();
            onChanged(mood);
          },
          child: AnimatedContainer(
            duration: const Duration(milliseconds: 180),
            curve: Curves.easeOut,
            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 10),
            decoration: BoxDecoration(
              color: active ? _kLeafSoft : Colors.white,
              borderRadius: BorderRadius.circular(14),
              border: Border.all(
                color: active ? _kLeaf : _kBorder,
                width: active ? 2 : 1,
              ),
              boxShadow: active
                  ? [
                      BoxShadow(
                        color: _kLeaf.withOpacity(0.18),
                        blurRadius: 8,
                        offset: const Offset(0, 3),
                      ),
                    ]
                  : null,
            ),
            child: Column(
              children: [
                Text(
                  mood.emoji,
                  style: TextStyle(
                      fontSize: active ? 28 : 24),
                ),
                const SizedBox(height: 4),
                Text(
                  mood.label,
                  style: TextStyle(
                    fontFamily: 'Outfit',
                    fontSize: 10,
                    fontWeight:
                        active ? FontWeight.w700 : FontWeight.w500,
                    color: active ? _kLeaf : _kInkMuted,
                  ),
                ),
              ],
            ),
          ),
        );
      }).toList(),
    );
  }
}
