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

/// A single medicine in the personal cabinet (mirrors `CabinetItemResponse`
/// in `apps/backend_fastapi/app/schemas/medicine.py`).
class CabinetItem {
  const CabinetItem({
    required this.id,
    required this.name,
    required this.warnings,
    required this.isActive,
    required this.createdAt,
    required this.updatedAt,
    this.dosage,
    this.riskLevel,
    this.guidance,
    this.remainingPills,
    this.doctorNotes,
    this.startDate,
    this.endDate,
  });

  final String id;
  final String name;
  final String? dosage;
  final String? riskLevel;
  final List<String> warnings;
  final String? guidance;
  final int? remainingPills;
  final String? doctorNotes;
  final bool isActive;
  final DateTime? startDate;
  final DateTime? endDate;
  final DateTime createdAt;
  final DateTime updatedAt;

  factory CabinetItem.fromJson(Map<String, dynamic> json) {
    final rawWarnings = json['warnings'];
    final warnings = rawWarnings is List
        ? rawWarnings.map((e) => e.toString()).toList()
        : <String>[];

    DateTime? parseDate(dynamic value) {
      if (value == null) return null;
      return DateTime.tryParse(value.toString());
    }

    return CabinetItem(
      id: (json['id'] ?? '') as String,
      name: (json['name'] ?? '') as String,
      dosage: json['dosage'] as String?,
      riskLevel: json['risk_level'] as String?,
      warnings: warnings,
      guidance: json['guidance'] as String?,
      remainingPills: json['remaining_pills'] is int
          ? json['remaining_pills'] as int
          : null,
      doctorNotes: json['doctor_notes'] as String?,
      isActive: (json['is_active'] ?? true) as bool,
      startDate: parseDate(json['start_date']),
      endDate: parseDate(json['end_date']),
      createdAt: parseDate(json['created_at']) ?? DateTime.now(),
      updatedAt: parseDate(json['updated_at']) ?? DateTime.now(),
    );
  }
}

/// Payload for creating or patching a [CabinetItem]. All fields are optional
/// for `PATCH`; `name` is required for `POST`.
class CabinetItemInput {
  const CabinetItemInput({
    this.name,
    this.dosage,
    this.riskLevel,
    this.warnings,
    this.guidance,
    this.remainingPills,
    this.doctorNotes,
    this.isActive,
    this.startDate,
    this.endDate,
  });

  final String? name;
  final String? dosage;
  final String? riskLevel;
  final List<String>? warnings;
  final String? guidance;
  final int? remainingPills;
  final String? doctorNotes;
  final bool? isActive;
  final DateTime? startDate;
  final DateTime? endDate;

  Map<String, dynamic> toJson() {
    final body = <String, dynamic>{};
    if (name != null) body['name'] = name;
    if (dosage != null) body['dosage'] = dosage;
    if (riskLevel != null) body['risk_level'] = riskLevel;
    if (warnings != null) body['warnings'] = warnings;
    if (guidance != null) body['guidance'] = guidance;
    if (remainingPills != null) body['remaining_pills'] = remainingPills;
    if (doctorNotes != null) body['doctor_notes'] = doctorNotes;
    if (isActive != null) body['is_active'] = isActive;
    if (startDate != null) {
      body['start_date'] = startDate!.toIso8601String().substring(0, 10);
    }
    if (endDate != null) {
      body['end_date'] = endDate!.toIso8601String().substring(0, 10);
    }
    return body;
  }
}

/// Daily journal entry in Soul Garden (mirrors `JournalResponse` in
/// `apps/backend_fastapi/app/api/routes/journal.py`).
class JournalRecord {
  const JournalRecord({
    required this.id,
    required this.date,
    required this.tags,
    required this.treePoints,
    required this.createdAt,
    required this.updatedAt,
    this.mood,
    this.content,
    this.aiAnalysis,
  });

  final String id;
  final DateTime date;

  /// Mood is `1 (very bad) … 5 (very good)`. May be null when the user has
  /// only typed content without picking a face.
  final int? mood;
  final String? content;
  final List<String> tags;
  final String? aiAnalysis;
  final int treePoints;
  final DateTime createdAt;
  final DateTime updatedAt;

  factory JournalRecord.fromJson(Map<String, dynamic> json) {
    final rawTags = json['tags'];
    final tags = rawTags is List
        ? rawTags.map((e) => e.toString()).toList()
        : <String>[];
    DateTime parseDate(dynamic value, {DateTime? fallback}) {
      final parsed =
          value == null ? null : DateTime.tryParse(value.toString());
      return parsed ?? fallback ?? DateTime.now();
    }

    return JournalRecord(
      id: (json['id'] ?? '') as String,
      date: parseDate(json['date']),
      mood: json['mood'] is int ? json['mood'] as int : null,
      content: json['content'] as String?,
      tags: tags,
      aiAnalysis: json['ai_analysis'] as String?,
      treePoints: json['tree_points'] is int ? json['tree_points'] as int : 0,
      createdAt: parseDate(json['created_at']),
      updatedAt: parseDate(json['updated_at']),
    );
  }
}

/// Payload for creating / patching a journal entry.
class JournalInput {
  const JournalInput({
    this.date,
    this.mood,
    this.content,
    this.tags,
  });

  final DateTime? date;
  final int? mood;
  final String? content;
  final List<String>? tags;

  Map<String, dynamic> toJson({bool isCreate = false}) {
    final body = <String, dynamic>{};
    if (isCreate) {
      // Backend defaults date to "today" if missing — only emit when set.
      final stamp = (date ?? DateTime.now()).toIso8601String().substring(0, 10);
      body['date'] = stamp;
    } else if (date != null) {
      body['date'] = date!.toIso8601String().substring(0, 10);
    }
    if (mood != null) body['mood'] = mood;
    if (content != null) body['content'] = content;
    if (tags != null) body['tags'] = tags;
    return body;
  }
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
