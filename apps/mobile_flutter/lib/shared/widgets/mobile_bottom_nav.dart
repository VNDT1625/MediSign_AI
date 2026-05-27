import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

/// Bottom navigation 5 tab cho Mobile App.
///
/// Theo `UI_Mau/mobile/readme.md`:
///   navigator bar = Home - Chat AI - Tủ Thuốc - Soul - Hồ Sơ
///
/// Tab active có viền dưới (indicator) + chữ + icon brand.
/// Tab inactive: icon outline + chữ ink-500.
class MobileBottomNav extends StatelessWidget {
  const MobileBottomNav({
    super.key,
    required this.currentIndex,
    required this.onChanged,
  });

  final int currentIndex;
  final ValueChanged<int> onChanged;

  static const Color _brand = Color(0xFF0284C7);
  static const Color _ink500 = Color(0xFF64748B);
  static const Color _ink200 = Color(0xFFE2E8F0);

  static const List<_NavTab> _tabs = [
    _NavTab(
      label: 'Home',
      iconOutline: Icons.home_outlined,
      iconFilled: Icons.home_rounded,
    ),
    _NavTab(
      label: 'Chat',
      iconOutline: Icons.chat_bubble_outline_rounded,
      iconFilled: Icons.chat_bubble_rounded,
    ),
    _NavTab(
      label: 'Tủ thuốc',
      iconOutline: Icons.medical_services_outlined,
      iconFilled: Icons.medical_services_rounded,
    ),
    _NavTab(
      label: 'Soul Garden',
      iconOutline: Icons.spa_outlined,
      iconFilled: Icons.spa_rounded,
    ),
    _NavTab(
      label: 'Hồ sơ',
      iconOutline: Icons.person_outline_rounded,
      iconFilled: Icons.person_rounded,
    ),
  ];

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: const BoxDecoration(
        color: Colors.white,
        border: Border(
          top: BorderSide(color: _ink200, width: 1),
        ),
      ),
      child: SafeArea(
        top: false,
        child: SizedBox(
          height: 68,
          child: Row(
            children: List.generate(_tabs.length, (i) {
              final tab = _tabs[i];
              final selected = i == currentIndex;
              return Expanded(
                child: _NavItem(
                  tab: tab,
                  selected: selected,
                  onTap: () {
                    if (!selected) {
                      HapticFeedback.selectionClick();
                      onChanged(i);
                    }
                  },
                ),
              );
            }),
          ),
        ),
      ),
    );
  }
}

class _NavItem extends StatelessWidget {
  const _NavItem({
    required this.tab,
    required this.selected,
    required this.onTap,
  });

  final _NavTab tab;
  final bool selected;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final color = selected
        ? MobileBottomNav._brand
        : MobileBottomNav._ink500;

    return Semantics(
      label: tab.label,
      selected: selected,
      button: true,
      child: InkWell(
        onTap: onTap,
        child: Padding(
          padding: const EdgeInsets.symmetric(vertical: 8),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(
                selected ? tab.iconFilled : tab.iconOutline,
                size: 24,
                color: color,
              ),
              const SizedBox(height: 4),
              Text(
                tab.label,
                style: TextStyle(
                  fontSize: 11,
                  fontWeight:
                      selected ? FontWeight.w700 : FontWeight.w500,
                  color: color,
                  height: 1.1,
                ),
              ),
              const SizedBox(height: 4),
              // Indicator gạch dưới khi active
              AnimatedContainer(
                duration: const Duration(milliseconds: 200),
                height: 3,
                width: selected ? 28 : 0,
                decoration: BoxDecoration(
                  color: MobileBottomNav._brand,
                  borderRadius: BorderRadius.circular(2),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _NavTab {
  const _NavTab({
    required this.label,
    required this.iconOutline,
    required this.iconFilled,
  });

  final String label;
  final IconData iconOutline;
  final IconData iconFilled;
}
