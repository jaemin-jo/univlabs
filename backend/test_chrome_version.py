#!/usr/bin/env python3
"""
Chrome 및 ChromeDriver 버전 확인 및 테스트
"""

import subprocess
import sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def check_chrome_version():
    """Chrome 버전 확인"""
    try:
        # Chrome 버전 확인
        result = subprocess.run(['google-chrome', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            chrome_version = result.stdout.strip()
            print(f"✅ Chrome 버전: {chrome_version}")
            return chrome_version
        else:
            print("❌ Chrome 버전 확인 실패")
            return None
    except Exception as e:
        print(f"❌ Chrome 버전 확인 오류: {e}")
        return None

def check_chromedriver_version():
    """ChromeDriver 버전 확인"""
    try:
        result = subprocess.run(['chromedriver', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            driver_version = result.stdout.strip()
            print(f"✅ ChromeDriver 버전: {driver_version}")
            return driver_version
        else:
            print("❌ ChromeDriver 버전 확인 실패")
            return None
    except Exception as e:
        print(f"❌ ChromeDriver 버전 확인 오류: {e}")
        return None

def test_selenium_connection():
    """Selenium 연결 테스트"""
    try:
        print("🔧 Selenium 연결 테스트 중...")
        
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        # WebDriver Manager로 자동 버전 관리
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # 간단한 테스트
        driver.get("https://www.google.com")
        title = driver.title
        driver.quit()
        
        print(f"✅ Selenium 연결 성공: {title}")
        return True
        
    except Exception as e:
        print(f"❌ Selenium 연결 실패: {e}")
        return False

def main():
    print("🔍 Chrome 및 ChromeDriver 버전 확인")
    print("=" * 50)
    
    # Chrome 버전 확인
    chrome_version = check_chrome_version()
    
    # ChromeDriver 버전 확인
    driver_version = check_chromedriver_version()
    
    # Selenium 연결 테스트
    selenium_success = test_selenium_connection()
    
    print("\n📊 결과 요약:")
    print(f"   Chrome: {'✅' if chrome_version else '❌'}")
    print(f"   ChromeDriver: {'✅' if driver_version else '❌'}")
    print(f"   Selenium: {'✅' if selenium_success else '❌'}")
    
    if selenium_success:
        print("\n🎉 모든 테스트 통과! 크롤링이 정상 작동할 것입니다.")
    else:
        print("\n⚠️ 문제가 있습니다. ChromeDriver 버전을 업데이트해야 합니다.")

if __name__ == "__main__":
    main()













