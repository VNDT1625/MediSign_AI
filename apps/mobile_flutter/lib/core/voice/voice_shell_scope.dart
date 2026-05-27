import 'package:flutter/widgets.dart';

import 'voice_shell_events.dart';

/// InheritedWidget de cac trang con `of(context)` lay VoiceShellEvents
/// va tu lang nghe (qua AnimatedBuilder hoac addListener).
class VoiceShellScope extends InheritedNotifier<VoiceShellEvents> {
  const VoiceShellScope({
    super.key,
    required VoiceShellEvents events,
    required super.child,
  }) : super(notifier: events);

  static VoiceShellEvents? maybeOf(BuildContext context) {
    final scope = context.dependOnInheritedWidgetOfExactType<VoiceShellScope>();
    return scope?.notifier;
  }

  static VoiceShellEvents of(BuildContext context) {
    final events = maybeOf(context);
    assert(events != null, 'VoiceShellScope.of() called outside of HomeShell');
    return events!;
  }
}
