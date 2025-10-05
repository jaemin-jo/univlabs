class Course {
  final String id;
  final String code;
  final String name;
  final String professor;
  final int credits;
  final String department;
  final List<CourseTime> times;
  final String? classroom;
  final int maxStudents;
  final int currentStudents;
  final String? description;

  Course({
    required this.id,
    required this.code,
    required this.name,
    required this.professor,
    required this.credits,
    required this.department,
    required this.times,
    this.classroom,
    required this.maxStudents,
    required this.currentStudents,
    this.description,
  });

  bool get isFull => currentStudents >= maxStudents;
  int get remainingSpots => maxStudents - currentStudents;
}

class CourseTime {
  final int dayOfWeek; // 1-7 (월-일)
  final int startHour;
  final int startMinute;
  final int endHour;
  final int endMinute;

  CourseTime({
    required this.dayOfWeek,
    required this.startHour,
    required this.startMinute,
    required this.endHour,
    required this.endMinute,
  });

  String get dayName {
    const days = ['월', '화', '수', '목', '금', '토', '일'];
    return days[dayOfWeek - 1];
  }

  String get timeString {
    return '${startHour.toString().padLeft(2, '0')}:${startMinute.toString().padLeft(2, '0')} - ${endHour.toString().padLeft(2, '0')}:${endMinute.toString().padLeft(2, '0')}';
  }
}

class TimeTable {
  final List<Course> courses;
  final int semester;
  final int year;

  TimeTable({
    required this.courses,
    required this.semester,
    required this.year,
  });

  List<Course> getCoursesForDay(int dayOfWeek) {
    return courses.where((course) => 
      course.times.any((time) => time.dayOfWeek == dayOfWeek)
    ).toList();
  }

  bool hasConflict(Course newCourse) {
    for (final existingCourse in courses) {
      for (final existingTime in existingCourse.times) {
        for (final newTime in newCourse.times) {
          if (existingTime.dayOfWeek == newTime.dayOfWeek) {
            // 시간 겹침 체크
            final existingStart = existingTime.startHour * 60 + existingTime.startMinute;
            final existingEnd = existingTime.endHour * 60 + existingTime.endMinute;
            final newStart = newTime.startHour * 60 + newTime.startMinute;
            final newEnd = newTime.endHour * 60 + newTime.endMinute;
            
            if ((newStart < existingEnd && newEnd > existingStart)) {
              return true;
            }
          }
        }
      }
    }
    return false;
  }
}
