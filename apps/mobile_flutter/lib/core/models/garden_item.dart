/// Garden customization item model — all visuals are emoji (zero assets).
///
/// Items are grouped by [GardenCategory] and unlocked through user
/// engagement (journaling, streaks, mood trends, breathing exercises).
library;

enum GardenCategory {
  tree,
  pot,
  accessory,
  background,
}

extension GardenCategoryX on GardenCategory {
  String get label {
    switch (this) {
      case GardenCategory.tree:
        return 'Cây';
      case GardenCategory.pot:
        return 'Chậu';
      case GardenCategory.accessory:
        return 'Phụ kiện';
      case GardenCategory.background:
        return 'Nền';
    }
  }

  String get emoji {
    switch (this) {
      case GardenCategory.tree:
        return '🌳';
      case GardenCategory.pot:
        return '🪴';
      case GardenCategory.accessory:
        return '✨';
      case GardenCategory.background:
        return '🎨';
    }
  }
}

/// A single equippable garden decoration item.
class GardenItem {
  const GardenItem({
    required this.id,
    required this.category,
    required this.emoji,
    required this.name,
    required this.unlockHint,
    this.isDefault = false,
  });

  final String id;
  final GardenCategory category;
  final String emoji;
  final String name;
  final String unlockHint; // Human-readable unlock requirement
  final bool isDefault; // Available from the start
}
