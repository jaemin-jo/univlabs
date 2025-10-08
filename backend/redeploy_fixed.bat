@echo off
echo 🔄 ChromeDriver 버전 문제 해결을 위한 클라우드 재배포
echo.

cd /d "%~dp0"

echo 📦 Docker 이미지 빌드 중...
docker build -t learnus-backend-fixed .

if %ERRORLEVEL% neq 0 (
    echo ❌ Docker 빌드 실패!
    pause
    exit /b 1
)

echo 🚀 Google Cloud Run에 배포 중...
gcloud run deploy learnus-backend \
  --image learnus-backend-fixed \
  --platform managed \
  --region asia-northeast3 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 900 \
  --max-instances 10

if %ERRORLEVEL% neq 0 (
    echo ❌ 배포 실패!
    pause
    exit /b 1
)

echo ✅ 배포 완료!
echo.
echo 🔍 배포된 서비스 확인:
echo    URL: https://learnus-backend-986202706020.asia-northeast3.run.app
echo    헬스체크: https://learnus-backend-986202706020.asia-northeast3.run.app/health
echo    과제 정보: https://learnus-backend-986202706020.asia-northeast3.run.app/assignments
echo.
echo 🔍 로그 확인: https://console.cloud.google.com/run/detail/asia-northeast3/learnus-backend/logs
echo.
echo 🧪 테스트 실행:
python sync_now.py

pause
