import 'package:flutter/material.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'package:timezone/timezone.dart' as tz;
import 'package:timezone/data/latest.dart' as tz;
import 'package:flutter/foundation.dart';
import '../models/schedule_item.dart';

class NotificationService {
  static final NotificationService _instance = NotificationService._internal();
  factory NotificationService() => _instance;
  NotificationService._internal();

  final FlutterLocalNotificationsPlugin _notifications = FlutterLocalNotificationsPlugin();
  bool _isInitialized = false;

  // 알림 초기화
  Future<void> initialize() async {
    if (_isInitialized) return;

    // 타임존 초기화
    tz.initializeTimeZones();
    tz.setLocalLocation(tz.getLocation('Asia/Seoul'));

    // Android 초기화 설정
    const AndroidInitializationSettings androidSettings = AndroidInitializationSettings('@mipmap/ic_launcher');

    // iOS 초기화 설정
    const DarwinInitializationSettings iosSettings = DarwinInitializationSettings(
      requestAlertPermission: true,
      requestBadgePermission: true,
      requestSoundPermission: true,
    );

    // 초기화 설정
    const InitializationSettings settings = InitializationSettings(
      android: androidSettings,
      iOS: iosSettings,
    );

    // 알림 플러그인 초기화
    await _notifications.initialize(
      settings,
      onDidReceiveNotificationResponse: _onNotificationTapped,
    );

    // Android 알림 채널 생성
    await _createNotificationChannel();

    _isInitialized = true;
    debugPrint('NotificationService initialized');
  }

  // Android 알림 채널 생성
  Future<void> _createNotificationChannel() async {
    const AndroidNotificationChannel channel = AndroidNotificationChannel(
      'urgent_schedule_channel',
      '긴급 일정 알림',
      description: '마감 직전 일정에 대한 알림',
      importance: Importance.high,
      playSound: true,
      enableVibration: true,
    );

    await _notifications
        .resolvePlatformSpecificImplementation<AndroidFlutterLocalNotificationsPlugin>()
        ?.createNotificationChannel(channel);
  }

  // 알림 탭 처리
  void _onNotificationTapped(NotificationResponse response) {
    debugPrint('Notification tapped: ${response.payload}');
    // 여기서 앱의 특정 화면으로 이동하거나 추가 작업 수행
  }

  // 일정 마감 3시간 전 알림 예약
  Future<void> scheduleUrgentNotification(ScheduleItem schedule) async {
    if (!_isInitialized) {
      await initialize();
    }

    // 마감 시간에서 3시간 전 계산
    final notificationTime = schedule.endDate?.subtract(const Duration(hours: 3));
    
    // 현재 시간보다 미래인 경우에만 알림 예약
    if (notificationTime != null && notificationTime.isAfter(DateTime.now())) {
      await _notifications.zonedSchedule(
        schedule.id.hashCode, // 고유 ID
        '마감 임박! ${schedule.title}',
        '${schedule.title}의 마감이 3시간 후입니다.\n마감: ${_formatDateTime(schedule.endDate!)}',
        tz.TZDateTime.from(notificationTime, tz.local),
        const NotificationDetails(
          android: AndroidNotificationDetails(
            'urgent_schedule_channel',
            '긴급 일정 알림',
            channelDescription: '마감 직전 일정에 대한 알림',
            importance: Importance.high,
            priority: Priority.high,
            icon: '@mipmap/ic_launcher',
            color: Color(0xFFE53935), // 빨간색
            playSound: true,
            enableVibration: true,
            fullScreenIntent: true,
          ),
          iOS: DarwinNotificationDetails(
            presentAlert: true,
            presentBadge: true,
            presentSound: true,
            sound: 'default',
          ),
        ),
        androidScheduleMode: AndroidScheduleMode.exactAllowWhileIdle,
        uiLocalNotificationDateInterpretation: UILocalNotificationDateInterpretation.absoluteTime,
        payload: 'schedule_${schedule.id}',
      );

      debugPrint('Urgent notification scheduled for ${schedule.title} at ${_formatDateTime(notificationTime)}');
    }
  }

  // 일정 마감 1시간 전 알림 예약
  Future<void> scheduleFinalNotification(ScheduleItem schedule) async {
    if (!_isInitialized) {
      await initialize();
    }

    // 마감 시간에서 1시간 전 계산
    final notificationTime = schedule.endDate?.subtract(const Duration(hours: 1));
    
    // 현재 시간보다 미래인 경우에만 알림 예약
    if (notificationTime != null && notificationTime.isAfter(DateTime.now())) {
      await _notifications.zonedSchedule(
        schedule.id.hashCode + 1000, // 고유 ID (3시간 전 알림과 구분)
        '마감 1시간 전! ${schedule.title}',
        '${schedule.title}의 마감이 1시간 후입니다.\n마감: ${_formatDateTime(schedule.endDate!)}',
        tz.TZDateTime.from(notificationTime, tz.local),
        const NotificationDetails(
          android: AndroidNotificationDetails(
            'urgent_schedule_channel',
            '긴급 일정 알림',
            channelDescription: '마감 직전 일정에 대한 알림',
            importance: Importance.max,
            priority: Priority.max,
            icon: '@mipmap/ic_launcher',
            color: Color(0xFFD32F2F), // 더 진한 빨간색
            playSound: true,
            enableVibration: true,
            fullScreenIntent: true,
            category: AndroidNotificationCategory.alarm,
          ),
          iOS: DarwinNotificationDetails(
            presentAlert: true,
            presentBadge: true,
            presentSound: true,
            sound: 'default',
            interruptionLevel: InterruptionLevel.critical,
          ),
        ),
        androidScheduleMode: AndroidScheduleMode.exactAllowWhileIdle,
        uiLocalNotificationDateInterpretation: UILocalNotificationDateInterpretation.absoluteTime,
        payload: 'schedule_final_${schedule.id}',
      );

      debugPrint('Final notification scheduled for ${schedule.title} at ${_formatDateTime(notificationTime)}');
    }
  }

  // 일정 마감 당일 알림 예약
  Future<void> scheduleTodayNotification(ScheduleItem schedule) async {
    if (!_isInitialized) {
      await initialize();
    }

    // 마감 당일 오전 9시에 알림
    final today = DateTime.now();
    final notificationTime = DateTime(today.year, today.month, today.day, 9, 0);
    
    // 마감일이 오늘이고, 현재 시간이 오전 9시 이전인 경우에만 알림 예약
    if (schedule.endDate != null && 
        schedule.endDate!.day == today.day && 
        schedule.endDate!.month == today.month && 
        schedule.endDate!.year == today.year &&
        DateTime.now().isBefore(notificationTime)) {
      
      await _notifications.zonedSchedule(
        schedule.id.hashCode + 2000, // 고유 ID
        '오늘 마감! ${schedule.title}',
        '${schedule.title}이 오늘 마감됩니다.\n마감: ${_formatDateTime(schedule.endDate!)}',
        tz.TZDateTime.from(notificationTime, tz.local),
        const NotificationDetails(
          android: AndroidNotificationDetails(
            'urgent_schedule_channel',
            '긴급 일정 알림',
            channelDescription: '마감 직전 일정에 대한 알림',
            importance: Importance.high,
            priority: Priority.high,
            icon: '@mipmap/ic_launcher',
            color: Color(0xFFFF9800), // 주황색
            playSound: true,
            enableVibration: true,
          ),
          iOS: DarwinNotificationDetails(
            presentAlert: true,
            presentBadge: true,
            presentSound: true,
            sound: 'default',
          ),
        ),
        androidScheduleMode: AndroidScheduleMode.exactAllowWhileIdle,
        uiLocalNotificationDateInterpretation: UILocalNotificationDateInterpretation.absoluteTime,
        payload: 'schedule_today_${schedule.id}',
      );

      debugPrint('Today notification scheduled for ${schedule.title} at ${_formatDateTime(notificationTime)}');
    }
  }

  // 모든 일정에 대한 알림 예약
  Future<void> scheduleAllNotifications(List<ScheduleItem> schedules) async {
    if (!_isInitialized) {
      await initialize();
    }

    // 기존 알림 모두 취소
    await cancelAllNotifications();

    // 각 일정에 대해 알림 예약
    for (final schedule in schedules) {
      // 마감일이 미래인 일정만 처리
      if (schedule.endDate != null && schedule.endDate!.isAfter(DateTime.now())) {
        await scheduleUrgentNotification(schedule);
        await scheduleFinalNotification(schedule);
        await scheduleTodayNotification(schedule);
      }
    }

    debugPrint('All notifications scheduled for ${schedules.length} schedules');
  }

  // 특정 일정의 알림 취소
  Future<void> cancelScheduleNotifications(String scheduleId) async {
    await _notifications.cancel(scheduleId.hashCode);
    await _notifications.cancel(scheduleId.hashCode + 1000);
    await _notifications.cancel(scheduleId.hashCode + 2000);
    debugPrint('Notifications cancelled for schedule: $scheduleId');
  }

  // 모든 알림 취소
  Future<void> cancelAllNotifications() async {
    await _notifications.cancelAll();
    debugPrint('All notifications cancelled');
  }

  // 예약된 알림 목록 조회
  Future<List<PendingNotificationRequest>> getPendingNotifications() async {
    return await _notifications.pendingNotificationRequests();
  }

  // 즉시 알림 표시 (테스트용)
  Future<void> showImmediateNotification(String title, String body) async {
    if (!_isInitialized) {
      await initialize();
    }

    await _notifications.show(
      DateTime.now().millisecondsSinceEpoch ~/ 1000,
      title,
      body,
      const NotificationDetails(
        android: AndroidNotificationDetails(
          'urgent_schedule_channel',
          '긴급 일정 알림',
          channelDescription: '마감 직전 일정에 대한 알림',
          importance: Importance.high,
          priority: Priority.high,
          icon: '@mipmap/ic_launcher',
        ),
        iOS: DarwinNotificationDetails(
          presentAlert: true,
          presentBadge: true,
          presentSound: true,
        ),
      ),
    );
  }

  // 날짜 시간 포맷팅
  String _formatDateTime(DateTime dateTime) {
    return '${dateTime.year}년 ${dateTime.month}월 ${dateTime.day}일 ${dateTime.hour.toString().padLeft(2, '0')}:${dateTime.minute.toString().padLeft(2, '0')}';
  }
}

