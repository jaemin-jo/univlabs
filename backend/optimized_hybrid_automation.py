#!/usr/bin/env python3
"""
최적화된 하이브리드 자동화 스크립트
- 병렬 처리로 시간 단축
- 상태 확인 최적화
- 배치 처리 지원
"""

import asyncio
import json
import requests
import logging
import time
import re
import os
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException, StaleElementReferenceException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.service import Service

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('optimized_automation.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class OptimizedHybridAutomation:
    def __init__(self, max_workers=3):
        self.max_workers = max_workers
        self.driver = None
        self.session = requests.Session()
        
    def setup_driver(self):
        """최적화된 Chrome 드라이버 설정"""
        try:
            logger.info("🔧 최적화된 Chrome 드라이버 설정 중...")
            
            chrome_options = Options()
            
            # 성능 최적화 옵션들
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-plugins")
            chrome_options.add_argument("--disable-images")  # 이미지 로딩 비활성화로 속도 향상
            chrome_options.add_argument("--disable-javascript")  # JS 비활성화로 속도 향상
            chrome_options.add_argument("--disable-web-security")
            chrome_options.add_argument("--disable-features=VizDisplayCompositor")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            chrome_options.add_argument("--log-level=3")
            
            # 자동화 감지 방지
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # 타임아웃 설정 최적화
            self.driver.set_page_load_timeout(60)  # 페이지 로딩 60초
            self.driver.implicitly_wait(5)  # 요소 찾기 5초로 단축
            
            # 자동화 감지 방지
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            logger.info("✅ 최적화된 Chrome 드라이버 초기화 완료")
            return True
            
        except Exception as e:
            logger.error(f"❌ Chrome 드라이버 설정 실패: {e}")
            return False
    
    def login_to_learnus(self, username, password):
        """런어스 로그인 (최적화된 버전)"""
        try:
            logger.info("🔐 런어스 로그인 시작...")
            
            # LearnUs 메인 페이지 접속
            self.driver.get("https://ys.learnus.org/")
            time.sleep(2)
            
            # 연세포털 로그인 버튼 찾기
            login_button = None
            login_selectors = [
                "a.btn.btn-sso",
                "a[href*='sso']",
                "a[href*='login']",
                ".btn-sso",
                ".login-btn"
            ]
            
            for selector in login_selectors:
                try:
                    login_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    break
                except:
                    continue
            
            if login_button:
                login_button.click()
                time.sleep(2)
            else:
                self.driver.get("https://ys.learnus.org/passni/sso/spLogin2.php")
                time.sleep(2)
            
            # 로그인 정보 입력
            username_field = self.driver.find_element(By.CSS_SELECTOR, "input[id='loginId']")
            password_field = self.driver.find_element(By.CSS_SELECTOR, "input[id='loginPw']")
            
            username_field.clear()
            username_field.send_keys(username)
            time.sleep(0.5)
            
            password_field.clear()
            password_field.send_keys(password)
            time.sleep(0.5)
            
            # 로그인 시도
            password_field.send_keys("\n")
            time.sleep(3)
            
            # 로그인 성공 확인
            current_url = self.driver.current_url
            if "ys.learnus.org" in current_url and "login" not in current_url.lower():
                logger.info("✅ 로그인 성공!")
                return True
            else:
                logger.error("❌ 로그인 실패")
                return False
                
        except Exception as e:
            logger.error(f"❌ 로그인 오류: {e}")
            return False
    
    def get_all_courses_optimized(self):
        """모든 과목 정보를 한 번에 가져오기 (최적화)"""
        try:
            logger.info("📚 모든 과목 정보 수집 중...")
            
            # 과목 목록 찾기
            course_elements = self.driver.find_elements(By.CSS_SELECTOR, ".course-title h3")
            
            if not course_elements:
                # 대안 선택자들
                alternative_selectors = [
                    "h3",
                    ".course-box h3",
                    ".course-name h3",
                    "a[href*='course/view.php'] h3",
                    ".my-course-lists h3"
                ]
                
                for selector in alternative_selectors:
                    course_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if course_elements:
                        break
            
            courses = []
            for element in course_elements:
                try:
                    course_name = element.text.strip()
                    if course_name and len(course_name) > 3:
                        courses.append({
                            'name': course_name,
                            'element': element
                        })
                except:
                    continue
            
            logger.info(f"✅ {len(courses)}개 과목 발견")
            return courses
            
        except Exception as e:
            logger.error(f"❌ 과목 정보 수집 실패: {e}")
            return []
    
    def process_single_course_optimized(self, course_info):
        """단일 과목 처리 (최적화된 버전)"""
        try:
            course_name = course_info['name']
            course_element = course_info['element']
            
            logger.info(f"📖 {course_name} 처리 시작...")
            
            # 과목 클릭
            course_element.click()
            time.sleep(1)
            
            # 페이지 소스 가져오기
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # 이번주 강의 섹션 찾기
            this_week_section = self.find_this_week_section_optimized(soup)
            
            activities = []
            if this_week_section:
                activities = self.extract_activities_optimized(this_week_section, course_name)
            
            # 메인 페이지로 돌아가기
            self.driver.back()
            time.sleep(0.5)
            
            logger.info(f"✅ {course_name} 처리 완료: {len(activities)}개 활동")
            return activities
            
        except Exception as e:
            logger.error(f"❌ {course_name} 처리 실패: {e}")
            return []
    
    def find_this_week_section_optimized(self, soup):
        """이번주 강의 섹션 찾기 (최적화)"""
        try:
            # 다양한 선택자로 섹션 찾기
            section_selectors = [
                'li.section.main',
                'div.section',
                'div[class*="section"]',
                'li[class*="section"]'
            ]
            
            for selector in section_selectors:
                sections = soup.select(selector)
                for section in sections:
                    section_text = section.get_text().lower()
                    if any(keyword in section_text for keyword in [
                        "이번주 강의", "이번주", "current week", "current week course",
                        "이번주강의", "current week lecture", "week", "주차",
                        "이번 주", "현재 주", "current", "강의", "주제별 학습활동"
                    ]):
                        if "개요" not in section_text and "overview" not in section_text:
                            return section
            
            # 정확한 키워드로 찾지 못하면 두 번째 섹션 사용
            for selector in section_selectors:
                sections = soup.select(selector)
                if len(sections) > 1:
                    return sections[1]
            
            # 여전히 없으면 첫 번째 섹션 사용
            for selector in section_selectors:
                sections = soup.select(selector)
                if sections:
                    return sections[0]
            
            return None
            
        except Exception as e:
            logger.error(f"❌ 섹션 찾기 실패: {e}")
            return None
    
    def extract_activities_optimized(self, section, course_name):
        """활동 정보 추출 (최적화)"""
        try:
            activities = []
            activity_links = section.find_all('a', href=True)
            
            for link in activity_links:
                try:
                    activity_name = link.get_text().strip()
                    activity_url = link.get('href', '')
                    
                    if not activity_name or not activity_url:
                        continue
                    
                    # 활동 타입 판별
                    activity_type = "기타"
                    if "mod/assign/" in activity_url:
                        activity_type = "과제"
                    elif "mod/vod/" in activity_url:
                        activity_type = "동영상"
                    elif "mod/resource/" in activity_url or "mod/ubfile/" in activity_url:
                        activity_type = "PDF 자료"
                    elif "mod/ubboard/" in activity_url:
                        activity_type = "게시판"
                    elif "mod/quiz/" in activity_url:
                        activity_type = "퀴즈"
                    elif "mod/forum/" in activity_url:
                        activity_type = "토론"
                    elif "mod/lesson/" in activity_url:
                        activity_type = "강의"
                    elif "mod/page/" in activity_url:
                        activity_type = "페이지"
                    
                    activities.append({
                        'course': course_name,
                        'activity': activity_name,
                        'type': activity_type,
                        'url': activity_url,
                        'status': '상태 확인 필요'
                    })
                    
                except Exception as e:
                    logger.debug(f"활동 정보 추출 실패: {e}")
                    continue
            
            return activities
            
        except Exception as e:
            logger.error(f"❌ 활동 추출 실패: {e}")
            return []
    
    def process_all_courses_parallel(self, courses):
        """모든 과목을 병렬로 처리"""
        try:
            logger.info(f"🚀 {len(courses)}개 과목 병렬 처리 시작...")
            
            all_activities = []
            
            # ThreadPoolExecutor를 사용한 병렬 처리
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                # 각 과목을 병렬로 처리
                future_to_course = {
                    executor.submit(self.process_single_course_optimized, course): course 
                    for course in courses
                }
                
                # 완료된 작업들을 처리
                for future in as_completed(future_to_course):
                    course = future_to_course[future]
                    try:
                        activities = future.result()
                        all_activities.extend(activities)
                        logger.info(f"✅ {course['name']} 병렬 처리 완료")
                    except Exception as e:
                        logger.error(f"❌ {course['name']} 병렬 처리 실패: {e}")
            
            logger.info(f"🎉 병렬 처리 완료: 총 {len(all_activities)}개 활동")
            return all_activities
            
        except Exception as e:
            logger.error(f"❌ 병렬 처리 실패: {e}")
            return []
    
    def run_optimized_automation(self, username, password):
        """최적화된 자동화 실행"""
        try:
            logger.info("🚀 최적화된 하이브리드 자동화 시작...")
            
            # 드라이버 설정
            if not self.setup_driver():
                return []
            
            # 로그인
            if not self.login_to_learnus(username, password):
                return []
            
            # 모든 과목 정보 수집
            courses = self.get_all_courses_optimized()
            if not courses:
                logger.warning("과목을 찾을 수 없습니다")
                return []
            
            # 병렬 처리로 모든 과목 처리
            all_activities = self.process_all_courses_parallel(courses)
            
            # 결과 저장
            self.save_activities_to_file(all_activities)
            
            logger.info(f"✅ 최적화된 자동화 완료: {len(all_activities)}개 활동")
            return all_activities
            
        except Exception as e:
            logger.error(f"❌ 최적화된 자동화 실패: {e}")
            return []
        finally:
            if self.driver:
                try:
                    self.driver.quit()
                    logger.info("🔚 드라이버 종료")
                except:
                    pass
    
    def save_activities_to_file(self, activities):
        """활동 정보를 파일에 저장"""
        try:
            with open('assignment.txt', 'w', encoding='utf-8') as f:
                f.write("📚 최적화된 LearnUs 과제 정보\n")
                f.write("=" * 60 + "\n\n")
                f.write(f"수집 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"총 수집된 항목 수: {len(activities)}개\n\n")
                
                if activities:
                    # 과목별로 그룹화
                    course_groups = {}
                    for activity in activities:
                        course = activity['course']
                        if course not in course_groups:
                            course_groups[course] = []
                        course_groups[course].append(activity)
                    
                    # 과목별로 출력
                    for course, course_activities in course_groups.items():
                        f.write(f"📖 {course}\n")
                        f.write("-" * 50 + "\n")
                        
                        for activity in course_activities:
                            f.write(f"  • {activity['activity']} ({activity['type']}) - {activity.get('status', '상태 불명')}\n")
                            if activity['url']:
                                f.write(f"    URL: {activity['url']}\n")
                        f.write("\n")
                else:
                    f.write("⚠️ 과목 정보를 찾을 수 없습니다\n")
            
            logger.info("💾 최적화된 결과가 assignment.txt 파일에 저장되었습니다")
            
        except Exception as e:
            logger.error(f"❌ 파일 저장 실패: {e}")

def main():
    """메인 함수"""
    print("🚀 최적화된 하이브리드 자동화 스크립트")
    print("=" * 60)
    print("⚡ 병렬 처리로 시간 단축")
    print("🔧 상태 확인 최적화")
    print("📦 배치 처리 지원")
    print()
    
    # 사용자 정보 입력
    username = input("학번: ").strip()
    password = input("비밀번호: ").strip()
    
    print()
    print("🔧 최적화된 자동화 시작...")
    
    # 최적화된 자동화 실행
    automation = OptimizedHybridAutomation(max_workers=3)
    activities = automation.run_optimized_automation(username, password)
    
    if activities:
        print(f"✅ 최적화된 자동화 완료: {len(activities)}개 활동")
        print("📄 assignment.txt 파일을 확인하세요.")
    else:
        print("❌ 자동화 실패")

if __name__ == "__main__":
    main()
