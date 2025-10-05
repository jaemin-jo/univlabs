import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:firebase_storage/firebase_storage.dart';
import 'package:flutter/foundation.dart';
import '../models/user_profile.dart';
import '../models/university.dart';
import '../models/learnus_credentials.dart';

class FirebaseService {
  static FirebaseService? _instance;
  static FirebaseService get instance => _instance ??= FirebaseService._();
  
  FirebaseService._();
  
  late FirebaseAuth _auth;
  late FirebaseFirestore _firestore;
  late FirebaseStorage _storage;
  
  FirebaseAuth get auth => _auth;
  FirebaseFirestore get firestore => _firestore;
  FirebaseStorage get storage => _storage;
  
  bool _isInitialized = false;
  bool get isInitialized => _isInitialized;
  
  Future<void> initialize() async {
    if (_isInitialized) return;
    
    try {
      await Firebase.initializeApp();
      _auth = FirebaseAuth.instance;
      _firestore = FirebaseFirestore.instance;
      _storage = FirebaseStorage.instance;
      
      _isInitialized = true;
      debugPrint('Firebase Service initialized successfully');
    } catch (e) {
      debugPrint('Failed to initialize Firebase Service: $e');
      rethrow;
    }
  }
  
  // 사용자 인증 상태 스트림
  Stream<User?> get authStateChanges => _auth.authStateChanges();
  
  // 현재 사용자
  User? get currentUser => _auth.currentUser;
  
  // 익명 로그인
  Future<UserCredential> signInAnonymously() async {
    return await _auth.signInAnonymously();
  }
  
  // 로그아웃
  Future<void> signOut() async {
    await _auth.signOut();
  }
  
  // ========== 사용자 프로필 관리 ==========
  
  // 사용자 프로필 생성/업데이트
  Future<void> saveUserProfile(UserProfile profile) async {
    try {
      final profileData = profile.toFirestore();
      await _firestore
          .collection('user_profiles')
          .doc(profile.uid)
          .set(profileData, SetOptions(merge: true));
      
      debugPrint('🔥 Firebase Firestore에 개인정보 저장 성공!');
      debugPrint('   📍 컬렉션: user_profiles');
      debugPrint('   📄 문서 ID: ${profile.uid}');
      debugPrint('   📊 저장된 데이터:');
      profileData.forEach((key, value) {
        debugPrint('     - $key: $value');
      });
    } catch (e) {
      debugPrint('❌ Firebase Firestore 저장 오류: $e');
      rethrow;
    }
  }
  
  // 사용자 프로필 가져오기
  Future<UserProfile?> getUserProfile(String uid) async {
    try {
      final doc = await _firestore
          .collection('user_profiles')
          .doc(uid)
          .get();
      
      if (doc.exists && doc.data() != null) {
        return UserProfile.fromFirestore(doc.data()!);
      }
      return null;
    } catch (e) {
      debugPrint('사용자 프로필 가져오기 오류: $e');
      return null;
    }
  }
  
  // 사용자 프로필 스트림
  Stream<UserProfile?> getUserProfileStream(String uid) {
    return _firestore
        .collection('user_profiles')
        .doc(uid)
        .snapshots()
        .map((doc) {
      if (doc.exists && doc.data() != null) {
        return UserProfile.fromFirestore(doc.data()!);
      }
      return null;
    });
  }
  
  // 대학교 정보 업데이트
  Future<void> updateUserUniversity(String uid, University university) async {
    try {
      await _firestore
          .collection('user_profiles')
          .doc(uid)
          .update({
        'university': university.name,
        'universityId': university.id,
        'universityCampus': university.campuses.isNotEmpty ? university.campuses.first : null,
        'updatedAt': FieldValue.serverTimestamp(),
      });
      debugPrint('사용자 대학교 정보 업데이트 완료: ${university.name}');
    } catch (e) {
      debugPrint('대학교 정보 업데이트 오류: $e');
      rethrow;
    }
  }
  
  // 사용자 대학교 정보 가져오기
  Future<University?> getUserUniversity(String uid) async {
    if (uid.isEmpty) {
      debugPrint('사용자 ID가 비어있습니다.');
      return null;
    }
    
    try {
      final doc = await _firestore
          .collection('user_profiles')
          .doc(uid)
          .get();
      
      if (doc.exists && doc.data() != null) {
        final data = doc.data()!;
        final universityId = data['universityId'] as String?;
        
        if (universityId != null) {
          // UniversityService에서 대학교 정보 가져오기
          final universities = await _getAllUniversities();
          return universities.firstWhere(
            (uni) => uni.id == universityId,
            orElse: () => universities.first,
          );
        }
      }
      return null;
    } catch (e) {
      debugPrint('사용자 대학교 정보 가져오기 오류: $e');
      return null;
    }
  }
  
  // 모든 대학교 정보 가져오기 (캐시된 데이터)
  Future<List<University>> _getAllUniversities() async {
    try {
      final doc = await _firestore
          .collection('universities')
          .doc('all_universities')
          .get();
      
      if (doc.exists && doc.data() != null) {
        final data = doc.data()!;
        final universitiesData = data['universities'] as List<dynamic>?;
        
        if (universitiesData != null) {
          return universitiesData
              .map((uniData) => University.fromFirestore(uniData as Map<String, dynamic>))
              .toList();
        }
      }
      
      // 기본 대학교 목록 반환
      return _getDefaultUniversities();
    } catch (e) {
      debugPrint('대학교 정보 가져오기 오류: $e');
      return _getDefaultUniversities();
    }
  }
  
  // 기본 대학교 목록
  List<University> _getDefaultUniversities() {
    return [
      University(
        id: 'yonsei',
        name: '연세대학교',
        fullName: '연세대학교',
        region: '서울',
        website: 'https://www.yonsei.ac.kr/',
        scheduleUrl: 'https://www.yonsei.ac.kr/sc/notice/',
        type: 'private',
        ranking: 1,
        campuses: ['신촌캠퍼스'],
        logoUrl: 'https://www.yonsei.ac.kr/_res/yonsei/img/common/logo.png',
      ),
      University(
        id: 'yonsei_mirae',
        name: '연세대학교 미래캠퍼스',
        fullName: '연세대학교 미래캠퍼스',
        region: '강원',
        website: 'https://mirae.yonsei.ac.kr/',
        scheduleUrl: 'https://mirae.yonsei.ac.kr/',
        type: 'private',
        ranking: 2,
        campuses: ['미래캠퍼스'],
        logoUrl: 'https://mirae.yonsei.ac.kr/_res/mirae/img/common/logo.png',
      ),
      University(
        id: 'snu',
        name: '서울대학교',
        fullName: '서울대학교',
        region: '서울',
        website: 'https://www.snu.ac.kr/',
        scheduleUrl: 'https://www.snu.ac.kr/',
        type: 'national',
        ranking: 1,
        campuses: ['관악캠퍼스'],
        logoUrl: 'https://www.snu.ac.kr/_res/snu/img/common/logo.png',
      ),
    ];
  }
  
  // 대학교 정보를 Firestore에 저장
  Future<void> saveUniversitiesToFirestore(List<University> universities) async {
    try {
      final universitiesData = universities.map((uni) => uni.toFirestore()).toList();
      
      await _firestore
          .collection('universities')
          .doc('all_universities')
          .set({
        'universities': universitiesData,
        'lastUpdated': FieldValue.serverTimestamp(),
      });
      
      debugPrint('대학교 정보 저장 완료: ${universities.length}개');
    } catch (e) {
      debugPrint('대학교 정보 저장 오류: $e');
    }
  }

  // 사용자 프로필 삭제
  Future<void> deleteUserProfile(String uid) async {
    try {
      await _firestore.collection('users').doc(uid).delete();
      debugPrint('사용자 프로필 삭제 완료: $uid');
    } catch (e) {
      debugPrint('사용자 프로필 삭제 오류: $e');
      rethrow;
    }
  }

  // ========== LearnUs 인증 정보 관리 ==========

  // LearnUs 인증 정보 저장
  Future<void> saveLearnUsCredentials(LearnUsCredentials credentials) async {
    try {
      final credentialsData = credentials.toFirestore();
      await _firestore
          .collection('learnus_credentials')
          .doc(credentials.uid)
          .set(credentialsData, SetOptions(merge: true));
      
      debugPrint('🔥 Firebase에 LearnUs 인증 정보 저장 성공!');
      debugPrint('   📍 컬렉션: learnus_credentials');
      debugPrint('   📄 문서 ID: ${credentials.uid}');
      debugPrint('   🏫 대학교: ${credentials.university}');
      debugPrint('   👤 사용자: ${credentials.username}');
    } catch (e) {
      debugPrint('❌ LearnUs 인증 정보 저장 오류: $e');
      rethrow;
    }
  }

  // LearnUs 인증 정보 가져오기
  Future<LearnUsCredentials?> getLearnUsCredentials(String uid) async {
    try {
      final doc = await _firestore
          .collection('learnus_credentials')
          .doc(uid)
          .get();
      
      if (doc.exists && doc.data() != null) {
        return LearnUsCredentials.fromFirestore(doc.data()!);
      }
      return null;
    } catch (e) {
      debugPrint('LearnUs 인증 정보 가져오기 오류: $e');
      return null;
    }
  }

  // 활성화된 모든 LearnUs 인증 정보 가져오기 (백엔드용)
  Future<List<LearnUsCredentials>> getAllActiveLearnUsCredentials() async {
    try {
      final querySnapshot = await _firestore
          .collection('learnus_credentials')
          .where('isActive', isEqualTo: true)
          .get();
      
      return querySnapshot.docs
          .map((doc) => LearnUsCredentials.fromFirestore(doc.data()))
          .toList();
    } catch (e) {
      debugPrint('모든 LearnUs 인증 정보 가져오기 오류: $e');
      return [];
    }
  }

  // LearnUs 인증 정보 업데이트
  Future<void> updateLearnUsCredentials(LearnUsCredentials credentials) async {
    try {
      final updatedCredentials = credentials.copyWith(
        updatedAt: DateTime.now(),
        lastUsedAt: DateTime.now(),
      );
      
      await saveLearnUsCredentials(updatedCredentials);
      debugPrint('LearnUs 인증 정보 업데이트 완료: ${credentials.uid}');
    } catch (e) {
      debugPrint('LearnUs 인증 정보 업데이트 오류: $e');
      rethrow;
    }
  }

  // LearnUs 인증 정보 비활성화
  Future<void> deactivateLearnUsCredentials(String uid) async {
    try {
      await _firestore
          .collection('learnus_credentials')
          .doc(uid)
          .update({
        'isActive': false,
        'updatedAt': FieldValue.serverTimestamp(),
      });
      debugPrint('LearnUs 인증 정보 비활성화 완료: $uid');
    } catch (e) {
      debugPrint('LearnUs 인증 정보 비활성화 오류: $e');
      rethrow;
    }
  }

  // LearnUs 인증 정보 삭제
  Future<void> deleteLearnUsCredentials(String uid) async {
    try {
      await _firestore
          .collection('learnus_credentials')
          .doc(uid)
          .delete();
      debugPrint('LearnUs 인증 정보 삭제 완료: $uid');
    } catch (e) {
      debugPrint('LearnUs 인증 정보 삭제 오류: $e');
      rethrow;
    }
  }
}
