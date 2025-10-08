"""
로컬 테스트용 - Chrome 드라이버 초기화 실패 지점 디버깅
"""

import os
import sys
import time
import json
import logging
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('automation_debug.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def setup_driver():
    """Chrome 드라이버 설정 (로컬 환경 최적화) - 최종 수정 버전"""
    try:
        logger.info("Chrome 드라이버 설정 중...")
        
        # 1단계: Chrome 실행 파일 확인
        logger.info("1단계: Chrome 실행 파일 확인 중...")
        chrome_bin_paths = [
            'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
            'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe',
            'C:\\Users\\jaemd\\AppData\\Local\\Google\\Chrome\\Application\\chrome.exe'
        ]
        
        chrome_found = False
        for chrome_path in chrome_bin_paths:
            if os.path.exists(chrome_path):
                logger.info(f"Chrome 실행 파일 발견: {chrome_path}")
                os.environ['CHROME_BIN'] = chrome_path
                chrome_found = True
                break
        
        if not chrome_found:
            logger.warning("Chrome 실행 파일을 찾을 수 없음, 기본 경로 사용")
        
        # 2단계: Chrome 옵션 설정 (최소한의 옵션으로 시작)
        logger.info("2단계: Chrome 옵션 설정 중...")
        chrome_options = Options()
        
        # 🔥 로컬 환경을 위한 필수 옵션들
        chrome_options.add_argument("--no-sandbox")  # 필수: 샌드박스 비활성화
        chrome_options.add_argument("--disable-dev-shm-usage")  # 필수: 공유 메모리 비활성화
        chrome_options.add_argument("--disable-gpu")  # GPU 비활성화
        chrome_options.add_argument("--window-size=1920,1080")  # 창 크기 설정
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        chrome_options.add_argument("--log-level=3")  # 로그 레벨 설정
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")  # 자동화 감지 방지
        
        # 🔥 DevToolsActivePort 오류 해결을 위한 핵심 옵션들
        chrome_options.add_argument("--remote-debugging-port=0")  # 🔥 핵심: 디버깅 포트 비활성화
        chrome_options.add_argument("--disable-dev-tools")  # 🔥 핵심: DevTools 완전 비활성화
        
        # 🔥 추가 안정성 옵션들
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-plugins")
        chrome_options.add_argument("--disable-images")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--disable-features=VizDisplayCompositor")
        chrome_options.add_argument("--no-zygote")
        chrome_options.add_argument("--disable-setuid-sandbox")
        chrome_options.add_argument("--disable-software-rasterizer")
        chrome_options.add_argument("--disable-gpu-sandbox")
        chrome_options.add_argument("--disable-gpu-process-crash-limit")
        chrome_options.add_argument("--disable-gpu-memory-buffer-compositor-resources")
        chrome_options.add_argument("--disable-gpu-rasterization")
        chrome_options.add_argument("--disable-background-timer-throttling")
        chrome_options.add_argument("--disable-backgrounding-occluded-windows")
        chrome_options.add_argument("--disable-renderer-backgrounding")
        chrome_options.add_argument("--disable-features=TranslateUI")
        chrome_options.add_argument("--disable-ipc-flooding-protection")
        chrome_options.add_argument("--disable-hang-monitor")
        chrome_options.add_argument("--disable-prompt-on-repost")
        chrome_options.add_argument("--disable-client-side-phishing-detection")
        chrome_options.add_argument("--disable-component-update")
        chrome_options.add_argument("--disable-domain-reliability")
        chrome_options.add_argument("--disable-background-networking")
        chrome_options.add_argument("--disable-default-apps")
        chrome_options.add_argument("--disable-sync")
        chrome_options.add_argument("--disable-translate")
        chrome_options.add_argument("--hide-scrollbars")
        chrome_options.add_argument("--mute-audio")
        chrome_options.add_argument("--no-first-run")
        chrome_options.add_argument("--disable-logging")
        chrome_options.add_argument("--disable-permissions-api")
        chrome_options.add_argument("--disable-popup-blocking")
        
        # 🔥 메모리 최적화
        chrome_options.add_argument("--memory-pressure-off")
        chrome_options.add_argument("--max_old_space_size=2048")  # 메모리 사용량 줄임
        
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        logger.info("Chrome 옵션 설정 완료")
        
        # 3단계: Chrome 드라이버 경로 확인
        logger.info("3단계: Chrome 드라이버 경로 확인 중...")
        
        # WebDriver Manager 사용 (로컬 환경)
        service = Service(ChromeDriverManager().install())
        logger.info("WebDriver Manager로 Chrome 드라이버 설치")
        
        # 4단계: Chrome 드라이버 초기화 시도
        logger.info("4단계: Chrome 드라이버 초기화 시도 중...")
        logger.info("이 순간에 실패할 가능성이 높습니다!")
        
        try:
            driver = webdriver.Chrome(service=service, options=chrome_options)
            logger.info("Chrome 드라이버 초기화 성공!")
        except Exception as driver_error:
            logger.error(f"Chrome 드라이버 초기화 실패: {driver_error}")
            logger.error(f"오류 타입: {type(driver_error).__name__}")
            logger.error(f"오류 메시지: {str(driver_error)}")
            return None
        
        # 5단계: 자동화 감지 방지 설정
        logger.info("5단계: 자동화 감지 방지 설정 중...")
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        driver.set_page_load_timeout(30)
        driver.implicitly_wait(10)
        
        logger.info("Chrome 드라이버 초기화 완료")
        return driver
        
    except Exception as e:
        logger.error(f"Chrome 드라이버 설정 실패: {e}")
        logger.error(f"최종 오류 타입: {type(e).__name__}")
        logger.error(f"최종 오류 메시지: {str(e)}")
        return None

def test_yonsei_site():
    """런어스연세 사이트 테스트"""
    driver = None
    try:
        logger.info("=== 런어스연세 사이트 테스트 시작 ===")
        
        # Chrome 드라이버 설정
        driver = setup_driver()
        if not driver:
            logger.error("Chrome 드라이버 설정 실패")
            return False
        
        logger.info("Chrome 드라이버 설정 성공!")
        
        # 런어스연세 메인 페이지 테스트
        logger.info("런어스연세 메인 페이지 테스트 시작...")
        driver.get("https://ys.learnus.org/")
        time.sleep(3)
        
        title = driver.title
        logger.info(f"런어스연세 페이지 제목: {title}")
        
        if "LearnUs" in title or "런어스" in title:
            logger.info("런어스연세 페이지 접근 성공!")
        else:
            logger.warning("런어스연세 페이지 접근 결과 이상")
        
        # 로그인 페이지 테스트
        logger.info("런어스연세 로그인 페이지 테스트 시작...")
        driver.get("https://ys.learnus.org/passni/sso/spLogin2.php")
        time.sleep(3)
        
        login_title = driver.title
        logger.info(f"로그인 페이지 제목: {login_title}")
        
        # 로그인 폼 요소 확인
        try:
            username_field = driver.find_element(By.CSS_SELECTOR, "input[id='loginId']")
            logger.info("사용자명 필드 발견!")
        except:
            logger.warning("사용자명 필드를 찾을 수 없습니다.")
        
        try:
            password_field = driver.find_element(By.CSS_SELECTOR, "input[type='password']")
            logger.info("비밀번호 필드 발견!")
        except:
            logger.warning("비밀번호 필드를 찾을 수 없습니다.")
        
        logger.info("=== 런어스연세 사이트 테스트 완료 ===")
        return True
        
    except Exception as e:
        logger.error(f"런어스연세 사이트 테스트 실패: {e}")
        return False
        
    finally:
        if driver:
            try:
                driver.quit()
                logger.info("Chrome 드라이버 종료")
            except:
                pass

def main():
    """메인 실행 함수"""
    try:
        logger.info("=== 로컬 Chrome 드라이버 테스트 시작 ===")
        
        if test_yonsei_site():
            logger.info("런어스연세 사이트 테스트 성공!")
        else:
            logger.error("런어스연세 사이트 테스트 실패!")
        
    except Exception as e:
        logger.error(f"테스트 실행 실패: {e}")

if __name__ == "__main__":
    main()
