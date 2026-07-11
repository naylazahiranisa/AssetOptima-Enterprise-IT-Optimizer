import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/config/api_endpoints.dart';
import '../../../core/network/dio_client.dart';
import '../models/asset.dart';
import '../models/asset_assignment.dart';
import '../models/asset_history.dart';

class AssetService {
  AssetService(this._dio);
  final Dio _dio;

  Future<List<Asset>> listAssets({
    int page = 1,
    int perPage = 20,
    String? keyword,
    String? status,
    String? condition,
    String? categoryId,
    String? employeeId,
  }) async {
    final params = <String, dynamic>{
      'page': page,
      'per_page': perPage,
    };
    if (keyword != null) params['keyword'] = keyword;
    if (status != null) params['status'] = status;
    if (condition != null) params['condition'] = condition;
    if (categoryId != null) params['category_id'] = categoryId;
    if (employeeId != null) params['employee_id'] = employeeId;

    final res = await _dio.get(ApiEndpoints.assets, queryParameters: params);
    final list = res.data['data'] as List<dynamic>;
    return list
        .map((e) => Asset.fromJson(e as Map<String, dynamic>))
        .toList();
  }

  Future<Asset> getAsset(String id) async {
    final res = await _dio.get(ApiEndpoints.asset(id));
    return Asset.fromJson(res.data['data'] as Map<String, dynamic>);
  }

  Future<Asset> getAssetByQr(String code) async {
    final res = await _dio.get(ApiEndpoints.assetByQr(code));
    return Asset.fromJson(res.data['data'] as Map<String, dynamic>);
  }

  Future<List<AssetHistory>> getHistory(String id) async {
    final res = await _dio.get(ApiEndpoints.assetHistory(id));
    final list = res.data['data'] as List<dynamic>;
    return list
        .map((e) => AssetHistory.fromJson(e as Map<String, dynamic>))
        .toList();
  }

  Future<AssetAssignment> assignAsset({
    required String assetId,
    required String employeeId,
    String? expectedReturnDate,
    String? notes,
  }) async {
    final res = await _dio.post(
      ApiEndpoints.assignAsset(assetId),
      data: {
        'employee_id': employeeId,
        if (expectedReturnDate != null)
          'expected_return_date': expectedReturnDate,
        if (notes != null) 'notes': notes,
      },
    );
    return AssetAssignment.fromJson(res.data['data'] as Map<String, dynamic>);
  }

  Future<void> returnAsset({
    required String assetId,
    String? notes,
    String? condition,
  }) async {
    await _dio.post(
      ApiEndpoints.returnAsset(assetId),
      data: {
        if (notes != null) 'notes': notes,
        if (condition != null) 'condition': condition,
      },
    );
  }

  Future<void> verifyAsset(String assetId) async {
    await _dio.post('${ApiEndpoints.verifyAsset}/$assetId');
  }

  Future<List<Employee>> searchEmployees(String keyword) async {
    final res = await _dio.get(
      ApiEndpoints.employees,
      queryParameters: {'keyword': keyword, 'per_page': 20},
    );
    final list = res.data['data'] as List<dynamic>;
    return list
        .map((e) => Employee.fromJson(e as Map<String, dynamic>))
        .toList();
  }
}

final assetServiceProvider = Provider<AssetService>((ref) {
  return AssetService(ref.watch(dioClientProvider));
});
