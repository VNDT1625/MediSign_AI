import '../models/consult_mode.dart';
import 'api_contracts.dart';
import 'api_models.dart';

class MockConsultApi implements ConsultApi {
  @override
  Future<TriageResult> triage({
    required String symptomText,
    required ConsultMode mode,
  }) async {
    await Future<void>.delayed(const Duration(milliseconds: 250));

    final lowered = symptomText.toLowerCase();
    var urgency = 'non_emergency';
    if (lowered.contains('kho tho') || lowered.contains('dau nguc')) {
      urgency = 'emergency';
    } else if (lowered.contains('sot') || lowered.contains('dau')) {
      urgency = 'urgent';
    }

    return TriageResult(
      urgencyLevel: urgency,
      summary: 'Mode ${mode.label}: thong tin tham khao, can theo doi them.',
      recommendations: const [
        'Uong du nuoc va nghi ngoi.',
        'Theo doi trieu chung 24 gio.',
      ],
    );
  }
}

class MockMedicineApi implements MedicineApi {
  @override
  Future<MedicineScanResult> scan({
    required String extractedText,
    List<String> currentMedications = const [],
  }) async {
    await Future<void>.delayed(const Duration(milliseconds: 250));

    final text = extractedText.trim();
    final hasAlcohol = currentMedications.any(
      (item) => item.toLowerCase().contains('alcohol'),
    );

    return MedicineScanResult(
      normalizedName: text.isEmpty ? 'Unknown' : text,
      riskLevel: hasAlcohol ? 'high' : 'low',
      warnings: [
        if (hasAlcohol)
          'Canh bao tuong tac voi ruou bia.'
        else
          'Khong co canh bao lon trong du lieu mau.',
      ],
      guidance: 'Xac minh voi duoc si truoc khi dung thuoc.',
    );
  }
}

class MockAuthApi implements AuthApi {
  @override
  Future<AuthTokens> login(
      {required String email, required String password}) async {
    await Future<void>.delayed(const Duration(milliseconds: 250));
    return const AuthTokens(
        accessToken: 'mock-access', refreshToken: 'mock-refresh');
  }

  @override
  Future<AuthTokens> refresh({required String refreshToken}) async {
    await Future<void>.delayed(const Duration(milliseconds: 250));
    return const AuthTokens(
        accessToken: 'mock-access-2', refreshToken: 'mock-refresh-2');
  }
}
