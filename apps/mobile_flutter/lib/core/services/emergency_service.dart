import 'package:flutter/material.dart';

class EmergencyService {
  Future<void> triggerEmergency(BuildContext context) async {
    await showDialog<void>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Emergency Call'),
        content: const Text('Goi cap cuu 115 neu co dau hieu nguy cap.'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Dong'),
          ),
        ],
      ),
    );
  }
}
