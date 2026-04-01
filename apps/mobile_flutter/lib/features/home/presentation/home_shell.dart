import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import '../../../core/theme/glass_theme.dart';

import '../../../core/models/communication_mode.dart';
import '../../../core/models/consult_mode.dart';
import '../../../core/models/health_profile.dart';
import '../../../core/network/api_contracts.dart';
import '../../../core/services/emergency_service.dart';
import 'dashboard_page.dart';
import '../../achievements/presentation/achievements_page.dart';
import '../../community/presentation/screens/community_screen.dart';
import '../../doctor_hub/presentation/doctor_hub_page.dart';
import '../../soul_garden/presentation/soul_garden_page.dart';
import '../../profile/presentation/profile_page.dart';
import '../../settings/presentation/settings_page.dart';
import '../../medicine_cabinet/presentation/medicine_cabinet_page.dart';
import '../../medicine_scan/presentation/medicine_scan_page.dart';

/// Root shell with 4-tab bottom navigation:
///   0. Trang chủ  (Dashboard)
///   1. Vườn Tâm Hồn  (Soul Garden)
///   2. Cộng đồng  (Community)
///   3. Hồ sơ  (Profile)
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
  });

  final ConsultMode mode;
  final Set<CommunicationMethod> communicationMethods;
  final ConsultApi consultApi;
  final MedicineApi medicineApi;
  final VoidCallback onResetOnboarding;
  final VoidCallback onResetCommunication;
  final HealthProfile healthProfile;

  @override
  State<HomeShell> createState() => _HomeShellState();
}

class _HomeShellState extends State<HomeShell> {
  final EmergencyService _emergencyService = EmergencyService();
  int _selectedIndex = 0;

  void _openMedicineCabinet() {
    Navigator.of(context).push(GlassTheme.route(
      const MedicineCabinetPage(),
    ));
  }

  void _openMedicineScan() {
    Navigator.of(context).push(GlassTheme.route(
      MedicineScanPage(medicineApi: widget.medicineApi),
    ));
  }

  void _openDoctorHub() {
    Navigator.of(context).push(GlassTheme.route(
      DoctorHubPage(
        onNavigate: (route) {
          Navigator.of(context).pop();
          switch (route) {
            case 'soul_garden':
              setState(() => _selectedIndex = 1);
              break;
            case 'profile':
              setState(() => _selectedIndex = 3);
              break;
            case 'achievements':
              _openAchievements();
              break;
            case 'medicine':
              _openMedicineScan();
              break;
            default:
              break;
          }
        },
      ),
    ));
  }

  void _openAchievements() {
    Navigator.of(context).push(GlassTheme.route(
      AchievementsPage(
        onBack: () => Navigator.of(context).pop(),
      ),
    ));
  }

  void _openSettings() {
    Navigator.of(context).push(GlassTheme.route(
      SettingsPage(
        mode: widget.mode,
        communicationMethods: widget.communicationMethods,
        onResetOnboarding: widget.onResetOnboarding,
        onResetCommunication: widget.onResetCommunication,
      ),
    ));
  }

  @override
  Widget build(BuildContext context) {
    final pages = [
      DashboardPage(
        mode: widget.mode,
        consultApi: widget.consultApi,
        onOpenMedicine: _openMedicineScan,
        onOpenDoctorHub: _openDoctorHub,
        onOpenAchievements: _openAchievements,
        onOpenCommunity: () => setState(() => _selectedIndex = 2),
      ),
      const SoulGardenPage(),
      const CommunityScreen(),
      ProfilePage(
        healthProfile: widget.healthProfile,
        onOpenMedicineCabinet: _openMedicineCabinet,
        onOpenSettings: _openSettings,
      ),
    ];

    return Scaffold(
      body: IndexedStack(index: _selectedIndex, children: pages),
      floatingActionButton: FloatingActionButton(
        heroTag: 'emergency_btn',
        backgroundColor: GlassTheme.emergencyRed,
        onPressed: () => _emergencyService.triggerEmergency(context),
        child: const Icon(Icons.call, color: Colors.white),
      ),
      bottomNavigationBar: _buildGlassBottomNav(),
    );
  }

  Widget _buildGlassBottomNav() {
    const items = [
      _NavItem(Icons.home_outlined, Icons.home_rounded, 'Trang chủ'),
      _NavItem(Icons.park_outlined, Icons.park_rounded, 'Vườn Tâm Hồn'),
      _NavItem(Icons.people_outline, Icons.people_rounded, 'Cộng đồng'),
      _NavItem(Icons.person_outline, Icons.person_rounded, 'Hồ sơ'),
    ];

    return Container(
      decoration: BoxDecoration(
        color: GlassTheme.navBackground.withOpacity(0.92),
        border: const Border(
          top: BorderSide(color: GlassTheme.glassBorder, width: 0.5),
        ),
      ),
      child: SafeArea(
        top: false,
        child: SizedBox(
          height: 72,
          child: Row(
            children: items.asMap().entries.map((entry) {
              final i = entry.key;
              final item = entry.value;
              final isSelected = i == _selectedIndex;

              return Expanded(
                child: GestureDetector(
                  onTap: () {
                    HapticFeedback.selectionClick();
                    setState(() => _selectedIndex = i);
                  },
                  behavior: HitTestBehavior.opaque,
                  child: Semantics(
                    label: item.label,
                    selected: isSelected,
                    button: true,
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        AnimatedContainer(
                          duration: const Duration(milliseconds: 200),
                          padding: const EdgeInsets.symmetric(
                            horizontal: 16,
                            vertical: 6,
                          ),
                          decoration: BoxDecoration(
                            color: isSelected
                                ? GlassTheme.primaryGreen.withOpacity(0.15)
                                : Colors.transparent,
                            borderRadius: BorderRadius.circular(20),
                          ),
                          child: Icon(
                            isSelected ? item.activeIcon : item.icon,
                            size: 24,
                            color: isSelected
                                ? GlassTheme.primaryGreenLight
                                : GlassTheme.textDisabled,
                          ),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          item.label,
                          style: TextStyle(
                            fontFamily: GlassTheme.fontFamily,
                            fontSize: 11,
                            fontWeight:
                                isSelected ? FontWeight.w600 : FontWeight.w400,
                            color: isSelected
                                ? GlassTheme.primaryGreenLight
                                : GlassTheme.textDisabled,
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              );
            }).toList(),
          ),
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
