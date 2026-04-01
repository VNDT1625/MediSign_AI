import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import '../../../core/models/achievement_model.dart';
import '../../../core/services/achievement_service.dart';
import '../../../core/theme/glass_theme.dart';

/// Trang hiển thị thành tựu và chuỗi hoạt động
class AchievementsPage extends StatefulWidget {
  const AchievementsPage({super.key, this.onBack});

  final VoidCallback? onBack;

  @override
  State<AchievementsPage> createState() => _AchievementsPageState();
}

class _AchievementsPageState extends State<AchievementsPage> {
  final AchievementService _service = AchievementService();
  UserAchievementSummary? _summary;
  List<AchievementProgress> _progress = [];
  AchievementCategory _selectedCategory = AchievementCategory.general;
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    final summary = await _service.getSummary();
    final progress = await _service.getAllProgress();
    if (mounted) {
      setState(() {
        _summary = summary;
        _progress = progress;
        _loading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return GlassTheme.scaffoldBackground(
      child: SafeArea(
        child: _loading
            ? GlassTheme.loadingIndicator(message: 'Đang tải thành tựu...')
            : CustomScrollView(
                slivers: [
                  SliverToBoxAdapter(child: _buildAppBar()),
                  SliverToBoxAdapter(child: _buildSummaryCard()),
                  SliverToBoxAdapter(child: _buildStreaksSection()),
                  SliverToBoxAdapter(child: _buildCategoryFilter()),
                  SliverToBoxAdapter(child: _buildAchievementsList()),
                  const SliverToBoxAdapter(child: SizedBox(height: 24)),
                ],
              ),
      ),
    );
  }

  Widget _buildAppBar() {
    return Padding(
      padding: const EdgeInsets.fromLTRB(8, 8, 8, 0),
      child: Row(
        children: [
          if (widget.onBack != null)
            GlassTheme.glassIconButton(
              icon: Icons.arrow_back_ios_new_rounded,
              onPressed: () {
                HapticFeedback.lightImpact();
                widget.onBack!();
              },
              size: 44,
            )
          else
            const SizedBox(width: 44),
          const Expanded(
            child: Text('Thành tựu',
                textAlign: TextAlign.center, style: GlassTheme.h3),
          ),
          const SizedBox(width: 44),
        ],
      ),
    );
  }

  Widget _buildSummaryCard() {
    final s = _summary;
    if (s == null) return const SizedBox.shrink();

    return Padding(
      padding: const EdgeInsets.fromLTRB(20, 20, 20, 0),
      child: GlassTheme.glassCard(
        padding: const EdgeInsets.all(20),
        child: Column(
          children: [
            Row(
              children: [
                // Level badge
                Container(
                  width: 64,
                  height: 64,
                  decoration: BoxDecoration(
                    gradient: const LinearGradient(
                      colors: [Color(0xFFF59E0B), Color(0xFFF97316)],
                    ),
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: Center(
                    child: Text(
                      'Lv${s.level}',
                      style: const TextStyle(
                        fontFamily: 'Outfit',
                        fontSize: 20,
                        fontWeight: FontWeight.w800,
                        color: Colors.white,
                      ),
                    ),
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        '${s.totalXp} XP',
                        style: GlassTheme.h2.copyWith(fontSize: 24),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        '${s.unlockedCount}/${s.totalCount} thành tựu đã mở',
                        style: GlassTheme.body,
                      ),
                    ],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            // XP progress bar
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text('Level ${s.level}', style: GlassTheme.caption),
                    Text('Level ${s.level + 1}', style: GlassTheme.caption),
                  ],
                ),
                const SizedBox(height: 6),
                GlassTheme.progressBar(value: s.progressToNextLevel),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStreaksSection() {
    final s = _summary;
    if (s == null || s.streaks.isEmpty) return const SizedBox.shrink();

    final activeStreaks =
        s.streaks.where((st) => st.currentStreak > 0).toList();

    return Padding(
      padding: const EdgeInsets.fromLTRB(20, 20, 20, 0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text('🔥 Chuỗi hoạt động', style: GlassTheme.h3),
          const SizedBox(height: 12),
          if (activeStreaks.isEmpty)
            GlassTheme.glassCard(
              padding: const EdgeInsets.all(16),
              child: const Row(
                children: [
                  Text('💤', style: TextStyle(fontSize: 28)),
                  SizedBox(width: 12),
                  Expanded(
                    child: Text(
                      'Chưa có chuỗi nào. Hãy bắt đầu hoạt động hàng ngày!',
                      style: GlassTheme.body,
                    ),
                  ),
                ],
              ),
            )
          else
            Row(
              children: activeStreaks.map((streak) {
                return Expanded(
                  child: Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 4),
                    child: _streakCard(streak),
                  ),
                );
              }).toList(),
            ),
        ],
      ),
    );
  }

  Widget _streakCard(ActivityStreak streak) {
    return GlassTheme.glassCard(
      padding: const EdgeInsets.all(14),
      child: Column(
        children: [
          Text(streak.category.emoji, style: const TextStyle(fontSize: 28)),
          const SizedBox(height: 8),
          Text(
            '${streak.currentStreak}',
            style: const TextStyle(
              fontFamily: 'Outfit',
              fontSize: 28,
              fontWeight: FontWeight.w800,
              color: Color(0xFFF59E0B),
            ),
          ),
          const Text('ngày', style: GlassTheme.caption),
          const SizedBox(height: 4),
          Text(
            streak.category.label,
            style: GlassTheme.label.copyWith(fontSize: 11),
            textAlign: TextAlign.center,
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
          ),
          if (streak.isActiveToday)
            Padding(
              padding: const EdgeInsets.only(top: 6),
              child: GlassTheme.badge(
                text: '✓ Hôm nay',
                backgroundColor: GlassTheme.primaryGreen.withOpacity(0.2),
                textColor: GlassTheme.primaryGreenLight,
              ),
            ),
        ],
      ),
    );
  }

  Widget _buildCategoryFilter() {
    final categories = [
      AchievementCategory.general,
      AchievementCategory.fitness,
      AchievementCategory.health,
      AchievementCategory.consult,
      AchievementCategory.soulGarden,
      AchievementCategory.medicine,
    ];

    return Padding(
      padding: const EdgeInsets.fromLTRB(20, 20, 20, 0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text('🏅 Danh sách thành tựu', style: GlassTheme.h3),
          const SizedBox(height: 12),
          SizedBox(
            height: 40,
            child: ListView.separated(
              scrollDirection: Axis.horizontal,
              itemCount: categories.length,
              separatorBuilder: (_, __) => const SizedBox(width: 8),
              itemBuilder: (context, index) {
                final cat = categories[index];
                final isSelected = _selectedCategory == cat;
                return GestureDetector(
                  onTap: () {
                    HapticFeedback.selectionClick();
                    setState(() => _selectedCategory = cat);
                  },
                  child: AnimatedContainer(
                    duration: const Duration(milliseconds: 200),
                    padding:
                        const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
                    decoration: BoxDecoration(
                      color: isSelected
                          ? GlassTheme.primaryGreen.withOpacity(0.2)
                          : GlassTheme.glassFill,
                      borderRadius: BorderRadius.circular(20),
                      border: Border.all(
                        color: isSelected
                            ? GlassTheme.primaryGreen.withOpacity(0.5)
                            : GlassTheme.glassBorder,
                      ),
                    ),
                    child: Text(
                      cat == AchievementCategory.general
                          ? 'Tất cả'
                          : '${cat.emoji} ${cat.label}',
                      style: TextStyle(
                        fontFamily: 'Outfit',
                        fontSize: 13,
                        fontWeight:
                            isSelected ? FontWeight.w600 : FontWeight.w400,
                        color: isSelected
                            ? GlassTheme.primaryGreenLight
                            : GlassTheme.textSecondary,
                      ),
                    ),
                  ),
                );
              },
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildAchievementsList() {
    final filtered = _selectedCategory == AchievementCategory.general
        ? AchievementDatabase.all
        : AchievementDatabase.byCategory(_selectedCategory);

    return Padding(
      padding: const EdgeInsets.fromLTRB(20, 16, 20, 0),
      child: Column(
        children: filtered.map((def) {
          final prog = _progress.firstWhere(
            (p) => p.definitionId == def.id,
            orElse: () => AchievementProgress(
              definitionId: def.id,
              currentCount: 0,
              isUnlocked: false,
            ),
          );
          return _achievementTile(def, prog);
        }).toList(),
      ),
    );
  }

  Widget _achievementTile(AchievementDefinition def, AchievementProgress prog) {
    final percent = prog.progressPercent(def.targetCount);

    return GlassTheme.glassCard(
      padding: const EdgeInsets.all(16),
      margin: const EdgeInsets.only(bottom: 10),
      isActive: prog.isUnlocked,
      activeColor: const Color(0xFFF59E0B),
      child: Row(
        children: [
          // Emoji + tier
          Container(
            width: 52,
            height: 52,
            decoration: BoxDecoration(
              color: prog.isUnlocked
                  ? const Color(0xFFF59E0B).withOpacity(0.15)
                  : GlassTheme.glassFill,
              borderRadius: BorderRadius.circular(16),
            ),
            child: Center(
              child: Text(
                def.emoji,
                style: TextStyle(
                  fontSize: 26,
                  color: prog.isUnlocked ? null : Colors.white38,
                ),
              ),
            ),
          ),
          const SizedBox(width: 14),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Flexible(
                      child: Text(
                        def.title,
                        style: TextStyle(
                          fontFamily: 'Outfit',
                          fontSize: 15,
                          fontWeight: FontWeight.w700,
                          color:
                              prog.isUnlocked ? Colors.white : Colors.white60,
                        ),
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
                    const SizedBox(width: 6),
                    Text(def.tier.emoji, style: const TextStyle(fontSize: 14)),
                  ],
                ),
                const SizedBox(height: 2),
                Text(
                  def.description,
                  style: GlassTheme.caption.copyWith(fontSize: 12),
                ),
                const SizedBox(height: 8),
                Row(
                  children: [
                    Expanded(
                      child: GlassTheme.progressBar(
                        value: percent,
                        progressColor:
                            prog.isUnlocked ? const Color(0xFFF59E0B) : null,
                      ),
                    ),
                    const SizedBox(width: 10),
                    Text(
                      '${prog.currentCount}/${def.targetCount}',
                      style: GlassTheme.caption.copyWith(fontSize: 11),
                    ),
                  ],
                ),
              ],
            ),
          ),
          if (prog.isUnlocked)
            const Padding(
              padding: EdgeInsets.only(left: 8),
              child: Text('✅', style: TextStyle(fontSize: 20)),
            ),
        ],
      ),
    );
  }
}
