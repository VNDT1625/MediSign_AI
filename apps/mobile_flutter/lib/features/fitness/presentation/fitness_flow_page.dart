// Fitness Flow Coordinator
// Module 6: AI Fitness Coach
// Manages navigation: Goal → Exercise → Workout → Summary

import 'package:flutter/material.dart';
import '../../../core/models/fitness_model.dart';
import 'fitness_goal_page.dart';
import 'exercise_selection_page.dart';
import 'fitness_workout_page.dart';

enum _FitnessStep { goal, exercise, workout }

class FitnessFlowPage extends StatefulWidget {
  final VoidCallback? onExit;

  const FitnessFlowPage({super.key, this.onExit});

  @override
  State<FitnessFlowPage> createState() => _FitnessFlowPageState();
}

class _FitnessFlowPageState extends State<FitnessFlowPage> {
  _FitnessStep _currentStep = _FitnessStep.goal;
  FitnessGoal? _selectedGoal;
  Exercise? _selectedExercise;

  void _onGoalSelected(FitnessGoal goal) {
    setState(() {
      _selectedGoal = goal;
      _currentStep = _FitnessStep.exercise;
    });
  }

  void _onExerciseSelected(Exercise exercise) {
    setState(() {
      _selectedExercise = exercise;
      _currentStep = _FitnessStep.workout;
    });
  }

  void _onWorkoutComplete() {
    // Return to goal selection for another round
    setState(() {
      _selectedExercise = null;
      _selectedGoal = null;
      _currentStep = _FitnessStep.goal;
    });
  }

  void _goBack() {
    switch (_currentStep) {
      case _FitnessStep.goal:
        // Exit fitness flow entirely
        if (widget.onExit != null) {
          widget.onExit!();
        } else {
          Navigator.of(context).pop();
        }
        break;
      case _FitnessStep.exercise:
        setState(() {
          _currentStep = _FitnessStep.goal;
          _selectedGoal = null;
        });
        break;
      case _FitnessStep.workout:
        setState(() {
          _currentStep = _FitnessStep.exercise;
          _selectedExercise = null;
        });
        break;
    }
  }

  @override
  Widget build(BuildContext context) {
    return PopScope(
      canPop: _currentStep == _FitnessStep.goal,
      onPopInvokedWithResult: (didPop, _) {
        if (!didPop) _goBack();
      },
      child: AnimatedSwitcher(
        duration: const Duration(milliseconds: 250),
        child: _buildCurrentStep(),
      ),
    );
  }

  Widget _buildCurrentStep() {
    switch (_currentStep) {
      case _FitnessStep.goal:
        return FitnessGoalPage(
          key: const ValueKey('goal'),
          onGoalSelected: _onGoalSelected,
          onBack: _goBack,
        );

      case _FitnessStep.exercise:
        return ExerciseSelectionPage(
          key: const ValueKey('exercise'),
          goal: _selectedGoal!,
          onExerciseSelected: _onExerciseSelected,
          onBack: _goBack,
        );

      case _FitnessStep.workout:
        return FitnessWorkoutPage(
          key: const ValueKey('workout'),
          exercise: _selectedExercise!,
          onComplete: _onWorkoutComplete,
          onCancel: _goBack,
        );
    }
  }
}
