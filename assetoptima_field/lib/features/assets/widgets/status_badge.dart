import 'package:flutter/material.dart';

class StatusBadge extends StatelessWidget {
  final String status;
  final double fontSize;
  const StatusBadge({super.key, required this.status, this.fontSize = 12});

  @override
  Widget build(BuildContext context) {
    final (color, label) = switch (status.toLowerCase()) {
      'available' || 'active' => (const Color(0xFF16A34A), 'Available'),
      'assigned' || 'in_use' => (const Color(0xFF2563EB), 'Assigned'),
      'maintenance' || 'repair' => (const Color(0xFFF59E0B), 'Maintenance'),
      'retired' || 'disposed' => (const Color(0xFF94A3B8), 'Retired'),
      'lost' || 'stolen' => (const Color(0xFFDC2626), 'Lost'),
      'pending' => (const Color(0xFF7C3AED), 'Pending'),
      _ => (const Color(0xFF94A3B8), status),
    };

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(6),
      ),
      child: Text(
        label,
        style: TextStyle(
          color: color,
          fontSize: fontSize,
          fontWeight: FontWeight.w600,
        ),
      ),
    );
  }
}
