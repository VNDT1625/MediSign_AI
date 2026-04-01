// Fitness Service - Pose Detection & Analysis
// Uses Google ML Kit Pose Detection for real-time pose estimation

import 'dart:math' as math;
import 'package:google_mlkit_pose_detection/google_mlkit_pose_detection.dart';
import '../models/fitness_model.dart';

class FitnessService {
  late PoseDetector _poseDetector;
  bool _isInitialized = false;

  // Callback for pose results
  Function(Pose)? onPoseResult;

  bool get isInitialized => _isInitialized;

  Future<void> initialize() async {
    final options = PoseDetectorOptions(
      mode: PoseDetectionMode.stream,
      model: PoseDetectionModel.base,
    );
    _poseDetector = PoseDetector(options: options);
    _isInitialized = true;
  }

  /// Process a camera frame and return pose results
  Future<Pose?> processFrame(InputImage inputImage) async {
    if (!_isInitialized) return null;
    final poses = await _poseDetector.processImage(inputImage);
    return poses.isNotEmpty ? poses.first : null;
  }

  /// Calculate angle between three points (A-B-C)
  /// B is the vertex (e.g., knee)
  double calculateAngle(
    double ax,
    double ay,
    double bx,
    double by,
    double cx,
    double cy,
  ) {
    // Vector BA
    final baX = ax - bx;
    final baY = ay - by;

    // Vector BC
    final bcX = cx - bx;
    final bcY = cy - by;

    // Calculate angle using dot product
    final dotProduct = baX * bcX + baY * bcY;
    final magBA = math.sqrt(baX * baX + baY * baY);
    final magBC = math.sqrt(bcX * bcX + bcY * bcY);

    if (magBA == 0 || magBC == 0) return 0;

    final cosAngle = dotProduct / (magBA * magBC);
    // Clamp to avoid floating point errors
    final clampedCos = cosAngle.clamp(-1.0, 1.0);

    return math.acos(clampedCos) * (180 / math.pi);
  }

  /// Extract key angles for an exercise from pose landmarks
  /// Uses ML Kit's PoseLandmarkType map instead of list
  Map<String, double> extractExerciseAngles(
    String exerciseId,
    Map<PoseLandmarkType, PoseLandmark> landmarks,
  ) {
    final angles = <String, double>{};

    // Helper to get landmark with safety check
    PoseLandmark? getLandmark(PoseLandmarkType type) {
      final lm = landmarks[type];
      if (lm == null || lm.likelihood < 0.5) return null;
      return lm;
    }

    switch (exerciseId) {
      case 'squat':
        // Get keypoints: hip, knee, ankle
        final leftHip = getLandmark(PoseLandmarkType.leftHip);
        final leftKnee = getLandmark(PoseLandmarkType.leftKnee);
        final leftAnkle = getLandmark(PoseLandmarkType.leftAnkle);
        final rightHip = getLandmark(PoseLandmarkType.rightHip);
        final rightKnee = getLandmark(PoseLandmarkType.rightKnee);
        final rightAnkle = getLandmark(PoseLandmarkType.rightAnkle);
        final leftShoulder = getLandmark(PoseLandmarkType.leftShoulder);
        // ignore: unused_local_variable
        final rightShoulder = getLandmark(PoseLandmarkType.rightShoulder);

        if (leftHip != null && leftKnee != null && leftAnkle != null) {
          // Knee angle (left leg)
          angles['left_knee'] = calculateAngle(
            leftHip.x,
            leftHip.y,
            leftKnee.x,
            leftKnee.y,
            leftAnkle.x,
            leftAnkle.y,
          );
        }

        if (rightHip != null && rightKnee != null && rightAnkle != null) {
          // Knee angle (right leg)
          angles['right_knee'] = calculateAngle(
            rightHip.x,
            rightHip.y,
            rightKnee.x,
            rightKnee.y,
            rightAnkle.x,
            rightAnkle.y,
          );
        }

        // Hip angle (using left side)
        if (leftHip != null && leftKnee != null && leftShoulder != null) {
          angles['left_hip'] = calculateAngle(
            leftKnee.x,
            leftKnee.y,
            leftHip.x,
            leftHip.y,
            leftShoulder.x,
            leftShoulder.y,
          );
        }

        // Back angle (shoulder-hip-knee) - using left side
        if (leftShoulder != null && leftHip != null && leftKnee != null) {
          angles['back'] = calculateAngle(
            leftShoulder.x,
            leftShoulder.y,
            leftHip.x,
            leftHip.y,
            leftKnee.x,
            leftKnee.y,
          );
        }
        break;

      case 'pushup':
        final leftElbow = getLandmark(PoseLandmarkType.leftElbow);
        final leftShoulder = getLandmark(PoseLandmarkType.leftShoulder);
        final leftWrist = getLandmark(PoseLandmarkType.leftWrist);
        final rightElbow = getLandmark(PoseLandmarkType.rightElbow);
        final rightShoulder = getLandmark(PoseLandmarkType.rightShoulder);
        final rightWrist = getLandmark(PoseLandmarkType.rightWrist);

        // Elbow angle
        if (leftShoulder != null && leftElbow != null && leftWrist != null) {
          angles['left_elbow'] = calculateAngle(
            leftShoulder.x,
            leftShoulder.y,
            leftElbow.x,
            leftElbow.y,
            leftWrist.x,
            leftWrist.y,
          );
        }
        if (rightShoulder != null && rightElbow != null && rightWrist != null) {
          angles['right_elbow'] = calculateAngle(
            rightShoulder.x,
            rightShoulder.y,
            rightElbow.x,
            rightElbow.y,
            rightWrist.x,
            rightWrist.y,
          );
        }

        // Body alignment (shoulder-hip-ankle)
        final lShoulder = getLandmark(PoseLandmarkType.leftShoulder);
        final lHip = getLandmark(PoseLandmarkType.leftHip);
        final lAnkle = getLandmark(PoseLandmarkType.leftAnkle);
        if (lShoulder != null && lHip != null && lAnkle != null) {
          angles['body'] = calculateAngle(
            lShoulder.x,
            lShoulder.y,
            lHip.x,
            lHip.y,
            lAnkle.x,
            lAnkle.y,
          );
        }
        break;

      case 'plank':
        // Body line: shoulder-hip-ankle
        final lShoulder = getLandmark(PoseLandmarkType.leftShoulder);
        final lHip = getLandmark(PoseLandmarkType.leftHip);
        final lAnkle = getLandmark(PoseLandmarkType.leftAnkle);
        if (lShoulder != null && lHip != null && lAnkle != null) {
          angles['shoulder_hip'] = calculateAngle(
            lShoulder.x,
            lShoulder.y,
            lHip.x,
            lHip.y,
            lAnkle.x,
            lAnkle.y,
          );
        }
        break;

      case 'lunge':
        final frontKnee = getLandmark(PoseLandmarkType.leftKnee);
        final frontAnkle = getLandmark(PoseLandmarkType.leftAnkle);
        final backKnee = getLandmark(PoseLandmarkType.rightKnee);
        final backAnkle = getLandmark(PoseLandmarkType.rightAnkle);
        final lHip = getLandmark(PoseLandmarkType.leftHip);
        final rHip = getLandmark(PoseLandmarkType.rightHip);

        if (lHip != null && frontKnee != null && frontAnkle != null) {
          angles['front_knee'] = calculateAngle(
            lHip.x,
            lHip.y,
            frontKnee.x,
            frontKnee.y,
            frontAnkle.x,
            frontAnkle.y,
          );
        }
        if (backAnkle != null && backKnee != null && rHip != null) {
          angles['back_knee'] = calculateAngle(
            backAnkle.x,
            backAnkle.y,
            backKnee.x,
            backKnee.y,
            rHip.x,
            rHip.y,
          );
        }
        break;

      case 'deadlift':
        final hip = getLandmark(PoseLandmarkType.leftHip);
        final knee = getLandmark(PoseLandmarkType.leftKnee);
        final ankle = getLandmark(PoseLandmarkType.leftAnkle);
        final shoulder = getLandmark(PoseLandmarkType.leftShoulder);

        if (knee != null && hip != null && shoulder != null) {
          angles['hip'] = calculateAngle(
            knee.x,
            knee.y,
            hip.x,
            hip.y,
            shoulder.x,
            shoulder.y,
          );
        }
        if (hip != null && knee != null && ankle != null) {
          angles['knee'] = calculateAngle(
            hip.x,
            hip.y,
            knee.x,
            knee.y,
            ankle.x,
            ankle.y,
          );
        }
        if (shoulder != null && hip != null && knee != null) {
          angles['back'] = calculateAngle(
                shoulder.x,
                shoulder.y,
                hip.x,
                hip.y,
                knee.x,
                knee.y,
              ) -
              180; // Relative to straight
        }
        break;
    }

    return angles;
  }

  /// Analyze form and return feedback
  FormAnalysis analyzeForm(
    String exerciseId,
    Map<String, double> currentAngles,
  ) {
    final exercise = ExerciseDatabase.getById(exerciseId);
    if (exercise == null) {
      return FormAnalysis(
        isGoodForm: false,
        score: 0,
        mistakes: ['Unknown exercise'],
        feedback: 'Bài tập không hợp lệ',
      );
    }

    final reference = exercise.reference;
    final mistakes = <String>[];
    final feedbackList = <String>[];
    double totalDeviation = 0;
    int angleCount = 0;

    // Check each angle
    for (final entry in reference.idealAngles.entries) {
      final key = entry.key;
      final idealRange = entry.value;

      // Find matching current angle
      final currentAngle = _findMatchingAngle(key, currentAngles);
      if (currentAngle == null) continue;

      angleCount++;
      final deviation = (currentAngle - idealRange.ideal).abs();

      if (!idealRange.isInRange(currentAngle)) {
        // Outside ideal range
        if (deviation > 15) {
          // Major mistake
          final mistake = _detectMistake(key, currentAngle, idealRange);
          mistakes.add(mistake);
          feedbackList.add(_getFeedback(key, currentAngle, idealRange));
        }
        totalDeviation += deviation;
      }
    }

    // Calculate score
    final score = angleCount > 0
        ? math.max(0, 100 - (totalDeviation / angleCount) * 2).toDouble()
        : 50.0;

    final isGoodForm = mistakes.isEmpty && score >= 70;

    return FormAnalysis(
      isGoodForm: isGoodForm,
      score: score,
      mistakes: mistakes,
      feedback:
          feedbackList.isEmpty ? 'Tư thế tốt! ✅' : feedbackList.join('. '),
    );
  }

  double? _findMatchingAngle(String key, Map<String, double> angles) {
    // Try exact match first
    if (angles.containsKey(key)) return angles[key];

    // Try left/right variants
    for (final angleKey in angles.keys) {
      if (angleKey.contains(key)) return angles[angleKey];
    }
    return null;
  }

  String _detectMistake(String key, double current, AngleRange ideal) {
    // Simplified mistake detection based on angle deviation direction
    if (current < ideal.min) {
      switch (key) {
        case 'knee':
          return 'chưa đủ sâu';
        case 'elbow':
          return 'chưa hạ đủ';
        default:
          return 'góc quá nhỏ';
      }
    } else {
      switch (key) {
        case 'knee':
          return 'hạ quá sâu';
        case 'elbow':
          return 'hạ quá sâu';
        case 'back':
          return 'lưng quá cong';
        default:
          return 'góc quá lớn';
      }
    }
  }

  String _getFeedback(String key, double current, AngleRange ideal) {
    final diff = current - ideal.ideal;
    final direction = diff > 0 ? 'thẳng ra' : 'xuống thêm';

    if (key == 'back' && ideal.min < 0) {
      // Neutral spine check for deadlift
      if (current.abs() > 15) {
        return 'Lưng không thẳng - NGUY HIỂM!';
      }
    }

    return 'Góc $key: ${current.toStringAsFixed(0)}° → $direction đến ${ideal.ideal.toStringAsFixed(0)}°';
  }

  void dispose() {
    _poseDetector.close();
    _isInitialized = false;
  }
}

class FormAnalysis {
  final bool isGoodForm;
  final double score;
  final List<String> mistakes;
  final String feedback;

  FormAnalysis({
    required this.isGoodForm,
    required this.score,
    required this.mistakes,
    required this.feedback,
  });
}
