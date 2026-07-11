class AssetAssignment {
  final String id;
  final String assetId;
  final String employeeId;
  final String? employeeName;
  final String? assignedByName;
  final DateTime assignedAt;
  final DateTime? returnedAt;
  final String status;
  final String? notes;

  const AssetAssignment({
    required this.id,
    required this.assetId,
    required this.employeeId,
    this.employeeName,
    this.assignedByName,
    required this.assignedAt,
    this.returnedAt,
    required this.status,
    this.notes,
  });

  factory AssetAssignment.fromJson(Map<String, dynamic> json) =>
      AssetAssignment(
        id: json['id'] as String,
        assetId: json['asset_id'] as String,
        employeeId: json['employee_id'] as String,
        employeeName: json['employee_name'] as String?,
        assignedByName: json['assigned_by_name'] as String?,
        assignedAt: DateTime.parse(json['assigned_at'] as String),
        returnedAt: json['returned_at'] != null
            ? DateTime.tryParse(json['returned_at'] as String)
            : null,
        status: json['status'] as String? ?? 'active',
        notes: json['notes'] as String?,
      );
}

class Employee {
  final String id;
  final String employeeId;
  final String fullName;
  final String? email;
  final String? position;

  const Employee({
    required this.id,
    required this.employeeId,
    required this.fullName,
    this.email,
    this.position,
  });

  factory Employee.fromJson(Map<String, dynamic> json) => Employee(
        id: json['id'] as String,
        employeeId: json['employee_id'] as String,
        fullName: json['full_name'] as String,
        email: json['email'] as String?,
        position: json['position'] as String?,
      );
}
