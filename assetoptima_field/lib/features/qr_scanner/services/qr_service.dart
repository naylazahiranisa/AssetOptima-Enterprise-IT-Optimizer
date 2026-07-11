import 'package:dio/dio.dart';
import '../../../core/config/api_endpoints.dart';
import '../../assets/models/asset.dart';

class QrService {
  QrService(this._dio);
  final Dio _dio;

  Future<Asset> lookupAsset(String qrCode) async {
    final res = await _dio.get(ApiEndpoints.assetByQr(qrCode));
    return Asset.fromJson(res.data['data'] as Map<String, dynamic>);
  }
}
