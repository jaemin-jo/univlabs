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

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('automation_debug.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def collect_this_week_lectures(driver):
    """이번주 강의 정보 수집 (하이브리드 방식)"""
    try:
        logger.info("🔍 이번주 강의 정보 수집 시작...")
        
        # h3 태그로 과목 찾기
        course_elements = driver.find_elements(By.TAG_NAME, "h3")
        logger.info(f"h3 태그 {len(course_elements)}개 발견")
        
        all_lectures = []
        processed_courses = set()  # 중복 방지
        
        for i, course_element in enumerate(course_elements):
            try:
                course_name = course_element.text.strip()
                if not course_name or len(course_name) < 3:
                    continue
                
                # 중복 과목 처리 방지
                if course_name in processed_courses:
                    logger.info(f"과목 {i+1}: {course_name} (중복, 건너뜀)")
                    continue
                
                processed_courses.add(course_name)
                logger.info(f"과목 {i+1}: {course_name} 처리 중... (총 {len(course_elements)}개 중 {i+1}번째)")
                
                # Selenium으로 과목 클릭 (기존 코드와 동일한 간단한 로직)
                try:
                    selenium_course_element = driver.find_element(By.XPATH, f"//h3[contains(text(), '{course_name}')]")
                    selenium_course_element.click()
                    time.sleep(0.3)  # 기존 코드와 동일한 짧은 대기
                    logger.info(f"   ✅ {course_name} 과목 페이지 진입")
                except Exception as e:
                    logger.warning(f"   ⚠️ {course_name} 과목 클릭 실패: {e}")
                    continue
                
                # BeautifulSoup으로 현재 페이지 분석
                try:
                    current_page_source = driver.page_source
                    current_soup = BeautifulSoup(current_page_source, 'html.parser')
                    
                    # 이번주 강의 섹션 찾기
                    this_week_section = None
                    
                    # 1단계: 다양한 선택자로 섹션 찾기 (기존 검증된 로직)
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
                    
                    # 4단계: 모든 섹션을 검사하여 링크가 있는 섹션 찾기 (추가 강화)
                    if not this_week_section:
                        logger.info(f"   🔍 모든 섹션 검사 중...")
                        all_sections = current_soup.find_all(['li', 'div'], class_=lambda x: x and 'section' in x)
                        for section in all_sections:
                            links = section.find_all('a', href=True)
                            if len(links) > 0:
                                this_week_section = section
                                logger.info(f"   ✅ 링크가 있는 섹션 발견: {len(links)}개 링크")
                                break
                    
                    # 5단계: 최후의 수단 - 모든 링크가 있는 요소 찾기
                    if not this_week_section:
                        logger.info(f"   🔍 최후의 수단: 모든 링크 검사...")
                        all_links = current_soup.find_all('a', href=True)
                        if all_links:
                            # 링크가 있는 첫 번째 부모 요소를 섹션으로 사용
                            for link in all_links:
                                parent = link.find_parent(['li', 'div'], class_=lambda x: x and 'section' in x)
                                if parent:
                                    this_week_section = parent
                                    logger.info(f"   ✅ 링크의 부모 섹션 발견")
                                    break
                    
                    if this_week_section:
                        logger.info(f"   ✅ {course_name}에서 '이번주 강의' 섹션 발견")
                        
                        # 이번주 강의 섹션 내의 모든 활동 링크 찾기
                        activity_links = this_week_section.find_all('a', href=True)
                        
                        course_lectures = []
                        for link in activity_links:
                            try:
                                activity_name = link.get_text().strip()
                                activity_url = link.get('href', '')
                                
                                if not activity_name or not activity_url:
                                    continue
                                
                                # 활동 타입 판별 (기존 검증된 로직)
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
                                
                                lecture_info = {
                                    "course": course_name,
                                    "activity": activity_name,
                                    "type": activity_type,
                                    "url": activity_url
                                }
                                
                                course_lectures.append(lecture_info)
                                logger.info(f"     ✅ {activity_name} ({activity_type})")
                                
                            except Exception as e:
                                continue
                        
                        if course_lectures:
                            all_lectures.extend(course_lectures)
                            logger.info(f"   📚 {course_name}: {len(course_lectures)}개 활동 발견")
                        else:
                            logger.info(f"   📭 {course_name}: 이번주 강의 활동 없음")
                    else:
                        logger.info(f"   📭 {course_name}: '이번주 강의' 섹션 없음")
                
                except Exception as e:
                    logger.warning(f"   {course_name} 페이지 분석 실패: {e}")
                
                # 메인 페이지로 돌아가기 (기존 코드와 동일한 간단한 로직)
                try:
                    driver.back()
                    time.sleep(0.3)  # 기존 코드와 동일한 짧은 대기
                    logger.info(f"   ✅ {course_name} 메인 페이지 복귀 완료")
                except Exception as e:
                    logger.warning(f"   {course_name} 메인 페이지 복귀 실패: {e}")
                    # 복귀 실패 시 메인 페이지로 직접 이동
                    try:
                        driver.get("https://ys.learnus.org/")
                        time.sleep(0.5)
                        logger.info(f"   🔄 {course_name} 메인 페이지 직접 이동")
                    except Exception as e2:
                        logger.error(f"   ❌ {course_name} 메인 페이지 직접 이동 실패: {e2}")
                    
            except Exception as e:
                logger.debug(f"   과목 {i+1} 처리 실패: {e}")
                continue
        
        logger.info(f"🔍 총 {len(all_lectures)}개 활동 수집 완료")
        logger.info(f"📚 처리된 과목 수: {len(processed_courses)}개")
        
        # 결과를 파일로 저장
        try:
            with open('assignment.txt', 'w', encoding='utf-8') as f:
                f.write("📚 이번주 강의 활동 목록\n")
                f.write("=" * 50 + "\n\n")
                f.write(f"수집 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"총 수집된 활동 수: {len(all_lectures)}개\n\n")
                
                if all_lectures:
                    # 과목별로 그룹화
                    course_groups = {}
                    for lecture in all_lectures:
                        course = lecture['course']
                        if course not in course_groups:
                            course_groups[course] = []
                        course_groups[course].append(lecture)
                    
                    # 과목별로 출력
                    for course, activities in course_groups.items():
                        f.write(f"📖 {course}\n")
                        f.write("-" * 40 + "\n")
                        
                        for activity in activities:
                            f.write(f"  • {activity['activity']} ({activity['type']})\n")
                            f.write(f"    URL: {activity['url']}\n\n")
                        
                        f.write("\n")
                else:
                    f.write("❌ 수집된 이번주 강의 활동이 없습니다.\n")
                    f.write("🔍 디버깅 정보:\n")
                    f.write("- 과목별로 '이번주 강의' 섹션을 찾지 못했을 수 있습니다.\n")
                    f.write("- 각 과목의 페이지 구조가 예상과 다를 수 있습니다.\n")
                    f.write("- 로그 파일(automation_debug.log)을 확인해보세요.\n")
                
            logger.info("💾 이번주 강의 정보가 assignment.txt 파일에 저장되었습니다")
        except Exception as e:
            logger.error(f"❌ 파일 저장 실패: {e}")
        
        return all_lectures
        
    except Exception as e:
        logger.error(f"❌ 이번주 강의 정보 수집 오류: {e}")
        return []

def test_direct_selenium(university, username, password, student_id):
    """직접 Selenium을 사용한 로그인 테스트"""
    driver = None
    try:
        logger.info(f"🧪 직접 Selenium 테스트 시작: {university}")
        logger.info(f"   사용자: {username}")
        logger.info(f"   학번: {student_id}")
        
        # Chrome 드라이버 설정
        logger.info("🔧 Chrome 드라이버 설정 중...")
        chrome_options = Options()
        
        # 기본 설정
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
        
        try:
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # 자동화 감지 방지
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            # 페이지 로드 타임아웃 설정
            driver.set_page_load_timeout(30)
            driver.implicitly_wait(10)
            
            logger.info("✅ Chrome 드라이버 초기화 완료")
        except Exception as e:
            logger.error(f"❌ Chrome 드라이버 초기화 실패: {e}")
            raise
        
        # 1단계: LearnUs 메인 페이지 접속 또는 직접 연세포털 로그인 페이지 접속
        learnus_url = "https://ys.learnus.org/"
        portal_login_url = "https://ys.learnus.org/passni/sso/spLogin2.php"
        
        logger.info(f"🌐 LearnUs 메인 페이지 접속: {learnus_url}")
        driver.get(learnus_url)
        
        # 페이지 로딩 대기 (단축)
        logger.info("⏳ 페이지 로딩 대기 중...")
        time.sleep(0.5)
        
        # 현재 URL과 페이지 제목 로깅
        current_url = driver.current_url
        page_title = driver.title
        logger.info(f"📍 현재 URL: {current_url}")
        logger.info(f"📄 페이지 제목: {page_title}")
        
        # 페이지 소스 일부 저장 (디버깅용)
        with open('debug_page_source.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        logger.info("💾 페이지 소스 저장: debug_page_source.html")
        
        # 연세포털 로그인 버튼 찾기 및 클릭
        logger.info("🔍 연세포털 로그인 버튼 찾는 중...")
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
                portal_login_button = driver.find_element(By.CSS_SELECTOR, selector)
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
                    portal_login_button = driver.find_element(By.XPATH, xpath)
                    logger.info(f"✅ 연세포털 로그인 버튼 발견 (XPath): {xpath}")
                    break
                except:
                    logger.debug(f"   XPath 실패: {xpath}")
                    continue
        
        # 3단계: 모든 링크를 검사하여 텍스트로 찾기
        if not portal_login_button:
            logger.info("   XPath도 실패, 모든 링크 검사 중...")
            try:
                all_links = driver.find_elements(By.TAG_NAME, "a")
                for link in all_links:
                    try:
                        link_text = link.text.strip()
                        link_href = link.get_attribute("href")
                        if "연세포털" in link_text or "spLogin2.php" in (link_href or ""):
                            logger.info(f"   텍스트 기반 발견: '{link_text}' -> {link_href}")
                            portal_login_button = link
                            break
                    except Exception as e:
                        logger.debug(f"   링크 검사 중 오류: {e}")
                        continue
            except Exception as e:
                logger.error(f"   링크 검사 실패: {e}")
        
        # 연세포털 로그인 버튼이 있는 경우에만 클릭
        if portal_login_button:
            logger.info("🖱️ 연세포털 로그인 버튼 클릭...")
            portal_login_button.click()
            time.sleep(0.1)
            
            # 클릭 후 URL 확인
            current_url = driver.current_url
            logger.info(f"📍 클릭 후 URL: {current_url}")
        else:
            logger.warning("⚠️ 연세포털 로그인 버튼을 찾을 수 없습니다. 직접 로그인 페이지로 이동합니다.")
            logger.info(f"🌐 직접 연세포털 로그인 페이지 접속: {portal_login_url}")
            driver.get(portal_login_url)
            time.sleep(0.1)
            
            # 현재 URL 확인
            current_url = driver.current_url
            logger.info(f"📍 직접 접속 후 URL: {current_url}")
            
            logger.info("🔍 페이지에서 사용 가능한 링크들:")
            try:
                links = driver.find_elements(By.TAG_NAME, "a")
                for i, link in enumerate(links[:10]):  # 처음 10개만
                    href = link.get_attribute("href")
                    text = link.text.strip()
                    if href and text:
                        logger.info(f"   링크 {i+1}: {text} -> {href}")
            except Exception as e:
                logger.error(f"링크 정보 수집 실패: {e}")
        
        # 2단계: 연세포털 로그인 페이지에서 실제 로그인
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
                username_field = driver.find_element(By.CSS_SELECTOR, selector)
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
                password_field = driver.find_element(By.CSS_SELECTOR, selector)
                logger.info(f"✅ 비밀번호 필드 발견: {selector}")
                break
            except:
                logger.debug(f"   실패: {selector}")
                continue
        
        if not username_field or not password_field:
            logger.error("❌ 로그인 폼 요소를 찾을 수 없습니다")
            return False
        
        # 로그인 정보 입력
        logger.info("📝 로그인 정보 입력 중...")
        username_field.clear()
        username_field.send_keys(username)
        password_field.clear()
        password_field.send_keys(password)
        
        # 로그인 버튼 찾기 및 클릭 (Enter 키를 먼저 시도)
        logger.info("🔍 로그인 버튼 찾는 중...")
        
        # 1단계: Enter 키로 먼저 시도 (가장 빠르고 정확)
        logger.info("⌨️ Enter 키로 로그인 시도...")
        password_field.send_keys("\n")
        time.sleep(2)
        
        # 로그인 성공 확인
        current_url = driver.current_url
        if "login" not in current_url.lower() and "portal" not in current_url.lower():
            logger.info("✅ Enter 키로 로그인 성공!")
        else:
            # 2단계: Enter 키 실패 시 버튼 클릭 시도
            logger.info("🔍 Enter 키 실패, 로그인 버튼 찾기...")
            login_button_selectors = [
                "input[type='submit']",
                "button[type='submit']",
                "input[value*='로그인']",
                "button:contains('로그인')",
                ".login-btn",
                ".btn-login"
            ]
            
            login_button = None
            for i, selector in enumerate(login_button_selectors):
                try:
                    logger.info(f"   로그인 버튼 시도 중 ({i+1}/{len(login_button_selectors)}): {selector}")
                    login_button = driver.find_element(By.CSS_SELECTOR, selector)
                    logger.info(f"✅ 로그인 버튼 발견: {selector}")
                    break
                except:
                    logger.debug(f"   실패: {selector}")
                    continue
            
            if login_button:
                logger.info("🖱️ 로그인 버튼 클릭...")
                login_button.click()
            else:
                logger.warning("⚠️ 로그인 버튼을 찾을 수 없음")
        
        time.sleep(2)
        
        # 3단계: 로그인 성공 확인
        current_url = driver.current_url
        page_title = driver.title
        logger.info(f"📍 로그인 후 URL: {current_url}")
        logger.info(f"📄 로그인 후 페이지 제목: {page_title}")
        
        # 로그인 성공 확인
        if "login" not in current_url.lower() and "portal" not in current_url.lower():
            logger.info("✅ 로그인 성공!")
            
            # 이번주 강의 정보 수집
            lectures = collect_this_week_lectures(driver)
            
            if lectures:
                logger.info(f"📚 총 {len(lectures)}개 이번주 강의 활동 수집 완료!")
                return True
            else:
                logger.warning("⚠️ 이번주 강의 활동을 찾을 수 없습니다")
                return False
        else:
            logger.warning("⚠️ 로그인 실패")
            return False
            
    except Exception as e:
        logger.error(f"❌ 테스트 실행 오류: {e}")
        return False
    
    finally:
        try:
            if driver:
                driver.quit()
                logger.info("🔚 Chrome 드라이버 종료")
        except:
            pass

def main():
    """메인 함수"""
    print("🚀 LearnUs 이번주 강의 자동화 테스트")
    print("=" * 50)
    
    # 사용자 입력
    university_input = input("대학교 (예: 연세대학교) 또는 9887: ").strip()
    
    if university_input == "9887":
        university = "연세대학교"
        username = "2024248012"
        password = "cjm9887@"
        student_id = "2024248012"
        print("🚀 개발자 모드: 연세대학교 자동 설정!")
        print(f"   대학교: {university}")
        print(f"   학번: {username}")
        print(f"   비밀번호: {password}")
    else:
        university = university_input
        username = input("아이디/학번: ").strip()
        password = input("비밀번호: ").strip()
        student_id = input("학번 (선택사항): ").strip()
    
    if not university or not username or not password:
        print("❌ 필수 정보가 누락되었습니다")
        return
    
    # 테스트 실행
    success = test_direct_selenium(university, username, password, student_id)
    
    if success:
        print("\n✅ 테스트 완료! assignment.txt 파일을 확인하세요.")
    else:
        print("\n❌ 테스트 실패. 로그 파일을 확인하세요.")

if __name__ == "__main__":
    main()
