# Firebase 설정 가이드

## 1. Firebase 프로젝트 생성

1. [Firebase Console](https://console.firebase.google.com/)에 접속
2. "프로젝트 추가" 클릭
3. 프로젝트 이름 입력 (예: univlabs-ai)
4. Google Analytics 설정 (선택사항)
5. 프로젝트 생성 완료

## 2. Android 앱 추가

1. Firebase 프로젝트에서 "Android 앱 추가" 클릭
2. Android 패키지 이름 입력: `com.example.univlabs`
3. 앱 닉네임 입력: `univlabs`
4. SHA-1 인증서 지문 추가 (선택사항)
5. `google-services.json` 파일 다운로드
6. 다운로드한 파일을 `android/app/` 폴더에 복사

## 3. Gemini API 활성화

### Gemini Developer API 사용 (권장)
1. [Google AI Studio](https://aistudio.google.com/)에 접속
2. API 키 생성
3. 환경 변수에 API 키 설정

### Vertex AI 사용
1. [Google Cloud Console](https://console.cloud.google.com/)에서 프로젝트 선택
2. Vertex AI API 활성화
3. 서비스 계정 생성 및 키 다운로드

## 4. Firestore 보안 규칙 설정

1. Firebase Console에서 "Firestore Database" 선택
2. "규칙" 탭 클릭
3. 다음 규칙을 복사하여 붙여넣기:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // 사용자 프로필 - 인증된 사용자만 자신의 프로필에 접근 가능
    match /users/{userId} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
    
    // 공지사항 - 모든 인증된 사용자가 읽기 가능
    match /announcements/{announcementId} {
      allow read: if request.auth != null;
      allow write: if request.auth != null;
    }
    
    // 기본 규칙 - 모든 인증된 사용자가 읽기 가능
    match /{document=**} {
      allow read: if request.auth != null;
      allow write: if request.auth != null;
    }
  }
}
```

4. "게시" 버튼 클릭하여 규칙 적용

## 5. 의존성 설치

```bash
flutter pub get
```

## 6. 빌드 및 실행

```bash
flutter run
```

## 주의사항

- `google-services.json` 파일이 `android/app/` 폴더에 있는지 확인
- 마이크 권한이 AndroidManifest.xml에 추가되었는지 확인
- Firebase 프로젝트에서 Gemini API가 활성화되었는지 확인

## 문제 해결

### Firestore 권한 오류 (PERMISSION_DENIED)
- Firebase Console에서 Firestore 보안 규칙이 올바르게 설정되었는지 확인
- 사용자가 인증되었는지 확인 (로그인 상태)
- 보안 규칙이 게시되었는지 확인

### 권한 오류
- 앱 설정에서 마이크 권한이 허용되었는지 확인
- Android 6.0 이상에서는 런타임 권한 요청이 필요

### API 오류
- Firebase 프로젝트 설정 확인
- API 키가 올바른지 확인
- 네트워크 연결 상태 확인
