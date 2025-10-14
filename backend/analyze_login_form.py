#!/usr/bin/env python3
"""
로그인 폼 구조 분석
정확한 선택자를 찾기 위한 디버깅
"""

import sys
import os
import time
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
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

def analyze_login_form():
    """로그인 폼 구조 분석"""
    print("=" * 80)
    print("로그인 폼 구조 분석")
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
        
        # 페이지 소스 분석
        print("페이지 소스 분석...")
        page_source = driver.page_source
        print(f"페이지 소스 길이: {len(page_source)}")
        
        # 모든 input 요소 찾기
        print("모든 input 요소 찾기...")
        inputs = driver.find_elements(By.TAG_NAME, "input")
        print(f"input 요소 {len(inputs)}개 발견")
        
        for i, input_elem in enumerate(inputs):
            try:
                input_type = input_elem.get_attribute("type")
                input_id = input_elem.get_attribute("id")
                input_name = input_elem.get_attribute("name")
                input_class = input_elem.get_attribute("class")
                input_value = input_elem.get_attribute("value")
                
                print(f"Input {i+1}:")
                print(f"  type: {input_type}")
                print(f"  id: {input_id}")
                print(f"  name: {input_name}")
                print(f"  class: {input_class}")
                print(f"  value: {input_value}")
                print()
            except Exception as e:
                print(f"Input {i+1} 분석 실패: {e}")
        
        # 모든 button 요소 찾기
        print("모든 button 요소 찾기...")
        buttons = driver.find_elements(By.TAG_NAME, "button")
        print(f"button 요소 {len(buttons)}개 발견")
        
        for i, button_elem in enumerate(buttons):
            try:
                button_type = button_elem.get_attribute("type")
                button_id = button_elem.get_attribute("id")
                button_name = button_elem.get_attribute("name")
                button_class = button_elem.get_attribute("class")
                button_text = button_elem.text
                
                print(f"Button {i+1}:")
                print(f"  type: {button_type}")
                print(f"  id: {button_id}")
                print(f"  name: {button_name}")
                print(f"  class: {button_class}")
                print(f"  text: {button_text}")
                print()
            except Exception as e:
                print(f"Button {i+1} 분석 실패: {e}")
        
        # 폼 요소 찾기
        print("폼 요소 찾기...")
        forms = driver.find_elements(By.TAG_NAME, "form")
        print(f"form 요소 {len(forms)}개 발견")
        
        for i, form_elem in enumerate(forms):
            try:
                form_id = form_elem.get_attribute("id")
                form_class = form_elem.get_attribute("class")
                form_action = form_elem.get_attribute("action")
                form_method = form_elem.get_attribute("method")
                
                print(f"Form {i+1}:")
                print(f"  id: {form_id}")
                print(f"  class: {form_class}")
                print(f"  action: {form_action}")
                print(f"  method: {form_method}")
                print()
            except Exception as e:
                print(f"Form {i+1} 분석 실패: {e}")
        
        # 페이지 소스 일부 출력
        print("페이지 소스 일부:")
        print(page_source[:2000])
        
    except Exception as e:
        print(f"로그인 폼 분석 실패: {e}")
    finally:
        if driver:
            try:
                driver.quit()
                print("Chrome 드라이버 종료 완료")
            except:
                pass

if __name__ == "__main__":
    analyze_login_form()















