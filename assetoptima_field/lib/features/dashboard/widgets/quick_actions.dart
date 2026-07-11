import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

class QuickActions extends StatelessWidget {
  const QuickActions({super.key});

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    final actions = [
      _Action(
        label: 'Scan QR',
        icon: Icons.qr_code_scanner_rounded,
        color: cs.primary,
        route: '/scanner',
      ),
      _Action(
        label: 'Search',
        icon: Icons.search_rounded,
        color: cs.secondary,
        route: '/assets',
      ),
      _Action(
        label: 'Alerts',
        icon: Icons.notifications_rounded,
        color: const Color(0xFFF59E0B),
        route: '/notifications',
      ),
      _Action(
        label: 'Settings',
        icon: Icons.settings_rounded,
        color: const Color(0xFF64748B),
        route: '/settings',
      ),
    ];

    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Quick Actions',
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.w600,
                ),
          ),
          const SizedBox(height: 12),
          Row(
            children: actions.map((a) {
              final isLeft = a == actions.first;
              final isRight = a == actions.last;
              return Expanded(
                child: Padding(
                  padding: EdgeInsets.only(
                    left: isLeft ? 0 : 6,
                    right: isRight ? 0 : 6,
                  ),
                  child: _ActionButton(action: a),
                ),
              );
            }).toList(),
          ),
        ],
      ),
    );
  }
}

class _Action {
  final String label;
  final IconData icon;
  final Color color;
  final String route;
  const _Action({
    required this.label,
    required this.icon,
    required this.color,
    required this.route,
  });
}

class _ActionButton extends StatelessWidget {
  final _Action action;
  const _ActionButton({required this.action});

  @override
  Widget build(BuildContext context) {
    return Card(
      clipBehavior: Clip.antiAlias,
      child: InkWell(
        onTap: () => context.push(action.route),
        child: Padding(
          padding: const EdgeInsets.symmetric(vertical: 16),
          child: Column(
            children: [
              Icon(action.icon, color: action.color, size: 26),
              const SizedBox(height: 8),
              Text(
                action.label,
                style: Theme.of(context).textTheme.labelSmall?.copyWith(
                      color: action.color,
                      fontWeight: FontWeight.w600,
                    ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
