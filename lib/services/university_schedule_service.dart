import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;
import 'package:html/parser.dart' as html_parser;
import 'package:html/dom.dart' as html_dom;
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:flutter/foundation.dart';
import '../models/university.dart';
import '../models/schedule_item.dart';
import '../services/firebase_service.dart';

class UniversityScheduleService {
  static UniversityScheduleService? _instance;
  static UniversityScheduleService get instance => _instance ??= UniversityScheduleService._();
  
  UniversityScheduleService._();
  
  final FirebaseFirestore _firestore = FirebaseService.instance.firestore;
  
  // 대학교별 학사일정 크롤링
  Future<List<ScheduleItem>> crawlUniversitySchedule(University university) async {
    try {
      debugPrint('크롤링 시작: ${university.name}');
      
      final response = await http.get(
        Uri.parse(university.scheduleUrl),
        headers: {
          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
          'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
          'Accept-Language': 'ko-KR,ko;q=0.9,en;q=0.8',
          'Accept-Encoding': 'gzip, deflate, br',
          'Connection': 'keep-alive',
          'Upgrade-Insecure-Requests': '1',
        },
      ).timeout(const Duration(seconds: 30));
      
      if (response.statusCode == 200) {
        final document = html_parser.parse(response.body);
        final schedules = _parseScheduleFromHtml(document, university);
        
        // Firestore에 저장
        await _saveSchedulesToFirestore(schedules, university);
        
        debugPrint('${university.name} 학사일정 크롤링 완료: ${schedules.length}개 일정');
        return schedules;
      } else {
        debugPrint('${university.name} 크롤링 실패: ${response.statusCode}');
        return [];
      }
    } catch (e) {
      debugPrint('${university.name} 크롤링 오류: $e');
      return [];
    }
  }
  
  // HTML에서 학사일정 파싱
  List<ScheduleItem> _parseScheduleFromHtml(html_dom.Document document, University university) {
    final schedules = <ScheduleItem>[];
    
    try {
      // 연세대학교 미래캠퍼스 학사일정 파싱
      if (university.id == 'yonsei_mirae') {
        return _parseYonseiMiraeSchedule(document, university);
      }
      // 연세대학교 신촌캠퍼스 학사일정 파싱
      else if (university.id == 'yonsei') {
        return _parseYonseiSchedule(document, university);
      }
      // 서울대학교 학사일정 파싱
      else if (university.id == 'snu') {
        return _parseSNUSchedule(document, university);
      }
      // 기타 대학교 학사일정 파싱
      else {
        return _parseGenericSchedule(document, university);
      }
    } catch (e) {
      debugPrint('학사일정 파싱 오류: $e');
      return [];
    }
  }
  
  // 연세대학교 미래캠퍼스 학사일정 파싱
  List<ScheduleItem> _parseYonseiMiraeSchedule(html_dom.Document document, University university) {
    final schedules = <ScheduleItem>[];
    
    try {
      // 학사일정 테이블 찾기
      final scheduleElements = document.querySelectorAll('.schedule-item, .calendar-item, .event-item');
      
      for (final element in scheduleElements) {
        final title = element.querySelector('h3, .title, .event-title')?.text.trim() ?? '';
        final dateText = element.querySelector('.date, .schedule-date, .event-date')?.text.trim() ?? '';
        final description = element.querySelector('.description, .content, .detail')?.text.trim() ?? '';
        
        if (title.isNotEmpty && dateText.isNotEmpty) {
          final schedule = ScheduleItem(
            id: '${university.id}_${DateTime.now().millisecondsSinceEpoch}_${schedules.length}',
            title: title,
            description: description,
            startDate: _parseDate(dateText),
            endDate: _parseDate(dateText),
            type: ScheduleType.event,
            status: ScheduleStatus.upcoming,
            isAllDay: true,
            location: university.name,
            category: '학사일정',
            priority: _getPriorityFromTitle(title),
            isImportant: _isImportantSchedule(title),
            university: university.name,
            campus: university.campuses.first,
            createdAt: DateTime.now(),
            updatedAt: DateTime.now(),
          );
          
          schedules.add(schedule);
        }
      }
      
      // 월별 학사일정 파싱 (연세대 미래캠퍼스 특화)
      final monthlySchedules = document.querySelectorAll('.monthly-schedule, .calendar-month');
      for (final monthElement in monthlySchedules) {
        final monthText = monthElement.querySelector('h2, .month-title')?.text.trim() ?? '';
        final events = monthElement.querySelectorAll('.event, .schedule-item');
        
        for (final event in events) {
          final title = event.querySelector('.title, .event-title')?.text.trim() ?? '';
          final dateText = event.querySelector('.date, .day')?.text.trim() ?? '';
          final description = event.querySelector('.description, .content')?.text.trim() ?? '';
          
          if (title.isNotEmpty && dateText.isNotEmpty) {
            final fullDateText = '$monthText $dateText';
            final schedule = ScheduleItem(
              id: '${university.id}_${DateTime.now().millisecondsSinceEpoch}_${schedules.length}',
              title: title,
              description: description,
              startDate: _parseDate(fullDateText),
              endDate: _parseDate(fullDateText),
              type: ScheduleType.event,
              status: ScheduleStatus.upcoming,
              isAllDay: true,
              location: university.name,
              category: '학사일정',
              priority: _getPriorityFromTitle(title),
              isImportant: _isImportantSchedule(title),
              university: university.name,
              campus: university.campuses.first,
              createdAt: DateTime.now(),
              updatedAt: DateTime.now(),
            );
            
            schedules.add(schedule);
          }
        }
      }
    } catch (e) {
      debugPrint('연세대 미래캠퍼스 파싱 오류: $e');
    }
    
    return schedules;
  }
  
  // 연세대학교 신촌캠퍼스 학사일정 파싱
  List<ScheduleItem> _parseYonseiSchedule(html_dom.Document document, University university) {
    final schedules = <ScheduleItem>[];
    
    try {
      // 연세대 신촌캠퍼스 학사일정 테이블 파싱
      final tableRows = document.querySelectorAll('table tr, .schedule-table tr');
      
      for (final row in tableRows) {
        final cells = row.querySelectorAll('td, th');
        if (cells.length >= 2) {
          final dateText = cells[0].text.trim();
          final title = cells[1].text.trim();
          final description = cells.length > 2 ? cells[2].text.trim() : '';
          
          if (title.isNotEmpty && dateText.isNotEmpty) {
            final schedule = ScheduleItem(
              id: '${university.id}_${DateTime.now().millisecondsSinceEpoch}_${schedules.length}',
              title: title,
              description: description,
              startDate: _parseDate(dateText),
              endDate: _parseDate(dateText),
              type: ScheduleType.event,
              status: ScheduleStatus.upcoming,
              isAllDay: true,
              location: university.name,
              category: '학사일정',
              priority: _getPriorityFromTitle(title),
              isImportant: _isImportantSchedule(title),
              university: university.name,
              campus: university.campuses.first,
              createdAt: DateTime.now(),
              updatedAt: DateTime.now(),
            );
            
            schedules.add(schedule);
          }
        }
      }
    } catch (e) {
      debugPrint('연세대 신촌캠퍼스 파싱 오류: $e');
    }
    
    return schedules;
  }
  
  // 서울대학교 학사일정 파싱
  List<ScheduleItem> _parseSNUSchedule(html_dom.Document document, University university) {
    final schedules = <ScheduleItem>[];
    
    try {
      // 서울대학교 학사일정 파싱 로직
      final scheduleElements = document.querySelectorAll('.schedule-item, .notice-item, .event-item');
      
      for (final element in scheduleElements) {
        final title = element.querySelector('h3, .title, .notice-title')?.text.trim() ?? '';
        final dateText = element.querySelector('.date, .notice-date, .event-date')?.text.trim() ?? '';
        final description = element.querySelector('.content, .description, .notice-content')?.text.trim() ?? '';
        
        if (title.isNotEmpty && dateText.isNotEmpty) {
          final schedule = ScheduleItem(
            id: '${university.id}_${DateTime.now().millisecondsSinceEpoch}_${schedules.length}',
            title: title,
            description: description,
            startDate: _parseDate(dateText),
            endDate: _parseDate(dateText),
            type: ScheduleType.event,
            status: ScheduleStatus.upcoming,
            isAllDay: true,
            location: university.name,
            category: '학사일정',
            priority: _getPriorityFromTitle(title),
            isImportant: _isImportantSchedule(title),
            university: university.name,
            campus: university.campuses.first,
            createdAt: DateTime.now(),
            updatedAt: DateTime.now(),
          );
          
          schedules.add(schedule);
        }
      }
    } catch (e) {
      debugPrint('서울대학교 파싱 오류: $e');
    }
    
    return schedules;
  }
  
  // 일반적인 대학교 학사일정 파싱
  List<ScheduleItem> _parseGenericSchedule(html_dom.Document document, University university) {
    final schedules = <ScheduleItem>[];
    
    try {
      // 일반적인 학사일정 파싱 로직
      final scheduleElements = document.querySelectorAll('.schedule, .calendar, .event, .notice');
      
      for (final element in scheduleElements) {
        final title = element.querySelector('h1, h2, h3, .title, .subject')?.text.trim() ?? '';
        final dateText = element.querySelector('.date, .time, .schedule-date')?.text.trim() ?? '';
        final description = element.querySelector('.content, .description, .detail')?.text.trim() ?? '';
        
        if (title.isNotEmpty && dateText.isNotEmpty) {
          final schedule = ScheduleItem(
            id: '${university.id}_${DateTime.now().millisecondsSinceEpoch}_${schedules.length}',
            title: title,
            description: description,
            startDate: _parseDate(dateText),
            endDate: _parseDate(dateText),
            type: ScheduleType.event,
            status: ScheduleStatus.upcoming,
            isAllDay: true,
            location: university.name,
            category: '학사일정',
            priority: _getPriorityFromTitle(title),
            isImportant: _isImportantSchedule(title),
            university: university.name,
            campus: university.campuses.first,
            createdAt: DateTime.now(),
            updatedAt: DateTime.now(),
          );
          
          schedules.add(schedule);
        }
      }
    } catch (e) {
      debugPrint('일반 학사일정 파싱 오류: $e');
    }
    
    return schedules;
  }
  
  // 날짜 파싱
  DateTime _parseDate(String dateStr) {
    try {
      // 다양한 날짜 형식 처리
      final now = DateTime.now();
      
      if (dateStr.contains('년') && dateStr.contains('월') && dateStr.contains('일')) {
        // "2025년 1월 15일" 형식
        final regex = RegExp(r'(\d{4})년\s*(\d{1,2})월\s*(\d{1,2})일');
        final match = regex.firstMatch(dateStr);
        if (match != null) {
          return DateTime(
            int.parse(match.group(1)!),
            int.parse(match.group(2)!),
            int.parse(match.group(3)!),
          );
        }
      } else if (dateStr.contains('-')) {
        // "2025-01-15" 형식
        return DateTime.parse(dateStr);
      } else if (dateStr.contains('.')) {
        // "2025.01.15" 형식
        final parts = dateStr.split('.');
        if (parts.length >= 3) {
          return DateTime(
            int.parse(parts[0]),
            int.parse(parts[1]),
            int.parse(parts[2]),
          );
        }
      }
      
      // 파싱 실패 시 현재 시간 반환
      return now;
    } catch (e) {
      return DateTime.now();
    }
  }
  
  // 제목에서 우선순위 추출
  int _getPriorityFromTitle(String title) {
    final importantKeywords = ['중요', '긴급', '필수', '마감', '신청', '등록', '시험', '과제'];
    final normalKeywords = ['일반', '안내', '공지', '정보'];
    
    if (importantKeywords.any((keyword) => title.contains(keyword))) {
      return 3; // 높은 우선순위
    } else if (normalKeywords.any((keyword) => title.contains(keyword))) {
      return 1; // 낮은 우선순위
    } else {
      return 2; // 중간 우선순위
    }
  }
  
  // 중요 일정 판단
  bool _isImportantSchedule(String title) {
    final importantKeywords = [
      '중요', '긴급', '필수', '마감', '신청', '등록', '시험', '과제',
      '장학금', '기숙사', '수강신청', '졸업', '학사', '휴학', '복학'
    ];
    
    return importantKeywords.any((keyword) => title.contains(keyword));
  }
  
  // Firestore에 학사일정 저장
  Future<void> _saveSchedulesToFirestore(List<ScheduleItem> schedules, University university) async {
    try {
      final batch = _firestore.batch();
      
      for (final schedule in schedules) {
        final docRef = _firestore
            .collection('university_schedules')
            .doc('${university.id}_${schedule.id}');
        batch.set(docRef, schedule.toFirestore(), SetOptions(merge: true));
      }
      
      await batch.commit();
      debugPrint('${university.name} 학사일정 ${schedules.length}개 저장 완료');
    } catch (e) {
      debugPrint('학사일정 저장 오류: $e');
    }
  }
  
  // 특정 대학교의 학사일정 가져오기
  Stream<List<ScheduleItem>> getUniversitySchedules(String universityId) {
    return _firestore
        .collection('university_schedules')
        .where('university', isEqualTo: universityId)
        .orderBy('startDate', descending: false)
        .snapshots()
        .map((snapshot) {
      return snapshot.docs
          .map((doc) => ScheduleItem.fromFirestore(doc.data()))
          .toList();
    });
  }
  
  // 모든 대학교의 학사일정 가져오기
  Stream<List<ScheduleItem>> getAllUniversitySchedules() {
    return _firestore
        .collection('university_schedules')
        .orderBy('startDate', descending: false)
        .snapshots()
        .map((snapshot) {
      return snapshot.docs
          .map((doc) => ScheduleItem.fromFirestore(doc.data()))
          .toList();
    });
  }
  
  // 학사일정 새로고침
  Future<void> refreshAllUniversitySchedules() async {
    try {
      final universities = UniversityService.getAllUniversities();
      
      for (final university in universities) {
        await crawlUniversitySchedule(university);
        // 대학교 간 딜레이
        await Future.delayed(const Duration(seconds: 2));
      }
      
      debugPrint('모든 대학교 학사일정 새로고침 완료');
    } catch (e) {
      debugPrint('학사일정 새로고침 오류: $e');
    }
  }
}
