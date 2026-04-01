import '../models/consult_mode.dart';
import 'api_models.dart';

abstract class ConsultApi {
  Future<TriageResult> triage({
    required String symptomText,
    required ConsultMode mode,
  });
}

abstract class MedicineApi {
  Future<MedicineScanResult> scan({
    required String extractedText,
    List<String> currentMedications,
  });
}

abstract class AuthApi {
  Future<AuthTokens> login({
    required String email,
    required String password,
  });

  Future<AuthTokens> refresh({
    required String refreshToken,
  });
}
