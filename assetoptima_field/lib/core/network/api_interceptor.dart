import 'package:dio/dio.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import '../config/api_endpoints.dart';

class ApiInterceptor extends Interceptor {
  static const _storage = FlutterSecureStorage();
  static const _accessTokenKey = 'access_token';
  static const _refreshTokenKey = 'refresh_token';

  static Future<void> saveTokens({
    required String accessToken,
    required String refreshToken,
  }) async {
    await _storage.write(key: _accessTokenKey, value: accessToken);
    await _storage.write(key: _refreshTokenKey, value: refreshToken);
  }

  static Future<String?> getAccessToken() async =>
      _storage.read(key: _accessTokenKey);

  static Future<String?> getRefreshToken() async =>
      _storage.read(key: _refreshTokenKey);

  static Future<void> clearTokens() async {
    await _storage.delete(key: _accessTokenKey);
    await _storage.delete(key: _refreshTokenKey);
  }

  @override
  void onRequest(
    RequestOptions options,
    RequestInterceptorHandler handler,
  ) async {
    final token = await getAccessToken();
    if (token != null) {
      options.headers['Authorization'] = 'Bearer $token';
    }
    handler.next(options);
  }

  @override
  void onError(DioException err, ErrorInterceptorHandler handler) async {
    if (err.response?.statusCode == 401) {
      final refreshToken = await getRefreshToken();
      if (refreshToken != null) {
        try {
          final dio = Dio(
            BaseOptions(
              baseUrl: err.requestOptions.baseUrl,
              headers: {'Content-Type': 'application/json'},
            ),
          );
          final res = await dio.post(
            ApiEndpoints.refresh,
            data: {'refresh_token': refreshToken},
          );
          final newAccess = res.data['access_token'] as String;
          final newRefresh = res.data['refresh_token'] as String;

          await saveTokens(
            accessToken: newAccess,
            refreshToken: newRefresh,
          );

          err.requestOptions.headers['Authorization'] = 'Bearer $newAccess';
          final response = await dio.fetch(err.requestOptions);
          handler.resolve(response);
          return;
        } catch (_) {
          await clearTokens();
        }
      }
    }
    handler.next(err);
  }
}
