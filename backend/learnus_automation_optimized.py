#!/usr/bin/env python3
"""
LearnUs 연세 자동화 - Playwright 분석 결과 기반 최적화 버전
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
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def create_optimized_chrome_options():
    """최적화된 Chrome 옵션 생성 (Playwright 분석 결과 기반)"""
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
    """자동화 감지 우회 로그인 (Playwright 분석 결과 기반)"""
    try:
        logger.info("🔍 LearnUs 메인 페이지 접속...")
        driver.get("https://ys.learnus.org/")
        human_like_delay()
        
        logger.info("🔍 연세포털 로그인 버튼 찾기...")
        login_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href*='spLogin2.php']"))
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

def collect_course_assignments(driver, course_name):
    """개별 과목의 과제 정보 수집 (Playwright 분석 결과 기반)"""
    try:
        assignments = []
        
        # 🔥 주차별 학습 활동에서 과제 찾기
        logger.info(f"🔍 {course_name} 과제 검색...")
        
        # 과제 링크 찾기 (Playwright 분석 결과 기반)
        assignment_selectors = [
            "a[href*='mod/assign/view.php']",  # 과제 제출 링크
            "a[href*='mod/vod/view.php']",     # 동영상 링크
            "a[href*='mod/ubfile/view.php']",  # 파일 링크
        ]
        
        for selector in assignment_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    try:
                        # 과제/동영상/파일 정보 추출
                        title_element = element.find_element(By.CSS_SELECTOR, "span, div")
                        title = title_element.text.strip()
                        
                        # 완료 상태 확인
                        status = "미완료"
                        try:
                            # 완료 아이콘 찾기
                            status_icon = element.find_element(By.XPATH, "following-sibling::img[contains(@alt, '완료')]")
                            if "완료함" in status_icon.get_attribute('alt'):
                                status = "완료"
                        except:
                            pass
                        
                        # 마감일 정보 추출
                        deadline = "정보 없음"
                        try:
                            deadline_element = element.find_element(By.XPATH, "following-sibling::*[contains(text(), '2025-')]")
                            deadline = deadline_element.text.strip()
                        except:
                            pass
                        
                        assignment_info = {
                            'course': course_name,
                            'title': title,
                            'type': '과제' if 'assign' in element.get_attribute('href') else '동영상' if 'vod' in element.get_attribute('href') else '파일',
                            'status': status,
                            'deadline': deadline,
                            'url': element.get_attribute('href')
                        }
                        
                        assignments.append(assignment_info)
                        logger.info(f"   📝 {assignment_info['type']}: {title} ({status})")
                        
                    except Exception as e:
                        logger.warning(f"⚠️ 과제 정보 추출 실패: {e}")
                        continue
                        
            except Exception as e:
                logger.warning(f"⚠️ {selector} 선택자 실패: {e}")
                continue
        
        return assignments
        
    except Exception as e:
        logger.error(f"❌ {course_name} 과제 수집 실패: {e}")
        return []

def collect_all_assignments(driver):
    """모든 과목의 과제 정보 수집 (Playwright 분석 결과 기반)"""
    try:
        logger.info("📚 LearnUs 과제 정보 수집 시작...")
        
        # 🔥 메인 페이지에서 과목 목록 수집
        logger.info("🔍 과목 목록 수집...")
        course_links = driver.find_elements(By.CSS_SELECTOR, "a[href*='course/view.php']")
        logger.info(f"✅ 발견된 과목 수: {len(course_links)}개")
        
        all_assignments = []
        
        # 각 과목별로 상세 정보 수집
        for i, course_link in enumerate(course_links[:5]):  # 최대 5개 과목만 처리
            try:
                course_name = course_link.find_element(By.CSS_SELECTOR, "h3").text.strip()
                course_url = course_link.get_attribute('href')
                logger.info(f"🔍 과목 {i+1}: {course_name}")
                
                # 과목 페이지로 이동
                driver.get(course_url)
                time.sleep(2)
                
                # 🔥 과제 정보 수집 (Playwright 분석 결과 기반)
                assignments = collect_course_assignments(driver, course_name)
                all_assignments.extend(assignments)
                
                # 메인 페이지로 돌아가기
                driver.get("https://ys.learnus.org/")
                time.sleep(1)
                
            except Exception as e:
                logger.warning(f"⚠️ 과목 {i+1} 처리 실패: {e}")
                continue
        
        logger.info(f"✅ 총 {len(all_assignments)}개 과제 수집 완료")
        return all_assignments
        
    except Exception as e:
        logger.error(f"❌ 과제 수집 실패: {e}")
        return []

def test_learnus_automation():
    """LearnUs 자동화 테스트 (Playwright 분석 결과 기반)"""
    print("=" * 80)
    print("LearnUs 연세 자동화 테스트 (Playwright 분석 결과 기반)")
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
            assignments = collect_all_assignments(driver)
            
            if assignments:
                print(f"✅ 과제 수집 성공: 총 {len(assignments)}개 과제 발견")
                for i, assignment in enumerate(assignments, 1):
                    print(f"   {i}. [{assignment['type']}] {assignment['title']} ({assignment['status']})")
                    print(f"      과목: {assignment['course']}")
                    print(f"      마감일: {assignment['deadline']}")
                    print(f"      URL: {assignment['url']}")
                    print()
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
    test_learnus_automation()










