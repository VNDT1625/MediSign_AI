/// Admin models for API responses.
library;

class AdminUser {
  final String id;
  final String username;
  final String email;
  final String? phone;
  final String fullName;
  final bool isEmailVerified;
  final bool isPhoneVerified;
  final bool isActive;
  final String accountType;
  final DateTime? lastLogin;
  final DateTime createdAt;

  AdminUser({
    required this.id,
    required this.username,
    required this.email,
    this.phone,
    required this.fullName,
    required this.isEmailVerified,
    required this.isPhoneVerified,
    required this.isActive,
    required this.accountType,
    this.lastLogin,
    required this.createdAt,
  });

  factory AdminUser.fromJson(Map<String, dynamic> json) {
    return AdminUser(
      id: json['id'] ?? '',
      username: json['username'] ?? '',
      email: json['email'] ?? '',
      phone: json['phone'],
      fullName: json['full_name'] ?? '',
      isEmailVerified: json['is_email_verified'] ?? false,
      isPhoneVerified: json['is_phone_verified'] ?? false,
      isActive: json['is_active'] ?? true,
      accountType: json['account_type'] ?? 'user',
      lastLogin: json['last_login'] != null 
          ? DateTime.tryParse(json['last_login']) 
          : null,
      createdAt: DateTime.parse(json['created_at'] ?? DateTime.now().toIso8601String()),
    );
  }

  Map<String, dynamic> toJson() => {
    'id': id,
    'username': username,
    'email': email,
    'phone': phone,
    'full_name': fullName,
    'is_email_verified': isEmailVerified,
    'is_phone_verified': isPhoneVerified,
    'is_active': isActive,
    'account_type': accountType,
  };
}

class AdminMedicine {
  final String regNumber;
  final String name;
  final String? activeIngredient;
  final String? dosageForm;
  final String? strength;
  final String? manufacturer;
  final bool isActive;
  final DateTime createdAt;

  AdminMedicine({
    required this.regNumber,
    required this.name,
    this.activeIngredient,
    this.dosageForm,
    this.strength,
    this.manufacturer,
    required this.isActive,
    required this.createdAt,
  });

  factory AdminMedicine.fromJson(Map<String, dynamic> json) {
    return AdminMedicine(
      regNumber: json['reg_number'] ?? '',
      name: json['name'] ?? '',
      activeIngredient: json['active_ingredient'],
      dosageForm: json['dosage_form'],
      strength: json['strength'],
      manufacturer: json['manufacturer'],
      isActive: json['is_active'] ?? true,
      createdAt: DateTime.parse(json['created_at'] ?? DateTime.now().toIso8601String()),
    );
  }
}

class AdminHospital {
  final int id;
  final String name;
  final String? address;
  final String? district;
  final String? city;
  final String? phone;
  final String? website;
  final String? latitude;
  final String? longitude;
  final String? specialties;
  final bool acceptsBhyt;
  final bool is24h;
  final bool hasEmergency;
  final String? hospitalType;

  AdminHospital({
    required this.id,
    required this.name,
    this.address,
    this.district,
    this.city,
    this.phone,
    this.website,
    this.latitude,
    this.longitude,
    this.specialties,
    required this.acceptsBhyt,
    required this.is24h,
    required this.hasEmergency,
    this.hospitalType,
  });

  factory AdminHospital.fromJson(Map<String, dynamic> json) {
    return AdminHospital(
      id: json['id'] ?? 0,
      name: json['name'] ?? '',
      address: json['address'],
      district: json['district'],
      city: json['city'],
      phone: json['phone'],
      website: json['website'],
      latitude: json['latitude'],
      longitude: json['longitude'],
      specialties: json['specialties'],
      acceptsBhyt: json['accepts_bhyt'] ?? false,
      is24h: json['is_24h'] ?? false,
      hasEmergency: json['has_emergency'] ?? false,
      hospitalType: json['hospital_type'],
    );
  }
}

class AdminStats {
  final int totalUsers;
  final int activeUsers;
  final int inactiveUsers;
  final int totalMedicines;
  final int totalHospitals;

  AdminStats({
    required this.totalUsers,
    required this.activeUsers,
    required this.inactiveUsers,
    required this.totalMedicines,
    required this.totalHospitals,
  });

  factory AdminStats.fromJson(Map<String, dynamic> json) {
    final users = json['users'] ?? {};
    final medicines = json['medicines'] ?? {};
    final hospitals = json['hospitals'] ?? {};
    
    return AdminStats(
      totalUsers: users['total'] ?? 0,
      activeUsers: users['active'] ?? 0,
      inactiveUsers: users['inactive'] ?? 0,
      totalMedicines: medicines['total'] ?? 0,
      totalHospitals: hospitals['total'] ?? 0,
    );
  }
}

