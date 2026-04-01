// Exercise Selection Page
// Module 6: AI Fitness Coach

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../../../core/models/fitness_model.dart';

class ExerciseSelectionPage extends StatelessWidget {
  final FitnessGoal goal;
  final Function(Exercise) onExerciseSelected;
  final VoidCallback? onBack;

  const ExerciseSelectionPage({
    super.key,
    required this.goal,
    required this.onExerciseSelected,
    this.onBack,
  });

  static const _primaryColor = Color(0xFF059669);
  static const _bgGradientTop = Color(0xFFF0FDF4);

  @override
  Widget build(BuildContext context) {
    final exercises = _getExercisesForGoal(goal);

    return Scaffold(
      backgroundColor: Colors.white,
      appBar: AppBar(
        title: const Text(
          'Chọn bài tập',
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
          child: Column(
            children: [
              // Goal header banner
              Container(
                margin: const EdgeInsets.fromLTRB(20, 16, 20, 0),
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  gradient: const LinearGradient(
                    colors: [Color(0xFF059669), Color(0xFF0D9488)],
                  ),
                  borderRadius: BorderRadius.circular(16),
                  boxShadow: [
                    BoxShadow(
                      color: _primaryColor.withOpacity(0.25),
                      blurRadius: 12,
                      offset: const Offset(0, 4),
                    ),
                  ],
                ),
                child: Row(
                  children: [
                    Container(
                      width: 48,
                      height: 48,
                      decoration: BoxDecoration(
                        color: Colors.white.withOpacity(0.15),
                        borderRadius: BorderRadius.circular(14),
                      ),
                      child: const Icon(Icons.fitness_center_rounded,
                          color: Colors.white, size: 26),
                    ),
                    const SizedBox(width: 14),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'Mục tiêu: ${goal.name}',
                            style: const TextStyle(
                              fontFamily: 'Outfit',
                              color: Colors.white,
                              fontSize: 17,
                              fontWeight: FontWeight.w700,
                            ),
                          ),
                          const SizedBox(height: 2),
                          Text(
                            '${exercises.length} bài tập được gợi ý',
                            style: TextStyle(
                              fontFamily: 'Outfit',
                              color: Colors.white.withOpacity(0.8),
                              fontSize: 13,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 20),

              const Padding(
                padding: EdgeInsets.symmetric(horizontal: 20),
                child: Align(
                  alignment: Alignment.centerLeft,
                  child: Text(
                    'Danh sách bài tập',
                    style: TextStyle(
                      fontFamily: 'Outfit',
                      fontSize: 18,
                      fontWeight: FontWeight.w700,
                      color: Color(0xFF111827),
                    ),
                  ),
                ),
              ),
              const SizedBox(height: 12),

              // Exercise list
              Expanded(
                child: ListView.builder(
                  padding: const EdgeInsets.fromLTRB(20, 0, 20, 12),
                  itemCount: exercises.length,
                  itemBuilder: (context, index) {
                    final exercise = exercises[index];
                    return _ExerciseCard(
                      exercise: exercise,
                      onTap: () {
                        HapticFeedback.mediumImpact();
                        onExerciseSelected(exercise);
                      },
                    );
                  },
                ),
              ),

              // Safety reminder
              Padding(
                padding: const EdgeInsets.fromLTRB(20, 0, 20, 16),
                child: Semantics(
                  label: 'Khởi động trước khi tập để tránh chấn thương',
                  child: Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: const Color(0xFFFFFBEB),
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(color: const Color(0xFFFDE68A)),
                    ),
                    child: const Row(
                      children: [
                        Icon(Icons.warning_amber_rounded,
                            color: Color(0xFF92400E), size: 20),
                        SizedBox(width: 10),
                        Expanded(
                          child: Text(
                            'Khởi động trước khi tập để tránh chấn thương',
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
              ),
            ],
          ),
        ),
      ),
    );
  }

  List<Exercise> _getExercisesForGoal(FitnessGoal goal) {
    return ExerciseDatabase.mvpExercises;
  }
}

class _ExerciseCard extends StatelessWidget {
  final Exercise exercise;
  final VoidCallback onTap;

  const _ExerciseCard({
    required this.exercise,
    required this.onTap,
  });

  IconData _getIconForExercise(String id) {
    switch (id) {
      case 'squat':
        return Icons.fitness_center_rounded;
      case 'pushup':
        return Icons.sports_gymnastics_rounded;
      case 'plank':
        return Icons.accessibility_new_rounded;
      case 'lunge':
        return Icons.directions_walk_rounded;
      case 'deadlift':
        return Icons.fitness_center_rounded;
      default:
        return Icons.fitness_center_rounded;
    }
  }

  Color _getColorForTarget(String target) {
    switch (target) {
      case 'lower_body':
        return const Color(0xFF3B82F6);
      case 'upper_body':
        return const Color(0xFFF97316);
      case 'core':
        return const Color(0xFF8B5CF6);
      default:
        return const Color(0xFF6B7280);
    }
  }

  @override
  Widget build(BuildContext context) {
    final color = _getColorForTarget(exercise.targetArea);

    return Semantics(
      button: true,
      label: '${exercise.nameVi}. ${exercise.descriptionVi}',
      child: Padding(
        padding: const EdgeInsets.only(bottom: 12),
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
                padding: const EdgeInsets.all(16),
                child: Row(
                  children: [
                    Container(
                      width: 56,
                      height: 56,
                      decoration: BoxDecoration(
                        color: color.withOpacity(0.10),
                        borderRadius: BorderRadius.circular(14),
                      ),
                      child: Icon(
                        _getIconForExercise(exercise.id),
                        color: color,
                        size: 28,
                      ),
                    ),
                    const SizedBox(width: 14),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            exercise.nameVi,
                            style: const TextStyle(
                              fontFamily: 'Outfit',
                              fontSize: 17,
                              fontWeight: FontWeight.w700,
                              color: Color(0xFF111827),
                            ),
                          ),
                          const SizedBox(height: 3),
                          Text(
                            exercise.descriptionVi,
                            style: const TextStyle(
                              fontFamily: 'Outfit',
                              fontSize: 13,
                              color: Color(0xFF6B7280),
                            ),
                          ),
                          const SizedBox(height: 8),
                          Wrap(
                            spacing: 6,
                            runSpacing: 4,
                            children:
                                exercise.muscleGroups.take(3).map((muscle) {
                              return Container(
                                padding: const EdgeInsets.symmetric(
                                  horizontal: 8,
                                  vertical: 3,
                                ),
                                decoration: BoxDecoration(
                                  color: color.withOpacity(0.08),
                                  borderRadius: BorderRadius.circular(10),
                                ),
                                child: Text(
                                  muscle,
                                  style: TextStyle(
                                    fontFamily: 'Outfit',
                                    fontSize: 11,
                                    fontWeight: FontWeight.w500,
                                    color: color,
                                  ),
                                ),
                              );
                            }).toList(),
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
      ),
    );
  }
}
