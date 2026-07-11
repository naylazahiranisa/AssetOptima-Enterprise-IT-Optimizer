import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/config/api_endpoints.dart';
import '../../../core/network/dio_client.dart';
import '../models/dashboard_stats.dart';

class DashboardService {
  DashboardService(this._dio);
  final Dio _dio;

  Future<DashboardStats> getStats() async {
    final res = await _dio.get(ApiEndpoints.dashboard);
    return DashboardStats.fromJson(res.data['data'] as Map<String, dynamic>);
  }
}

final dashboardServiceProvider = Provider<DashboardService>((ref) {
  return DashboardService(ref.watch(dioClientProvider));
});
