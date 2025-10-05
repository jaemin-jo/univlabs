import 'dart:convert';
import 'package:flutter/services.dart';
import '../models/academic_calendar.dart';

class AcademicCalendarService {
  static AcademicCalendar? _cachedCalendar;
  static DateTime? _lastLoadTime;

  /// 학사일정 데이터 로드 (캐시 사용)
  static Future<AcademicCalendar> loadAcademicCalendar() async {
    // 캐시가 있고 1시간 이내라면 캐시 사용
    if (_cachedCalendar != null && 
        _lastLoadTime != null && 
        DateTime.now().difference(_lastLoadTime!).inHours < 1) {
      return _cachedCalendar!;
    }

    try {
      // JSON 파일에서 데이터 로드
      final String jsonString = await rootBundle.loadString('lib/data/academic_calendar.json');
      final Map<String, dynamic> jsonData = json.decode(jsonString);
      
      _cachedCalendar = AcademicCalendar.fromJson(jsonData);
      _lastLoadTime = DateTime.now();
      
      return _cachedCalendar!;
    } catch (e) {
      throw Exception('학사일정 데이터 로드 실패: $e');
    }
  }

  /// 특정 월의 일정 조회
  static Future<List<CalendarEvent>> getEventsForMonth(String month) async {
    final calendar = await loadAcademicCalendar();
    final monthSchedule = calendar.schedule.firstWhere(
      (schedule) => schedule.month == month,
      orElse: () => MonthSchedule(month: month, events: []),
    );
    return monthSchedule.events;
  }

  /// 오늘 날짜의 일정 조회
  static Future<List<CalendarEvent>> getTodayEvents() async {
    final now = DateTime.now();
    final month = '${now.month}월';
    final events = await getEventsForMonth(month);
    
    // 오늘 날짜와 일치하는 이벤트 필터링
    return events.where((event) {
      // 날짜 파싱 (예: "15(금)" -> 15)
      final dateMatch = RegExp(r'(\d+)').firstMatch(event.date);
      if (dateMatch != null) {
        final day = int.parse(dateMatch.group(1)!);
        return day == now.day;
      }
      return false;
    }).toList();
  }

  /// 이번 주 일정 조회
  static Future<List<CalendarEvent>> getThisWeekEvents() async {
    final now = DateTime.now();
    final startOfWeek = now.subtract(Duration(days: now.weekday - 1));
    final endOfWeek = startOfWeek.add(Duration(days: 6));
    
    final allEvents = <CalendarEvent>[];
    
    // 현재 월과 다음 월의 이벤트 조회
    final currentMonth = '${now.month}월';
    final nextMonth = '${now.month + 1}월';
    
    allEvents.addAll(await getEventsForMonth(currentMonth));
    if (now.month < 12) {
      allEvents.addAll(await getEventsForMonth(nextMonth));
    }
    
    // 이번 주 범위 내의 이벤트 필터링
    return allEvents.where((event) {
      final dateMatch = RegExp(r'(\d+)').firstMatch(event.date);
      if (dateMatch != null) {
        final day = int.parse(dateMatch.group(1)!);
        final eventDate = DateTime(now.year, now.month, day);
        return eventDate.isAfter(startOfWeek.subtract(Duration(days: 1))) &&
               eventDate.isBefore(endOfWeek.add(Duration(days: 1)));
      }
      return false;
    }).toList();
  }

  /// 특정 타입의 일정 조회
  static Future<List<CalendarEvent>> getEventsByType(String type) async {
    final calendar = await loadAcademicCalendar();
    final allEvents = <CalendarEvent>[];
    
    for (final monthSchedule in calendar.schedule) {
      allEvents.addAll(monthSchedule.events.where((event) => event.type == type));
    }
    
    return allEvents;
  }

  /// 시험 일정만 조회
  static Future<List<CalendarEvent>> getExamSchedule() async {
    return getEventsByType('시험');
  }

  /// 휴일만 조회
  static Future<List<CalendarEvent>> getHolidays() async {
    return getEventsByType('휴일');
  }

  /// 수강신청 일정만 조회
  static Future<List<CalendarEvent>> getRegistrationSchedule() async {
    return getEventsByType('수강신청');
  }

  /// 캐시 클리어
  static void clearCache() {
    _cachedCalendar = null;
    _lastLoadTime = null;
  }

  /// 전체 학사일정 데이터 반환
  static Future<AcademicCalendar> getFullCalendar() async {
    return loadAcademicCalendar();
  }
}
