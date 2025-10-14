@echo off
echo 🔄 LearnUs 클라우드 데이터 동기화 시작...
echo.

cd /d "%~dp0"

python sync_now.py

echo.
echo 동기화 완료! 아무 키나 누르면 종료됩니다.
pause > nul















