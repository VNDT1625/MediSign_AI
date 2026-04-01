/// A medicine saved to the user's personal medicine cabinet.
class SavedMedicine {
  final String id;
  final String name;
  final String? activeIngredient;
  final String? dosage;
  final String? frequency;
  final String? notes;
  final DateTime addedDate;

  const SavedMedicine({
    required this.id,
    required this.name,
    this.activeIngredient,
    this.dosage,
    this.frequency,
    this.notes,
    required this.addedDate,
  });

  SavedMedicine copyWith({
    String? id,
    String? name,
    String? activeIngredient,
    String? dosage,
    String? frequency,
    String? notes,
    DateTime? addedDate,
  }) {
    return SavedMedicine(
      id: id ?? this.id,
      name: name ?? this.name,
      activeIngredient: activeIngredient ?? this.activeIngredient,
      dosage: dosage ?? this.dosage,
      frequency: frequency ?? this.frequency,
      notes: notes ?? this.notes,
      addedDate: addedDate ?? this.addedDate,
    );
  }
}
