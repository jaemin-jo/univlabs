class AcademicCalendar {
  final String university;
  final String semester;
  final List<MonthSchedule> schedule;

  AcademicCalendar({
    required this.university,
    required this.semester,
    required this.schedule,
  });

  factory AcademicCalendar.fromJson(Map<String, dynamic> json) {
    return AcademicCalendar(
      university: json['university'] ?? '',
      semester: json['semester'] ?? '',
      schedule: (json['schedule'] as List<dynamic>)
          .map((monthJson) => MonthSchedule.fromJson(monthJson))
          .toList(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'university': university,
      'semester': semester,
      'schedule': schedule.map((month) => month.toJson()).toList(),
    };
  }
}

class MonthSchedule {
  final String month;
  final String monthEn;
  final List<CalendarEvent> events;

  MonthSchedule({
    required this.month,
    required this.monthEn,
    required this.events,
  });

  factory MonthSchedule.fromJson(Map<String, dynamic> json) {
    return MonthSchedule(
      month: json['month'] ?? '',
      monthEn: json['month_en'] ?? '',
      events: (json['events'] as List<dynamic>)
          .map((eventJson) => CalendarEvent.fromJson(eventJson))
          .toList(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'month': month,
      'month_en': monthEn,
      'events': events.map((event) => event.toJson()).toList(),
    };
  }
}

class CalendarEvent {
  final String date;
  final String event;
  final String type;
  final String priority;

  CalendarEvent({
    required this.date,
    required this.event,
    required this.type,
    required this.priority,
  });

  factory CalendarEvent.fromJson(Map<String, dynamic> json) {
    return CalendarEvent(
      date: json['date'] ?? '',
      event: json['event'] ?? '',
      type: json['type'] ?? '',
      priority: json['priority'] ?? 'medium',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'date': date,
      'event': event,
      'type': type,
      'priority': priority,
    };
  }

  // 편의를 위한 getter들
  String get title => event;
  String get description => '';

  // 이벤트 타입별 색상 반환
  String get typeColor {
    switch (type) {
      case '수강신청':
        return '#FF6B6B'; // 빨간색
      case '등록':
        return '#FF8C00'; // 주황색
      case '시험':
        return '#E74C3C'; // 진한 빨간색
      case '휴일':
        return '#4ECDC4'; // 청록색
      case '개강':
        return '#45B7D1'; // 파란색
      case '졸업':
        return '#9B59B6'; // 보라색
      case '복학':
        return '#2ECC71'; // 초록색
      case '휴학':
        return '#F39C12'; // 주황색
      default:
        return '#95A5A6'; // 회색
    }
  }

  // 이벤트 타입별 아이콘 반환
  String get typeIcon {
    switch (type) {
      case '수강신청':
        return '📝';
      case '등록':
        return '📋';
      case '시험':
        return '📚';
      case '휴일':
        return '🎉';
      case '개강':
        return '🎓';
      case '졸업':
        return '🎓';
      case '복학':
        return '🔄';
      case '휴학':
        return '⏸️';
      default:
        return '📌';
    }
  }

  // 우선순위별 색상 반환
  String get priorityColor {
    switch (priority) {
      case 'high':
        return '#E74C3C'; // 빨간색
      case 'medium':
        return '#F39C12'; // 주황색
      case 'low':
        return '#95A5A6'; // 회색
      default:
        return '#95A5A6'; // 회색
    }
  }
}
