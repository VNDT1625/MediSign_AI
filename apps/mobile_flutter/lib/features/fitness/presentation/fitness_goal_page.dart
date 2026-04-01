// Fitness Goal Selection Page
// Module 6: AI Fitness Coach

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../../../core/models/fitness_model.dart';

class FitnessGoalPage extends StatelessWidget {
  final Function(FitnessGoal) onGoalSelected;
  final VoidCallback? onBack;

  const FitnessGoalPage({
    super.key,
    required this.onGoalSelected,
    this.onBack,
  });

  static const _primaryColor = Color(0xFF059669);
  static const _bgGradientTop = Color(0xFFF0FDF4);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      appBar: AppBar(
        title: const Text(
          'Tập thể dục',
          style: TextStyle(fontFamily: 'Outfit', fontWeight: FontWeight.w700),
        ),
        backgroundColor: _primaryColor,
        foregroundColor: Colors.white,
        elevation: 0,
        leading: onBack != null
            ? IconButton(
                icon: const Icon(Icons.arrow_back_rounded),
                onPressed: onBack,
              )
            : null,
      ),
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [_bgGradientTop, Colors.white],
          ),
        ),
        child: SafeArea(
          child: ListView(
            padding: const EdgeInsets.fromLTRB(20, 24, 20, 24),
            children: [
              // Header
              const Text(
                'Bạn muốn đạt được gì?',
                style: TextStyle(
                  fontFamily: 'Outfit',
                  fontSize: 26,
                  fontWeight: FontWeight.w800,
                  color: Color(0xFF111827),
                ),
              ),
              const SizedBox(height: 8),
              const Text(
                'Chúng tôi sẽ gợi ý bài tập phù hợp với mục tiêu của bạn',
                style: TextStyle(
                  fontFamily: 'Outfit',
                  fontSize: 15,
                  color: Color(0xFF6B7280),
                ),
              ),
              const SizedBox(height: 28),

              // Goal cards
              _GoalCard(
                goal: FitnessGoal.loseWeight,
                icon: Icons.local_fire_department_rounded,
                color: const Color(0xFFF97316),
                subtitle: 'Cardio, HIIT, giảm mỡ',
                onTap: () => _selectGoal(context, FitnessGoal.loseWeight),
              ),
              const SizedBox(height: 14),
              _GoalCard(
                goal: FitnessGoal.buildMuscle,
                icon: Icons.fitness_center_rounded,
                color: const Color(0xFF3B82F6),
                subtitle: 'Sức mạnh, tăng cơ bắp',
                onTap: () => _selectGoal(context, FitnessGoal.buildMuscle),
              ),
              const SizedBox(height: 14),
              _GoalCard(
                goal: FitnessGoal.maintain,
                icon: Icons.favorite_rounded,
                color: _primaryColor,
                subtitle: 'Giữ dáng, sức khỏe tổng thể',
                onTap: () => _selectGoal(context, FitnessGoal.maintain),
              ),

              const SizedBox(height: 28),

              // Disclaimer
              Semantics(
                label:
                    'Lưu ý: AI chỉ mang tính tham khảo, hãy tham khảo huấn luyện viên chuyên nghiệp.',
                child: Container(
                  padding: const EdgeInsets.all(14),
                  decoration: BoxDecoration(
                    color: const Color(0xFFFFFBEB),
                    borderRadius: BorderRadius.circular(14),
                    border: Border.all(color: const Color(0xFFFDE68A)),
                  ),
                  child: const Row(
                    children: [
                      Icon(Icons.info_outline_rounded,
                          color: Color(0xFF92400E), size: 22),
                      SizedBox(width: 12),
                      Expanded(
                        child: Text(
                          'AI chỉ mang tính tham khảo. Hãy tham khảo huấn luyện viên chuyên nghiệp để đảm bảo an toàn.',
                          style: TextStyle(
                            fontFamily: 'Outfit',
                            fontSize: 13,
                            color: Color(0xFF92400E),
                          ),
                        ),
                      ),
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

  void _selectGoal(BuildContext context, FitnessGoal goal) {
    HapticFeedback.mediumImpact();
    onGoalSelected(goal);
  }
}

class _GoalCard extends StatelessWidget {
  final FitnessGoal goal;
  final IconData icon;
  final Color color;
  final String subtitle;
  final VoidCallback onTap;

  const _GoalCard({
    required this.goal,
    required this.icon,
    required this.color,
    required this.subtitle,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Semantics(
      button: true,
      label: '${goal.name}. $subtitle',
      child: Material(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        child: InkWell(
          onTap: onTap,
          borderRadius: BorderRadius.circular(16),
          child: Ink(
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: const Color(0xFFE5E7EB)),
            ),
            child: Padding(
              padding: const EdgeInsets.all(18),
              child: Row(
                children: [
                  Container(
                    width: 56,
                    height: 56,
                    decoration: BoxDecoration(
                      color: color.withOpacity(0.12),
                      borderRadius: BorderRadius.circular(14),
                    ),
                    child: Icon(icon, color: color, size: 30),
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          goal.name,
                          style: const TextStyle(
                            fontFamily: 'Outfit',
                            fontSize: 18,
                            fontWeight: FontWeight.w700,
                            color: Color(0xFF111827),
                          ),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          subtitle,
                          style: const TextStyle(
                            fontFamily: 'Outfit',
                            fontSize: 13,
                            color: Color(0xFF6B7280),
                          ),
                        ),
                      ],
                    ),
                  ),
                  const Icon(Icons.chevron_right_rounded,
                      color: Color(0xFF9CA3AF)),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}
