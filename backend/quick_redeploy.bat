@echo off
echo 🚀 빠른 재배포 (Docker 없이)
echo.

cd /d "%~dp0"

echo 소스 코드를 Google Cloud Run에 직접 배포 중...
gcloud run deploy learnus-backend --source . --platform managed --region asia-northeast3 --allow-unauthenticated --memory 2Gi --cpu 2 --timeout 3600 --max-instances 10

if %ERRORLEVEL% neq 0 (
    echo ❌ 배포 실패!
    pause
    exit /b 1
)

echo ✅ 배포 완료!
echo.
echo 🧪 배포 테스트:
timeout /t 30 /nobreak > nul
python sync_now.py

pause
