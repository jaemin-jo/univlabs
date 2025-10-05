import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'dart:convert';
import 'dart:async';
import '../models/interest_tag.dart';
import '../services/ai_crawling_service.dart';

class InterestTagProvider with ChangeNotifier {
  List<InterestTag> _tags = [];
  List<InterestTag> _matchedAnnouncements = []; // AI가 찾은 관련 공지사항
  Timer? _crawlingTimer;
  bool _isCrawling = false;

  List<InterestTag> get tags => _tags.where((tag) => tag.isActive).toList();
  List<InterestTag> get allTags => _tags;
  List<InterestTag> get matchedAnnouncements => _matchedAnnouncements;
  bool get isCrawling => _isCrawling;

  // SharedPreferences 키
  static const String _tagsKey = 'interest_tags';

  InterestTagProvider() {
    _loadTags();
    _startPeriodicCrawling();
  }

  @override
  void dispose() {
    _crawlingTimer?.cancel();
    super.dispose();
  }

  // 태그 로드
  Future<void> _loadTags() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final tagsJson = prefs.getString(_tagsKey);
      
      if (tagsJson != null) {
        final List<dynamic> tagsList = json.decode(tagsJson);
        _tags = tagsList.map((json) => InterestTag.fromJson(json)).toList();
        notifyListeners();
      } else {
        // 기본 태그들 추가
        _addDefaultTags();
      }
    } catch (e) {
      print('태그 로드 오류: $e');
      _addDefaultTags();
    }
  }

  // 기본 태그들 추가
  void _addDefaultTags() {
    _tags = [
      InterestTag(
        id: '1',
        name: '수강신청',
        description: '수강신청 관련 공지사항',
        createdAt: DateTime.now(),
        keywords: ['수강신청', '수강신청기간', '수강신청안내'],
      ),
      InterestTag(
        id: '2',
        name: '기숙사',
        description: '기숙사 관련 공지사항',
        createdAt: DateTime.now(),
        keywords: ['기숙사', '기숙사신청', '기숙사배정'],
      ),
      InterestTag(
        id: '3',
        name: '장학금',
        description: '장학금 관련 공지사항',
        createdAt: DateTime.now(),
        keywords: ['장학금', '장학금신청', '장학금안내'],
      ),
    ];
    _saveTags();
  }

  // 태그 저장
  Future<void> _saveTags() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final tagsJson = json.encode(_tags.map((tag) => tag.toJson()).toList());
      await prefs.setString(_tagsKey, tagsJson);
    } catch (e) {
      print('태그 저장 오류: $e');
    }
  }

  // 태그 추가
  Future<void> addTag(InterestTag tag) async {
    _tags.add(tag);
    await _saveTags();
    notifyListeners();
  }

  // 태그 삭제
  Future<void> removeTag(String tagId) async {
    _tags.removeWhere((tag) => tag.id == tagId);
    await _saveTags();
    notifyListeners();
  }

  // 태그 업데이트
  Future<void> updateTag(InterestTag updatedTag) async {
    final index = _tags.indexWhere((tag) => tag.id == updatedTag.id);
    if (index != -1) {
      _tags[index] = updatedTag;
      await _saveTags();
      notifyListeners();
    }
  }

  // 태그 활성화/비활성화
  Future<void> toggleTagActive(String tagId) async {
    final index = _tags.indexWhere((tag) => tag.id == tagId);
    if (index != -1) {
      _tags[index] = _tags[index].copyWith(isActive: !_tags[index].isActive);
      await _saveTags();
      notifyListeners();
    }
  }

  // AI가 찾은 관련 공지사항 추가
  void addMatchedAnnouncement(InterestTag announcement) {
    // 중복 체크
    if (!_matchedAnnouncements.any((item) => item.id == announcement.id)) {
      _matchedAnnouncements.add(announcement);
      notifyListeners();
    }
  }

  // 매칭된 공지사항 제거
  void removeMatchedAnnouncement(String announcementId) {
    _matchedAnnouncements.removeWhere((item) => item.id == announcementId);
    notifyListeners();
  }

  // 모든 매칭된 공지사항 제거
  void clearMatchedAnnouncements() {
    _matchedAnnouncements.clear();
    notifyListeners();
  }

  // 태그 검색
  List<InterestTag> searchTags(String query) {
    if (query.isEmpty) return tags;
    
    return tags.where((tag) {
      return tag.name.toLowerCase().contains(query.toLowerCase()) ||
             tag.description?.toLowerCase().contains(query.toLowerCase()) == true ||
             tag.keywords.any((keyword) => keyword.toLowerCase().contains(query.toLowerCase()));
    }).toList();
  }

  // 주기적 크롤링 시작
  void _startPeriodicCrawling() {
    _crawlingTimer?.cancel();
    _crawlingTimer = Timer.periodic(const Duration(hours: 1), (timer) {
      _performCrawling();
    });
  }

  // 크롤링 실행
  Future<void> _performCrawling() async {
    if (_isCrawling || tags.isEmpty) return;
    
    _isCrawling = true;
    notifyListeners();
    
    try {
      // AI 크롤링 서비스를 통한 공지사항 검색
      final announcements = await AICrawlingService.findRelevantAnnouncements(tags);
      
      if (announcements.isNotEmpty) {
        for (final announcement in announcements) {
          addMatchedAnnouncement(announcement);
        }
      }
    } catch (e) {
      print('크롤링 오류: $e');
    } finally {
      _isCrawling = false;
      notifyListeners();
    }
  }

  // 수동 크롤링 실행
  Future<void> performManualCrawling() async {
    await _performCrawling();
  }

  // 특정 태그에 대한 크롤링
  Future<void> crawlForTag(InterestTag tag) async {
    if (_isCrawling) return;
    
    _isCrawling = true;
    notifyListeners();
    
    try {
      final announcements = await AICrawlingService.searchForTag(tag);
      
      if (announcements.isNotEmpty) {
        for (final announcement in announcements) {
          addMatchedAnnouncement(announcement);
        }
      }
    } catch (e) {
      print('태그 크롤링 오류: $e');
    } finally {
      _isCrawling = false;
      notifyListeners();
    }
  }

  // 크롤링 상태 토글
  void toggleCrawling() {
    if (_crawlingTimer?.isActive == true) {
      _crawlingTimer?.cancel();
    } else {
      _startPeriodicCrawling();
    }
    notifyListeners();
  }

  // 크롤링 간격 설정 (분 단위)
  void setCrawlingInterval(int minutes) {
    _crawlingTimer?.cancel();
    _crawlingTimer = Timer.periodic(Duration(minutes: minutes), (timer) {
      _performCrawling();
    });
    notifyListeners();
  }
}
