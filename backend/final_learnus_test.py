#!/usr/bin/env python3
"""
최종 LearnUs 자동화 테스트
로그인 폼 문제를 해결하고 완전한 자동화 구현
"""

import sys
import os
import time
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_optimized_chrome_options():
    """최적화된 Chrome 옵션 생성"""
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
    
    return chrome_options

def test_learnus_automation():
    """LearnUs 자동화 테스트"""
    print("=" * 80)
    print("최종 LearnUs 자동화 테스트")
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
        login_button = driver.find_element(By.CSS_SELECTOR, "a.btn.btn-sso")
        print(f"로그인 버튼 발견: {login_button.text}")
        
        # 로그인 버튼 클릭
        print("로그인 버튼 클릭...")
        login_button.click()
        time.sleep(5)
        
        print(f"로그인 페이지 접속: {driver.current_url}")
        
        # 페이지 소스 확인
        print("페이지 소스 확인...")
        page_source = driver.page_source
        print(f"페이지 소스 길이: {len(page_source)}")
        
        # 다양한 선택자로 로그인 폼 찾기
        print("로그인 폼 찾기...")
        login_selectors = [
            "input[id='loginPw']",
            "input[name='loginPw']",
            "input[type='password']",
            "#loginPw",
            "input#loginPw",
            "input[name='password']",
            "input[type='password']"
        ]
        
        password_field = None
        for selector in login_selectors:
            try:
                password_field = driver.find_element(By.CSS_SELECTOR, selector)
                print(f"비밀번호 필드 발견: {selector}")
                break
            except:
                print(f"비밀번호 필드 없음: {selector}")
                continue
        
        if not password_field:
            print("비밀번호 필드를 찾을 수 없습니다!")
            print("페이지 소스 일부:")
            print(page_source[:1000])
            return False
        
        # 사용자명 필드 찾기
        username_selectors = [
            "input[id='loginId']",
            "input[name='loginId']",
            "input[type='text']",
            "#loginId",
            "input#loginId",
            "input[name='username']",
            "input[name='user']"
        ]
        
        username_field = None
        for selector in username_selectors:
            try:
                username_field = driver.find_element(By.CSS_SELECTOR, selector)
                print(f"사용자명 필드 발견: {selector}")
                break
            except:
                print(f"사용자명 필드 없음: {selector}")
                continue
        
        if not username_field:
            print("사용자명 필드를 찾을 수 없습니다!")
            return False
        
        # 로그인 정보 입력
        print("로그인 정보 입력...")
        username_field.clear()
        username_field.send_keys("2024248012")
        password_field.clear()
        password_field.send_keys("cjm9887@")
        print("로그인 정보 입력 완료!")
        
        # 로그인 버튼 찾기 및 클릭
        print("로그인 버튼 찾기...")
        submit_selectors = [
            "input[type='submit']",
            "button[type='submit']",
            "input[value='로그인']",
            "button:contains('로그인')",
            ".btn-primary",
            ".login-btn"
        ]
        
        submit_button = None
        for selector in submit_selectors:
            try:
                submit_button = driver.find_element(By.CSS_SELECTOR, selector)
                print(f"로그인 버튼 발견: {selector}")
                break
            except:
                print(f"로그인 버튼 없음: {selector}")
                continue
        
        if not submit_button:
            print("로그인 버튼을 찾을 수 없습니다!")
            return False
        
        # 로그인 버튼 클릭
        print("로그인 버튼 클릭...")
        submit_button.click()
        time.sleep(5)
        
        print(f"로그인 후 URL: {driver.current_url}")
        
        # 로그인 성공 확인
        if "learnus.org" in driver.current_url and "login" not in driver.current_url.lower():
            print("로그인 성공!")
            
            # 과제 정보 수집
            print("과제 정보 수집...")
            assignment_selectors = [
                "h3",
                ".course-title h3",
                ".course-box h3",
                "a[href*='course']",
                ".card a",
                ".course-card a"
            ]
            
            assignments_found = []
            for selector in assignment_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        print(f"과제 요소 발견 ({selector}): {len(elements)}개")
                        for i, element in enumerate(elements[:5]):
                            text = element.text.strip()
                            if text:
                                assignments_found.append(text)
                                print(f"과제 {i+1}: {text}")
                    else:
                        print(f"과제 요소 없음 ({selector})")
                except Exception as e:
                    print(f"과제 수집 실패 ({selector}): {e}")
            
            if assignments_found:
                print(f"과제 수집 성공: 총 {len(assignments_found)}개 과제 발견")
                return True
            else:
                print("과제 수집 실패: 과제를 찾을 수 없음")
                return False
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










