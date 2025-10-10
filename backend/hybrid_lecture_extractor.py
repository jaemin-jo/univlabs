#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import logging
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import requests

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('hybrid_lecture_extractor.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class HybridLectureExtractor:
    def __init__(self):
        self.driver = None
        self.session = requests.Session()
        
    def setup_driver(self):
        """Chrome 드라이버 설정 (로그인용)"""
        try:
            chrome_options = Options()
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.driver.set_page_load_timeout(30)
            self.driver.implicitly_wait(10)
            
            logger.info("✅ Chrome 드라이버 초기화 완료")
            return True
            
        except Exception as e:
            logger.error(f"❌ Chrome 드라이버 초기화 실패: {e}")
            return False
    
    def setup_session_from_selenium(self):
        """Selenium에서 쿠키를 가져와서 requests 세션에 적용"""
        try:
            # Selenium에서 쿠키 가져오기
            selenium_cookies = self.driver.get_cookies()
            
            # requests 세션에 쿠키 적용
            for cookie in selenium_cookies:
                self.session.cookies.set(cookie['name'], cookie['value'])
            
            # User-Agent 설정
            self.session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'ko-KR,ko;q=0.8,en-US;q=0.5,en;q=0.3',
                'Connection': 'keep-alive',
            })
            
            logger.info("✅ Selenium 쿠키를 requests 세션에 적용 완료")
            return True
            
        except Exception as e:
            logger.error(f"❌ 쿠키 적용 실패: {e}")
            return False
    
    def login_with_selenium(self, username, password):
        """Selenium으로 로그인"""
        try:
            logger.info("🔐 Selenium으로 로그인 시도...")
            
            # LearnUs 메인 페이지 접속
            self.driver.get("https://ys.learnus.org/")
            time.sleep(2)
            
            # 로그인 버튼 클릭
            try:
                login_button = self.driver.find_element(By.XPATH, "//a[contains(text(), '로그인') or contains(@href, 'login')]")
                login_button.click()
                time.sleep(2)
            except:
                logger.info("로그인 버튼을 찾을 수 없음, 직접 로그인 페이지 접속")
                self.driver.get("https://ys.learnus.org/login/index.php")
                time.sleep(2)
            
            # 로그인 폼 입력
            username_field = self.driver.find_element(By.NAME, "username")
            password_field = self.driver.find_element(By.NAME, "password")
            
            username_field.clear()
            username_field.send_keys(username)
            password_field.clear()
            password_field.send_keys(password)
            
            # 로그인 버튼 클릭
            login_submit = self.driver.find_element(By.XPATH, "//input[@type='submit' or @value='로그인']")
            login_submit.click()
            time.sleep(3)
            
            # 로그인 성공 확인
            current_url = self.driver.current_url
            if "login" not in current_url and "dashboard" in current_url or "main" in current_url:
                logger.info("✅ Selenium 로그인 성공!")
                return True
            else:
                logger.warning("⚠️ Selenium 로그인 실패")
                return False
                
        except Exception as e:
            logger.error(f"❌ Selenium 로그인 오류: {e}")
            return False
    
    def get_course_list_http(self):
        """HTTP Request로 과목 목록 가져오기"""
        try:
            logger.info("📚 HTTP Request로 과목 목록 수집 중...")
            
            # 메인 페이지에서 과목 목록 가져오기
            main_url = "https://ys.learnus.org/"
            response = self.session.get(main_url)
            
            if response.status_code != 200:
                logger.error(f"메인 페이지 접속 실패: {response.status_code}")
                return []
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 과목 링크 찾기
            course_links = []
            for link in soup.find_all('a', href=True):
                href = link.get('href', '')
                if '/course/view.php?id=' in href:
                    course_name = link.get_text().strip()
                    if course_name and len(course_name) > 3:
                        course_links.append({
                            'name': course_name,
                            'url': href if href.startswith('http') else f"https://ys.learnus.org{href}",
                        })
            
            logger.info(f"📚 {len(course_links)}개 과목 발견")
            return course_links
            
        except Exception as e:
            logger.error(f"❌ 과목 목록 수집 오류: {e}")
            return []
    
    def get_course_content_http(self, course_url):
        """HTTP Request로 과목 페이지 내용 가져오기"""
        try:
            response = self.session.get(course_url)
            
            if response.status_code != 200:
                logger.warning(f"과목 페이지 접속 실패: {response.status_code}")
                return None
            
            return BeautifulSoup(response.text, 'html.parser')
            
        except Exception as e:
            logger.error(f"❌ 과목 페이지 로드 오류: {e}")
            return None
    
    def find_this_week_section(self, soup, course_name):
        """이번주 강의 섹션 찾기"""
        try:
            sections = soup.find_all('li', class_='section main')
            logger.info(f"   {course_name}: {len(sections)}개 섹션 발견")
            
            for idx, section in enumerate(sections):
                try:
                    section_title = section.find('h3') or section.find('div', class_='section-title')
                    if section_title:
                        title_text = section_title.get_text().strip().lower()
                        logger.info(f"   섹션 {idx+1}: {title_text}")
                        
                        if any(keyword in title_text for keyword in [
                            "이번주 강의", "이번주", "current week", "week", "주차", "이번 주"
                        ]):
                            if "개요" not in title_text and "overview" not in title_text:
                                logger.info(f"   ✅ '이번주 강의' 섹션 발견: {title_text}")
                                return section
                    
                    section_text = section.get_text().lower()
                    if any(keyword in section_text for keyword in [
                        "이번주 강의", "이번주", "current week", "week", "주차"
                    ]):
                        if "개요" not in section_text and "overview" not in section_text:
                            logger.info(f"   ✅ '이번주 강의' 섹션 발견 (텍스트)")
                            return section
                            
                except Exception as e:
                    logger.debug(f"   섹션 {idx+1} 분석 실패: {e}")
                    continue
            
            if len(sections) > 1:
                logger.info(f"   🔍 키워드로 찾지 못함, 두 번째 섹션 사용")
                return sections[1]
            
            if sections:
                logger.info(f"   🔍 첫 번째 섹션 사용")
                return sections[0]
            
            return None
            
        except Exception as e:
            logger.error(f"❌ 섹션 찾기 오류: {e}")
            return None
    
    def extract_activities_from_section(self, section, course_name):
        """섹션에서 활동 추출"""
        activities = []
        
        try:
            links = section.find_all('a', href=True)
            logger.info(f"   {len(links)}개 링크 발견")
            
            for link in links:
                try:
                    activity_name = link.get_text().strip()
                    activity_url = link.get('href', '')
                    
                    if not activity_name or not activity_url:
                        continue
                    
                    if any(skip in activity_name.lower() for skip in [
                        "더보기", "more", "자세히", "detail", "보기", "view"
                    ]):
                        continue
                    
                    if not activity_url.startswith('http'):
                        activity_url = f"https://ys.learnus.org{activity_url}"
                    
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
                    
                    activity_info = {
                        "course": course_name,
                        "activity": activity_name,
                        "type": activity_type,
                        "url": activity_url
                    }
                    
                    activities.append(activity_info)
                    logger.info(f"     ✅ {activity_name} ({activity_type})")
                    
                except Exception as e:
                    logger.debug(f"     링크 처리 실패: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"   활동 추출 실패: {e}")
        
        return activities
    
    def extract_all_lectures(self):
        """모든 과목의 이번주 강의 추출 (하이브리드 방식)"""
        try:
            logger.info("🔍 하이브리드 방식으로 이번주 강의 정보 수집 시작...")
            
            # Selenium에서 쿠키를 requests 세션에 적용
            if not self.setup_session_from_selenium():
                return []
            
            # HTTP Request로 과목 목록 가져오기
            courses = self.get_course_list_http()
            if not courses:
                logger.warning("과목 목록을 가져올 수 없습니다")
                return []
            
            all_lectures = []
            
            for i, course in enumerate(courses[:5]):  # 처음 5개 과목만 테스트
                try:
                    course_name = course['name']
                    course_url = course['url']
                    
                    logger.info(f"\n📖 과목 {i+1}: {course_name}")
                    
                    # HTTP Request로 과목 페이지 가져오기
                    soup = self.get_course_content_http(course_url)
                    if not soup:
                        logger.warning(f"   ⚠️ {course_name} 페이지 로드 실패")
                        continue
                    
                    # 이번주 강의 섹션 찾기
                    this_week_section = self.find_this_week_section(soup, course_name)
                    
                    if this_week_section:
                        course_activities = self.extract_activities_from_section(this_week_section, course_name)
                        
                        if course_activities:
                            all_lectures.extend(course_activities)
                            logger.info(f"   📚 {len(course_activities)}개 활동 발견")
                        else:
                            logger.info(f"   📭 활동 없음")
                    else:
                        logger.info(f"   📭 '이번주 강의' 섹션 없음")
                    
                    time.sleep(1)  # 요청 간격 조절
                        
                except Exception as e:
                    logger.warning(f"   ❌ 과목 {i+1} 처리 실패: {e}")
                    continue
            
            return all_lectures
            
        except Exception as e:
            logger.error(f"❌ 강의 추출 오류: {e}")
            return []
    
    def save_to_file(self, lectures):
        """결과를 파일로 저장"""
        try:
            with open('assignment.txt', 'w', encoding='utf-8') as f:
                f.write("📚 이번주 강의 활동 목록 (하이브리드 방식)\n")
                f.write("=" * 60 + "\n\n")
                f.write(f"수집 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"총 수집된 활동 수: {len(lectures)}개\n\n")
                
                if lectures:
                    course_groups = {}
                    for lecture in lectures:
                        course = lecture['course']
                        if course not in course_groups:
                            course_groups[course] = []
                        course_groups[course].append(lecture)
                    
                    for course, activities in course_groups.items():
                        f.write(f"📖 {course}\n")
                        f.write("-" * 40 + "\n")
                        
                        for activity in activities:
                            f.write(f"  • {activity['activity']} ({activity['type']})\n")
                            f.write(f"    URL: {activity['url']}\n\n")
                        
                        f.write("\n")
                else:
                    f.write("❌ 수집된 이번주 강의 활동이 없습니다.\n")
                
            logger.info("💾 assignment.txt 파일에 저장 완료")
            return True
            
        except Exception as e:
            logger.error(f"❌ 파일 저장 실패: {e}")
            return False
    
    def run(self, username=None, password=None):
        """메인 실행 함수"""
        print("🚀 하이브리드 방식 이번주 강의 추출기")
        print("=" * 60)
        print("💡 Selenium으로 로그인 → HTTP Request로 데이터 수집")
        
        # 로그인 정보 입력
        if not username or not password:
            print("📝 자동화 테스트를 위한 정보 입력")
            print("------------------------------")
            university_input = input("대학교 (예: 연세대학교) 또는 9887: ").strip()
            
            if university_input == "9887":
                username = "2024248012"
                password = "cjm9887@"
                print("🚀 개발자 모드: 연세대학교 자동 설정!")
                print(f"   학번: {username}")
                print(f"   비밀번호: {password}")
            else:
                username = input("아이디/학번: ").strip()
                password = input("비밀번호: ").strip()
        
        if not username or not password:
            print("❌ 로그인 정보가 누락되었습니다")
            return False
        
        if not self.setup_driver():
            return False
        
        try:
            # Selenium으로 로그인
            if not self.login_with_selenium(username, password):
                print("❌ 로그인 실패")
                return False
            
            # HTTP Request로 이번주 강의 정보 수집
            lectures = self.extract_all_lectures()
            
            # 결과 저장
            if self.save_to_file(lectures):
                print(f"\n✅ 총 {len(lectures)}개 이번주 강의 활동 수집 완료!")
                print("📄 assignment.txt 파일을 확인하세요.")
                print("⚡ 하이브리드 방식으로 안정적이고 빠르게 처리되었습니다!")
            else:
                print("\n❌ 파일 저장 실패")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 실행 오류: {e}")
            return False
        
        finally:
            try:
                self.driver.quit()
                logger.info("🔚 드라이버 종료")
            except:
                pass

def main():
    extractor = HybridLectureExtractor()
    extractor.run()

if __name__ == "__main__":
    main()

























