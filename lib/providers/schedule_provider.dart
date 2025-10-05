import 'package:flutter/material.dart';
import '../models/schedule_item.dart';
import '../services/notification_service.dart';
import '../services/schedule_service.dart';

class ScheduleProvider extends ChangeNotifier {
  List<ScheduleItem> _schedules = [];
  List<ScheduleItem> _upcomingSchedules = [];
  List<ScheduleItem> _importantSchedules = [];
  List<ScheduleItem> _urgentSchedules = [];
  
  final NotificationService _notificationService = NotificationService();

  List<ScheduleItem> get schedules => _schedules;
  List<ScheduleItem> get upcomingSchedules => _upcomingSchedules;
  List<ScheduleItem> get importantSchedules => _importantSchedules;
  List<ScheduleItem> get urgentSchedules => _urgentSchedules;

  void loadSchedules() async {
    try {
      // 실제 학사일정 데이터 로드
      _schedules = await ScheduleService.instance.getAllSchedules();
      
      // 더미 수강신청 데이터 추가
      _addDummyEnrollmentData();
      
      _updateFilteredSchedules();
      
      // 알림 서비스 초기화 및 알림 예약
      await _notificationService.initialize();
      await _notificationService.scheduleAllNotifications(_schedules);
      
      notifyListeners();
    } catch (e) {
      debugPrint('학사일정 로드 오류: $e');
      // 오류 발생 시 빈 리스트로 초기화
      _schedules = [];
      _updateFilteredSchedules();
      notifyListeners();
    }
  }

  void _addDummyEnrollmentData() {
    final now = DateTime.now();
    
    // 수강신청 더미 데이터 추가
    final enrollmentSchedule = ScheduleItem(
      id: 'dummy_enrollment_2025_1st',
      title: '2025학년도 1학기 수강신청',
      description: '2025학년도 1학기 수강신청 기간입니다. 포털에서 수강신청을 진행해주세요.',
      date: DateTime(2025, 2, 17, 9, 0), // 2025년 2월 17일 오전 9시
      endDate: DateTime(2025, 2, 21, 18, 0), // 2025년 2월 21일 오후 6시
      type: ScheduleType.enrollment,
      status: ScheduleStatus.upcoming,
      priority: SchedulePriority.high,
      location: '연세대학교 포털',
      isImportant: true,
      isUrgent: true,
      isAllDay: false,
      category: '수강신청',
      university: '연세대학교',
      semester: '2025-1',
      campus: '신촌캠퍼스',
      tags: ['수강신청', '1학기', '필수'],
      createdAt: DateTime.now(),
      updatedAt: DateTime.now(),
    );
    
    _schedules.add(enrollmentSchedule);
    
    debugPrint('더미 수강신청 데이터 추가 완료');
  }

  void addSchedule(ScheduleItem schedule) async {
    _schedules.add(schedule);
    _updateFilteredSchedules();
    
    // 새 일정에 대한 알림 예약
    await _notificationService.scheduleUrgentNotification(schedule);
    await _notificationService.scheduleFinalNotification(schedule);
    await _notificationService.scheduleTodayNotification(schedule);
    
    notifyListeners();
  }

  void updateSchedule(String id, ScheduleItem updatedSchedule) async {
    final index = _schedules.indexWhere((schedule) => schedule.id == id);
    if (index != -1) {
      // 기존 알림 취소
      await _notificationService.cancelScheduleNotifications(id);
      
      _schedules[index] = updatedSchedule;
      _updateFilteredSchedules();
      
      // 업데이트된 일정에 대한 새 알림 예약
      await _notificationService.scheduleUrgentNotification(updatedSchedule);
      await _notificationService.scheduleFinalNotification(updatedSchedule);
      await _notificationService.scheduleTodayNotification(updatedSchedule);
      
      notifyListeners();
    }
  }

  void deleteSchedule(String id) async {
    // 해당 일정의 알림 취소
    await _notificationService.cancelScheduleNotifications(id);
    
    _schedules.removeWhere((schedule) => schedule.id == id);
    _updateFilteredSchedules();
    notifyListeners();
  }

  void _updateFilteredSchedules() {
    final now = DateTime.now();
    final threeDaysLater = now.add(const Duration(days: 3));
    
    _upcomingSchedules = _schedules
        .where((schedule) => schedule.date.isAfter(now))
        .toList()
      ..sort((a, b) => a.date.compareTo(b.date));

    _importantSchedules = _schedules
        .where((schedule) => schedule.isImportant)
        .toList()
      ..sort((a, b) => a.date.compareTo(b.date));

    // 긴급한 일정: 3일 이내에 시작하는 중요한 일정
    _urgentSchedules = _schedules
        .where((schedule) => 
            schedule.isImportant && 
            schedule.date.isAfter(now) && 
            schedule.date.isBefore(threeDaysLater))
        .toList()
      ..sort((a, b) => a.date.compareTo(b.date));
  }

}
