# GCP 배포 가이드 - 24시간 자동화 백엔드

## 🎯 **목표**
- 노트북을 끄고도 24시간 자동으로 LearnUs 과제 정보 업데이트
- 5분마다 Selenium 자동화 실행
- Firebase와 완벽 통합

## 🚀 **1단계: GCP 계정 생성**

### **1.1 Google Cloud Console 접속**
1. [Google Cloud Console](https://console.cloud.google.com) 접속
2. Google 계정으로 로그인
3. **$300 크레딧 활성화** (1년 무료!)

### **1.2 프로젝트 생성**
1. "새 프로젝트" 클릭
2. 프로젝트 이름: `univlabs-backend`
3. 조직: 선택 (없으면 건너뛰기)
4. "만들기" 클릭

## 🔧 **2단계: 필요한 서비스 활성화**

### **2.1 Cloud Run 활성화**
```bash
# Cloud Run API 활성화
gcloud services enable run.googleapis.com
```

### **2.2 Cloud Build 활성화**
```bash
# Cloud Build API 활성화
gcloud services enable cloudbuild.googleapis.com
```

### **2.3 Container Registry 활성화**
```bash
# Container Registry API 활성화
gcloud services enable containerregistry.googleapis.com
```

## 📦 **3단계: 코드 준비**

### **3.1 requirements.txt 생성**
```txt
fastapi==0.104.1
uvicorn==0.24.0
selenium==4.15.2
webdriver-manager==4.0.1
schedule==1.2.0
firebase-admin==6.2.0
google-cloud-firestore==2.13.1
requests==2.31.0
python-multipart==0.0.6
```

### **3.2 Dockerfile 생성**
```dockerfile
FROM python:3.11-slim

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 패키지 업데이트 및 Chrome 설치
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 앱 코드 복사
COPY . .

# 포트 노출
EXPOSE 8080

# 앱 실행
CMD ["uvicorn", "scheduler_server:app", "--host", "0.0.0.0", "--port", "8080"]
```

### **3.3 cloudbuild.yaml 생성**
```yaml
steps:
  # Docker 이미지 빌드
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/learnus-backend', '.']
  
  # Docker 이미지 푸시
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/learnus-backend']
  
  # Cloud Run에 배포
  - name: 'gcr.io/cloud-builders/gcloud'
    args: [
      'run', 'deploy', 'learnus-backend',
      '--image', 'gcr.io/$PROJECT_ID/learnus-backend',
      '--platform', 'managed',
      '--region', 'asia-northeast3',
      '--allow-unauthenticated',
      '--memory', '2Gi',
      '--cpu', '2',
      '--timeout', '3600'
    ]
```

## 🔐 **4단계: 환경 변수 설정**

### **4.1 Firebase 서비스 계정 키**
1. Firebase Console → 프로젝트 설정 → 서비스 계정
2. "새 비공개 키 생성" 클릭
3. JSON 파일 다운로드
4. 파일명을 `firebase_service_account.json`으로 변경

### **4.2 환경 변수 설정**
Cloud Run에서 다음 환경 변수 설정:

```
FIREBASE_PROJECT_ID=univlabs-ai
FIREBASE_PRIVATE_KEY_ID=your_private_key_id
FIREBASE_PRIVATE_KEY=your_private_key
FIREBASE_CLIENT_EMAIL=firebase-adminsdk-fbsvc@univlabs-ai.iam.gserviceaccount.com
FIREBASE_CLIENT_ID=your_client_id
FIREBASE_AUTH_URI=https://accounts.google.com/o/oauth2/auth
FIREBASE_TOKEN_URI=https://oauth2.googleapis.com/token
```

## 🚀 **5단계: 배포**

### **5.1 GitHub에 코드 푸시**
```bash
git add .
git commit -m "GCP 배포 준비"
git push origin main
```

### **5.2 Cloud Build로 배포**
```bash
# Cloud Build 실행
gcloud builds submit --config cloudbuild.yaml
```

### **5.3 배포 확인**
```bash
# Cloud Run 서비스 확인
gcloud run services list

# 서비스 URL 확인
gcloud run services describe learnus-backend --region=asia-northeast3
```

## 📊 **6단계: 모니터링 및 관리**

### **6.1 로그 확인**
```bash
# Cloud Run 로그 확인
gcloud logs read --service=learnus-backend --limit=50
```

### **6.2 서비스 상태 확인**
```bash
# 서비스 상태 확인
curl https://learnus-backend-xxxxx-uc.a.run.app/health
```

### **6.3 자동화 실행 확인**
```bash
# 자동화 실행
curl -X POST https://learnus-backend-xxxxx-uc.a.run.app/automation/run
```

## 💰 **7단계: 비용 관리**

### **7.1 예상 비용**
- **Cloud Run**: 월 $5-15 (사용량 기반)
- **Cloud Build**: 월 $1-3 (빌드 횟수 기반)
- **Container Registry**: 월 $1-2 (이미지 저장)
- **총 예상 비용**: 월 $7-20

### **7.2 비용 절약 팁**
1. **자동 스케일링**: 사용하지 않을 때 0으로 스케일링
2. **리전 선택**: asia-northeast3 (도쿄) 선택
3. **메모리 최적화**: 2GB 메모리로 설정
4. **타임아웃 설정**: 3600초 (1시간) 설정

## 🔧 **8단계: 문제 해결**

### **8.1 일반적인 문제**
1. **Chrome 설치 실패**: Dockerfile에서 Chrome 설치 확인
2. **Firebase 연결 실패**: 환경 변수 확인
3. **메모리 부족**: Cloud Run 메모리 증가
4. **타임아웃**: Cloud Run 타임아웃 증가

### **8.2 로그 확인**
```bash
# 실시간 로그 확인
gcloud logs tail --service=learnus-backend
```

## 🎯 **9단계: 완료 확인**

### **9.1 서비스 상태 확인**
```bash
# 헬스체크
curl https://learnus-backend-xxxxx-uc.a.run.app/health

# 과제 정보 확인
curl https://learnus-backend-xxxxx-uc.a.run.app/assignments
```

### **9.2 자동화 실행 확인**
```bash
# 자동화 실행
curl -X POST https://learnus-backend-xxxxx-uc.a.run.app/automation/run
```

## 🎉 **완료!**

**이제 노트북을 끄고도 24시간 자동으로 LearnUs 과제 정보가 업데이트됩니다!**

### **✅ 확인 사항:**
1. **24시간 자동 실행**: ✅
2. **5분마다 자동화**: ✅
3. **Selenium 실행**: ✅
4. **Firebase 통합**: ✅
5. **비용 효율**: ✅ ($300 크레딧으로 1년 무료)

### **📱 Flutter 앱에서 확인:**
1. Flutter 앱 실행
2. 과제 탭에서 아이디/비밀번호 입력
3. 실시간으로 과제 정보 확인

**이제 진짜 프로덕션 환경에서 24시간 자동화가 돌아갑니다!** 🚀
