#!/usr/bin/env python3
"""
수동 로그인 테스트 (브라우저를 열어서 직접 확인)
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

def test_manual_login():
    """수동 로그인 테스트 (브라우저를 열어서 직접 확인)"""
    driver = None
    try:
        logger.info("=" * 60)
        logger.info("🔍 수동 로그인 테스트 시작")
        logger.info("브라우저를 열어서 직접 로그인 과정을 확인합니다")
        logger.info("=" * 60)
        
        # Selenium import
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.chrome.service import Service
        from webdriver_manager.chrome import ChromeDriverManager
        
        # Chrome 옵션 (브라우저를 보이게 설정)
        chrome_options = webdriver.ChromeOptions()
        # chrome_options.add_argument("--headless")  # 헤드리스 모드 제거
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
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
        with open('debug_manual_page.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        logger.info("💾 페이지 소스 저장: debug_manual_page.html")
        
        # 연세포털 로그인 버튼 찾기
        logger.info("🔍 연세포털 로그인 버튼 찾는 중...")
        try:
            login_button = driver.find_element(By.CSS_SELECTOR, "a.btn.btn-sso")
            logger.info("✅ 연세포털 로그인 버튼 발견")
            
            # 버튼 클릭
            logger.info("🖱️ 로그인 버튼 클릭...")
            login_button.click()
            time.sleep(5)
            
            logger.info(f"📍 클릭 후 URL: {driver.current_url}")
            logger.info(f"📄 클릭 후 페이지 제목: {driver.title}")
            
            # 로그인 후 페이지 소스 저장
            with open('debug_manual_login_page.html', 'w', encoding='utf-8') as f:
                f.write(driver.page_source)
            logger.info("💾 로그인 페이지 소스 저장: debug_manual_login_page.html")
            
            logger.info("=" * 60)
            logger.info("🔍 수동 확인이 필요합니다!")
            logger.info("브라우저에서 로그인 과정을 직접 확인해주세요.")
            logger.info("로그인 후 LearnUs 메인 페이지로 돌아오면 Enter를 눌러주세요.")
            logger.info("=" * 60)
            
            # 사용자 입력 대기
            input("로그인 완료 후 Enter를 눌러주세요...")
            
            logger.info(f"📍 최종 URL: {driver.current_url}")
            logger.info(f"📄 최종 페이지 제목: {driver.title}")
            
            # 최종 페이지 소스 저장
            with open('debug_manual_final_page.html', 'w', encoding='utf-8') as f:
                f.write(driver.page_source)
            logger.info("💾 최종 페이지 소스 저장: debug_manual_final_page.html")
            
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
                        for i, element in enumerate(elements[:5]):  # 처음 5개만
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
                
        except Exception as e:
            logger.error(f"❌ 로그인 버튼 찾기 실패: {e}")
            return []
            
    except Exception as e:
        logger.error(f"❌ 자동화 오류: {e}")
        return []
    finally:
        if driver:
            logger.info("🔚 Chrome 드라이버 종료")
            driver.quit()

def main():
    """메인 함수"""
    print("수동 로그인 테스트")
    print("=" * 30)
    print("브라우저를 열어서 직접 로그인 과정을 확인합니다")
    print()
    
    result = test_manual_login()
    
    print("=" * 30)
    if result:
        print(f"✅ 테스트 성공! {len(result)}개 과제/과목 발견")
        for i, item in enumerate(result, 1):
            print(f"   {i}. {item}")
    else:
        print("❌ 테스트 실패!")
    print("=" * 30)

if __name__ == "__main__":
    main()










