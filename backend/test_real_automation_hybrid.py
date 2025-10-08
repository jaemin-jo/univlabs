"""
완벽한 혼합 버전 자동화 스크립트
- 기존 코드의 검증된 과목 순차 처리 로직
- 픽스드 버전의 향상된 요소 추출 로직
- 9887 빠른 실행 기능 포함
"""

import asyncio
import json
import requests
import logging
import time
import re
import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.service import Service

# 로깅 설정 (JST 시간대)
import os
os.environ['TZ'] = 'Asia/Tokyo'  # JST 시간대 설정

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler('automation_debug.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def safe_mouse_move(driver, x_offset=0, y_offset=0):
    """안전한 마우스 이동 함수"""
    try:
        # 화면 크기 확인
        window_size = driver.get_window_size()
        max_x = window_size['width']
        max_y = window_size['height']
        
        # 안전한 범위 내에서만 이동
        safe_x = max(10, min(x_offset, max_x - 10))
        safe_y = max(10, min(y_offset, max_y - 10))
        
        actions = ActionChains(driver)
        actions.move_by_offset(safe_x, safe_y).perform()
        time.sleep(0.1)
        actions.move_by_offset(-safe_x, -safe_y).perform()
        time.sleep(0.1)
        return True
    except Exception as e:
        logger.debug(f"마우스 이동 실패 (무시): {e}")
        return False

def check_completion_status_on_main_page(driver, activity_url):
    """메인 페이지에서 특정 활동의 완료 상태 아이콘 확인 (BeautifulSoup 사용)"""
    try:
        # 활동 URL에서 활동 ID 추출
        activity_id = None
        if "id=" in activity_url:
            activity_id = activity_url.split("id=")[1].split("&")[0]
        
        if not activity_id:
            return "⏳ 대기 중"
        
        logger.debug(f"🔍 활동 ID {activity_id}의 완료 상태 확인 중...")
        
        # 현재 페이지의 HTML 소스 가져오기
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        
        # 특정 활동의 li 요소 찾기
        activity_li = soup.find('li', {'id': f'module-{activity_id}'})
        
        if not activity_li:
            logger.debug(f"❌ 활동 ID {activity_id}에 해당하는 li 요소를 찾을 수 없음")
            return "⏳ 대기 중"
        
        # autocompletion span 내의 img 태그 찾기
        autocompletion_span = activity_li.find('span', class_='autocompletion')
        
        if not autocompletion_span:
            logger.debug(f"⏳ 활동 ID {activity_id}: autocompletion span 없음")
            return "⏳ 대기 중"
        
        # img 태그 찾기
        img_tag = autocompletion_span.find('img', class_='icon')
        
        if not img_tag:
            logger.debug(f"⏳ 활동 ID {activity_id}: 완료 아이콘 없음")
            return "⏳ 대기 중"
        
        # img 태그의 속성들 확인
        title = img_tag.get('title', '')
        alt = img_tag.get('alt', '')
        src = img_tag.get('src', '')
        
        logger.debug(f"🔍 활동 ID {activity_id} 아이콘 정보:")
        logger.debug(f"   title: {title}")
        logger.debug(f"   alt: {alt}")
        logger.debug(f"   src: {src}")
        
        # 완료 상태 판단
        if '완료함' in title or '완료함' in alt or 'completion-auto-y' in src:
            logger.debug(f"✅ 활동 ID {activity_id}: 완료 상태 확인")
            return "✅ 완료"
        elif '완료하지 못함' in title or '완료하지 못함' in alt or 'completion-auto-n' in src:
            logger.debug(f"❌ 활동 ID {activity_id}: 미완료 상태 확인")
            return "❌ 해야 할 과제"  # 완료하지 못함 = 해야 할 과제
        else:
            logger.debug(f"⏳ 활동 ID {activity_id}: 상태 불명")
            return "⏳ 대기 중"
        
    except Exception as e:
        logger.debug(f"완료 상태 확인 실패: {e}")
        return "❓ 상태 확인 불가"

def check_assignment_status(driver, assignment_url):
    """과제 완료 상태 확인 (빠른 확인)"""
    try:
        # 메인 페이지에서 바로 아이콘 확인 (페이지 이동 없음)
        completion_selectors = [
            "//span[@class='autocompletion']//img[@class='icon' and contains(@title, '완료함')]",
            "//span[@class='autocompletion']//img[@class='icon' and contains(@alt, '완료함')]",
            "//span[@class='autocompletion']//img[@class='icon' and contains(@src, 'completion-auto-y')]",
            "//img[@class='icon' and contains(@title, '완료함')]",
            "//img[@class='icon' and contains(@src, 'completion-auto-y')]",
        ]
        
        for selector in completion_selectors:
            try:
                element = driver.find_element(By.XPATH, selector)
                if element:
                    return "✅ 완료"
            except:
                continue
        
        # 미완료 상태 확인
        incomplete_selectors = [
            "//span[@class='autocompletion']//img[@class='icon' and contains(@title, '완료하지 못함')]",
            "//span[@class='autocompletion']//img[@class='icon' and contains(@alt, '완료하지 못함')]",
            "//span[@class='autocompletion']//img[@class='icon' and contains(@src, 'completion-auto-n')]",
            "//img[@class='icon' and contains(@title, '완료하지 못함')]",
            "//img[@class='icon' and contains(@src, 'completion-auto-n')]",
        ]
        
        for selector in incomplete_selectors:
            try:
                element = driver.find_element(By.XPATH, selector)
                if element:
                    return "❌ 미완료"
            except:
                continue
        
        return "⏳ 대기 중"
        
    except Exception as e:
        logger.debug(f"과제 상태 확인 실패: {e}")
        return "❓ 상태 확인 불가"

def check_video_status(driver, video_url):
    """동영상 시청 상태 확인 (LearnUs 실제 구조 기반)"""
    try:
        # 메인 페이지에서 바로 아이콘 확인 (페이지 이동 없음)
        
        # 완료 상태 확인
        completion_selectors = [
            "//span[@class='autocompletion']//img[@class='icon' and contains(@title, '완료함')]",
            "//span[@class='autocompletion']//img[@class='icon' and contains(@alt, '완료함')]",
            "//span[@class='autocompletion']//img[@class='icon' and contains(@src, 'completion-auto-y')]",
            "//img[@class='icon' and contains(@title, '완료함')]",
            "//img[@class='icon' and contains(@src, 'completion-auto-y')]",
        ]
        
        for selector in completion_selectors:
            try:
                element = driver.find_element(By.XPATH, selector)
                if element:
                    return "✅ 시청완료"
            except:
                continue
        
        # 미완료 상태 확인
        incomplete_selectors = [
            "//span[@class='autocompletion']//img[@class='icon' and contains(@title, '완료하지 못함')]",
            "//span[@class='autocompletion']//img[@class='icon' and contains(@alt, '완료하지 못함')]",
            "//span[@class='autocompletion']//img[@class='icon' and contains(@src, 'completion-auto-n')]",
            "//img[@class='icon' and contains(@title, '완료하지 못함')]",
            "//img[@class='icon' and contains(@src, 'completion-auto-n')]",
        ]
        
        for selector in incomplete_selectors:
            try:
                element = driver.find_element(By.XPATH, selector)
                if element:
                    return "❌ 미시청"
            except:
                continue
        
        return "⏳ 대기 중"
        
    except Exception as e:
        logger.debug(f"동영상 상태 확인 실패: {e}")
        return "❓ 상태 확인 불가"

def check_quiz_status(driver, quiz_url):
    """퀴즈 완료 상태 확인 (LearnUs 실제 구조 기반)"""
    try:
        # 메인 페이지에서 바로 아이콘 확인 (페이지 이동 없음)
        
        # 완료 상태 확인
        completion_selectors = [
            "//span[@class='autocompletion']//img[@class='icon' and contains(@title, '완료함')]",
            "//span[@class='autocompletion']//img[@class='icon' and contains(@alt, '완료함')]",
            "//span[@class='autocompletion']//img[@class='icon' and contains(@src, 'completion-auto-y')]",
            "//img[@class='icon' and contains(@title, '완료함')]",
            "//img[@class='icon' and contains(@src, 'completion-auto-y')]",
        ]
        
        for selector in completion_selectors:
            try:
                element = driver.find_element(By.XPATH, selector)
                if element:
                    return "✅ 완료"
            except:
                continue
        
        # 미완료 상태 확인
        incomplete_selectors = [
            "//span[@class='autocompletion']//img[@class='icon' and contains(@title, '완료하지 못함')]",
            "//span[@class='autocompletion']//img[@class='icon' and contains(@alt, '완료하지 못함')]",
            "//span[@class='autocompletion']//img[@class='icon' and contains(@src, 'completion-auto-n')]",
            "//img[@class='icon' and contains(@title, '완료하지 못함')]",
            "//img[@class='icon' and contains(@src, 'completion-auto-n')]",
        ]
        
        for selector in incomplete_selectors:
            try:
                element = driver.find_element(By.XPATH, selector)
                if element:
                    return "❌ 미완료"
            except:
                continue
        
        return "⏳ 대기 중"
        
    except Exception as e:
        logger.debug(f"퀴즈 상태 확인 실패: {e}")
        return "❓ 상태 확인 불가"

def setup_driver():
    """Chrome 드라이버 설정 (Cloud Run 환경 최적화)"""
    try:
        logger.info("🔧 Chrome 드라이버 설정 중...")
        
        # 🔍 1단계: Chrome 실행 파일 확인
        logger.info("🔍 1단계: Chrome 실행 파일 확인 중...")
        chrome_bin_paths = [
            '/usr/bin/google-chrome',
            '/usr/bin/chromium-browser',
            '/usr/bin/chromium',
        ]
        
        chrome_found = False
        for chrome_path in chrome_bin_paths:
            if os.path.exists(chrome_path):
                logger.info(f"✅ Chrome 실행 파일 발견: {chrome_path}")
                os.environ['CHROME_BIN'] = chrome_path
                chrome_found = True
                break
        
        if not chrome_found:
            logger.warning("⚠️ Chrome 실행 파일을 찾을 수 없음, 기본 경로 사용")
        
        # 🔍 2단계: Chrome 옵션 설정
        logger.info("🔍 2단계: Chrome 옵션 설정 중...")
        chrome_options = Options()
        
        # 🔥 Cloud Run 환경 최적화 핵심 옵션들 (중복 제거, 필수만 유지)
        
        # DevToolsActivePort 오류 해결을 위한 핵심 옵션들
        chrome_options.add_argument("--no-sandbox")  # 필수: 샌드박스 비활성화
        chrome_options.add_argument("--disable-dev-shm-usage")  # 필수: 공유 메모리 비활성화
        chrome_options.add_argument("--disable-setuid-sandbox")  # 필수: setuid 샌드박스 비활성화
        chrome_options.add_argument("--disable-gpu")  # 필수: GPU 비활성화
        chrome_options.add_argument("--headless")  # 필수: 헤드리스 모드
        chrome_options.add_argument("--disable-web-security")  # 필수: 웹 보안 비활성화
        chrome_options.add_argument("--disable-features=VizDisplayCompositor")  # 필수: Viz 디스플레이 컴포저 비활성화
        chrome_options.add_argument("--remote-debugging-port=0")  # 핵심: 디버깅 포트 비활성화
        
        # 자동화 감지 우회 핵심 옵션들
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Cloud Run 환경 최적화 옵션들
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
        chrome_options.add_argument("--disable-component-update")
        chrome_options.add_argument("--disable-default-apps")
        chrome_options.add_argument("--no-first-run")
        chrome_options.add_argument("--disable-background-mode")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-plugins")
        chrome_options.add_argument("--disable-images")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--log-level=3")
        
        # 메모리 최적화 옵션들
        chrome_options.add_argument("--no-zygote")
        chrome_options.add_argument("--memory-pressure-off")
        chrome_options.add_argument("--max_old_space_size=4096")
        chrome_options.add_argument("--hide-scrollbars")
        chrome_options.add_argument("--mute-audio")
        chrome_options.add_argument("--disable-logging")
        chrome_options.add_argument("--disable-permissions-api")
        chrome_options.add_argument("--disable-popup-blocking")
        
        # GPU 관련 옵션들
        chrome_options.add_argument("--disable-dev-tools")
        chrome_options.add_argument("--disable-gpu-sandbox")
        chrome_options.add_argument("--disable-accelerated-2d-canvas")
        chrome_options.add_argument("--disable-accelerated-jpeg-decoding")
        chrome_options.add_argument("--disable-accelerated-mjpeg-decode")
        chrome_options.add_argument("--disable-accelerated-video-decode")
        chrome_options.add_argument("--disable-gpu-memory-buffer-compositor-resources")
        chrome_options.add_argument("--disable-gpu-memory-buffer-video-frames")
        chrome_options.add_argument("--disable-gpu-rasterization")
        chrome_options.add_argument("--disable-zero-copy")
        
        # 사용자 에이전트 설정 (Linux 환경에 맞춤)
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        chrome_options.add_argument("--accept-lang=ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7")
        
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Cloud Run 환경에서 Chrome 드라이버 설정 (시스템 드라이버 우선)
        try:
            # 🔥 시스템 Chrome 드라이버 우선 사용 (안정성)
            chrome_driver_paths = [
                "/usr/bin/chromedriver",  # 설치된 chromedriver
                "/usr/bin/chromium-driver",  # chromium-driver
                "/usr/lib/chromium-browser/chromedriver",  # chromium 경로
            ]
            
            service = None
            logger.info("🔍 시스템 Chrome 드라이버 경로 확인 중...")
            for i, path in enumerate(chrome_driver_paths):
                exists = os.path.exists(path)
                logger.info(f"   경로 {i+1}/{len(chrome_driver_paths)}: {path} - {'존재' if exists else '없음'}")
                if exists:
                    try:
                        # 파일 권한 확인
                        is_executable = os.access(path, os.X_OK)
                        file_size = os.path.getsize(path)
                        logger.info(f"   ✅ 파일 발견: {path}")
                        logger.info(f"   📊 파일 크기: {file_size} bytes")
                        logger.info(f"   🔐 실행 권한: {'있음' if is_executable else '없음'}")
                        
                        # ChromeDriver 버전 확인 시도
                        try:
                            import subprocess
                            result = subprocess.run([path, "--version"], capture_output=True, text=True, timeout=5)
                            if result.returncode == 0:
                                logger.info(f"   ✅ ChromeDriver 버전: {result.stdout.strip()}")
                            else:
                                logger.warning(f"   ⚠️ ChromeDriver 버전 확인 실패: {result.stderr}")
                        except Exception as version_error:
                            logger.warning(f"   ⚠️ ChromeDriver 버전 확인 오류: {version_error}")
                            
                        service = Service(path)
                        logger.info(f"✅ 시스템 Chrome 드라이버 사용: {path}")
                        break
                        
                    except Exception as file_error:
                        logger.error(f"   ❌ 파일 정보 확인 실패: {file_error}")
                        continue
            
            if service is None:
                logger.warning("시스템 드라이버 없음, WebDriver Manager 사용")
                try:
                    # WebDriver Manager fallback
                    logger.info("🔧 WebDriver Manager로 Chrome 드라이버 설치 중...")
                    wdm_path = ChromeDriverManager().install()
                    logger.info(f"✅ WebDriver Manager 경로: {wdm_path}")
                    
                    # WebDriver Manager 경로 확인
                    if os.path.exists(wdm_path):
                        logger.info(f"✅ WebDriver Manager 파일 존재: {wdm_path}")
                        service = Service(wdm_path)
                        logger.info("✅ WebDriver Manager로 Chrome 드라이버 설치")
                    else:
                        raise Exception(f"WebDriver Manager 파일이 존재하지 않음: {wdm_path}")
                        
                except Exception as wdm_error:
                    logger.error(f"❌ WebDriver Manager 실패: {wdm_error}")
                    raise Exception(f"모든 Chrome 드라이버 설정 실패: 시스템 드라이버 없음, WebDriver Manager 실패")
        
            driver = webdriver.Chrome(service=service, options=chrome_options)
            
        except Exception as driver_error:
            logger.error(f"❌ Chrome 드라이버 초기화 실패: {driver_error}")
            logger.error(f"   오류 타입: {type(driver_error).__name__}")
            logger.error(f"   오류 메시지: {str(driver_error)}")
            
            # 추가 디버깅 정보
            try:
                logger.info("🔍 추가 디버깅 정보:")
                logger.info(f"   현재 작업 디렉토리: {os.getcwd()}")
                import sys
                logger.info(f"   Python 버전: {sys.version}")
                
                # Chrome 실행 파일 확인
                chrome_paths = ["/usr/bin/google-chrome", "/usr/bin/chromium", "/usr/bin/chrome"]
                for chrome_path in chrome_paths:
                    if os.path.exists(chrome_path):
                        logger.info(f"   Chrome 실행 파일: {chrome_path}")
                        break
                else:
                    logger.warning("   Chrome 실행 파일을 찾을 수 없음")
                    
                # ChromeDriver 경로 재확인
                driver_paths = ["/usr/bin/chromedriver", "/usr/bin/chromium-driver"]
                for driver_path in driver_paths:
                    if os.path.exists(driver_path):
                        logger.info(f"   ChromeDriver 경로: {driver_path}")
                        try:
                            is_executable = os.access(driver_path, os.X_OK)
                            logger.info(f"   실행 권한: {'있음' if is_executable else '없음'}")
                        except Exception as perm_error:
                            logger.warning(f"   권한 확인 실패: {perm_error}")
                    else:
                        logger.warning(f"   ChromeDriver 없음: {driver_path}")
                        
            except Exception as debug_error:
                logger.error(f"   디버깅 정보 수집 실패: {debug_error}")
            
            # Cloud Run 환경에서 Chrome 실행을 위한 추가 시도
            try:
                # Chrome 실행 파일 경로 우선순위 설정
                chrome_bin_paths = [
                    '/usr/bin/google-chrome',
                    '/usr/bin/chromium-browser',
                    '/usr/bin/chromium',
                ]
                
                for chrome_path in chrome_bin_paths:
                    if os.path.exists(chrome_path):
                        os.environ['CHROME_BIN'] = chrome_path
                        logger.info(f"✅ Chrome 실행 파일 설정: {chrome_path}")
                        break
                
                # 직접 경로로 재시도
                service = Service('/usr/bin/chromedriver')
                driver = webdriver.Chrome(service=service, options=chrome_options)
                logger.info("✅ 직접 경로로 Chrome 드라이버 초기화 성공")
                
            except Exception as fallback_error:
                logger.error(f"❌ Chrome 드라이버 fallback 실패: {fallback_error}")
                return None
        
        # 자동화 감지 방지
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        logger.info("✅ Chrome 드라이버 초기화 완료")
        return driver
        
    except Exception as e:
        logger.error(f"❌ Chrome 드라이버 설정 실패: {e}")
        return None

def test_direct_selenium(university, username, password, student_id):
    """직접 Selenium 로그인 테스트 (기존 코드의 검증된 로직)"""
    driver = None
    try:
        logger.info("=" * 80)
        logger.info("🚀 LearnUs 자동화 시작")
        logger.info(f"   대학: {university}")
        logger.info(f"   사용자명: {username}")
        logger.info(f"   학생ID: {student_id}")
        logger.info("=" * 80)
        
        logger.info("🔧 Chrome 드라이버 초기화 중...")
        driver = setup_driver()
        if not driver:
            logger.error("❌ Chrome 드라이버 초기화 실패")
            return False
        
        # 🔥 자동화 감지 우회 JavaScript 실행
        logger.info("🔧 자동화 감지 우회 JavaScript 실행...")
        try:
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
                    delete window.selenium;
                    delete window.webdriver;
                    delete window.driver;
                    delete window.playwright;
                    delete window.automation;
                '''
            })
            logger.info("✅ 자동화 감지 우회 JavaScript 실행 완료")
        except Exception as e:
            logger.warning(f"⚠️ 자동화 감지 우회 JavaScript 실행 실패: {e}")
        
        logger.info("✅ Chrome 드라이버 초기화 성공")
        
        logger.info(f"🌐 LearnUs 메인 페이지 접속: https://ys.learnus.org/")
        driver.get("https://ys.learnus.org/")
        time.sleep(2)
        
        logger.info("⏳ 페이지 로딩 대기 중...")
        time.sleep(2)
        
        # 페이지 로딩 확인 (마우스 이동 제거)
        logger.info("📄 페이지 로딩 확인 중...")
        time.sleep(1)
        
        logger.info(f"📍 현재 URL: {driver.current_url}")
        logger.info(f"📄 페이지 제목: {driver.title}")
        
        # 페이지 소스 저장 (디버깅용)
        with open('debug_page_source.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        logger.info("💾 페이지 소스 저장: debug_page_source.html")
        
        # 연세포털 로그인 버튼 찾기 (기존 코드의 검증된 로직)
        login_button = None
        login_selectors = [
            "a.btn.btn-sso",
            "a[href*='sso']",
            "a[href*='login']",
            ".btn-sso",
            ".login-btn",
            "a:contains('연세포털')",
            "a:contains('로그인')",
            "button:contains('로그인')",
            "input[value*='로그인']"
        ]
        
        logger.info("🔍 연세포털 로그인 버튼 찾는 중...")
        for i, selector in enumerate(login_selectors):
            try:
                logger.info(f"   CSS 선택자 시도 중 ({i+1}/{len(login_selectors)}): {selector}")
                if ":contains" in selector:
                    # XPath로 변환
                    xpath = f"//a[contains(text(), '연세포털')] | //a[contains(text(), '로그인')] | //button[contains(text(), '로그인')] | //input[contains(@value, '로그인')]"
                    login_button = driver.find_element(By.XPATH, xpath)
                else:
                    login_button = driver.find_element(By.CSS_SELECTOR, selector)
                logger.info(f"✅ 연세포털 로그인 버튼 발견: {selector}")
                logger.info(f"   버튼 텍스트: {login_button.text}")
                logger.info(f"   버튼 태그: {login_button.tag_name}")
                break
            except Exception as e:
                logger.debug(f"   선택자 {selector} 실패: {e}")
                continue
        
        if login_button:
            logger.info("🖱️ 연세포털 로그인 버튼 클릭...")
            login_button.click()
            time.sleep(2)
            logger.info(f"📍 클릭 후 URL: {driver.current_url}")
            
            # 로그인 페이지 로딩 확인
            logger.info("📄 로그인 페이지 로딩 확인...")
            time.sleep(1)
        else:
            logger.info("로그인 버튼을 찾을 수 없음, 직접 로그인 페이지 접속")
            driver.get("https://ys.learnus.org/passni/sso/spLogin2.php")
            time.sleep(2)
            
            # 로그인 페이지 로딩 확인
            logger.info("📄 로그인 페이지 로딩 확인...")
            time.sleep(1)
        
        # 사용자명 필드 찾기 (기존 코드의 검증된 로직)
        username_field = None
        username_selectors = [
            "input[id='loginId']",
            "input[name='loginId']",
            "input[id='username']",
            "input[name='username']",
            "input[id='userid']",
            "input[name='userid']",
            "input[id='id']",
            "input[name='id']",
            "input[type='text']",
            "input[placeholder*='아이디']",
            "input[placeholder*='사용자']"
        ]
        
        logger.info("🔍 사용자명 필드 찾는 중...")
        for i, selector in enumerate(username_selectors):
            try:
                logger.info(f"   사용자명 필드 시도 중 ({i+1}/{len(username_selectors)}): {selector}")
                username_field = driver.find_element(By.CSS_SELECTOR, selector)
                logger.info(f"✅ 사용자명 필드 발견: {selector}")
                break
            except:
                continue
        
        if not username_field:
            logger.error("❌ 사용자명 필드를 찾을 수 없습니다")
            return False
        
        # 비밀번호 필드 찾기 (기존 코드의 검증된 로직)
        password_field = None
        password_selectors = [
            "input[id='loginPasswd']",  # 수정: 정확한 ID 사용
            "input[name='loginPasswd']",  # 수정: 정확한 name 사용
            "input[id='loginPw']",
            "input[name='loginPw']",
            "input[type='password']",
            "input[id='password']",
            "input[name='password']",
            "input[id='passwd']",
            "input[name='passwd']",
            "input[placeholder*='비밀번호']"
        ]
        
        logger.info("🔍 비밀번호 필드 찾는 중...")
        for i, selector in enumerate(password_selectors):
            try:
                logger.info(f"   비밀번호 필드 시도 중 ({i+1}/{len(password_selectors)}): {selector}")
                password_field = driver.find_element(By.CSS_SELECTOR, selector)
                logger.info(f"✅ 비밀번호 필드 발견: {selector}")
                break
            except:
                continue
        
        if not password_field:
            logger.error("❌ 비밀번호 필드를 찾을 수 없습니다")
            return False
        
        # 로그인 정보 입력
        logger.info("📝 로그인 정보 입력 중...")
        
        username_field.clear()
        username_field.send_keys(username)
        time.sleep(0.5)
        
        password_field.clear()
        password_field.send_keys(password)
        time.sleep(0.5)
        
        # 🔥 숨겨진 필드들 처리 (E2, E3, E4)
        logger.info("🔧 숨겨진 필드들 처리 중...")
        try:
            # E2 필드 설정 (JavaScript 사용)
            driver.execute_script("document.getElementById('E2').value = arguments[0];", username)
            logger.info("✅ E2 필드 설정 완료")
        except Exception as e:
            logger.warning(f"⚠️ E2 필드 설정 실패: {e}")
        
        try:
            # E3 필드 설정 (JavaScript 사용)
            driver.execute_script("document.getElementById('E3').value = arguments[0];", password)
            logger.info("✅ E3 필드 설정 완료")
        except Exception as e:
            logger.warning(f"⚠️ E3 필드 설정 실패: {e}")
        
        try:
            # E4 필드 설정 (JavaScript 사용)
            driver.execute_script("document.getElementById('E4').value = arguments[0];", username)
            logger.info("✅ E4 필드 설정 완료")
        except Exception as e:
            logger.warning(f"⚠️ E4 필드 설정 실패: {e}")
        
        # 로그인 버튼 찾기 및 클릭 (기존 코드의 검증된 로직)
        login_submit_button = None
        login_button_selectors = [
            "input[type='submit']",
            "button[type='submit']",
            "input[value*='로그인']",
            "button:contains('로그인')",
            ".login-btn",
            ".btn-login"
        ]
        
        logger.info("🔍 로그인 버튼 찾는 중...")
        for i, selector in enumerate(login_button_selectors):
            try:
                logger.info(f"   로그인 버튼 시도 중 ({i+1}/{len(login_button_selectors)}): {selector}")
                if ":contains" in selector:
                    xpath = "//input[contains(@value, '로그인')] | //button[contains(text(), '로그인')]"
                    login_submit_button = driver.find_element(By.XPATH, xpath)
                else:
                    login_submit_button = driver.find_element(By.CSS_SELECTOR, selector)
                logger.info(f"✅ 로그인 버튼 발견: {selector}")
                break
            except:
                continue
        
        # 로그인 시도 (Enter 키 우선, 버튼 클릭 대안)
        if login_submit_button:
            logger.info("🖱️ 로그인 버튼 클릭...")
            login_submit_button.click()
        else:
            logger.info("⌨️ Enter 키로 로그인 시도...")
            password_field.send_keys("\n")
        
        time.sleep(3)
        
        # 로그인 후 페이지 로딩 확인
        logger.info("📄 로그인 후 페이지 로딩 확인...")
        time.sleep(2)
        
        # 로그인 성공 확인
        current_url = driver.current_url
        page_title = driver.title
        logger.info(f"📍 로그인 후 URL: {current_url}")
        logger.info(f"📄 로그인 후 페이지 제목: {page_title}")
        
        if "ys.learnus.org" in current_url and "login" not in current_url.lower():
            logger.info("✅ 로그인 성공!")
            
            # 페이지 소스에서 로그인 상태 재확인
            page_source = driver.page_source
            if "로그아웃" in page_source or "logout" in page_source.lower():
                logger.info("✅ 로그인 상태 재확인: 로그아웃 버튼 발견")
            else:
                logger.warning("⚠️ 로그인 상태 불확실: 로그아웃 버튼 없음")
            
            # 🔥 과제 페이지로 이동 시도
            logger.info("🔍 과제 관련 페이지로 이동 시도...")
            try:
                # 과제 관련 링크 찾기
                assignment_links = driver.find_elements(By.CSS_SELECTOR, "a[href*='assignment'], a[href*='과제'], a[href*='task'], a[href*='homework']")
                if assignment_links:
                    logger.info(f"✅ 과제 관련 링크 {len(assignment_links)}개 발견")
                    for i, link in enumerate(assignment_links[:3]):
                        logger.info(f"   {i+1}. {link.text} - {link.get_attribute('href')}")
                    
                    # 첫 번째 과제 링크 클릭
                    assignment_links[0].click()
                    time.sleep(3)
                    logger.info(f"✅ 과제 페이지 이동: {driver.current_url}")
                else:
                    logger.info("ℹ️ 과제 관련 링크를 찾을 수 없음. 메인 페이지에서 과제 정보 수집 시도...")
            except Exception as e:
                logger.warning(f"⚠️ 과제 페이지 이동 실패: {e}")
            
            # 🔥 Playwright 분석 결과 기반 과제 수집
            logger.info("📚 LearnUs 과제 정보 수집 시작 (Playwright 분석 결과 기반)...")
            
            # 🔥 메인 페이지에서 과목 목록 수집
            logger.info("🔍 과목 목록 수집...")
            course_links = driver.find_elements(By.CSS_SELECTOR, "a[href*='course/view.php']")
            logger.info(f"✅ 발견된 과목 수: {len(course_links)}개")
            
            all_assignments = []
            
            # 각 과목별로 상세 정보 수집 (최대 3개 과목만 처리)
            for i, course_link in enumerate(course_links[:3]):
                try:
                    course_name = course_link.find_element(By.CSS_SELECTOR, "h3").text.strip()
                    course_url = course_link.get_attribute('href')
                    logger.info(f"🔍 과목 {i+1}: {course_name}")
                    
                    # 과목 페이지로 이동
                    driver.get(course_url)
                    time.sleep(2)
                    
                    # 🔥 과제 정보 수집 (Playwright 분석 결과 기반)
                    assignments = collect_course_assignments_optimized(driver, course_name)
                    all_assignments.extend(assignments)
                    
                    # 메인 페이지로 돌아가기
                    driver.get("https://ys.learnus.org/")
                    time.sleep(1)
                    
                except Exception as e:
                    logger.warning(f"⚠️ 과목 {i+1} 처리 실패: {e}")
                    continue
            
            logger.info(f"✅ 총 {len(all_assignments)}개 과제 수집 완료")
            assignments = all_assignments
            
            if assignments:
                logger.info(f"✅ 과제 수집 성공: {len(assignments)}개 과제 발견")
                for i, assignment in enumerate(assignments, 1):
                    logger.info(f"   {i}. {assignment.get('course', '')}: {assignment.get('activity', '')}")
            else:
                logger.warning("⚠️ 과제 수집 실패: 과제가 없거나 수집 실패")
            
            return assignments if assignments else []
        else:
            logger.error("❌ 로그인 실패")
            logger.error(f"   현재 URL: {current_url}")
            logger.error(f"   예상 URL: ys.learnus.org (login 없음)")
            return False
            
    except Exception as e:
        logger.error(f"❌ Selenium 로그인 오류: {e}")
        return False
    finally:
        if driver:
            time.sleep(2)
            logger.info("🔚 Chrome 드라이버 종료")
            driver.quit()

def collect_course_assignments_optimized(driver, course_name):
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

def collect_this_week_lectures_hybrid(driver):
    """혼합 로직으로 이번주 강의 정보 수집"""
    try:
        logger.info("=" * 60)
        logger.info("🔍 이번주 강의 정보 수집 시작...")
        logger.info(f"📍 현재 URL: {driver.current_url}")
        logger.info(f"📄 페이지 제목: {driver.title}")
        logger.info("=" * 60)
        
        # 페이지 소스 저장 (디버깅용)
        with open('debug_learnus_page.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        logger.info("💾 LearnUs 페이지 소스 저장: debug_learnus_page.html")
        
        # 실제 페이지 구조에 맞는 과목 찾기
        course_elements = []
        
        # 1. 기존 방식 (course-title h3)
        logger.info("🔍 course-title h3 태그 찾는 중...")
        course_elements = driver.find_elements(By.CSS_SELECTOR, ".course-title h3")
        logger.info(f"course-title 클래스 안의 h3 태그 {len(course_elements)}개 발견")
        
        # 2. 실제 페이지 구조에 맞는 방식들
        if len(course_elements) == 0:
            logger.info("course-title h3를 찾지 못함, 다른 선택자 시도...")
            alternative_selectors = [
                "h3",  # 기본 h3 태그
                ".course-box h3",
                ".course-name h3", 
                "a[href*='course/view.php'] h3",
                ".my-course-lists h3",
                # 실제 페이지 구조에 맞는 새로운 선택자들
                "a[href*='course']",  # 과목 링크
                ".card a",  # 카드 내 링크
                ".course-card a",  # 과목 카드 링크
                ".my-course a",  # 나의강좌 링크
                "div[class*='course'] a",  # course 클래스가 포함된 div의 링크
                # 🔥 추가된 과제 관련 선택자들
                ".assignment-item",  # 과제 아이템
                ".task-item",  # 작업 아이템
                ".homework-item",  # 숙제 아이템
                "a[href*='assignment']",  # 과제 링크
                "a[href*='task']",  # 작업 링크
                "a[href*='homework']",  # 숙제 링크
                ".activity-item",  # 활동 아이템
                ".module-item",  # 모듈 아이템
                "li[class*='course']",  # course 클래스가 포함된 li
                "div[class*='activity']",  # activity 클래스가 포함된 div
            ]
            
            for selector in alternative_selectors:
                course_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if len(course_elements) > 0:
                    logger.info(f"✅ {selector} 선택자로 {len(course_elements)}개 과목 발견")
                    break
                else:
                    logger.info(f"❌ {selector} 선택자로 과목을 찾지 못함")
        
        # 발견된 과목 목록 상세 로그
        if len(course_elements) > 0:
            logger.info("📚 발견된 과목 목록:")
            for idx, element in enumerate(course_elements):
                try:
                    course_text = element.text.strip()
                    logger.info(f"   {idx+1}. '{course_text}'")
                except Exception as e:
                    logger.info(f"   {idx+1}. 과목명 추출 실패: {e}")
        
        # 만약 위에서 찾지 못했다면 다른 선택자들도 시도
        if len(course_elements) == 0:
            logger.info("course-title h3를 찾지 못함, 다른 선택자 시도...")
            alternative_selectors = [
                "h3",  # 기본 h3 태그
                ".course-box h3",
                ".course-name h3", 
                "a[href*='course/view.php'] h3",
                ".my-course-lists h3"
            ]
            
            for selector in alternative_selectors:
                course_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if len(course_elements) > 0:
                    logger.info(f"✅ {selector} 선택자로 {len(course_elements)}개 과목 발견")
                    
                    # 발견된 과목 목록 상세 로그
                    logger.info(f"📚 {selector} 선택자로 발견된 과목 목록:")
                    for idx, element in enumerate(course_elements):
                        try:
                            course_text = element.text.strip()
                            logger.info(f"   {idx+1}. '{course_text}'")
                        except Exception as e:
                            logger.info(f"   {idx+1}. 과목명 추출 실패: {e}")
                    break
                else:
                    logger.info(f"❌ {selector} 선택자로 과목을 찾지 못함")
        
        # 과목 목록 로딩 확인
        logger.info("📄 과목 목록 로딩 확인 중...")
        time.sleep(1)
        
        all_lectures = []
        processed_courses = set()  # 중복 방지
        
        # 기존 코드의 검증된 과목 순차 처리 로직
        logger.info(f"🔄 총 {len(course_elements)}개 과목 순차 처리 시작...")
        logger.info(f"📋 처리된 과목 목록: {list(processed_courses)}")
        
        # 과목 인덱스를 추적하기 위한 변수
        current_course_index = 0
        
        # 순차적으로 과목 처리 (한 과목씩)
        logger.info(f"🔄 과목 순회 시작: 총 {len(course_elements)}개 과목, 현재 인덱스: {current_course_index}")
        while current_course_index < len(course_elements):
            try:
                logger.info(f"🔍 과목 {current_course_index+1}/{len(course_elements)} 처리 시작...")
                # Stale Element Reference 방지: 매번 새로운 요소 찾기
                try:
                    # 매번 새로운 요소 찾기로 Stale Element 방지
                    course_elements = driver.find_elements(By.CSS_SELECTOR, ".course-title h3")
                    if len(course_elements) == 0:
                        # 다른 선택자들로 재시도
                        alternative_selectors = [
                            "h3", ".course-box h3", ".course-name h3", 
                            "a[href*='course/view.php'] h3", ".my-course-lists h3",
                            "a[href*='course']", ".card a", ".course-card a"
                        ]
                        for selector in alternative_selectors:
                            course_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                            if len(course_elements) > 0:
                                break
                    
                    if current_course_index >= len(course_elements):
                        logger.warning(f"과목 {current_course_index+1}을 찾을 수 없음, 건너뜀")
                        current_course_index += 1
                        continue
                        
                    course_element = course_elements[current_course_index]
                    course_name = course_element.text.strip()
                    
                except Exception as stale_error:
                    logger.warning(f"Stale element 감지, 요소 재찾기: {stale_error}")
                    # 요소 재찾기
                    course_elements = driver.find_elements(By.CSS_SELECTOR, ".course-title h3")
                    if len(course_elements) == 0:
                        # 다른 선택자들로 재시도
                        alternative_selectors = [
                            "h3", ".course-box h3", ".course-name h3", 
                            "a[href*='course/view.php'] h3", ".my-course-lists h3",
                            "a[href*='course']", ".card a", ".course-card a"
                        ]
                        for selector in alternative_selectors:
                            course_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                            if len(course_elements) > 0:
                                break
                    
                    if current_course_index < len(course_elements):
                        course_element = course_elements[current_course_index]
                        course_name = course_element.text.strip()
                    else:
                        logger.warning(f"과목 {current_course_index+1}을 재찾을 수 없음, 건너뜀")
                        current_course_index += 1
                        continue
                
                i = current_course_index
                logger.info(f"🔍 과목 {i+1}/{len(course_elements)} 처리 시작...")
                logger.info(f"   📖 원본 과목명: '{course_name}'")
                
                # 과목명에서 불필요한 부분 제거 (예: "(2학기)" 등)
                original_course_name = course_name
                if "(" in course_name and ")" in course_name:
                    # 괄호 안의 내용이 학기 정보인지 확인
                    import re
                    semester_match = re.search(r'\((\d+학기)\)', course_name)
                    if semester_match:
                        # 학기 정보 제거
                        course_name = course_name.replace(semester_match.group(0), "").strip()
                        logger.info(f"   🧹 학기 정보 제거 후: '{course_name}' (원본: '{original_course_name}')")
                        
                        # 학기 정보 제거 후 과목명이 너무 짧아지면 원본 사용
                        if len(course_name) < 3:
                            course_name = original_course_name
                            logger.info(f"   🔄 학기 정보 제거 후 과목명이 너무 짧음, 원본 사용: '{course_name}'")
                
                logger.info(f"   📖 최종 과목명: '{course_name}'")
                
                if not course_name or len(course_name) < 3:
                    logger.info(f"   ⚠️ 과목명이 너무 짧음: '{course_name}' (길이: {len(course_name)})")
                    current_course_index += 1
                    logger.info(f"   🔄 과목명이 너무 짧아서 건너뛰고 다음 과목으로 이동 (인덱스: {current_course_index})")
                    continue
                
                # 중복 과목 처리 방지
                if course_name in processed_courses:
                    logger.info(f"   ⚠️ 중복 과목 건너뜀: '{course_name}' (이미 처리됨)")
                    current_course_index += 1
                    logger.info(f"   🔄 중복 과목 건너뛰고 다음 과목으로 이동 (인덱스: {current_course_index})")
                    continue
                
                processed_courses.add(course_name)
                logger.info(f"   ✅ 과목 {i+1}: '{course_name}' 처리 시작 (총 {len(processed_courses)}개 처리됨)")
                
                # Selenium으로 과목 클릭 (기존 코드의 간단한 로직)
                try:
                    # 과목 클릭 전 로딩 확인
                    logger.info(f"   📄 {course_name} 과목 클릭 전 로딩 확인...")
                    time.sleep(0.5)
                    
                    # Stale Element Reference 방지: 매번 새로운 요소 찾기
                    logger.info(f"   🔍 {course_name} 과목 요소 찾기 시작...")
                    selenium_course_element = None
                    
                    # WebDriverWait를 사용한 Stale Element Reference 방지
                    try:
                        # 과목 요소들이 로드될 때까지 명시적으로 대기
                        logger.info(f"   ⏳ {course_name} 과목 요소 로딩 대기 중...")
                        WebDriverWait(driver, 10).until(
                            EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".course-title h3"))
                        )
                        
                        # 현재 인덱스에 해당하는 과목 요소를 다시 찾기
                        fresh_course_elements = driver.find_elements(By.CSS_SELECTOR, ".course-title h3")
                        if len(fresh_course_elements) == 0:
                            # 다른 선택자들로 재시도
                            alternative_selectors = [
                                "h3", ".course-box h3", ".course-name h3", 
                                "a[href*='course/view.php'] h3", ".my-course-lists h3",
                                "a[href*='course']", ".card a", ".course-card a"
                            ]
                            for selector in alternative_selectors:
                                try:
                                    WebDriverWait(driver, 5).until(
                                        EC.presence_of_all_elements_located((By.CSS_SELECTOR, selector))
                                    )
                                    fresh_course_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                                    if len(fresh_course_elements) > 0:
                                        break
                                except:
                                    continue
                        
                        if current_course_index < len(fresh_course_elements):
                            selenium_course_element = fresh_course_elements[current_course_index]
                            logger.info(f"   ✅ {course_name} 과목 요소 재찾기 성공")
                        else:
                            logger.warning(f"   ⚠️ {course_name} 과목 요소를 재찾을 수 없음")
                            current_course_index += 1
                            continue
                    except Exception as e:
                        logger.warning(f"   ⚠️ 과목 요소 재찾기 실패: {e}")
                        current_course_index += 1
                        continue
                    
                    # 다양한 과목명 변형으로 시도
                    course_name_variations = [
                        course_name,  # 원본
                        course_name.replace(" NEW", ""),  # NEW 제거
                        course_name.replace(" NEW", " (2학기)NEW"),  # 학기 정보 추가
                        course_name.replace(" NEW", " (2학기)"),  # 학기 정보만 추가
                        original_course_name,  # 원본 과목명
                    ]
                    
                    # 실제 페이지 구조에 맞는 선택자들
                    selectors_to_try = []
                    for variation in course_name_variations:
                        selectors_to_try.extend([
                            # 기존 선택자들
                            f"//div[@class='course-title']//h3[contains(text(), '{variation}')]",
                            f"//h3[contains(text(), '{variation}')]",
                            f"//div[@class='course-box']//h3[contains(text(), '{variation}')]",
                            f"//div[@class='course-name']//h3[contains(text(), '{variation}')]",
                            # 실제 페이지 구조에 맞는 새로운 선택자들
                            f"//a[contains(text(), '{variation}')]",  # 링크로 된 과목명
                            f"//div[contains(@class, 'course')]//a[contains(text(), '{variation}')]",  # 카드 내 링크
                            f"//div[contains(@class, 'card')]//a[contains(text(), '{variation}')]",  # 카드 구조
                            f"//div[contains(@class, 'course-card')]//a[contains(text(), '{variation}')]",  # 과목 카드
                            f"//div[contains(@class, 'my-course')]//a[contains(text(), '{variation}')]",  # 나의강좌 카드
                        ])
                    
                    logger.info(f"   🔍 {len(selectors_to_try)}개 선택자로 {course_name} 과목 찾기 시도...")
                    for idx, selector in enumerate(selectors_to_try):
                        try:
                            logger.info(f"   🔍 선택자 {idx+1}/{len(selectors_to_try)} 시도: {selector}")
                            selenium_course_element = driver.find_element(By.XPATH, selector)
                            logger.info(f"   ✅ {course_name} 과목 요소 발견: {selector}")
                            break
                        except Exception as e:
                            logger.info(f"   ❌ 선택자 {idx+1} 실패: {str(e)[:100]}...")
                            continue
                    
                    # 마지막 시도: 부분 매칭으로 찾기
                    if not selenium_course_element:
                        logger.info(f"   🔍 부분 매칭으로 {course_name} 과목 찾기 시도...")
                        try:
                            # 과목명의 핵심 부분만 추출
                            core_name = course_name.split('(')[0].strip()  # 괄호 앞 부분만
                            if core_name:
                                partial_selectors = [
                                    # 기존 선택자들
                                    f"//div[@class='course-title']//h3[contains(text(), '{core_name}')]",
                                    f"//h3[contains(text(), '{core_name}')]",
                                    # 실제 페이지 구조에 맞는 선택자들
                                    f"//a[contains(text(), '{core_name}')]",
                                    f"//div[contains(@class, 'course')]//a[contains(text(), '{core_name}')]",
                                    f"//div[contains(@class, 'card')]//a[contains(text(), '{core_name}')]",
                                    f"//div[contains(@class, 'course-card')]//a[contains(text(), '{core_name}')]",
                                    f"//div[contains(@class, 'my-course')]//a[contains(text(), '{core_name}')]",
                                ]
                                
                                for selector in partial_selectors:
                                    try:
                                        selenium_course_element = driver.find_element(By.XPATH, selector)
                                        logger.info(f"   ✅ 부분 매칭으로 {course_name} 과목 발견: {selector}")
                                        break
                                    except:
                                        continue
                        except Exception as e:
                            logger.debug(f"   부분 매칭 실패: {e}")
                    
                    if not selenium_course_element:
                        logger.warning(f"   ⚠️ {course_name} 과목 요소를 찾을 수 없음 - 모든 선택자 실패")
                        logger.info(f"   🔍 현재 페이지에서 사용 가능한 h3 요소들:")
                        try:
                            all_h3_elements = driver.find_elements(By.TAG_NAME, "h3")
                            for idx, h3_elem in enumerate(all_h3_elements[:5]):  # 처음 5개만 표시
                                try:
                                    h3_text = h3_elem.text.strip()
                                    logger.info(f"      {idx+1}. '{h3_text}'")
                                except:
                                    logger.info(f"      {idx+1}. 텍스트 추출 실패")
                        except Exception as e:
                            logger.info(f"   ❌ h3 요소 검색 실패: {e}")
                        continue
                    
                    # 과목 클릭
                    selenium_course_element.click()
                    logger.info(f"   ✅ {course_name} 과목 페이지 진입")
                    
                    # WebDriverWait를 사용한 과목 페이지 로딩 확인
                    try:
                        logger.info(f"   ⏳ {course_name} 과목 페이지 로딩 대기 중...")
                        # 과목 페이지의 주요 요소가 로드될 때까지 대기
                        WebDriverWait(driver, 10).until(
                            EC.any_of(
                                EC.presence_of_element_located((By.CSS_SELECTOR, ".course-content")),
                                EC.presence_of_element_located((By.CSS_SELECTOR, ".course-header")),
                                EC.presence_of_element_located((By.CSS_SELECTOR, ".course-info")),
                                EC.presence_of_element_located((By.CSS_SELECTOR, ".course-title")),
                                EC.presence_of_element_located((By.CSS_SELECTOR, "h1")),
                                EC.presence_of_element_located((By.CSS_SELECTOR, "h2"))
                            )
                        )
                        logger.info(f"   ✅ {course_name} 과목 페이지 로딩 완료")
                    except Exception as e:
                        logger.warning(f"   ⚠️ {course_name} 과목 페이지 로딩 확인 실패: {e}")
                        # 로딩 실패해도 계속 진행
                    
                    # 과목 페이지 로딩 확인
                    logger.info(f"   📄 {course_name} 과목 페이지 로딩 확인...")
                    time.sleep(1)
                    
                except Exception as e:
                    logger.warning(f"   ⚠️ {course_name} 과목 클릭 실패: {e}")
                    continue
                
                # 픽스드 버전의 향상된 요소 추출 로직
                try:
                    current_page_source = driver.page_source
                    current_soup = BeautifulSoup(current_page_source, 'html.parser')
                    
                    # 이번주 강의 섹션 찾기 (5단계 강화된 로직)
                    this_week_section = None
                    
                    # 1단계: 다양한 선택자로 섹션 찾기
                    section_selectors = [
                        'li.section.main',
                        'div.section',
                        'div[class*="section"]',
                        'li[class*="section"]'
                    ]
                    
                    for selector in section_selectors:
                        sections = current_soup.select(selector)
                        for section in sections:
                            section_text = section.get_text().lower()
                            # 더 다양한 키워드로 검색 (주제별 학습활동 포함)
                            if any(keyword in section_text for keyword in [
                                "이번주 강의", "이번주", "current week", "current week course",
                                "이번주강의", "current week lecture", "week", "주차",
                                "이번 주", "현재 주", "current", "강의", "주제별 학습활동", "주제별학습활동"
                            ]):
                                # "강의 개요"는 제외
                                if "개요" not in section_text and "overview" not in section_text:
                                    this_week_section = section
                                    logger.info(f"   ✅ '이번주 강의' 섹션 발견: {section_text[:50]}...")
                                    break
                        if this_week_section:
                            break
                    
                    # 2단계: 정확한 키워드로 찾지 못함, 두 번째 섹션을 '이번주 강의'로 시도
                    if not this_week_section:
                        logger.info(f"   🔍 정확한 키워드로 찾지 못함, 두 번째 섹션을 '이번주 강의'로 시도")
                        for selector in section_selectors:
                            sections = current_soup.select(selector)
                            if len(sections) > 1:  # 두 번째 섹션이 있는 경우
                                this_week_section = sections[1]  # 두 번째 섹션 사용
                                logger.info(f"   ✅ 두 번째 섹션을 '이번주 강의'로 설정")
                                break
                    
                    # 3단계: 여전히 없으면 첫 번째 섹션 사용 (최후의 수단)
                    if not this_week_section:
                        logger.info(f"   🔍 두 번째 섹션도 없음, 첫 번째 섹션을 '이번주 강의'로 간주")
                        for selector in section_selectors:
                            sections = current_soup.select(selector)
                            if sections:
                                this_week_section = sections[0]  # 첫 번째 섹션 사용
                                logger.info(f"   ✅ 첫 번째 섹션을 '이번주 강의'로 설정")
                                break
                    
                    # 4단계: 링크가 있는 섹션 찾기
                    if not this_week_section:
                        logger.info(f"   🔍 링크가 있는 섹션을 '이번주 강의'로 시도")
                        for selector in section_selectors:
                            sections = current_soup.select(selector)
                            for section in sections:
                                links = section.find_all('a', href=True)
                                if links:
                                    this_week_section = section
                                    logger.info(f"   ✅ 링크가 있는 섹션을 '이번주 강의'로 설정")
                                    break
                            if this_week_section:
                                break
                    
                    # 5단계: 최후의 수단 - 모든 링크에서 부모 섹션 찾기
                    if not this_week_section:
                        logger.info(f"   🔍 최후의 수단: 모든 링크에서 부모 섹션 찾기")
                        all_links = current_soup.find_all('a', href=True)
                        for link in all_links:
                            parent_li = link.find_parent('li', class_=lambda x: x and 'section' in x)
                            if parent_li:
                                this_week_section = parent_li
                                logger.info(f"   ✅ 링크의 부모 섹션을 '이번주 강의'로 설정")
                                break
                            parent_div = link.find_parent('div', class_=lambda x: x and 'section' in x)
                            if parent_div:
                                this_week_section = parent_div
                                logger.info(f"   ✅ 링크의 부모 섹션을 '이번주 강의'로 설정")
                                break
                    
                    if this_week_section:
                        logger.info(f"   ✅ {course_name}에서 '이번주 강의' 섹션 발견")
                        
                        # 활동 링크 찾기
                        activity_links = this_week_section.find_all('a', href=True)
                        logger.info(f"   📚 {course_name}: {len(activity_links)}개 활동 발견")
                        
                        if len(activity_links) > 0:
                            for link in activity_links:
                                try:
                                    activity_name = link.get_text().strip()
                                    activity_url = link.get('href', '')
                                    
                                    if not activity_name or not activity_url:
                                        continue
                                    
                                    # 활동 타입 판별 (픽스드 버전의 향상된 로직)
                                    activity_type = "기타"
                                    completion_status = "상태 불명"
                                    
                                    if "mod/assign/" in activity_url:
                                        activity_type = "과제"
                                        # 과제 완료 상태 확인을 위한 추가 정보 수집
                                        try:
                                            # 과제 링크에서 완료 상태 확인
                                            # 메인 페이지에서 바로 완료 상태 아이콘 확인
                                            assignment_status = check_completion_status_on_main_page(driver, activity_url)
                                            completion_status = assignment_status
                                        except:
                                            completion_status = "상태 확인 불가"
                                    elif "mod/vod/" in activity_url:
                                        activity_type = "동영상"
                                        # 동영상 시청 상태 확인
                                        try:
                                            # 메인 페이지에서 바로 완료 상태 아이콘 확인
                                            video_status = check_completion_status_on_main_page(driver, activity_url)
                                            completion_status = video_status
                                        except:
                                            completion_status = "상태 확인 불가"
                                    elif "mod/resource/" in activity_url or "mod/ubfile/" in activity_url:
                                        activity_type = "PDF 자료"
                                        completion_status = "다운로드 가능"
                                    elif "mod/ubboard/" in activity_url:
                                        activity_type = "게시판"
                                        completion_status = "접근 가능"
                                    elif "mod/quiz/" in activity_url:
                                        activity_type = "퀴즈"
                                        # 퀴즈 완료 상태 확인
                                        try:
                                            # 메인 페이지에서 바로 완료 상태 아이콘 확인
                                            quiz_status = check_completion_status_on_main_page(driver, activity_url)
                                            completion_status = quiz_status
                                        except:
                                            completion_status = "상태 확인 불가"
                                    elif "mod/forum/" in activity_url:
                                        activity_type = "토론"
                                        completion_status = "참여 가능"
                                    elif "mod/lesson/" in activity_url:
                                        activity_type = "강의"
                                        completion_status = "학습 가능"
                                    elif "mod/page/" in activity_url:
                                        activity_type = "페이지"
                                        completion_status = "접근 가능"
                                    
                                    lecture_info = {
                                        'course': course_name,
                                        'activity': activity_name,
                                        'type': activity_type,
                                        'url': activity_url,
                                        'status': completion_status
                                    }
                                    all_lectures.append(lecture_info)
                                    logger.info(f"      ✅ {activity_name} ({activity_type})")
                                    
                                except Exception as e:
                                    logger.debug(f"      활동 정보 추출 실패: {e}")
                                    continue
                        else:
                            # 활동이 없어도 과목명은 기록
                            logger.info(f"   📝 {course_name}: 이번주 강의 활동 없음, 과목명만 기록")
                            lecture_info = {
                                'course': course_name,
                                'activity': '이번주 강의 활동 없음',
                                'type': '정보 없음',
                                'url': ''
                            }
                            all_lectures.append(lecture_info)
                    else:
                        logger.info(f"   📭 {course_name}: '이번주 강의' 섹션 없음, 과목명만 기록")
                        # 섹션이 없어도 과목명은 기록
                        lecture_info = {
                            'course': course_name,
                            'activity': '이번주 강의 섹션 없음',
                            'type': '정보 없음',
                            'url': ''
                        }
                        all_lectures.append(lecture_info)
                
                except Exception as e:
                    logger.warning(f"   {course_name} 페이지 분석 실패: {e}")
                
                # 메인 페이지로 돌아가기 (WebDriverWait 사용)
                try:
                    driver.back()
                    logger.info(f"   ✅ {course_name} 메인 페이지 복귀 완료")
                    
                    # WebDriverWait를 사용한 메인 페이지 로딩 대기
                    try:
                        logger.info(f"   ⏳ {course_name} 메인 페이지 로딩 대기 중...")
                        # 메인 페이지의 과목 목록이 로드될 때까지 대기
                        WebDriverWait(driver, 10).until(
                            EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".course-title h3"))
                        )
                        logger.info(f"   ✅ {course_name} 메인 페이지 로딩 완료")
                    except Exception as e:
                        logger.warning(f"   ⚠️ {course_name} 메인 페이지 로딩 확인 실패: {e}")
                        # 로딩 실패해도 계속 진행
                    
                    # 메인 페이지 복귀 후 상태 확인
                    current_url = driver.current_url
                    logger.info(f"   📍 복귀 후 URL: {current_url}")
                    
                    # 메인 페이지인지 확인
                    if "ys.learnus.org" in current_url and "course/view.php" not in current_url:
                        logger.info(f"   ✅ {course_name} 메인 페이지 정상 복귀 확인")
                        
                        # 메인 페이지 복귀 후 과목 목록 다시 찾기
                        logger.info(f"   🔄 {course_name} 메인 페이지 복귀 후 과목 목록 재검색...")
                        new_course_elements = driver.find_elements(By.CSS_SELECTOR, ".course-title h3")
                        logger.info(f"   📚 재검색된 과목 수: {len(new_course_elements)}개")
                        
                        # 과목 목록 업데이트
                        if len(new_course_elements) > 0:
                            course_elements = new_course_elements
                            logger.info(f"   ✅ {course_name} 과목 목록 업데이트 완료")
                            
                            # 과목 목록이 업데이트되었으므로 현재 인덱스 조정
                            if current_course_index >= len(course_elements):
                                logger.info(f"   🔄 {course_name} 과목 목록 업데이트로 인덱스 조정: {current_course_index} -> {len(course_elements)-1}")
                                current_course_index = len(course_elements) - 1
                        else:
                            logger.warning(f"   ⚠️ {course_name} 재검색된 과목 목록이 비어있음")
                        
                        # 재검색된 과목 목록 상세 로그
                        if len(course_elements) > 0:
                            logger.info(f"   📚 {course_name} 복귀 후 발견된 과목 목록:")
                            for idx, element in enumerate(course_elements):
                                try:
                                    course_text = element.text.strip()
                                    logger.info(f"      {idx+1}. '{course_text}'")
                                except Exception as e:
                                    logger.info(f"      {idx+1}. 과목명 추출 실패: {e}")
                        
                        # 과목 목록이 비어있다면 다른 선택자도 시도
                        if len(course_elements) == 0:
                            logger.info(f"   🔄 {course_name} 과목 목록이 비어있음, 다른 선택자 시도...")
                            alternative_selectors = [
                                "h3",
                                ".course-box h3",
                                ".course-name h3", 
                                "a[href*='course/view.php'] h3",
                                ".my-course-lists h3"
                            ]
                            
                            for selector in alternative_selectors:
                                logger.info(f"   🔍 {course_name} 대안 선택자 시도: {selector}")
                                course_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                                if len(course_elements) > 0:
                                    logger.info(f"   ✅ {course_name} {selector} 선택자로 {len(course_elements)}개 과목 재발견")
                                    
                                    # 재발견된 과목 목록 상세 로그
                                    logger.info(f"   📚 {course_name} {selector} 선택자로 재발견된 과목 목록:")
                                    for idx, element in enumerate(course_elements):
                                        try:
                                            course_text = element.text.strip()
                                            logger.info(f"      {idx+1}. '{course_text}'")
                                        except Exception as e:
                                            logger.info(f"      {idx+1}. 과목명 추출 실패: {e}")
                                    break
                                else:
                                    logger.info(f"   ❌ {course_name} {selector} 선택자로 과목을 찾지 못함")
                    else:
                        logger.warning(f"   ⚠️ {course_name} 메인 페이지 복귀 실패, 아직 과목 페이지에 있음")
                        # 한 번 더 뒤로가기 시도
                        try:
                            driver.back()
                            time.sleep(0.5)
                            logger.info(f"   🔄 {course_name} 추가 뒤로가기 시도")
                        except:
                            pass
                    
                    # 메인 페이지 복귀 후 로딩 확인
                    logger.info(f"   📄 {course_name} 메인 페이지 복귀 후 로딩 확인...")
                    time.sleep(1)
                    
                except Exception as e:
                    logger.warning(f"   {course_name} 메인 페이지 복귀 실패: {e}")
                    # 복귀 실패 시 메인 페이지로 직접 이동
                    try:
                        driver.get("https://ys.learnus.org/")
                        time.sleep(1)
                        logger.info(f"   🔄 {course_name} 메인 페이지 직접 이동")
                        
                        # 직접 이동 후 상태 확인
                        current_url = driver.current_url
                        logger.info(f"   📍 직접 이동 후 URL: {current_url}")
                        
                        # 직접 이동 후 과목 목록 다시 찾기
                        logger.info(f"   🔄 {course_name} 직접 이동 후 과목 목록 재검색...")
                        new_course_elements = driver.find_elements(By.CSS_SELECTOR, ".course-title h3")
                        logger.info(f"   📚 재검색된 과목 수: {len(new_course_elements)}개")
                        
                        # 과목 목록 업데이트
                        if len(new_course_elements) > 0:
                            course_elements = new_course_elements
                            logger.info(f"   ✅ {course_name} 직접 이동 후 과목 목록 업데이트 완료")
                            
                            # 과목 목록이 업데이트되었으므로 현재 인덱스 조정
                            if current_course_index >= len(course_elements):
                                logger.info(f"   🔄 {course_name} 직접 이동 후 과목 목록 업데이트로 인덱스 조정: {current_course_index} -> {len(course_elements)-1}")
                                current_course_index = len(course_elements) - 1
                        else:
                            logger.warning(f"   ⚠️ {course_name} 직접 이동 후 재검색된 과목 목록이 비어있음")
                        
                        # 과목 목록이 비어있다면 다른 선택자도 시도
                        if len(course_elements) == 0:
                            logger.info(f"   🔄 {course_name} 직접 이동 후 과목 목록이 비어있음, 다른 선택자 시도...")
                            alternative_selectors = [
                                "h3",
                                ".course-box h3",
                                ".course-name h3", 
                                "a[href*='course/view.php'] h3",
                                ".my-course-lists h3"
                            ]
                            
                            for selector in alternative_selectors:
                                course_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                                if len(course_elements) > 0:
                                    logger.info(f"   ✅ {course_name} 직접 이동 후 {selector} 선택자로 {len(course_elements)}개 과목 재발견")
                                    break
                        
                        # 직접 이동 후 로딩 확인
                        logger.info(f"   📄 {course_name} 직접 이동 후 로딩 확인...")
                        time.sleep(1)
                        
                    except Exception as e2:
                        logger.error(f"   ❌ {course_name} 메인 페이지 직접 이동 실패: {e2}")
                
                # 과목 처리 완료 후 인덱스 증가
                current_course_index += 1
                logger.info(f"   ✅ {course_name} 처리 완료, 다음 과목으로 이동 (인덱스: {current_course_index})")
                    
            except Exception as e:
                logger.error(f"❌ 과목 {current_course_index+1} 처리 실패: {e}")
                logger.error(f"❌ 오류 상세: {str(e)}")
                import traceback
                logger.error(f"❌ 스택 트레이스: {traceback.format_exc()}")
                current_course_index += 1
                continue
        
        logger.info(f"🔍 총 {len(all_lectures)}개 활동 수집 완료")
        logger.info(f"📚 처리된 과목 수: {len(processed_courses)}개")
        logger.info(f"📋 최종 처리된 과목 목록: {list(processed_courses)}")
        
        # 처리되지 않은 과목이 있는지 확인
        if len(processed_courses) < len(course_elements):
            logger.warning(f"⚠️ 일부 과목이 처리되지 않음: {len(processed_courses)}/{len(course_elements)}")
            logger.info("🔍 처리되지 않은 과목들:")
            for i, element in enumerate(course_elements):
                try:
                    course_text = element.text.strip()
                    if course_text not in processed_courses:
                        logger.info(f"   - '{course_text}'")
                except:
                    logger.info(f"   - 과목 {i+1} (텍스트 추출 실패)")
        
        # 최종 결과 로딩 확인
        logger.info("📄 최종 결과 로딩 확인...")
        time.sleep(1)
        
        # 결과를 파일로 저장
        try:
            with open('assignment.txt', 'w', encoding='utf-8') as f:
                f.write("📚 LearnUs 과목 및 이번주 강의 활동 목록\n")
                f.write("=" * 60 + "\n\n")
                f.write(f"수집 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"총 수집된 항목 수: {len(all_lectures)}개\n")
                f.write(f"처리된 과목 수: {len(processed_courses)}개\n\n")
                
                if all_lectures:
                    # 과목별로 그룹화
                    course_groups = {}
                    for lecture in all_lectures:
                        course = lecture['course']
                        if course not in course_groups:
                            course_groups[course] = []
                        course_groups[course].append(lecture)
                    
                    # 과목별로 출력
                    for course, lectures in course_groups.items():
                        f.write(f"📖 {course}\n")
                        f.write("-" * 50 + "\n")
                        
                        # 활동이 있는지 확인
                        has_activities = any(lecture['activity'] not in ['이번주 강의 활동 없음', '이번주 강의 섹션 없음'] for lecture in lectures)
                        
                        if has_activities:
                            f.write("📚 이번주 강의 활동:\n")
                            for lecture in lectures:
                                if lecture['activity'] not in ['이번주 강의 활동 없음', '이번주 강의 섹션 없음']:
                                    f.write(f"  • {lecture['activity']} ({lecture['type']}) - {lecture.get('status', '상태 불명')}\n")
                                    if lecture['url']:
                                        f.write(f"    URL: {lecture['url']}\n")
                                    f.write("\n")
                        else:
                            f.write("📝 이번주 강의 정보: 활동 없음\n")
                            for lecture in lectures:
                                if lecture['activity'] in ['이번주 강의 활동 없음', '이번주 강의 섹션 없음']:
                                    f.write(f"  • {lecture['activity']}\n")
                        f.write("\n")
                    
                    # 요약 정보 추가
                    f.write("\n" + "=" * 60 + "\n")
                    f.write("📊 요약 정보\n")
                    f.write("=" * 60 + "\n")
                    
                    # 활동이 있는 과목과 없는 과목 분류
                    courses_with_activities = []
                    courses_without_activities = []
                    
                    for course, lectures in course_groups.items():
                        has_activities = any(lecture['activity'] not in ['이번주 강의 활동 없음', '이번주 강의 섹션 없음'] for lecture in lectures)
                        if has_activities:
                            courses_with_activities.append(course)
                        else:
                            courses_without_activities.append(course)
                    
                    f.write(f"✅ 이번주 강의 활동이 있는 과목: {len(courses_with_activities)}개\n")
                    for course in courses_with_activities:
                        f.write(f"  • {course}\n")
                    
                    f.write(f"\n📝 이번주 강의 활동이 없는 과목: {len(courses_without_activities)}개\n")
                    for course in courses_without_activities:
                        f.write(f"  • {course}\n")
                    
                    # 이번주 해야 할 과제만 따로 정리
                    f.write("\n" + "=" * 60 + "\n")
                    f.write("📋 이번주 해야 할 과제 목록\n")
                    f.write("=" * 60 + "\n")
                    
                    # 완료되지 않은 과제들만 필터링
                    incomplete_assignments = []
                    incomplete_videos = []
                    incomplete_other_activities = []
                    
                    for lecture in all_lectures:
                        if lecture['activity'] not in ['이번주 강의 활동 없음', '이번주 강의 섹션 없음']:
                            status = lecture.get('status', '상태 불명')
                            # "해야 할 과제" 또는 "미완료" 상태인 것만 포함
                            if '해야 할 과제' in status or '미완료' in status or '미시청' in status:
                                if lecture['type'] == '과제':
                                    incomplete_assignments.append(lecture)
                                elif lecture['type'] == '동영상':
                                    incomplete_videos.append(lecture)
                                else:
                                    incomplete_other_activities.append(lecture)
                    
                    if incomplete_assignments:
                        f.write("📝 해야 할 과제:\n")
                        for assignment in incomplete_assignments:
                            f.write(f"  • {assignment['course']}: {assignment['activity']} - {assignment.get('status', '상태 불명')}\n")
                            if assignment['url']:
                                f.write(f"    URL: {assignment['url']}\n")
                        f.write("\n")
                    
                    if incomplete_videos:
                        f.write("🎥 시청해야 할 동영상:\n")
                        for video in incomplete_videos:
                            f.write(f"  • {video['course']}: {video['activity']} - {video.get('status', '상태 불명')}\n")
                            if video['url']:
                                f.write(f"    URL: {video['url']}\n")
                        f.write("\n")
                    
                    if incomplete_other_activities:
                        f.write("📚 해야 할 기타 활동:\n")
                        for activity in incomplete_other_activities:
                            f.write(f"  • {activity['course']}: {activity['activity']} ({activity['type']}) - {activity.get('status', '상태 불명')}\n")
                            if activity['url']:
                                f.write(f"    URL: {activity['url']}\n")
                        f.write("\n")
                    
                    if not incomplete_assignments and not incomplete_videos and not incomplete_other_activities:
                        f.write("📝 이번주 해야 할 과제가 없습니다.\n")
                        
                else:
                    f.write("⚠️ 과목 정보를 찾을 수 없습니다\n")
            
            logger.info("💾 과목 및 이번주 강의 정보가 assignment.txt 파일에 저장되었습니다")
            if all_lectures:
                logger.info(f"📚 총 {len(all_lectures)}개 항목 수집 완료!")
            else:
                logger.warning("⚠️ 과목 정보를 찾을 수 없습니다")
                
        except Exception as e:
            logger.error(f"❌ 파일 저장 실패: {e}")
            
    except Exception as e:
        logger.error(f"❌ 이번주 강의 정보 수집 실패: {e}")
    
    # 리스트를 딕셔너리로 변환하여 반환
    return {
        "lectures": all_lectures,
        "count": len(all_lectures),
        "success": True,
        "message": f"총 {len(all_lectures)}개 강의 정보 수집 완료"
    }

def main():
    """메인 함수 (9887 빠른 실행 포함)"""
    print("🚀 완벽한 혼합 버전 자동화 스크립트")
    print("=" * 60)
    print("💡 기존 코드의 검증된 과목 순차 처리 + 픽스드 버전의 향상된 요소 추출")
    print("⚡ 9887 입력 시 자동 로그인 설정")
    print()
    
    # 대학교 입력
    university_input = input("대학교 (예: 연세대학교) 또는 9887: ").strip()
    
    if university_input == "9887":
        print("🚀 개발자 모드: 연세대학교 자동 설정!")
        university = "연세대학교"
        username = "2024248012"
        password = "cjm9887@"
        student_id = "2024248012"
        print(f"   학번: {username}")
        print(f"   비밀번호: {password}")
    else:
        university = university_input
        username = input("학번: ").strip()
        password = input("비밀번호: ").strip()
        student_id = username
    
    print()
    print("🔧 자동화 테스트 시작...")
    print("=" * 60)
    
    # Selenium 직접 테스트
    logger.info("🚀 메인 자동화 테스트 시작")
    logger.info(f"   대학: {university}")
    logger.info(f"   사용자: {username}")
    logger.info(f"   학생ID: {student_id}")
    
    success = test_direct_selenium(university, username, password, student_id)
    
    print("=" * 60)
    if success:
        if isinstance(success, list) and len(success) > 0:
            print(f"✅ 자동화 성공! {len(success)}개 과제 발견")
            for i, assignment in enumerate(success, 1):
                print(f"   {i}. {assignment.get('course', '')}: {assignment.get('activity', '')}")
        else:
            print("⚠️ 자동화 완료되었지만 과제가 없습니다.")
        print("✅ 테스트 완료! assignment.txt 파일을 확인하세요.")
    else:
        print("❌ 자동화 실패!")
    print("=" * 60)

if __name__ == "__main__":
    main()
