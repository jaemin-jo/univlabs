///
///보안 자격증명 관리 서비스
/// 암호화된 로컬 저장
/// Firebase 연동
///자동 갱신
///

import 'dart:convert';
import 'dart:io';
import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:crypto/crypto.dart';
import 'package:encrypt/encrypt.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:cloud_firestore/cloud_firestore.dart';

class SecureCredentialService {
  static final SecureCredentialService _instance = SecureCredentialService._internal();
  factory SecureCredentialService() => _instance;
  SecureCredentialService._internal();

  final FirebaseFirestore _firestore = FirebaseFirestore.instance;
  final FirebaseAuth _auth = FirebaseAuth.instance;
  
  late final Encrypter _encrypter;
  late final Key _key;
  late final IV _iv;

  Future<void> initialize() async {
    debugPrint('🔐 보안 자격증명 서비스 초기화');
    
    // 암호화 키 생성 (사용자별 고유 키)
    final user = _auth.currentUser;
    if (user == null) {
      throw Exception('사용자가 로그인되지 않음');
    }

    // 사용자 UID 기반 키 생성
    final keyString = _generateUserKey(user.uid);
    _key = Key.fromBase64(keyString);
    _iv = IV.fromSecureRandom(16);
    _encrypter = Encrypter(AES(_key));

    debugPrint('✅ 암호화 키 초기화 완료');
  }

  String _generateUserKey(String uid) {
    // 사용자 UID를 기반으로 고유한 암호화 키 생성
    final bytes = utf8.encode(uid + 'univlabs_secret_salt_2024');
    final digest = sha256.convert(bytes);
    return base64.encode(digest.bytes);
  }

  Future<bool> saveCredentials({
    required String university,
    required String username,
    required String password,
    required String studentId,
  }) async {
    try {
      await initialize();
      
      final user = _auth.currentUser;
      if (user == null) {
        debugPrint('❌ 사용자가 로그인되지 않음');
        return false;
      }

      // 자격증명 데이터 준비
      final credentialData = {
        'university': university,
        'username': username,
        'password': password, // 암호화됨
        'studentId': studentId,
        'createdAt': DateTime.now().toIso8601String(),
        'lastUsed': null,
        'isActive': true,
      };

      // 암호화
      final encryptedData = _encrypter.encrypt(json.encode(credentialData), iv: _iv);
      final encryptedBase64 = encryptedData.base64;

      // Firebase에 암호화된 데이터 저장
      await _firestore
          .collection('user_credentials')
          .doc(user.uid)
          .set({
        'encryptedData': encryptedBase64,
        'university': university, // 검색용 (암호화되지 않음)
        'isActive': true,
        'lastUpdated': FieldValue.serverTimestamp(),
      });

      // 로컬에도 백업 저장
      await _saveToLocalStorage(user.uid, encryptedBase64);

      debugPrint('✅ 자격증명 암호화 저장 완료');
      debugPrint('   - 대학교: $university');
      debugPrint('   - 사용자: $username');
      debugPrint('   - 학번: $studentId');
      
      return true;
    } catch (e) {
      debugPrint('❌ 자격증명 저장 오류: $e');
      return false;
    }
  }

  Future<Map<String, dynamic>?> getCredentials() async {
    try {
      await initialize();
      
      final user = _auth.currentUser;
      if (user == null) {
        debugPrint('❌ 사용자가 로그인되지 않음');
        return null;
      }

      // Firebase에서 암호화된 데이터 조회
      final doc = await _firestore
          .collection('user_credentials')
          .doc(user.uid)
          .get();

      if (!doc.exists) {
        debugPrint('⚠️ 저장된 자격증명이 없음');
        return null;
      }

      final encryptedBase64 = doc.data()?['encryptedData'] as String?;
      if (encryptedBase64 == null) {
        debugPrint('❌ 암호화된 데이터가 없음');
        return null;
      }

      // 복호화
      final encrypted = Encrypted.fromBase64(encryptedBase64);
      final decryptedJson = _encrypter.decrypt(encrypted, iv: _iv);
      final credentialData = json.decode(decryptedJson) as Map<String, dynamic>;

      debugPrint('✅ 자격증명 복호화 성공');
      return credentialData;
    } catch (e) {
      debugPrint('❌ 자격증명 조회 오류: $e');
      return null;
    }
  }

  Future<void> _saveToLocalStorage(String userId, String encryptedData) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('encrypted_credentials_$userId', encryptedData);
      debugPrint('💾 로컬 백업 저장 완료');
    } catch (e) {
      debugPrint('⚠️ 로컬 저장 오류: $e');
    }
  }

  Future<bool> updateLastUsed() async {
    try {
      final credentials = await getCredentials();
      if (credentials == null) return false;

      final user = _auth.currentUser;
      if (user == null) return false;

      // 마지막 사용 시간 업데이트
      credentials['lastUsed'] = DateTime.now().toIso8601String();
      
      // 암호화하여 다시 저장
      final encryptedData = _encrypter.encrypt(json.encode(credentials), iv: _iv);
      final encryptedBase64 = encryptedData.base64;

      await _firestore
          .collection('user_credentials')
          .doc(user.uid)
          .update({
        'encryptedData': encryptedBase64,
        'lastUsed': FieldValue.serverTimestamp(),
      });

      debugPrint('✅ 마지막 사용 시간 업데이트 완료');
      return true;
    } catch (e) {
      debugPrint('❌ 사용 시간 업데이트 오류: $e');
      return false;
    }
  }

  Future<bool> deleteCredentials() async {
    try {
      final user = _auth.currentUser;
      if (user == null) return false;

      // Firebase에서 삭제
      await _firestore
          .collection('user_credentials')
          .doc(user.uid)
          .delete();

      // 로컬에서도 삭제
      final prefs = await SharedPreferences.getInstance();
      await prefs.remove('encrypted_credentials_$user.uid');

      debugPrint('✅ 자격증명 삭제 완료');
      return true;
    } catch (e) {
      debugPrint('❌ 자격증명 삭제 오류: $e');
      return false;
    }
  }

  Future<bool> hasCredentials() async {
    try {
      final credentials = await getCredentials();
      return credentials != null;
    } catch (e) {
      debugPrint('❌ 자격증명 확인 오류: $e');
      return false;
    }
  }
}
