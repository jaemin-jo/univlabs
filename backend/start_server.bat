@echo off
echo 학교 자동화 백엔드 서버 시작 중...

REM Python 가상환경 활성화 (있는 경우)
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

REM 의존성 설치
echo 의존성 설치 중...
pip install -r requirements.txt

REM 서버 시작
echo 서버 시작 중...
python run_server.py

pause
