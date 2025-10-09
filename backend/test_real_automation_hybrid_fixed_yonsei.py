"""
LearnUs 연세 자동화 시스템 - Chrome 드라이버 문제 해결 버전
런어스연세 사이트 + 하이브리드 로직 + DevToolsActivePort 오류 해결
"""

import os
import sys
import time
import json
import logging
import requests
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
import firebase_admin
from firebase_admin import credentials, firestore

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

# Firebase 초기화
try:
    if not firebase_admin._apps:
        cred = credentials.Certificate('e_service_account.json')
        firebase_admin.initialize_app(cred)
    db = firestore.client()
    logger.info("Firebase Admin SDK 초기화 완료 (서비스 계정 키)")
    logger.info("Firebase Firestore 클라이언트 초기화 완료")
except Exception as e:
    logger.error(f"Firebase 초기화 실패: {e}")

def get_all_active_users():
    """Firebase에서 활성화된 사용자 정보 조회"""
    try:
        users_ref = db.collection('users')
        docs = users_ref.where('isActive', '==', True).stream()
        
        active_users = []
        for doc in docs:
            user_data = doc.to_dict()
            user_data['uid'] = doc.id
            active_users.append(user_data)
        
        logger.info(f"활성화된 LearnUs 인증 정보 {len(active_users)}개 조회 완료")
        return active_users
        
    except Exception as e:
        logger.error(f"Firebase 사용자 조회 실패: {e}")
        return []

def setup_driver():
    """Chrome 드라이버 설정 (Cloud Run 환경 최적화) - DevToolsActivePort 오류 해결"""
    try:
        logger.info("Chrome 드라이버 설정 중...")
        
        chrome_options = Options()
        
        # 🔥 DevToolsActivePort 오류 해결을 위한 핵심 옵션들
        chrome_options.add_argument("--no-sandbox")  # 필수: 샌드박스 비활성화
        chrome_options.add_argument("--disable-dev-shm-usage")  # 필수: 공유 메모리 비활성화
        chrome_options.add_argument("--single-process")  # 필수: 단일 프로세스 모드
        chrome_options.add_argument("--headless")  # 필수: 헤드리스 모드
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-plugins")
        chrome_options.add_argument("--disable-images")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--disable-features=VizDisplayCompositor")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        chrome_options.add_argument("--log-level=3")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        
        # 🔥 DevToolsActivePort 오류 해결을 위한 핵심 옵션들
        chrome_options.add_argument("--remote-debugging-port=0")  # 🔥 핵심: 디버깅 포트 비활성화
        chrome_options.add_argument("--disable-dev-tools")  # 🔥 핵심: DevTools 완전 비활성화
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
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
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
        
        # 🔥 추가 DevToolsActivePort 오류 해결 옵션들
        chrome_options.add_argument("--disable-setuid-sandbox")
        chrome_options.add_argument("--disable-accelerated-2d-canvas")
        chrome_options.add_argument("--disable-accelerated-jpeg-decoding")
        chrome_options.add_argument("--disable-accelerated-mjpeg-decode")
        chrome_options.add_argument("--disable-accelerated-video-decode")
        chrome_options.add_argument("--disable-gpu-memory-buffer-video-frames")
        chrome_options.add_argument("--disable-zero-copy")
        chrome_options.add_argument("--disable-gpu-sandbox")
        chrome_options.add_argument("--disable-software-rasterizer")
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
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
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
        driver = webdriver.Chrome(options=chrome_options)
        driver.set_page_load_timeout(30)
        driver.implicitly_wait(10)
        
        # 자동화 감지 방지
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        logger.info("Chrome 드라이버 설정 완료")
        return driver
        
    except Exception as e:
        logger.error(f"Chrome 드라이버 설정 실패: {e}")
        return None

def login_to_learnus_yonsei(driver, username, password):
    """런어스연세 로그인 (하이브리드 로직)"""
    try:
        logger.info(f"런어스연세 로그인 시도: {username}")
        
        # 런어스연세 메인 페이지로 이동
        driver.get("https://ys.learnus.org/")
        time.sleep(3)
        
        logger.info(f"현재 URL: {driver.current_url}")
        
        # 로그인 버튼 찾기 (하이브리드 로직)
        login_button = None
        login_selectors = [
            "a[href*='login']",
            "button[class*='login']",
            "input[value*='로그인']",
            "a[class*='login']",
            "button[onclick*='login']",
            "a[onclick*='login']"
        ]
        
        logger.info("로그인 버튼 찾는 중...")
        for selector in login_selectors:
            try:
                login_button = driver.find_element(By.CSS_SELECTOR, selector)
                logger.info(f"로그인 버튼 발견: {selector}")
                break
            except:
                continue
        
        if login_button:
            logger.info("로그인 버튼 클릭...")
            login_button.click()
            time.sleep(2)
            logger.info(f"클릭 후 URL: {driver.current_url}")
        else:
            logger.info("로그인 버튼을 찾을 수 없음, 직접 로그인 페이지 접속")
            driver.get("https://ys.learnus.org/passni/sso/spLogin2.php")
            time.sleep(2)
        
        # 사용자명 필드 찾기
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
        
        logger.info("사용자명 필드 찾는 중...")
        for selector in username_selectors:
            try:
                username_field = driver.find_element(By.CSS_SELECTOR, selector)
                logger.info(f"사용자명 필드 발견: {selector}")
                break
            except:
                continue
        
        if not username_field:
            logger.error("사용자명 필드를 찾을 수 없습니다.")
            return False
        
        # 비밀번호 필드 찾기
        password_field = None
        password_selectors = [
            "input[id='password']",
            "input[name='password']",
            "input[id='passwd']",
            "input[name='passwd']",
            "input[type='password']",
            "input[placeholder*='비밀번호']",
            "input[placeholder*='패스워드']"
        ]
        
        logger.info("비밀번호 필드 찾는 중...")
        for selector in password_selectors:
            try:
                password_field = driver.find_element(By.CSS_SELECTOR, selector)
                logger.info(f"비밀번호 필드 발견: {selector}")
                break
            except:
                continue
        
        if not password_field:
            logger.error("비밀번호 필드를 찾을 수 없습니다.")
            return False
        
        # 로그인 정보 입력
        logger.info("로그인 정보 입력 중...")
        username_field.clear()
        username_field.send_keys(username)
        password_field.clear()
        password_field.send_keys(password)
        
        # 로그인 버튼 클릭
        submit_button = None
        submit_selectors = [
            "input[type='submit']",
            "button[type='submit']",
            "button[class*='login']",
            "input[value*='로그인']",
            "button[onclick*='login']"
        ]
        
        for selector in submit_selectors:
            try:
                submit_button = driver.find_element(By.CSS_SELECTOR, selector)
                logger.info(f"로그인 버튼 발견: {selector}")
                break
            except:
                continue
        
        if submit_button:
            logger.info("로그인 버튼 클릭...")
            submit_button.click()
            time.sleep(3)
        else:
            logger.info("Enter 키로 로그인 시도...")
            password_field.send_keys("\n")
            time.sleep(3)
        
        # 로그인 성공 확인
        logger.info(f"로그인 후 URL: {driver.current_url}")
        
        # 로그인 성공 여부 확인
        if "login" not in driver.current_url.lower() and "ys.learnus.org" in driver.current_url:
            logger.info("런어스연세 로그인 성공")
            return True
        else:
            logger.error("런어스연세 로그인 실패")
            return False
        
    except Exception as e:
        logger.error(f"런어스연세 로그인 실패: {e}")
        return False

def extract_assignments_hybrid(driver):
    """과제 정보 추출 (하이브리드 로직)"""
    try:
        logger.info("과제 정보 추출 시작 (하이브리드 로직)")
        
        # 과제 페이지로 이동
        driver.get("https://ys.learnus.org/")
        time.sleep(3)
        
        assignments = []
        
        # 과제 관련 링크 찾기
        assignment_links = []
        link_selectors = [
            "a[href*='assignment']",
            "a[href*='과제']",
            "a[href*='task']",
            "a[class*='assignment']",
            "a[class*='과제']"
        ]
        
        for selector in link_selectors:
            try:
                links = driver.find_elements(By.CSS_SELECTOR, selector)
                assignment_links.extend(links)
            except:
                continue
        
        logger.info(f"과제 관련 링크 {len(assignment_links)}개 발견")
        
        # 각 링크에서 과제 정보 추출
        for link in assignment_links[:5]:  # 최대 5개만 처리
            try:
                link_text = link.text.strip()
                if link_text:
                    assignments.append({
                        "course": "런어스연세",
                        "activity": link_text,
                        "status": "확인 필요",
                        "extracted_at": datetime.now().isoformat()
                    })
            except:
                continue
        
        # 기본 과제 정보 추가 (하이브리드 로직)
        if not assignments:
            assignments.append({
                "course": "런어스연세",
                "activity": "이번주 과제 확인",
                "status": "로그인 완료",
                "extracted_at": datetime.now().isoformat()
            })
        
        logger.info(f"과제 정보 추출 완료: {len(assignments)}개")
        return assignments
        
    except Exception as e:
        logger.error(f"과제 정보 추출 실패: {e}")
        return []

def save_assignments_to_file(assignments):
    """과제 정보를 파일에 저장"""
    try:
        with open("assignment.txt", "w", encoding="utf-8") as f:
            f.write("=== LearnUs 연세 과제 정보 업데이트 ===\n")
            f.write(f"업데이트 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            if assignments:
                f.write("과제 목록:\n")
                for assignment in assignments:
                    f.write(f"  • {assignment['course']}: {assignment['activity']} - {assignment['status']}\n")
            else:
                f.write("이번주 과제가 없습니다.\n")
        
        logger.info("assignment.txt 파일 업데이트 완료")
        
    except Exception as e:
        logger.error(f"파일 저장 실패: {e}")

def run_automation_for_user(username, password, university, student_id):
    """사용자별 자동화 실행 (런어스연세 + 하이브리드 로직)"""
    driver = None
    try:
        logger.info(f"사용자 {username} 자동화 시작...")
        logger.info(f"대학교: {university}")
        logger.info(f"학번: {student_id}")
        
        # Chrome 드라이버 설정
        driver = setup_driver()
        if not driver:
            logger.error("Chrome 드라이버 설정 실패")
            return []
        
        # 런어스연세 로그인
        if not login_to_learnus_yonsei(driver, username, password):
            logger.error("런어스연세 로그인 실패")
            return []
        
        # 과제 정보 추출 (하이브리드 로직)
        assignments = extract_assignments_hybrid(driver)
        
        # 파일에 저장
        save_assignments_to_file(assignments)
        
        logger.info(f"사용자 {username} 자동화 완료: {len(assignments)}개 과제")
        return assignments
        
    except Exception as e:
        logger.error(f"사용자 {username} 자동화 실패: {e}")
        return []
        
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass

def main():
    """메인 실행 함수"""
    try:
        logger.info("LearnUs 연세 자동화 시스템 시작")
        
        # 활성화된 사용자 조회
        active_users = get_all_active_users()
        
        if not active_users:
            logger.warning("활성화된 사용자가 없습니다.")
            return
        
        logger.info(f"활성화된 사용자 {len(active_users)}명 발견")
        
        # 모든 사용자에 대해 자동화 실행
        all_assignments = []
        for user in active_users:
            username = user.get('username', '')
            password = user.get('password', '')
            university = user.get('university', '')
            student_id = user.get('studentId', '')
            
            if username and password:
                assignments = run_automation_for_user(username, password, university, student_id)
                all_assignments.extend(assignments)
        
        logger.info(f"전체 자동화 완료: {len(all_assignments)}개 과제")
        
    except Exception as e:
        logger.error(f"자동화 실행 실패: {e}")

if __name__ == "__main__":
    main()











