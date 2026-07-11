import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/utils/date_formatter.dart';
import '../providers/asset_provider.dart';
import '../widgets/status_badge.dart';

class AssetDetailScreen extends ConsumerWidget {
  final String assetId;
  const AssetDetailScreen({super.key, required this.assetId});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final detailAsync = ref.watch(assetDetailProvider(assetId));
    final cs = Theme.of(context).colorScheme;
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Asset Detail'),
        actions: [
          PopupMenuButton<String>(
            onSelected: (v) async {},
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(12),
            ),
            itemBuilder: (_) => [
              const PopupMenuItem(
                  value: 'assign', child: Text('Assign')),
              const PopupMenuItem(
                  value: 'return', child: Text('Return')),
              const PopupMenuItem(
                  value: 'maintenance',
                  child: Text('Maintenance')),
              const PopupMenuItem(
                  value: 'verify', child: Text('Verify')),
            ],
          ),
        ],
      ),
      body: detailAsync.when(
        data: (data) {
          final asset = data.asset;
          return ListView(
            padding: const EdgeInsets.all(16),
            children: [
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Expanded(
                            child: Text(
                              asset.name,
                              style: theme.textTheme.headlineSmall
                                  ?.copyWith(
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                          ),
                          StatusBadge(status: asset.status),
                        ],
                      ),
                      const SizedBox(height: 4),
                      Text(
                        asset.assetCode,
                        style: theme.textTheme.bodyMedium?.copyWith(
                          color: cs.onSurfaceVariant,
                        ),
                      ),
                      if (asset.description != null) ...[
                        const SizedBox(height: 12),
                        Text(asset.description!),
                      ],
                      const Divider(height: 28),
                      _InfoRow(
                          label: 'Serial Number',
                          value: asset.serialNumber),
                      _InfoRow(
                          label: 'Condition',
                          value: asset.condition),
                      _InfoRow(
                          label: 'Category ID',
                          value: asset.categoryId),
                      _InfoRow(
                          label: 'Employee ID',
                          value: asset.currentEmployeeId),
                      _InfoRow(
                          label: 'Location ID',
                          value: asset.locationId),
                      _InfoRow(
                          label: 'Purchase Date',
                          value: DateFormatter.date(
                              asset.purchaseDate)),
                      if (asset.purchasePrice != null)
                        _InfoRow(
                          label: 'Purchase Price',
                          value:
                              'Rp ${asset.purchasePrice!.toStringAsFixed(0)}',
                        ),
                      _InfoRow(
                        label: 'Created',
                        value: DateFormatter.dateTime(
                            asset.createdAt),
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 20),
              Text(
                'History',
                style: theme.textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.w600,
                ),
              ),
              const SizedBox(height: 12),
              if (data.history.isEmpty)
                Card(
                  child: Padding(
                    padding: const EdgeInsets.all(24),
                    child: Center(
                      child: Text(
                        'No history records',
                        style: TextStyle(
                            color: cs.onSurfaceVariant),
                      ),
                    ),
                  ),
                )
              else
                ...data.history.map((h) => Padding(
                      padding: const EdgeInsets.only(bottom: 8),
                      child: Card(
                        child: ListTile(
                          contentPadding:
                              const EdgeInsets.symmetric(
                                  horizontal: 16, vertical: 4),
                          leading: Container(
                            padding: const EdgeInsets.all(8),
                            decoration: BoxDecoration(
                              color: cs.primary
                                  .withValues(alpha: 0.1),
                              borderRadius:
                                  BorderRadius.circular(10),
                            ),
                            child: Icon(
                              Icons.history_rounded,
                              color: cs.primary,
                              size: 20,
                            ),
                          ),
                          title: Text(
                            h.actionLabel,
                            style: const TextStyle(
                                fontWeight: FontWeight.w600),
                          ),
                          subtitle: Text(h.notes ?? ''),
                          trailing: Text(
                            DateFormatter.relative(
                                h.performedAt),
                            style: theme.textTheme.bodySmall,
                          ),
                        ),
                      ),
                    )),
            ],
          );
        },
        loading: () =>
            const Center(child: CircularProgressIndicator()),
        error: (err, _) => Center(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(Icons.error_outline_rounded,
                  size: 48, color: cs.error),
              const SizedBox(height: 8),
              const Text('Failed to load asset details'),
            ],
          ),
        ),
      ),
    );
  }
}

class _InfoRow extends StatelessWidget {
  final String label;
  final String? value;
  const _InfoRow({required this.label, this.value});

  @override
  Widget build(BuildContext context) {
    if (value == null) return const SizedBox.shrink();
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 5),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 120,
            child: Text(
              label,
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    fontWeight: FontWeight.w500,
                    color: Theme.of(context).colorScheme.onSurfaceVariant,
                  ),
            ),
          ),
          Expanded(
            child: Text(
              value!,
              style: Theme.of(context).textTheme.bodyMedium,
            ),
          ),
        ],
      ),
    );
  }
}
