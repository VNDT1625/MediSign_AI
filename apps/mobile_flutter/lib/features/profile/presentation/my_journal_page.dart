import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import '../../../core/models/journal_entry.dart';
import '../../../core/services/soul_garden_service.dart';
import '../../soul_garden/presentation/journal_compose_page.dart';

const _kBg = Color(0xFFF8FAFC);
const _kBorder = Color(0xFFE2E8F0);
const _kInk = Color(0xFF0F172A);
const _kInkSoft = Color(0xFF475569);
const _kInkMuted = Color(0xFF94A3B8);
const _kBrand = Color(0xFF16A34A);
const _kBrandSoft = Color(0xFFDCFCE7);

/// Liệt kê toàn bộ nhật ký cảm xúc của người dùng. Cho phép mở để xem
/// chi tiết / chỉnh sửa qua [JournalComposePage].
class MyJournalPage extends StatefulWidget {
  const MyJournalPage({super.key});

  @override
  State<MyJournalPage> createState() => _MyJournalPageState();
}

class _MyJournalPageState extends State<MyJournalPage> {
  final _svc = SoulGardenService.instance;

  Future<void> _openCompose([JournalEntry? entry]) async {
    HapticFeedback.selectionClick();
    await Navigator.of(context).push<JournalEntry>(
      MaterialPageRoute(builder: (_) => JournalComposePage(entry: entry)),
    );
    if (mounted) setState(() {});
  }

  @override
  Widget build(BuildContext context) {
    final entries = List<JournalEntry>.from(_svc.entries)
      ..sort((a, b) => b.date.compareTo(a.date));

    return Scaffold(
      backgroundColor: _kBg,
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0,
        scrolledUnderElevation: 0,
        foregroundColor: _kInk,
        title: const Text(
          'Nhật ký của tôi',
          style: TextStyle(
            fontFamily: 'Outfit',
            fontWeight: FontWeight.w700,
            fontSize: 18,
            color: _kInk,
          ),
        ),
      ),
      floatingActionButton: FloatingActionButton.extended(
        backgroundColor: _kBrand,
        foregroundColor: Colors.white,
        onPressed: () => _openCompose(),
        icon: const Icon(Icons.edit_note_rounded, size: 20),
        label: const Text(
          'Viết mới',
          style: TextStyle(fontFamily: 'Outfit', fontWeight: FontWeight.w700),
        ),
      ),
      body: SafeArea(
        child: entries.isEmpty
            ? _EmptyState(onWrite: () => _openCompose())
            : ListView.separated(
                padding: const EdgeInsets.fromLTRB(16, 12, 16, 96),
                itemCount: entries.length + 1,
                separatorBuilder: (_, __) => const SizedBox(height: 10),
                itemBuilder: (_, i) {
                  if (i == 0) return _Summary(count: entries.length);
                  final entry = entries[i - 1];
                  return _EntryCard(
                    entry: entry,
                    onTap: () => _openCompose(entry),
                  );
                },
              ),
      ),
    );
  }
}

class _Summary extends StatelessWidget {
  const _Summary({required this.count});
  final int count;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.fromLTRB(16, 14, 16, 14),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [_kBrandSoft, Color(0xFFF0FDF4)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: Colors.white, width: 1.5),
      ),
      child: Row(
        children: [
          Container(
            width: 44,
            height: 44,
            decoration: const BoxDecoration(
              color: Colors.white,
              shape: BoxShape.circle,
            ),
            child: const Icon(Icons.menu_book_rounded,
                color: _kBrand, size: 22),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisSize: MainAxisSize.min,
              children: [
                Text(
                  '$count bài nhật ký',
                  style: const TextStyle(
                    fontFamily: 'Outfit',
                    fontSize: 15,
                    fontWeight: FontWeight.w800,
                    color: _kInk,
                  ),
                ),
                const SizedBox(height: 2),
                const Text(
                  'Mỗi bài viết là một bước trên hành trình chữa lành.',
                  style: TextStyle(
                    fontFamily: 'Outfit',
                    fontSize: 12,
                    color: _kInkSoft,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _EntryCard extends StatelessWidget {
  const _EntryCard({required this.entry, required this.onTap});
  final JournalEntry entry;
  final VoidCallback onTap;

  static const _kVnMonths = [
    'Th1', 'Th2', 'Th3', 'Th4', 'Th5', 'Th6',
    'Th7', 'Th8', 'Th9', 'Th10', 'Th11', 'Th12',
  ];

  String get _dateLabel {
    final d = entry.date;
    return '${d.day} ${_kVnMonths[d.month - 1]} ${d.year}';
  }

  @override
  Widget build(BuildContext context) {
    final preview = entry.content.trim().isEmpty
        ? '(Không có nội dung — chỉ ghi lại cảm xúc)'
        : entry.content;

    return Material(
      color: Colors.white,
      borderRadius: BorderRadius.circular(16),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(16),
        child: Container(
          padding: const EdgeInsets.fromLTRB(14, 12, 14, 12),
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: _kBorder),
          ),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Container(
                width: 44,
                height: 44,
                decoration: BoxDecoration(
                  color: const Color(0xFFF1F5F9),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Center(
                  child: Text(
                    entry.mood.emoji,
                    style: const TextStyle(fontSize: 22),
                  ),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Row(
                      children: [
                        Text(
                          entry.mood.label,
                          style: const TextStyle(
                            fontFamily: 'Outfit',
                            fontSize: 13.5,
                            fontWeight: FontWeight.w700,
                            color: _kInk,
                          ),
                        ),
                        const SizedBox(width: 8),
                        Text(
                          _dateLabel,
                          style: const TextStyle(
                            fontFamily: 'Outfit',
                            fontSize: 11.5,
                            color: _kInkMuted,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 4),
                    Text(
                      preview,
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                      style: const TextStyle(
                        fontFamily: 'Outfit',
                        fontSize: 12.5,
                        color: _kInkSoft,
                        height: 1.4,
                      ),
                    ),
                    if (entry.tags.isNotEmpty) ...[
                      const SizedBox(height: 6),
                      Wrap(
                        spacing: 6,
                        runSpacing: 4,
                        children: entry.tags
                            .take(4)
                            .map((t) => _TagChip(label: t.label))
                            .toList(),
                      ),
                    ],
                  ],
                ),
              ),
              const Icon(Icons.chevron_right_rounded,
                  size: 20, color: _kInkMuted),
            ],
          ),
        ),
      ),
    );
  }
}

class _TagChip extends StatelessWidget {
  const _TagChip({required this.label});
  final String label;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
      decoration: BoxDecoration(
        color: _kBrandSoft,
        borderRadius: BorderRadius.circular(999),
      ),
      child: Text(
        label,
        style: const TextStyle(
          fontFamily: 'Outfit',
          fontSize: 10.5,
          fontWeight: FontWeight.w600,
          color: _kBrand,
        ),
      ),
    );
  }
}

class _EmptyState extends StatelessWidget {
  const _EmptyState({required this.onWrite});
  final VoidCallback onWrite;

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              width: 84,
              height: 84,
              decoration: const BoxDecoration(
                color: _kBrandSoft,
                shape: BoxShape.circle,
              ),
              child: const Icon(Icons.menu_book_rounded,
                  size: 40, color: _kBrand),
            ),
            const SizedBox(height: 16),
            const Text(
              'Chưa có nhật ký nào',
              style: TextStyle(
                fontFamily: 'Outfit',
                fontSize: 16,
                fontWeight: FontWeight.w800,
                color: _kInk,
              ),
            ),
            const SizedBox(height: 6),
            const Text(
              'Hãy ghi lại cảm xúc đầu tiên của bạn — chỉ một vài câu thôi cũng đủ.',
              textAlign: TextAlign.center,
              style: TextStyle(
                fontFamily: 'Outfit',
                fontSize: 12.5,
                color: _kInkSoft,
                height: 1.5,
              ),
            ),
            const SizedBox(height: 16),
            ElevatedButton.icon(
              onPressed: onWrite,
              icon: const Icon(Icons.edit_note_rounded, size: 18),
              label: const Text(
                'Viết bài đầu tiên',
                style: TextStyle(
                    fontFamily: 'Outfit', fontWeight: FontWeight.w700),
              ),
              style: ElevatedButton.styleFrom(
                backgroundColor: _kBrand,
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(
                    horizontal: 18, vertical: 12),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
