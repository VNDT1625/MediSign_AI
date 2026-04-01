import 'package:flutter/material.dart';

import '../../../core/models/journal_entry.dart';
import '../../../core/services/soul_garden_service.dart';

/// Mood Analytics — charts, trends, tag cloud, AI insights.
class MoodAnalyticsPage extends StatefulWidget {
  const MoodAnalyticsPage({super.key});

  @override
  State<MoodAnalyticsPage> createState() => _MoodAnalyticsPageState();
}

class _MoodAnalyticsPageState extends State<MoodAnalyticsPage> {
  int _rangeDays = 7;
  final _svc = SoulGardenService.instance;

  static const _ranges = [
    (days: 7, label: '7 ngày'),
    (days: 30, label: '30 ngày'),
    (days: 90, label: '3 tháng'),
  ];

  @override
  Widget build(BuildContext context) {
    final stats = _svc.statsForDays(_rangeDays);
    final insights = _svc.getInsights(_rangeDays);

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
              // App bar
              Padding(
                padding: const EdgeInsets.fromLTRB(8, 8, 16, 0),
                child: Row(
                  children: [
                    IconButton(
                      icon: const Icon(Icons.arrow_back_ios,
                          color: Colors.white70),
                      onPressed: () => Navigator.pop(context),
                    ),
                    const Text('Phân tích tâm trạng',
                        style: TextStyle(
                            color: Colors.white,
                            fontSize: 18,
                            fontWeight: FontWeight.w600)),
                  ],
                ),
              ),
              // Range selector
              Padding(
                padding: const EdgeInsets.fromLTRB(20, 16, 20, 8),
                child: Row(
                  children: _ranges.map((r) {
                    final selected = _rangeDays == r.days;
                    return Expanded(
                      child: GestureDetector(
                        onTap: () => setState(() => _rangeDays = r.days),
                        child: Container(
                          margin: const EdgeInsets.symmetric(horizontal: 4),
                          padding: const EdgeInsets.symmetric(vertical: 10),
                          decoration: BoxDecoration(
                            color: selected
                                ? const Color(0xFF52B788)
                                : Colors.white.withOpacity(0.08),
                            borderRadius: BorderRadius.circular(12),
                          ),
                          child: Text(r.label,
                              textAlign: TextAlign.center,
                              style: TextStyle(
                                  color: Colors.white,
                                  fontWeight: selected
                                      ? FontWeight.w700
                                      : FontWeight.w400,
                                  fontSize: 14)),
                        ),
                      ),
                    );
                  }).toList(),
                ),
              ),
              Expanded(
                child: SingleChildScrollView(
                  padding: const EdgeInsets.fromLTRB(20, 8, 20, 32),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      // ─── Summary cards ─────────
                      _buildSummaryRow(stats),
                      const SizedBox(height: 20),

                      // ─── Mood Distribution ─────
                      _sectionTitle('Phân bố tâm trạng'),
                      const SizedBox(height: 12),
                      _buildDistributionChart(stats),
                      const SizedBox(height: 24),

                      // ─── Tag Cloud ─────────────
                      if (stats.tagFrequency.isNotEmpty) ...[
                        _sectionTitle('Cảm xúc thường gặp'),
                        const SizedBox(height: 12),
                        _buildTagCloud(stats),
                        const SizedBox(height: 24),
                      ],

                      // ─── AI Insights ───────────
                      if (insights.isNotEmpty) ...[
                        _sectionTitle('Nhận xét từ AI'),
                        const SizedBox(height: 12),
                        _buildInsights(insights),
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

  Widget _sectionTitle(String text) {
    return Text(text,
        style: const TextStyle(
            color: Colors.white,
            fontSize: 16,
            fontWeight: FontWeight.w600));
  }

  Widget _buildSummaryRow(MoodStats stats) {
    final trend = stats.trendPercent;
    return Row(
      children: [
        _summaryCard(
          emoji: '📝',
          value: '${stats.totalEntries}',
          label: 'Bài viết',
        ),
        const SizedBox(width: 10),
        _summaryCard(
          emoji: '⭐',
          value: stats.averageScore.toStringAsFixed(1),
          label: 'Điểm TB',
        ),
        const SizedBox(width: 10),
        _summaryCard(
          emoji: trend != null && trend >= 0 ? '📈' : '📉',
          value: trend != null
              ? '${trend >= 0 ? '+' : ''}${trend.toStringAsFixed(0)}%'
              : '—',
          label: 'Xu hướng',
        ),
      ],
    );
  }

  Widget _summaryCard(
      {required String emoji, required String value, required String label}) {
    return Expanded(
      child: Container(
        padding: const EdgeInsets.all(14),
        decoration: BoxDecoration(
          color: Colors.white.withOpacity(0.1),
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: Colors.white.withOpacity(0.1)),
        ),
        child: Column(
          children: [
            Text(emoji, style: const TextStyle(fontSize: 24)),
            const SizedBox(height: 6),
            Text(value,
                style: const TextStyle(
                    color: Colors.white,
                    fontSize: 20,
                    fontWeight: FontWeight.bold)),
            const SizedBox(height: 2),
            Text(label,
                style: TextStyle(
                    color: Colors.white.withOpacity(0.5), fontSize: 11)),
          ],
        ),
      ),
    );
  }

  Widget _buildDistributionChart(MoodStats stats) {
    final maxCount = stats.distribution.values.fold<int>(
        1, (a, b) => a > b ? a : b);

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.08),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Column(
        children: Mood.values.map((mood) {
          final count = stats.distribution[mood] ?? 0;
          final fraction = maxCount > 0 ? count / maxCount : 0.0;
          return Padding(
            padding: const EdgeInsets.symmetric(vertical: 6),
            child: Row(
              children: [
                SizedBox(
                  width: 32,
                  child: Text(mood.emoji,
                      style: const TextStyle(fontSize: 20)),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: Stack(
                    children: [
                      Container(
                        height: 24,
                        decoration: BoxDecoration(
                          color: Colors.white.withOpacity(0.06),
                          borderRadius: BorderRadius.circular(12),
                        ),
                      ),
                      FractionallySizedBox(
                        widthFactor: fraction.clamp(0.02, 1.0),
                        child: Container(
                          height: 24,
                          decoration: BoxDecoration(
                            color: mood.color.withOpacity(0.6),
                            borderRadius: BorderRadius.circular(12),
                          ),
                          alignment: Alignment.centerRight,
                          padding: const EdgeInsets.only(right: 8),
                          child: Text('$count',
                              style: const TextStyle(
                                  color: Colors.white,
                                  fontSize: 12,
                                  fontWeight: FontWeight.w600)),
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(width: 8),
                SizedBox(
                  width: 64,
                  child: Text(mood.label,
                      style: TextStyle(
                          color: Colors.white.withOpacity(0.6),
                          fontSize: 11)),
                ),
              ],
            ),
          );
        }).toList(),
      ),
    );
  }

  Widget _buildTagCloud(MoodStats stats) {
    final sorted = stats.tagFrequency.entries.toList()
      ..sort((a, b) => b.value.compareTo(a.value));

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.08),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Wrap(
        spacing: 8,
        runSpacing: 8,
        children: sorted.map((e) {
          return Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
            decoration: BoxDecoration(
              color: const Color(0xFF52B788).withOpacity(0.2),
              borderRadius: BorderRadius.circular(20),
              border: Border.all(
                  color: const Color(0xFF52B788).withOpacity(0.4)),
            ),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                Text(e.key.emoji, style: const TextStyle(fontSize: 16)),
                const SizedBox(width: 6),
                Text('${e.key.label} (${e.value})',
                    style: TextStyle(
                        color: Colors.white.withOpacity(0.8), fontSize: 13)),
              ],
            ),
          );
        }).toList(),
      ),
    );
  }

  Widget _buildInsights(List<String> insights) {
    return Column(
      children: insights
          .map((i) => Container(
                width: double.infinity,
                margin: const EdgeInsets.only(bottom: 10),
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Colors.white.withOpacity(0.08),
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(color: Colors.white.withOpacity(0.1)),
                ),
                child: Text(i,
                    style: const TextStyle(
                        color: Colors.white, fontSize: 14, height: 1.5)),
              ))
          .toList(),
    );
  }
}
