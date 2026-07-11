class Asset {
  final String id;
  final String assetCode;
  final String name;
  final String? description;
  final String? serialNumber;
  final String status;
  final String condition;
  final String? categoryId;
  final String? vendorId;
  final String? locationId;
  final String? currentEmployeeId;
  final DateTime? purchaseDate;
  final double? purchasePrice;
  final String? warrantyExpiry;
  final String? qrValue;
  final String? notes;
  final bool isActive;
  final DateTime createdAt;
  final DateTime? updatedAt;

  const Asset({
    required this.id,
    required this.assetCode,
    required this.name,
    this.description,
    this.serialNumber,
    required this.status,
    required this.condition,
    this.categoryId,
    this.vendorId,
    this.locationId,
    this.currentEmployeeId,
    this.purchaseDate,
    this.purchasePrice,
    this.warrantyExpiry,
    this.qrValue,
    this.notes,
    required this.isActive,
    required this.createdAt,
    this.updatedAt,
  });

  factory Asset.fromJson(Map<String, dynamic> json) => Asset(
        id: json['id'] as String,
        assetCode: json['asset_code'] as String? ?? json['id'] as String,
        name: json['name'] as String,
        description: json['description'] as String?,
        serialNumber: json['serial_number'] as String?,
        status: json['status'] as String? ?? 'unknown',
        condition: json['condition'] as String? ?? 'unknown',
        categoryId: json['category_id'] as String?,
        vendorId: json['vendor_id'] as String?,
        locationId: json['location_id'] as String?,
        currentEmployeeId: json['current_employee_id'] as String?,
        purchaseDate: json['purchase_date'] != null
            ? DateTime.tryParse(json['purchase_date'] as String)
            : null,
        purchasePrice: (json['purchase_price'] as num?)?.toDouble(),
        warrantyExpiry: json['warranty_expiry'] as String?,
        qrValue: json['qr_value'] as String?,
        notes: json['notes'] as String?,
        isActive: json['is_active'] as bool? ?? true,
        createdAt: DateTime.parse(json['created_at'] as String),
        updatedAt: json['updated_at'] != null
            ? DateTime.tryParse(json['updated_at'] as String)
            : null,
      );
}
