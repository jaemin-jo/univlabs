#!/bin/bash

# GCP VM에서 Docker로 배포하는 스크립트
# Firebase 연결 문제 해결을 위한 완전한 배포 스크립트

echo "🚀 GCP VM Docker 배포 시작..."

# 1. Docker 이미지 빌드
echo "📦 Docker 이미지 빌드 중..."
docker build -f Dockerfile.simple -t univlabs-automation:latest .

# 2. 기존 컨테이너 중지 및 제거
echo "🛑 기존 컨테이너 중지 및 제거..."
docker-compose down
docker container prune -f

# 3. Firebase 서비스 계정 키 파일 확인
echo "🔍 Firebase 서비스 계정 키 파일 확인..."
if [ ! -f "firebase_service_account.json" ]; then
    echo "❌ firebase_service_account.json 파일이 없습니다!"
    echo "💡 Firebase 콘솔에서 서비스 계정 키를 다운로드하여 backend/ 디렉토리에 저장하세요."
    exit 1
fi

# 4. 환경변수 설정 파일 생성
echo "🔧 환경변수 설정 파일 생성..."
cat > .env << EOF
# Firebase 설정
FIREBASE_PROJECT_ID=univlabs-ai
FIREBASE_PRIVATE_KEY_ID=b8bf857a1c94fcabe3d40f1bca598f3a15b05d9e
FIREBASE_PRIVATE_KEY=-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCRETPmyUaPXH/5\noUGK+zwXRnfGjdQ3onctu4Z+yQTn99qFB9+wwxHuV3K5tZOSMn+PE3brblRISGU/\nJIjj++Mh8SLYrz0EQS8qza5jjujL+VCe73b/sqNdfv07s1KrtLQiX9eiulZKJAnP\nrIBVMAPp9IkPq8HZbhJg6l5hBiM2iTAINbdMEXkEmNvGlfLtwaDyIPmZ+/neTXXn\n7M8vmCLArftKVdABxNuAX+MufZoX/gIot2hpGBl3167vF9yHnBBjaBulhX0xmkVk\nRbaXK8ApFPCOBb0DhnlU79W0sBeHvIsZ0Ip5rfciDWEf0//sVdBBGu4hWF5u+8ya\n/7TEWooFAgMBAAECggEAF/XP7T/0VAxypMACK9roJ23/rX9SfGfsqFSPV9SK52d0\nI8HTrAXkKcouzEaV27FUiUStQSCFcjTm6CF4LLO3Za1G1KRI/zFnAXpcYdxCTiJd\nMwsZTA1s1y341In/TxX3JLBQ1PNS+kbuiesTfT6DfvphQwHa8DcyeOhs8ziIy2Jo\nsDCPyybnLeVakYYTjgOPGr1m07jaCH1WdBVPx4mWdKYayrpwgFCi7psope47xJ61\n6ZZw4OJzskwl0jiWBmbwox/GQ++7jFIJZZDR/3kI0QsyDtxXAmSjRj+INwjO1SS9\nlyaEW+6gpKPy3V5e+yyzrFXT4ohuo7VppDv/gfx6AQKBgQDBK0tcSoH6rDZ1v7WE\nTPahRbU7nP23P4hw9zXScMgxoIAH8S+BAYoPSZAUqU86LiSOXFHSOsudKOjoG+9M\n3VqxYLBWlQXUugh4mg1UZxmtnvH7ylV+Y3SB4slxopZSGNBmo030ZHd//6/i7Ibc\n1M3+jm3fpKcJFtrGzEwRuWSpBQKBgQDAQJUrHBRT+x6eSxF0881NQyR7opYuoLlK\nS8Lf62VQ1/x85qFv6m7SbadxH8K9ExJsrz1h4gUAWj26xDO01NaOA3oLtshAlTyM\nV1K6a1AutHhIePHjb94uSwaI/6o3kdD8lGa25gT2yne1fJldYFtHIaRcKDsaSWfV\noPiVOEAtAQKBgApzpz41IddIXiH833trFqUfOnEhS3EQ1PcXySe7xnk47/R+Dk3y\noV+2YT9c8dZ6DKxPPnYbjEzSm9eDO21zRKb4TlJA+fHKpw6vdy0r7u2//ePbzMhr\n5S/p73BglbWXdh83ks44aWbZlNC4b4ufUA4H8tX4+Li7Ldc30p3a5CFpAoGBAK7Q\nCtOQTMuwZD77c3ws1FmU2++v/2+WpeVwzlpd6VqBiwzniZQCT5L4MnEiuCjE1tQM\n5HvE0VdotwjEr1+WySGI98j/A0f2a4ARRyBLxDUz1MvRbeGpLxZZEjAwic7NwIJr\nTpqwvYLKx9821R2bKGSdqp5B1rwoU0plfKPy6igBAoGAM6/L+uHwRYGll0tkKix+\nORa/KE3Er/QCg6OXYzO4fphAd/yrxbQjD1RVm0Se7F1AXaKXt/48pgmiazra1OVc\n1YFTi3XqasbTSdJla3RTOOtKjcq3Ym8/9GcdlX9Deyjkrc6vGX64Sp8KpyyZW7hB\n/tOOSKwpOJNPfcCNPm7uh2E=\n-----END PRIVATE KEY-----\n
FIREBASE_CLIENT_EMAIL=firebase-adminsdk-fbsvc@univlabs-ai.iam.gserviceaccount.com
FIREBASE_CLIENT_ID=110322192572543241401
FIREBASE_AUTH_URI=https://accounts.google.com/o/oauth2/auth
FIREBASE_TOKEN_URI=https://oauth2.googleapis.com/token
GOOGLE_APPLICATION_CREDENTIALS=/app/firebase_service_account.json

# 서버 설정
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=INFO
DATABASE_URL=sqlite:///./learnus_automation.db
EOF

# 5. Docker Compose로 서비스 시작
echo "🚀 Docker Compose로 서비스 시작..."
docker-compose up -d

# 6. 컨테이너 상태 확인
echo "🔍 컨테이너 상태 확인..."
docker-compose ps

# 7. 로그 확인
echo "📋 초기 로그 확인..."
docker-compose logs --tail=50 learnus-automation

# 8. Firebase 연결 테스트
echo "🧪 Firebase 연결 테스트..."
sleep 10
curl -f http://localhost:8000/health || echo "❌ 헬스체크 실패"

# 9. 배포 완료 메시지
echo "✅ 배포 완료!"
echo "🌐 서버 주소: http://localhost:8000"
echo "📋 API 문서: http://localhost:8000/docs"
echo "🔍 헬스체크: http://localhost:8000/health"
echo "📝 과제 정보: http://localhost:8000/assignments"
echo ""
echo "🔧 문제 해결을 위한 명령어:"
echo "  - 로그 확인: docker-compose logs -f learnus-automation"
echo "  - 컨테이너 재시작: docker-compose restart learnus-automation"
echo "  - 서비스 중지: docker-compose down"
