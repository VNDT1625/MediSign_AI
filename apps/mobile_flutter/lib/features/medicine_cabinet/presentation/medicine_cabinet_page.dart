import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:medisign_mobile/core/network/api_scope.dart';
import 'package:medisign_mobile/core/network/api_models.dart';

// ── Light theme tokens (đồng bộ với dashboard_page.dart) ──
const _kBrand = Color(0xFF0284C7);
const _kBrandLight = Color(0xFF38BDF8);
const _kBrandSoft = Color(0xFFE0F2FE);
const _kBrandSofter = Color(0xFFF0F9FF);
const _kBg = Color(0xFFF8FAFC);
const _kBorder = Color(0xFFE2E8F0);
const _kInk = Color(0xFF0F172A);
const _kInkSoft = Color(0xFF475569);
const _kInkMuted = Color(0xFF94A3B8);
const _kSuccess = Color(0xFF10B981);
const _kWarn = Color(0xFFF59E0B);
const _kWarnSoft = Color(0xFFFEF3C7);

enum _CabinetTab { today, ongoing, prescription }

/// Tủ thuốc — light theme, layout đúng screenshot.
class MedicineCabinetPage extends StatefulWidget {
  const MedicineCabinetPage({super.key});

  @override
  State<MedicineCabinetPage> createState() => _MedicineCabinetPageState();
}

class _MedicineCabinetPageState extends State<MedicineCabinetPage> {
  _CabinetTab _tab = _CabinetTab.today;
  List<CabinetItem> _items = [];
  bool _isLoading = false;
  String? _error;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _loadItems();
    });
  }

  Future<void> _loadItems() async {
    if (!mounted) return;
    setState(() {
      _isLoading = true;
      _error = null;
    });
    try {
      final api = ApiScope.of(context).cabinet;
      final list = await api.list();
      if (!mounted) return;
      setState(() {
        _items = list;
        _isLoading = false;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _error = e.toString();
        _isLoading = false;
      });
    }
  }

  Future<void> _addCabinetItem(CabinetItemInput input) async {
    try {
      final api = ApiScope.of(context).cabinet;
      await api.add(input);
      _loadItems();
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Đã thêm thuốc mới vào tủ thuốc thành công!'),
          backgroundColor: _kSuccess,
        ),
      );
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Lỗi khi thêm thuốc: $e')),
      );
    }
  }

  Future<void> _deleteCabinetItem(String itemId) async {
    try {
      final api = ApiScope.of(context).cabinet;
      await api.remove(itemId);
      _loadItems();
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Đã xóa thuốc khỏi tủ thuốc!'),
          backgroundColor: Colors.redAccent,
        ),
      );
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Lỗi khi xóa thuốc: $e')),
      );
    }
  }

  Future<void> _toggleItemActive(CabinetItem item) async {
    try {
      final api = ApiScope.of(context).cabinet;
      final updatedInput = CabinetItemInput(
        isActive: !item.isActive,
      );
      await api.update(item.id, updatedInput);
      _loadItems();
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(item.isActive ? 'Đã tạm ngưng sử dụng thuốc!' : 'Đã kích hoạt lại thuốc!'),
          backgroundColor: _kBrand,
        ),
      );
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Lỗi khi cập nhật trạng thái thuốc: $e')),
      );
    }
  }

  Future<void> _recordDose(String itemId) async {
    try {
      final api = ApiScope.of(context).cabinet;
      await api.recordDose(itemId);
      _loadItems();
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Đã ghi nhận liều dùng thành công! Số lượng thuốc đã được cập nhật.'),
          backgroundColor: _kSuccess,
        ),
      );
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Lỗi khi ghi nhận liều dùng: $e')),
      );
    }
  }

  void _showAddMedicineSheet() {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) => _AddMedicineSheet(
        onAdd: (input) {
          _addCabinetItem(input);
        },
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final activeMeds = _items.where((i) => i.isActive).toList();
    final runningOutMeds = activeMeds.where((i) => i.remainingPills != null && i.remainingPills! <= 5).toList();
    final inactiveMeds = _items.where((i) => !i.isActive).toList();

    return Scaffold(
      backgroundColor: _kBg,
      floatingActionButton: _AddFab(onTap: _showAddMedicineSheet),
      body: SafeArea(
        bottom: false,
        child: Column(
          children: [
            const _CabinetHeader(),
            Expanded(
              child: ListView(
                padding: const EdgeInsets.fromLTRB(16, 4, 16, 96),
                physics: const BouncingScrollPhysics(),
                children: [
                  const _PageTitle(),
                  const SizedBox(height: 12),
                  _SummaryHero(
                    activeCount: activeMeds.length,
                    nextDoseName: activeMeds.isNotEmpty ? activeMeds.first.name : null,
                  ),
                  const SizedBox(height: 14),
                  _TabSwitcher(
                    selected: _tab,
                    onChanged: (t) => setState(() => _tab = t),
                  ),
                  const SizedBox(height: 12),
                  if (_isLoading)
                    const Padding(
                      padding: EdgeInsets.symmetric(vertical: 40),
                      child: Center(
                        child: CircularProgressIndicator(color: _kBrand),
                      ),
                    )
                  else if (_error != null)
                    Padding(
                      padding: const EdgeInsets.symmetric(vertical: 24),
                      child: Container(
                        padding: const EdgeInsets.all(16),
                        decoration: BoxDecoration(
                          color: const Color(0xFFFEF2F2),
                          borderRadius: BorderRadius.circular(16),
                          border: Border.all(color: const Color(0xFFFCA5A5)),
                        ),
                        child: Column(
                          children: [
                            const Icon(Icons.error_outline_rounded, color: Colors.redAccent, size: 32),
                            const SizedBox(height: 8),
                            Text(
                              'Đã xảy ra lỗi khi tải tủ thuốc: $_error',
                              textAlign: TextAlign.center,
                              style: const TextStyle(fontFamily: 'Outfit', color: _kInk),
                            ),
                            const SizedBox(height: 12),
                            ElevatedButton.icon(
                              onPressed: _loadItems,
                              icon: const Icon(Icons.refresh_rounded, color: Colors.white, size: 16),
                              label: const Text('Thử lại', style: TextStyle(fontFamily: 'Outfit', color: Colors.white)),
                              style: ElevatedButton.styleFrom(
                                backgroundColor: _kBrand,
                                shape: RoundedRectangleBorder(
                                  borderRadius: BorderRadius.circular(8),
                                ),
                              ),
                            ),
                          ],
                        ),
                      ),
                    )
                  else if (_items.isEmpty)
                    Padding(
                      padding: const EdgeInsets.symmetric(vertical: 32),
                      child: Container(
                        padding: const EdgeInsets.all(24),
                        decoration: BoxDecoration(
                          color: Colors.white,
                          borderRadius: BorderRadius.circular(20),
                          border: Border.all(color: _kBorder),
                        ),
                        child: Column(
                          children: [
                            Container(
                              width: 64,
                              height: 64,
                              decoration: const BoxDecoration(
                                color: _kBrandSofter,
                                shape: BoxShape.circle,
                              ),
                              child: const Icon(Icons.medical_services_outlined, color: _kBrand, size: 32),
                            ),
                            const SizedBox(height: 16),
                            const Text(
                              'Tủ thuốc trống',
                              style: TextStyle(
                                fontFamily: 'Outfit',
                                fontSize: 18,
                                fontWeight: FontWeight.w800,
                                color: _kInk,
                              ),
                            ),
                            const SizedBox(height: 8),
                            const Text(
                              'Hãy thêm các loại thuốc bạn đang sử dụng để MediSign AI hỗ trợ nhắc lịch và quản lý nhé!',
                              textAlign: TextAlign.center,
                              style: TextStyle(
                                fontFamily: 'Outfit',
                                fontSize: 13,
                                color: _kInkSoft,
                              ),
                            ),
                            const SizedBox(height: 16),
                            ElevatedButton.icon(
                              onPressed: _showAddMedicineSheet,
                              icon: const Icon(Icons.add_rounded, color: Colors.white, size: 18),
                              label: const Text('Thêm thuốc ngay', style: TextStyle(fontFamily: 'Outfit', color: Colors.white, fontWeight: FontWeight.bold)),
                              style: ElevatedButton.styleFrom(
                                backgroundColor: _kBrand,
                                shape: RoundedRectangleBorder(
                                  borderRadius: BorderRadius.circular(12),
                                ),
                                padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
                              ),
                            ),
                          ],
                        ),
                      ),
                    )
                  else ...[
                    // Tab today
                    if (_tab == _CabinetTab.today) ...[
                      if (activeMeds.isNotEmpty) ...[
                        _NextDoseCard(
                          item: activeMeds.first,
                          onTake: () => _recordDose(activeMeds.first.id),
                        ),
                        const SizedBox(height: 12),
                        _OngoingCard(
                          items: activeMeds,
                          onDelete: _deleteCabinetItem,
                          onToggleActive: _toggleItemActive,
                        ),
                      ] else
                        Padding(
                          padding: const EdgeInsets.symmetric(vertical: 20),
                          child: Container(
                            padding: const EdgeInsets.all(16),
                            decoration: BoxDecoration(
                              color: Colors.white,
                              borderRadius: BorderRadius.circular(16),
                              border: Border.all(color: _kBorder),
                            ),
                            child: const Center(
                              child: Text(
                                'Không có thuốc nào cần uống hôm nay',
                                style: TextStyle(
                                  fontFamily: 'Outfit',
                                  fontSize: 13.5,
                                  color: _kInkSoft,
                                ),
                              ),
                            ),
                          ),
                        ),
                      if (runningOutMeds.isNotEmpty) ...[
                        const SizedBox(height: 12),
                        _RunningOutCard(item: runningOutMeds.first),
                      ],
                      const SizedBox(height: 12),
                      Row(
                        children: const [
                          Expanded(child: _RecentPrescriptionsCard()),
                          SizedBox(width: 10),
                          Expanded(child: _FamilyCabinetCard()),
                        ],
                      ),
                    ],

                    // Tab ongoing
                    if (_tab == _CabinetTab.ongoing) ...[
                      _OngoingCard(
                        items: activeMeds,
                        onDelete: _deleteCabinetItem,
                        onToggleActive: _toggleItemActive,
                      ),
                      if (runningOutMeds.isNotEmpty) ...[
                        const SizedBox(height: 12),
                        ...runningOutMeds.map((med) => Padding(
                          padding: const EdgeInsets.only(bottom: 12.0),
                          child: _RunningOutCard(item: med),
                        )),
                      ],
                      const SizedBox(height: 12),
                      Row(
                        children: const [
                          Expanded(child: _RecentPrescriptionsCard()),
                          SizedBox(width: 10),
                          Expanded(child: _FamilyCabinetCard()),
                        ],
                      ),
                    ],

                    // Tab prescription
                    if (_tab == _CabinetTab.prescription) ...[
                      Row(
                        children: const [
                          Expanded(child: _RecentPrescriptionsCard()),
                          SizedBox(width: 10),
                          Expanded(child: _FamilyCabinetCard()),
                        ],
                      ),
                      if (inactiveMeds.isNotEmpty) ...[
                        const SizedBox(height: 16),
                        const Padding(
                          padding: EdgeInsets.symmetric(horizontal: 4),
                          child: Text(
                            'Lịch sử thuốc đã dùng',
                            style: TextStyle(
                              fontFamily: 'Outfit',
                              fontSize: 15,
                              fontWeight: FontWeight.w700,
                              color: _kInk,
                            ),
                          ),
                        ),
                        const SizedBox(height: 8),
                        _OngoingCard(
                          items: inactiveMeds,
                          onDelete: _deleteCabinetItem,
                          onToggleActive: _toggleItemActive,
                        ),
                      ],
                    ],
                  ],
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

// ───────────────────────── HEADER ─────────────────────────

class _CabinetHeader extends StatelessWidget {
  const _CabinetHeader();

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(8, 4, 8, 4),
      child: Row(
        children: [
          _SquareIconBtn(icon: Icons.menu_rounded, onTap: () {}),
          const SizedBox(width: 6),
          _ShieldLogo(),
          const SizedBox(width: 8),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'MediSign AI',
                  style: TextStyle(
                    fontFamily: 'Outfit',
                    fontSize: 18,
                    fontWeight: FontWeight.w800,
                    color: _kInk,
                    height: 1.1,
                  ),
                ),
                const SizedBox(height: 2),
                Row(
                  children: const [
                    _Dot(color: _kSuccess),
                    SizedBox(width: 6),
                    Text(
                      'Chăm sóc sức khỏe mỗi ngày',
                      style: TextStyle(
                        fontFamily: 'Outfit',
                        fontSize: 11,
                        color: _kInkSoft,
                        height: 1.1,
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
          _CircleIconBtn(icon: Icons.notifications_outlined, badge: true),
          const SizedBox(width: 6),
          _CircleIconBtn(
              icon: Icons.person_outline_rounded, fill: _kBrandSofter),
        ],
      ),
    );
  }
}

class _ShieldLogo extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Container(
      width: 32,
      height: 32,
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [_kBrand, _kBrandLight],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(8),
        boxShadow: [
          BoxShadow(
            color: _kBrand.withOpacity(0.25),
            blurRadius: 6,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: const Icon(Icons.medical_services_rounded,
          color: Colors.white, size: 18),
    );
  }
}

class _SquareIconBtn extends StatelessWidget {
  const _SquareIconBtn({required this.icon, required this.onTap});
  final IconData icon;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return InkResponse(
      onTap: () {
        HapticFeedback.selectionClick();
        onTap();
      },
      radius: 24,
      child: SizedBox(
        width: 40,
        height: 40,
        child: Icon(icon, size: 20, color: _kInkSoft),
      ),
    );
  }
}

class _CircleIconBtn extends StatelessWidget {
  const _CircleIconBtn({
    required this.icon,
    this.badge = false,
    this.fill = Colors.white,
  });
  final IconData icon;
  final bool badge;
  final Color fill;

  @override
  Widget build(BuildContext context) {
    return InkResponse(
      onTap: () {},
      radius: 24,
      child: Container(
        width: 40,
        height: 40,
        decoration: BoxDecoration(
          color: fill,
          shape: BoxShape.circle,
          border: Border.all(color: _kBorder),
        ),
        child: Stack(
          alignment: Alignment.center,
          children: [
            Icon(icon, size: 19, color: _kInkSoft),
            if (badge)
              Positioned(
                top: 8,
                right: 10,
                child: Container(
                  width: 8,
                  height: 8,
                  decoration: BoxDecoration(
                    color: const Color(0xFFEF4444),
                    shape: BoxShape.circle,
                    border: Border.all(color: Colors.white, width: 1.5),
                  ),
                ),
              ),
          ],
        ),
      ),
    );
  }
}

class _Dot extends StatelessWidget {
  const _Dot({required this.color});
  final Color color;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 6,
      height: 6,
      decoration: BoxDecoration(color: color, shape: BoxShape.circle),
    );
  }
}

// ───────────────────────── PAGE TITLE ─────────────────────────

class _PageTitle extends StatelessWidget {
  const _PageTitle();

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 4),
      child: Row(
        children: [
          Container(
            width: 44,
            height: 44,
            decoration: BoxDecoration(
              color: _kBrandSofter,
              borderRadius: BorderRadius.circular(12),
            ),
            child: const Icon(Icons.medication_outlined,
                size: 24, color: _kBrand),
          ),
          const SizedBox(width: 10),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: const [
              Text(
                'Tủ thuốc',
                style: TextStyle(
                  fontFamily: 'Outfit',
                  fontSize: 22,
                  fontWeight: FontWeight.w800,
                  color: _kInk,
                  height: 1.1,
                ),
              ),
              SizedBox(height: 2),
              Text(
                'Quản lý thuốc thông minh',
                style: TextStyle(
                  fontFamily: 'Outfit',
                  fontSize: 12.5,
                  color: _kInkSoft,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}

// ───────────────────────── SUMMARY HERO ─────────────────────────

class _SummaryHero extends StatelessWidget {
  const _SummaryHero({required this.activeCount, this.nextDoseName});
  final int activeCount;
  final String? nextDoseName;

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [Color(0xFFE0F2FE), Color(0xFFDBEAFE)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: Colors.white, width: 1.5),
      ),
      padding: const EdgeInsets.fromLTRB(14, 12, 14, 14),
      child: Stack(
        clipBehavior: Clip.none,
        children: [
          // Pill bottle illustration bên phải
          Positioned(
            right: -8,
            top: -4,
            bottom: -8,
            child: _PillBottlePlaceholder(),
          ),
          Padding(
            padding: const EdgeInsets.only(right: 110),
            child: Row(
              children: [
                Expanded(child: _SummaryStat(
                  icon: Icons.calendar_today_outlined,
                  label: 'Hôm nay',
                  bigValue: activeCount.toString(),
                  bigSuffix: 'loại thuốc\ncần uống',
                )),
                Container(
                  width: 1,
                  height: 56,
                  color: Colors.white.withOpacity(0.6),
                ),
                const SizedBox(width: 10),
                Expanded(child: _SummaryStat(
                  icon: Icons.access_time_rounded,
                  label: 'Uống tiếp theo',
                  bigValue: nextDoseName != null ? '10:00' : '--:--',
                  bigSuffix: nextDoseName != null ? nextDoseName! : 'Chưa có lịch',
                  alignTop: true,
                )),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _SummaryStat extends StatelessWidget {
  const _SummaryStat({
    required this.icon,
    required this.label,
    required this.bigValue,
    required this.bigSuffix,
    this.alignTop = false,
  });

  final IconData icon;
  final String label;
  final String bigValue;
  final String bigSuffix;
  final bool alignTop;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Icon(icon, size: 13, color: _kBrand),
            const SizedBox(width: 6),
            Text(
              label,
              style: const TextStyle(
                fontFamily: 'Outfit',
                fontSize: 12,
                fontWeight: FontWeight.w700,
                color: _kInk,
              ),
            ),
          ],
        ),
        const SizedBox(height: 8),
        Row(
          crossAxisAlignment: alignTop
              ? CrossAxisAlignment.start
              : CrossAxisAlignment.end,
          children: [
            Text(
              bigValue,
              style: const TextStyle(
                fontFamily: 'Outfit',
                fontSize: 28,
                fontWeight: FontWeight.w800,
                color: _kInk,
                height: 1.0,
              ),
            ),
            const SizedBox(width: 6),
            Flexible(
              child: Text(
                bigSuffix,
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
                style: const TextStyle(
                  fontFamily: 'Outfit',
                  fontSize: 11.5,
                  color: _kInkSoft,
                  height: 1.2,
                ),
              ),
            ),
          ],
        ),
      ],
    );
  }
}

class _PillBottlePlaceholder extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Container(
      width: 130,
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [_kBrandSoft, _kBrandLight.withOpacity(0.45)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: const BorderRadius.only(
          topRight: Radius.circular(18),
          bottomRight: Radius.circular(18),
          topLeft: Radius.circular(60),
          bottomLeft: Radius.circular(60),
        ),
      ),
      child: const Center(
        child: Icon(
          Icons.medication_liquid_rounded,
          color: Colors.white,
          size: 48,
        ),
      ),
    );
  }
}

// ───────────────────────── TAB SWITCHER ─────────────────────────

class _TabSwitcher extends StatelessWidget {
  const _TabSwitcher({required this.selected, required this.onChanged});
  final _CabinetTab selected;
  final ValueChanged<_CabinetTab> onChanged;

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Expanded(
          child: _TabBtn(
            label: 'Hôm nay',
            active: selected == _CabinetTab.today,
            onTap: () => onChanged(_CabinetTab.today),
          ),
        ),
        const SizedBox(width: 8),
        Expanded(
          child: _TabBtn(
            label: 'Đang dùng',
            active: selected == _CabinetTab.ongoing,
            onTap: () => onChanged(_CabinetTab.ongoing),
          ),
        ),
        const SizedBox(width: 8),
        Expanded(
          child: _TabBtn(
            label: 'Đơn thuốc',
            active: selected == _CabinetTab.prescription,
            onTap: () => onChanged(_CabinetTab.prescription),
          ),
        ),
      ],
    );
  }
}

class _TabBtn extends StatelessWidget {
  const _TabBtn({
    required this.label,
    required this.active,
    required this.onTap,
  });
  final String label;
  final bool active;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Material(
      color: active ? _kBrand : Colors.white,
      borderRadius: BorderRadius.circular(999),
      child: InkWell(
        onTap: () {
          HapticFeedback.selectionClick();
          onTap();
        },
        borderRadius: BorderRadius.circular(999),
        child: Container(
          padding: const EdgeInsets.symmetric(vertical: 10),
          decoration: BoxDecoration(
            border: Border.all(color: active ? _kBrand : _kBorder),
            borderRadius: BorderRadius.circular(999),
            boxShadow: active
                ? [
                    BoxShadow(
                      color: _kBrand.withOpacity(0.25),
                      blurRadius: 8,
                      offset: const Offset(0, 3),
                    ),
                  ]
                : null,
          ),
          alignment: Alignment.center,
          child: Text(
            label,
            style: TextStyle(
              fontFamily: 'Outfit',
              fontSize: 13,
              fontWeight: FontWeight.w700,
              color: active ? Colors.white : _kInkSoft,
            ),
          ),
        ),
      ),
    );
  }
}

// ───────────────────────── NEXT DOSE CARD ─────────────────────────

class _NextDoseCard extends StatelessWidget {
  const _NextDoseCard({required this.item, required this.onTake});
  final CabinetItem item;
  final VoidCallback onTake;

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(18),
        border: Border.all(color: _kBorder),
      ),
      padding: const EdgeInsets.fromLTRB(14, 12, 14, 14),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                width: 26,
                height: 26,
                decoration: BoxDecoration(
                  color: _kBrandSofter,
                  borderRadius: BorderRadius.circular(8),
                ),
                child: const Icon(Icons.access_time_rounded,
                    size: 15, color: _kBrand),
              ),
              const SizedBox(width: 8),
              const Text(
                'Uống tiếp theo',
                style: TextStyle(
                  fontFamily: 'Outfit',
                  fontSize: 13.5,
                  fontWeight: FontWeight.w700,
                  color: _kInk,
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Row(
            children: [
              const _PillThumbnail(),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Expanded(
                          child: Text(
                            item.name,
                            style: const TextStyle(
                              fontFamily: 'Outfit',
                              fontSize: 14.5,
                              fontWeight: FontWeight.w700,
                              color: _kInk,
                              height: 1.2,
                            ),
                          ),
                        ),
                        _PillTag(label: item.dosage ?? '1 viên'),
                      ],
                    ),
                    const SizedBox(height: 4),
                    Text(
                      item.doctorNotes ?? item.guidance ?? 'Hỗ trợ sức khỏe mỗi ngày',
                      style: const TextStyle(
                        fontFamily: 'Outfit',
                        fontSize: 12,
                        color: _kInkSoft,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Row(
                      children: [
                        _ChipMini(label: item.dosage ?? '1 viên'),
                        const SizedBox(width: 6),
                        if (item.remainingPills != null)
                          _ChipMini(label: 'Còn ${item.remainingPills} viên')
                        else
                          const _ChipMini(label: 'Không giới hạn'),
                      ],
                    ),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          SizedBox(
            width: double.infinity,
            child: Material(
              color: _kBrand,
              borderRadius: BorderRadius.circular(12),
              child: InkWell(
                onTap: () {
                  HapticFeedback.lightImpact();
                  onTake();
                },
                borderRadius: BorderRadius.circular(12),
                child: Padding(
                  padding: const EdgeInsets.symmetric(vertical: 11),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: const [
                      Icon(Icons.check_circle_outline_rounded,
                          size: 16, color: Colors.white),
                      SizedBox(width: 6),
                      Text(
                        'Đánh dấu đã uống',
                        style: TextStyle(
                          fontFamily: 'Outfit',
                          fontSize: 13.5,
                          fontWeight: FontWeight.w700,
                          color: Colors.white,
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _PillThumbnail extends StatelessWidget {
  const _PillThumbnail();
  @override
  Widget build(BuildContext context) {
    return Container(
      width: 56,
      height: 56,
      decoration: BoxDecoration(
        color: _kBrandSofter,
        borderRadius: BorderRadius.circular(14),
      ),
      child: const Icon(Icons.medication_rounded,
          size: 28, color: _kBrand),
    );
  }
}

class _PillTag extends StatelessWidget {
  const _PillTag({required this.label});
  final String label;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(
        color: _kBrandSofter,
        borderRadius: BorderRadius.circular(999),
      ),
      child: Text(
        label,
        style: const TextStyle(
          fontFamily: 'Outfit',
          fontSize: 11.5,
          fontWeight: FontWeight.w700,
          color: _kBrand,
        ),
      ),
    );
  }
}

class _ChipMini extends StatelessWidget {
  const _ChipMini({required this.label});
  final String label;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
      decoration: BoxDecoration(
        color: _kBrandSofter,
        borderRadius: BorderRadius.circular(999),
      ),
      child: Text(
        label,
        style: const TextStyle(
          fontFamily: 'Outfit',
          fontSize: 10.5,
          fontWeight: FontWeight.w600,
          color: _kBrand,
        ),
      ),
    );
  }
}

// ───────────────────────── ONGOING CARD ─────────────────────────

class _OngoingCard extends StatelessWidget {
  const _OngoingCard({
    required this.items,
    required this.onDelete,
    required this.onToggleActive,
  });

  final List<CabinetItem> items;
  final ValueChanged<String> onDelete;
  final ValueChanged<CabinetItem> onToggleActive;

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(18),
        border: Border.all(color: _kBorder),
      ),
      padding: const EdgeInsets.fromLTRB(14, 12, 14, 12),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                width: 26,
                height: 26,
                decoration: BoxDecoration(
                  color: _kBrandSofter,
                  borderRadius: BorderRadius.circular(8),
                ),
                child: const Icon(Icons.medical_services_outlined,
                    size: 15, color: _kBrand),
              ),
              const SizedBox(width: 8),
              const Expanded(
                child: Text(
                  'Thuốc đang dùng',
                  style: TextStyle(
                    fontFamily: 'Outfit',
                    fontSize: 13.5,
                    fontWeight: FontWeight.w700,
                    color: _kInk,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          if (items.isEmpty)
            const Padding(
              padding: EdgeInsets.symmetric(vertical: 20),
              child: Center(
                child: Text(
                  'Chưa có thuốc trong tủ',
                  style: TextStyle(
                    fontFamily: 'Outfit',
                    fontSize: 13.5,
                    color: _kInkSoft,
                  ),
                ),
              ),
            )
          else
            SingleChildScrollView(
              scrollDirection: Axis.horizontal,
              physics: const BouncingScrollPhysics(),
              child: Row(
                children: items.map((item) {
                  final idx = items.indexOf(item);
                  final colors = [
                    [const Color(0xFF3B82F6), const Color(0xFFDBEAFE)],
                    [const Color(0xFF10B981), const Color(0xFFD1FAE5)],
                    [const Color(0xFFF97316), const Color(0xFFFFEDD5)],
                    [const Color(0xFF8B5CF6), const Color(0xFFEDE9FE)],
                  ];
                  final pair = colors[idx % colors.length];

                  return Padding(
                    padding: const EdgeInsets.only(right: 8.0),
                    child: SizedBox(
                      width: 150,
                      child: _OngoingItem(
                        item: item,
                        iconColor: pair[0],
                        iconBg: pair[1],
                        onTap: () => _showMedicineActionsDialog(context, item),
                      ),
                    ),
                  );
                }).toList(),
              ),
            ),
        ],
      ),
    );
  }

  void _showMedicineActionsDialog(BuildContext context, CabinetItem item) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(
          item.name,
          style: const TextStyle(fontFamily: 'Outfit', fontWeight: FontWeight.w800, color: _kInk),
        ),
        content: Text(
          'Bạn muốn thực hiện thao tác nào với thuốc này?',
          style: const TextStyle(fontFamily: 'Outfit', color: _kInkSoft),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Hủy', style: TextStyle(fontFamily: 'Outfit', color: _kInkSoft)),
          ),
          TextButton(
            onPressed: () {
              Navigator.pop(context);
              onToggleActive(item);
            },
            child: Text(
              item.isActive ? 'Tạm ngưng sử dụng' : 'Kích hoạt lại',
              style: const TextStyle(fontFamily: 'Outfit', color: _kWarn),
            ),
          ),
          TextButton(
            onPressed: () {
              Navigator.pop(context);
              onDelete(item.id);
            },
            child: const Text(
              'Xóa vĩnh viễn',
              style: TextStyle(fontFamily: 'Outfit', color: Colors.redAccent, fontWeight: FontWeight.w700),
            ),
          ),
        ],
      ),
    );
  }
}

class _OngoingItem extends StatelessWidget {
  const _OngoingItem({
    required this.item,
    required this.iconColor,
    required this.iconBg,
    required this.onTap,
  });

  final CabinetItem item;
  final Color iconColor;
  final Color iconBg;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: const Color(0xFFFAFAFA),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: _kBorder.withOpacity(0.5)),
      ),
      child: Material(
        color: Colors.transparent,
        borderRadius: BorderRadius.circular(12),
        child: InkWell(
          onTap: onTap,
          borderRadius: BorderRadius.circular(12),
          child: Padding(
            padding: const EdgeInsets.all(8),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Container(
                      width: 32,
                      height: 32,
                      decoration: BoxDecoration(
                        color: iconBg,
                        shape: BoxShape.circle,
                      ),
                      child: Icon(Icons.medication_rounded,
                          size: 18, color: iconColor),
                    ),
                    const SizedBox(width: 6),
                    Expanded(
                      child: Column(
                        mainAxisSize: MainAxisSize.min,
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            item.name,
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                            style: const TextStyle(
                              fontFamily: 'Outfit',
                              fontSize: 11.5,
                              fontWeight: FontWeight.w700,
                              color: _kInk,
                              height: 1.2,
                            ),
                          ),
                          const SizedBox(height: 1),
                          Text(
                            item.doctorNotes ?? item.guidance ?? 'Hỗ trợ sức khỏe',
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                            style: const TextStyle(
                              fontFamily: 'Outfit',
                              fontSize: 10,
                              color: _kInkSoft,
                              height: 1.2,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                Text(
                  item.dosage ?? '1 viên/ngày',
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                  style: const TextStyle(
                    fontFamily: 'Outfit',
                    fontSize: 10.5,
                    color: _kInk,
                  ),
                ),
                const SizedBox(height: 4),
                Row(
                  children: [
                    const Text(
                      'Còn ',
                      style: TextStyle(
                        fontFamily: 'Outfit',
                        fontSize: 10.5,
                        color: _kInkSoft,
                      ),
                    ),
                    Text(
                      item.remainingPills != null ? item.remainingPills.toString() : '∞',
                      style: const TextStyle(
                        fontFamily: 'Outfit',
                        fontSize: 12,
                        fontWeight: FontWeight.w800,
                        color: _kInk,
                      ),
                    ),
                    const Text(
                      ' viên',
                      style: TextStyle(
                        fontFamily: 'Outfit',
                        fontSize: 10.5,
                        color: _kInkSoft,
                      ),
                    ),
                    const Spacer(),
                    const Icon(Icons.chevron_right_rounded,
                        size: 14, color: _kInkMuted),
                  ],
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

// ───────────────────────── RUNNING OUT CARD ─────────────────────────

class _RunningOutCard extends StatelessWidget {
  const _RunningOutCard({required this.item});
  final CabinetItem item;

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: _kWarnSoft,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: _kWarn.withOpacity(0.3)),
      ),
      padding: const EdgeInsets.fromLTRB(12, 10, 10, 10),
      child: Row(
        children: [
          Container(
            width: 30,
            height: 30,
            decoration: BoxDecoration(
              color: _kWarn.withOpacity(0.18),
              borderRadius: BorderRadius.circular(8),
            ),
            child: const Icon(Icons.warning_amber_rounded,
                size: 18, color: _kWarn),
          ),
          const SizedBox(width: 10),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: const [
              Text(
                'Sắp hết thuốc',
                style: TextStyle(
                  fontFamily: 'Outfit',
                  fontSize: 12.5,
                  fontWeight: FontWeight.w800,
                  color: _kInk,
                  height: 1.2,
                ),
              ),
            ],
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Row(
              children: [
                Container(
                  width: 28,
                  height: 28,
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: const Icon(Icons.medication_rounded,
                      size: 16, color: _kInkSoft),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        item.name,
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                        style: const TextStyle(
                          fontFamily: 'Outfit',
                          fontSize: 12.5,
                          fontWeight: FontWeight.w700,
                          color: _kInk,
                          height: 1.2,
                        ),
                      ),
                      Text(
                        'Còn ${item.remainingPills ?? 0} viên',
                        style: const TextStyle(
                          fontFamily: 'Outfit',
                          fontSize: 11,
                          color: _kInkSoft,
                          height: 1.2,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
          Material(
            color: Colors.white,
            borderRadius: BorderRadius.circular(999),
            child: InkWell(
              onTap: () {
                HapticFeedback.selectionClick();
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(
                    content: Text('Yêu cầu mua thêm thuốc "${item.name}" đã được gửi!'),
                    backgroundColor: _kBrand,
                  ),
                );
              },
              borderRadius: BorderRadius.circular(999),
              child: Container(
                padding:
                    const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                decoration: BoxDecoration(
                  border: Border.all(color: _kBorder),
                  borderRadius: BorderRadius.circular(999),
                ),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: const [
                    Icon(Icons.shopping_cart_outlined,
                        size: 13, color: _kInk),
                    SizedBox(width: 4),
                    Text(
                      'Mua thêm',
                      style: TextStyle(
                        fontFamily: 'Outfit',
                        fontSize: 11.5,
                        fontWeight: FontWeight.w700,
                        color: _kInk,
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

// ───────────────────────── 2 SHORTCUT CARDS ─────────────────────────

class _RecentPrescriptionsCard extends StatelessWidget {
  const _RecentPrescriptionsCard();

  @override
  Widget build(BuildContext context) {
    return _ShortcutCard(
      icon: Icons.assignment_outlined,
      iconBg: _kBrandSofter,
      iconColor: _kBrand,
      title: 'Đơn thuốc gần đây',
      sub1: 'Đơn ngày 12/05/2026',
      sub2: '3 loại thuốc',
    );
  }
}

class _FamilyCabinetCard extends StatelessWidget {
  const _FamilyCabinetCard();

  @override
  Widget build(BuildContext context) {
    return _ShortcutCard(
      icon: Icons.groups_outlined,
      iconBg: const Color(0xFFFFEDD5),
      iconColor: const Color(0xFFF97316),
      title: 'Tủ thuốc gia đình',
      sub1: '4 thành viên',
      sub2: 'Chia sẻ & quản lý',
    );
  }
}

class _ShortcutCard extends StatelessWidget {
  const _ShortcutCard({
    required this.icon,
    required this.iconBg,
    required this.iconColor,
    required this.title,
    required this.sub1,
    required this.sub2,
  });

  final IconData icon;
  final Color iconBg;
  final Color iconColor;
  final String title;
  final String sub1;
  final String sub2;

  @override
  Widget build(BuildContext context) {
    return Material(
      color: Colors.white,
      borderRadius: BorderRadius.circular(16),
      child: InkWell(
        onTap: () {
          HapticFeedback.lightImpact();
        },
        borderRadius: BorderRadius.circular(16),
        child: Container(
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            border: Border.all(color: _kBorder),
            borderRadius: BorderRadius.circular(16),
          ),
          child: Row(
            children: [
              Container(
                width: 36,
                height: 36,
                decoration: BoxDecoration(
                  color: iconBg,
                  borderRadius: BorderRadius.circular(10),
                ),
                child: Icon(icon, size: 18, color: iconColor),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      title,
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      style: const TextStyle(
                        fontFamily: 'Outfit',
                        fontSize: 12.5,
                        fontWeight: FontWeight.w700,
                        color: _kInk,
                        height: 1.2,
                      ),
                    ),
                    const SizedBox(height: 1),
                    Text(
                      sub1,
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      style: const TextStyle(
                        fontFamily: 'Outfit',
                        fontSize: 10.5,
                        color: _kInkSoft,
                        height: 1.2,
                      ),
                    ),
                    Text(
                      sub2,
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      style: const TextStyle(
                        fontFamily: 'Outfit',
                        fontSize: 10.5,
                        color: _kInkSoft,
                        height: 1.2,
                      ),
                    ),
                  ],
                ),
              ),
              const Icon(Icons.chevron_right_rounded,
                  size: 18, color: _kInkMuted),
            ],
          ),
        ),
      ),
    );
  }
}

// ───────────────────────── ADD FAB ─────────────────────────

class _AddFab extends StatelessWidget {
  const _AddFab({required this.onTap});
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Material(
        color: _kBrand,
        shape: const CircleBorder(),
        elevation: 6,
        shadowColor: _kBrand.withOpacity(0.4),
        child: InkWell(
          onTap: () {
            HapticFeedback.lightImpact();
            onTap();
          },
          customBorder: const CircleBorder(),
          child: const SizedBox(
            width: 52,
            height: 52,
            child: Icon(Icons.add_rounded, color: Colors.white, size: 26),
          ),
        ),
      ),
    );
  }
}

// ───────────────────────── ADD MEDICINE SHEET ─────────────────────────

class _AddMedicineSheet extends StatefulWidget {
  const _AddMedicineSheet({required this.onAdd});
  final ValueChanged<CabinetItemInput> onAdd;

  @override
  State<_AddMedicineSheet> createState() => _AddMedicineSheetState();
}

class _AddMedicineSheetState extends State<_AddMedicineSheet> {
  final _formKey = GlobalKey<FormState>();
  final _nameCtrl = TextEditingController();
  final _dosageCtrl = TextEditingController();
  final _pillsCtrl = TextEditingController();
  final _notesCtrl = TextEditingController();

  @override
  void dispose() {
    _nameCtrl.dispose();
    _dosageCtrl.dispose();
    _pillsCtrl.dispose();
    _notesCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: const BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.only(
          topLeft: Radius.circular(24),
          topRight: Radius.circular(24),
        ),
      ),
      padding: EdgeInsets.only(
        left: 20,
        right: 20,
        top: 20,
        bottom: MediaQuery.of(context).viewInsets.bottom + 24,
      ),
      child: Form(
        key: _formKey,
        child: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Text(
                    'Thêm thuốc mới',
                    style: TextStyle(
                      fontFamily: 'Outfit',
                      fontSize: 20,
                      fontWeight: FontWeight.w800,
                      color: _kInk,
                    ),
                  ),
                  IconButton(
                    icon: const Icon(Icons.close_rounded, color: _kInkSoft),
                    onPressed: () => Navigator.pop(context),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              const Text(
                'Tên thuốc *',
                style: TextStyle(
                  fontFamily: 'Outfit',
                  fontSize: 13.5,
                  fontWeight: FontWeight.w700,
                  color: _kInk,
                ),
              ),
              const SizedBox(height: 6),
              TextFormField(
                controller: _nameCtrl,
                decoration: InputDecoration(
                  hintText: 'Ví dụ: Panadol Extra, Metformin...',
                  hintStyle: const TextStyle(color: _kInkMuted, fontSize: 13.5),
                  contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
                  filled: true,
                  fillColor: _kBg,
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                    borderSide: BorderSide.none,
                  ),
                ),
                style: const TextStyle(fontFamily: 'Outfit', fontSize: 14.5, color: _kInk),
                validator: (val) => val == null || val.trim().isEmpty ? 'Vui lòng nhập tên thuốc' : null,
              ),
              const SizedBox(height: 14),
              Row(
                children: [
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text(
                          'Liều lượng',
                          style: TextStyle(
                            fontFamily: 'Outfit',
                            fontSize: 13.5,
                            fontWeight: FontWeight.w700,
                            color: _kInk,
                          ),
                        ),
                        const SizedBox(height: 6),
                        TextFormField(
                          controller: _dosageCtrl,
                          decoration: InputDecoration(
                            hintText: 'Ví dụ: 1 viên, 500mg',
                            hintStyle: const TextStyle(color: _kInkMuted, fontSize: 13.5),
                            contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
                            filled: true,
                            fillColor: _kBg,
                            border: OutlineInputBorder(
                              borderRadius: BorderRadius.circular(12),
                              borderSide: BorderSide.none,
                            ),
                          ),
                          style: const TextStyle(fontFamily: 'Outfit', fontSize: 14.5, color: _kInk),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text(
                          'Số viên còn lại',
                          style: TextStyle(
                            fontFamily: 'Outfit',
                            fontSize: 13.5,
                            fontWeight: FontWeight.w700,
                            color: _kInk,
                          ),
                        ),
                        const SizedBox(height: 6),
                        TextFormField(
                          controller: _pillsCtrl,
                          keyboardType: TextInputType.number,
                          decoration: InputDecoration(
                            hintText: 'Ví dụ: 30',
                            hintStyle: const TextStyle(color: _kInkMuted, fontSize: 13.5),
                            contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
                            filled: true,
                            fillColor: _kBg,
                            border: OutlineInputBorder(
                              borderRadius: BorderRadius.circular(12),
                              borderSide: BorderSide.none,
                            ),
                          ),
                          style: const TextStyle(fontFamily: 'Outfit', fontSize: 14.5, color: _kInk),
                          validator: (val) {
                            if (val != null && val.isNotEmpty) {
                              final p = int.tryParse(val);
                              if (p == null || p < 0) {
                                return 'Số lượng không hợp lệ';
                              }
                            }
                            return null;
                          },
                        ),
                      ],
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 14),
              const Text(
                'Hướng dẫn / Ghi chú bác sĩ',
                style: TextStyle(
                  fontFamily: 'Outfit',
                  fontSize: 13.5,
                  fontWeight: FontWeight.w700,
                  color: _kInk,
                ),
              ),
              const SizedBox(height: 6),
              TextFormField(
                controller: _notesCtrl,
                maxLines: 3,
                decoration: InputDecoration(
                  hintText: 'Ví dụ: Uống sau ăn sáng, không uống chung với rượu...',
                  hintStyle: const TextStyle(color: _kInkMuted, fontSize: 13.5),
                  contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
                  filled: true,
                  fillColor: _kBg,
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                    borderSide: BorderSide.none,
                  ),
                ),
                style: const TextStyle(fontFamily: 'Outfit', fontSize: 14.5, color: _kInk),
              ),
              const SizedBox(height: 20),
              SizedBox(
                width: double.infinity,
                child: Material(
                  color: _kBrand,
                  borderRadius: BorderRadius.circular(12),
                  child: InkWell(
                    onTap: () {
                      if (_formKey.currentState!.validate()) {
                        HapticFeedback.mediumImpact();
                        final pills = int.tryParse(_pillsCtrl.text);
                        final input = CabinetItemInput(
                          name: _nameCtrl.text.trim(),
                          dosage: _dosageCtrl.text.trim().isEmpty ? null : _dosageCtrl.text.trim(),
                          remainingPills: pills,
                          doctorNotes: _notesCtrl.text.trim().isEmpty ? null : _notesCtrl.text.trim(),
                          isActive: true,
                          riskLevel: 'Low',
                          warnings: const [],
                          guidance: _notesCtrl.text.trim().isEmpty ? null : _notesCtrl.text.trim(),
                        );
                        widget.onAdd(input);
                        Navigator.pop(context);
                      }
                    },
                    borderRadius: BorderRadius.circular(12),
                    child: const Padding(
                      padding: EdgeInsets.symmetric(vertical: 14),
                      child: Center(
                        child: Text(
                          'Thêm vào tủ thuốc',
                          style: TextStyle(
                            fontFamily: 'Outfit',
                            fontSize: 15.5,
                            fontWeight: FontWeight.w700,
                            color: Colors.white,
                          ),
                        ),
                      ),
                    ),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
