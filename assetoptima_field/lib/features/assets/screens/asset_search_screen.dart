import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../core/utils/debouncer.dart';
import '../providers/asset_provider.dart';
import '../widgets/asset_card.dart';

class AssetSearchScreen extends ConsumerStatefulWidget {
  const AssetSearchScreen({super.key});

  @override
  ConsumerState<AssetSearchScreen> createState() =>
      _AssetSearchScreenState();
}

class _AssetSearchScreenState extends ConsumerState<AssetSearchScreen> {
  final _searchCtrl = TextEditingController();
  final _debouncer = Debouncer();
  String? _statusFilter;
  String? _searchQuery;

  @override
  void dispose() {
    _searchCtrl.dispose();
    _debouncer.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final params = AssetSearchParams(
      keyword: _searchQuery,
      status: _statusFilter,
    );
    final assetsAsync = ref.watch(assetSearchProvider(params));
    final cs = Theme.of(context).colorScheme;

    return Scaffold(
      appBar: AppBar(title: const Text('Search Assets')),
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.fromLTRB(16, 8, 16, 8),
            child: TextField(
              controller: _searchCtrl,
              decoration: InputDecoration(
                hintText: 'Search by name or asset code...',
                prefixIcon: const Icon(Icons.search),
                suffixIcon: _searchCtrl.text.isNotEmpty
                    ? IconButton(
                        icon: const Icon(Icons.clear),
                        onPressed: () {
                          _searchCtrl.clear();
                          setState(() => _searchQuery = null);
                        },
                      )
                    : null,
              ),
              onChanged: (v) {
                _debouncer(() => setState(() {
                      _searchQuery = v.isEmpty ? null : v;
                    }));
              },
            ),
          ),
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16),
            child: Row(
              children: [
                _FilterChip(
                  label: 'All',
                  selected: _statusFilter == null,
                  onTap: () =>
                      setState(() => _statusFilter = null),
                ),
                const SizedBox(width: 8),
                _FilterChip(
                  label: 'Available',
                  selected: _statusFilter == 'available',
                  onTap: () => setState(
                      () => _statusFilter = 'available'),
                ),
                const SizedBox(width: 8),
                _FilterChip(
                  label: 'Assigned',
                  selected: _statusFilter == 'assigned',
                  onTap: () => setState(
                      () => _statusFilter = 'assigned'),
                ),
                const SizedBox(width: 8),
                _FilterChip(
                  label: 'Maintenance',
                  selected: _statusFilter == 'maintenance',
                  onTap: () => setState(
                      () => _statusFilter = 'maintenance'),
                ),
              ],
            ),
          ),
          const SizedBox(height: 8),
          Expanded(
            child: assetsAsync.when(
              data: (assets) {
                if (assets.isEmpty) {
                  return Center(
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Icon(Icons.search_off_rounded,
                            size: 48, color: cs.onSurfaceVariant),
                        const SizedBox(height: 8),
                        Text('No assets found',
                            style: TextStyle(
                                color: cs.onSurfaceVariant)),
                      ],
                    ),
                  );
                }
                return ListView.separated(
                  padding: const EdgeInsets.symmetric(
                      horizontal: 16, vertical: 8),
                  itemCount: assets.length,
                  separatorBuilder: (_, __) =>
                      const SizedBox(height: 8),
                  itemBuilder: (_, i) => AssetCard(
                    asset: assets[i],
                    onTap: () =>
                        context.push('/assets/${assets[i].id}'),
                  ),
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
                    Text('Failed to load assets',
                        style: TextStyle(color: cs.error)),
                  ],
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _FilterChip extends StatelessWidget {
  final String label;
  final bool selected;
  final VoidCallback onTap;
  const _FilterChip({
    required this.label,
    required this.selected,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    return AnimatedContainer(
      duration: const Duration(milliseconds: 200),
      child: Material(
        color: selected
            ? cs.primary.withValues(alpha: 0.1)
            : Colors.transparent,
        borderRadius: BorderRadius.circular(20),
        child: InkWell(
          borderRadius: BorderRadius.circular(20),
          onTap: onTap,
          child: Padding(
            padding: const EdgeInsets.symmetric(
                horizontal: 14, vertical: 7),
            child: Text(
              label,
              style: TextStyle(
                color: selected
                    ? cs.primary
                    : cs.onSurfaceVariant,
                fontWeight:
                    selected ? FontWeight.w600 : FontWeight.normal,
                fontSize: 13,
              ),
            ),
          ),
        ),
      ),
    );
  }
}
