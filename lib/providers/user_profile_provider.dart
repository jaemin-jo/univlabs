import 'package:flutter/material.dart';
import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';
import '../models/user_profile.dart';
import '../models/university.dart';
import '../services/profile_service.dart';
import '../services/firebase_service.dart';

class UserProfileProvider extends ChangeNotifier {
  UserProfile? _userProfile;
  University? _selectedUniversity;
  bool _isLoading = false;
  String? _error;

  UserProfile? get userProfile => _userProfile;
  University? get selectedUniversity => _selectedUniversity;
  bool get isLoading => _isLoading;
  String? get error => _error;

  UserProfileProvider() {
    _loadUserProfile();
    _setupFirebaseListener();
  }

  // 사용자 프로필 로드
  Future<void> _loadUserProfile() async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      // SharedPreferences에서 로컬 프로필 로드
      final prefs = await SharedPreferences.getInstance();
      final profileData = prefs.getString('user_profile');
      
      if (profileData != null) {
        _userProfile = UserProfile.fromJson(json.decode(profileData));
      } else {
        // 기본 프로필 생성
        _userProfile = UserProfile(
          uid: DateTime.now().millisecondsSinceEpoch.toString(),
          name: '',
          studentId: '',
          major: '',
          email: '',
          createdAt: DateTime.now(),
          updatedAt: DateTime.now(),
        );
      }

      // Firebase에서 최신 프로필 동기화
      await _syncWithFirebase();
      
      // 사용자 프로필이 있을 때만 대학교 정보 로드
      if (_userProfile != null && _userProfile!.uid.isNotEmpty) {
        await _loadSelectedUniversity();
      }
    } catch (e) {
      _error = e.toString();
      debugPrint('Error loading user profile: $e');
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  // Firebase와 동기화
  Future<void> _syncWithFirebase() async {
    try {
      final firebaseProfile = await ProfileService.instance.getUserProfile();
      if (firebaseProfile != null) {
        _userProfile = firebaseProfile;
        await _saveToLocal();
      }
    } catch (e) {
      debugPrint('Error syncing with Firebase: $e');
    }
  }

  // 로컬에 저장
  Future<void> _saveToLocal() async {
    if (_userProfile != null) {
      final prefs = await SharedPreferences.getInstance();
      final profileJson = json.encode(_userProfile!.toJson());
      await prefs.setString('user_profile', profileJson);
    }
  }

  // 사용자 프로필 업데이트
  Future<void> updateUserProfile(UserProfile profile) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      _userProfile = profile.copyWith(updatedAt: DateTime.now());
      
      // 로컬에 저장
      await _saveToLocal();
      
      // Firebase에 저장
      await ProfileService.instance.saveUserProfile(_userProfile!);
      
      debugPrint('✅ Firebase에 개인정보 저장 완료:');
      debugPrint('   - UID: ${_userProfile!.uid}');
      debugPrint('   - 이름: ${_userProfile!.name}');
      debugPrint('   - 학번: ${_userProfile!.studentId}');
      debugPrint('   - 전공: ${_userProfile!.major}');
      debugPrint('   - 대학교: ${_userProfile!.university}');
      debugPrint('   - 이메일: ${_userProfile!.email}');
      
      notifyListeners();
    } catch (e) {
      _error = e.toString();
      debugPrint('❌ Firebase 개인정보 저장 오류: $e');
      notifyListeners();
    } finally {
      _isLoading = false;
    }
  }

  // 사용자 프로필 저장 (온보딩용)
  Future<void> saveUserProfile(UserProfile profile) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      _userProfile = profile;
      
      // 로컬에 저장
      await _saveToLocal();
      
      // Firebase에 저장
      await ProfileService.instance.saveUserProfile(_userProfile!);
      
      notifyListeners();
    } catch (e) {
      _error = e.toString();
      debugPrint('Error saving user profile: $e');
      notifyListeners();
    } finally {
      _isLoading = false;
    }
  }

  // 관심사 태그 업데이트
  Future<void> updateInterestTags(List<String> tags) async {
    if (_userProfile == null) return;

    try {
      final updatedProfile = _userProfile!.copyWith(
        interestTags: tags,
        updatedAt: DateTime.now(),
      );
      
      await updateUserProfile(updatedProfile);
      
      // Firebase에도 별도로 업데이트
      await ProfileService.instance.updateInterestTags(tags);
    } catch (e) {
      _error = e.toString();
      debugPrint('Error updating interest tags: $e');
      notifyListeners();
    }
  }

  // 구독 채널 업데이트
  Future<void> updateSubscribedChannels(List<String> channels) async {
    if (_userProfile == null) return;

    try {
      final updatedProfile = _userProfile!.copyWith(
        subscribedChannels: channels,
        updatedAt: DateTime.now(),
      );
      
      await updateUserProfile(updatedProfile);
      
      // Firebase에도 별도로 업데이트
      await ProfileService.instance.updateSubscribedChannels(channels);
    } catch (e) {
      _error = e.toString();
      debugPrint('Error updating subscribed channels: $e');
      notifyListeners();
    }
  }

  // 프로필 이미지 업로드
  Future<String?> uploadProfileImage(String imagePath) async {
    if (_userProfile == null) return null;

    try {
      final imageUrl = await ProfileService.instance.uploadProfileImage(imagePath);
      
      if (imageUrl != null) {
        final updatedProfile = _userProfile!.copyWith(
          profileImageUrl: imageUrl,
          updatedAt: DateTime.now(),
        );
        
        await updateUserProfile(updatedProfile);
      }
      
      return imageUrl;
    } catch (e) {
      _error = e.toString();
      debugPrint('Error uploading profile image: $e');
      notifyListeners();
      return null;
    }
  }

  // 사용자 프로필 삭제
  Future<void> deleteUserProfile() async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      await ProfileService.instance.deleteUserProfile();
      
      // 로컬 데이터 삭제
      final prefs = await SharedPreferences.getInstance();
      await prefs.remove('user_profile');
      
      _userProfile = null;
      notifyListeners();
    } catch (e) {
      _error = e.toString();
      debugPrint('Error deleting user profile: $e');
      notifyListeners();
    } finally {
      _isLoading = false;
    }
  }

  // 프로필 새로고침
  Future<void> refreshProfile() async {
    await _loadUserProfile();
  }

  // 에러 클리어
  void clearError() {
    _error = null;
    notifyListeners();
  }

  // 프로필 요약 정보 가져오기
  Map<String, dynamic> getProfileSummary() {
    if (_userProfile == null) return {};
    
    return {
      'name': _userProfile!.name,
      'studentId': _userProfile!.studentId,
      'major': _userProfile!.major,
      'university': _userProfile!.university,
      'department': _userProfile!.department,
      'grade': _userProfile!.grade,
      'interestTagsCount': _userProfile!.interestTags.length,
      'subscribedChannelsCount': _userProfile!.subscribedChannels.length,
    };
  }

  // 학과별 공지사항 필터링을 위한 학과 정보
  String getDepartmentForFiltering() {
    if (_userProfile == null) return '';
    
    // department가 있으면 사용, 없으면 major 사용
    return _userProfile!.department ?? _userProfile!.major;
  }

  // 학년별 공지사항 필터링을 위한 학년 정보
  int? getGradeForFiltering() {
    return _userProfile?.grade;
  }

  // 관심사 태그 기반 공지사항 필터링
  List<String> getInterestTagsForFiltering() {
    return _userProfile?.interestTags ?? [];
  }

  // 프로필 존재 여부 확인
  bool get hasProfile {
    return _userProfile != null && 
           _userProfile!.name.isNotEmpty && 
           _userProfile!.studentId.isNotEmpty;
  }

  // 사용자 요약 정보
  String get userSummary {
    if (_userProfile == null) return '프로필 없음';
    
    final parts = <String>[];
    if (_userProfile!.major.isNotEmpty) {
      parts.add(_userProfile!.major);
    }
    if (_userProfile!.grade != null) {
      parts.add('${_userProfile!.grade}학년');
    }
    if (_userProfile!.university?.isNotEmpty == true) {
      parts.add(_userProfile!.university!);
    }
    
    return parts.isNotEmpty ? parts.join(' ') : '프로필 정보 없음';
  }

  // 모든 관련 키워드 (학과, 전공, 관심사 등)
  List<String> get allRelevantKeywords {
    if (_userProfile == null) return [];
    
    final keywords = <String>[];
    
    if (_userProfile!.major.isNotEmpty) {
      keywords.add(_userProfile!.major);
    }
    if (_userProfile!.department != null && _userProfile!.department!.isNotEmpty) {
      keywords.add(_userProfile!.department!);
    }
    if (_userProfile!.university?.isNotEmpty == true) {
      keywords.add(_userProfile!.university!);
    }
    
    // 관심사 태그 추가
    keywords.addAll(_userProfile!.interestTags);
    
    return keywords;
  }

  // 학년별 키워드
  List<String> get gradeKeywords {
    if (_userProfile?.grade == null) return [];
    
    final grade = _userProfile!.grade!;
    final keywords = <String>[];
    
    // 학년별 일반적인 키워드
    switch (grade) {
      case 1:
        keywords.addAll(['신입생', '1학년', 'OT', '새내기', '입학']);
        break;
      case 2:
        keywords.addAll(['2학년', '전공기초', '전공선택']);
        break;
      case 3:
        keywords.addAll(['3학년', '전공심화', '인턴십', '취업준비']);
        break;
      case 4:
        keywords.addAll(['4학년', '졸업', '졸업논문', '취업', '대학원']);
        break;
    }
    
    return keywords;
  }

  // 선택된 대학교 정보 로드
  Future<void> _loadSelectedUniversity() async {
    if (_userProfile?.uid == null || _userProfile!.uid.isEmpty) return;
    
    try {
      _selectedUniversity = await FirebaseService.instance.getUserUniversity(_userProfile!.uid);
      notifyListeners();
    } catch (e) {
      debugPrint('Error loading selected university: $e');
    }
  }
  
  // 대학교 변경
  Future<void> updateUniversity(University university) async {
    if (_userProfile == null) return;
    
    _isLoading = true;
    _error = null;
    notifyListeners();
    
    try {
      // Firebase에 대학교 정보 업데이트
      await FirebaseService.instance.updateUserUniversity(_userProfile!.uid, university);
      
      // 로컬 프로필 업데이트 (university 필드만 업데이트)
      final updatedProfile = _userProfile!.copyWith(
        university: university.name,
        updatedAt: DateTime.now(),
      );
      
      // 프로필 업데이트 (Firebase에 저장)
      await FirebaseService.instance.saveUserProfile(updatedProfile);
      
      // 로컬 상태 업데이트
      _userProfile = updatedProfile;
      _selectedUniversity = university;
      
      debugPrint('대학교 변경 완료: ${university.name}');
    } catch (e) {
      _error = e.toString();
      debugPrint('Error updating university: $e');
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }
  
  // 현재 대학교 정보 가져오기
  String get currentUniversityName {
    return _selectedUniversity?.name ?? _userProfile?.university ?? '대학교 미선택';
  }
  
  // 현재 대학교 캠퍼스 정보
  String get currentCampus {
    if (_selectedUniversity?.campuses.isNotEmpty == true) {
      return _selectedUniversity!.campuses.first;
    }
    return '';
  }
  
  // 대학교 정보 새로고침
  Future<void> refreshUniversityInfo() async {
    await _loadSelectedUniversity();
  }
  
  // Firebase 리스너 설정
  void _setupFirebaseListener() {
    // 사용자 프로필이 있을 때만 리스너 설정
    if (_userProfile?.uid != null && _userProfile!.uid.isNotEmpty) {
      FirebaseService.instance.getUserProfileStream(_userProfile!.uid).listen(
        (profile) {
          if (profile != null && profile != _userProfile) {
            _userProfile = profile;
            _loadSelectedUniversity(); // 대학교 정보도 다시 로드
            notifyListeners();
          }
        },
        onError: (error) {
          debugPrint('Firebase profile stream error: $error');
        },
      );
    }
  }

  // 프로필 로드 (public 메서드)
  Future<void> loadUserProfile() async {
    await _loadUserProfile();
  }

  // 프로필 필드 업데이트
  Future<void> updateProfileFields({
    String? name,
    String? studentId,
    String? major,
    String? department,
    String? university,
    int? grade,
    String? email,
    String? semesterInfo,
  }) async {
    if (_userProfile == null) return;

    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final updatedProfile = _userProfile!.copyWith(
        name: name ?? _userProfile!.name,
        studentId: studentId ?? _userProfile!.studentId,
        major: major ?? _userProfile!.major,
        department: department ?? _userProfile!.department,
        university: university ?? _userProfile!.university,
        grade: grade ?? _userProfile!.grade,
        email: email ?? _userProfile!.email,
        semesterInfo: semesterInfo ?? _userProfile!.semesterInfo,
        updatedAt: DateTime.now(),
      );
      
      await updateUserProfile(updatedProfile);
      
      debugPrint('프로필 필드 업데이트 완료: ${name ?? studentId ?? major ?? department ?? email ?? '기타'}');
    } catch (e) {
      _error = e.toString();
      debugPrint('Error updating profile fields: $e');
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }
}