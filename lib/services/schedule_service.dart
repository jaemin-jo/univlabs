import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../models/schedule_item.dart';

/// 학사일정 서비스
/// 1학기와 2학기 학사일정을 통합 관리
class ScheduleService {
  static ScheduleService? _instance;
  static ScheduleService get instance => _instance ??= ScheduleService._();
  
  ScheduleService._();
  
  // 1학기와 2학기 학사일정 데이터
  static const String _scheduleData = '''
  {
    "university": "연세대학교",
    "semester": "2025-1학기, 2025-2학기",
    "schedule": [
      {
        "month": "2월",
        "events": [
          {"date": "03 (월)", "event": "휴학 접수 시작", "type": "휴학", "priority": "high"},
          {"date": "12 (수) ~ 18 (화)", "event": "2025-1학기 수강신청", "type": "수강신청", "priority": "high"},
          {"date": "21 (금) ~ 27 (목)", "event": "2025-1학기 등록", "type": "등록", "priority": "high"},
          {"date": "23 (일)", "event": "졸업예배", "type": "졸업", "priority": "medium"},
          {"date": "24 (월)", "event": "복학 접수 마감, 학위수여식", "type": "복학", "priority": "high"}
        ]
      },
      {
        "month": "3월",
        "events": [
          {"date": "01 (토)", "event": "삼일절", "type": "휴일", "priority": "medium"},
          {"date": "03 (월)", "event": "대체휴일", "type": "휴일", "priority": "medium"},
          {"date": "04 (화)", "event": "개강", "type": "개강", "priority": "high"},
          {"date": "06 (목)", "event": "교무위원회", "type": "행사", "priority": "low"},
          {"date": "06 (목) ~ 10 (월)", "event": "수강신청 확인 및 변경", "type": "수강신청", "priority": "high"},
          {"date": "12 (수) ~ 14 (금)", "event": "2025-1학기 추가등록", "type": "등록", "priority": "high"},
          {"date": "17 (월)", "event": "미등록자 일반휴학 접수 마감", "type": "휴학", "priority": "high"},
          {"date": "17 (월) ~ 21 (금)", "event": "조기졸업 신청", "type": "졸업", "priority": "medium"}
        ]
      },
      {
        "month": "4월",
        "events": [
          {"date": "03 (목)", "event": "교무위원회", "type": "행사", "priority": "low"},
          {"date": "09 (수)", "event": "학기 1/3선", "type": "학사", "priority": "medium"},
          {"date": "14 (월) ~ 19 (토)", "event": "고난주간", "type": "행사", "priority": "low"},
          {"date": "15 (화) ~ 17 (목)", "event": "수강철회", "type": "수강신청", "priority": "high"},
          {"date": "20 (일)", "event": "부활절", "type": "휴일", "priority": "medium"},
          {"date": "22 (화) ~ 28 (월)", "event": "중간시험", "type": "시험", "priority": "high"},
          {"date": "28 (월) ~ 02 (금)", "event": "2025-2학기 캠퍼스내 소속변경 신청", "type": "전과", "priority": "medium"},
          {"date": "29 (화) ~ 01 (목)", "event": "S/U평가 신청", "type": "성적", "priority": "high"}
        ]
      },
      {
        "month": "5월",
        "events": [
          {"date": "01 (목)", "event": "근로자의날", "type": "휴일", "priority": "medium"},
          {"date": "05 (월)", "event": "부처님 오신 날, 어린이날", "type": "휴일", "priority": "medium"},
          {"date": "06 (화)", "event": "대체휴일", "type": "휴일", "priority": "medium"},
          {"date": "07 (수)", "event": "은퇴교수의 날", "type": "행사", "priority": "low"},
          {"date": "08 (목)", "event": "교무위원회", "type": "행사", "priority": "low"},
          {"date": "10 (토)", "event": "창립기념일", "type": "휴일", "priority": "medium"},
          {"date": "16 (금)", "event": "학기 2/3선, 일반휴학 접수 마감", "type": "휴학", "priority": "high"},
          {"date": "19 (월)", "event": "질병휴학 접수시작", "type": "휴학", "priority": "medium"}
        ]
      },
      {
        "month": "6월",
        "events": [
          {"date": "03 (화)", "event": "질병휴학 접수마감", "type": "휴학", "priority": "high"},
          {"date": "05 (목)", "event": "교무위원회", "type": "행사", "priority": "low"},
          {"date": "06 (금)", "event": "현충일", "type": "휴일", "priority": "medium"},
          {"date": "08 (일)", "event": "성령강림절", "type": "휴일", "priority": "medium"},
          {"date": "10 (화) ~ 16 (월)", "event": "자율학습 및 보충수업 기간", "type": "학사", "priority": "medium"},
          {"date": "17 (화) ~ 23 (월)", "event": "학기말시험", "type": "시험", "priority": "high"},
          {"date": "24 (화)", "event": "여름방학 시작", "type": "방학", "priority": "medium"},
          {"date": "24 (화) ~ 30 (월)", "event": "2025-2학기 캠퍼스내 복수전공 · 연계전공 · 융합심화전공 신청", "type": "전공", "priority": "high"},
          {"date": "30 (월)", "event": "2025-1학기 성적제출 마감, 여름계절제 수업시작", "type": "성적", "priority": "high"}
        ]
      },
      {
        "month": "7월",
        "events": [
          {"date": "14 (월)", "event": "복학 접수 시작", "type": "복학", "priority": "high"},
          {"date": "21 (월)", "event": "여름계절제 수업종료", "type": "계절제", "priority": "medium"}
        ]
      },
      {
        "month": "8월",
        "events": [
          {"date": "01 (금)", "event": "휴학 접수 시작", "type": "휴학", "priority": "high"},
          {"date": "11 (월) ~ 18 (월)", "event": "2025-2학기 수강신청", "type": "수강신청", "priority": "high"},
          {"date": "15 (금)", "event": "광복절", "type": "휴일", "priority": "medium"},
          {"date": "22 (금) ~ 28 (목)", "event": "2025-2학기 등록", "type": "등록", "priority": "high"},
          {"date": "25 (월)", "event": "복학 접수 마감", "type": "복학", "priority": "high"},
          {"date": "29 (금)", "event": "학위수여식", "type": "졸업", "priority": "medium"}
        ]
      },
      {
        "month": "9월",
        "events": [
          {"date": "01 (월)", "event": "개강", "type": "개강", "priority": "high"},
          {"date": "03 (수) ~ 05 (금)", "event": "수강신청 확인 및 변경", "type": "수강신청", "priority": "high"},
          {"date": "04 (목)", "event": "교무위원회", "type": "행사", "priority": "low"},
          {"date": "09 (화) ~ 11 (목)", "event": "2025-2학기 추가등록", "type": "등록", "priority": "high"},
          {"date": "15 (월)", "event": "미등록자 일반휴학 접수 마감", "type": "휴학", "priority": "high"},
          {"date": "15 (월) ~ 19 (금)", "event": "조기졸업 신청", "type": "졸업", "priority": "medium"}
        ]
      },
      {
        "month": "10월",
        "events": [
          {"date": "02 (목)", "event": "교무위원회", "type": "행사", "priority": "low"},
          {"date": "03 (금)", "event": "개천절", "type": "휴일", "priority": "medium"},
          {"date": "05 (일) ~ 07 (화)", "event": "추석연휴", "type": "휴일", "priority": "high"},
          {"date": "08 (수)", "event": "학기 1/3선, 대체휴일", "type": "학사", "priority": "medium"},
          {"date": "09 (목)", "event": "한글날", "type": "휴일", "priority": "medium"},
          {"date": "13 (월) ~ 15 (수)", "event": "수강철회", "type": "수강신청", "priority": "high"},
          {"date": "20 (월) ~ 25 (토)", "event": "중간시험", "type": "시험", "priority": "high"},
          {"date": "27 (월) ~ 31 (금)", "event": "2026-1학기 캠퍼스내 소속변경 신청", "type": "전과", "priority": "medium"},
          {"date": "27 (월) ~ 29 (수)", "event": "S/U평가 신청", "type": "성적", "priority": "high"}
        ]
      },
      {
        "month": "11월",
        "events": [
          {"date": "06 (목)", "event": "교무위원회", "type": "행사", "priority": "low"},
          {"date": "13 (목)", "event": "학기 2/3선, 일반휴학 접수 마감", "type": "휴학", "priority": "high"},
          {"date": "14 (금)", "event": "질병휴학 접수시작", "type": "휴학", "priority": "medium"},
          {"date": "16 (일)", "event": "추수감사절", "type": "휴일", "priority": "medium"},
          {"date": "24 (월) ~ 28 (금)", "event": "캠퍼스간 소속변경", "type": "전과", "priority": "medium"}
        ]
      },
      {
        "month": "12월",
        "events": [
          {"date": "01 (월)", "event": "질병휴학 접수마감", "type": "휴학", "priority": "high"},
          {"date": "04 (목)", "event": "성탄절예배", "type": "행사", "priority": "low"},
          {"date": "08 (월) ~ 13 (토)", "event": "자율학습 및 보충수업 기간", "type": "학사", "priority": "medium"},
          {"date": "15 (월) ~ 20 (토)", "event": "학기말 시험", "type": "시험", "priority": "high"},
          {"date": "16 (화)", "event": "교무위원회", "type": "행사", "priority": "low"},
          {"date": "22 (월)", "event": "겨울방학시작", "type": "방학", "priority": "medium"},
          {"date": "22 (월) ~ 29 (월)", "event": "2026-1학기 캠퍼스내 복수전공 · 연계전공 · 융합심화전공 신청", "type": "전공", "priority": "high"},
          {"date": "25 (목)", "event": "성탄절", "type": "휴일", "priority": "medium"},
          {"date": "28 (일)", "event": "성적제출 마감", "type": "성적", "priority": "high"},
          {"date": "29 (월)", "event": "겨울계절제 수업 시작", "type": "계절제", "priority": "medium"}
        ]
      },
      {
        "month": "1월",
        "events": [
          {"date": "01 (목)", "event": "신정", "type": "휴일", "priority": "medium"},
          {"date": "12 (월)", "event": "복학 접수 시작", "type": "복학", "priority": "high"},
          {"date": "20 (화)", "event": "겨울계절제 수업 종료", "type": "계절제", "priority": "medium"}
        ]
      },
      {
        "month": "2월",
        "events": [
          {"date": "02 (월)", "event": "휴학 접수 시작", "type": "휴학", "priority": "high"},
          {"date": "09 (월) ~ 13 (금)", "event": "2026-1학기 수강신청", "type": "수강신청", "priority": "high"},
          {"date": "16 (월) ~ 18 (수)", "event": "설연휴", "type": "휴일", "priority": "high"},
          {"date": "22 (일)", "event": "졸업예배", "type": "졸업", "priority": "medium"},
          {"date": "23 (월)", "event": "학위수여식", "type": "졸업", "priority": "medium"},
          {"date": "23 (월)", "event": "복학 접수 마감", "type": "복학", "priority": "high"}
        ]
      }
    ]
  }
  ''';
  
  // 모든 학사일정 가져오기
  Future<List<ScheduleItem>> getAllSchedules() async {
    try {
      final List<ScheduleItem> schedules = [];
      final data = json.decode(_scheduleData);
      
      for (final monthData in data['schedule']) {
        final month = monthData['month'] as String;
        
        for (final event in monthData['events']) {
          final schedule = ScheduleItem(
            id: 'yonsei_${schedules.length}',
            title: event['event'] as String,
            description: '${month} ${event['date']} - ${event['event']}',
            date: _parseScheduleDate(event['date'] as String, month),
            type: _parseScheduleType(event['type'] as String),
            status: ScheduleStatus.upcoming,
            priority: _parsePriority(event['priority'] as String),
            isImportant: _isImportantSchedule(event['event'] as String),
            tags: _generateScheduleTags(event['event'] as String, event['type'] as String),
            university: '연세대학교',
            semester: _getSemester(month),
          );
          
          schedules.add(schedule);
        }
      }
      
      debugPrint('전체 학사일정 ${schedules.length}개 로드 완료');
      return schedules;
      
    } catch (e) {
      debugPrint('학사일정 로드 오류: $e');
      return [];
    }
  }
  
  // 다가오는 학사일정 가져오기
  Future<List<ScheduleItem>> getUpcomingSchedules({int days = 30}) async {
    try {
      final allSchedules = await getAllSchedules();
      final now = DateTime.now();
      final targetDate = now.add(Duration(days: days));
      
      final upcomingSchedules = allSchedules.where((schedule) {
        final scheduleDate = schedule.date;
        return scheduleDate.isAfter(now) && scheduleDate.isBefore(targetDate);
      }).toList();
      
      // 날짜순으로 정렬
      upcomingSchedules.sort((a, b) => a.date.compareTo(b.date));
      
      debugPrint('다가오는 학사일정 ${upcomingSchedules.length}개 반환');
      return upcomingSchedules;
      
    } catch (e) {
      debugPrint('다가오는 학사일정 조회 오류: $e');
      return [];
    }
  }
  
  // 중요한 학사일정 가져오기
  Future<List<ScheduleItem>> getImportantSchedules() async {
    try {
      final allSchedules = await getAllSchedules();
      final importantSchedules = allSchedules.where((schedule) => schedule.isImportant).toList();
      
      debugPrint('중요 학사일정 ${importantSchedules.length}개 반환');
      return importantSchedules;
      
    } catch (e) {
      debugPrint('중요 학사일정 조회 오류: $e');
      return [];
    }
  }
  
  // 타입별 학사일정 가져오기
  Future<List<ScheduleItem>> getSchedulesByType(ScheduleType type) async {
    try {
      final allSchedules = await getAllSchedules();
      final filteredSchedules = allSchedules.where((schedule) => schedule.type == type).toList();
      
      debugPrint('${type.name} 학사일정 ${filteredSchedules.length}개 반환');
      return filteredSchedules;
      
    } catch (e) {
      debugPrint('타입별 학사일정 조회 오류: $e');
      return [];
    }
  }
  
  // 학기 판단
  String _getSemester(String month) {
    final monthNum = _getMonthNumber(month);
    if (monthNum >= 2 && monthNum <= 7) {
      return '2025-1학기';
    } else {
      return '2025-2학기';
    }
  }
  
  // 월 번호 가져오기
  int _getMonthNumber(String month) {
    final monthMapping = {
      '1월': 1, '2월': 2, '3월': 3, '4월': 4, '5월': 5, '6월': 6,
      '7월': 7, '8월': 8, '9월': 9, '10월': 10, '11월': 11, '12월': 12
    };
    return monthMapping[month] ?? 1;
  }
  
  // 학사일정 날짜 파싱
  DateTime _parseScheduleDate(String dateStr, String month) {
    try {
      final currentYear = 2025;
      final monthNum = _getMonthNumber(month);
      
      // 날짜 문자열에서 일 추출
      String dayStr;
      if (dateStr.contains('~')) {
        // 기간인 경우 시작일 사용
        final startDate = dateStr.split('~')[0].trim();
        dayStr = startDate.split('(')[0].trim();
      } else {
        dayStr = dateStr.split('(')[0].trim();
      }
      
      final day = int.parse(dayStr);
      
      // 2026년 1-2월은 2026년으로 처리
      final year = (monthNum <= 2) ? 2026 : currentYear;
      
      return DateTime(year, monthNum, day);
      
    } catch (e) {
      debugPrint('날짜 파싱 오류: $e');
      return DateTime.now();
    }
  }
  
  // 학사일정 타입 파싱
  ScheduleType _parseScheduleType(String typeStr) {
    switch (typeStr) {
      case '수강신청':
        return ScheduleType.enrollment;
      case '등록':
        return ScheduleType.registration;
      case '시험':
        return ScheduleType.exam;
      case '휴학':
        return ScheduleType.leave;
      case '복학':
        return ScheduleType.return_;
      case '졸업':
        return ScheduleType.graduation;
      case '휴일':
        return ScheduleType.holiday;
      case '전과':
        return ScheduleType.transfer;
      case '성적':
        return ScheduleType.grade;
      case '개강':
        return ScheduleType.semesterStart;
      case '방학':
        return ScheduleType.vacation;
      case '계절제':
        return ScheduleType.summerWinter;
      case '전공':
        return ScheduleType.doubleMajor;
      case '학사':
        return ScheduleType.general;
      case '행사':
        return ScheduleType.event;
      default:
        return ScheduleType.general;
    }
  }
  
  // 우선순위 파싱
  SchedulePriority _parsePriority(String priorityStr) {
    switch (priorityStr) {
      case 'high':
        return SchedulePriority.high;
      case 'medium':
        return SchedulePriority.medium;
      case 'low':
        return SchedulePriority.low;
      default:
        return SchedulePriority.medium;
    }
  }
  
  // 중요한 학사일정 여부 판단
  bool _isImportantSchedule(String eventName) {
    final importantKeywords = [
      '수강신청', '등록', '개강', '종강', '시험', '성적', '졸업', '휴학', '복학',
      '추가등록', '수강철회', '중간시험', '학기말', '방학', '계절제'
    ];
    
    return importantKeywords.any((keyword) => eventName.contains(keyword));
  }
  
  // 학사일정 태그 생성
  List<String> _generateScheduleTags(String eventName, String eventType) {
    final tags = <String>[];
    
    // 이벤트 타입 기반 태그
    final typeTags = {
      '수강신청': ['수강신청', '등록'],
      '등록': ['등록', '수강신청'],
      '시험': ['시험', '성적'],
      '휴학': ['휴학', '복학'],
      '복학': ['복학', '휴학'],
      '졸업': ['졸업', '학위'],
      '휴일': ['휴일', '공휴일'],
      '전과': ['전과', '전공'],
      '성적': ['성적', '시험'],
    };
    
    if (typeTags.containsKey(eventType)) {
      tags.addAll(typeTags[eventType]!);
    }
    
    // 이벤트명 기반 태그
    if (eventName.contains('수강신청')) tags.add('수강신청');
    if (eventName.contains('등록')) tags.add('등록');
    if (eventName.contains('시험')) tags.add('시험');
    if (eventName.contains('휴학')) tags.add('휴학');
    if (eventName.contains('복학')) tags.add('복학');
    if (eventName.contains('졸업')) tags.add('졸업');
    
    // 기본 태그
    if (tags.isEmpty) {
      tags.add('학사일정');
    }
    
    return tags.toSet().toList(); // 중복 제거
  }
}