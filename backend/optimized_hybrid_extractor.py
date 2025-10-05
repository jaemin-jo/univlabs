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
import json

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('optimized_hybrid_extractor.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class OptimizedHybridExtractor:
    def __init__(self):
        self.driver = None
        self.session = requests.Session()
        self.course_urls = []  # 과목 URL 목록 저장
        
    def setup_driver(self):
        """Chrome 드라이버 설정 (동적 작업용) - 기존 검증된 설정 사용"""
        try:
            logger.info("🔧 Chrome 드라이버 설정 중...")
            chrome_options = Options()
            
            # 기본 설정 (기존 검증된 설정)
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--disable-web-security")
            chrome_options.add_argument("--disable-features=VizDisplayCompositor")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            
            # 로그 레벨 설정
            chrome_options.add_argument("--log-level=3")
            chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # 추가 설정
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # 자동화 감지 방지
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            # 페이지 로드 타임아웃 설정
            self.driver.set_page_load_timeout(30)
            self.driver.implicitly_wait(10)
            
            logger.info("✅ Chrome 드라이버 초기화 완료 (동적 작업용)")
            return True
            
        except Exception as e:
            logger.error(f"❌ Chrome 드라이버 초기화 실패: {e}")
            return False
    
    def setup_http_session(self):
        """HTTP 세션 설정 (정적 데이터 추출용)"""
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
            
            logger.info("✅ HTTP 세션 설정 완료 (정적 데이터 추출용)")
            return True
            
        except Exception as e:
            logger.error(f"❌ HTTP 세션 설정 실패: {e}")
            return False
    
    def selenium_login(self, username, password):
        """Selenium으로 로그인 (동적 작업) - 기존 검증된 로직 사용"""
        try:
            logger.info("🔐 Selenium으로 로그인 시도...")
            
            # 1단계: LearnUs 메인 페이지 접속
            learnus_url = "https://ys.learnus.org/"
            portal_login_url = "https://ys.learnus.org/passni/sso/spLogin2.php"
            
            logger.info(f"🌐 LearnUs 메인 페이지 접속: {learnus_url}")
            self.driver.get(learnus_url)
            time.sleep(1.0)
            
            # 현재 URL과 페이지 제목 로깅
            current_url = self.driver.current_url
            page_title = self.driver.title
            logger.info(f"📍 현재 URL: {current_url}")
            logger.info(f"📄 페이지 제목: {page_title}")
            
            # 연세포털 로그인 버튼 찾기 및 클릭 (기존 검증된 로직)
            logger.info("🔍 연세포털 로그인 버튼 찾는 중...")
            
            # 1단계: CSS 선택자로 찾기
            portal_button_selectors = [
                "a.btn.btn-sso",  # 정확한 클래스 조합 (가장 빠름)
                "a[href*='spLogin2.php']",  # 부분 매칭 (빠름)
                "a[href*='passni/sso']",  # 중간 경로
                "a[href='https://ys.learnus.org/passni/sso/spLogin2.php']",  # 정확한 href
                "a[href*='portal']",
                "a[href*='login']",
                ".login-btn",
                ".portal-btn",
                "a[class*='btn'][class*='sso']"  # 클래스 부분 매칭
            ]
            
            portal_login_button = None
            for i, selector in enumerate(portal_button_selectors):
                try:
                    logger.info(f"   CSS 선택자 시도 중 ({i+1}/{len(portal_button_selectors)}): {selector}")
                    portal_login_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    logger.info(f"✅ 연세포털 로그인 버튼 발견: {selector}")
                    break
                except:
                    logger.debug(f"   실패: {selector}")
                    continue
            
            # 2단계: XPath로 찾기 (CSS 선택자가 실패한 경우)
            if not portal_login_button:
                logger.info("   CSS 선택자 실패, XPath로 시도 중...")
                xpath_selectors = [
                    "//a[@class='btn btn-sso']",
                    "//a[contains(@href, 'spLogin2.php')]",
                    "//a[contains(@href, 'passni/sso')]",
                    "//a[contains(text(), '연세포털 로그인')]",
                    "//a[contains(text(), '연세포털')]",
                    "//a[contains(@class, 'btn') and contains(@class, 'sso')]"
                ]
                
                for i, xpath in enumerate(xpath_selectors):
                    try:
                        logger.info(f"   XPath 시도 중 ({i+1}/{len(xpath_selectors)}): {xpath}")
                        portal_login_button = self.driver.find_element(By.XPATH, xpath)
                        logger.info(f"✅ 연세포털 로그인 버튼 발견 (XPath): {xpath}")
                        break
                    except:
                        logger.debug(f"   XPath 실패: {xpath}")
                        continue
            
            # 3단계: 모든 링크를 검사하여 텍스트로 찾기
            if not portal_login_button:
                logger.info("   XPath도 실패, 모든 링크 검사 중...")
                try:
                    all_links = self.driver.find_elements(By.TAG_NAME, "a")
                    for link in all_links:
                        try:
                            link_text = link.text.strip()
                            link_href = link.get_attribute("href")
                            if "연세포털" in link_text or "spLogin2.php" in (link_href or ""):
                                logger.info(f"   텍스트 기반 발견: '{link_text}' -> {link_href}")
                                portal_login_button = link
                                break
                        except:
                            continue
                except Exception as e:
                    logger.error(f"   링크 검사 실패: {e}")
            
            # 연세포털 로그인 버튼이 있는 경우에만 클릭
            if portal_login_button:
                logger.info("🖱️ 연세포털 로그인 버튼 클릭...")
                portal_login_button.click()
                time.sleep(0.2)
                
                current_url = self.driver.current_url
                logger.info(f"📍 클릭 후 URL: {current_url}")
            else:
                logger.warning("⚠️ 연세포털 로그인 버튼을 찾을 수 없습니다. 직접 로그인 페이지로 이동합니다.")
                logger.info(f"🌐 직접 연세포털 로그인 페이지 접속: {portal_login_url}")
                self.driver.get(portal_login_url)
                time.sleep(0.2)
                
                current_url = self.driver.current_url
                logger.info(f"📍 직접 접속 후 URL: {current_url}")
            
            # 2단계: 연세포털 로그인 페이지에서 로그인
            logger.info("🔐 연세포털 로그인 페이지에서 로그인 시도...")
            
            # 로그인 폼 요소 찾기 (기존 검증된 로직)
            logger.info("🔍 사용자명 필드 찾는 중...")
            username_selectors = [
                "input[id='loginId']",  # 가장 정확한 선택자 (빠름)
                "input[name='loginId']",  # name 속성
                "input[type='text']",  # 타입 기반
                "input[placeholder*='학번']",
                "input[placeholder*='ID']",
                "input[placeholder*='아이디']",
                "input[name='username']",
                "input[name='userid']", 
                "input[name='id']",
                "#username",
                "#userid",
                "#id"
            ]
            
            username_field = None
            for i, selector in enumerate(username_selectors):
                try:
                    logger.info(f"   사용자명 필드 시도 중 ({i+1}/{len(username_selectors)}): {selector}")
                    username_field = self.driver.find_element(By.CSS_SELECTOR, selector)
                    logger.info(f"✅ 사용자명 필드 발견: {selector}")
                    break
                except:
                    logger.debug(f"   실패: {selector}")
                    continue
            
            logger.info("🔍 비밀번호 필드 찾는 중...")
            password_selectors = [
                "input[id='loginPw']",  # 가장 정확한 선택자 (빠름)
                "input[name='loginPw']",  # name 속성
                "input[type='password']",  # 타입 기반
                "input[placeholder*='비밀번호']",
                "input[placeholder*='Password']",
                "input[name='password']",
                "input[name='passwd']",
                "#password",
                "#passwd"
            ]
            
            password_field = None
            for i, selector in enumerate(password_selectors):
                try:
                    logger.info(f"   비밀번호 필드 시도 중 ({i+1}/{len(password_selectors)}): {selector}")
                    password_field = self.driver.find_element(By.CSS_SELECTOR, selector)
                    logger.info(f"✅ 비밀번호 필드 발견: {selector}")
                    break
                except:
                    logger.debug(f"   실패: {selector}")
                    continue
            
            if not username_field or not password_field:
                logger.error("   ❌ 로그인 폼 요소를 찾을 수 없음")
                return False
            
            # 로그인 정보 입력
            username_field.clear()
            username_field.send_keys(username)
            password_field.clear()
            password_field.send_keys(password)
            
            # 로그인 버튼 찾기 및 클릭
            login_button_selectors = [
                "input[type='submit']",
                "button[type='submit']",
                "input[value*='로그인']",
                "button:contains('로그인')",
                ".login-btn",
                ".btn-login"
            ]
            
            login_button = None
            for selector in login_button_selectors:
                try:
                    login_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    logger.info(f"   ✅ 로그인 버튼 발견: {selector}")
                    break
                except:
                    continue
            
            if login_button:
                login_button.click()
                logger.info("   ✅ 로그인 버튼 클릭")
            else:
                # Enter 키로 로그인 시도
                password_field.send_keys("\n")
                logger.info("   ✅ Enter 키로 로그인 시도")
            
            time.sleep(3)
            
            # 3단계: 로그인 성공 확인
            current_url = self.driver.current_url
            page_title = self.driver.title
            logger.info(f"📍 로그인 후 URL: {current_url}")
            logger.info(f"📄 로그인 후 페이지 제목: {page_title}")
            
            # 로그인 성공 확인
            if "login" not in current_url.lower() and "portal" not in current_url.lower():
                logger.info("✅ Selenium 로그인 성공!")
                return True
            else:
                logger.warning("⚠️ Selenium 로그인 실패")
                return False
                
        except Exception as e:
            logger.error(f"❌ Selenium 로그인 오류: {e}")
            return False
    
    def selenium_collect_course_urls(self):
        """Selenium으로 과목 URL 수집 (동적 작업) - 기존 검증된 로직 사용"""
        try:
            logger.info("📚 Selenium으로 과목 URL 수집 중...")
            
            # h3 태그로 과목 찾기 (기존 방식)
            course_elements = self.driver.find_elements(By.TAG_NAME, "h3")
            logger.info(f"   h3 태그 {len(course_elements)}개 발견")
            
            self.course_urls = []
            processed_courses = set()  # 중복 방지
            
            for i, course_element in enumerate(course_elements):
                try:
                    course_name = course_element.text.strip()
                    if not course_name or len(course_name) < 3:
                        continue
                    
                    # 중복 과목 처리 방지
                    if course_name in processed_courses:
                        continue
                    
                    processed_courses.add(course_name)
                    logger.info(f"   과목 {i+1}: {course_name}")
                    
                    # 과목 클릭하여 URL 수집
                    try:
                        course_element.click()
                        time.sleep(1)  # 페이지 로딩 대기
                        
                        current_url = self.driver.current_url
                        if '/course/view.php?id=' in current_url:
                            self.course_urls.append({
                                'name': course_name,
                                'url': current_url
                            })
                            logger.info(f"   ✅ {course_name} URL 수집: {current_url}")
                        
                        # 메인 페이지로 돌아가기
                        self.driver.back()
                        time.sleep(0.5)
                        
                    except Exception as e:
                        logger.warning(f"   ⚠️ {course_name} 클릭 실패: {e}")
                        continue
                        
                except Exception as e:
                    logger.debug(f"   과목 {i+1} 처리 실패: {e}")
                    continue
            
            logger.info(f"✅ {len(self.course_urls)}개 과목 URL 수집 완료")
            return True
            
        except Exception as e:
            logger.error(f"❌ 과목 URL 수집 오류: {e}")
            return False
    
    def http_get_course_content(self, course_url):
        """HTTP Request로 과목 페이지 내용 가져오기 (정적 데이터 추출)"""
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
        """이번주 강의 섹션 찾기 (정적 데이터 분석)"""
        try:
            sections = soup.find_all('li', class_='section main')
            logger.info(f"   {course_name}: {len(sections)}개 섹션 발견")
            
            # 각 섹션 분석
            for idx, section in enumerate(sections):
                try:
                    # 섹션 제목 확인
                    section_title = section.find('h3') or section.find('div', class_='section-title')
                    if section_title:
                        title_text = section_title.get_text().strip().lower()
                        logger.info(f"   섹션 {idx+1}: {title_text}")
                        
                        # 이번주 강의 키워드 확인
                        if any(keyword in title_text for keyword in [
                            "이번주 강의", "이번주", "current week", "week", "주차", "이번 주"
                        ]):
                            if "개요" not in title_text and "overview" not in title_text:
                                logger.info(f"   ✅ '이번주 강의' 섹션 발견: {title_text}")
                                return section
                    
                    # 섹션 전체 텍스트로도 확인
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
            
            # 키워드로 찾지 못했으면 두 번째 섹션 시도
            if len(sections) > 1:
                logger.info(f"   🔍 키워드로 찾지 못함, 두 번째 섹션 사용")
                return sections[1]
            
            # 마지막 수단: 첫 번째 섹션
            if sections:
                logger.info(f"   🔍 첫 번째 섹션 사용")
                return sections[0]
            
            return None
            
        except Exception as e:
            logger.error(f"❌ 섹션 찾기 오류: {e}")
            return None
    
    def extract_activities_from_section(self, section, course_name):
        """섹션에서 활동 추출 (정적 데이터 분석)"""
        activities = []
        
        try:
            # 모든 링크 찾기
            links = section.find_all('a', href=True)
            logger.info(f"   {len(links)}개 링크 발견")
            
            for link in links:
                try:
                    activity_name = link.get_text().strip()
                    activity_url = link.get('href', '')
                    
                    if not activity_name or not activity_url:
                        continue
                    
                    # 의미없는 링크 제외
                    if any(skip in activity_name.lower() for skip in [
                        "더보기", "more", "자세히", "detail", "보기", "view"
                    ]):
                        continue
                    
                    # URL 완성
                    if not activity_url.startswith('http'):
                        activity_url = f"https://ys.learnus.org{activity_url}"
                    
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
    
    def http_extract_all_lectures(self):
        """HTTP Request로 모든 과목의 이번주 강의 추출 (정적 데이터 추출)"""
        try:
            logger.info("🔍 HTTP Request로 이번주 강의 정보 수집 시작...")
            
            all_lectures = []
            
            for i, course in enumerate(self.course_urls[:5]):  # 처음 5개 과목만 테스트
                try:
                    course_name = course['name']
                    course_url = course['url']
                    
                    logger.info(f"\n📖 과목 {i+1}: {course_name}")
                    
                    # HTTP Request로 과목 페이지 가져오기
                    soup = self.http_get_course_content(course_url)
                    if not soup:
                        logger.warning(f"   ⚠️ {course_name} 페이지 로드 실패")
                        continue
                    
                    # 이번주 강의 섹션 찾기
                    this_week_section = self.find_this_week_section(soup, course_name)
                    
                    if this_week_section:
                        # 섹션에서 활동 추출
                        course_activities = self.extract_activities_from_section(this_week_section, course_name)
                        
                        if course_activities:
                            all_lectures.extend(course_activities)
                            logger.info(f"   📚 {len(course_activities)}개 활동 발견")
                        else:
                            logger.info(f"   📭 활동 없음")
                    else:
                        logger.info(f"   📭 '이번주 강의' 섹션 없음")
                    
                    # 요청 간격 조절 (서버 부하 방지)
                    time.sleep(0.5)
                        
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
                f.write("📚 이번주 강의 활동 목록 (최적화된 하이브리드 방식)\n")
                f.write("=" * 70 + "\n\n")
                f.write(f"수집 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"총 수집된 활동 수: {len(lectures)}개\n")
                f.write("💡 Selenium(동적 작업) + HTTP Request(정적 추출) 하이브리드\n\n")
                
                if lectures:
                    # 과목별로 그룹화
                    course_groups = {}
                    for lecture in lectures:
                        course = lecture['course']
                        if course not in course_groups:
                            course_groups[course] = []
                        course_groups[course].append(lecture)
                    
                    # 과목별로 출력
                    for course, activities in course_groups.items():
                        f.write(f"📖 {course}\n")
                        f.write("-" * 50 + "\n")
                        
                        for activity in activities:
                            f.write(f"  • {activity['activity']} ({activity['type']})\n")
                            f.write(f"    URL: {activity['url']}\n\n")
                        
                        f.write("\n")
                else:
                    f.write("❌ 수집된 이번주 강의 활동이 없습니다.\n")
                    f.write("🔍 디버깅 정보:\n")
                    f.write("- 로그 파일(optimized_hybrid_extractor.log)을 확인해보세요.\n")
                
            logger.info("💾 assignment.txt 파일에 저장 완료")
            return True
            
        except Exception as e:
            logger.error(f"❌ 파일 저장 실패: {e}")
            return False
    
    def run(self, username=None, password=None):
        """메인 실행 함수"""
        print("🚀 최적화된 하이브리드 이번주 강의 추출기")
        print("=" * 70)
        print("💡 Selenium(동적 작업) + HTTP Request(정적 추출) 최적 조합")
        print("⚡ 로그인/클릭/이동: Selenium | 데이터 추출: HTTP Request")
        
        # 로그인 정보 입력
        if not username or not password:
            print("\n📝 자동화 테스트를 위한 정보 입력")
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
        
        # 1단계: Selenium 드라이버 설정
        if not self.setup_driver():
            return False
        
        try:
            # 2단계: Selenium으로 로그인 (동적 작업)
            if not self.selenium_login(username, password):
                print("❌ 로그인 실패")
                return False
            
            # 3단계: Selenium으로 과목 URL 수집 (동적 작업)
            if not self.selenium_collect_course_urls():
                print("❌ 과목 URL 수집 실패")
                return False
            
            # 4단계: HTTP 세션 설정 (쿠키 전달)
            if not self.setup_http_session():
                print("❌ HTTP 세션 설정 실패")
                return False
            
            # 5단계: HTTP Request로 데이터 추출 (정적 작업)
            lectures = self.http_extract_all_lectures()
            
            # 6단계: 결과 저장
            if self.save_to_file(lectures):
                print(f"\n✅ 총 {len(lectures)}개 이번주 강의 활동 수집 완료!")
                print("📄 assignment.txt 파일을 확인하세요.")
                print("⚡ 최적화된 하이브리드 방식으로 빠르고 안정적으로 처리되었습니다!")
                print("💡 동적 작업: Selenium | 정적 추출: HTTP Request")
            else:
                print("\n❌ 파일 저장 실패")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 실행 오류: {e}")
            return False
        
        finally:
            try:
                self.driver.quit()
                logger.info("🔚 Selenium 드라이버 종료")
            except:
                pass

def main():
    extractor = OptimizedHybridExtractor()
    extractor.run()

if __name__ == "__main__":
    main()
