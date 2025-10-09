"""
Chrome 드라이버 간단 테스트 - Windows 환경 최적화
"""

import time
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_chrome_simple():
    """Chrome 드라이버 간단 테스트"""
    driver = None
    try:
        logger.info("Chrome 드라이버 간단 테스트 시작")
        
        chrome_options = Options()
        
        # Windows 환경을 위한 최소한의 옵션들
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-plugins")
        chrome_options.add_argument("--disable-images")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        chrome_options.add_argument("--log-level=3")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        
        # DevToolsActivePort 오류 해결
        chrome_options.add_argument("--remote-debugging-port=0")
        chrome_options.add_argument("--disable-dev-tools")
        chrome_options.add_argument("--disable-software-rasterizer")
        chrome_options.add_argument("--disable-gpu-sandbox")
        chrome_options.add_argument("--disable-gpu-process-crash-limit")
        chrome_options.add_argument("--disable-gpu-memory-buffer-compositor-resources")
        chrome_options.add_argument("--disable-gpu-rasterization")
        chrome_options.add_argument("--disable-background-timer-throttling")
        chrome_options.add_argument("--disable-backgrounding-occluded-windows")
        chrome_options.add_argument("--disable-renderer-backgrounding")
        chrome_options.add_argument("--disable-features=VizDisplayCompositor")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-plugins")
        chrome_options.add_argument("--disable-images")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        chrome_options.add_argument("--log-level=3")
        chrome_options.add_argument("--no-zygote")
        chrome_options.add_argument("--memory-pressure-off")
        chrome_options.add_argument("--max_old_space_size=4096")
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
        chrome_options.add_argument("--disable-prompt-on-repost")
        chrome_options.add_argument("--disable-hang-monitor")
        chrome_options.add_argument("--disable-client-side-phishing-detection")
        chrome_options.add_argument("--disable-component-update")
        chrome_options.add_argument("--disable-domain-reliability")
        chrome_options.add_argument("--disable-features=TranslateUI")
        chrome_options.add_argument("--disable-ipc-flooding-protection")
        
        # Chrome 드라이버 실행
        logger.info("Chrome 드라이버 시작 중...")
        driver = webdriver.Chrome(options=chrome_options)
        driver.set_page_load_timeout(30)
        driver.implicitly_wait(10)
        
        logger.info("Chrome 드라이버 설정 완료")
        
        # 간단한 웹페이지 테스트
        logger.info("웹페이지 테스트 시작...")
        driver.get("https://www.google.com")
        time.sleep(2)
        
        title = driver.title
        logger.info(f"페이지 제목: {title}")
        
        if "Google" in title:
            logger.info("웹페이지 테스트 성공!")
        else:
            logger.warning("웹페이지 테스트 결과 이상")
        
        # LearnUs 페이지 테스트
        logger.info("LearnUs 페이지 테스트 시작...")
        driver.get("https://learnus.org/")
        time.sleep(3)
        
        learnus_title = driver.title
        logger.info(f"LearnUs 페이지 제목: {learnus_title}")
        
        if "LearnUs" in learnus_title or "런어스" in learnus_title:
            logger.info("LearnUs 페이지 접근 성공!")
        else:
            logger.warning("LearnUs 페이지 접근 결과 이상")
        
        logger.info("Chrome 드라이버 테스트 완료")
        return True
        
    except Exception as e:
        logger.error(f"Chrome 드라이버 테스트 실패: {e}")
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
        logger.info("Chrome 드라이버 간단 테스트 시작")
        
        if test_chrome_simple():
            logger.info("Chrome 드라이버 테스트 성공!")
        else:
            logger.error("Chrome 드라이버 테스트 실패!")
        
    except Exception as e:
        logger.error(f"테스트 실행 실패: {e}")

if __name__ == "__main__":
    main()











