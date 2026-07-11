import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/config/api_endpoints.dart';
import '../../../core/network/dio_client.dart';
import '../models/notification_model.dart';

class NotificationService {
  NotificationService(this._dio);
  final Dio _dio;

  Future<List<AppNotification>> listNotifications({
    int page = 1,
    int perPage = 20,
  }) async {
    final res = await _dio.get(
      ApiEndpoints.notifications,
      queryParameters: {'page': page, 'per_page': perPage},
    );
    final list = res.data['data'] as List<dynamic>;
    return list
        .map((e) => AppNotification.fromJson(e as Map<String, dynamic>))
        .toList();
  }

  Future<int> getUnreadCount() async {
    final res = await _dio.get(ApiEndpoints.unreadCount);
    return res.data['data']?['total'] as int? ?? 0;
  }

  Future<void> markAsRead(String id) async {
    await _dio.post(ApiEndpoints.readNotification(id));
  }

  Future<void> archive(String id) async {
    await _dio.post(ApiEndpoints.archiveNotification(id));
  }
}

final notificationServiceProvider = Provider<NotificationService>((ref) {
  return NotificationService(ref.watch(dioClientProvider));
});
