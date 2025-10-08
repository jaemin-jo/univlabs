# 🔄 LearnUs 클라우드 데이터 동기화 가이드

## 📋 개요

클라우드 백엔드에서 주기적으로 크롤링한 최신 과제 데이터를 로컬 `assignment.txt` 파일로 자동 동기화하는 도구입니다.

## 🎯 주요 기능

- ✅ **클라우드 데이터 실시간 동기화**: 클라우드 서버의 최신 과제 데이터를 로컬로 가져오기
- ✅ **자동 스케줄링**: 주기적으로 자동 동기화 (30분 간격)
- ✅ **수동 동기화**: 언제든지 즉시 동기화 가능
- ✅ **상태 모니터링**: 동기화 상태 및 통계 확인

## 🚀 사용 방법

### 1. 즉시 동기화 (수동)

```bash
# Python으로 실행
python sync_now.py

# 또는 배치 파일로 실행 (Windows)
sync_now.bat
```

### 2. 자동 동기화 (스케줄러)

```bash
# 자동 동기화 스케줄러 시작 (30분 간격)
python auto_sync_scheduler.py
```

### 3. 프로그래밍 방식

```python
from sync_cloud_data import CloudDataSyncer

# 동기화 객체 생성
syncer = CloudDataSyncer()

# 즉시 동기화
success = syncer.sync()

if success:
    print("동기화 완료!")
else:
    print("동기화 실패!")
```

## 📁 파일 구조

```
backend/
├── sync_cloud_data.py          # 핵심 동기화 클래스
├── auto_sync_scheduler.py       # 자동 스케줄러
├── sync_now.py                 # 즉시 동기화 스크립트
├── sync_now.bat                # Windows 배치 파일
├── assignment.txt              # 동기화된 과제 데이터 (자동 생성)
└── README_SYNC.md              # 이 가이드
```

## 🔧 설정 옵션

### 클라우드 서버 URL 변경

```python
# sync_cloud_data.py에서 수정
syncer = CloudDataSyncer(cloud_server_url="https://your-server.com")
```

### 동기화 간격 변경

```python
# auto_sync_scheduler.py에서 수정
scheduler = AutoSyncScheduler(sync_interval_minutes=60)  # 60분 간격
```

## 📊 동기화된 데이터 형식

```txt
=== LearnUs 과제 정보 업데이트 ===
업데이트 시간: 2025-10-07 03:09:17
클라우드 동기화 시간: 2025-10-07T02:57:47

📊 통계: 총 8개 과제, 미완료 8개

📚 이번주 해야 할 과제 목록
==================================================

📖 사회봉사 (연세머레이캠프) (YHQ1017.02-00)
----------------------------------------
  • 2025-2학기 사회봉사교과목 중간보고서 제출 안내 과제 (과제)
    상태: ❌ 해야 할 과제
```

## 🎯 클라우드 백엔드 크롤링 상태

### ✅ 정상 작동 중

클라우드 백엔드는 다음과 같이 정상적으로 작동하고 있습니다:

1. **자동 스케줄링**: 매일 09:00, 18:00에 자동 크롤링
2. **개발 모드**: 5분마다 크롤링 (테스트용)
3. **실시간 데이터**: 최신 LearnUs 과제 정보 수집
4. **API 엔드포인트**: `/assignments`로 데이터 제공

### 📈 크롤링 통계

- **총 과제**: 8개
- **미완료**: 8개
- **마지막 업데이트**: 실시간
- **서버 상태**: 정상 작동

## 🔍 문제 해결

### 동기화 실패 시

1. **클라우드 서버 연결 확인**
   ```bash
   curl https://learnus-backend-986202706020.asia-northeast3.run.app/health
   ```

2. **네트워크 연결 확인**
   ```bash
   ping learnus-backend-986202706020.asia-northeast3.run.app
   ```

3. **로그 확인**
   - 동기화 로그는 콘솔에 출력됩니다
   - 오류 메시지를 확인하여 문제를 파악하세요

### Flutter 앱에서 데이터가 안 보일 때

1. **로컬 서버 실행**
   ```bash
   cd backend
   python scheduler_server.py
   ```

2. **동기화 실행**
   ```bash
   python sync_now.py
   ```

3. **Flutter 앱 재시작**

## 📝 주의사항

- 동기화는 클라우드 서버의 데이터를 기반으로 합니다
- 로컬 `assignment.txt` 파일은 덮어쓰기됩니다
- 자동 스케줄러는 백그라운드에서 실행됩니다
- Ctrl+C로 스케줄러를 중지할 수 있습니다

## 🎉 완료!

이제 클라우드에서 주기적으로 얻는 최신 과제 데이터를 로컬 파일에 자동으로 동기화할 수 있습니다!

- **즉시 동기화**: `python sync_now.py`
- **자동 동기화**: `python auto_sync_scheduler.py`
- **Flutter 앱**: 최신 과제 정보 확인 가능
