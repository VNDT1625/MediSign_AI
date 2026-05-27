import 'package:flutter/foundation.dart';

import 'voice_intents.dart';

/// Bus event giua HomeShell va cac trang con (ConsultPage, Dashboard...).
/// Cho phep voice intent xuyen qua cay widget ma khong dung global state.
class VoiceShellEvents extends ChangeNotifier {
  VoiceIntent? _last;
  double _textScale = 1.0;
  bool _elderly = false;
  int _seq = 0;

  VoiceIntent? get last => _last;
  int get seq => _seq;
  double get textScale => _textScale;
  bool get elderly => _elderly;

  void emit(VoiceIntent intent) {
    _last = intent;
    _seq++;
    notifyListeners();
  }

  void setTextScale(double v) {
    _textScale = v.clamp(0.85, 1.4);
    notifyListeners();
  }

  void toggleElderly() {
    _elderly = !_elderly;
    notifyListeners();
  }
}
