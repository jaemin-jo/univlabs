# Firebase 설정 가이드

## 1. Firebase Console에서 서비스 계정 키 생성

1. [Firebase Console](https://console.firebase.google.com/) 접속
2. 프로젝트 선택
3. **프로젝트 설정** → **서비스 계정** 탭
4. **새 비공개 키 생성** 클릭
5. JSON 파일 다운로드
6. 파일명을 `firebase_service_account.json`으로 변경
7. `backend/` 폴더에 저장

## 2. Firebase 규칙 설정

Firestore 규칙을 다음과 같이 설정:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // 사용자 프로필 - 인증된 사용자만 자신의 프로필에 접근 가능
    match /users/{userId} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
    
    // 사용자 프로필 - 인증된 사용자만 자신의 프로필에 접근 가능
    match /user_profiles/{userId} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
    
    // LearnUs 인증 정보 - 인증된 사용자만 자신의 정보에 접근 가능
    match /learnus_credentials/{userId} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
    
    // 공지사항 - 모든 인증된 사용자가 읽기 가능
    match /announcements/{announcementId} {
      allow read: if request.auth != null;
      allow write: if request.auth != null; // 관리자만 쓰기 가능하도록 나중에 수정
    }
    
    // 대학교 정보 - 모든 인증된 사용자가 읽기 가능
    match /universities/{universityId} {
      allow read: if request.auth != null;
      allow write: if request.auth != null; // 관리자만 쓰기 가능하도록 나중에 수정
    }
    
    // 기본 규칙 - 모든 인증된 사용자가 읽기 가능
    match /{document=**} {
      allow read: if request.auth != null;
      allow write: if request.auth != null;
    }
  }
}
```

## 3. 백엔드에서 Firebase 연결 테스트

```bash
cd backend
python add_real_user.py
```

## 4. 자동화 실행 테스트

```bash
curl -X POST http://localhost:8000/automation/run
```