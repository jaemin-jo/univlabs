@echo off
echo 🔧 Cloud Run 로컬 테스트 파이프라인
echo ================================================
echo.

REM Python 가상환경 활성화 (선택사항)
REM call venv\Scripts\activate

REM 필요한 패키지 설치
echo 📦 필요한 패키지 설치 중...
pip install requests

REM 테스트 파이프라인 실행
echo 🚀 테스트 파이프라인 시작...
python local_test_pipeline.py

echo.
echo 📋 테스트 완료! pipeline_test.log 파일을 확인하세요.
pause







