import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/notification_model.dart';
import '../services/notification_service.dart';

final notificationsProvider =
    AsyncNotifierProvider<NotificationsNotifier, List<AppNotification>>(
  NotificationsNotifier.new,
);

class NotificationsNotifier extends AsyncNotifier<List<AppNotification>> {
  @override
  Future<List<AppNotification>> build() async {
    final service = ref.read(notificationServiceProvider);
    return service.listNotifications();
  }

  Future<void> refresh() async {
    state = const AsyncLoading();
    state = await AsyncValue.guard(() async {
      final service = ref.read(notificationServiceProvider);
      return service.listNotifications();
    });
  }

  Future<void> markAsRead(String id) async {
    try {
      final service = ref.read(notificationServiceProvider);
      await service.markAsRead(id);
      state = AsyncData(
        (state.valueOrNull ?? []).map((n) {
          if (n.id == id) {
            return AppNotification(
              id: n.id,
              title: n.title,
              message: n.message,
              category: n.category,
              priority: n.priority,
              status: 'read',
              referenceId: n.referenceId,
              readAt: DateTime.now().toIso8601String(),
              createdAt: n.createdAt,
            );
          }
          return n;
        }).toList(),
      );
    } catch (_) {}
  }
}

final unreadCountProvider = FutureProvider<int>((ref) {
  final service = ref.read(notificationServiceProvider);
  return service.getUnreadCount();
});
