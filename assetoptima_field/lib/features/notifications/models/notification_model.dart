import 'package:flutter/material.dart';

class AppNotification {
  final String id;
  final String title;
  final String? message;
  final String category;
  final String? priority;
  final String? status;
  final String? referenceId;
  final String? readAt;
  final DateTime createdAt;

  const AppNotification({
    required this.id,
    required this.title,
    this.message,
    required this.category,
    this.priority,
    this.status,
    this.referenceId,
    this.readAt,
    required this.createdAt,
  });

  bool get isRead => status == 'read' || readAt != null;

  factory AppNotification.fromJson(Map<String, dynamic> json) =>
      AppNotification(
        id: json['id'] as String,
        title: json['title'] as String,
        message: json['message'] as String?,
        category: json['category'] as String? ?? 'general',
        priority: json['priority'] as String?,
        status: json['status'] as String?,
        referenceId: json['reference_id'] as String?,
        readAt: json['read_at'] as String?,
        createdAt: DateTime.parse(json['created_at'] as String),
      );

  IconData get icon {
    switch (category) {
      case 'assignment':
        return Icons.person_add_outlined;
      case 'maintenance':
        return Icons.build_outlined;
      case 'verification':
        return Icons.verified_outlined;
      case 'warning':
        return Icons.warning_amber_outlined;
      default:
        return Icons.notifications_outlined;
    }
  }
}
