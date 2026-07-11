import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/config/api_endpoints.dart';
import '../../../core/network/api_interceptor.dart';
import '../../../core/network/dio_client.dart';
import '../models/user.dart';

class AuthService {
  AuthService(this._dio);

  final Dio _dio;

  Future<User> login({
    required String email,
    required String password,
  }) async {
    final res = await _dio.post(
      ApiEndpoints.login,
      data: {'email': email, 'password': password},
    );
    final data = res.data;
    await ApiInterceptor.saveTokens(
      accessToken: data['access_token'] as String,
      refreshToken: data['refresh_token'] as String,
    );
    return User(
      id: data['user_id'] ?? '',
      email: email,
      fullName: data['full_name'] ?? email,
      role: data['role'] as String,
      isActive: true,
    );
  }

  Future<User> getProfile() async {
    final res = await _dio.get(ApiEndpoints.me);
    final data = res.data is Map && res.data['data'] != null
        ? res.data['data'] as Map<String, dynamic>
        : res.data as Map<String, dynamic>;
    return User.fromJson(data);
  }

  Future<void> logout() async {
    try {
      await _dio.post(ApiEndpoints.logout);
    } catch (_) {}
    await ApiInterceptor.clearTokens();
  }

  Future<bool> hasSession() async {
    final token = await ApiInterceptor.getAccessToken();
    return token != null;
  }
}

final authServiceProvider = Provider<AuthService>((ref) {
  final dio = ref.watch(dioClientProvider);
  return AuthService(dio);
});
