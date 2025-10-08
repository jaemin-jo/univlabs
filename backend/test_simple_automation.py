#!/usr/bin/env python3
"""
간단한 LearnUs 자동화 테스트 (Chrome 크래시 문제 해결)
"""

import sys
import os
import time
import logging
from datetime import datetime

# 현재 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_simple_learnus():
    """간단한 LearnUs 테스트 (크래시 방지)"""
    driver = None
    try:
        logger.info("=" * 60)
        logger.info("🚀 간단한 LearnUs 테스트 시작")
        logger.info("=" * 60)
        
        # Selenium import
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.chrome.service import Service
        from webdriver_manager.chrome import ChromeDriverManager
        
        # Chrome 옵션 (최소한으로 설정)
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--headless")  # 헤드리스 모드
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        # Chrome 드라이버 설정
        logger.info("🔧 Chrome 드라이버 설정 중...")
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        logger.info("✅ Chrome 드라이버 초기화 성공")
        
        # LearnUs 메인 페이지 접속
        logger.info("🌐 LearnUs 메인 페이지 접속...")
        driver.get("https://ys.learnus.org/")
        time.sleep(3)
        
        logger.info(f"📍 현재 URL: {driver.current_url}")
        logger.info(f"📄 페이지 제목: {driver.title}")
        
        # 페이지 소스 저장
        with open('debug_simple_page.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        logger.info("💾 페이지 소스 저장: debug_simple_page.html")
        
        # 연세포털 로그인 버튼 찾기
        logger.info("🔍 연세포털 로그인 버튼 찾는 중...")
        try:
            login_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "a.btn.btn-sso"))
            )
            logger.info("✅ 연세포털 로그인 버튼 발견")
            
            # 버튼 클릭
            logger.info("🖱️ 로그인 버튼 클릭...")
            login_button.click()
            time.sleep(3)
            
            logger.info(f"📍 클릭 후 URL: {driver.current_url}")
            
            # 로그인 폼 찾기 (다양한 선택자 시도)
            logger.info("🔍 로그인 폼 찾는 중...")
            username_field = None
            password_field = None
            
            # 사용자명 필드 찾기
            username_selectors = ["input[id='loginId']", "input[name='loginId']", "input[type='text']"]
            for selector in username_selectors:
                try:
                    username_field = driver.find_element(By.CSS_SELECTOR, selector)
                    logger.info(f"✅ 사용자명 필드 발견: {selector}")
                    break
                except:
                    continue
            
            # 비밀번호 필드 찾기
            password_selectors = ["input[id='loginPw']", "input[name='loginPw']", "input[type='password']"]
            for selector in password_selectors:
                try:
                    password_field = driver.find_element(By.CSS_SELECTOR, selector)
                    logger.info(f"✅ 비밀번호 필드 발견: {selector}")
                    break
                except:
                    continue
            
            if not username_field or not password_field:
                logger.error("❌ 로그인 폼을 찾을 수 없습니다")
                return []
            
            logger.info("✅ 로그인 폼 발견")
            
            # 로그인 정보 입력
            logger.info("📝 로그인 정보 입력 중...")
            username_field.clear()
            username_field.send_keys("2024248012")
            
            password_field.clear()
            password_field.send_keys("cjm9887@")
            
            logger.info("✅ 로그인 정보 입력 완료")
            
            # 로그인 버튼 클릭
            logger.info("🖱️ 로그인 버튼 클릭...")
            submit_button = driver.find_element(By.CSS_SELECTOR, "input[type='submit']")
            submit_button.click()
            
            # 로그인 완료 대기
            logger.info("⏳ 로그인 완료 대기 중...")
            time.sleep(5)
            
            logger.info(f"📍 로그인 후 URL: {driver.current_url}")
            logger.info(f"📄 로그인 후 페이지 제목: {driver.title}")
            
            # 로그인 성공 확인
            if "learnus.org" in driver.current_url and "login" not in driver.current_url.lower():
                logger.info("✅ 로그인 성공!")
                
                # 페이지 소스 저장
                with open('debug_learnus_logged_in.html', 'w', encoding='utf-8') as f:
                    f.write(driver.page_source)
                logger.info("💾 로그인 후 페이지 소스 저장: debug_learnus_logged_in.html")
                
                # 과제 정보 찾기
                logger.info("🔍 과제 정보 찾는 중...")
                
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
                            logger.info(f"✅ {selector}로 {len(elements)}개 요소 발견")
                            for i, element in enumerate(elements[:3]):  # 처음 3개만
                                text = element.text.strip()
                                if text:
                                    assignments_found.append(text)
                                    logger.info(f"   {i+1}. {text}")
                        else:
                            logger.info(f"❌ {selector}로 요소를 찾지 못함")
                    except Exception as e:
                        logger.debug(f"선택자 {selector} 실패: {e}")
                
                if assignments_found:
                    logger.info(f"🎉 총 {len(assignments_found)}개 과제/과목 발견!")
                    return assignments_found
                else:
                    logger.warning("⚠️ 과제/과목을 찾지 못했습니다.")
                    return []
                        
            else:
                    logger.error("❌ 로그인 실패")
                    return []
                    
            except Exception as e:
                logger.error(f"❌ 로그인 폼 찾기 실패: {e}")
                return []
                
        except Exception as e:
            logger.error(f"❌ 로그인 버튼 찾기 실패: {e}")
            return []
            
    except Exception as e:
        logger.error(f"❌ 자동화 오류: {e}")
        return []
    finally:
        if driver:
            time.sleep(2)
            logger.info("🔚 Chrome 드라이버 종료")
            driver.quit()

def main():
    """메인 함수"""
    print("간단한 LearnUs 자동화 테스트")
    print("=" * 40)
    print("Chrome 크래시 문제 해결을 위한 간단한 테스트")
    print()
    
    result = test_simple_learnus()
    
    print("=" * 40)
    if result:
        print(f"✅ 테스트 성공! {len(result)}개 과제/과목 발견")
        for i, item in enumerate(result, 1):
            print(f"   {i}. {item}")
    else:
        print("❌ 테스트 실패!")
    print("=" * 40)

if __name__ == "__main__":
    main()
