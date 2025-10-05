"""
개발 환경 설정 스크립트
- 가상환경 생성
- 패키지 설치
- 환경 변수 설정
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """명령어 실행"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} 완료")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} 실패: {e}")
        print(f"오류 출력: {e.stderr}")
        return False

def setup_python_environment():
    """Python 환경 설정"""
    print("🐍 Python 환경 설정 시작")
    
    # 1. 가상환경 생성
    if not run_command("python -m venv venv", "가상환경 생성"):
        return False
    
    # 2. 가상환경 활성화 (Windows)
    if os.name == 'nt':  # Windows
        activate_cmd = "venv\\Scripts\\activate"
    else:  # Linux/Mac
        activate_cmd = "source venv/bin/activate"
    
    # 3. pip 업그레이드
    if not run_command(f"{activate_cmd} && python -m pip install --upgrade pip", "pip 업그레이드"):
        return False
    
    # 4. 필수 패키지 설치
    packages = [
        "fastapi==0.104.1",
        "uvicorn==0.24.0",
        "selenium==4.15.2",
        "beautifulsoup4==4.12.2",
        "requests==2.31.0",
        "python-dotenv==1.0.0",
        "pydantic==2.5.0",
        "python-multipart==0.0.6",
        "cryptography==41.0.7",
        "schedule==1.2.0",
        "python-dateutil==2.8.2",
        "lxml==4.9.3",
        "webdriver-manager==4.0.1"
    ]
    
    for package in packages:
        if not run_command(f"{activate_cmd} && pip install {package}", f"{package} 설치"):
            return False
    
    print("✅ Python 환경 설정 완료")
    return True

def create_startup_scripts():
    """시작 스크립트 생성"""
    print("📝 시작 스크립트 생성")
    
    # Windows 배치 파일
    windows_script = """@echo off
echo 🚀 백엔드 서버 시작 중...
cd /d "%~dp0"
call venv\\Scripts\\activate
python run_server.py
pause
"""
    
    with open("start_server_windows.bat", "w", encoding="utf-8") as f:
        f.write(windows_script)
    
    # Linux/Mac 셸 스크립트
    unix_script = """#!/bin/bash
echo "🚀 백엔드 서버 시작 중..."
cd "$(dirname "$0")"
source venv/bin/activate
python run_server.py
"""
    
    with open("start_server_unix.sh", "w", encoding="utf-8") as f:
        f.write(unix_script)
    
    # 실행 권한 부여 (Unix)
    if os.name != 'nt':
        os.chmod("start_server_unix.sh", 0o755)
    
    print("✅ 시작 스크립트 생성 완료")

def main():
    """메인 설정 함수"""
    print("🔧 자동화 시스템 환경 설정")
    print("=" * 50)
    
    if setup_python_environment():
        create_startup_scripts()
        print("\n🎉 환경 설정 완료!")
        print("\n📋 다음 단계:")
        print("1. Windows: start_server_windows.bat 실행")
        print("2. Linux/Mac: ./start_server_unix.sh 실행")
        print("3. Flutter 앱에서 테스트")
    else:
        print("\n❌ 환경 설정 실패")
        sys.exit(1)

if __name__ == "__main__":
    main()
