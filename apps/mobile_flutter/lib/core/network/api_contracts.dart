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

/// Personal medicine cabinet — talks to `/medicine/cabinet/*`.
///
/// All operations require an authenticated user (the backend pulls the user
/// from the Bearer token, never from the request body).
abstract class CabinetApi {
  /// List active items in the user's cabinet (newest first).
  Future<List<CabinetItem>> list();

  /// Add a new item; returns the freshly persisted record.
  Future<CabinetItem> add(CabinetItemInput input);

  /// Partially update an item.
  Future<CabinetItem> update(String itemId, CabinetItemInput patch);

  /// Permanently remove an item.
  Future<void> remove(String itemId);

  /// Decrement `remainingPills` by 1 (no-op when null/zero).
  Future<CabinetItem> recordDose(String itemId);
}

/// Soul Garden daily journal — talks to `/journal/*`.
///
/// Used by the SoulGarden mood tracker and gamification tree state. All
/// operations require auth.
abstract class JournalApi {
  /// List journal entries (newest first), optionally bounded to a date range.
  Future<List<JournalRecord>> list({
    DateTime? from,
    DateTime? to,
    int page = 1,
    int pageSize = 50,
  });

  /// Create a new entry. Returns `null` when the day already has an entry —
  /// callers should fall back to [update] using the returned id.
  Future<JournalRecord> create(JournalInput input);

  /// Patch an existing entry (mood / content / tags).
  Future<JournalRecord> update(String entryId, JournalInput patch);

  /// Permanently remove an entry.
  Future<void> remove(String entryId);
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
