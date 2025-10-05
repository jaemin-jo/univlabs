import 'package:flutter/material.dart';
import '../models/announcement.dart';
import '../services/announcement_service.dart';

class AnnouncementProvider extends ChangeNotifier {
  List<Announcement> _announcements = [];
  List<Announcement> _importantAnnouncements = [];
  bool _isLoading = false;
  String? _error;

  List<Announcement> get announcements => _announcements;
  List<Announcement> get importantAnnouncements => _importantAnnouncements;
  bool get isLoading => _isLoading;
  String? get error => _error;

  AnnouncementProvider() {
    loadAnnouncements();
  }

  // 공지사항 로드
  Future<void> loadAnnouncements() async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      // Firebase에서 사용자별 맞춤 공지사항 가져오기
      final announcementService = AnnouncementService.instance;
      
      // 스트림 구독
      announcementService.getUserAnnouncements().listen(
        (announcements) {
          _announcements = announcements;
          _updateImportantAnnouncements();
          notifyListeners();
        },
        onError: (error) {
          _error = error.toString();
          debugPrint('Error loading announcements: $error');
          notifyListeners();
        },
      );

      // 중요 공지사항도 별도로 구독
      announcementService.getImportantAnnouncements().listen(
        (importantAnnouncements) {
          _importantAnnouncements = importantAnnouncements;
          notifyListeners();
        },
        onError: (error) {
          debugPrint('Error loading important announcements: $error');
        },
      );
    } catch (e) {
      _error = e.toString();
      debugPrint('Error loading announcements: $e');
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  // 중요 공지사항 업데이트
  void _updateImportantAnnouncements() {
    _importantAnnouncements = _announcements
        .where((announcement) => announcement.isImportant)
        .toList()
      ..sort((a, b) => b.publishedAt.compareTo(a.publishedAt));
  }

  // 타입별 공지사항 가져오기
  List<Announcement> getAnnouncementsByType(AnnouncementType type) {
    return _announcements
        .where((announcement) => announcement.type == type)
        .toList()
      ..sort((a, b) => b.publishedAt.compareTo(a.publishedAt));
  }

  // 출처별 공지사항 가져오기
  List<Announcement> getAnnouncementsBySource(String source) {
    return _announcements
        .where((announcement) => announcement.source == source)
        .toList()
      ..sort((a, b) => b.publishedAt.compareTo(a.publishedAt));
  }

  // 관심사 태그와 매칭된 공지사항 가져오기
  List<Announcement> getMatchedAnnouncements() {
    return _announcements
        .where((announcement) => announcement.tags.isNotEmpty)
        .toList()
      ..sort((a, b) => b.publishedAt.compareTo(a.publishedAt));
  }

  // 공지사항 검색
  Future<List<Announcement>> searchAnnouncements(String query) async {
    try {
      return await AnnouncementService.instance.searchAnnouncements(query);
    } catch (e) {
      debugPrint('Error searching announcements: $e');
      return [];
    }
  }

  // 공지사항 읽음 처리
  Future<void> markAsRead(String announcementId) async {
    try {
      await AnnouncementService.instance.markAsRead(announcementId);
      
      // 로컬 상태 업데이트
      final index = _announcements.indexWhere((a) => a.id == announcementId);
      if (index != -1) {
        _announcements[index] = _announcements[index].copyWith(isRead: true);
        notifyListeners();
      }
    } catch (e) {
      debugPrint('Error marking announcement as read: $e');
    }
  }

  // 공지사항 중요도 토글
  Future<void> toggleImportance(String announcementId) async {
    try {
      final index = _announcements.indexWhere((a) => a.id == announcementId);
      if (index != -1) {
        final announcement = _announcements[index];
        final updatedAnnouncement = announcement.copyWith(
          isImportant: !announcement.isImportant,
        );
        
        _announcements[index] = updatedAnnouncement;
        _updateImportantAnnouncements();
        notifyListeners();
        
        // Firebase에 업데이트 (실제 구현에서는 AnnouncementService에 메서드 추가 필요)
        // await AnnouncementService.instance.updateAnnouncement(updatedAnnouncement);
      }
    } catch (e) {
      debugPrint('Error toggling announcement importance: $e');
    }
  }

  // 공지사항 통계 가져오기
  Future<Map<String, int>> getAnnouncementStats() async {
    try {
      return await AnnouncementService.instance.getAnnouncementStats();
    } catch (e) {
      debugPrint('Error getting announcement stats: $e');
      return {};
    }
  }

  // 공지사항 새로고침
  Future<void> refreshAnnouncements() async {
    await loadAnnouncements();
  }

  // 에러 클리어
  void clearError() {
    _error = null;
    notifyListeners();
  }

  // 필터링된 공지사항 가져오기
  List<Announcement> getFilteredAnnouncements({
    AnnouncementType? type,
    String? source,
    bool? isImportant,
    bool? isMatched,
    String? searchQuery,
  }) {
    List<Announcement> filtered = List.from(_announcements);

    if (type != null) {
      filtered = filtered.where((a) => a.type == type).toList();
    }

    if (source != null && source.isNotEmpty) {
      filtered = filtered.where((a) => a.source == source).toList();
    }

    if (isImportant != null) {
      filtered = filtered.where((a) => a.isImportant == isImportant).toList();
    }

    if (isMatched != null) {
      if (isMatched) {
        filtered = filtered.where((a) => a.tags.isNotEmpty).toList();
      } else {
        filtered = filtered.where((a) => a.tags.isEmpty).toList();
      }
    }

    if (searchQuery != null && searchQuery.isNotEmpty) {
      filtered = filtered.where((a) => 
        a.title.toLowerCase().contains(searchQuery.toLowerCase()) ||
        a.content.toLowerCase().contains(searchQuery.toLowerCase()) ||
        (a.department?.toLowerCase().contains(searchQuery.toLowerCase()) ?? false)
      ).toList();
    }

    // 최신순으로 정렬
    filtered.sort((a, b) => b.publishedAt.compareTo(a.publishedAt));

    return filtered;
  }

  // 오늘의 공지사항 가져오기
  List<Announcement> getTodayAnnouncements() {
    final today = DateTime.now();
    final todayStart = DateTime(today.year, today.month, today.day);
    
    return _announcements
        .where((announcement) => announcement.publishedAt.isAfter(todayStart))
        .toList()
      ..sort((a, b) => b.publishedAt.compareTo(a.publishedAt));
  }

  // 읽지 않은 공지사항 가져오기
  List<Announcement> getUnreadAnnouncements() {
    return _announcements
        .where((announcement) => !announcement.isRead)
        .toList()
      ..sort((a, b) => b.publishedAt.compareTo(a.publishedAt));
  }
}