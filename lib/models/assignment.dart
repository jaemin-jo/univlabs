class Assignment {
  final String course;
  final String activity;
  final String type;
  final String status;
  final String url;

  Assignment({
    required this.course,
    required this.activity,
    required this.type,
    required this.status,
    required this.url,
  });

  factory Assignment.fromJson(Map<String, dynamic> json) {
    return Assignment(
      course: json['course'] ?? '',
      activity: json['activity'] ?? '',
      type: json['type'] ?? '',
      status: json['status'] ?? '',
      url: json['url'] ?? '',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'course': course,
      'activity': activity,
      'type': type,
      'status': status,
      'url': url,
    };
  }

  bool get isCompleted => status.contains('✅');
  bool get isIncomplete => status.contains('❌');
}