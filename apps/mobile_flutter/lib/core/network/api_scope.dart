import 'package:flutter/widgets.dart';

import 'api_contracts.dart';

/// Inherited scope that exposes the production [CabinetApi] / [JournalApi]
/// to any descendant widget without threading them through every page
/// constructor.
///
/// Usage:
/// ```dart
/// final api = ApiScope.of(context).cabinet;
/// final items = await api.list();
/// ```
///
/// Mounted near the root of the widget tree (in `app.dart`) right after
/// authentication completes. When the user logs out, the parent should
/// dispose this scope so descendants stop receiving the cabinet API.
class ApiScope extends InheritedWidget {
  const ApiScope({
    super.key,
    required this.cabinet,
    required this.journal,
    required super.child,
  });

  /// Personal medicine cabinet client (`/medicine/cabinet/*`).
  final CabinetApi cabinet;

  /// Soul Garden journal client (`/journal/*`).
  final JournalApi journal;

  /// Look up the nearest [ApiScope]. Throws when no scope is mounted —
  /// pages that genuinely require auth-backed data should never be rendered
  /// outside one. Wrap with a try/catch or use [maybeOf] for opt-in usage.
  static ApiScope of(BuildContext context) {
    final scope = context.dependOnInheritedWidgetOfExactType<ApiScope>();
    assert(
      scope != null,
      'ApiScope.of() called with a context that does not contain an ApiScope. '
      'Wrap your widget tree in `ApiScope(...)` (typically inside app.dart).',
    );
    return scope!;
  }

  /// Returns the nearest [ApiScope], or `null` when the caller is rendered
  /// outside one (e.g. in legacy mock-only flows).
  static ApiScope? maybeOf(BuildContext context) {
    return context.dependOnInheritedWidgetOfExactType<ApiScope>();
  }

  @override
  bool updateShouldNotify(ApiScope oldWidget) {
    return cabinet != oldWidget.cabinet || journal != oldWidget.journal;
  }
}
