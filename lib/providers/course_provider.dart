import 'package:flutter/material.dart';
import '../models/course.dart';

class CourseProvider extends ChangeNotifier {
  List<Course> _availableCourses = [];
  TimeTable? _currentTimeTable;
  List<Course> _selectedCourses = [];

  List<Course> get availableCourses => _availableCourses;
  TimeTable? get currentTimeTable => _currentTimeTable;
  List<Course> get selectedCourses => _selectedCourses;

  void loadCourses() {
    // 데모 데이터 로드
    _availableCourses = _getDemoCourses();
    _currentTimeTable = TimeTable(
      courses: _selectedCourses,
      semester: 1,
      year: 2024,
    );
    notifyListeners();
  }

  void addCourseToTimeTable(Course course) {
    if (!_selectedCourses.contains(course) && !_hasConflict(course)) {
      _selectedCourses.add(course);
      _updateTimeTable();
      notifyListeners();
    }
  }

  void removeCourseFromTimeTable(Course course) {
    _selectedCourses.remove(course);
    _updateTimeTable();
    notifyListeners();
  }

  bool _hasConflict(Course newCourse) {
    if (_currentTimeTable == null) return false;
    return _currentTimeTable!.hasConflict(newCourse);
  }

  void _updateTimeTable() {
    _currentTimeTable = TimeTable(
      courses: _selectedCourses,
      semester: 1,
      year: 2024,
    );
  }

  List<Course> getCoursesForDay(int dayOfWeek) {
    if (_currentTimeTable == null) return [];
    return _currentTimeTable!.getCoursesForDay(dayOfWeek);
  }

  List<Course> _getDemoCourses() {
    return [
      Course(
        id: '1',
        code: 'CS101',
        name: '프로그래밍 기초',
        professor: '김교수',
        credits: 3,
        department: '컴퓨터공학과',
        times: [
          CourseTime(dayOfWeek: 1, startHour: 9, startMinute: 0, endHour: 10, endMinute: 30),
          CourseTime(dayOfWeek: 3, startHour: 9, startMinute: 0, endHour: 10, endMinute: 30),
        ],
        classroom: 'A101',
        maxStudents: 50,
        currentStudents: 35,
        description: '프로그래밍의 기초 개념을 학습합니다.',
      ),
      Course(
        id: '2',
        code: 'CS102',
        name: '자료구조',
        professor: '이교수',
        credits: 3,
        department: '컴퓨터공학과',
        times: [
          CourseTime(dayOfWeek: 2, startHour: 10, startMinute: 0, endHour: 11, endMinute: 30),
          CourseTime(dayOfWeek: 4, startHour: 10, startMinute: 0, endHour: 11, endMinute: 30),
        ],
        classroom: 'A102',
        maxStudents: 40,
        currentStudents: 40,
        description: '자료구조의 기본 개념과 구현을 학습합니다.',
      ),
      Course(
        id: '3',
        code: 'MATH201',
        name: '미적분학',
        professor: '박교수',
        credits: 3,
        department: '수학과',
        times: [
          CourseTime(dayOfWeek: 1, startHour: 11, startMinute: 0, endHour: 12, endMinute: 30),
          CourseTime(dayOfWeek: 3, startHour: 11, startMinute: 0, endHour: 12, endMinute: 30),
        ],
        classroom: 'B201',
        maxStudents: 60,
        currentStudents: 45,
        description: '미적분학의 기본 개념을 학습합니다.',
      ),
      Course(
        id: '4',
        code: 'ENG101',
        name: '영어회화',
        professor: 'Smith',
        credits: 2,
        department: '영어영문학과',
        times: [
          CourseTime(dayOfWeek: 2, startHour: 14, startMinute: 0, endHour: 15, endMinute: 30),
          CourseTime(dayOfWeek: 4, startHour: 14, startMinute: 0, endHour: 15, endMinute: 30),
        ],
        classroom: 'C101',
        maxStudents: 25,
        currentStudents: 20,
        description: '기본적인 영어 회화 능력을 기릅니다.',
      ),
      Course(
        id: '5',
        code: 'PHYS101',
        name: '일반물리학',
        professor: '최교수',
        credits: 3,
        department: '물리학과',
        times: [
          CourseTime(dayOfWeek: 1, startHour: 13, startMinute: 0, endHour: 14, endMinute: 30),
          CourseTime(dayOfWeek: 3, startHour: 13, startMinute: 0, endHour: 14, endMinute: 30),
        ],
        classroom: 'D101',
        maxStudents: 50,
        currentStudents: 30,
        description: '일반물리학의 기본 개념을 학습합니다.',
      ),
    ];
  }
}
