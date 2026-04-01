import 'package:flutter/material.dart';

import '../../../core/network/api_contracts.dart';
import '../../../core/network/api_models.dart';
import '../../../core/theme/glass_theme.dart';

class MedicineScanPage extends StatefulWidget {
  const MedicineScanPage({
    super.key,
    required this.medicineApi,
  });

  final MedicineApi medicineApi;

  @override
  State<MedicineScanPage> createState() => _MedicineScanPageState();
}

class _MedicineScanPageState extends State<MedicineScanPage> {
  final TextEditingController _textController = TextEditingController();
  MedicineScanResult? _result;
  bool _loading = false;

  Color _riskColor(String level) {
    final normalized = level.toLowerCase();
    if (normalized.contains('cao') || normalized.contains('high')) {
      return const Color(0xFFE11D48);
    }
    if (normalized.contains('trung') || normalized.contains('medium')) {
      return const Color(0xFFF59E0B);
    }
    return const Color(0xFF10B981);
  }

  @override
  void dispose() {
    _textController.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    final extractedText = _textController.text.trim();
    if (extractedText.length < 2) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Nhập ít nhất 2 ký tự tên thuốc.')),
      );
      return;
    }

    setState(() => _loading = true);

    final result = await widget.medicineApi.scan(
      extractedText: extractedText,
      currentMedications: const ['alcohol'],
    );

    if (!mounted) return;

    setState(() {
      _result = result;
      _loading = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    return GlassTheme.scaffoldBackground(
      child: SafeArea(
        child: ListView(
          padding: const EdgeInsets.fromLTRB(20, 16, 20, 24),
          children: [
            // Header
            GlassTheme.glassCard(
              padding: const EdgeInsets.all(18),
              child: Row(
                children: [
                  Container(
                    width: 56,
                    height: 56,
                    decoration: BoxDecoration(
                      gradient: const LinearGradient(
                        colors: [Color(0xFF2563EB), Color(0xFF0EA5E9)],
                      ),
                      borderRadius: BorderRadius.circular(16),
                    ),
                    child: const Center(
                        child: Text('💊', style: TextStyle(fontSize: 28))),
                  ),
                  const SizedBox(width: 16),
                  const Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text('Quét thuốc thông minh', style: GlassTheme.h3),
                        SizedBox(height: 4),
                        Text('Kiểm tra rủi ro tương tác',
                            style: GlassTheme.caption),
                      ],
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 20),

            // Input Card
            GlassTheme.glassCard(
              padding: const EdgeInsets.all(18),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('Nhập tên thuốc',
                      style: GlassTheme.h3.copyWith(fontSize: 16)),
                  const SizedBox(height: 12),
                  GlassTheme.textField(
                    controller: _textController,
                    hint: 'Ví dụ: Paracetamol 500mg...',
                    maxLines: 3,
                  ),
                  const SizedBox(height: 16),
                  GlassTheme.primaryButton(
                    text: _loading ? 'Đang quét...' : 'Kiểm tra thuốc',
                    icon: _loading ? null : Icons.document_scanner_outlined,
                    isLoading: _loading,
                    onPressed: _loading ? null : _submit,
                    backgroundColor: const Color(0xFF2563EB),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 20),

            // Result
            if (_result != null) _buildResultCard(),
          ],
        ),
      ),
    );
  }

  Widget _buildResultCard() {
    final color = _riskColor(_result!.riskLevel);
    return GlassTheme.glassCard(
      padding: const EdgeInsets.all(18),
      borderColor: color.withOpacity(0.5),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Expanded(
                  child: Text(_result!.normalizedName, style: GlassTheme.h3)),
              GlassTheme.statusBadge(text: _result!.riskLevel, color: color),
            ],
          ),
          const SizedBox(height: 16),
          const Text('Cảnh báo', style: GlassTheme.label),
          const SizedBox(height: 10),
          ..._result!.warnings.map((warning) => Padding(
                padding: const EdgeInsets.only(bottom: 8),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Icon(Icons.warning_amber_rounded, size: 18, color: color),
                    const SizedBox(width: 10),
                    Expanded(child: Text(warning, style: GlassTheme.body)),
                  ],
                ),
              )),
          const SizedBox(height: 16),
          const Text('Hướng dẫn', style: GlassTheme.label),
          const SizedBox(height: 8),
          Text(_result!.guidance, style: GlassTheme.body),
        ],
      ),
    );
  }
}
