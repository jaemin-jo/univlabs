class ScheduleItem {
  final String id;
  final String title;
  final String description;
  final DateTime date; // 단일 날짜 (startDate 대신)
  final DateTime? endDate; // 기간인 경우 종료일
  final ScheduleType type;
  final ScheduleStatus status;
  final SchedulePriority priority; // 우선순위 열거형
  final String? location;
  final bool isImportant;
  final bool isUrgent;
  final bool isAllDay;
  final String? category;
  final String? university;
  final String? semester; // 학기 정보
  final String? campus;
  final List<String> tags; // 태그 목록
  final DateTime? createdAt;
  final DateTime? updatedAt;

  ScheduleItem({
    required this.id,
    required this.title,
    required this.description,
    required this.date,
    this.endDate,
    required this.type,
    required this.status,
    required this.priority,
    this.location,
    this.isImportant = false,
    this.isUrgent = false,
    this.isAllDay = false,
    this.category,
    this.university,
    this.semester,
    this.campus,
    this.tags = const [],
    this.createdAt,
    this.updatedAt,
  });
}

enum ScheduleType {
  enrollment, // 수강신청
  registration, // 등록
  exam, // 시험
  leave, // 휴학
  return_, // 복학
  graduation, // 졸업
  holiday, // 휴일
  transfer, // 전과
  grade, // 성적
  semesterStart, // 개강
  vacation, // 방학
  summerWinter, // 계절제
  general, // 일반
  dormitoryApplication, // 기숙사신청
  courseChange, // 수강변경
  scheduleCheck, // 시간표 점검
  doubleMajor, // 이중전공 신청
  contest, // 공모전/대회
  assignment, // 과제
  event, // 행사
  other, // 기타
}

enum ScheduleStatus {
  upcoming, // 예정
  inProgress, // 진행중
  completed, // 완료
  cancelled, // 취소
  overdue, // 지연
}

enum SchedulePriority {
  high, // 높음
  medium, // 보통
  low, // 낮음
}

extension ScheduleTypeExtension on ScheduleType {
  String get displayName {
    switch (this) {
      case ScheduleType.enrollment:
        return '수강신청';
      case ScheduleType.registration:
        return '등록';
      case ScheduleType.exam:
        return '시험';
      case ScheduleType.leave:
        return '휴학';
      case ScheduleType.return_:
        return '복학';
      case ScheduleType.graduation:
        return '졸업';
      case ScheduleType.holiday:
        return '휴일';
      case ScheduleType.transfer:
        return '전과';
      case ScheduleType.grade:
        return '성적';
      case ScheduleType.semesterStart:
        return '개강';
      case ScheduleType.vacation:
        return '방학';
      case ScheduleType.summerWinter:
        return '계절제';
      case ScheduleType.general:
        return '일반';
      case ScheduleType.dormitoryApplication:
        return '기숙사신청';
      case ScheduleType.courseChange:
        return '수강변경';
      case ScheduleType.scheduleCheck:
        return '시간표 점검';
      case ScheduleType.doubleMajor:
        return '이중전공 신청';
      case ScheduleType.contest:
        return '공모전/대회';
      case ScheduleType.assignment:
        return '과제';
      case ScheduleType.event:
        return '행사';
      case ScheduleType.other:
        return '기타';
    }
  }

  String get icon {
    switch (this) {
      case ScheduleType.enrollment:
        return '📚';
      case ScheduleType.registration:
        return '📝';
      case ScheduleType.exam:
        return '📝';
      case ScheduleType.leave:
        return '⏸️';
      case ScheduleType.return_:
        return '▶️';
      case ScheduleType.graduation:
        return '🎓';
      case ScheduleType.holiday:
        return '🎉';
      case ScheduleType.transfer:
        return '🔄';
      case ScheduleType.grade:
        return '📊';
      case ScheduleType.semesterStart:
        return '🚀';
      case ScheduleType.vacation:
        return '🏖️';
      case ScheduleType.summerWinter:
        return '❄️';
      case ScheduleType.general:
        return '📌';
      case ScheduleType.dormitoryApplication:
        return '🏠';
      case ScheduleType.courseChange:
        return '🔄';
      case ScheduleType.scheduleCheck:
        return '📅';
      case ScheduleType.doubleMajor:
        return '🎓';
      case ScheduleType.contest:
        return '🏆';
      case ScheduleType.assignment:
        return '📋';
      case ScheduleType.event:
        return '🎉';
      case ScheduleType.other:
        return '📌';
    }
  }
}

// Firestore 변환 메서드
extension ScheduleItemFirestore on ScheduleItem {
  Map<String, dynamic> toFirestore() {
    return {
      'id': id,
      'title': title,
      'description': description,
      'date': date.toIso8601String(),
      'endDate': endDate?.toIso8601String(),
      'type': type.name,
      'status': status.name,
      'priority': priority.name,
      'location': location,
      'isImportant': isImportant,
      'isUrgent': isUrgent,
      'isAllDay': isAllDay,
      'category': category,
      'university': university,
      'semester': semester,
      'campus': campus,
      'tags': tags,
      'createdAt': createdAt?.toIso8601String(),
      'updatedAt': updatedAt?.toIso8601String(),
    };
  }

  static ScheduleItem fromFirestore(Map<String, dynamic> data) {
    return ScheduleItem(
      id: data['id'] as String,
      title: data['title'] as String,
      description: data['description'] as String,
      date: DateTime.parse(data['date'] as String),
      endDate: data['endDate'] != null ? DateTime.parse(data['endDate'] as String) : null,
      type: ScheduleType.values.firstWhere(
        (e) => e.name == data['type'],
        orElse: () => ScheduleType.other,
      ),
      status: ScheduleStatus.values.firstWhere(
        (e) => e.name == data['status'],
        orElse: () => ScheduleStatus.upcoming,
      ),
      priority: SchedulePriority.values.firstWhere(
        (e) => e.name == data['priority'],
        orElse: () => SchedulePriority.medium,
      ),
      location: data['location'] as String?,
      isImportant: data['isImportant'] as bool? ?? false,
      isUrgent: data['isUrgent'] as bool? ?? false,
      isAllDay: data['isAllDay'] as bool? ?? false,
      category: data['category'] as String?,
      university: data['university'] as String?,
      semester: data['semester'] as String?,
      campus: data['campus'] as String?,
      tags: List<String>.from(data['tags'] ?? []),
      createdAt: data['createdAt'] != null 
          ? DateTime.parse(data['createdAt'] as String)
          : null,
      updatedAt: data['updatedAt'] != null 
          ? DateTime.parse(data['updatedAt'] as String)
          : null,
    );
  }
}
