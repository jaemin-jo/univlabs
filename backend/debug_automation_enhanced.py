#!/usr/bin/env python3
"""
초강력 디버깅 시스템이 포함된 LearnUs 자동화
모든 단계를 세밀하게 추적하고 문제점을 정확히 파악
"""

import sys
import os
import time
import logging
import traceback
import psutil
import subprocess
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager

# 로깅 설정 (JST 시간대)
os.environ['TZ'] = 'Asia/Tokyo'

# 초강력 디버깅 로거 설정
class DebugLogger:
    def __init__(self):
        self.logger = logging.getLogger('debug_automation')
        self.logger.setLevel(logging.DEBUG)
        
        # 파일 핸들러 (상세 로그)
        file_handler = logging.FileHandler('debug_automation_detailed.log', encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        
        # 콘솔 핸들러 (요약 로그)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # 포맷터
        detailed_formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(funcName)s:%(lineno)d - %(message)s'
        )
        simple_formatter = logging.Formatter('%(asctime)s - %(message)s')
        
        file_handler.setFormatter(detailed_formatter)
        console_handler.setFormatter(simple_formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def debug_step(self, step_name, details=None):
        """단계별 디버깅 로그"""
        self.logger.info(f"🔍 STEP: {step_name}")
        if details:
            self.logger.debug(f"   상세: {details}")
    
    def debug_success(self, step_name, result=None):
        """성공 단계 로그"""
        self.logger.info(f"✅ SUCCESS: {step_name}")
        if result:
            self.logger.debug(f"   결과: {result}")
    
    def debug_error(self, step_name, error, context=None):
        """에러 단계 로그"""
        self.logger.error(f"❌ ERROR: {step_name}")
        self.logger.error(f"   오류: {error}")
        if context:
            self.logger.error(f"   컨텍스트: {context}")
        self.logger.error(f"   스택트레이스: {traceback.format_exc()}")
    
    def debug_system_info(self):
        """시스템 정보 수집"""
        try:
            self.logger.info("🖥️ 시스템 정보 수집")
            self.logger.debug(f"   Python 버전: {sys.version}")
            self.logger.debug(f"   작업 디렉토리: {os.getcwd()}")
            self.logger.debug(f"   환경 변수 TZ: {os.environ.get('TZ', 'Not set')}")
            
            # 메모리 정보
            memory = psutil.virtual_memory()
            self.logger.debug(f"   메모리 사용량: {memory.percent}% ({memory.used / 1024 / 1024:.1f}MB / {memory.total / 1024 / 1024:.1f}MB)")
            
            # 디스크 정보
            disk = psutil.disk_usage('/')
            self.logger.debug(f"   디스크 사용량: {disk.percent}% ({disk.used / 1024 / 1024:.1f}MB / {disk.total / 1024 / 1024:.1f}MB)")
            
        except Exception as e:
            self.logger.error(f"시스템 정보 수집 실패: {e}")

# 전역 디버그 로거
debug_logger = DebugLogger()

def debug_chrome_environment():
    """Chrome 환경 상세 분석"""
    debug_logger.debug_step("Chrome 환경 분석 시작")
    
    try:
        # Chrome 실행 파일 확인
        chrome_paths = [
            "/usr/bin/google-chrome",
            "/usr/bin/chromium",
            "/usr/bin/chrome",
            "/usr/bin/chromium-browser"
        ]
        
        chrome_found = False
        for path in chrome_paths:
            if os.path.exists(path):
                debug_logger.debug_success(f"Chrome 실행 파일 발견: {path}")
                try:
                    # Chrome 버전 확인
                    result = subprocess.run([path, "--version"], capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        debug_logger.debug_success(f"Chrome 버전: {result.stdout.strip()}")
                    else:
                        debug_logger.debug_error("Chrome 버전 확인 실패", result.stderr)
                except Exception as e:
                    debug_logger.debug_error("Chrome 버전 확인 오류", str(e))
                chrome_found = True
                break
        
        if not chrome_found:
            debug_logger.debug_error("Chrome 실행 파일 없음", "모든 경로에서 Chrome을 찾을 수 없음")
        
        # ChromeDriver 확인
        chromedriver_paths = [
            "/usr/bin/chromedriver",
            "/usr/bin/chromium-driver",
            "/usr/lib/chromium-browser/chromedriver"
        ]
        
        driver_found = False
        for path in chromedriver_paths:
            if os.path.exists(path):
                debug_logger.debug_success(f"ChromeDriver 발견: {path}")
                try:
                    # ChromeDriver 버전 확인
                    result = subprocess.run([path, "--version"], capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        debug_logger.debug_success(f"ChromeDriver 버전: {result.stdout.strip()}")
                    else:
                        debug_logger.debug_error("ChromeDriver 버전 확인 실패", result.stderr)
                except Exception as e:
                    debug_logger.debug_error("ChromeDriver 버전 확인 오류", str(e))
                driver_found = True
                break
        
        if not driver_found:
            debug_logger.debug_error("ChromeDriver 없음", "모든 경로에서 ChromeDriver를 찾을 수 없음")
        
        # X11 디스플레이 확인
        display = os.environ.get('DISPLAY')
        debug_logger.debug_step("X11 디스플레이 확인", f"DISPLAY={display}")
        
        if display:
            try:
                result = subprocess.run(['xhost'], capture_output=True, text=True, timeout=5)
                debug_logger.debug_success("xhost 명령 실행", result.stdout)
            except Exception as e:
                debug_logger.debug_error("xhost 명령 실패", str(e))
        else:
            debug_logger.debug_step("DISPLAY 환경변수 없음", "헤드리스 모드로 실행 예정")
        
    except Exception as e:
        debug_logger.debug_error("Chrome 환경 분석 실패", str(e))

def create_optimized_chrome_options():
    """최적화된 Chrome 옵션 생성 (단계별 검증)"""
    debug_logger.debug_step("Chrome 옵션 생성 시작")
    
    try:
        chrome_options = Options()
        
        # 1단계: 핵심 옵션 (DevToolsActivePort 해결)
        debug_logger.debug_step("1단계: 핵심 옵션 설정")
        chrome_options.add_argument("--remote-debugging-port=9222")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        debug_logger.debug_success("핵심 옵션 설정 완료")
        
        # 2단계: 헤드리스 모드
        debug_logger.debug_step("2단계: 헤드리스 모드 설정")
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--single-process")
        debug_logger.debug_success("헤드리스 모드 설정 완료")
        
        # 3단계: 성능 최적화
        debug_logger.debug_step("3단계: 성능 최적화 옵션")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-plugins")
        chrome_options.add_argument("--disable-images")
        chrome_options.add_argument("--disable-web-security")
        debug_logger.debug_success("성능 최적화 옵션 설정 완료")
        
        # 4단계: Cloud Run 환경 최적화
        debug_logger.debug_step("4단계: Cloud Run 환경 최적화")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36")
        chrome_options.add_argument("--log-level=3")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        debug_logger.debug_success("Cloud Run 최적화 완료")
        
        # 5단계: 추가 안정성 옵션
        debug_logger.debug_step("5단계: 추가 안정성 옵션")
        chrome_options.add_argument("--no-first-run")
        chrome_options.add_argument("--disable-default-apps")
        chrome_options.add_argument("--disable-background-mode")
        chrome_options.add_argument("--disable-features=VizDisplayCompositor")
        debug_logger.debug_success("추가 안정성 옵션 설정 완료")
        
        # 6단계: 실험적 옵션 (문제 해결용)
        debug_logger.debug_step("6단계: 실험적 옵션")
        chrome_options.add_argument("--disable-dev-tools")
        chrome_options.add_argument("--disable-logging")
        chrome_options.add_argument("--disable-background-timer-throttling")
        chrome_options.add_argument("--disable-backgrounding-occluded-windows")
        chrome_options.add_argument("--disable-renderer-backgrounding")
        debug_logger.debug_success("실험적 옵션 설정 완료")
        
        return chrome_options
        
    except Exception as e:
        debug_logger.debug_error("Chrome 옵션 생성 실패", str(e))
        return None

def setup_driver_with_debug():
    """디버깅이 강화된 Chrome 드라이버 설정"""
    debug_logger.debug_step("Chrome 드라이버 설정 시작")
    
    try:
        # 시스템 정보 수집
        debug_logger.debug_system_info()
        
        # Chrome 환경 분석
        debug_chrome_environment()
        
        # Chrome 옵션 생성
        chrome_options = create_optimized_chrome_options()
        if not chrome_options:
            debug_logger.debug_error("Chrome 옵션 생성 실패", "옵션 생성 중 오류 발생")
            return None
        
        # ChromeDriver 서비스 설정
        debug_logger.debug_step("ChromeDriver 서비스 설정")
        service = None
        
        # 시스템 ChromeDriver 우선 시도
        system_driver_paths = [
            "/usr/bin/chromedriver",
            "/usr/bin/chromium-driver",
            "/usr/lib/chromium-browser/chromedriver"
        ]
        
        for path in system_driver_paths:
            if os.path.exists(path):
                debug_logger.debug_success(f"시스템 ChromeDriver 사용: {path}")
                service = Service(path)
                break
        
        if not service:
            debug_logger.debug_step("WebDriver Manager 사용")
            try:
                wdm_path = ChromeDriverManager().install()
                debug_logger.debug_success(f"WebDriver Manager 경로: {wdm_path}")
                service = Service(wdm_path)
            except Exception as e:
                debug_logger.debug_error("WebDriver Manager 실패", str(e))
                return None
        
        # Chrome 드라이버 초기화
        debug_logger.debug_step("Chrome 드라이버 초기화 시도")
        try:
            driver = webdriver.Chrome(service=service, options=chrome_options)
            debug_logger.debug_success("Chrome 드라이버 초기화 성공")
            return driver
        except Exception as e:
            debug_logger.debug_error("Chrome 드라이버 초기화 실패", str(e))
            return None
            
    except Exception as e:
        debug_logger.debug_error("Chrome 드라이버 설정 전체 실패", str(e))
        return None

def test_learnus_automation():
    """LearnUs 자동화 테스트 (초강력 디버깅)"""
    debug_logger.debug_step("LearnUs 자동화 테스트 시작")
    
    driver = None
    try:
        # 1단계: Chrome 드라이버 설정
        driver = setup_driver_with_debug()
        if not driver:
            debug_logger.debug_error("Chrome 드라이버 설정 실패", "드라이버 초기화 불가")
            return False
        
        # 2단계: LearnUs 메인 페이지 접속
        debug_logger.debug_step("LearnUs 메인 페이지 접속")
        try:
            driver.get("https://ys.learnus.org/")
            time.sleep(3)
            debug_logger.debug_success("LearnUs 메인 페이지 접속", f"URL: {driver.current_url}")
        except Exception as e:
            debug_logger.debug_error("LearnUs 메인 페이지 접속 실패", str(e))
            return False
        
        # 3단계: 페이지 로딩 확인
        debug_logger.debug_step("페이지 로딩 확인")
        try:
            page_title = driver.title
            page_source_length = len(driver.page_source)
            debug_logger.debug_success("페이지 로딩 확인", f"제목: {page_title}, 소스 길이: {page_source_length}")
        except Exception as e:
            debug_logger.debug_error("페이지 로딩 확인 실패", str(e))
            return False
        
        # 4단계: 연세포털 로그인 버튼 찾기
        debug_logger.debug_step("연세포털 로그인 버튼 찾기")
        try:
            login_button = driver.find_element(By.CSS_SELECTOR, "a.btn.btn-sso")
            debug_logger.debug_success("연세포털 로그인 버튼 발견", f"텍스트: {login_button.text}")
        except Exception as e:
            debug_logger.debug_error("연세포털 로그인 버튼 찾기 실패", str(e))
            return False
        
        # 5단계: 로그인 버튼 클릭
        debug_logger.debug_step("로그인 버튼 클릭")
        try:
            login_button.click()
            time.sleep(5)
            debug_logger.debug_success("로그인 버튼 클릭", f"현재 URL: {driver.current_url}")
        except Exception as e:
            debug_logger.debug_error("로그인 버튼 클릭 실패", str(e))
            return False
        
        # 6단계: 로그인 폼 확인
        debug_logger.debug_step("로그인 폼 확인")
        try:
            username_field = driver.find_element(By.ID, "loginId")
            password_field = driver.find_element(By.ID, "loginPw")
            debug_logger.debug_success("로그인 폼 발견", "사용자명/비밀번호 필드 확인")
        except Exception as e:
            debug_logger.debug_error("로그인 폼 찾기 실패", str(e))
            return False
        
        # 7단계: 로그인 정보 입력
        debug_logger.debug_step("로그인 정보 입력")
        try:
            username_field.clear()
            username_field.send_keys("2024248012")
            password_field.clear()
            password_field.send_keys("cjm9887@")
            debug_logger.debug_success("로그인 정보 입력 완료")
        except Exception as e:
            debug_logger.debug_error("로그인 정보 입력 실패", str(e))
            return False
        
        # 8단계: 로그인 버튼 클릭
        debug_logger.debug_step("로그인 버튼 클릭")
        try:
            submit_button = driver.find_element(By.CSS_SELECTOR, "input[type='submit']")
            submit_button.click()
            time.sleep(5)
            debug_logger.debug_success("로그인 버튼 클릭", f"현재 URL: {driver.current_url}")
        except Exception as e:
            debug_logger.debug_error("로그인 버튼 클릭 실패", str(e))
            return False
        
        # 9단계: 로그인 성공 확인
        debug_logger.debug_step("로그인 성공 확인")
        try:
            current_url = driver.current_url
            if "learnus.org" in current_url and "login" not in current_url.lower():
                debug_logger.debug_success("로그인 성공", f"URL: {current_url}")
            else:
                debug_logger.debug_error("로그인 실패", f"예상 URL과 다름: {current_url}")
                return False
        except Exception as e:
            debug_logger.debug_error("로그인 성공 확인 실패", str(e))
            return False
        
        # 10단계: 과제 정보 수집
        debug_logger.debug_step("과제 정보 수집")
        try:
            # 다양한 선택자로 과제 찾기
            assignment_selectors = [
                ".course-title h3",
                "h3",
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
                        debug_logger.debug_success(f"과제 요소 발견 ({selector})", f"{len(elements)}개")
                        for i, element in enumerate(elements[:3]):
                            text = element.text.strip()
                            if text:
                                assignments_found.append(text)
                                debug_logger.debug_step(f"과제 {i+1}", text)
                    else:
                        debug_logger.debug_step(f"과제 요소 없음 ({selector})", "해당 선택자로 요소를 찾지 못함")
                except Exception as e:
                    debug_logger.debug_error(f"과제 수집 실패 ({selector})", str(e))
            
            if assignments_found:
                debug_logger.debug_success("과제 수집 성공", f"총 {len(assignments_found)}개 과제 발견")
                return True
            else:
                debug_logger.debug_error("과제 수집 실패", "과제를 찾을 수 없음")
                return False
                
        except Exception as e:
            debug_logger.debug_error("과제 정보 수집 실패", str(e))
            return False
        
    except Exception as e:
        debug_logger.debug_error("LearnUs 자동화 전체 실패", str(e))
        return False
    finally:
        if driver:
            debug_logger.debug_step("Chrome 드라이버 종료")
            try:
                driver.quit()
                debug_logger.debug_success("Chrome 드라이버 종료 완료")
            except Exception as e:
                debug_logger.debug_error("Chrome 드라이버 종료 실패", str(e))

def main():
    """메인 함수"""
    print("=" * 80)
    print("초강력 디버깅 시스템이 포함된 LearnUs 자동화")
    print("=" * 80)
    print("모든 단계를 세밀하게 추적하고 문제점을 정확히 파악합니다.")
    print()
    
    # 시스템 정보 출력
    debug_logger.debug_system_info()
    
    # 자동화 실행
    result = test_learnus_automation()
    
    print("=" * 80)
    if result:
        print("자동화 성공!")
        print("상세 로그: debug_automation_detailed.log")
    else:
        print("자동화 실패!")
        print("상세 로그: debug_automation_detailed.log")
        print("문제점을 로그에서 확인하세요.")
    print("=" * 80)

if __name__ == "__main__":
    main()
