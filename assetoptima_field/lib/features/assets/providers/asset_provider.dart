import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/asset.dart';
import '../models/asset_history.dart';
import '../services/asset_service.dart';

final assetSearchProvider =
    FutureProvider.family<List<Asset>, AssetSearchParams>((ref, params) {
  final service = ref.read(assetServiceProvider);
  return service.listAssets(
    page: params.page,
    perPage: 20,
    keyword: params.keyword,
    status: params.status,
  );
});

class AssetSearchParams {
  final int page;
  final String? keyword;
  final String? status;
  const AssetSearchParams({
    this.page = 1,
    this.keyword,
    this.status,
  });

  AssetSearchParams copyWith({
    int? page,
    String? keyword,
    String? status,
  }) =>
      AssetSearchParams(
        page: page ?? this.page,
        keyword: keyword ?? this.keyword,
        status: status ?? this.status,
      );

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is AssetSearchParams &&
          runtimeType == other.runtimeType &&
          page == other.page &&
          keyword == other.keyword &&
          status == other.status;

  @override
  int get hashCode => Object.hash(page, keyword, status);
}

final assetDetailProvider =
    FutureProvider.family<AssetDetailData, String>((ref, assetId) async {
  final service = ref.read(assetServiceProvider);
  final results = await Future.wait([
    service.getAsset(assetId),
    service.getHistory(assetId),
  ]);
  return AssetDetailData(
    asset: results[0] as Asset,
    history: results[1] as List<AssetHistory>,
  );
});

class AssetDetailData {
  final Asset asset;
  final List<AssetHistory> history;
  const AssetDetailData({required this.asset, required this.history});
}
