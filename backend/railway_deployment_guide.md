# Railway 배포 가이드

## 🚀 Railway로 백엔드 서버 배포하기

### **1. Railway 계정 생성**
1. [Railway.app](https://railway.app) 접속
2. GitHub 계정으로 로그인
3. 무료 계정 생성

### **2. 프로젝트 설정**

#### **requirements.txt 생성**
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

#### **Procfile 생성**
```
web: uvicorn scheduler_server:app --host 0.0.0.0 --port $PORT
```

#### **railway.json 생성**
```json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "uvicorn scheduler_server:app --host 0.0.0.0 --port $PORT",
    "healthcheckPath": "/health"
  }
}
```

### **3. 환경 변수 설정**
Railway 대시보드에서 다음 환경 변수 설정:

```
FIREBASE_PROJECT_ID=univlabs-ai
FIREBASE_PRIVATE_KEY_ID=your_private_key_id
FIREBASE_PRIVATE_KEY=your_private_key
FIREBASE_CLIENT_EMAIL=firebase-adminsdk-fbsvc@univlabs-ai.iam.gserviceaccount.com
FIREBASE_CLIENT_ID=your_client_id
FIREBASE_AUTH_URI=https://accounts.google.com/o/oauth2/auth
FIREBASE_TOKEN_URI=https://oauth2.googleapis.com/token
```

### **4. 배포 과정**
1. GitHub에 코드 푸시
2. Railway에서 "New Project" → "Deploy from GitHub repo"
3. 저장소 선택
4. 자동 배포 완료!

### **5. 비용**
- **무료 티어**: 월 500시간 (약 20일)
- **Pro 플랜**: 월 $5 (무제한)

## 🔧 **Docker 배포 방법 (대안)**

### **Dockerfile 생성**
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
EXPOSE 8000

# 앱 실행
CMD ["uvicorn", "scheduler_server:app", "--host", "0.0.0.0", "--port", "8000"]
```

### **docker-compose.yml 생성**
```yaml
version: '3.8'
services:
  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - FIREBASE_PROJECT_ID=univlabs-ai
    volumes:
      - ./firebase_service_account.json:/app/firebase_service_account.json
    restart: unless-stopped
```

## 📊 **비용 비교**

| 플랫폼 | 무료 티어 | 유료 플랜 | 특징 |
|--------|-----------|----------|------|
| **Railway** | 월 500시간 | $5/월 | 가장 간단 |
| **Heroku** | 월 550시간 | $7/월 | 인기 많음 |
| **DigitalOcean** | 없음 | $5/월 | 성능 좋음 |
| **AWS EC2** | 1년 무료 | $3-10/월 | 확장성 좋음 |
| **Google Cloud** | $300 크레딧 | $5-15/월 | Google 생태계 |

## 🎯 **추천 순서**

### **1단계: Railway (가장 추천)**
- 가장 간단하고 빠름
- 무료 티어로 테스트 가능
- GitHub 연동으로 자동 배포

### **2단계: Heroku (대안)**
- 인기 많고 안정적
- 무료 티어로 시작
- 확장성 좋음

### **3단계: DigitalOcean (비용 효율)**
- 비용 대비 성능 우수
- Docker 기반 배포
- 중간 규모까지 확장

## 🚀 **즉시 시작하기**

1. **Railway 계정 생성**
2. **GitHub에 코드 푸시**
3. **Railway에서 배포**
4. **환경 변수 설정**
5. **완료!** 🎉

이제 노트북을 끄고도 24시간 자동으로 백엔드가 돌아갑니다!
