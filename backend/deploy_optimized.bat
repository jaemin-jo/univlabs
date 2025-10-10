@echo off
echo 🚀 최적화된 자동화 배포
echo.
echo ⚡ 시간 제한 문제 해결:
echo    - Cloud Run 타임아웃: 60분 (3600초)
echo    - 병렬 처리로 속도 향상
echo    - 배치 처리로 안정성 확보
echo    - 상태 확인 최적화
echo.

cd /d "%~dp0"

echo 📦 최적화된 코드 배포 중...
gcloud run deploy learnus-backend \
  --source . \
  --platform managed \
  --region asia-northeast3 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 3600 \
  --max-instances 10

if %ERRORLEVEL% neq 0 (
    echo ❌ 배포 실패!
    pause
    exit /b 1
)

echo ✅ 최적화된 배포 완료!
echo.
echo 🔍 배포된 서비스 확인:
echo    URL: https://learnus-backend-986202706020.asia-northeast3.run.app
echo    헬스체크: https://learnus-backend-986202706020.asia-northeast3.run.app/health
echo    과제 정보: https://learnus-backend-986202706020.asia-northeast3.run.app/assignments
echo.
echo 🧪 배포 테스트:
timeout /t 30 /nobreak > nul
python sync_now.py

pause
