import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;
import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../models/assignment.dart';
import '../models/user_profile.dart';

/// 학교 홈페이지 자동화 서비스
/// Python 백엔드와 통신하여 실제 로그인 및 과제 정보 수집
class SchoolAutomationService {
  static SchoolAutomationService? _instance;
  static SchoolAutomationService get instance => _instance ??= SchoolAutomationService._();
  
  SchoolAutomationService._();
  
  // Python 백엔드 서버 URL (VM 서버용)
  static String get _backendUrl {
    if (kIsWeb) {
      return 'http://localhost:8080';
    } else if (Platform.isAndroid) {
      // Android에서는 VM의 외부 IP 사용 (VM IP 주소로 변경 필요)
      return 'http://34.64.123.45:8080'; // VM의 외부 IP로 변경
    } else {
      // iOS 시뮬레이터나 데스크톱에서는 VM IP 사용
      return 'http://34.64.123.45:8080'; // VM의 외부 IP로 변경
    }
  }
  
  // 사용자 자격 증명 저장
  Future<void> saveUserCredentials({
    required String university,
    required String username,
    required String password,
    required String studentId,
  }) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final credentials = {
        'university': university,
        'username': username,
        'password': password,
        'studentId': studentId,
        'savedAt': DateTime.now().toIso8601String(),
      };
      
      await prefs.setString('school_credentials', json.encode(credentials));
      debugPrint('학교 자격 증명 저장 완료');
    } catch (e) {
      debugPrint('자격 증명 저장 오류: $e');
    }
  }
  
  // 저장된 자격 증명 가져오기
  Future<Map<String, String>?> getUserCredentials() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final credentialsJson = prefs.getString('school_credentials');
      
      if (credentialsJson != null) {
        final credentials = json.decode(credentialsJson) as Map<String, dynamic>;
        return {
          'university': credentials['university'] as String,
          'username': credentials['username'] as String,
          'password': credentials['password'] as String,
          'studentId': credentials['studentId'] as String,
        };
      }
    } catch (e) {
      debugPrint('자격 증명 로드 오류: $e');
    }
    return null;
  }
  
  // 자격 증명 삭제
  Future<void> clearUserCredentials() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.remove('school_credentials');
      debugPrint('학교 자격 증명 삭제 완료');
    } catch (e) {
      debugPrint('자격 증명 삭제 오류: $e');
    }
  }
  
  // Python 백엔드에 로그인 요청
  Future<bool> loginToSchool() async {
    try {
      final credentials = await getUserCredentials();
      if (credentials == null) {
        debugPrint('저장된 자격 증명이 없습니다');
        return false;
      }
      
      final response = await http.post(
        Uri.parse('$_backendUrl/login'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'university': credentials['university'],
          'username': credentials['username'],
          'password': credentials['password'],
          'studentId': credentials['studentId'],
        }),
      ).timeout(const Duration(seconds: 30));
      
      if (response.statusCode == 200) {
        final result = json.decode(response.body);
        debugPrint('로그인 성공: ${result['message']}');
        return true;
      } else {
        debugPrint('로그인 실패: ${response.statusCode} - ${response.body}');
        return false;
      }
    } catch (e) {
      debugPrint('로그인 요청 오류: $e');
      return false;
    }
  }
  
  // 과제 정보 수집 요청
  Future<List<Assignment>> fetchAssignments() async {
    try {
      final response = await http.get(
        Uri.parse('$_backendUrl/assignments'),
        headers: {'Content-Type': 'application/json'},
      ).timeout(const Duration(seconds: 30));
      
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        final assignments = <Assignment>[];
        
        for (final item in data['assignments']) {
          assignments.add(Assignment.fromJson(item));
        }
        
        debugPrint('과제 정보 수집 완료: ${assignments.length}개');
        return assignments;
      } else {
        debugPrint('과제 정보 수집 실패: ${response.statusCode}');
        return [];
      }
    } catch (e) {
      debugPrint('과제 정보 수집 오류: $e');
      return [];
    }
  }

  // VM의 assignment.txt 파일 내용을 직접 가져오기
  Future<String> fetchRawAssignments() async {
    try {
      final response = await http.get(
        Uri.parse('$_backendUrl/assignments/raw'),
        headers: {'Content-Type': 'application/json'},
      ).timeout(const Duration(seconds: 30));
      
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        debugPrint('assignment.txt 파일 내용 조회 완료');
        return data['content'] ?? '파일 내용이 없습니다.';
      } else {
        debugPrint('assignment.txt 파일 조회 실패: ${response.statusCode}');
        return '파일 조회 실패';
      }
    } catch (e) {
      debugPrint('assignment.txt 파일 조회 오류: $e');
      return '파일 조회 오류: $e';
    }
  }
  
  // 새로운 과제 확인
  Future<List<Assignment>> checkNewAssignments() async {
    try {
      final response = await http.get(
        Uri.parse('$_backendUrl/assignments/new'),
        headers: {'Content-Type': 'application/json'},
      ).timeout(const Duration(seconds: 30));
      
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        final newAssignments = <Assignment>[];
        
        for (final item in data['new_assignments']) {
          newAssignments.add(Assignment.fromJson(item));
        }
        
        debugPrint('새로운 과제 확인 완료: ${newAssignments.length}개');
        return newAssignments;
      } else {
        debugPrint('새로운 과제 확인 실패: ${response.statusCode}');
        return [];
      }
    } catch (e) {
      debugPrint('새로운 과제 확인 오류: $e');
      return [];
    }
  }
  
  // 마감 임박 과제 확인
  Future<List<Assignment>> checkUpcomingDeadlines() async {
    try {
      final response = await http.get(
        Uri.parse('$_backendUrl/assignments/upcoming'),
        headers: {'Content-Type': 'application/json'},
      ).timeout(const Duration(seconds: 30));
      
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        final upcomingAssignments = <Assignment>[];
        
        for (final item in data['upcoming_assignments']) {
          upcomingAssignments.add(Assignment.fromJson(item));
        }
        
        debugPrint('마감 임박 과제 확인 완료: ${upcomingAssignments.length}개');
        return upcomingAssignments;
      } else {
        debugPrint('마감 임박 과제 확인 실패: ${response.statusCode}');
        return [];
      }
    } catch (e) {
      debugPrint('마감 임박 과제 확인 오류: $e');
      return [];
    }
  }
  
  // 백엔드 서버 상태 확인
  Future<bool> checkBackendStatus() async {
    try {
      final response = await http.get(
        Uri.parse('$_backendUrl/health'),
        headers: {'Content-Type': 'application/json'},
      ).timeout(const Duration(seconds: 10));
      
      return response.statusCode == 200;
    } catch (e) {
      debugPrint('백엔드 서버 상태 확인 오류: $e');
      return false;
    }
  }
  
  // 자동화 작업 시작
  Future<bool> startAutomation() async {
    try {
      final response = await http.post(
        Uri.parse('$_backendUrl/automation/start'),
        headers: {'Content-Type': 'application/json'},
      ).timeout(const Duration(seconds: 30));
      
      if (response.statusCode == 200) {
        debugPrint('자동화 작업 시작됨');
        return true;
      } else {
        debugPrint('자동화 작업 시작 실패: ${response.statusCode}');
        return false;
      }
    } catch (e) {
      debugPrint('자동화 작업 시작 오류: $e');
      return false;
    }
  }
  
  // 자동화 작업 중지
  Future<bool> stopAutomation() async {
    try {
      final response = await http.post(
        Uri.parse('$_backendUrl/automation/stop'),
        headers: {'Content-Type': 'application/json'},
      ).timeout(const Duration(seconds: 30));
      
      if (response.statusCode == 200) {
        debugPrint('자동화 작업 중지됨');
        return true;
      } else {
        debugPrint('자동화 작업 중지 실패: ${response.statusCode}');
        return false;
      }
    } catch (e) {
      debugPrint('자동화 작업 중지 오류: $e');
      return false;
    }
  }
  
  // 자동화 상태 확인
  Future<Map<String, dynamic>> getAutomationStatus() async {
    try {
      final response = await http.get(
        Uri.parse('$_backendUrl/automation/status'),
        headers: {'Content-Type': 'application/json'},
      ).timeout(const Duration(seconds: 10));
      
      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        return {'status': 'error', 'message': '상태 확인 실패'};
      }
    } catch (e) {
      debugPrint('자동화 상태 확인 오류: $e');
      return {'status': 'error', 'message': e.toString()};
    }
  }
  
  // 자동화 로그인 테스트
  Future<Map<String, dynamic>> testLogin(
    String university,
    String username,
    String password,
    String studentId,
  ) async {
    try {
      debugPrint('🧪 자동화 로그인 테스트 시작: $university');
      
      final response = await http.post(
        Uri.parse('$_backendUrl/automation/test-login'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'university': university,
          'username': username,
          'password': password,
          'student_id': studentId,
        }),
      ).timeout(const Duration(seconds: 60));
      
      if (response.statusCode == 200) {
        final result = json.decode(response.body);
        debugPrint('✅ 테스트 결과: ${result['message']}');
        return result;
      } else {
        final error = json.decode(response.body);
        debugPrint('❌ 테스트 실패: ${error['detail']}');
        return {
          'success': false,
          'message': error['detail'] ?? '테스트 실패',
          'login_status': '실패',
          'error': error['detail'] ?? '알 수 없는 오류'
        };
      }
    } catch (e) {
      debugPrint('❌ 테스트 오류: $e');
      return {
        'success': false,
        'message': '테스트 오류: $e',
        'login_status': '오류',
        'error': e.toString()
      };
    }
  }
  
  // 자동화 디버그 정보 조회
  Future<Map<String, dynamic>> getDebugInfo() async {
    try {
      final response = await http.get(
        Uri.parse('$_backendUrl/automation/debug'),
        headers: {'Content-Type': 'application/json'},
      ).timeout(const Duration(seconds: 10));
      
      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        return {'error': '디버그 정보 조회 실패'};
      }
    } catch (e) {
      debugPrint('디버그 정보 조회 오류: $e');
      return {'error': e.toString()};
    }
  }
}
