import 'dart:io';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter/foundation.dart';
import '../models/user_profile.dart';
import 'firebase_service.dart';

class ProfileService {
  static ProfileService? _instance;
  static ProfileService get instance => _instance ??= ProfileService._();
  
  ProfileService._();
  
  final FirebaseFirestore _firestore = FirebaseService.instance.firestore;
  final FirebaseAuth _auth = FirebaseService.instance.auth;
  
  // 사용자 프로필 스트림
  Stream<UserProfile?> get userProfileStream {
    final user = _auth.currentUser;
    if (user == null) return Stream.value(null);
    
    return _firestore
        .collection('users')
        .doc(user.uid)
        .snapshots()
        .map((doc) {
      if (!doc.exists) return null;
      return UserProfile.fromFirestore(doc.data()!);
    });
  }
  
  // 사용자 프로필 가져오기
  Future<UserProfile?> getUserProfile() async {
    final user = _auth.currentUser;
    if (user == null) return null;
    
    try {
      final doc = await _firestore.collection('users').doc(user.uid).get();
      if (!doc.exists) return null;
      return UserProfile.fromFirestore(doc.data()!);
    } catch (e) {
      debugPrint('Error getting user profile: $e');
      return null;
    }
  }
  
  // 사용자 프로필 생성/업데이트
  Future<void> saveUserProfile(UserProfile profile) async {
    try {
      await _firestore
          .collection('users')
          .doc(profile.uid)
          .set(profile.toFirestore(), SetOptions(merge: true));
      debugPrint('User profile saved successfully');
    } catch (e) {
      debugPrint('Error saving user profile: $e');
      rethrow;
    }
  }
  
  // 관심사 태그 업데이트
  Future<void> updateInterestTags(List<String> tags) async {
    final user = _auth.currentUser;
    if (user == null) return;
    
    try {
      await _firestore.collection('users').doc(user.uid).update({
        'interestTags': tags,
        'updatedAt': FieldValue.serverTimestamp(),
      });
      debugPrint('Interest tags updated successfully');
    } catch (e) {
      debugPrint('Error updating interest tags: $e');
      rethrow;
    }
  }
  
  // 구독 채널 업데이트
  Future<void> updateSubscribedChannels(List<String> channels) async {
    final user = _auth.currentUser;
    if (user == null) return;
    
    try {
      await _firestore.collection('users').doc(user.uid).update({
        'subscribedChannels': channels,
        'updatedAt': FieldValue.serverTimestamp(),
      });
      debugPrint('Subscribed channels updated successfully');
    } catch (e) {
      debugPrint('Error updating subscribed channels: $e');
      rethrow;
    }
  }
  
  // 프로필 이미지 업로드
  Future<String?> uploadProfileImage(String imagePath) async {
    final user = _auth.currentUser;
    if (user == null) return null;
    
    try {
      final ref = FirebaseService.instance.storage
          .ref()
          .child('profile_images')
          .child('${user.uid}.jpg');
      
      await ref.putFile(File(imagePath));
      final downloadUrl = await ref.getDownloadURL();
      
      // 프로필에 이미지 URL 업데이트
      await _firestore.collection('users').doc(user.uid).update({
        'profileImageUrl': downloadUrl,
        'updatedAt': FieldValue.serverTimestamp(),
      });
      
      return downloadUrl;
    } catch (e) {
      debugPrint('Error uploading profile image: $e');
      return null;
    }
  }
  
  // 사용자 프로필 삭제
  Future<void> deleteUserProfile() async {
    final user = _auth.currentUser;
    if (user == null) return;
    
    try {
      await _firestore.collection('users').doc(user.uid).delete();
      debugPrint('User profile deleted successfully');
    } catch (e) {
      debugPrint('Error deleting user profile: $e');
      rethrow;
    }
  }
}
