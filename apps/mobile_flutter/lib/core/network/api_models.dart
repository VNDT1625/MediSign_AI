class TriageResult {
  const TriageResult({
    required this.urgencyLevel,
    required this.summary,
    required this.recommendations,
  });

  final String urgencyLevel;
  final String summary;
  final List<String> recommendations;
}

class MedicineScanResult {
  const MedicineScanResult({
    required this.normalizedName,
    required this.riskLevel,
    required this.warnings,
    required this.guidance,
  });

  final String normalizedName;
  final String riskLevel;
  final List<String> warnings;
  final String guidance;
}

class AuthTokens {
  const AuthTokens({
    required this.accessToken,
    required this.refreshToken,
    this.tokenType = 'bearer',
  });

  final String accessToken;
  final String refreshToken;
  final String tokenType;
}
