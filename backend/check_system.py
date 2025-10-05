#!/usr/bin/env python3
"""
시스템 상태 확인 도구
자동화 시스템이 정상 작동하는지 확인합니다.
"""

import sys
import os
import subprocess
import importlib

def check_python_packages():
    """Python 패키지 설치 상태 확인"""
    print("📦 Python 패키지 확인")
    print("-" * 30)
    
    required_packages = [
        'fastapi',
        'uvicorn', 
        'selenium',
        'requests',
        'beautifulsoup4',
        'webdriver_manager'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'beautifulsoup4':
                importlib.import_module('bs4')
                print(f"✅ {package} (bs4)")
            else:
                importlib.import_module(package)
                print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - 설치 필요")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n🔧 설치 명령어:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    else:
        print("✅ 모든 필수 패키지가 설치되어 있습니다.")
        return True

def check_chrome_driver():
    """Chrome 드라이버 확인"""
    print("\n🌐 Chrome 드라이버 확인")
    print("-" * 30)
    
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from webdriver_manager.chrome import ChromeDriverManager
        
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        print("Chrome 드라이버 다운로드 중...")
        driver_path = ChromeDriverManager().install()
        print(f"✅ Chrome 드라이버 설치됨: {driver_path}")
        
        print("Chrome 브라우저 테스트 중...")
        driver = webdriver.Chrome(options=chrome_options)
        driver.get("https://www.google.com")
        title = driver.title
        driver.quit()
        
        print(f"✅ Chrome 브라우저 정상 작동: {title}")
        return True
        
    except Exception as e:
        print(f"❌ Chrome 드라이버 오류: {e}")
        return False

def check_network_connectivity():
    """네트워크 연결 확인"""
    print("\n🌍 네트워크 연결 확인")
    print("-" * 30)
    
    test_urls = [
        "https://www.google.com",
        "https://ys.learnus.org/",
        "http://localhost:8000"
    ]
    
    try:
        import requests
        
        for url in test_urls:
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    print(f"✅ {url} - 연결 성공")
                else:
                    print(f"⚠️ {url} - 상태 코드: {response.status_code}")
            except requests.exceptions.RequestException as e:
                print(f"❌ {url} - 연결 실패: {e}")
                
    except ImportError:
        print("❌ requests 모듈이 설치되지 않았습니다.")

def check_backend_server():
    """백엔드 서버 상태 확인"""
    print("\n🖥️ 백엔드 서버 확인")
    print("-" * 30)
    
    try:
        import requests
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ 백엔드 서버 실행 중")
            return True
        else:
            print(f"⚠️ 백엔드 서버 응답 오류: {response.status_code}")
            return False
    except requests.exceptions.RequestException:
        print("❌ 백엔드 서버가 실행되지 않았습니다.")
        print("💡 해결방법: cd backend && python run_server.py")
        return False

def main():
    """메인 진단 함수"""
    print("🔍 자동화 시스템 진단 도구")
    print("=" * 50)
    
    checks = [
        ("Python 패키지", check_python_packages),
        ("Chrome 드라이버", check_chrome_driver),
        ("네트워크 연결", check_network_connectivity),
        ("백엔드 서버", check_backend_server)
    ]
    
    results = []
    
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ {name} 확인 중 오류: {e}")
            results.append((name, False))
    
    # 결과 요약
    print("\n📊 진단 결과 요약")
    print("=" * 50)
    
    all_passed = True
    for name, result in results:
        status = "✅ 통과" if result else "❌ 실패"
        print(f"{name}: {status}")
        if not result:
            all_passed = False
    
    if all_passed:
        print("\n🎉 모든 진단이 통과했습니다!")
        print("자동화 기능을 사용할 수 있습니다.")
    else:
        print("\n⚠️ 일부 진단이 실패했습니다.")
        print("위의 오류를 해결한 후 다시 시도해주세요.")
    
    print("\n💡 자격증명 테스트:")
    print("python test_credentials.py")

if __name__ == "__main__":
    main()
