// AI Fitness Workout Page
// Module 6: AI Fitness Coach - Real-time pose detection and feedback

import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:camera/camera.dart';
import 'package:google_mlkit_pose_detection/google_mlkit_pose_detection.dart';
import '../../../core/models/fitness_model.dart';
import '../../../core/services/fitness_service.dart';

class FitnessWorkoutPage extends StatefulWidget {
  final Exercise exercise;
  final VoidCallback onComplete;
  final VoidCallback onCancel;

  const FitnessWorkoutPage({
    super.key,
    required this.exercise,
    required this.onComplete,
    required this.onCancel,
  });

  @override
  State<FitnessWorkoutPage> createState() => _FitnessWorkoutPageState();
}

class _FitnessWorkoutPageState extends State<FitnessWorkoutPage> {
  CameraController? _cameraController;
  final FitnessService _fitnessService = FitnessService();

  bool _isLoading = true;
  String _feedback = 'Chuẩn bị...';
  int _repCount = 0;
  int _goodReps = 0;
  double _currentScore = 100;

  final List<RepData> _repHistory = [];
  bool _isInRep = false;
  double _minAngleThisRep = 180;
  double _maxAngleThisRep = 0;

  Pose? _lastPose;

  @override
  void initState() {
    super.initState();
    _initialize();
  }

  Future<void> _initialize() async {
    try {
      // Initialize fitness service
      await _fitnessService.initialize();

      // Initialize camera
      final cameras = await availableCameras();
      if (cameras.isEmpty) {
        setState(() {
          _feedback = 'Không tìm thấy camera';
          _isLoading = false;
        });
        return;
      }

      // Use front camera
      final frontCamera = cameras.firstWhere(
        (cam) => cam.lensDirection == CameraLensDirection.front,
        orElse: () => cameras.first,
      );

      _cameraController = CameraController(
        frontCamera,
        ResolutionPreset.medium,
        enableAudio: false,
      );

      await _cameraController!.initialize();

      if (mounted) {
        setState(() {
          _isLoading = false;
          _feedback = 'Sẵn sàng! Bắt đầu tập nào!';
        });
      }

      // Start processing frames
      _startFrameProcessing();
    } catch (e) {
      setState(() {
        _feedback = 'Lỗi khởi động: $e';
        _isLoading = false;
      });
    }
  }

  void _startFrameProcessing() {
    // This would be called to process each frame
    // In production, you'd use a stream or timer
  }

  // ignore: unused_element - placeholder for future pose processing
  void _processPoseResult(Pose result) {
    if (result.landmarks.isEmpty) {
      setState(() {
        _feedback = 'Không nhận diện được cơ thể';
      });
      return;
    }

    // ML Kit returns landmarks as a Map<PoseLandmarkType, Landmark>
    final landmarks = result.landmarks;

    // Extract angles for current exercise
    final angles = _fitnessService.extractExerciseAngles(
      widget.exercise.id,
      landmarks,
    );

    // Analyze form
    final analysis = _fitnessService.analyzeForm(widget.exercise.id, angles);

    // Get primary angle (e.g., knee for squat)
    final primaryAngle = _getPrimaryAngle(angles);

    // Track rep progress
    _trackRep(primaryAngle, analysis);

    setState(() {
      _lastPose = result;
      _feedback = analysis.feedback;
      _currentScore = analysis.score;
    });
  }

  double _getPrimaryAngle(Map<String, double> angles) {
    switch (widget.exercise.id) {
      case 'squat':
        return (angles['left_knee'] ?? angles['right_knee'] ?? 180);
      case 'pushup':
        return (angles['left_elbow'] ?? angles['right_elbow'] ?? 180);
      case 'plank':
        return angles['shoulder_hip'] ?? 180;
      case 'lunge':
        return angles['front_knee'] ?? 180;
      case 'deadlift':
        return angles['back']?.abs() ?? 180;
      default:
        return 180;
    }
  }

  void _trackRep(double angle, FormAnalysis analysis) {
    // Simplified rep counting based on angle thresholds
    final threshold = widget.exercise.id == 'plank'
        ? 0 // plank is hold, not rep
        : 90; // typical rep threshold

    if (widget.exercise.id == 'plank') {
      // For plank, just track time
      return;
    }

    if (angle < threshold && !_isInRep) {
      // Start of new rep (going down)
      _isInRep = true;
      _minAngleThisRep = angle;
    } else if (angle > threshold && _isInRep) {
      // End of rep (coming up)
      _isInRep = false;
      _maxAngleThisRep = angle;

      // Record rep
      _repCount++;
      final isGood = analysis.isGoodForm && _minAngleThisRep < threshold - 10;
      if (isGood) _goodReps++;

      _repHistory.add(RepData(
        repNumber: _repCount,
        minAngle: _minAngleThisRep,
        maxAngle: _maxAngleThisRep,
        isGoodForm: isGood,
        mistakes: analysis.mistakes,
      ));

      HapticFeedback.lightImpact();
    }

    if (_isInRep && angle < _minAngleThisRep) {
      _minAngleThisRep = angle;
    }
  }

  @override
  void dispose() {
    _cameraController?.dispose();
    _fitnessService.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black,
      appBar: AppBar(
        title: Text(widget.exercise.nameVi),
        backgroundColor: Colors.transparent,
        foregroundColor: Colors.white,
        elevation: 0,
        actions: [
          IconButton(
            icon: const Icon(Icons.close),
            onPressed: () {
              _showExitDialog();
            },
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator(color: Colors.white))
          : Column(
              children: [
                // Camera preview with pose overlay
                Expanded(
                  flex: 3,
                  child: Stack(
                    fit: StackFit.expand,
                    children: [
                      // Camera preview
                      if (_cameraController != null &&
                          _cameraController!.value.isInitialized)
                        Transform.scale(
                          scaleX: -1, // Mirror for front camera
                          child: CameraPreview(_cameraController!),
                        ),

                      // Pose skeleton overlay (custom paint)
                      CustomPaint(
                        painter: PoseSkeletonPainter(
                          pose: _lastPose,
                          isGoodForm: _currentScore >= 70,
                        ),
                      ),

                      // Angle indicator
                      Positioned(
                        top: 16,
                        left: 16,
                        child: Container(
                          padding: const EdgeInsets.symmetric(
                            horizontal: 12,
                            vertical: 6,
                          ),
                          decoration: BoxDecoration(
                            color: _currentScore >= 70
                                ? Colors.green
                                : Colors.orange,
                            borderRadius: BorderRadius.circular(20),
                          ),
                          child: Text(
                            'Form: ${_currentScore.toStringAsFixed(0)}%',
                            style: const TextStyle(
                              color: Colors.white,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ),
                      ),
                    ],
                  ),
                ),

                // Feedback panel
                Container(
                  padding: const EdgeInsets.all(20),
                  decoration: const BoxDecoration(
                    color: Color(0xFF1E1E1E),
                    borderRadius: BorderRadius.vertical(
                      top: Radius.circular(24),
                    ),
                  ),
                  child: SafeArea(
                    top: false,
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        // Feedback text
                        Text(
                          _feedback,
                          style: const TextStyle(
                            fontSize: 18,
                            color: Colors.white,
                            fontWeight: FontWeight.w500,
                          ),
                          textAlign: TextAlign.center,
                        ),
                        const SizedBox(height: 20),

                        // Rep counter
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                          children: [
                            _StatItem(
                              label: 'Reps',
                              value: '$_repCount',
                              icon: Icons.repeat,
                            ),
                            _StatItem(
                              label: 'Tốt',
                              value: '$_goodReps',
                              icon: Icons.check_circle,
                              color: Colors.green,
                            ),
                            _StatItem(
                              label: 'Cần cải thiện',
                              value: '${_repCount - _goodReps}',
                              icon: Icons.warning,
                              color: Colors.orange,
                            ),
                          ],
                        ),
                        const SizedBox(height: 20),

                        // Action buttons
                        Row(
                          children: [
                            Expanded(
                              child: OutlinedButton(
                                onPressed: _showExitDialog,
                                style: OutlinedButton.styleFrom(
                                  foregroundColor: Colors.white,
                                  side: const BorderSide(color: Colors.white54),
                                  padding:
                                      const EdgeInsets.symmetric(vertical: 16),
                                ),
                                child: const Text('Dừng'),
                              ),
                            ),
                            const SizedBox(width: 16),
                            Expanded(
                              child: ElevatedButton(
                                onPressed: _finishWorkout,
                                style: ElevatedButton.styleFrom(
                                  backgroundColor: const Color(0xFF0D9B6B),
                                  foregroundColor: Colors.white,
                                  padding:
                                      const EdgeInsets.symmetric(vertical: 16),
                                ),
                                child: const Text('Hoàn thành'),
                              ),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                ),
              ],
            ),
    );
  }

  void _showExitDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Dừng tập?'),
        content: const Text('Bạn có muốn dừng buổi tập không?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Tiếp tục tập'),
          ),
          TextButton(
            onPressed: () {
              Navigator.pop(context);
              widget.onCancel();
            },
            child: const Text('Dừng'),
          ),
        ],
      ),
    );
  }

  void _finishWorkout() {
    final score = _repCount > 0 ? (_goodReps / _repCount * 100) : 0.0;

    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Hoàn thành buổi tập! 🎉'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              score >= 70 ? Icons.emoji_events : Icons.fitness_center,
              size: 64,
              color: score >= 70 ? Colors.amber : Colors.grey,
            ),
            const SizedBox(height: 16),
            Text(
              'Form Score: ${score.toStringAsFixed(0)}%',
              style: const TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              'Tổng reps: $_repCount | Tốt: $_goodReps',
              style: const TextStyle(color: Colors.grey),
            ),
          ],
        ),
        actions: [
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              widget.onComplete();
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFF0D9B6B),
            ),
            child: const Text('Hoàn thành'),
          ),
        ],
      ),
    );
  }
}

class _StatItem extends StatelessWidget {
  final String label;
  final String value;
  final IconData icon;
  final Color? color;

  const _StatItem({
    required this.label,
    required this.value,
    required this.icon,
    this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Icon(icon, color: color ?? Colors.white54, size: 24),
        const SizedBox(height: 4),
        Text(
          value,
          style: TextStyle(
            fontSize: 24,
            fontWeight: FontWeight.bold,
            color: color ?? Colors.white,
          ),
        ),
        Text(
          label,
          style: const TextStyle(
            fontSize: 12,
            color: Colors.white54,
          ),
        ),
      ],
    );
  }
}

// Custom painter for pose skeleton overlay
class PoseSkeletonPainter extends CustomPainter {
  final Pose? pose;
  final bool isGoodForm;

  PoseSkeletonPainter({
    this.pose,
    required this.isGoodForm,
  });

  @override
  void paint(Canvas canvas, Size size) {
    if (pose == null || pose!.landmarks.isEmpty) return;

    final landmarks = pose!.landmarks;
    final paint = Paint()
      ..color = isGoodForm ? Colors.green : Colors.orange
      ..strokeWidth = 4
      ..style = PaintingStyle.stroke;

    // ML Kit landmark connections (by index in MediaPipe order)
    final connections = [
      // Body
      [PoseLandmarkType.leftShoulder, PoseLandmarkType.rightShoulder],
      [PoseLandmarkType.leftShoulder, PoseLandmarkType.leftHip],
      [PoseLandmarkType.rightShoulder, PoseLandmarkType.rightHip],
      [PoseLandmarkType.leftHip, PoseLandmarkType.rightHip],
      // Left arm
      [PoseLandmarkType.leftShoulder, PoseLandmarkType.leftElbow],
      [PoseLandmarkType.leftElbow, PoseLandmarkType.leftWrist],
      // Right arm
      [PoseLandmarkType.rightShoulder, PoseLandmarkType.rightElbow],
      [PoseLandmarkType.rightElbow, PoseLandmarkType.rightWrist],
      // Left leg
      [PoseLandmarkType.leftHip, PoseLandmarkType.leftKnee],
      [PoseLandmarkType.leftKnee, PoseLandmarkType.leftAnkle],
      [PoseLandmarkType.leftAnkle, PoseLandmarkType.leftFootIndex],
      // Right leg
      [PoseLandmarkType.rightHip, PoseLandmarkType.rightKnee],
      [PoseLandmarkType.rightKnee, PoseLandmarkType.rightAnkle],
      [PoseLandmarkType.rightAnkle, PoseLandmarkType.rightFootIndex],
    ];

    for (final conn in connections) {
      final p1 = landmarks[conn[0]];
      final p2 = landmarks[conn[1]];
      if (p1 != null &&
          p2 != null &&
          p1.likelihood > 0.5 &&
          p2.likelihood > 0.5) {
        canvas.drawLine(
          Offset(p1.x * size.width, p1.y * size.height),
          Offset(p2.x * size.width, p2.y * size.height),
          paint,
        );
      }
    }

    // Draw keypoints
    final dotPaint = Paint()
      ..color = isGoodForm ? Colors.green : Colors.orange
      ..style = PaintingStyle.fill;

    for (final landmark in landmarks.values) {
      if (landmark.likelihood > 0.5) {
        canvas.drawCircle(
          Offset(landmark.x * size.width, landmark.y * size.height),
          6,
          dotPaint,
        );
      }
    }
  }

  @override
  bool shouldRepaint(covariant PoseSkeletonPainter oldDelegate) {
    return oldDelegate.pose != pose || oldDelegate.isGoodForm != isGoodForm;
  }
}
