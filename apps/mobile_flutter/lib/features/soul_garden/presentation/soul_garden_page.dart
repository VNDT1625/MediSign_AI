import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import '../../../core/models/garden_item.dart';
import '../../../core/models/journal_entry.dart';
import '../../../core/services/soul_garden_service.dart';
import 'achievements_page.dart';
import 'breathing_exercise_page.dart';
import 'garden_shop_page.dart';
import 'journal_compose_page.dart';
import 'mood_analytics_page.dart';

// ── Light theme tokens (đồng bộ các tab khác) ──
const _kBrand = Color(0xFF0284C7);
const _kBrandLight = Color(0xFF38BDF8);
const _kBg = Color(0xFFF8FAFC);
const _kBorder = Color(0xFFE2E8F0);
const _kInk = Color(0xFF0F172A);
const _kInkSoft = Color(0xFF475569);
const _kInkMuted = Color(0xFF94A3B8);

// ── Soul Garden palette (xanh lá tự nhiên) ──
const _kLeaf = Color(0xFF16A34A);
const _kLeafLight = Color(0xFF22C55E);
const _kLeafSoft = Color(0xFFDCFCE7);
const _kLeafSofter = Color(0xFFF0FDF4);

// ── Mood palette ──
const _kMoodHappy = Color(0xFFF59E0B);
const _kMoodHappyBg = Color(0xFFFEF3C7);
const _kMoodCalm = _kLeafLight;
const _kMoodCalmBg = _kLeafSoft;
const _kMoodStress = Color(0xFF8B5CF6);
const _kMoodStressBg = Color(0xFFEDE9FE);
const _kMoodSad = Color(0xFF3B82F6);
const _kMoodSadBg = Color(0xFFDBEAFE);
const _kMoodTired = Color(0xFFF97316);
const _kMoodTiredBg = Color(0xFFFFEDD5);

enum _Mood { happy, calm, stress, sad, tired }

/// Maps the local UI _Mood enum to the domain Mood enum.
Mood _toDomainMood(_Mood m) {
  switch (m) {
    case _Mood.happy:
      return Mood.awesome;
    case _Mood.calm:
      return Mood.good;
    case _Mood.stress:
    case _Mood.tired:
      return Mood.neutral;
    case _Mood.sad:
      return Mood.sad;
  }
}

/// Soul Garden — light theme, wired to SoulGardenService.
class SoulGardenPage extends StatefulWidget {
  const SoulGardenPage({super.key});

  @override
  State<SoulGardenPage> createState() => _SoulGardenPageState();
}

class _SoulGardenPageState extends State<SoulGardenPage> {
  _Mood _selectedMood = _Mood.calm;
  final _svc = SoulGardenService.instance;

  void _saveMood() {
    HapticFeedback.lightImpact();
    // Add a quick mood entry without detailed content
    final entry = JournalEntry(
      id: 'mood_${DateTime.now().millisecondsSinceEpoch}',
      date: DateTime.now(),
      mood: _toDomainMood(_selectedMood),
      content: '',
      tags: const {},
    );
    _svc.addEntry(entry);
    setState(() {}); // refresh hero stats
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: const Text('Đã lưu cảm xúc hôm nay'),
        behavior: SnackBarBehavior.floating,
        backgroundColor: _kLeaf,
        duration: const Duration(seconds: 2),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      ),
    );
  }

  Future<void> _openJournalCompose() async {
    await Navigator.push<JournalEntry>(
      context,
      MaterialPageRoute(builder: (_) => const JournalComposePage()),
    );
    setState(() {}); // refresh after returning
  }

  void _openAnalytics() {
    Navigator.push(
      context,
      MaterialPageRoute(builder: (_) => const MoodAnalyticsPage()),
    );
  }

  void _openAchievements() {
    Navigator.push(
      context,
      MaterialPageRoute(builder: (_) => const AchievementsPage()),
    );
  }

  void _openGardenShop() {
    Navigator.push(
      context,
      MaterialPageRoute(builder: (_) => const GardenShopPage()),
    ).then((_) => setState(() {}));
  }

  void _openBreathing() {
    Navigator.push(
      context,
      MaterialPageRoute(builder: (_) => const BreathingExercisePage()),
    );
  }

  @override
  Widget build(BuildContext context) {
    final recentEntries = _svc.entries.take(4).toList();

    return Scaffold(
      backgroundColor: _kBg,
      body: SafeArea(
        bottom: false,
        child: Column(
          children: [
            _SgHeader(onAchievementsTap: _openAchievements),
            Expanded(
              child: ListView(
                padding: const EdgeInsets.fromLTRB(16, 4, 16, 24),
                physics: const BouncingScrollPhysics(),
                children: [
                  _PageTitle(onGardenShopTap: _openGardenShop),
                  const SizedBox(height: 12),
                  _GardenStatusHero(
                    svc: _svc,
                    onCustomizeTap: _openGardenShop,
                  ),
                  const SizedBox(height: 14),
                  _MoodPickerCard(
                    selected: _selectedMood,
                    onChanged: (m) => setState(() => _selectedMood = m),
                    onSave: _saveMood,
                    onWriteJournal: _openJournalCompose,
                  ),
                  const SizedBox(height: 18),
                  _SectionHeader(
                    title: 'Nhật ký gần đây',
                    actionLabel: 'Xem tất cả',
                    onActionTap: _openAnalytics,
                  ),
                  const SizedBox(height: 8),
                  if (recentEntries.isEmpty)
                    _EmptyJournalBanner(onTap: _openJournalCompose)
                  else
                    _JournalGrid(
                      entries: recentEntries,
                      onTap: (e) => _openJournalCompose(),
                      onWriteNew: _openJournalCompose,
                    ),
                  const SizedBox(height: 16),
                  _SectionHeader(
                    title: 'Bài tập đề xuất',
                    actionLabel: 'Xem tất cả',
                    onActionTap: () {},
                  ),
                  const SizedBox(height: 8),
                  Row(
                    children: [
                      Expanded(
                        child: _ExerciseCard(
                          duration: '3 phút',
                          title: 'Hít thở 3 phút',
                          desc: 'Giảm căng thẳng nhanh',
                          tone: _ExerciseTone.cloud,
                          onTap: _openBreathing,
                        ),
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: _ExerciseCard(
                          duration: '5 phút',
                          title: 'Thiền ngắn',
                          desc: 'Tập trung & thư giãn',
                          tone: _ExerciseTone.leaf,
                          onTap: _openBreathing,
                        ),
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: _ExerciseCard(
                          duration: '10 phút',
                          title: 'Nhạc thư giãn',
                          desc: 'Thư giãn & ngủ ngon',
                          tone: _ExerciseTone.peach,
                          onTap: () {},
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 16),
                  _SectionHeader(
                    title: 'Khu vườn cảm xúc',
                    actionLabel: 'Xem tiến trình',
                    onActionTap: _openAchievements,
                  ),
                  const SizedBox(height: 10),
                  _GrowthTimeline(svc: _svc),
                ],
              ),
            ),
          ],
        ),
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: _openJournalCompose,
        backgroundColor: _kLeaf,
        foregroundColor: Colors.white,
        elevation: 3,
        icon: const Icon(Icons.edit_rounded, size: 20),
        label: const Text(
          'Viết nhật ký',
          style: TextStyle(
            fontFamily: 'Outfit',
            fontSize: 14,
            fontWeight: FontWeight.w700,
          ),
        ),
      ),
    );
  }
}

// ───────────────────────── HEADER ─────────────────────────

class _SgHeader extends StatelessWidget {
  const _SgHeader({this.onAchievementsTap});
  final VoidCallback? onAchievementsTap;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(8, 4, 8, 4),
      child: Row(
        children: [
          _SquareIconBtn(icon: Icons.menu_rounded, onTap: () {}),
          const SizedBox(width: 6),
          _ShieldLogo(),
          const SizedBox(width: 8),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'MediSign AI',
                  style: TextStyle(
                    fontFamily: 'Outfit',
                    fontSize: 18,
                    fontWeight: FontWeight.w800,
                    color: _kInk,
                    height: 1.1,
                  ),
                ),
                const SizedBox(height: 2),
                Row(
                  children: const [
                    _Dot(color: _kLeafLight),
                    SizedBox(width: 6),
                    Text(
                      'Chăm sóc sức khỏe mỗi ngày',
                      style: TextStyle(
                        fontFamily: 'Outfit',
                        fontSize: 11,
                        color: _kInkSoft,
                        height: 1.1,
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
          _CircleIconBtn(icon: Icons.notifications_outlined, badge: true),
          const SizedBox(width: 6),
          _CircleIconBtn(
            icon: Icons.emoji_events_rounded,
            onTap: onAchievementsTap,
          ),
        ],
      ),
    );
  }
}

class _ShieldLogo extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Container(
      width: 32,
      height: 32,
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [_kBrand, _kBrandLight],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(8),
        boxShadow: [
          BoxShadow(
            color: _kBrand.withOpacity(0.25),
            blurRadius: 6,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: const Icon(Icons.medical_services_rounded,
          color: Colors.white, size: 18),
    );
  }
}

class _SquareIconBtn extends StatelessWidget {
  const _SquareIconBtn({required this.icon, required this.onTap});
  final IconData icon;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return InkResponse(
      onTap: () {
        HapticFeedback.selectionClick();
        onTap();
      },
      radius: 24,
      child: SizedBox(
        width: 40,
        height: 40,
        child: Icon(icon, size: 20, color: _kInkSoft),
      ),
    );
  }
}

class _CircleIconBtn extends StatelessWidget {
  const _CircleIconBtn({required this.icon, this.badge = false, this.onTap});
  final IconData icon;
  final bool badge;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    return InkResponse(
      onTap: () {
        HapticFeedback.selectionClick();
        onTap?.call();
      },
      radius: 24,
      child: Container(
        width: 40,
        height: 40,
        decoration: BoxDecoration(
          color: Colors.white,
          shape: BoxShape.circle,
          border: Border.all(color: _kBorder),
        ),
        child: Stack(
          alignment: Alignment.center,
          children: [
            Icon(icon, size: 19, color: _kInkSoft),
            if (badge)
              Positioned(
                top: 8,
                right: 10,
                child: Container(
                  width: 8,
                  height: 8,
                  decoration: BoxDecoration(
                    color: const Color(0xFFEF4444),
                    shape: BoxShape.circle,
                    border: Border.all(color: Colors.white, width: 1.5),
                  ),
                ),
              ),
          ],
        ),
      ),
    );
  }
}

class _Dot extends StatelessWidget {
  const _Dot({required this.color});
  final Color color;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 6,
      height: 6,
      decoration: BoxDecoration(color: color, shape: BoxShape.circle),
    );
  }
}

// ───────────────────────── PAGE TITLE ─────────────────────────

class _PageTitle extends StatelessWidget {
  const _PageTitle({this.onGardenShopTap});
  final VoidCallback? onGardenShopTap;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 4),
      child: Row(
        children: [
          const Icon(Icons.eco_rounded, size: 22, color: _kLeaf),
          const SizedBox(width: 8),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisSize: MainAxisSize.min,
              children: const [
                Text(
                  'Soul Garden',
                  style: TextStyle(
                    fontFamily: 'Outfit',
                    fontSize: 22,
                    fontWeight: FontWeight.w800,
                    color: _kInk,
                    height: 1.1,
                  ),
                ),
                SizedBox(height: 2),
                Text(
                  'Theo dõi cảm xúc & chăm sóc tinh thần',
                  style: TextStyle(
                    fontFamily: 'Outfit',
                    fontSize: 12,
                    color: _kInkSoft,
                  ),
                ),
              ],
            ),
          ),
          _GuideButton(onTap: onGardenShopTap),
        ],
      ),
    );
  }
}

class _GuideButton extends StatelessWidget {
  const _GuideButton({this.onTap});
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    return Material(
      color: _kLeafSofter,
      borderRadius: BorderRadius.circular(999),
      child: InkWell(
        onTap: () {
          HapticFeedback.selectionClick();
          onTap?.call();
        },
        borderRadius: BorderRadius.circular(999),
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 7),
          decoration: BoxDecoration(
            border: Border.all(color: _kLeafSoft),
            borderRadius: BorderRadius.circular(999),
          ),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: const [
              Icon(Icons.store_rounded, size: 13, color: _kLeaf),
              SizedBox(width: 5),
              Text(
                'Tùy chỉnh vườn',
                style: TextStyle(
                  fontFamily: 'Outfit',
                  fontSize: 12,
                  fontWeight: FontWeight.w700,
                  color: _kLeaf,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

// ───────────────────────── GARDEN STATUS HERO ─────────────────────────

class _GardenStatusHero extends StatelessWidget {
  const _GardenStatusHero({required this.svc, this.onCustomizeTap});
  final SoulGardenService svc;
  final VoidCallback? onCustomizeTap;

  @override
  Widget build(BuildContext context) {
    final treeState = svc.treeState;
    final streak = svc.streak;
    final tree = svc.equippedItem(GardenCategory.tree);
    final pot = svc.equippedItem(GardenCategory.pot);
    final acc = svc.equippedItem(GardenCategory.accessory);

    final stats = svc.statsForDays(7);
    final moodLabel = stats.averageScore >= 4.0
        ? 'Tích cực'
        : stats.averageScore >= 3.0
            ? 'Bình yên'
            : stats.averageScore >= 2.0
                ? 'Hơi mệt'
                : 'Cần nghỉ ngơi';

    return GestureDetector(
      onTap: onCustomizeTap,
      child: Container(
        decoration: BoxDecoration(
          gradient: const LinearGradient(
            colors: [_kLeafSofter, Color(0xFFF7FEE7)],
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          ),
          borderRadius: BorderRadius.circular(20),
          border: Border.all(color: Colors.white, width: 1.5),
        ),
        padding: const EdgeInsets.fromLTRB(14, 12, 14, 14),
        child: Stack(
          clipBehavior: Clip.none,
          children: [
            // Garden visual bên phải
            Positioned(
              right: -8,
              top: -4,
              bottom: -8,
              child: _GardenMiniPreview(
                tree: tree,
                pot: pot,
                acc: acc,
                treeEmoji: treeState.emoji,
              ),
            ),
            Padding(
              padding: const EdgeInsets.only(right: 130),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Khu vườn của bạn',
                    style: const TextStyle(
                      fontFamily: 'Outfit',
                      fontSize: 12,
                      color: _kInkSoft,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Row(
                    children: [
                      Container(
                        width: 32,
                        height: 32,
                        decoration: const BoxDecoration(
                          color: _kLeaf,
                          shape: BoxShape.circle,
                        ),
                        child: Center(
                          child: Text(
                            treeState.emoji,
                            style: const TextStyle(fontSize: 16),
                          ),
                        ),
                      ),
                      const SizedBox(width: 8),
                      Text(
                        moodLabel,
                        style: const TextStyle(
                          fontFamily: 'Outfit',
                          fontSize: 22,
                          fontWeight: FontWeight.w800,
                          color: _kInk,
                          height: 1.0,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 14),
                  _StatusRow(
                    icon: Icons.local_fire_department_rounded,
                    iconColor: const Color(0xFFF97316),
                    title: '$streak ngày liên tiếp',
                    sub: streak > 0
                        ? 'Duy trì thói quen tuyệt vời!'
                        : 'Hãy bắt đầu hôm nay!',
                  ),
                  const SizedBox(height: 10),
                  _StatusRow(
                    icon: Icons.bar_chart_rounded,
                    iconColor: _kInkSoft,
                    title: '${svc.entries.length} bài nhật ký',
                    sub: treeState.description,
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

/// Mini garden preview showing equipped items.
class _GardenMiniPreview extends StatelessWidget {
  const _GardenMiniPreview({
    required this.treeEmoji,
    this.tree,
    this.pot,
    this.acc,
  });
  final String treeEmoji;
  final GardenItem? tree;
  final GardenItem? pot;
  final GardenItem? acc;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 140,
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [_kLeafSoft, _kLeafLight.withOpacity(0.45)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: const BorderRadius.only(
          topRight: Radius.circular(18),
          bottomRight: Radius.circular(18),
          topLeft: Radius.circular(60),
          bottomLeft: Radius.circular(60),
        ),
      ),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          if (acc != null)
            Text(acc!.emoji, style: const TextStyle(fontSize: 18)),
          Text(tree?.emoji ?? treeEmoji, style: const TextStyle(fontSize: 48)),
          Text(pot?.emoji ?? '🟤', style: const TextStyle(fontSize: 22)),
        ],
      ),
    );
  }
}

class _StatusRow extends StatelessWidget {
  const _StatusRow({
    required this.icon,
    required this.iconColor,
    required this.title,
    required this.sub,
    this.trailing,
  });

  final IconData icon;
  final Color iconColor;
  final String title;
  final String sub;
  final String? trailing;  @override
  Widget build(BuildContext context) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.only(top: 2),
          child: Icon(icon, size: 14, color: iconColor),
        ),
        const SizedBox(width: 6),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                title,
                style: const TextStyle(
                  fontFamily: 'Outfit',
                  fontSize: 13,
                  fontWeight: FontWeight.w700,
                  color: _kInk,
                  height: 1.2,
                ),
              ),
              const SizedBox(height: 2),
              Text(
                sub,
                style: const TextStyle(
                  fontFamily: 'Outfit',
                  fontSize: 11.5,
                  color: _kInkSoft,
                  height: 1.2,
                ),
              ),
            ],
          ),
        ),
        if (trailing != null)
          Text(
            trailing!,
            style: const TextStyle(
              fontFamily: 'Outfit',
              fontSize: 13,
              fontWeight: FontWeight.w800,
              color: _kInk,
            ),
          ),
      ],
    );
  }
}

class _BonsaiPlaceholder extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    // Kept for backward compatibility but replaced by _GardenMiniPreview in hero.
    return const SizedBox.shrink();
  }
}

// ───────────────────────── MOOD PICKER ─────────────────────────

class _MoodPickerCard extends StatelessWidget {
  const _MoodPickerCard({
    required this.selected,
    required this.onChanged,
    required this.onSave,
    required this.onWriteJournal,
  });

  final _Mood selected;
  final ValueChanged<_Mood> onChanged;
  final VoidCallback onSave;
  final VoidCallback onWriteJournal;

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: _kBorder),
      ),
      padding: const EdgeInsets.fromLTRB(14, 14, 14, 14),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.center,
        children: [
          const Align(
            alignment: Alignment.centerLeft,
            child: Text(
              'Hôm nay bạn cảm thấy thế nào?',
              style: TextStyle(
                fontFamily: 'Outfit',
                fontSize: 14,
                fontWeight: FontWeight.w700,
                color: _kInk,
              ),
            ),
          ),
          const SizedBox(height: 12),
          Row(
            children: [
              _MoodItem(
                mood: _Mood.happy,
                selected: selected,
                onChanged: onChanged,
                label: 'Rất vui',
                icon: Icons.sentiment_very_satisfied_rounded,
                color: _kMoodHappy,
                bg: _kMoodHappyBg,
              ),
              _MoodItem(
                mood: _Mood.calm,
                selected: selected,
                onChanged: onChanged,
                label: 'Bình yên',
                icon: Icons.eco_rounded,
                color: _kMoodCalm,
                bg: _kMoodCalmBg,
              ),
              _MoodItem(
                mood: _Mood.stress,
                selected: selected,
                onChanged: onChanged,
                label: 'Căng thẳng',
                icon: Icons.psychology_rounded,
                color: _kMoodStress,
                bg: _kMoodStressBg,
              ),
              _MoodItem(
                mood: _Mood.sad,
                selected: selected,
                onChanged: onChanged,
                label: 'Buồn',
                icon: Icons.cloud_rounded,
                color: _kMoodSad,
                bg: _kMoodSadBg,
              ),
              _MoodItem(
                mood: _Mood.tired,
                selected: selected,
                onChanged: onChanged,
                label: 'Mệt mỏi',
                icon: Icons.bedtime_rounded,
                color: _kMoodTired,
                bg: _kMoodTiredBg,
              ),
            ],
          ),
          const SizedBox(height: 14),
          Row(
            children: [
              Expanded(
                child: Material(
                  color: _kLeaf,
                  borderRadius: BorderRadius.circular(999),
                  child: InkWell(
                    onTap: onSave,
                    borderRadius: BorderRadius.circular(999),
                    child: const Padding(
                      padding: EdgeInsets.symmetric(vertical: 12),
                      child: Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Icon(Icons.check_rounded, size: 16, color: Colors.white),
                          SizedBox(width: 6),
                          Text(
                            'Lưu cảm xúc',
                            style: TextStyle(
                              fontFamily: 'Outfit',
                              fontSize: 14,
                              fontWeight: FontWeight.w700,
                              color: Colors.white,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                ),
              ),
              const SizedBox(width: 8),
              Material(
                color: _kLeafSofter,
                borderRadius: BorderRadius.circular(999),
                child: InkWell(
                  onTap: onWriteJournal,
                  borderRadius: BorderRadius.circular(999),
                  child: Container(
                    padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
                    decoration: BoxDecoration(
                      border: Border.all(color: _kLeafSoft),
                      borderRadius: BorderRadius.circular(999),
                    ),
                    child: const Row(
                      children: [
                        Icon(Icons.edit_rounded, size: 15, color: _kLeaf),
                        SizedBox(width: 5),
                        Text(
                          'Viết thêm',
                          style: TextStyle(
                            fontFamily: 'Outfit',
                            fontSize: 13,
                            fontWeight: FontWeight.w700,
                            color: _kLeaf,
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: const [
              Icon(Icons.eco_rounded, size: 12, color: _kLeaf),
              SizedBox(width: 4),
              Flexible(
                child: Text(
                  'Ghi lại cảm xúc mỗi ngày để hiểu bản thân hơn',
                  style: TextStyle(
                    fontFamily: 'Outfit',
                    fontSize: 11,
                    color: _kInkSoft,
                  ),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}

class _MoodItem extends StatelessWidget {
  const _MoodItem({
    required this.mood,
    required this.selected,
    required this.onChanged,
    required this.label,
    required this.icon,
    required this.color,
    required this.bg,
  });

  final _Mood mood;
  final _Mood selected;
  final ValueChanged<_Mood> onChanged;
  final String label;
  final IconData icon;
  final Color color;
  final Color bg;

  @override
  Widget build(BuildContext context) {
    final active = mood == selected;
    return Expanded(
      child: InkResponse(
        onTap: () {
          HapticFeedback.selectionClick();
          onChanged(mood);
        },
        radius: 36,
        child: Column(
          children: [
            Container(
              width: 48,
              height: 48,
              decoration: BoxDecoration(
                color: bg,
                shape: BoxShape.circle,
                border: Border.all(
                  color: active ? color : Colors.transparent,
                  width: 2,
                ),
                boxShadow: active
                    ? [
                        BoxShadow(
                          color: color.withOpacity(0.25),
                          blurRadius: 8,
                          offset: const Offset(0, 3),
                        ),
                      ]
                    : null,
              ),
              child: Icon(icon, size: 22, color: color),
            ),
            const SizedBox(height: 6),
            Text(
              label,
              style: TextStyle(
                fontFamily: 'Outfit',
                fontSize: 10.5,
                fontWeight: active ? FontWeight.w700 : FontWeight.w600,
                color: active ? _kInk : _kInkSoft,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

// ───────────────────────── SECTION HEADER ─────────────────────────

class _SectionHeader extends StatelessWidget {
  const _SectionHeader({
    required this.title,
    this.actionLabel,
    this.onActionTap,
  });
  final String title;
  final String? actionLabel;
  final VoidCallback? onActionTap;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 4),
      child: Row(
        children: [
          Expanded(
            child: Text(
              title,
              style: const TextStyle(
                fontFamily: 'Outfit',
                fontSize: 14.5,
                fontWeight: FontWeight.w700,
                color: _kInk,
              ),
            ),
          ),
          if (actionLabel != null)
            InkWell(
              onTap: () {
                HapticFeedback.selectionClick();
                onActionTap?.call();
              },
              borderRadius: BorderRadius.circular(8),
              child: Padding(
                padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 4),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Text(
                      actionLabel!,
                      style: const TextStyle(
                        fontFamily: 'Outfit',
                        fontSize: 12,
                        fontWeight: FontWeight.w600,
                        color: _kLeaf,
                      ),
                    ),
                    const Icon(Icons.chevron_right_rounded,
                        size: 16, color: _kLeaf),
                  ],
                ),
              ),
            ),
        ],
      ),
    );
  }
}

// ───────────────────────── EMPTY JOURNAL BANNER ─────────────────────────

class _EmptyJournalBanner extends StatelessWidget {
  const _EmptyJournalBanner({required this.onTap});
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.all(20),
        decoration: BoxDecoration(
          color: _kLeafSofter,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: _kLeafSoft, style: BorderStyle.solid),
        ),
        child: Row(
          children: [
            Container(
              width: 48,
              height: 48,
              decoration: BoxDecoration(
                color: _kLeafSoft,
                borderRadius: BorderRadius.circular(14),
              ),
              child: const Icon(Icons.auto_stories_rounded, color: _kLeaf, size: 26),
            ),
            const SizedBox(width: 14),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: const [
                  Text(
                    'Bắt đầu viết nhật ký đầu tiên',
                    style: TextStyle(
                      fontFamily: 'Outfit',
                      fontSize: 14,
                      fontWeight: FontWeight.w700,
                      color: _kInk,
                    ),
                  ),
                  SizedBox(height: 3),
                  Text(
                    'Ghi lại cảm xúc hôm nay để khu vườn phát triển',
                    style: TextStyle(
                      fontFamily: 'Outfit',
                      fontSize: 11.5,
                      color: _kInkSoft,
                    ),
                  ),
                ],
              ),
            ),
            const Icon(Icons.arrow_forward_ios_rounded, size: 14, color: _kLeaf),
          ],
        ),
      ),
    );
  }
}

// ───────────────────────── JOURNAL GRID (real data) ─────────────────────────

class _JournalGrid extends StatelessWidget {
  const _JournalGrid({
    required this.entries,
    required this.onTap,
    required this.onWriteNew,
  });
  final List<JournalEntry> entries;
  final ValueChanged<JournalEntry> onTap;
  final VoidCallback onWriteNew;

  @override
  Widget build(BuildContext context) {
    final visible = entries.take(2).toList();
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        for (int i = 0; i < visible.length; i++) ...[
          if (i > 0) const SizedBox(width: 10),
          Expanded(
            child: _JournalCard(
              entry: visible[i],
              tone: i.isEven ? _JournalTone.lavender : _JournalTone.green,
              onTap: () => onTap(visible[i]),
            ),
          ),
        ],
        if (visible.length < 2) ...[
          const SizedBox(width: 10),
          Expanded(
            child: _WriteNewCard(onTap: onWriteNew),
          ),
        ],
      ],
    );
  }
}

class _WriteNewCard extends StatelessWidget {
  const _WriteNewCard({required this.onTap});
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.all(10),
        decoration: BoxDecoration(
          border: Border.all(color: _kBorder, style: BorderStyle.solid),
          borderRadius: BorderRadius.circular(16),
          color: _kLeafSofter,
        ),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: const [
            SizedBox(height: 14),
            Icon(Icons.add_circle_outline_rounded, size: 28, color: _kLeaf),
            SizedBox(height: 8),
            Text(
              'Viết bài mới',
              style: TextStyle(
                fontFamily: 'Outfit',
                fontSize: 12,
                fontWeight: FontWeight.w700,
                color: _kLeaf,
              ),
            ),
            SizedBox(height: 14),
          ],
        ),
      ),
    );
  }
}

// ───────────────────────── JOURNAL CARD ─────────────────────────

enum _JournalTone { lavender, green }

class _JournalCard extends StatelessWidget {
  const _JournalCard({
    required this.entry,
    required this.tone,
    required this.onTap,
  });

  final JournalEntry entry;
  final _JournalTone tone;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final accent = tone == _JournalTone.lavender
        ? const Color(0xFF8B5CF6)
        : _kLeaf;
    final accentBg = tone == _JournalTone.lavender
        ? const Color(0xFFEDE9FE)
        : _kLeafSoft;
    final icon = tone == _JournalTone.lavender
        ? Icons.local_florist_rounded
        : Icons.eco_rounded;

    final dateStr =
        '${entry.date.day.toString().padLeft(2, '0')}/${entry.date.month.toString().padLeft(2, '0')}/${entry.date.year}';
    final excerpt = entry.content.isEmpty ? 'Cảm xúc: ${entry.mood.label}' : entry.content;

    return Material(
      color: Colors.white,
      borderRadius: BorderRadius.circular(16),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(16),
        child: Container(
          padding: const EdgeInsets.all(10),
          decoration: BoxDecoration(
            border: Border.all(color: _kBorder),
            borderRadius: BorderRadius.circular(16),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: [
              Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Container(
                    width: 38,
                    height: 38,
                    decoration: BoxDecoration(
                      color: accentBg,
                      borderRadius: BorderRadius.circular(10),
                    ),
                    child: Center(
                      child: Text(entry.mood.emoji,
                          style: const TextStyle(fontSize: 20)),
                    ),
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Text(
                          entry.mood.label,
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                          style: const TextStyle(
                            fontFamily: 'Outfit',
                            fontSize: 12.5,
                            fontWeight: FontWeight.w800,
                            color: _kInk,
                            height: 1.2,
                          ),
                        ),
                        const SizedBox(height: 2),
                        Text(
                          excerpt,
                          maxLines: 2,
                          overflow: TextOverflow.ellipsis,
                          style: const TextStyle(
                            fontFamily: 'Outfit',
                            fontSize: 10.5,
                            color: _kInkSoft,
                            height: 1.3,
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 8),
              Row(
                children: [
                  Text(
                    dateStr,
                    style: const TextStyle(
                      fontFamily: 'Outfit',
                      fontSize: 10,
                      color: _kInkMuted,
                    ),
                  ),
                  const SizedBox(width: 6),
                  const Text('·',
                      style: TextStyle(
                          fontFamily: 'Outfit', fontSize: 10, color: _kInkMuted)),
                  const SizedBox(width: 6),
                  Icon(icon, size: 11, color: accent),
                  const SizedBox(width: 3),
                  Flexible(
                    child: Text(
                      entry.tags.take(2).map((t) => t.emoji).join(' '),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      style: TextStyle(
                        fontFamily: 'Outfit',
                        fontSize: 10,
                        fontWeight: FontWeight.w600,
                        color: accent,
                      ),
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}

// ───────────────────────── EXERCISE CARD ─────────────────────────

enum _ExerciseTone { cloud, leaf, peach }

class _ExerciseCard extends StatelessWidget {
  const _ExerciseCard({
    required this.duration,
    required this.title,
    required this.desc,
    required this.tone,
    required this.onTap,
  });

  final String duration;
  final String title;
  final String desc;
  final _ExerciseTone tone;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    Color bg;
    Color accent;
    IconData badgeIcon;
    switch (tone) {
      case _ExerciseTone.cloud:
        bg = const Color(0xFFF1F5F9);
        accent = const Color(0xFF64748B);
        badgeIcon = Icons.air_rounded;
        break;
      case _ExerciseTone.leaf:
        bg = _kLeafSofter;
        accent = _kLeaf;
        badgeIcon = Icons.eco_rounded;
        break;
      case _ExerciseTone.peach:
        bg = const Color(0xFFFFEDD5);
        accent = const Color(0xFFF97316);
        badgeIcon = Icons.music_note_rounded;
        break;
    }

    return Material(
      color: Colors.white,
      borderRadius: BorderRadius.circular(16),
      child: InkWell(
        onTap: () {
          HapticFeedback.selectionClick();
          onTap();
        },
        borderRadius: BorderRadius.circular(16),
        child: Container(
          padding: const EdgeInsets.all(10),
          decoration: BoxDecoration(
            border: Border.all(color: _kBorder),
            borderRadius: BorderRadius.circular(16),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: [
              Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Container(
                    width: 38,
                    height: 38,
                    decoration: BoxDecoration(
                      color: bg,
                      borderRadius: BorderRadius.circular(10),
                    ),
                    child: Icon(badgeIcon, size: 18, color: accent),
                  ),
                  const SizedBox(width: 6),
                  Expanded(
                    child: Container(
                      padding: const EdgeInsets.symmetric(
                          horizontal: 8, vertical: 4),
                      decoration: BoxDecoration(
                        color: bg,
                        borderRadius: BorderRadius.circular(999),
                      ),
                      child: Text(
                        duration,
                        textAlign: TextAlign.center,
                        style: TextStyle(
                          fontFamily: 'Outfit',
                          fontSize: 10.5,
                          fontWeight: FontWeight.w700,
                          color: accent,
                        ),
                      ),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 8),
              Text(
                title,
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
                style: const TextStyle(
                  fontFamily: 'Outfit',
                  fontSize: 12.5,
                  fontWeight: FontWeight.w800,
                  color: _kInk,
                  height: 1.2,
                ),
              ),
              const SizedBox(height: 2),
              Row(
                children: [
                  Expanded(
                    child: Text(
                      desc,
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                      style: const TextStyle(
                        fontFamily: 'Outfit',
                        fontSize: 10.5,
                        color: _kInkSoft,
                        height: 1.25,
                      ),
                    ),
                  ),
                  const SizedBox(width: 4),
                  Container(
                    width: 22,
                    height: 22,
                    decoration: BoxDecoration(
                      color: accent,
                      shape: BoxShape.circle,
                    ),
                    child: const Icon(Icons.play_arrow_rounded,
                        size: 14, color: Colors.white),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}

// ───────────────────────── GROWTH TIMELINE ─────────────────────────

class _GrowthTimeline extends StatelessWidget {
  const _GrowthTimeline({required this.svc});
  final SoulGardenService svc;

  static const _stageData = [
    (label: 'Hạt mầm', sub: 'Lv. 0', icon: Icons.grass_rounded, threshold: 0),
    (label: 'Mầm non', sub: 'Lv. 1', icon: Icons.spa_rounded, threshold: 1),
    (label: 'Cây nhỏ', sub: 'Lv. 2', icon: Icons.park_rounded, threshold: 3),
    (label: 'Cây trưởng thành', sub: 'Lv. 3', icon: Icons.forest_rounded, threshold: 6),
    (label: 'Khu vườn an yên', sub: 'Lv. 4', icon: Icons.holiday_village_rounded, threshold: 10),
  ];

  @override
  Widget build(BuildContext context) {
    final currentLevel = svc.treeState.level;
    final stages = _stageData.map((d) {
      final _StageState state;
      if (currentLevel > _stageData.indexOf(d)) {
        state = _StageState.done;
      } else if (currentLevel == _stageData.indexOf(d)) {
        state = _StageState.current;
      } else {
        state = _StageState.locked;
      }
      return _Stage(
        label: d.label,
        sub: d.sub,
        icon: d.icon,
        state: state,
      );
    }).toList();

    return SizedBox(
      height: 120,
      child: ListView.builder(
        scrollDirection: Axis.horizontal,
        padding: const EdgeInsets.symmetric(horizontal: 4),
        itemCount: stages.length,
        itemBuilder: (_, i) {
          final s = stages[i];
          final isLast = i == stages.length - 1;
          return SizedBox(
            width: 102,
            child: Column(
              children: [
                Stack(
                  alignment: Alignment.center,
                  children: [
                    if (!isLast)
                      Positioned(
                        right: -12,
                        top: 30,
                        child: Container(
                          width: 24,
                          height: 1,
                          decoration: const BoxDecoration(
                            border: Border(
                              top: BorderSide(
                                color: _kBorder,
                                style: BorderStyle.solid,
                                width: 1,
                              ),
                            ),
                          ),
                          child: CustomPaint(
                            painter: _DashedLinePainter(),
                          ),
                        ),
                      ),
                    _StageIcon(stage: s),
                  ],
                ),
                const SizedBox(height: 6),
                Text(
                  s.label,
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                  style: TextStyle(
                    fontFamily: 'Outfit',
                    fontSize: 11,
                    fontWeight: s.state == _StageState.current
                        ? FontWeight.w800
                        : FontWeight.w600,
                    color: s.state == _StageState.locked
                        ? _kInkMuted
                        : _kInk,
                  ),
                ),
                if (s.sub.isNotEmpty) ...[
                  const SizedBox(height: 2),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Text(
                        s.sub,
                        style: const TextStyle(
                          fontFamily: 'Outfit',
                          fontSize: 10,
                          color: _kInkMuted,
                        ),
                      ),
                      if (s.state == _StageState.locked) ...[
                        const SizedBox(width: 3),
                        const Icon(Icons.lock_rounded,
                            size: 10, color: _kInkMuted),
                      ],
                    ],
                  ),
                ] else
                  const SizedBox(height: 2),
              ],
            ),
          );
        },
      ),
    );
  }
}

enum _StageState { done, current, locked }

class _Stage {
  final String label;
  final String sub;
  final IconData icon;
  final _StageState state;
  const _Stage({
    required this.label,
    required this.sub,
    required this.icon,
    required this.state,
  });
}

class _StageIcon extends StatelessWidget {
  const _StageIcon({required this.stage});
  final _Stage stage;

  @override
  Widget build(BuildContext context) {
    Color bg;
    Color iconColor;
    Border? border;

    switch (stage.state) {
      case _StageState.done:
        bg = _kLeafSofter;
        iconColor = _kLeaf;
        border = null;
        break;
      case _StageState.current:
        bg = _kLeafSoft;
        iconColor = _kLeaf;
        border = Border.all(color: _kLeaf, width: 2);
        break;
      case _StageState.locked:
        bg = const Color(0xFFF1F5F9);
        iconColor = _kInkMuted;
        border = null;
        break;
    }

    return Container(
      width: 60,
      height: 60,
      decoration: BoxDecoration(
        color: bg,
        borderRadius: BorderRadius.circular(14),
        border: border,
      ),
      child: Stack(
        clipBehavior: Clip.none,
        alignment: Alignment.center,
        children: [
          Icon(stage.icon, size: 30, color: iconColor),
          if (stage.state == _StageState.done)
            Positioned(
              right: -4,
              bottom: -4,
              child: Container(
                width: 18,
                height: 18,
                decoration: BoxDecoration(
                  color: _kLeaf,
                  shape: BoxShape.circle,
                  border: Border.all(color: Colors.white, width: 2),
                ),
                child: const Icon(Icons.check_rounded,
                    size: 11, color: Colors.white),
              ),
            ),
        ],
      ),
    );
  }
}

class _DashedLinePainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = _kInkMuted
      ..strokeWidth = 1;
    const dashWidth = 3.0;
    const dashSpace = 3.0;
    double startX = 0;
    while (startX < size.width) {
      canvas.drawLine(
        Offset(startX, size.height / 2),
        Offset(startX + dashWidth, size.height / 2),
        paint,
      );
      startX += dashWidth + dashSpace;
    }
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}
