import 'package:flutter/material.dart';

import '../../../core/models/consult_mode.dart';
import '../../../core/network/api_contracts.dart';
import '../../../core/network/api_models.dart';
import '../../../core/theme/glass_theme.dart';

class ConsultPage extends StatefulWidget {
  const ConsultPage({
    super.key,
    required this.mode,
    required this.consultApi,
  });

  final ConsultMode mode;
  final ConsultApi consultApi;

  @override
  State<ConsultPage> createState() => _ConsultPageState();
}

class _ConsultPageState extends State<ConsultPage> {
  final TextEditingController _symptomController = TextEditingController();
  TriageResult? _result;
  bool _loading = false;

  Color _urgencyColor(String level) {
    final normalized = level.toLowerCase();
    if (normalized.contains('cao') || normalized.contains('high')) {
      return const Color(0xFFE11D48);
    }
    if (normalized.contains('trung') || normalized.contains('medium')) {
      return const Color(0xFFF59E0B);
    }
    return const Color(0xFF10B981);
  }

  Color _modeColor() {
    switch (widget.mode) {
      case ConsultMode.hybrid:
        return const Color(0xFF0D9B6B);
      case ConsultMode.local:
        return const Color(0xFF2563EB);
      case ConsultMode.cloud:
        return const Color(0xFF7C3AED);
    }
  }

  @override
  void dispose() {
    _symptomController.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    final symptomText = _symptomController.text.trim();
    if (symptomText.length < 3) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
            content: Text('Nhập ít nhất 3 ký tự mô tả triệu chứng.')),
      );
      return;
    }

    setState(() {
      _loading = true;
    });

    final result = await widget.consultApi
        .triage(symptomText: symptomText, mode: widget.mode);

    if (!mounted) return;

    setState(() {
      _result = result;
      _loading = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    final modeColor = _modeColor();
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
                      gradient: LinearGradient(
                          colors: [modeColor, modeColor.withOpacity(0.7)]),
                      borderRadius: BorderRadius.circular(16),
                    ),
                    child: const Center(
                        child: Text('🩺', style: TextStyle(fontSize: 28))),
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text('Bác sĩ AI tư vấn nhanh',
                            style: GlassTheme.h3),
                        const SizedBox(height: 4),
                        Text('Chế độ: ${widget.mode.title}',
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
                  Text('Mô tả triệu chứng',
                      style: GlassTheme.h3.copyWith(fontSize: 16)),
                  const SizedBox(height: 12),
                  GlassTheme.textField(
                    controller: _symptomController,
                    hint: 'Ví dụ: đau đầu 2 ngày, sốt nhẹ, mệt mỏi...',
                    maxLines: 4,
                  ),
                  const SizedBox(height: 16),
                  GlassTheme.primaryButton(
                    text: _loading ? 'Đang phân tích...' : 'Phân tích ngay',
                    icon: _loading ? null : Icons.medical_services_outlined,
                    isLoading: _loading,
                    onPressed: _loading ? null : _submit,
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
    final color = _urgencyColor(_result!.urgencyLevel);
    return GlassTheme.glassCard(
      padding: const EdgeInsets.all(18),
      borderColor: color.withOpacity(0.5),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Text('Kết quả sơ bộ',
                  style: GlassTheme.h3.copyWith(fontSize: 16)),
              const Spacer(),
              GlassTheme.statusBadge(text: _result!.urgencyLevel, color: color),
            ],
          ),
          const SizedBox(height: 16),
          Text(_result!.summary, style: GlassTheme.bodyLarge),
          const SizedBox(height: 16),
          const Text('Khuyến nghị', style: GlassTheme.label),
          const SizedBox(height: 10),
          ..._result!.recommendations.map((item) => Padding(
                padding: const EdgeInsets.only(bottom: 8),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Icon(Icons.check_circle,
                        size: 18, color: Color(0xFF0D9B6B)),
                    const SizedBox(width: 10),
                    Expanded(child: Text(item, style: GlassTheme.body)),
                  ],
                ),
              )),
        ],
      ),
    );
  }
}
