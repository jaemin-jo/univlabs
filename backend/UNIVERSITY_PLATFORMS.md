# 대학교별 온라인 학습 플랫폼 정보

각 대학교마다 고유한 온라인 학습 관리 시스템(LMS)을 사용합니다. 자동화 시스템이 각 플랫폼의 구조에 맞게 설정되어 있습니다.

## 지원 대학교 및 플랫폼

### 1. 연세대학교
- **플랫폼**: LearnUs (런어스)
- **URL**: https://ys.learnus.org/
- **특징**: 
  - 과제 제출 및 학사 공지
  - 강의 자료 다운로드
  - 온라인 강의 시청
  - 출석 체크

### 2. 고려대학교
- **플랫폼**: LMS (Learning Management System)
- **URL**: https://lms.korea.ac.kr/
- **특징**:
  - 과제 관리
  - 성적 확인
  - 강의 자료 공유

### 3. 서울대학교
- **플랫폼**: Blackboard
- **URL**: https://snu.blackboard.com/
- **특징**:
  - 국제 표준 LMS
  - 과제 제출 및 피드백
  - 토론 게시판

### 4. 한국과학기술원 (KAIST)
- **플랫폼**: KLMS
- **URL**: https://klms.kaist.ac.kr/
- **특징**:
  - 과제 및 프로젝트 관리
  - 실험 보고서 제출
  - 팀 프로젝트 지원

### 5. 포스텍 (POSTECH)
- **플랫폼**: LMS
- **URL**: https://lms.postech.ac.kr/
- **특징**:
  - 과제 및 시험 관리
  - 강의 녹화 영상
  - 성적 확인

## 자동화 시스템 설정

### 로그인 설정
각 대학교별로 로그인 폼의 구조가 다르므로, 실제 필드명과 선택자를 확인하여 설정해야 합니다.

```python
# 연세대학교 LearnUs 예시
"연세대학교": {
    "login_url": "https://ys.learnus.org/",
    "username_field": "username",  # 실제 필드명 확인 필요
    "password_field": "password",   # 실제 필드명 확인 필요
    "login_button": "button[type='submit']",
}
```

### 과제 정보 수집 설정
각 플랫폼의 HTML 구조에 맞는 CSS 선택자를 사용합니다.

```python
# 연세대학교 LearnUs 과제 파싱 설정
"연세대학교": {
    "assignment_url": "https://ys.learnus.org/",
    "assignment_list": ".course-list, .assignment-list",
    "assignment_item": ".course-item, .assignment-item",
    "title": ".course-title, .assignment-title",
    "description": ".course-description, .assignment-description",
    "due_date": ".due-date, .deadline",
    "course_name": ".course-name, .subject-name",
    "course_code": ".course-code, .subject-code",
    "status": ".assignment-status, .course-status",
}
```

## 새로운 대학교 추가 방법

1. **로그인 설정 추가**
   - `_get_login_config()` 함수에 새로운 대학교 설정 추가
   - 실제 로그인 폼의 필드명과 선택자 확인

2. **과제 파싱 설정 추가**
   - `_get_assignment_config()` 함수에 새로운 대학교 설정 추가
   - 해당 플랫폼의 HTML 구조 분석하여 CSS 선택자 설정

3. **Flutter 앱 업데이트**
   - `SchoolAutomationScreen`의 드롭다운 메뉴에 새로운 대학교 추가

## 주의사항

1. **학교 정책 준수**: 각 대학교의 이용약관을 확인하고 준수해야 합니다.
2. **보안**: 사용자의 로그인 정보는 암호화되어 저장됩니다.
3. **정기 업데이트**: 학교 웹사이트 구조 변경 시 설정 업데이트가 필요할 수 있습니다.
4. **테스트**: 새로운 대학교 추가 시 충분한 테스트를 거쳐야 합니다.

## 문제 해결

### 로그인 실패
- 로그인 폼의 필드명이 변경되었을 수 있습니다
- JavaScript로 동적 생성되는 요소인지 확인
- 캡차나 2단계 인증이 있는지 확인

### 과제 정보 수집 실패
- HTML 구조가 변경되었을 수 있습니다
- CSS 선택자를 업데이트해야 할 수 있습니다
- 로그인 상태가 유지되는지 확인

### 성능 최적화
- 각 대학교별로 적절한 대기 시간 설정
- 불필요한 요소 로딩 방지
- 에러 처리 및 재시도 로직 구현
