class DashboardStats {
  final int totalAssets;
  final int assignedAssets;
  final int availableAssets;
  final int maintenanceAssets;
  final int pendingVerifications;
  final int totalEmployees;
  final int unreadNotifications;

  const DashboardStats({
    required this.totalAssets,
    required this.assignedAssets,
    required this.availableAssets,
    required this.maintenanceAssets,
    required this.pendingVerifications,
    required this.totalEmployees,
    required this.unreadNotifications,
  });

  factory DashboardStats.fromJson(Map<String, dynamic> json) =>
      DashboardStats(
        totalAssets: json['total_assets'] as int? ?? 0,
        assignedAssets: json['assigned_assets'] as int? ?? 0,
        availableAssets: json['available_assets'] as int? ?? 0,
        maintenanceAssets: json['maintenance_assets'] as int? ?? 0,
        pendingVerifications: json['pending_verifications'] as int? ?? 0,
        totalEmployees: json['total_employees'] as int? ?? 0,
        unreadNotifications: json['unread_notifications'] as int? ?? 0,
      );
}
