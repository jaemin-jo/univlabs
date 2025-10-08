#!/usr/bin/env python3
"""
최적화된 Chrome 옵션으로 LearnUs 자동화 테스트
충돌 옵션을 제거하고 안정적인 옵션만 사용
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

def create_optimized_chrome_options():
    """최적화된 Chrome 옵션 생성 (충돌 제거)"""
    chrome_options = Options()
    
    # 핵심 안정성 옵션
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--remote-debugging-port=9222")
    
    # 성능 최적화 옵션
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-plugins")
    chrome_options.add_argument("--disable-images")
    chrome_options.add_argument("--disable-web-security")
    
    # 창 크기 및 사용자 에이전트
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36")
    
    # 로그 레벨 설정
    chrome_options.add_argument("--log-level=3")
    
    # 자동화 감지 방지
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    
    # 추가 안정성 옵션
    chrome_options.add_argument("--no-first-run")
    chrome_options.add_argument("--disable-default-apps")
    chrome_options.add_argument("--disable-background-mode")
    chrome_options.add_argument("--disable-features=VizDisplayCompositor")
    
    # 충돌 옵션 제거
    # chrome_options.add_argument("--disable-dev-tools")  # 제거!
    # chrome_options.add_argument("--disable-logging")     # 제거!
    # chrome_options.add_argument("--single-process")      # 제거!
    
    return chrome_options

def test_learnus_automation():
    """LearnUs 자동화 테스트"""
    print("=" * 80)
    print("최적화된 Chrome 옵션으로 LearnUs 자동화 테스트")
    print("=" * 80)
    
    driver = None
    try:
        # Chrome 옵션 생성
        chrome_options = create_optimized_chrome_options()
        
        # ChromeDriver 서비스 설정
        service = Service(ChromeDriverManager().install())
        
        # Chrome 드라이버 초기화
        print("Chrome 드라이버 초기화 중...")
        driver = webdriver.Chrome(service=service, options=chrome_options)
        print("Chrome 드라이버 초기화 성공!")
        
        # LearnUs 메인 페이지 접속
        print("LearnUs 메인 페이지 접속 중...")
        driver.get("https://ys.learnus.org/")
        time.sleep(3)
        
        print(f"LearnUs 접속 성공: {driver.current_url}")
        print(f"페이지 제목: {driver.title}")
        
        # 연세포털 로그인 버튼 찾기
        print("연세포털 로그인 버튼 찾기...")
        login_button = driver.find_element("css selector", "a.btn.btn-sso")
        print(f"로그인 버튼 발견: {login_button.text}")
        
        # 로그인 버튼 클릭
        print("로그인 버튼 클릭...")
        login_button.click()
        time.sleep(5)
        
        print(f"로그인 페이지 접속: {driver.current_url}")
        
        # 로그인 폼 확인
        print("로그인 폼 확인...")
        username_field = driver.find_element("id", "loginId")
        password_field = driver.find_element("id", "loginPw")
        print("로그인 폼 발견!")
        
        # 로그인 정보 입력
        print("로그인 정보 입력...")
        username_field.clear()
        username_field.send_keys("2024248012")
        password_field.clear()
        password_field.send_keys("cjm9887@")
        print("로그인 정보 입력 완료!")
        
        # 로그인 버튼 클릭
        print("로그인 버튼 클릭...")
        submit_button = driver.find_element("css selector", "input[type='submit']")
        submit_button.click()
        time.sleep(5)
        
        print(f"로그인 후 URL: {driver.current_url}")
        
        # 로그인 성공 확인
        if "learnus.org" in driver.current_url and "login" not in driver.current_url.lower():
            print("로그인 성공!")
            
            # 과제 정보 수집
            print("과제 정보 수집...")
            assignments = driver.find_elements("css selector", "h3")
            print(f"과제 요소 {len(assignments)}개 발견")
            
            for i, assignment in enumerate(assignments[:5]):
                text = assignment.text.strip()
                if text:
                    print(f"과제 {i+1}: {text}")
            
            print("LearnUs 자동화 성공!")
            return True
        else:
            print("로그인 실패!")
            return False
        
    except Exception as e:
        print(f"LearnUs 자동화 실패: {e}")
        return False
    finally:
        if driver:
            try:
                driver.quit()
                print("Chrome 드라이버 종료 완료")
            except:
                pass

if __name__ == "__main__":
    test_learnus_automation()










