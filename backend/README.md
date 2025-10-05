# 학교 홈페이지 자동화 백엔드

Flutter 앱과 통신하여 실제 학교 홈페이지에 로그인하고 과제 정보를 수집하는 Python 백엔드 서버입니다.

## 기능

- 🎓 대학교별 로그인 자동화
- 📚 과제 정보 자동 수집
- 🔔 새로운 과제 및 마감 임박 알림
- ⏰ 주기적 자동화 실행
- 📱 Flutter 앱과 REST API 통신

## 지원 대학교

- **연세대학교** - LearnUs (https://ys.learnus.org/)
- **고려대학교** - LMS (https://lms.korea.ac.kr/)
- **서울대학교** - Blackboard (https://snu.blackboard.com/)
- **한국과학기술원** - KLMS (https://klms.kaist.ac.kr/)
- **포스텍** - LMS (https://lms.postech.ac.kr/)

## 설치 및 실행

### 1. 의존성 설치

```bash
cd backend
pip install -r requirements.txt
```

### 2. 환경 변수 설정

```bash
cp env_example.txt .env
# .env 파일을 편집하여 실제 값들로 수정
```

### 3. 서버 실행

```bash
python run_server.py
```

또는

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## API 엔드포인트

### 기본
- `GET /health` - 서버 상태 확인

### 인증
- `POST /login` - 학교 홈페이지 로그인

### 과제 정보
- `GET /assignments` - 모든 과제 조회
- `GET /assignments/new` - 새로운 과제 조회
- `GET /assignments/upcoming` - 마감 임박 과제 조회
- `POST /assignments/refresh` - 수동 과제 정보 업데이트

### 자동화
- `POST /automation/start` - 자동화 시작
- `POST /automation/stop` - 자동화 중지
- `GET /automation/status` - 자동화 상태 확인

## 사용 방법

### 1. Flutter 앱에서 자격 증명 설정

```dart
await SchoolAutomationService.instance.saveUserCredentials(
  university: '연세대학교',
  username: 'your_username',
  password: 'your_password',
  studentId: 'your_student_id',
);
```

### 2. 로그인 및 과제 정보 수집

```dart
// 로그인
bool loginSuccess = await SchoolAutomationService.instance.loginToSchool();

if (loginSuccess) {
  // 과제 정보 수집
  List<Assignment> assignments = await SchoolAutomationService.instance.fetchAssignments();
  
  // 새로운 과제 확인
  List<Assignment> newAssignments = await SchoolAutomationService.instance.checkNewAssignments();
  
  // 마감 임박 과제 확인
  List<Assignment> upcomingAssignments = await SchoolAutomationService.instance.checkUpcomingDeadlines();
}
```

### 3. 자동화 시작

```dart
// 자동화 시작 (1시간마다 자동 실행)
bool started = await SchoolAutomationService.instance.startAutomation();
```

## 보안 주의사항

- 사용자의 아이디와 비밀번호는 암호화되어 저장됩니다
- HTTPS를 사용하여 통신을 암호화하세요
- 프로덕션 환경에서는 적절한 인증 및 권한 관리를 구현하세요

## 문제 해결

### Chrome 드라이버 오류
- Chrome 브라우저가 설치되어 있는지 확인
- webdriver-manager가 자동으로 드라이버를 다운로드합니다

### 로그인 실패
- 학교 홈페이지의 로그인 폼 구조가 변경되었을 수 있습니다
- `services/school_automation.py`의 `_get_login_config` 함수를 수정하세요

### 과제 정보 수집 실패
- LMS 시스템의 구조가 변경되었을 수 있습니다
- `services/assignment_parser.py`의 선택자를 수정하세요

## 개발자 정보

이 프로젝트는 Flutter 앱과 연동하여 학교 홈페이지 자동화 기능을 제공합니다.
