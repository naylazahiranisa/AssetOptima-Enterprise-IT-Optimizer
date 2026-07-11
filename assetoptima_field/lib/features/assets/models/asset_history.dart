class AssetHistory {
  final String id;
  final String action;
  final String? performedBy;
  final DateTime performedAt;
  final String? notes;

  const AssetHistory({
    required this.id,
    required this.action,
    this.performedBy,
    required this.performedAt,
    this.notes,
  });

  factory AssetHistory.fromJson(Map<String, dynamic> json) => AssetHistory(
        id: json['id'] as String,
        action: json['action'] as String,
        performedBy: json['performed_by'] as String?,
        performedAt: DateTime.parse(json['performed_at'] as String),
        notes: json['notes'] as String?,
      );

  String get actionLabel {
    switch (action) {
      case 'create':
        return 'Created';
      case 'update':
        return 'Updated';
      case 'assign':
        return 'Assigned';
      case 'return':
        return 'Returned';
      case 'transfer':
        return 'Transferred';
      case 'maintenance':
        return 'Maintenance';
      case 'verify':
        return 'Verified';
      default:
        return action;
    }
  }
}
