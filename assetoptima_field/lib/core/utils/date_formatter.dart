import 'package:intl/intl.dart';

class DateFormatter {
  DateFormatter._();

  static final _dateFormat = DateFormat('dd MMM yyyy');
  static final _dateTimeFormat = DateFormat('dd MMM yyyy HH:mm');
  static final _timeFormat = DateFormat('HH:mm');

  static String date(DateTime? dt) =>
      dt != null ? _dateFormat.format(dt) : '-';

  static String dateTime(DateTime? dt) =>
      dt != null ? _dateTimeFormat.format(dt) : '-';

  static String time(DateTime? dt) =>
      dt != null ? _timeFormat.format(dt) : '-';

  static String relative(DateTime? dt) {
    if (dt == null) return '-';
    final now = DateTime.now();
    final diff = now.difference(dt);
    if (diff.inMinutes < 1) return 'Just now';
    if (diff.inMinutes < 60) return '${diff.inMinutes}m ago';
    if (diff.inHours < 24) return '${diff.inHours}h ago';
    if (diff.inDays < 7) return '${diff.inDays}d ago';
    return _dateFormat.format(dt);
  }
}
