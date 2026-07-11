import 'environment.dart';

class ApiEndpoints {
  ApiEndpoints._();

  static const String _pref = Environment.apiPrefix;

  static const String login = '$_pref/auth/login';
  static const String refresh = '$_pref/auth/refresh';
  static const String logout = '$_pref/auth/logout';
  static const String me = '$_pref/auth/me';

  static const String assets = '$_pref/assets';
  static String asset(String id) => '$_pref/assets/$id';
  static String assetHistory(String id) => '$_pref/assets/$id/history';
  static String assignAsset(String id) => '$_pref/assets/$id/assign';
  static String returnAsset(String id) => '$_pref/assets/$id/return';
  static String transferAsset(String id) => '$_pref/assets/$id/transfer';
  static const String verifyAsset = '$_pref/assets/verify';
  static String assetByQr(String code) => '$_pref/assets/qr/$code';

  static const String employees = '$_pref/employees';
  static String employee(String id) => '$_pref/employees/$id';

  static const String notifications = '$_pref/notifications';
  static String notification(String id) => '$_pref/notifications/$id';
  static const String unreadCount = '$_pref/notifications/unread/count';
  static String readNotification(String id) =>
      '$_pref/notifications/read/$id';
  static String archiveNotification(String id) =>
      '$_pref/notifications/archive/$id';

  static const String dashboard = '$_pref/dashboard/stats';
}
