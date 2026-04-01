import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:medisign_mobile/core/models/garden_item.dart';
import 'package:medisign_mobile/core/models/journal_entry.dart';
import 'package:medisign_mobile/features/soul_garden/presentation/soul_garden_page.dart';
import 'package:medisign_mobile/core/services/soul_garden_service.dart';

void main() {
  Widget buildSubject() {
    return const MaterialApp(home: SoulGardenPage());
  }

  // Use pump(duration) instead of pumpAndSettle because the tree animation
  // repeats infinitely, which causes pumpAndSettle to time out.
  Future<void> pumpPage(WidgetTester tester) async {
    await tester.pumpWidget(buildSubject());
    await tester.pump(const Duration(seconds: 1));
  }

  group('SoulGardenPage', () {
    testWidgets('renders garden scene and key UI', (tester) async {
      await pumpPage(tester);

      // Garden scene should be visible (equipped tree emoji)
      final svc = SoulGardenService.instance;
      final tree = svc.equippedItem(GardenCategory.tree);
      expect(find.text(tree?.emoji ?? '🌱'), findsWidgets);

      // Customize button should be visible
      expect(find.textContaining('Tùy chỉnh vườn'), findsOneWidget);
    });

    testWidgets('renders sample entries on first launch', (tester) async {
      await pumpPage(tester);
      expect(SoulGardenService.instance.entries.length,
          greaterThanOrEqualTo(10));
    });

    testWidgets('write journal button is reachable', (tester) async {
      await pumpPage(tester);

      // Scroll to find the write button
      final scrollable = find.byType(Scrollable).first;
      await tester.scrollUntilVisible(
        find.textContaining('Viết nhật ký'),
        200,
        scrollable: scrollable,
      );
      await tester.pump(const Duration(milliseconds: 300));

      expect(find.textContaining('Viết nhật ký'), findsWidgets);
    });
  });

  group('SoulGardenService', () {
    test('seed data creates at least 10 entries', () {
      final svc = SoulGardenService.instance;
      expect(svc.entries.length, greaterThanOrEqualTo(10));
    });

    test('addEntry increases count', () {
      final svc = SoulGardenService.instance;
      final before = svc.entries.length;

      svc.addEntry(JournalEntry(
        id: 'test_${DateTime.now().millisecondsSinceEpoch}',
        date: DateTime.now(),
        mood: Mood.good,
        content: 'Test entry',
        tags: {},
      ));

      expect(svc.entries.length, before + 1);
    });

    test('streak calculation works', () {
      final svc = SoulGardenService.instance;
      expect(svc.streak, greaterThanOrEqualTo(1));
    });

    test('treeState returns valid state', () {
      final svc = SoulGardenService.instance;
      final state = svc.treeState;
      expect(state.emoji.isNotEmpty, true);
      expect(state.name.isNotEmpty, true);
    });

    test('statsForDays returns valid stats', () {
      final svc = SoulGardenService.instance;
      final stats = svc.statsForDays(7);
      expect(stats.totalEntries, greaterThanOrEqualTo(0));
      expect(stats.distribution.length, 5);
    });

    test('achievements list is not empty', () {
      final svc = SoulGardenService.instance;
      expect(svc.allAchievements.length, greaterThan(0));
    });
  });

  group('Garden Shop', () {
    test('catalog has 30 items', () {
      expect(SoulGardenService.gardenCatalog.length, 30);
    });

    test('default items are unlocked', () {
      final svc = SoulGardenService.instance;
      final defaults =
          SoulGardenService.gardenCatalog.where((i) => i.isDefault);
      for (final item in defaults) {
        expect(svc.isItemUnlocked(item), true,
            reason: '${item.id} should be unlocked by default');
      }
    });

    test('equip changes equipped item', () {
      final svc = SoulGardenService.instance;

      // Equip tree_herb (should be unlocked with 10+ entries)
      svc.equip('tree_herb');
      expect(svc.equippedId(GardenCategory.tree), 'tree_herb');

      // Equip pot_vase (should be unlocked with streak >= 3)
      svc.equip('pot_vase');
      expect(svc.equippedId(GardenCategory.pot), 'pot_vase');

      // Reset to defaults
      svc.equip('tree_sprout');
      svc.equip('pot_basic');
    });

    test('unequipAccessory clears accessory', () {
      final svc = SoulGardenService.instance;

      svc.equip('acc_bee'); // Unlock with 10+ entries
      expect(svc.equippedId(GardenCategory.accessory), 'acc_bee');

      svc.unequipAccessory();
      expect(svc.equippedId(GardenCategory.accessory), '');
    });

    test('unlocked count increases with entries', () {
      final svc = SoulGardenService.instance;
      final count = svc.unlockedItemIds.length;
      // With 10+ seed entries, should have several unlocked
      expect(count, greaterThan(3));
    });

    test('each category has at least one default item', () {
      for (final cat in GardenCategory.values) {
        final hasDefault = SoulGardenService.gardenCatalog
            .any((i) => i.category == cat && i.isDefault);
        // accessories don't have a default
        if (cat != GardenCategory.accessory) {
          expect(hasDefault, true,
              reason: '${cat.label} should have a default item');
        }
      }
    });
  });
}
