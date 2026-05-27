import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import '../../../core/theme/glass_theme.dart';

import '../../../core/models/communication_mode.dart';
import '../../../core/models/consult_mode.dart';
import '../../../core/models/health_profile.dart';
import '../../../core/network/api_contracts.dart';
import '../../../core/services/auth_service.dart';
import '../../../core/voice/voice_controller.dart';
import '../../../core/voice/voice_intents.dart';
import '../../../core/voice/voice_overlay.dart';
import '../../../core/voice/voice_shell_events.dart';
import '../../../core/voice/voice_shell_scope.dart';
import 'dashboard_page.dart';
import '../../consult/presentation/consult_page.dart';
import '../../soul_garden/presentation/soul_garden_page.dart';
import '../../profile/presentation/profile_page.dart';
import '../../settings/presentation/settings_page.dart';
import '../../medicine_cabinet/presentation/medicine_cabinet_page.dart';
import '../../medicine_scan/presentation/medicine_scan_page.dart';

const _kBrand = Color(0xFF0284C7);
const _kBg = Color(0xFFF8FAFC);
const _kBorder = Color(0xFFE2E8F0);
const _kInk = Color(0xFF0F172A);
const _kInkMuted = Color(0xFF94A3B8);

class HomeShell extends StatefulWidget {
  const HomeShell({
    super.key,
    required this.mode,
    required this.communicationMethods,
    required this.consultApi,
    required this.medicineApi,
    required this.onResetOnboarding,
    required this.onResetCommunication,
    required this.healthProfile,
    required this.authService,
    required this.onLoggedOut,
  });

  final ConsultMode mode;
  final Set<CommunicationMethod> communicationMethods;
  final ConsultApi consultApi;
  final MedicineApi medicineApi;
  final VoidCallback onResetOnboarding;
  final VoidCallback onResetCommunication;
  final HealthProfile healthProfile;
  final AuthService authService;
  final VoidCallback onLoggedOut;

  @override
  State<HomeShell> createState() => _HomeShellState();
}

class _HomeShellState extends State<HomeShell> {
  int _selectedIndex = 0;
  bool _voiceOverlayOpen = false;
  String _lastSpoken = '';

  late final VoiceShellEvents _events = VoiceShellEvents();
  late final VoiceController _voice = VoiceController(onIntent: _handleIntent);

  @override
  void dispose() {
    _voice.dispose();
    _events.dispose();
    super.dispose();
  }

  void _go(int index) {
    HapticFeedback.selectionClick();
    setState(() => _selectedIndex = index);
  }

  int _tabToIndex(HomeTab tab) {
    switch (tab) {
      case HomeTab.home:
        return 0;
      case HomeTab.chat:
        return 1;
      case HomeTab.medicine:
        return 2;
      case HomeTab.soulGarden:
        return 3;
      case HomeTab.profile:
        return 4;
    }
  }

  String _handleIntent(VoiceIntent intent) {
    setState(() => _voiceOverlayOpen = true);
    String reply = intent.reply;

    switch (intent.kind) {
      case VoiceIntentKind.navigateTab:
        if (intent.tab != null) _go(_tabToIndex(intent.tab!));
        break;
      case VoiceIntentKind.openScan:
        _openMedicineScan();
        break;
      case VoiceIntentKind.openSettings:
        _openSettings();
        break;
      case VoiceIntentKind.back:
        if (Navigator.of(context).canPop()) Navigator.of(context).pop();
        break;
      case VoiceIntentKind.fontSize:
        switch (intent.fontDir!) {
          case VoiceFontDir.increase:
            _events.setTextScale(_events.textScale + 0.1);
            break;
          case VoiceFontDir.decrease:
            _events.setTextScale(_events.textScale - 0.1);
            break;
          case VoiceFontDir.reset:
            _events.setTextScale(1.0);
            break;
        }
        break;
      case VoiceIntentKind.elderlyToggle:
        _events.toggleElderly();
        break;
      case VoiceIntentKind.authLogin:
      case VoiceIntentKind.authLogout:
      case VoiceIntentKind.chatMode:
      case VoiceIntentKind.uiSubmit:
      case VoiceIntentKind.uiDictate:
      case VoiceIntentKind.uiClear:
      case VoiceIntentKind.scroll:
        // Forward cho trang con (chat / dashboard) xu ly.
        _events.emit(intent);
        break;
      case VoiceIntentKind.readPage:
        _voice.say('Đây là trang ${_tabName(_selectedIndex)}.');
        break;
      case VoiceIntentKind.repeat:
        if (_lastSpoken.isNotEmpty) _voice.say(_lastSpoken);
        reply = _lastSpoken.isEmpty ? 'Chưa có nội dung để nhắc lại.' : '';
        break;
      case VoiceIntentKind.close:
        setState(() => _voiceOverlayOpen = false);
        break;
      case VoiceIntentKind.stop:
        _voice.stop();
        break;
      case VoiceIntentKind.help:
      case VoiceIntentKind.unknown:
        break;
    }

    if (reply.isNotEmpty) _lastSpoken = reply;
    return reply;
  }

  String _tabName(int i) {
    switch (i) {
      case 0:
        return 'trang chủ';
      case 1:
        return 'chat AI';
      case 2:
        return 'tủ thuốc';
      case 3:
        return 'Soul Garden';
      case 4:
        return 'hồ sơ';
      default:
        return 'ứng dụng';
    }
  }

  void _toggleVoice() {
    setState(() => _voiceOverlayOpen = !_voiceOverlayOpen);
    if (_voiceOverlayOpen && _voice.mode == VoiceMode.off) {
      _voice.start();
    }
  }

  void _hideVoiceOverlay() {
    setState(() => _voiceOverlayOpen = false);
  }

  void _closeVoiceOverlay() {
    setState(() => _voiceOverlayOpen = false);
    _voice.stop();
  }

  void _openMedicineScan() {
    Navigator.of(context).push(MaterialPageRoute(
      builder: (_) => MedicineScanPage(medicineApi: widget.medicineApi),
    ));
  }

  void _openSettings() {
    Navigator.of(context).push(MaterialPageRoute(
      builder: (_) => SettingsPage(
        mode: widget.mode,
        communicationMethods: widget.communicationMethods,
        onResetOnboarding: widget.onResetOnboarding,
        onResetCommunication: widget.onResetCommunication,
      ),
    ));
  }

  @override
  Widget build(BuildContext context) {
    final pages = <Widget>[
      DashboardPage(
        mode: widget.mode,
        consultApi: widget.consultApi,
        userName: 'Minh An',
        onOpenChat: () => _go(1),
        onOpenMedicineCabinet: () => _go(2),
        onOpenSoulGarden: () => _go(3),
        onOpenProfile: () => _go(4),
        onShowMenu: _openSettings,
        onMic: () => _go(1),
        onCamera: _openMedicineScan,
        onSeeReminders: () => _go(2),
        onSeeHealthSummary: () => _go(4),
        onSuggestionTap: (_) => _go(1),
      ),
      ConsultPage(mode: widget.mode, consultApi: widget.consultApi),
      const MedicineCabinetPage(),
      const SoulGardenPage(),
      ProfilePage(
        healthProfile: widget.healthProfile,
        authService: widget.authService,
        onOpenMedicineCabinet: () => _go(2),
        onOpenSoulGarden: () => _go(3),
        onOpenSettings: _openSettings,
        onLoggedOut: widget.onLoggedOut,
      ),
    ];

    return AnimatedBuilder(
      animation: _events,
      builder: (context, _) {
        final mediaQuery = MediaQuery.of(context);
        return MediaQuery(
          data: mediaQuery.copyWith(
            textScaler: TextScaler.linear(_events.textScale),
          ),
          child: VoiceShellScope(
            events: _events,
            child: Scaffold(
              backgroundColor: _kBg,
              body: AnimatedBuilder(
                animation: _voice,
                builder: (context, _) {
                  return Stack(
                    children: [
                      IndexedStack(index: _selectedIndex, children: pages),
                      if (_voiceOverlayOpen)
                        Positioned.fill(
                          child: Stack(
                            children: [
                              Positioned.fill(
                                child: GestureDetector(
                                  behavior: HitTestBehavior.translucent,
                                  onTap: _hideVoiceOverlay,
                                ),
                              ),
                              VoiceOverlay(
                                controller: _voice,
                                onClose: _closeVoiceOverlay,
                              ),
                            ],
                          ),
                        ),
                      Positioned(
                        right: 16,
                        bottom: 80,
                        child: VoiceFab(
                          active: _voice.mode != VoiceMode.off,
                          onTap: _toggleVoice,
                        ),
                      ),
                    ],
                  );
                },
              ),
              bottomNavigationBar: _LightBottomNav(
                selectedIndex: _selectedIndex,
                onTap: _go,
              ),
            ),
          ),
        );
      },
    );
  }
}

class _LightBottomNav extends StatelessWidget {
  const _LightBottomNav({
    required this.selectedIndex,
    required this.onTap,
  });

  final int selectedIndex;
  final ValueChanged<int> onTap;

  static const _items = <_NavItem>[
    _NavItem(Icons.home_outlined, Icons.home_rounded, 'Home'),
    _NavItem(
        Icons.chat_bubble_outline_rounded, Icons.chat_bubble_rounded, 'Chat'),
    _NavItem(Icons.medical_services_outlined, Icons.medical_services_rounded,
        'Tủ thuốc'),
    _NavItem(Icons.spa_outlined, Icons.spa_rounded, 'Soul Garden'),
    _NavItem(Icons.person_outline_rounded, Icons.person_rounded, 'Hồ sơ'),
  ];

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: const BoxDecoration(
        color: Colors.white,
        border: Border(top: BorderSide(color: _kBorder, width: 0.6)),
      ),
      child: SafeArea(
        top: false,
        child: SizedBox(
          height: 64,
          child: Row(
            children: List.generate(_items.length, (i) {
              final item = _items[i];
              final isSelected = i == selectedIndex;
              return Expanded(
                child: _NavTab(
                  item: item,
                  isSelected: isSelected,
                  onTap: () => onTap(i),
                ),
              );
            }),
          ),
        ),
      ),
    );
  }
}

class _NavTab extends StatelessWidget {
  const _NavTab({
    required this.item,
    required this.isSelected,
    required this.onTap,
  });

  final _NavItem item;
  final bool isSelected;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final color = isSelected ? _kBrand : _kInkMuted;
    return Semantics(
      label: item.label,
      selected: isSelected,
      button: true,
      child: InkResponse(
        onTap: onTap,
        radius: 36,
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            AnimatedContainer(
              duration: const Duration(milliseconds: 200),
              width: isSelected ? 18 : 0,
              height: 3,
              margin: const EdgeInsets.only(bottom: 6),
              decoration: BoxDecoration(
                color: _kBrand,
                borderRadius: BorderRadius.circular(2),
              ),
            ),
            Icon(
              isSelected ? item.activeIcon : item.icon,
              size: 22,
              color: color,
            ),
            const SizedBox(height: 4),
            Text(
              item.label,
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
              style: TextStyle(
                fontFamily: 'Outfit',
                fontSize: 10.5,
                fontWeight: isSelected ? FontWeight.w700 : FontWeight.w500,
                color: color,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _NavItem {
  final IconData icon;
  final IconData activeIcon;
  final String label;
  const _NavItem(this.icon, this.activeIcon, this.label);
}

// ignore: unused_element
const _kept = [_kInk, GlassTheme.fontFamily];
