// import 'package:workmanager/workmanager.dart';
import 'package:flutter/foundation.dart';
import 'web_crawling_service.dart';
import 'firebase_service.dart';

class BackgroundTaskService {
  static const String _crawlingTaskName = 'webCrawlingTask';
  static const String _crawlingTaskId = 'web_crawling_task';
  
  static Future<void> initialize() async {
    // Workmanager 임시 비활성화
    debugPrint('Background task service initialized (workmanager disabled)');
  }
  
  // 10분마다 웹 크롤링 작업 예약 (임시 비활성화)
  static Future<void> scheduleWebCrawling() async {
    debugPrint('Web crawling task scheduling disabled (workmanager not available)');
  }
  
  // 웹 크롤링 작업 취소 (임시 비활성화)
  static Future<void> cancelWebCrawling() async {
    debugPrint('Web crawling task cancellation disabled (workmanager not available)');
  }
  
  // 모든 백그라운드 작업 취소 (임시 비활성화)
  static Future<void> cancelAllTasks() async {
    debugPrint('All background task cancellation disabled (workmanager not available)');
  }
}

// 백그라운드 작업 콜백 함수 (임시 비활성화)
// @pragma('vm:entry-point')
// void callbackDispatcher() {
//   // Workmanager 비활성화로 인해 주석 처리
// }

// 웹 크롤링 실행 (수동 실행용)
Future<void> executeWebCrawling() async {
  try {
    // Firebase 초기화
    await FirebaseService.instance.initialize();
    
    // 웹 크롤링 실행
    await WebCrawlingService.instance.crawlAllSites();
    
    debugPrint('Manual web crawling completed successfully');
  } catch (e) {
    debugPrint('Manual web crawling failed: $e');
  }
}
