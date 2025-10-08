#!/usr/bin/env python3
"""
Chrome 옵션 충돌 문제 해결을 위한 단계별 테스트
"""

import sys
import os
import time
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_chrome_options_step_by_step():
    """Chrome 옵션을 단계별로 테스트"""
    
    print("=" * 80)
    print("Chrome 옵션 충돌 문제 해결 테스트")
    print("=" * 80)
    
    # 1단계: 최소 옵션으로 테스트
    print("\n1단계: 최소 옵션으로 테스트")
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.get("https://www.google.com")
        print("최소 옵션 성공!")
        driver.quit()
    except Exception as e:
        print(f"최소 옵션 실패: {e}")
    
    # 2단계: DevTools 포트 추가
    print("\n2단계: DevTools 포트 추가")
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--remote-debugging-port=9222")
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.get("https://www.google.com")
        print("DevTools 포트 성공!")
        driver.quit()
    except Exception as e:
        print(f"DevTools 포트 실패: {e}")
    
    # 3단계: 단일 프로세스 추가
    print("\n3단계: 단일 프로세스 추가")
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--remote-debugging-port=9222")
        chrome_options.add_argument("--single-process")
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.get("https://www.google.com")
        print("단일 프로세스 성공!")
        driver.quit()
    except Exception as e:
        print(f"단일 프로세스 실패: {e}")
    
    # 4단계: GPU 비활성화 추가
    print("\n4단계: GPU 비활성화 추가")
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--remote-debugging-port=9222")
        chrome_options.add_argument("--single-process")
        chrome_options.add_argument("--disable-gpu")
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.get("https://www.google.com")
        print("GPU 비활성화 성공!")
        driver.quit()
    except Exception as e:
        print(f"GPU 비활성화 실패: {e}")
    
    # 5단계: 확장 프로그램 비활성화 추가
    print("\n5단계: 확장 프로그램 비활성화 추가")
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--remote-debugging-port=9222")
        chrome_options.add_argument("--single-process")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-extensions")
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.get("https://www.google.com")
        print("확장 프로그램 비활성화 성공!")
        driver.quit()
    except Exception as e:
        print(f"확장 프로그램 비활성화 실패: {e}")
    
    # 6단계: DevTools 비활성화 추가 (충돌 가능성)
    print("\n6단계: DevTools 비활성화 추가 (충돌 가능성)")
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--remote-debugging-port=9222")
        chrome_options.add_argument("--single-process")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-dev-tools")  # 충돌 가능성!
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.get("https://www.google.com")
        print("DevTools 비활성화 성공!")
        driver.quit()
    except Exception as e:
        print(f"DevTools 비활성화 실패: {e}")
        print("충돌 발견! --disable-dev-tools와 --remote-debugging-port=9222가 충돌!")
    
    # 7단계: 충돌 해결 - DevTools 비활성화 제거
    print("\n7단계: 충돌 해결 - DevTools 비활성화 제거")
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--remote-debugging-port=9222")
        chrome_options.add_argument("--single-process")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-extensions")
        # chrome_options.add_argument("--disable-dev-tools")  # 제거!
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.get("https://www.google.com")
        print("충돌 해결 성공!")
        driver.quit()
    except Exception as e:
        print(f"충돌 해결 실패: {e}")

def test_learnus_with_fixed_options():
    """수정된 옵션으로 LearnUs 테스트"""
    print("\n" + "=" * 80)
    print("수정된 옵션으로 LearnUs 테스트")
    print("=" * 80)
    
    try:
        chrome_options = Options()
        
        # 핵심 옵션 (충돌 없음)
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--remote-debugging-port=9222")
        chrome_options.add_argument("--single-process")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-plugins")
        chrome_options.add_argument("--disable-images")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36")
        chrome_options.add_argument("--log-level=3")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        
        # 추가 안정성 옵션
        chrome_options.add_argument("--no-first-run")
        chrome_options.add_argument("--disable-default-apps")
        chrome_options.add_argument("--disable-background-mode")
        chrome_options.add_argument("--disable-features=VizDisplayCompositor")
        
        # 충돌 옵션 제거
        # chrome_options.add_argument("--disable-dev-tools")  # 제거!
        # chrome_options.add_argument("--disable-logging")     # 제거!
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        print("Chrome 드라이버 초기화 성공!")
        
        # LearnUs 테스트
        driver.get("https://ys.learnus.org/")
        time.sleep(3)
        
        print(f"LearnUs 접속 성공: {driver.current_url}")
        print(f"페이지 제목: {driver.title}")
        
        driver.quit()
        print("LearnUs 테스트 완료!")
        
    except Exception as e:
        print(f"LearnUs 테스트 실패: {e}")

if __name__ == "__main__":
    test_chrome_options_step_by_step()
    test_learnus_with_fixed_options()
