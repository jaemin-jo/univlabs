import 'package:flutter/material.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:google_sign_in/google_sign_in.dart';
import '../services/firebase_service.dart';
import '../models/user_profile.dart';

class AuthProvider extends ChangeNotifier {
  final FirebaseAuth _auth = FirebaseAuth.instance;
  final GoogleSignIn _googleSignIn = GoogleSignIn();
  
  User? _user;
  bool _isLoading = false;
  String? _error;

  // Getters
  User? get user => _user;
  bool get isLoading => _isLoading;
  String? get error => _error;
  bool get isAuthenticated => _user != null;

  AuthProvider() {
    _init();
  }

  void _init() {
    // 현재 사용자 상태 확인
    _user = _auth.currentUser;
    
    // 인증 상태 변화 감지
    _auth.authStateChanges().listen((User? user) {
      _user = user;
      notifyListeners();
    });
  }

  // 구글 로그인
  Future<void> signInWithGoogle() async {
    try {
      _setLoading(true);
      _clearError();

      // 구글 로그인 실행
      final GoogleSignInAccount? googleUser = await _googleSignIn.signIn();
      if (googleUser == null) {
        throw Exception('구글 로그인이 취소되었습니다.');
      }

      // 인증 정보 가져오기
      final GoogleSignInAuthentication googleAuth = await googleUser.authentication;
      
      // 토큰 유효성 검사
      if (googleAuth.accessToken == null || googleAuth.idToken == null) {
        throw Exception('구글 인증 토큰을 가져올 수 없습니다. 네트워크 연결을 확인해주세요.');
      }

      final credential = GoogleAuthProvider.credential(
        accessToken: googleAuth.accessToken,
        idToken: googleAuth.idToken,
      );

      // Firebase 인증
      final UserCredential userCredential = await _auth.signInWithCredential(credential);
      _user = userCredential.user;

      // 사용자 프로필이 Firebase에 없으면 생성
      if (_user != null) {
        await _createUserProfileIfNeeded(_user!);
      }

      debugPrint('구글 로그인 성공: ${_user?.email}');
    } catch (e) {
      String errorMessage = '구글 로그인 실패';
      
      if (e.toString().contains('network_error')) {
        errorMessage = '네트워크 연결을 확인해주세요.';
      } else if (e.toString().contains('ApiException: 7')) {
        errorMessage = 'Google Play Services를 업데이트해주세요.';
      } else if (e.toString().contains('DEVELOPER_ERROR')) {
        errorMessage = '개발자 설정을 확인해주세요.';
      } else {
        errorMessage = '구글 로그인 실패: $e';
      }
      
      _setError(errorMessage);
      debugPrint('구글 로그인 오류: $e');
      rethrow;
    } finally {
      _setLoading(false);
    }
  }

  // 사용자 프로필 생성 (필요한 경우)
  Future<void> _createUserProfileIfNeeded(User user) async {
    try {
      final existingProfile = await FirebaseService.instance.getUserProfile(user.uid);
      
      if (existingProfile == null) {
        // 새 사용자 프로필 생성
        final newProfile = UserProfile(
          uid: user.uid,
          name: user.displayName ?? '사용자',
          email: user.email ?? '',
          studentId: '',
          major: '',
          department: '',
          university: '',
          grade: 1,
          semesterInfo: '',
          interestTags: [],
          subscribedChannels: [],
          createdAt: DateTime.now(),
          updatedAt: DateTime.now(),
        );
        
        await FirebaseService.instance.saveUserProfile(newProfile);
        debugPrint('새 사용자 프로필 생성: ${user.uid}');
      }
    } catch (e) {
      debugPrint('사용자 프로필 생성 오류: $e');
    }
  }

  // 이메일/비밀번호 로그인
  Future<void> signInWithEmailAndPassword(String email, String password) async {
    try {
      _setLoading(true);
      _clearError();

      final UserCredential userCredential = await _auth.signInWithEmailAndPassword(
        email: email,
        password: password,
      );

      _user = userCredential.user;
      
      debugPrint('이메일 로그인 성공: ${_user?.email}');
    } catch (e) {
      _setError('로그인 실패: $e');
      debugPrint('이메일 로그인 오류: $e');
      rethrow;
    } finally {
      _setLoading(false);
    }
  }

  // 이메일/비밀번호 회원가입
  Future<void> createUserWithEmailAndPassword(String email, String password) async {
    try {
      _setLoading(true);
      _clearError();

      final UserCredential userCredential = await _auth.createUserWithEmailAndPassword(
        email: email,
        password: password,
      );

      _user = userCredential.user;
      
      debugPrint('회원가입 성공: ${_user?.email}');
    } catch (e) {
      _setError('회원가입 실패: $e');
      debugPrint('회원가입 오류: $e');
      rethrow;
    } finally {
      _setLoading(false);
    }
  }

  // 로그아웃
  Future<void> signOut() async {
    try {
      _setLoading(true);
      _clearError();

      // 구글 로그아웃
      await _googleSignIn.signOut();
      
      // Firebase 로그아웃
      await _auth.signOut();
      
      _user = null;
      
      debugPrint('로그아웃 완료');
    } catch (e) {
      _setError('로그아웃 실패: $e');
      debugPrint('로그아웃 오류: $e');
      rethrow;
    } finally {
      _setLoading(false);
    }
  }

  // 계정 삭제
  Future<void> deleteAccount() async {
    try {
      _setLoading(true);
      _clearError();

      if (_user != null) {
        // Firebase에서 사용자 데이터 삭제
        await FirebaseService.instance.deleteUserProfile(_user!.uid);
        
        // Firebase Auth에서 계정 삭제
        await _user!.delete();
        
        _user = null;
        
        debugPrint('계정 삭제 완료');
      }
    } catch (e) {
      _setError('계정 삭제 실패: $e');
      debugPrint('계정 삭제 오류: $e');
      rethrow;
    } finally {
      _setLoading(false);
    }
  }

  // 로딩 상태 설정
  void _setLoading(bool loading) {
    _isLoading = loading;
    notifyListeners();
  }

  // 에러 설정
  void _setError(String error) {
    _error = error;
    notifyListeners();
  }

  // 에러 클리어
  void _clearError() {
    _error = null;
    notifyListeners();
  }

  // 에러 수동 클리어
  void clearError() {
    _clearError();
  }
}
