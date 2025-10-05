import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter/foundation.dart';
import '../models/announcement.dart';
import 'firebase_service.dart';

class AnnouncementService {
  static AnnouncementService? _instance;
  static AnnouncementService get instance => _instance ??= AnnouncementService._();
  
  AnnouncementService._();
  
  final FirebaseFirestore _firestore = FirebaseService.instance.firestore;
  final FirebaseAuth _auth = FirebaseService.instance.auth;
  
  // 사용자별 맞춤 공지사항 스트림
  Stream<List<Announcement>> getUserAnnouncements() {
    final user = _auth.currentUser;
    if (user == null) return Stream.value([]);
    
    return _firestore
        .collection('users')
        .doc(user.uid)
        .snapshots()
        .asyncMap((userDoc) async {
      if (!userDoc.exists) return <Announcement>[];
      
      final userData = userDoc.data()!;
      final interestTags = List<String>.from(userData['interestTags'] ?? []);
      
      if (interestTags.isEmpty) {
        // 관심사 태그가 없으면 최신 공지사항 반환
        return await _getLatestAnnouncements();
      }
      
      // 관심사 태그와 매칭되는 공지사항 가져오기
      return await _getMatchingAnnouncements(interestTags);
    });
  }
  
  // 최신 공지사항 가져오기
  Future<List<Announcement>> _getLatestAnnouncements() async {
    try {
      final snapshot = await _firestore
          .collection('announcements')
          .orderBy('publishedAt', descending: true)
          .limit(20)
          .get();
      
      return snapshot.docs
          .map((doc) => Announcement.fromFirestore(doc.data()))
          .toList();
    } catch (e) {
      debugPrint('Error getting latest announcements: $e');
      // 권한 오류인 경우 빈 목록 반환
      if (e.toString().contains('permission-denied')) {
        debugPrint('Firestore permission denied. Please check security rules.');
        return [];
      }
      return [];
    }
  }
  
  // 관심사 태그와 매칭되는 공지사항 가져오기
  Future<List<Announcement>> _getMatchingAnnouncements(List<String> interestTags) async {
    try {
      final snapshot = await _firestore
          .collection('announcements')
          .where('tags', arrayContainsAny: interestTags)
          .orderBy('publishedAt', descending: true)
          .limit(50)
          .get();
      
      return snapshot.docs
          .map((doc) => Announcement.fromFirestore(doc.data()))
          .toList();
    } catch (e) {
      debugPrint('Error getting matching announcements: $e');
      return [];
    }
  }
  
  // 공지사항 읽음 처리
  Future<void> markAsRead(String announcementId) async {
    try {
      await _firestore
          .collection('announcements')
          .doc(announcementId)
          .update({'isRead': true});
    } catch (e) {
      debugPrint('Error marking announcement as read: $e');
    }
  }
  
  // 중요 공지사항 가져오기
  Stream<List<Announcement>> getImportantAnnouncements() {
    return _firestore
        .collection('announcements')
        .where('isImportant', isEqualTo: true)
        .orderBy('publishedAt', descending: true)
        .limit(10)
        .snapshots()
        .map((snapshot) {
      return snapshot.docs
          .map((doc) => Announcement.fromFirestore(doc.data()))
          .toList();
    }).handleError((error) {
      debugPrint('Error loading important announcements: $error');
      return <Announcement>[];
    });
  }
  
  // 특정 출처의 공지사항 가져오기
  Stream<List<Announcement>> getAnnouncementsBySource(String source) {
    return _firestore
        .collection('announcements')
        .where('source', isEqualTo: source)
        .orderBy('publishedAt', descending: true)
        .limit(20)
        .snapshots()
        .map((snapshot) {
      return snapshot.docs
          .map((doc) => Announcement.fromFirestore(doc.data()))
          .toList();
    });
  }
  
  // 공지사항 검색
  Future<List<Announcement>> searchAnnouncements(String query) async {
    try {
      // 제목에서 검색
      final titleSnapshot = await _firestore
          .collection('announcements')
          .where('title', isGreaterThanOrEqualTo: query)
          .where('title', isLessThan: query + 'z')
          .limit(10)
          .get();
      
      // 내용에서 검색
      final contentSnapshot = await _firestore
          .collection('announcements')
          .where('content', isGreaterThanOrEqualTo: query)
          .where('content', isLessThan: query + 'z')
          .limit(10)
          .get();
      
      final results = <Announcement>[];
      
      // 제목 검색 결과 추가
      for (final doc in titleSnapshot.docs) {
        results.add(Announcement.fromFirestore(doc.data()));
      }
      
      // 내용 검색 결과 추가 (중복 제거)
      for (final doc in contentSnapshot.docs) {
        final announcement = Announcement.fromFirestore(doc.data());
        if (!results.any((a) => a.id == announcement.id)) {
          results.add(announcement);
        }
      }
      
      // 최신순으로 정렬
      results.sort((a, b) => b.publishedAt.compareTo(a.publishedAt));
      
      return results.take(20).toList();
    } catch (e) {
      debugPrint('Error searching announcements: $e');
      return [];
    }
  }
  
  // 공지사항 통계
  Future<Map<String, int>> getAnnouncementStats() async {
    try {
      final snapshot = await _firestore.collection('announcements').get();
      final stats = <String, int>{
        'total': 0,
        'important': 0,
        'unread': 0,
        'today': 0,
      };
      
      final today = DateTime.now();
      final todayStart = DateTime(today.year, today.month, today.day);
      
      for (final doc in snapshot.docs) {
        final data = doc.data();
        stats['total'] = (stats['total'] ?? 0) + 1;
        
        if (data['isImportant'] == true) {
          stats['important'] = (stats['important'] ?? 0) + 1;
        }
        
        if (data['isRead'] != true) {
          stats['unread'] = (stats['unread'] ?? 0) + 1;
        }
        
        final publishedAt = data['publishedAt'] is DateTime 
            ? data['publishedAt'] 
            : DateTime.now();
        if (publishedAt.isAfter(todayStart)) {
          stats['today'] = (stats['today'] ?? 0) + 1;
        }
      }
      
      return stats;
    } catch (e) {
      debugPrint('Error getting announcement stats: $e');
      return {};
    }
  }
}
