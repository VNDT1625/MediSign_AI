import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import '../../../core/models/garden_item.dart';
import '../../../core/services/soul_garden_service.dart';

/// Garden Shop — browse, preview, and equip garden decorations.
class GardenShopPage extends StatefulWidget {
  const GardenShopPage({super.key});

  @override
  State<GardenShopPage> createState() => _GardenShopPageState();
}

class _GardenShopPageState extends State<GardenShopPage>
    with SingleTickerProviderStateMixin {
  final _svc = SoulGardenService.instance;
  late TabController _tabController;

  static const _categories = GardenCategory.values;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: _categories.length, vsync: this);
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [Color(0xFF1B4332), Color(0xFF2D6A4F), Color(0xFF40916C)],
          ),
        ),
        child: SafeArea(
          child: Column(
            children: [
              // ─── Header ──────────────────────
              Padding(
                padding: const EdgeInsets.fromLTRB(8, 8, 16, 0),
                child: Row(
                  children: [
                    IconButton(
                      icon: const Icon(Icons.arrow_back_ios,
                          color: Colors.white70),
                      onPressed: () => Navigator.pop(context),
                    ),
                    const Text('Tùy chỉnh vườn',
                        style: TextStyle(
                            color: Colors.white,
                            fontSize: 18,
                            fontWeight: FontWeight.w600)),
                    const Spacer(),
                    // Unlocked count badge
                    Container(
                      padding: const EdgeInsets.symmetric(
                          horizontal: 10, vertical: 5),
                      decoration: BoxDecoration(
                        color: const Color(0xFF52B788).withOpacity(0.3),
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: Text(
                        '${_svc.unlockedItemIds.length}/${SoulGardenService.gardenCatalog.length}',
                        style: const TextStyle(
                            color: Colors.white,
                            fontSize: 13,
                            fontWeight: FontWeight.w600),
                      ),
                    ),
                  ],
                ),
              ),

              // ─── Garden Preview ──────────────
              const SizedBox(height: 12),
              _buildGardenPreview(),

              // ─── Category Tabs ───────────────
              const SizedBox(height: 16),
              TabBar(
                controller: _tabController,
                indicatorColor: const Color(0xFF52B788),
                indicatorWeight: 3,
                labelColor: Colors.white,
                unselectedLabelColor: Colors.white54,
                labelStyle: const TextStyle(
                    fontSize: 13, fontWeight: FontWeight.w600),
                tabs: _categories
                    .map((c) => Tab(text: '${c.emoji} ${c.label}'))
                    .toList(),
              ),

              // ─── Item Grid ───────────────────
              Expanded(
                child: TabBarView(
                  controller: _tabController,
                  children:
                      _categories.map((c) => _buildItemGrid(c)).toList(),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  // ─── GARDEN PREVIEW ─────────────────────────

  Widget _buildGardenPreview() {
    final tree = _svc.equippedItem(GardenCategory.tree);
    final pot = _svc.equippedItem(GardenCategory.pot);
    final acc = _svc.equippedItem(GardenCategory.accessory);
    final bg = _svc.equippedItem(GardenCategory.background);

    // Background gradient based on equipped bg
    final bgColors = _bgGradient(bg?.id ?? 'bg_day');

    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 20),
      height: 180,
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topCenter,
          end: Alignment.bottomCenter,
          colors: bgColors,
        ),
        borderRadius: BorderRadius.circular(24),
        border: Border.all(color: Colors.white.withOpacity(0.15)),
      ),
      child: Stack(
        alignment: Alignment.center,
        children: [
          // Background emoji (top-right)
          if (bg != null)
            Positioned(
              top: 12,
              right: 16,
              child: Text(bg.emoji,
                  style: const TextStyle(fontSize: 32)),
            ),

          // Accessory (floating left of tree)
          if (acc != null)
            Positioned(
              top: 28,
              left: 40,
              child: _floatingWidget(
                child: Text(acc.emoji,
                    style: const TextStyle(fontSize: 28)),
              ),
            ),

          // Tree (centered)
          Positioned(
            bottom: 48,
            child: Text(tree?.emoji ?? '🌱',
                style: const TextStyle(fontSize: 64)),
          ),

          // Pot (below tree)
          Positioned(
            bottom: 16,
            child: Text(pot?.emoji ?? '🟤',
                style: const TextStyle(fontSize: 36)),
          ),
        ],
      ),
    );
  }

  Widget _floatingWidget({required Widget child}) {
    return TweenAnimationBuilder<double>(
      tween: Tween(begin: 0, end: 1),
      duration: const Duration(seconds: 2),
      builder: (_, value, c) {
        return Transform.translate(
          offset: Offset(0, -4 * (0.5 - (value - 0.5).abs())),
          child: c,
        );
      },
      child: child,
    );
  }

  List<Color> _bgGradient(String bgId) {
    switch (bgId) {
      case 'bg_sunset':
        return [const Color(0xFF7C2D12), const Color(0xFFF59E0B)];
      case 'bg_night':
        return [const Color(0xFF0F172A), const Color(0xFF1E293B)];
      case 'bg_rain':
        return [const Color(0xFF374151), const Color(0xFF6B7280)];
      case 'bg_snow':
        return [const Color(0xFFBFDBFE), const Color(0xFFDDD6FE)];
      case 'bg_galaxy':
        return [const Color(0xFF1E1B4B), const Color(0xFF4C1D95)];
      default: // bg_day
        return [const Color(0xFF065F46), const Color(0xFF34D399)];
    }
  }

  // ─── ITEM GRID ──────────────────────────────

  Widget _buildItemGrid(GardenCategory category) {
    final items = SoulGardenService.gardenCatalog
        .where((i) => i.category == category)
        .toList();
    final equippedId = _svc.equippedId(category);

    return GridView.builder(
      padding: const EdgeInsets.fromLTRB(20, 16, 20, 32),
      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 3,
        crossAxisSpacing: 12,
        mainAxisSpacing: 12,
        childAspectRatio: 0.78,
      ),
      itemCount: items.length,
      itemBuilder: (_, i) {
        final item = items[i];
        final unlocked = _svc.isItemUnlocked(item);
        final equipped = equippedId == item.id;

        return GestureDetector(
          onTap: () {
            if (!unlocked) {
              _showLockedInfo(item);
              return;
            }
            HapticFeedback.selectionClick();
            setState(() {
              if (equipped && category == GardenCategory.accessory) {
                _svc.unequipAccessory();
              } else {
                _svc.equip(item.id);
              }
            });
          },
          child: Container(
            decoration: BoxDecoration(
              color: equipped
                  ? const Color(0xFF52B788).withOpacity(0.2)
                  : unlocked
                      ? Colors.white.withOpacity(0.08)
                      : Colors.white.withOpacity(0.03),
              borderRadius: BorderRadius.circular(16),
              border: Border.all(
                color: equipped
                    ? const Color(0xFF52B788)
                    : unlocked
                        ? Colors.white.withOpacity(0.1)
                        : Colors.white.withOpacity(0.05),
                width: equipped ? 2 : 1,
              ),
            ),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Text(
                  unlocked ? item.emoji : '🔒',
                  style: TextStyle(
                    fontSize: unlocked ? 36 : 24,
                  ),
                ),
                const SizedBox(height: 8),
                Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 4),
                  child: Text(
                    unlocked ? item.name : '???',
                    textAlign: TextAlign.center,
                    style: TextStyle(
                      color: unlocked
                          ? Colors.white
                          : Colors.white.withOpacity(0.3),
                      fontSize: 11,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                ),
                if (equipped)
                  const Padding(
                    padding: EdgeInsets.only(top: 4),
                    child: Icon(Icons.check_circle,
                        color: Color(0xFF52B788), size: 16),
                  ),
                if (!unlocked)
                  Padding(
                    padding: const EdgeInsets.only(top: 2),
                    child: Text(
                      item.unlockHint,
                      textAlign: TextAlign.center,
                      style: TextStyle(
                        color: Colors.white.withOpacity(0.25),
                        fontSize: 9,
                      ),
                    ),
                  ),
              ],
            ),
          ),
        );
      },
    );
  }

  void _showLockedInfo(GardenItem item) {
    showModalBottomSheet(
      context: context,
      backgroundColor: Colors.transparent,
      builder: (_) => Container(
        padding: const EdgeInsets.all(24),
        decoration: const BoxDecoration(
          color: Color(0xFF1B4332),
          borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              width: 40,
              height: 4,
              decoration: BoxDecoration(
                color: Colors.white24,
                borderRadius: BorderRadius.circular(2),
              ),
            ),
            const SizedBox(height: 20),
            const Text('🔒', style: TextStyle(fontSize: 48)),
            const SizedBox(height: 12),
            Text(item.name,
                style: const TextStyle(
                    color: Colors.white,
                    fontSize: 18,
                    fontWeight: FontWeight.w700)),
            const SizedBox(height: 8),
            Container(
              padding: const EdgeInsets.symmetric(
                  horizontal: 16, vertical: 10),
              decoration: BoxDecoration(
                color: Colors.white.withOpacity(0.08),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  const Icon(Icons.lock_outline,
                      color: Color(0xFF52B788), size: 18),
                  const SizedBox(width: 8),
                  Text(item.unlockHint,
                      style: const TextStyle(
                          color: Colors.white70, fontSize: 14)),
                ],
              ),
            ),
            const SizedBox(height: 16),
            Text('Tiếp tục viết nhật ký để mở khóa!',
                style: TextStyle(
                    color: Colors.white.withOpacity(0.5), fontSize: 13)),
            const SizedBox(height: 16),
          ],
        ),
      ),
    );
  }
}
