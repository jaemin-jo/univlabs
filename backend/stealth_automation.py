#!/usr/bin/env python3
"""
자동화 감지 우회 LearnUs 자동화
Playwright 분석 결과를 바탕으로 완전한 자동화 구현
"""

import sys
import os
import time
import logging
import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_stealth_chrome_options():
    """자동화 감지 우회 Chrome 옵션 생성"""
    chrome_options = Options()
    
    # 🔥 자동화 감지 우회 핵심 옵션들
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-plugins")
    chrome_options.add_argument("--disable-images")
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--disable-features=VizDisplayCompositor")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--remote-debugging-port=9222")
    
    # 🔥 자동화 감지 우회를 위한 추가 옵션들
    chrome_options.add_argument("--disable-background-timer-throttling")
    chrome_options.add_argument("--disable-backgrounding-occluded-windows")
    chrome_options.add_argument("--disable-renderer-backgrounding")
    chrome_options.add_argument("--disable-features=TranslateUI")
    chrome_options.add_argument("--disable-ipc-flooding-protection")
    chrome_options.add_argument("--disable-software-rasterizer")
    chrome_options.add_argument("--disable-background-networking")
    chrome_options.add_argument("--disable-sync")
    chrome_options.add_argument("--disable-translate")
    chrome_options.add_argument("--disable-plugins-discovery")
    chrome_options.add_argument("--disable-preconnect")
    chrome_options.add_argument("--disable-hang-monitor")
    chrome_options.add_argument("--disable-prompt-on-repost")
    chrome_options.add_argument("--disable-domain-reliability")
    chrome_options.add_argument("--disable-component-extensions-with-background-pages")
    chrome_options.add_argument("--disable-background-downloads")
    chrome_options.add_argument("--disable-add-to-shelf")
    chrome_options.add_argument("--disable-client-side-phishing-detection")
    
    # 🔥 헤드리스 모드 (Cloud Run용)
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-first-run")
    chrome_options.add_argument("--disable-default-apps")
    chrome_options.add_argument("--disable-background-mode")
    
    # 🔥 실제 사용자처럼 보이게 하는 옵션들
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36")
    chrome_options.add_argument("--accept-lang=ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7")
    
    # 🔥 자동화 감지 우회를 위한 실험적 옵션들
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    return chrome_options

def human_like_delay():
    """사람처럼 보이는 랜덤 딜레이"""
    delay = random.uniform(0.5, 2.0)
    time.sleep(delay)

def human_like_typing(element, text):
    """사람처럼 보이는 타이핑"""
    element.clear()
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(0.05, 0.15))

def human_like_mouse_move(driver, element):
    """사람처럼 보이는 마우스 이동"""
    try:
        actions = ActionChains(driver)
        actions.move_to_element(element).perform()
        human_like_delay()
    except Exception as e:
        logger.warning(f"마우스 이동 실패: {e}")

def stealth_login(driver, username, password):
    """자동화 감지 우회 로그인"""
    try:
        logger.info("🔍 LearnUs 메인 페이지 접속...")
        driver.get("https://ys.learnus.org/")
        human_like_delay()
        
        logger.info("🔍 연세포털 로그인 버튼 찾기...")
        login_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a.btn.btn-sso"))
        )
        
        # 사람처럼 보이는 마우스 이동
        human_like_mouse_move(driver, login_button)
        
        logger.info("🔍 연세포털 로그인 버튼 클릭...")
        login_button.click()
        human_like_delay()
        
        logger.info("🔍 로그인 폼 대기...")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "loginId"))
        )
        
        # 🔥 자동화 감지 우회를 위한 JavaScript 실행
        logger.info("🔧 자동화 감지 우회 JavaScript 실행...")
        driver.execute_script("""
            // webdriver 속성 제거
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
            
            // chrome 속성 정리
            delete window.chrome;
            window.chrome = {
                runtime: {},
                loadTimes: function() {},
                csi: function() {},
                app: {}
            };
            
            // 자동화 관련 속성들 제거
            delete window.selenium;
            delete window.webdriver;
            delete window.driver;
            delete window.playwright;
            delete window.automation;
        """)
        
        # 사용자명 필드 찾기
        logger.info("🔍 사용자명 필드 찾기...")
        username_field = driver.find_element(By.ID, "loginId")
        
        # 비밀번호 필드 찾기
        logger.info("🔍 비밀번호 필드 찾기...")
        password_field = driver.find_element(By.ID, "loginPasswd")
        
        # 🔥 숨겨진 필드들 처리 (JavaScript로)
        logger.info("🔧 숨겨진 필드들 처리...")
        driver.execute_script("""
            // E2, E3, E4 필드 설정
            document.getElementById('E2').value = arguments[0];
            document.getElementById('E3').value = arguments[1];
            document.getElementById('E4').value = arguments[0];
        """, username, password)
        
        # 사람처럼 보이는 타이핑
        logger.info("🔍 사용자명 입력...")
        human_like_mouse_move(driver, username_field)
        human_like_typing(username_field, username)
        
        logger.info("🔍 비밀번호 입력...")
        human_like_mouse_move(driver, password_field)
        human_like_typing(password_field, password)
        
        # 로그인 버튼 찾기 및 클릭
        logger.info("🔍 로그인 버튼 찾기...")
        submit_button = driver.find_element(By.CSS_SELECTOR, "a[href='#none;']")
        
        # 사람처럼 보이는 마우스 이동 및 클릭
        human_like_mouse_move(driver, submit_button)
        human_like_delay()
        
        logger.info("🔍 로그인 버튼 클릭...")
        submit_button.click()
        human_like_delay()
        
        # 로그인 결과 확인
        logger.info("🔍 로그인 결과 확인...")
        time.sleep(3)
        
        current_url = driver.current_url
        logger.info(f"현재 URL: {current_url}")
        
        if "learnus.org" in current_url and "login" not in current_url.lower():
            logger.info("✅ 로그인 성공!")
            return True
        else:
            logger.error("❌ 로그인 실패!")
            return False
            
    except Exception as e:
        logger.error(f"❌ 로그인 과정 오류: {e}")
        return False

def collect_assignments_stealth(driver):
    """자동화 감지 우회 과제 수집"""
    try:
        logger.info("📚 과제 정보 수집 시작...")
        
        # 과제 관련 페이지로 이동 시도
        logger.info("🔍 과제 관련 링크 찾기...")
        assignment_links = driver.find_elements(By.CSS_SELECTOR, 
            "a[href*='assignment'], a[href*='과제'], a[href*='task'], a[href*='homework']")
        
        if assignment_links:
            logger.info(f"✅ 과제 관련 링크 {len(assignment_links)}개 발견")
            for i, link in enumerate(assignment_links[:3]):
                logger.info(f"   {i+1}. {link.text} - {link.get_attribute('href')}")
            
            # 첫 번째 과제 링크 클릭
            human_like_mouse_move(driver, assignment_links[0])
            assignment_links[0].click()
            human_like_delay()
            logger.info(f"✅ 과제 페이지 이동: {driver.current_url}")
        else:
            logger.info("ℹ️ 과제 관련 링크를 찾을 수 없음. 메인 페이지에서 과제 정보 수집 시도...")
        
        # 과제 정보 수집
        assignments = []
        assignment_selectors = [
            "h3",
            ".course-title h3",
            ".course-box h3",
            "a[href*='course']",
            ".card a",
            ".course-card a",
            ".assignment-item",
            ".task-item",
            ".homework-item",
            "a[href*='assignment']",
            "a[href*='task']",
            "a[href*='homework']",
            ".activity-item",
            ".module-item",
            "li[class*='course']",
            "div[class*='activity']"
        ]
        
        for selector in assignment_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    logger.info(f"✅ {selector} 선택자로 {len(elements)}개 과제 발견")
                    for i, element in enumerate(elements[:5]):
                        text = element.text.strip()
                        if text:
                            assignments.append({
                                'course': text,
                                'activity': text,
                                'selector': selector
                            })
                            logger.info(f"   과제 {i+1}: {text}")
                    break
                else:
                    logger.info(f"❌ {selector} 선택자로 과제를 찾지 못함")
            except Exception as e:
                logger.warning(f"⚠️ {selector} 선택자 실패: {e}")
        
        return assignments
        
    except Exception as e:
        logger.error(f"❌ 과제 수집 실패: {e}")
        return []

def test_stealth_automation():
    """자동화 감지 우회 테스트"""
    print("=" * 80)
    print("자동화 감지 우회 LearnUs 자동화 테스트")
    print("=" * 80)
    
    driver = None
    try:
        # Chrome 옵션 생성
        chrome_options = create_stealth_chrome_options()
        
        # ChromeDriver 서비스 설정
        service = Service(ChromeDriverManager().install())
        
        # Chrome 드라이버 초기화
        print("Chrome 드라이버 초기화 중...")
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # 🔥 자동화 감지 우회를 위한 추가 JavaScript 실행
        driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': '''
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined,
                });
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5],
                });
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['ko-KR', 'ko', 'en-US', 'en'],
                });
                window.chrome = {
                    runtime: {},
                };
            '''
        })
        
        print("Chrome 드라이버 초기화 성공!")
        
        # 자동화 감지 우회 로그인
        print("자동화 감지 우회 로그인 시도...")
        if stealth_login(driver, "2024248012", "cjm9887@"):
            print("✅ 로그인 성공!")
            
            # 과제 정보 수집
            print("과제 정보 수집...")
            assignments = collect_assignments_stealth(driver)
            
            if assignments:
                print(f"✅ 과제 수집 성공: 총 {len(assignments)}개 과제 발견")
                for i, assignment in enumerate(assignments, 1):
                    print(f"   {i}. {assignment['course']}")
                return True
            else:
                print("❌ 과제 수집 실패: 과제를 찾을 수 없음")
                return False
        else:
            print("❌ 로그인 실패!")
            return False
        
    except Exception as e:
        print(f"❌ 자동화 실패: {e}")
        return False
    finally:
        if driver:
            try:
                driver.quit()
                print("Chrome 드라이버 종료 완료")
            except:
                pass

if __name__ == "__main__":
    test_stealth_automation()













