#!/usr/bin/env python3
"""
과제 자동화 서버 시작 스크립트
Flutter 앱과 연동되는 백엔드 서버
"""

import subprocess
import sys
import os
import time
import requests
from pathlib import Path

def check_server_running():
    """서버가 실행 중인지 확인"""
    try:
        response = requests.get('http://localhost:8000/health', timeout=5)
        return response.status_code == 200
    except:
        return False

def start_server():
    """서버 시작"""
    print("🚀 LearnUs 자동화 서버 시작 중...")
    
    # 서버가 이미 실행 중인지 확인
    if check_server_running():
        print("✅ 서버가 이미 실행 중입니다!")
        return True
    
    # 서버 디렉토리로 이동
    server_dir = Path(__file__).parent
    os.chdir(server_dir)
    
    try:
        # 필요한 패키지 설치
        print("📦 필요한 패키지 설치 중...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                      check=True, capture_output=True)
        
        # 서버 시작
        print("🌐 서버 시작 중...")
        process = subprocess.Popen([
            sys.executable, 'server_architecture.py'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # 서버 시작 대기
        print("⏳ 서버 시작 대기 중...")
        for i in range(30):  # 30초 대기
            time.sleep(1)
            if check_server_running():
                print("✅ 서버가 성공적으로 시작되었습니다!")
                print("📱 Flutter 앱에서 http://localhost:8000 으로 연결됩니다.")
                return True
            print(f"   {i+1}/30초 대기 중...")
        
        print("❌ 서버 시작에 실패했습니다.")
        return False
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return False

def main():
    print("=" * 50)
    print("🎓 LearnUs 과제 자동화 서버")
    print("=" * 50)
    
    if start_server():
        print("\n🎉 서버가 준비되었습니다!")
        print("📱 이제 Flutter 앱에서 '과제' 탭을 사용할 수 있습니다.")
        print("\n💡 서버를 중지하려면 Ctrl+C를 누르세요.")
        
        try:
            # 서버가 계속 실행되도록 대기
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n👋 서버를 종료합니다.")
    else:
        print("\n❌ 서버 시작에 실패했습니다.")
        print("🔧 문제 해결 방법:")
        print("   1. 포트 8000이 사용 중인지 확인")
        print("   2. Python 패키지가 올바르게 설치되었는지 확인")
        print("   3. 방화벽 설정 확인")

if __name__ == "__main__":
    main()
















