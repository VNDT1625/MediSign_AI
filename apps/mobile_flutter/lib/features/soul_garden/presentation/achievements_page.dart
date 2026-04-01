import 'package:flutter/material.dart';

import '../../../core/services/soul_garden_service.dart';

/// Achievements & Tree Collection page.
class AchievementsPage extends StatelessWidget {
  const AchievementsPage({super.key});

  @override
  Widget build(BuildContext context) {
    final svc = SoulGardenService.instance;
    final unlocked = svc.unlockedAchievements;
    final locked = svc.lockedAchievements;

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
                padding: const EdgeInsets.fromLTRB(8, 8, 16, 0),
                child: Row(
                  children: [
                    IconButton(
                      icon: const Icon(Icons.arrow_back_ios,
                          color: Colors.white70),
                      onPressed: () => Navigator.pop(context),
                    ),
                    const Text('Thành tựu & Bộ sưu tập',
                        style: TextStyle(
                            color: Colors.white,
                            fontSize: 18,
                            fontWeight: FontWeight.w600)),
                  ],
                ),
              ),
              Expanded(
                child: SingleChildScrollView(
                  padding: const EdgeInsets.fromLTRB(20, 20, 20, 32),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      // ─── Progress overview ──────
                      _buildProgressCard(svc, unlocked),
                      const SizedBox(height: 24),

                      // ─── Tree Collection ────────
                      const Text('🌳 Bộ sưu tập cây',
                          style: TextStyle(
                              color: Colors.white,
                              fontSize: 16,
                              fontWeight: FontWeight.w600)),
                      const SizedBox(height: 12),
                      _buildTreeCollection(svc),
                      const SizedBox(height: 24),

                      // ─── Unlocked Achievements ──
                      if (unlocked.isNotEmpty) ...[
                        Text(
                            '✅ Đã mở khóa (${unlocked.length}/${svc.allAchievements.length})',
                            style: const TextStyle(
                                color: Colors.white,
                                fontSize: 16,
                                fontWeight: FontWeight.w600)),
                        const SizedBox(height: 12),
                        ...unlocked.map((a) => _achievementTile(a, true)),
                        const SizedBox(height: 20),
                      ],

                      // ─── Locked Achievements ────
                      if (locked.isNotEmpty) ...[
                        Text('🔒 Chưa mở khóa (${locked.length})',
                            style: TextStyle(
                                color: Colors.white.withOpacity(0.7),
                                fontSize: 16,
                                fontWeight: FontWeight.w600)),
                        const SizedBox(height: 12),
                        ...locked.map((a) => _achievementTile(a, false)),
                      ],
                    ],
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildProgressCard(SoulGardenService svc, List<Achievement> unlocked) {
    final total = svc.allAchievements.length;
    final progress = total > 0 ? unlocked.length / total : 0.0;

    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.1),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: Colors.white.withOpacity(0.15)),
      ),
      child: Column(
        children: [
          Row(
            children: [
              Text(svc.treeState.emoji, style: const TextStyle(fontSize: 48)),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(svc.treeState.name,
                        style: const TextStyle(
                            color: Colors.white,
                            fontSize: 20,
                            fontWeight: FontWeight.w700)),
                    const SizedBox(height: 4),
                    Text(svc.treeState.description,
                        style: TextStyle(
                            color: Colors.white.withOpacity(0.6),
                            fontSize: 13)),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 20),
          // Progress bar
          Column(
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text('Tiến độ thành tựu',
                      style: TextStyle(
                          color: Colors.white.withOpacity(0.7), fontSize: 13)),
                  Text('${unlocked.length}/$total',
                      style: const TextStyle(
                          color: Colors.white,
                          fontWeight: FontWeight.w600,
                          fontSize: 13)),
                ],
              ),
              const SizedBox(height: 8),
              ClipRRect(
                borderRadius: BorderRadius.circular(6),
                child: LinearProgressIndicator(
                  value: progress,
                  minHeight: 10,
                  backgroundColor: Colors.white.withOpacity(0.1),
                  valueColor: const AlwaysStoppedAnimation(Color(0xFF52B788)),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildTreeCollection(SoulGardenService svc) {
    final unlockedCount = svc.unlockedTreeCount;
    const trees = SoulGardenService.allTrees;

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.08),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Wrap(
        spacing: 12,
        runSpacing: 12,
        children: List.generate(trees.length, (i) {
          final tree = trees[i];
          final unlocked = i < unlockedCount;
          return Container(
            width: 90,
            padding: const EdgeInsets.all(10),
            decoration: BoxDecoration(
              color: unlocked
                  ? const Color(0xFF52B788).withOpacity(0.15)
                  : Colors.white.withOpacity(0.04),
              borderRadius: BorderRadius.circular(14),
              border: Border.all(
                color: unlocked
                    ? const Color(0xFF52B788).withOpacity(0.3)
                    : Colors.white.withOpacity(0.06),
              ),
            ),
            child: Column(
              children: [
                Text(
                  unlocked ? tree['emoji']! : '🔒',
                  style: TextStyle(
                      fontSize: unlocked ? 32 : 24,
                      color: unlocked ? null : Colors.white38),
                ),
                const SizedBox(height: 6),
                Text(tree['name']!,
                    textAlign: TextAlign.center,
                    style: TextStyle(
                        color: unlocked
                            ? Colors.white
                            : Colors.white.withOpacity(0.3),
                        fontSize: 11,
                        fontWeight: FontWeight.w500)),
                const SizedBox(height: 2),
                Text(tree['requirement']!,
                    textAlign: TextAlign.center,
                    style: TextStyle(
                        color: Colors.white.withOpacity(0.3), fontSize: 9)),
              ],
            ),
          );
        }),
      ),
    );
  }

  Widget _achievementTile(Achievement a, bool unlocked) {
    return Container(
      margin: const EdgeInsets.only(bottom: 10),
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: unlocked
            ? const Color(0xFF52B788).withOpacity(0.12)
            : Colors.white.withOpacity(0.05),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: unlocked
              ? const Color(0xFF52B788).withOpacity(0.3)
              : Colors.white.withOpacity(0.06),
        ),
      ),
      child: Row(
        children: [
          Text(unlocked ? a.emoji : '🔒', style: const TextStyle(fontSize: 28)),
          const SizedBox(width: 14),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(a.title,
                    style: TextStyle(
                        color: unlocked
                            ? Colors.white
                            : Colors.white.withOpacity(0.4),
                        fontSize: 14,
                        fontWeight: FontWeight.w600)),
                const SizedBox(height: 2),
                Text(a.description,
                    style: TextStyle(
                        color: Colors.white.withOpacity(unlocked ? 0.6 : 0.3),
                        fontSize: 12)),
              ],
            ),
          ),
          if (unlocked)
            const Icon(Icons.check_circle, color: Color(0xFF52B788), size: 22),
        ],
      ),
    );
  }
}
