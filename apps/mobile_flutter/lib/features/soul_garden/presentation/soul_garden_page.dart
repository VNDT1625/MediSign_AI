import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import '../../../core/models/journal_entry.dart';
import '../../../core/services/soul_garden_service.dart';
import 'achievements_page.dart';
import 'breathing_exercise_page.dart';
import 'mood_analytics_page.dart';

/// Soul Garden overview — mood-based tree, streak, weekly mood, CTA, recent entries,
/// navigation to analytics / achievements / breathing.
class SoulGardenPage extends StatefulWidget {
  const SoulGardenPage({super.key});

  @override
  State<SoulGardenPage> createState() => _SoulGardenPageState();
}

class _SoulGardenPageState extends State<SoulGardenPage>
    with SingleTickerProviderStateMixin {
  final _svc = SoulGardenService.instance;
  late AnimationController _treeAnim;

  @override
  void initState() {
    super.initState();
    _treeAnim = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 3),
    )..repeat(reverse: true);
  }

  @override
  void dispose() {
    _treeAnim.dispose();
    super.dispose();
  }

  void _openWriteJournal() {
    Navigator.of(context).push(MaterialPageRoute(
      builder: (_) => _JournalWritePage(onSave: (entry) {
        _svc.addEntry(entry);
        setState(() {});
        Navigator.of(context).pop();
      }),
    ));
  }

  void _openJournalList() {
    Navigator.of(context)
        .push(MaterialPageRoute(builder: (_) => _JournalListPage(svc: _svc)))
        .then((_) => setState(() {}));
  }

  void _openJournalHistory() {
    Navigator.of(context)
        .push(MaterialPageRoute(builder: (_) => _JournalHistoryPage(svc: _svc)))
        .then((_) => setState(() {}));
  }

  void _openAnalytics() {
    Navigator.of(context)
        .push(MaterialPageRoute(builder: (_) => const MoodAnalyticsPage()))
        .then((_) => setState(() {}));
  }

  void _openAchievements() {
    Navigator.of(context)
        .push(MaterialPageRoute(builder: (_) => const AchievementsPage()))
        .then((_) => setState(() {}));
  }

  void _openBreathing() {
    Navigator.of(context)
        .push(MaterialPageRoute(builder: (_) => const BreathingExercisePage()));
  }

  void _showEntryDetail(JournalEntry entry) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (_) => _EntryDetailSheet(entry: entry),
    );
  }

  @override
  Widget build(BuildContext context) {
    final tree = _svc.treeState;
    final entries = _svc.entries;
    final unlocked = _svc.unlockedAchievements;

    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [Color(0xFF1B4332), Color(0xFF2D6A4F), Color(0xFF40916C)],
          ),
        ),
        child: SafeArea(
          child: SingleChildScrollView(
            padding: const EdgeInsets.fromLTRB(20, 16, 20, 32),
            child: Column(
              children: [
                _buildHeader(),
                const SizedBox(height: 24),
                _buildTreeCard(tree),
                const SizedBox(height: 20),
                _buildWeeklyMood(entries),
                const SizedBox(height: 20),
                _buildActionButtons(),
                const SizedBox(height: 16),
                _buildQuickLinks(),
                const SizedBox(height: 20),
                if (unlocked.isNotEmpty) ...[
                  _buildAchievementPreview(unlocked),
                  const SizedBox(height: 20),
                ],
                if (entries.isNotEmpty) _buildRecentEntries(entries),
              ],
            ),
          ),
        ),
      ),
    );
  }

  // ─── HEADER ──────────────────────────────────

  Widget _buildHeader() {
    return Row(
      children: [
        const Text('🌳', style: TextStyle(fontSize: 32)),
        const SizedBox(width: 12),
        Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('Vườn Tâm Hồn',
                style: TextStyle(
                    color: Colors.white,
                    fontSize: 24,
                    fontWeight: FontWeight.w700)),
            Text('Chăm sóc tâm hồn mỗi ngày',
                style: TextStyle(
                    color: Colors.white.withOpacity(0.7), fontSize: 14)),
          ],
        ),
        const Spacer(),
        GestureDetector(
          onTap: _openJournalHistory,
          child: Container(
            padding: const EdgeInsets.all(10),
            decoration: BoxDecoration(
              color: Colors.white.withOpacity(0.12),
              borderRadius: BorderRadius.circular(14),
            ),
            child: const Icon(Icons.calendar_month_rounded,
                color: Colors.white70, size: 22),
          ),
        ),
      ],
    );
  }

  // ─── TREE CARD (MOOD-BASED EVOLUTION) ────────

  Widget _buildTreeCard(TreeState tree) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.1),
        borderRadius: BorderRadius.circular(24),
        border: Border.all(color: Colors.white.withOpacity(0.15)),
      ),
      child: Column(
        children: [
          AnimatedBuilder(
            animation: _treeAnim,
            builder: (_, __) {
              return Transform.scale(
                scale: 1.0 + _treeAnim.value * 0.05,
                child: Text(tree.emoji, style: const TextStyle(fontSize: 72)),
              );
            },
          ),
          const SizedBox(height: 12),
          Text(tree.name,
              style: const TextStyle(
                  color: Colors.white,
                  fontSize: 20,
                  fontWeight: FontWeight.bold)),
          const SizedBox(height: 4),
          Text(tree.description,
              style: TextStyle(
                  color: Colors.white.withOpacity(0.6), fontSize: 13)),
          const SizedBox(height: 14),
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              _statBadge('🔥', '${_svc.streak} ngày streak'),
              const SizedBox(width: 16),
              _statBadge('📝', '${_svc.entries.length} bài viết'),
            ],
          ),
        ],
      ),
    );
  }

  Widget _statBadge(String emoji, String text) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 6),
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.12),
        borderRadius: BorderRadius.circular(20),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Text(emoji, style: const TextStyle(fontSize: 16)),
          const SizedBox(width: 6),
          Text(text,
              style: const TextStyle(color: Colors.white70, fontSize: 13)),
        ],
      ),
    );
  }

  // ─── WEEKLY MOOD ─────────────────────────────

  Widget _buildWeeklyMood(List<JournalEntry> entries) {
    final now = DateTime.now();
    final days = ['T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'CN'];

    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.1),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: Colors.white.withOpacity(0.12)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Expanded(
                child: Text('Tâm trạng tuần này',
                    style: TextStyle(
                        color: Colors.white,
                        fontSize: 16,
                        fontWeight: FontWeight.w600)),
              ),
              GestureDetector(
                onTap: _openAnalytics,
                child: const Text('Phân tích →',
                    style: TextStyle(
                        color: Color(0xFF95D5B2),
                        fontSize: 13,
                        fontWeight: FontWeight.w500)),
              ),
            ],
          ),
          const SizedBox(height: 16),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: List.generate(7, (i) {
              final dayDate = now.subtract(Duration(days: now.weekday - 1 - i));
              final entry = entries.cast<JournalEntry?>().firstWhere(
                    (e) =>
                        e!.date.year == dayDate.year &&
                        e.date.month == dayDate.month &&
                        e.date.day == dayDate.day,
                    orElse: () => null,
                  );
              final isToday = dayDate.day == now.day &&
                  dayDate.month == now.month &&
                  dayDate.year == now.year;

              return Column(
                children: [
                  Text(days[i],
                      style: TextStyle(
                          color: Colors.white.withOpacity(0.5), fontSize: 11)),
                  const SizedBox(height: 6),
                  Container(
                    width: 36,
                    height: 36,
                    decoration: BoxDecoration(
                      color: isToday
                          ? Colors.white.withOpacity(0.2)
                          : Colors.transparent,
                      borderRadius: BorderRadius.circular(10),
                      border: isToday
                          ? Border.all(
                              color: const Color(0xFF52B788), width: 1.5)
                          : null,
                    ),
                    child: Center(
                      child: Text(
                        entry?.mood.emoji ?? '·',
                        style: TextStyle(fontSize: entry != null ? 20 : 14),
                      ),
                    ),
                  ),
                ],
              );
            }),
          ),
        ],
      ),
    );
  }

  // ─── ACTION BUTTONS ──────────────────────────

  Widget _buildActionButtons() {
    return SizedBox(
      width: double.infinity,
      height: 56,
      child: ElevatedButton(
        onPressed: _openWriteJournal,
        style: ElevatedButton.styleFrom(
          backgroundColor: const Color(0xFF52B788),
          foregroundColor: Colors.white,
          shape:
              RoundedRectangleBorder(borderRadius: BorderRadius.circular(28)),
          elevation: 4,
        ),
        child: const Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.edit_note_rounded, size: 24),
            SizedBox(width: 10),
            Text('Viết nhật ký hôm nay',
                style: TextStyle(fontSize: 16, fontWeight: FontWeight.w700)),
          ],
        ),
      ),
    );
  }

  // ─── QUICK LINKS (Analytics / Achievements / Breathing) ──

  Widget _buildQuickLinks() {
    return Row(
      children: [
        _quickLink('📊', 'Phân tích', _openAnalytics),
        const SizedBox(width: 10),
        _quickLink('🏆', 'Thành tựu', _openAchievements),
        const SizedBox(width: 10),
        _quickLink('🧘', 'Bài tập thở', _openBreathing),
      ],
    );
  }

  Widget _quickLink(String emoji, String label, VoidCallback onTap) {
    return Expanded(
      child: GestureDetector(
        onTap: onTap,
        child: Container(
          padding: const EdgeInsets.symmetric(vertical: 14),
          decoration: BoxDecoration(
            color: Colors.white.withOpacity(0.08),
            borderRadius: BorderRadius.circular(14),
            border: Border.all(color: Colors.white.withOpacity(0.08)),
          ),
          child: Column(
            children: [
              Text(emoji, style: const TextStyle(fontSize: 22)),
              const SizedBox(height: 6),
              Text(label,
                  style: TextStyle(
                      color: Colors.white.withOpacity(0.8),
                      fontSize: 12,
                      fontWeight: FontWeight.w500)),
            ],
          ),
        ),
      ),
    );
  }

  // ─── ACHIEVEMENT PREVIEW ─────────────────────

  Widget _buildAchievementPreview(List<Achievement> unlocked) {
    return GestureDetector(
      onTap: _openAchievements,
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: const Color(0xFF52B788).withOpacity(0.12),
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: const Color(0xFF52B788).withOpacity(0.25)),
        ),
        child: Row(
          children: [
            Text(unlocked.last.emoji, style: const TextStyle(fontSize: 28)),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('🎉 ${unlocked.last.title}',
                      style: const TextStyle(
                          color: Colors.white,
                          fontWeight: FontWeight.w600,
                          fontSize: 14)),
                  Text('${unlocked.length} thành tựu đã mở khóa — Xem tất cả →',
                      style: TextStyle(
                          color: Colors.white.withOpacity(0.6), fontSize: 12)),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  // ─── RECENT ENTRIES ──────────────────────────

  Widget _buildRecentEntries(List<JournalEntry> entries) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            const Text('Gần đây',
                style: TextStyle(
                    color: Colors.white,
                    fontSize: 16,
                    fontWeight: FontWeight.w600)),
            const Spacer(),
            GestureDetector(
              onTap: _openJournalList,
              child: const Text('Xem tất cả',
                  style: TextStyle(
                      color: Color(0xFF95D5B2),
                      fontSize: 13,
                      fontWeight: FontWeight.w500)),
            ),
          ],
        ),
        const SizedBox(height: 12),
        ...entries.take(3).map((e) => Padding(
              padding: const EdgeInsets.only(bottom: 10),
              child: GestureDetector(
                onTap: () => _showEntryDetail(e),
                child: Container(
                  padding: const EdgeInsets.all(14),
                  decoration: BoxDecoration(
                    color: Colors.white.withOpacity(0.08),
                    borderRadius: BorderRadius.circular(16),
                    border: Border.all(color: Colors.white.withOpacity(0.1)),
                  ),
                  child: Row(
                    children: [
                      Text(e.mood.emoji, style: const TextStyle(fontSize: 28)),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(e.mood.label,
                                style: const TextStyle(
                                    color: Colors.white,
                                    fontWeight: FontWeight.w600,
                                    fontSize: 14)),
                            if (e.content.isNotEmpty)
                              Text(
                                e.content.length > 60
                                    ? '${e.content.substring(0, 60)}...'
                                    : e.content,
                                style: TextStyle(
                                    color: Colors.white.withOpacity(0.6),
                                    fontSize: 12),
                              ),
                          ],
                        ),
                      ),
                      Text(
                        '${e.date.day}/${e.date.month}',
                        style: TextStyle(
                            color: Colors.white.withOpacity(0.4), fontSize: 12),
                      ),
                    ],
                  ),
                ),
              ),
            )),
      ],
    );
  }
}

// ══════════════════════════════════════════════
// ENTRY DETAIL BOTTOM SHEET
// ══════════════════════════════════════════════
class _EntryDetailSheet extends StatelessWidget {
  const _EntryDetailSheet({required this.entry});
  final JournalEntry entry;

  @override
  Widget build(BuildContext context) {
    return DraggableScrollableSheet(
      initialChildSize: 0.6,
      maxChildSize: 0.9,
      minChildSize: 0.4,
      builder: (_, controller) => Container(
        decoration: const BoxDecoration(
          color: Color(0xFF1B4332),
          borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
        ),
        child: ListView(
          controller: controller,
          padding: const EdgeInsets.fromLTRB(24, 12, 24, 32),
          children: [
            // Drag handle
            Center(
              child: Container(
                width: 40,
                height: 4,
                decoration: BoxDecoration(
                  color: Colors.white.withOpacity(0.3),
                  borderRadius: BorderRadius.circular(2),
                ),
              ),
            ),
            const SizedBox(height: 20),
            // Mood + date
            Row(
              children: [
                Text(entry.mood.emoji, style: const TextStyle(fontSize: 48)),
                const SizedBox(width: 16),
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(entry.mood.label,
                        style: const TextStyle(
                            color: Colors.white,
                            fontSize: 22,
                            fontWeight: FontWeight.w700)),
                    Text(
                      '${entry.date.day}/${entry.date.month}/${entry.date.year} — ${entry.date.hour.toString().padLeft(2, '0')}:${entry.date.minute.toString().padLeft(2, '0')}',
                      style: TextStyle(
                          color: Colors.white.withOpacity(0.5), fontSize: 13),
                    ),
                  ],
                ),
              ],
            ),
            const SizedBox(height: 24),
            // Content
            if (entry.content.isNotEmpty) ...[
              const Text('Nội dung',
                  style: TextStyle(
                      color: Colors.white,
                      fontSize: 15,
                      fontWeight: FontWeight.w600)),
              const SizedBox(height: 8),
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Colors.white.withOpacity(0.06),
                  borderRadius: BorderRadius.circular(14),
                ),
                child: Text(entry.content,
                    style: TextStyle(
                        color: Colors.white.withOpacity(0.8),
                        fontSize: 14,
                        height: 1.6)),
              ),
              const SizedBox(height: 20),
            ],
            // Tags
            if (entry.tags.isNotEmpty) ...[
              const Text('Cảm xúc',
                  style: TextStyle(
                      color: Colors.white,
                      fontSize: 15,
                      fontWeight: FontWeight.w600)),
              const SizedBox(height: 8),
              Wrap(
                spacing: 8,
                runSpacing: 8,
                children: entry.tags.map((t) {
                  return Container(
                    padding:
                        const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                    decoration: BoxDecoration(
                      color: const Color(0xFF52B788).withOpacity(0.15),
                      borderRadius: BorderRadius.circular(20),
                    ),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Text(t.emoji, style: const TextStyle(fontSize: 16)),
                        const SizedBox(width: 6),
                        Text(t.label,
                            style: TextStyle(
                                color: Colors.white.withOpacity(0.8),
                                fontSize: 13)),
                      ],
                    ),
                  );
                }).toList(),
              ),
              const SizedBox(height: 20),
            ],
            // Mock AI Analysis
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: const Color(0xFF60A5FA).withOpacity(0.1),
                borderRadius: BorderRadius.circular(14),
                border:
                    Border.all(color: const Color(0xFF60A5FA).withOpacity(0.2)),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Row(
                    children: [
                      Icon(Icons.auto_awesome,
                          color: Color(0xFF60A5FA), size: 18),
                      SizedBox(width: 8),
                      Text('Phân tích AI',
                          style: TextStyle(
                              color: Color(0xFF60A5FA),
                              fontSize: 14,
                              fontWeight: FontWeight.w600)),
                    ],
                  ),
                  const SizedBox(height: 10),
                  Text(
                    _getAiAnalysis(entry),
                    style: TextStyle(
                        color: Colors.white.withOpacity(0.7),
                        fontSize: 13,
                        height: 1.5),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  String _getAiAnalysis(JournalEntry entry) {
    if (entry.mood.isPositive) {
      return 'Tâm trạng tích cực! Việc ghi nhận những khoảnh khắc vui vẻ giúp cải thiện sức khỏe tinh thần. Hãy tiếp tục duy trì thói quen này nhé. 🌟';
    } else if (entry.mood.isNegative) {
      return 'Mọi người đều có những ngày không tốt, và việc ghi lại cảm xúc là bước đầu rất tốt. Hãy thử bài tập thở 4-7-8 để thư giãn. Nếu tâm trạng kéo dài, hãy nói chuyện với ai đó bạn tin tưởng. 💛';
    } else {
      return 'Ngày bình thường cũng đáng ghi nhận. Hãy chú ý đến những điều nhỏ làm bạn vui trong ngày — chúng tích lũy tạo nên hạnh phúc lớn. ☀️';
    }
  }
}

// ══════════════════════════════════════════════
// JOURNAL WRITE PAGE (Mood → Content → Save)
// ══════════════════════════════════════════════
class _JournalWritePage extends StatefulWidget {
  const _JournalWritePage({required this.onSave});
  final ValueChanged<JournalEntry> onSave;

  @override
  State<_JournalWritePage> createState() => _JournalWritePageState();
}

class _JournalWritePageState extends State<_JournalWritePage> {
  Mood? _selectedMood;
  final _contentController = TextEditingController();
  final Set<EmotionTag> _selectedTags = {};
  bool _showContent = false;

  @override
  void dispose() {
    _contentController.dispose();
    super.dispose();
  }

  void _save() {
    if (_selectedMood == null) return;
    final entry = JournalEntry(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      date: DateTime.now(),
      mood: _selectedMood!,
      content: _contentController.text.trim(),
      tags: Set.unmodifiable(_selectedTags),
    );
    widget.onSave(entry);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [Color(0xFF1B4332), Color(0xFF2D6A4F), Color(0xFF40916C)],
          ),
        ),
        child: SafeArea(
          child: Column(
            children: [
              // Header
              Padding(
                padding: const EdgeInsets.fromLTRB(16, 8, 16, 0),
                child: Row(
                  children: [
                    IconButton(
                      icon: const Icon(Icons.close, color: Colors.white70),
                      onPressed: () => Navigator.of(context).pop(),
                    ),
                    const Expanded(
                      child: Text('Viết nhật ký',
                          textAlign: TextAlign.center,
                          style: TextStyle(
                              color: Colors.white,
                              fontSize: 18,
                              fontWeight: FontWeight.w600)),
                    ),
                    const SizedBox(width: 48),
                  ],
                ),
              ),
              Expanded(
                child: SingleChildScrollView(
                  padding: const EdgeInsets.all(24),
                  child: _showContent ? _buildContentStep() : _buildMoodStep(),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildMoodStep() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text('Hôm nay bạn cảm thấy thế nào?',
            style: TextStyle(
                color: Colors.white,
                fontSize: 22,
                fontWeight: FontWeight.w700)),
        const SizedBox(height: 8),
        Text('Chọn tâm trạng phù hợp nhất',
            style:
                TextStyle(color: Colors.white.withOpacity(0.6), fontSize: 14)),
        const SizedBox(height: 32),
        ...Mood.values.map((m) => Padding(
              padding: const EdgeInsets.only(bottom: 12),
              child: GestureDetector(
                onTap: () {
                  HapticFeedback.selectionClick();
                  setState(() {
                    _selectedMood = m;
                    _showContent = true;
                  });
                },
                child: Container(
                  padding: const EdgeInsets.all(18),
                  decoration: BoxDecoration(
                    color: _selectedMood == m
                        ? m.color.withOpacity(0.25)
                        : Colors.white.withOpacity(0.08),
                    borderRadius: BorderRadius.circular(20),
                    border: Border.all(
                      color: _selectedMood == m
                          ? m.color.withOpacity(0.5)
                          : Colors.white.withOpacity(0.1),
                      width: _selectedMood == m ? 2 : 1,
                    ),
                  ),
                  child: Row(
                    children: [
                      Text(m.emoji, style: const TextStyle(fontSize: 36)),
                      const SizedBox(width: 16),
                      Text(m.label,
                          style: const TextStyle(
                              color: Colors.white,
                              fontSize: 18,
                              fontWeight: FontWeight.w600)),
                    ],
                  ),
                ),
              ),
            )),
      ],
    );
  }

  Widget _buildContentStep() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Selected mood
        GestureDetector(
          onTap: () => setState(() => _showContent = false),
          child: Row(
            children: [
              Text(_selectedMood!.emoji, style: const TextStyle(fontSize: 32)),
              const SizedBox(width: 12),
              Text(_selectedMood!.label,
                  style: const TextStyle(
                      color: Colors.white,
                      fontSize: 18,
                      fontWeight: FontWeight.w600)),
              const SizedBox(width: 8),
              Icon(Icons.edit, color: Colors.white.withOpacity(0.4), size: 16),
            ],
          ),
        ),
        const SizedBox(height: 24),
        const Text('Có gì muốn chia sẻ không?',
            style: TextStyle(
                color: Colors.white,
                fontSize: 18,
                fontWeight: FontWeight.w600)),
        const SizedBox(height: 12),
        Container(
          decoration: BoxDecoration(
            color: Colors.white.withOpacity(0.08),
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: Colors.white.withOpacity(0.12)),
          ),
          child: TextField(
            controller: _contentController,
            maxLines: 6,
            style: const TextStyle(color: Colors.white, fontSize: 15),
            decoration: InputDecoration(
              hintText: 'Viết những gì bạn muốn...',
              hintStyle:
                  TextStyle(color: Colors.white.withOpacity(0.3), fontSize: 15),
              border: InputBorder.none,
              contentPadding: const EdgeInsets.all(16),
            ),
          ),
        ),
        const SizedBox(height: 20),
        const Text('Cảm xúc',
            style: TextStyle(
                color: Colors.white,
                fontSize: 16,
                fontWeight: FontWeight.w600)),
        const SizedBox(height: 12),
        Wrap(
          spacing: 8,
          runSpacing: 8,
          children: EmotionTag.values.map((tag) {
            final selected = _selectedTags.contains(tag);
            return GestureDetector(
              onTap: () {
                HapticFeedback.selectionClick();
                setState(() {
                  if (selected) {
                    _selectedTags.remove(tag);
                  } else {
                    _selectedTags.add(tag);
                  }
                });
              },
              child: Container(
                padding:
                    const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
                decoration: BoxDecoration(
                  color: selected
                      ? const Color(0xFF52B788).withOpacity(0.3)
                      : Colors.white.withOpacity(0.08),
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(
                    color: selected
                        ? const Color(0xFF52B788)
                        : Colors.white.withOpacity(0.1),
                  ),
                ),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Text(tag.emoji, style: const TextStyle(fontSize: 16)),
                    const SizedBox(width: 6),
                    Text(tag.label,
                        style: TextStyle(
                            color: Colors.white.withOpacity(0.8),
                            fontSize: 13)),
                  ],
                ),
              ),
            );
          }).toList(),
        ),
        const SizedBox(height: 32),
        SizedBox(
          width: double.infinity,
          height: 54,
          child: ElevatedButton(
            onPressed: _save,
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFF52B788),
              foregroundColor: Colors.white,
              shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(27)),
              elevation: 4,
            ),
            child: const Text('Lưu nhật ký',
                style: TextStyle(fontSize: 16, fontWeight: FontWeight.w700)),
          ),
        ),
      ],
    );
  }
}

// ══════════════════════════════════════════════
// JOURNAL LIST PAGE (Recent entries + achievements)
// ══════════════════════════════════════════════
class _JournalListPage extends StatelessWidget {
  const _JournalListPage({required this.svc});
  final SoulGardenService svc;

  @override
  Widget build(BuildContext context) {
    final entries = svc.entries;

    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [Color(0xFF1B4332), Color(0xFF2D6A4F)],
          ),
        ),
        child: SafeArea(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Padding(
                padding: const EdgeInsets.fromLTRB(8, 8, 16, 0),
                child: Row(
                  children: [
                    IconButton(
                      icon: const Icon(Icons.arrow_back_ios,
                          color: Colors.white70),
                      onPressed: () => Navigator.pop(context),
                    ),
                    const Text('Danh sách nhật ký',
                        style: TextStyle(
                            color: Colors.white,
                            fontSize: 18,
                            fontWeight: FontWeight.w600)),
                  ],
                ),
              ),
              // Achievements
              Padding(
                padding: const EdgeInsets.fromLTRB(20, 16, 20, 8),
                child: Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: Colors.white.withOpacity(0.08),
                    borderRadius: BorderRadius.circular(16),
                  ),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceAround,
                    children: [
                      _achievementBadge('📝', '${entries.length}', 'Bài viết'),
                      _achievementBadge('🔥', '${svc.streak}', 'Streak'),
                      _achievementBadge('🏆', '${(entries.length / 7).floor()}',
                          'Tuần đều đặn'),
                    ],
                  ),
                ),
              ),
              Expanded(
                child: entries.isEmpty
                    ? Center(
                        child: Column(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            const Text('🌱', style: TextStyle(fontSize: 48)),
                            const SizedBox(height: 12),
                            Text('Chưa có nhật ký nào',
                                style: TextStyle(
                                    color: Colors.white.withOpacity(0.5),
                                    fontSize: 16)),
                          ],
                        ),
                      )
                    : ListView.builder(
                        padding: const EdgeInsets.fromLTRB(20, 8, 20, 32),
                        itemCount: entries.length,
                        itemBuilder: (_, i) => _buildEntryCard(entries[i]),
                      ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _achievementBadge(String emoji, String value, String label) {
    return Column(
      children: [
        Text(emoji, style: const TextStyle(fontSize: 24)),
        const SizedBox(height: 4),
        Text(value,
            style: const TextStyle(
                color: Colors.white,
                fontSize: 18,
                fontWeight: FontWeight.bold)),
        Text(label,
            style:
                TextStyle(color: Colors.white.withOpacity(0.5), fontSize: 11)),
      ],
    );
  }

  Widget _buildEntryCard(JournalEntry entry) {
    return Container(
      margin: const EdgeInsets.only(bottom: 10),
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.08),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.white.withOpacity(0.08)),
      ),
      child: Row(
        children: [
          Text(entry.mood.emoji, style: const TextStyle(fontSize: 28)),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Text(entry.mood.label,
                        style: const TextStyle(
                            color: Colors.white,
                            fontWeight: FontWeight.w600,
                            fontSize: 14)),
                    const Spacer(),
                    Text(
                      '${entry.date.day}/${entry.date.month}/${entry.date.year}',
                      style: TextStyle(
                          color: Colors.white.withOpacity(0.4), fontSize: 12),
                    ),
                  ],
                ),
                if (entry.content.isNotEmpty) ...[
                  const SizedBox(height: 4),
                  Text(
                    entry.content.length > 80
                        ? '${entry.content.substring(0, 80)}...'
                        : entry.content,
                    style: TextStyle(
                        color: Colors.white.withOpacity(0.6), fontSize: 13),
                  ),
                ],
                if (entry.tags.isNotEmpty) ...[
                  const SizedBox(height: 6),
                  Wrap(
                    spacing: 4,
                    children: entry.tags
                        .map((t) =>
                            Text(t.emoji, style: const TextStyle(fontSize: 14)))
                        .toList(),
                  ),
                ],
              ],
            ),
          ),
        ],
      ),
    );
  }
}

// ══════════════════════════════════════════════
// JOURNAL HISTORY PAGE (Calendar + full list)
// ══════════════════════════════════════════════
class _JournalHistoryPage extends StatefulWidget {
  const _JournalHistoryPage({required this.svc});
  final SoulGardenService svc;

  @override
  State<_JournalHistoryPage> createState() => _JournalHistoryPageState();
}

class _JournalHistoryPageState extends State<_JournalHistoryPage> {
  late DateTime _displayedMonth;

  @override
  void initState() {
    super.initState();
    _displayedMonth = DateTime(DateTime.now().year, DateTime.now().month);
  }

  void _prevMonth() {
    setState(() {
      _displayedMonth =
          DateTime(_displayedMonth.year, _displayedMonth.month - 1);
    });
  }

  void _nextMonth() {
    setState(() {
      _displayedMonth =
          DateTime(_displayedMonth.year, _displayedMonth.month + 1);
    });
  }

  Mood? _moodForDay(int day) {
    final entries =
        widget.svc.entriesForMonth(_displayedMonth.year, _displayedMonth.month);
    final entry = entries.cast<JournalEntry?>().firstWhere(
          (e) => e!.date.day == day,
          orElse: () => null,
        );
    return entry?.mood;
  }

  @override
  Widget build(BuildContext context) {
    final daysInMonth =
        DateUtils.getDaysInMonth(_displayedMonth.year, _displayedMonth.month);
    final firstWeekday =
        DateTime(_displayedMonth.year, _displayedMonth.month, 1).weekday;
    final months = [
      'Tháng 1',
      'Tháng 2',
      'Tháng 3',
      'Tháng 4',
      'Tháng 5',
      'Tháng 6',
      'Tháng 7',
      'Tháng 8',
      'Tháng 9',
      'Tháng 10',
      'Tháng 11',
      'Tháng 12',
    ];

    final monthEntries =
        widget.svc.entriesForMonth(_displayedMonth.year, _displayedMonth.month);

    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [Color(0xFF1B4332), Color(0xFF2D6A4F)],
          ),
        ),
        child: SafeArea(
          child: Column(
            children: [
              Padding(
                padding: const EdgeInsets.fromLTRB(8, 8, 16, 0),
                child: Row(
                  children: [
                    IconButton(
                      icon: const Icon(Icons.arrow_back_ios,
                          color: Colors.white70),
                      onPressed: () => Navigator.pop(context),
                    ),
                    const Text('Lịch sử nhật ký',
                        style: TextStyle(
                            color: Colors.white,
                            fontSize: 18,
                            fontWeight: FontWeight.w600)),
                  ],
                ),
              ),
              // Month navigator
              Padding(
                padding: const EdgeInsets.fromLTRB(20, 16, 20, 8),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    IconButton(
                      icon: const Icon(Icons.chevron_left, color: Colors.white),
                      onPressed: _prevMonth,
                    ),
                    Text(
                      '${months[_displayedMonth.month - 1]} ${_displayedMonth.year}',
                      style: const TextStyle(
                          color: Colors.white,
                          fontSize: 16,
                          fontWeight: FontWeight.w600),
                    ),
                    IconButton(
                      icon:
                          const Icon(Icons.chevron_right, color: Colors.white),
                      onPressed: _nextMonth,
                    ),
                  ],
                ),
              ),
              // Calendar grid
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 20),
                child: Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: Colors.white.withOpacity(0.08),
                    borderRadius: BorderRadius.circular(16),
                  ),
                  child: Column(
                    children: [
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceAround,
                        children: ['T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'CN']
                            .map((d) => SizedBox(
                                  width: 36,
                                  child: Text(d,
                                      textAlign: TextAlign.center,
                                      style: TextStyle(
                                          color: Colors.white.withOpacity(0.4),
                                          fontSize: 11)),
                                ))
                            .toList(),
                      ),
                      const SizedBox(height: 8),
                      ...List.generate(
                        ((daysInMonth + firstWeekday - 1) / 7).ceil(),
                        (week) {
                          return Padding(
                            padding: const EdgeInsets.symmetric(vertical: 2),
                            child: Row(
                              mainAxisAlignment: MainAxisAlignment.spaceAround,
                              children: List.generate(7, (wd) {
                                final day =
                                    week * 7 + wd - (firstWeekday - 1) + 1;
                                if (day < 1 || day > daysInMonth) {
                                  return const SizedBox(width: 36, height: 36);
                                }
                                final mood = _moodForDay(day);
                                return SizedBox(
                                  width: 36,
                                  height: 36,
                                  child: Center(
                                    child: mood != null
                                        ? Text(mood.emoji,
                                            style:
                                                const TextStyle(fontSize: 18))
                                        : Text('$day',
                                            style: TextStyle(
                                                color: Colors.white
                                                    .withOpacity(0.3),
                                                fontSize: 13)),
                                  ),
                                );
                              }),
                            ),
                          );
                        },
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 16),
              // List of entries for this month
              Expanded(
                child: ListView(
                  padding: const EdgeInsets.fromLTRB(20, 0, 20, 32),
                  children: monthEntries
                      .map((e) => Container(
                            margin: const EdgeInsets.only(bottom: 8),
                            padding: const EdgeInsets.all(12),
                            decoration: BoxDecoration(
                              color: Colors.white.withOpacity(0.06),
                              borderRadius: BorderRadius.circular(14),
                            ),
                            child: Row(
                              children: [
                                Text(e.mood.emoji,
                                    style: const TextStyle(fontSize: 24)),
                                const SizedBox(width: 10),
                                Expanded(
                                  child: Column(
                                    crossAxisAlignment:
                                        CrossAxisAlignment.start,
                                    children: [
                                      Text(
                                        'Ngày ${e.date.day} — ${e.mood.label}',
                                        style: const TextStyle(
                                            color: Colors.white,
                                            fontSize: 13,
                                            fontWeight: FontWeight.w500),
                                      ),
                                      if (e.content.isNotEmpty)
                                        Text(
                                          e.content.length > 50
                                              ? '${e.content.substring(0, 50)}...'
                                              : e.content,
                                          style: TextStyle(
                                              color:
                                                  Colors.white.withOpacity(0.5),
                                              fontSize: 12),
                                        ),
                                    ],
                                  ),
                                ),
                              ],
                            ),
                          ))
                      .toList(),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
