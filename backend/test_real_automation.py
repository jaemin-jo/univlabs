"""
실제 자동화 테스트 스크립트
- 연세대학교 LearnUs 로그인 테스트
- 과제 정보 수집 테스트
"""

import asyncio
import json
import requests
import logging
import time
import re
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.service import Service

# 로깅 설정
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('automation_debug.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def test_backend_connection():
    """백엔드 서버 연결 테스트"""
    try:
        response = requests.get('http://localhost:8000/health', timeout=5)
        if response.status_code == 200:
            print("✅ 백엔드 서버 연결 성공")
            return True
        else:
            print(f"❌ 백엔드 서버 응답 오류: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 백엔드 서버 연결 실패: {e}")
        return False

def collect_course_info(driver):
    """과목 정보 수집 함수"""
    import re  # 함수 내부에서 re 모듈 import
    try:
        logger.info("🔍 과목 정보 수집 중...")
        
        # h3 태그로 과목명 찾기
        course_elements = driver.find_elements(By.TAG_NAME, "h3")
        courses = []
        
        logger.info(f"   h3 태그 {len(course_elements)}개 발견")
        for i, element in enumerate(course_elements):
            try:
                course_text = element.text.strip()
                if course_text and len(course_text) > 2:  # 의미있는 텍스트만
                    courses.append(course_text)
                    logger.info(f"   발견된 과목 (h3-{i+1}): {course_text}")
            except Exception as e:
                logger.debug(f"   과목 정보 추출 실패 (h3-{i+1}): {e}")
                continue
        
        # LearnUs 특화 선택자들 (개발자 도구에서 확인한 구조 기반)
        learnus_selectors = [
            ".my-course-lists .course-title",
            ".my-course-lists .course-name", 
            ".course-box .course-title",
            ".course-box .course-name",
            "a[href*='course/view.php'] .course-title",
            "a[href*='course/view.php'] .course-name",
            ".course-link .course-title",
            ".course-link .course-name",
            ".course-item .title",
            ".course-item .name",
            # 추가 선택자들
            ".my-course-lists h3",
            ".course-box h3",
            ".course-link h3",
            "a[href*='course/view.php'] h3",
            ".course-title",
            ".course-name",
            ".course-link",
            ".course-box",
            ".my-course-lists li",
            ".course-list li"
        ]
        
        for selector in learnus_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    try:
                        course_text = element.text.strip()
                        if course_text and len(course_text) > 2:
                            courses.append(course_text)
                            logger.info(f"   발견된 과목 ({selector}): {course_text}")
                    except Exception as e:
                        continue
            except Exception as e:
                logger.debug(f"   선택자 실패: {selector} - {e}")
                continue
        
        # h3가 없는 경우 다른 선택자들 시도
        if not courses:
            logger.info("   h3 태그에서 과목을 찾지 못함, 다른 선택자 시도...")
            
            # 다양한 선택자로 과목명 찾기
            course_selectors = [
                ".course-title",
                ".course-name", 
                ".course-link",
                ".course-box",
                ".my-course-lists .course-title",
                ".my-course-lists .course-name",
                ".course-list .course-title",
                ".course-list .course-name",
                "a[href*='course/view.php']",
                ".course-item .title",
                ".course-item .name"
            ]
            
            for selector in course_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        try:
                            course_text = element.text.strip()
                            if course_text and len(course_text) > 2:
                                courses.append(course_text)
                                logger.info(f"   발견된 과목 ({selector}): {course_text}")
                        except Exception as e:
                            continue
                except Exception as e:
                    logger.debug(f"   선택자 실패: {selector} - {e}")
                    continue
        
        # 중복 제거
        courses = list(set(courses))
        
        # 과목 정보가 여전히 없는 경우 페이지 소스에서 직접 검색
        if not courses:
            logger.info("   선택자로 과목을 찾지 못함, 페이지 소스에서 검색...")
            try:
                page_source = driver.page_source
                
                # 페이지 소스에서 과목명 패턴 찾기
                import re
                course_patterns = [
                    r'([A-Z]{3}\d{4}\.\d{2}-\d{2})',  # ASD2009.01-00 패턴
                    r'([A-Z]{3}\d{4})',  # ASD2009 패턴
                    r'(\d{4}-\d{2}학기)',  # 2025-2학기 패턴
                    r'(AI응용수학|기초AI알고리즘|AI시스템프로그래밍|딥러닝입문|채플|RC체육활동|뉴미디어와대중문화의이해)',  # 실제 과목명
                    r'(생활관 화재대피훈련)',  # 비교과 과목
                ]
                
                for pattern in course_patterns:
                    matches = re.findall(pattern, page_source)
                    for match in matches:
                        if match not in courses:
                            courses.append(match)
                            logger.info(f"   패턴 매칭 발견: {match}")
                
                # HTML 태그에서 텍스트 추출
                logger.info("   HTML 태그에서 텍스트 추출 시도...")
                try:
                    # 모든 텍스트 요소 찾기
                    all_elements = driver.find_elements(By.XPATH, "//*[text()]")
                    for element in all_elements:
                        try:
                            text = element.text.strip()
                            # 과목명으로 보이는 텍스트 필터링
                            if (len(text) > 3 and len(text) < 50 and 
                                not text.startswith(('http', 'www', 'mailto')) and
                                not text in ['로그인', '로그아웃', '메뉴', '검색', '설정']):
                                if text not in courses:
                                    courses.append(text)
                                    logger.info(f"   텍스트 추출: {text}")
                        except:
                            continue
                except Exception as e:
                    logger.debug(f"   텍스트 추출 실패: {e}")
                    
            except Exception as e:
                logger.error(f"   페이지 소스 검색 실패: {e}")
        
        # 과목 정보를 구조화된 형태로 정리 (중복 제거 강화)
        structured_courses = []
        seen_courses = set()
        
        for course in courses:
            if course and len(course.strip()) > 2:
                clean_course = course.strip()
                
                # 과목명만 추출 (교수명, 학습률 등 제거)
                course_name = clean_course
                
                # 불필요한 정보 제거
                if '\n' in course_name:
                    lines = course_name.split('\n')
                    # 첫 번째 줄이 과목명일 가능성이 높음
                    course_name = lines[0].strip()
                
                # 교수명, 학습률, 출석현황 등 제거
                course_name = re.sub(r'\s*/\s*[^/]+$', '', course_name)  # 교수명 제거
                course_name = re.sub(r'\s*학습률\s*\d+\.?\d*%', '', course_name)  # 학습률 제거
                course_name = re.sub(r'\s*출석현황', '', course_name)  # 출석현황 제거
                course_name = re.sub(r'\s*NEW$', '', course_name)  # NEW 제거
                course_name = re.sub(r'\s*\(2학기\)$', '', course_name)  # (2학기) 제거
                course_name = re.sub(r'\s*\(학부\)$', '', course_name)  # (학부) 제거
                course_name = re.sub(r'^교과\s*', '', course_name)  # 교과 제거
                course_name = re.sub(r'^비교과\s*', '', course_name)  # 비교과 제거
                course_name = re.sub(r'^학부\s*', '', course_name)  # 학부 제거
                
                # 의미있는 과목명만 추가
                if (len(course_name) > 3 and 
                    course_name not in seen_courses and
                    not course_name.startswith(('http', 'www', 'mailto')) and
                    course_name not in ['로그인', '로그아웃', '메뉴', '검색', '설정', '출석현황']):
                    
                    structured_courses.append(course_name)
                    seen_courses.add(course_name)
                    logger.info(f"   정리된 과목: {course_name}")
        
        logger.info(f"📊 총 {len(structured_courses)}개 과목 정보 수집 완료")
        
        # 과목 정보를 파일로 저장
        try:
            with open('collected_courses.txt', 'w', encoding='utf-8') as f:
                f.write("=== 수집된 과목 정보 ===\n")
                f.write(f"총 {len(structured_courses)}개 과목\n\n")
                for i, course in enumerate(structured_courses, 1):
                    f.write(f"{i}. {course}\n")
            logger.info("💾 과목 정보가 collected_courses.txt 파일에 저장되었습니다")
        except Exception as e:
            logger.error(f"❌ 파일 저장 실패: {e}")
        
        return structured_courses
        
    except Exception as e:
        logger.error(f"❌ 과목 정보 수집 오류: {e}")
        return []

def collect_this_week_lectures(driver):
    """각 과목의 '이번주 강의' 박스 요소만 추출"""
    try:
        logger.info("🔍 각 과목의 '이번주 강의' 정보 수집 중...")
        
        # 현재 페이지의 HTML 소스 가져오기
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        
        # h3 태그로 과목 찾기
        course_elements = soup.find_all('h3')
        logger.info(f"   h3 태그 {len(course_elements)}개 발견")
        
        all_lectures = []
        processed_courses = set()  # 이미 처리된 과목 추적
        
        for i, course_element in enumerate(course_elements):
            try:
                course_name = course_element.get_text().strip()
                if not course_name or len(course_name) < 3:
                    continue
                
                # 중복 과목 처리 방지
                if course_name in processed_courses:
                    continue
                
                processed_courses.add(course_name)
                logger.info(f"   과목 {i+1}: {course_name} 처리 중...")
                
                # Selenium으로 과목 클릭
                try:
                    selenium_course_element = driver.find_element(By.XPATH, f"//h3[contains(text(), '{course_name}')]")
                    selenium_course_element.click()
                    time.sleep(1)  # 페이지 로딩 대기
                    logger.info(f"   ✅ {course_name} 과목 페이지 진입")
                except Exception as e:
                    logger.warning(f"   ⚠️ {course_name} 과목 클릭 실패: {e}")
                    continue
                
                # BeautifulSoup으로 현재 페이지 분석
                try:
                    current_page_source = driver.page_source
                    current_soup = BeautifulSoup(current_page_source, 'html.parser')
                    
                    # "이번주 강의" 섹션 찾기 (더 정확한 검색)
                    this_week_section = None
                    
                    # 1단계: 정확한 키워드로 검색
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
                            # 더 다양한 키워드로 검색
                            if any(keyword in section_text for keyword in [
                                "이번주 강의", "이번주", "current week", "current week course",
                                "이번주강의", "current week lecture", "week", "주차",
                                "이번 주", "현재 주", "current", "강의"
                            ]):
                                # "강의 개요"는 제외
                                if "개요" not in section_text and "overview" not in section_text:
                                    this_week_section = section
                                    logger.info(f"   ✅ '이번주 강의' 섹션 발견: {section_text[:50]}...")
                                    break
                        if this_week_section:
                            break
                    
                    # 2단계: 두 번째 섹션을 시도 (첫 번째는 보통 강의 개요)
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
                
                # 메인 페이지로 돌아가기
                try:
                    driver.back()
                    time.sleep(0.5)
                except Exception as e:
                    try:
                        driver.get("https://ys.learnus.org/")
                        time.sleep(0.5)
                    except Exception as e2:
                        pass
                    
            except Exception as e:
                logger.warning(f"   과목 {i+1} 처리 실패: {e}")
                continue
        
        # 결과 저장
        logger.info(f"📊 총 {len(all_lectures)}개 이번주 강의 활동 수집 완료")
        
        # 디버깅: 수집된 데이터 로그 출력
        logger.info(f"🔍 수집된 데이터 상세:")
        for i, lecture in enumerate(all_lectures, 1):
            logger.info(f"   {i}. {lecture}")
        
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

def collect_assignment_deadlines_hybrid(driver):
    """BeautifulSoup + Selenium 하이브리드 방식으로 과제 정보 수집"""
    try:
        logger.info("🔍 하이브리드 방식으로 과제 정보 수집 중...")
        
        # 현재 페이지의 HTML 소스 가져오기
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        
        # h3 태그로 과목 찾기
        course_elements = soup.find_all('h3')
        logger.info(f"   h3 태그 {len(course_elements)}개 발견")
        
        assignment_deadlines = []
        processed_courses = set()  # 이미 처리된 과목 추적
        
        for i, course_element in enumerate(course_elements):
            try:
                course_name = course_element.get_text().strip()
                if not course_name or len(course_name) < 3:
                    continue
                
                # 중복 과목 처리 방지
                if course_name in processed_courses:
                    continue
                
                processed_courses.add(course_name)
                logger.info(f"   과목 {i+1}: {course_name} 처리 중...")
                
                # Selenium으로 과목 클릭
                try:
                    selenium_course_element = driver.find_element(By.XPATH, f"//h3[contains(text(), '{course_name}')]")
                    selenium_course_element.click()
                    time.sleep(0.5)  # 페이지 로딩 대기
                    logger.info(f"   ✅ {course_name} 과목 페이지 진입")
                except Exception as e:
                    logger.warning(f"   ⚠️ {course_name} 과목 클릭 실패: {e}")
                    continue
                
                # BeautifulSoup으로 현재 페이지 분석
                try:
                    current_page_source = driver.page_source
                    current_soup = BeautifulSoup(current_page_source, 'html.parser')
                    
                    # 주차별 섹션 찾기
                    week_sections = current_soup.find_all('li', class_='section main')
                    logger.info(f"   {course_name}에서 {len(week_sections)}개 주차 섹션 발견")
                    
                    if len(week_sections) > 0:
                        # 각 주차 섹션 분석
                        for section_idx, section in enumerate(week_sections):
                            try:
                                section_text = section.get_text().lower()
                                
                                # 의미없는 섹션 건너뛰기
                                skip_section_keywords = [
                                    "강의 개요", "개요", "course overview", 
                                    "이번주강의", "current week course", 
                                    "이번주", "current week",
                                    "강의개요", "course outline",
                                    "class announcements", "강의 공지", "공지사항", "과목공지",
                                    "announcements", "notice", "notices",
                                    "course summary", "강의 요약", "요약",
                                    "class q&a", "강의 q&a", "질문과 답변",
                                    "class files", "강의 파일", "파일",
                                    "course files", "강의 자료"
                                ]
                                
                                if any(keyword in section_text for keyword in skip_section_keywords):
                                                    continue
                                            
                                # 실제 활동 링크 찾기
                                activity_links = section.find_all('a', href=re.compile(r'mod/(assign|vod|resource|ubfile|ubboard)/'))
                                
                                if len(activity_links) > 0:
                                    logger.info(f"   섹션 {section_idx + 1}에서 {len(activity_links)}개 활동 발견")
                                    
                                    # 각 활동 처리
                                    for link in activity_links:
                                        try:
                                            activity_name = link.get_text().strip()
                                            activity_url = link.get('href', '')
                                            
                                            if not activity_name or not activity_url:
                                                continue
                                        
                                            # 활동 타입 판별
                                            activity_type = "unknown"
                                            if "mod/assign/" in activity_url:
                                                activity_type = "과제"
                                            elif "mod/vod/" in activity_url:
                                                activity_type = "동영상"
                                            elif "mod/resource/" in activity_url or "mod/ubfile/" in activity_url:
                                                activity_type = "PDF 자료"
                                            elif "mod/ubboard/" in activity_url:
                                                activity_type = "게시판"
                                            
                                            # 활동 정보 저장
                                            activity_info = {
                                                "course": course_name,
                                                "activity": activity_name,
                                                "type": activity_type,
                                                "url": activity_url,
                                                "week": f"섹션 {section_idx + 1}"
                                            }
                                            
                                            assignment_deadlines.append(activity_info)
                                            logger.info(f"     ✅ {activity_name} ({activity_type})")
                                            
                                        except Exception as e:
                                            continue
                                        
                                    except Exception as e:
                                        continue
                                    
                    else:
                        logger.info(f"   📭 {course_name}에 주차 섹션이 없습니다.")
                            
                except Exception as e:
                    logger.warning(f"   {course_name} 페이지 분석 실패: {e}")
                
                # 메인 페이지로 돌아가기
                try:
                    driver.back()
                    time.sleep(0.1)
                except Exception as e:
                    try:
                        driver.get("https://ys.learnus.org/")
                        time.sleep(0.1)
                    except Exception as e2:
                        pass
                    
            except Exception as e:
                logger.warning(f"   과목 {i+1} 처리 실패: {e}")
                continue
        
        # 결과 저장
        logger.info(f"📊 총 {len(assignment_deadlines)}개 과제 마감일 정보 수집 완료")
        
        try:
            with open('assignment.txt', 'w', encoding='utf-8') as f:
                f.write("📋 과제 마감일 정보\n")
                f.write("=" * 50 + "\n\n")
                
                if assignment_deadlines:
                    # 과목별로 그룹화
                    course_groups = {}
                    for deadline_info in assignment_deadlines:
                        course = deadline_info['course']
                        if course not in course_groups:
                            course_groups[course] = []
                        course_groups[course].append(deadline_info)
                    
                    # 과목별로 출력
                    for course_idx, (course_name, activities) in enumerate(course_groups.items(), 1):
                        f.write(f"📚 과목 {course_idx}: {course_name}\n")
                        f.write("=" * 60 + "\n")
                        
                        for activity_idx, activity in enumerate(activities, 1):
                            f.write(f"  📋 활동 {activity_idx}: {activity['activity']}\n")
                            f.write(f"     타입: {activity['type']}\n")
                            if 'week' in activity:
                                f.write(f"     주차: {activity['week']}\n")
                            if 'url' in activity:
                                f.write(f"     링크: {activity['url']}\n")
                            f.write("-" * 40 + "\n")
                        
                        f.write("\n")
                    
                    # 요약 정보
                    f.write("📊 요약 정보\n")
                    f.write("=" * 30 + "\n")
                    f.write(f"총 과목 수: {len(course_groups)}개\n")
                    f.write(f"총 활동 수: {len(assignment_deadlines)}개\n")
                    
                    for course_name, activities in course_groups.items():
                        f.write(f"  • {course_name}: {len(activities)}개 활동\n")
                    
                else:
                    f.write("과제 마감일 정보를 찾을 수 없습니다.\n")
                
            logger.info("💾 과제 마감일 정보가 assignment.txt 파일에 저장되었습니다")
        except Exception as e:
            logger.error(f"❌ 파일 저장 실패: {e}")
        
        return assignment_deadlines
        
    except Exception as e:
        logger.error(f"❌ 하이브리드 과제 정보 수집 오류: {e}")
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
        chrome_options.add_argument("--log-level=3")  # INFO 레벨
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # 헤드리스 모드 비활성화 (디버깅을 위해)
        # chrome_options.add_argument("--headless")
        
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
        
        # 스크린샷 저장 함수 제거 (성능 최적화)
        
        # 1단계: LearnUs 메인 페이지 접속 또는 직접 연세포털 로그인 페이지 접속
        learnus_url = "https://ys.learnus.org/"
        portal_login_url = "https://ys.learnus.org/passni/sso/spLogin2.php"
        
        logger.info(f"🌐 LearnUs 메인 페이지 접속: {learnus_url}")
        driver.get(learnus_url)
        
        # 페이지 로딩 대기
        logger.info("⏳ 페이지 로딩 대기 중...")
        time.sleep(1.0)  # 로그인 후 안정화 대기 (1초로 단축)
        
        # 스크린샷 저장
        # 스크린샷 제거 (성능 최적화)
        
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
        
        # 1단계: CSS 선택자로 찾기
        for i, selector in enumerate(portal_button_selectors):
            try:
                logger.info(f"   시도 중 ({i+1}/{len(portal_button_selectors)}): {selector}")
                portal_login_button = WebDriverWait(driver, 1).until(  # 타임아웃 단축
                    EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                )
                logger.info(f"✅ 연세포털 로그인 버튼 발견: {selector}")
                break
            except TimeoutException:
                logger.debug(f"   실패: {selector}")
                continue
            except Exception as e:
                logger.debug(f"   예외 발생: {selector} - {e}")
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
                    portal_login_button = WebDriverWait(driver, 1).until(  # 타임아웃 단축
                        EC.element_to_be_clickable((By.XPATH, xpath))
                    )
                    logger.info(f"✅ 연세포털 로그인 버튼 발견 (XPath): {xpath}")
                    break
                except TimeoutException:
                    logger.debug(f"   XPath 실패: {xpath}")
                    continue
                except Exception as e:
                    logger.debug(f"   XPath 예외 발생: {xpath} - {e}")
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
            time.sleep(0.2)  # 대기 시간 대폭 단축
            
            # 스크린샷 저장
            # 스크린샷 제거 (성능 최적화)
            
            # 클릭 후 URL 확인
            current_url = driver.current_url
            logger.info(f"📍 클릭 후 URL: {current_url}")
        else:
            logger.warning("⚠️ 연세포털 로그인 버튼을 찾을 수 없습니다. 직접 로그인 페이지로 이동합니다.")
            logger.info(f"🌐 직접 연세포털 로그인 페이지 접속: {portal_login_url}")
            driver.get(portal_login_url)
            time.sleep(0.2)  # 대기 시간 대폭 단축
            
            # 스크린샷 저장
            # 스크린샷 제거 (성능 최적화)
            
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
            "input[placeholder*='아이디']"
        ]
        
        username_field = None
        for i, selector in enumerate(username_selectors):
            try:
                logger.info(f"   시도 중 ({i+1}/{len(username_selectors)}): {selector}")
                username_field = WebDriverWait(driver, 1).until(  # 타임아웃 단축
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                logger.info(f"✅ 사용자명 필드 발견: {selector}")
                break
            except TimeoutException:
                logger.debug(f"   실패: {selector}")
                continue
            except Exception as e:
                logger.debug(f"   예외 발생: {selector} - {e}")
                continue
        
        if not username_field:
            logger.error("❌ 사용자명 필드를 찾을 수 없습니다")
            return False
        
        # 비밀번호 필드 찾기
        logger.info("🔍 비밀번호 필드 찾는 중...")
        password_selectors = [
            "input[id='loginPasswd']",  # 가장 정확한 선택자 (빠름)
            "input[name='loginPasswd']",  # name 속성
            "input[type='password']",  # 타입 기반
            "input[placeholder*='비밀번호']",
            "input[placeholder*='Password']"
        ]
        
        password_field = None
        for i, selector in enumerate(password_selectors):
            try:
                logger.info(f"   시도 중 ({i+1}/{len(password_selectors)}): {selector}")
                password_field = WebDriverWait(driver, 1).until(  # 타임아웃 단축
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                logger.info(f"✅ 비밀번호 필드 발견: {selector}")
                break
            except TimeoutException:
                logger.debug(f"   실패: {selector}")
                continue
            except Exception as e:
                logger.debug(f"   예외 발생: {selector} - {e}")
                continue
        
        if not password_field:
            logger.error("❌ 비밀번호 필드를 찾을 수 없습니다")
            return False
        
        # 로그인 정보 입력
        logger.info("📝 로그인 정보 입력 중...")
        username_field.clear()
        password_field.clear()
        username_field.send_keys(username)
        password_field.send_keys(password)  
        logger.info("✅ 로그인 정보 입력 완료")
        
        # 스크린샷 저장
        # 스크린샷 제거 (성능 최적화)
        
        # 로그인 버튼 찾기 및 클릭
        logger.info("🔍 로그인 버튼 찾는 중...")
        login_button_selectors = [
            "a[id='loginBtn']",  # 가장 정확한 선택자 (빠름)
            "#loginBtn",  # ID 기반
            "a.submit",  # 클래스 기반
            "button[type='submit']",
            "input[type='submit']",
            ".login-btn",
            "input[value*='로그인']",
            "button[value*='로그인']",
            ".btn-login",
            ".submit-btn"
        ]
        
        login_button = None
        for i, selector in enumerate(login_button_selectors):
            try:
                logger.info(f"   시도 중 ({i+1}/{len(login_button_selectors)}): {selector}")
                login_button = WebDriverWait(driver, 1).until(  # 타임아웃 단축
                    EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                )
                logger.info(f"✅ 로그인 버튼 발견: {selector}")
                break
            except (TimeoutException, NoSuchElementException):
                logger.debug(f"   실패: {selector}")
                continue
            except Exception as e:
                logger.debug(f"   예외 발생: {selector} - {e}")
                continue
        
        if not login_button:
            logger.error("❌ 로그인 버튼을 찾을 수 없습니다")
            return False
        
        # 로그인 버튼 클릭 (재시도 로직 포함)
        logger.info("🖱️ 로그인 버튼 클릭...")
        max_retries = 3
        for attempt in range(max_retries):
            try:
                logger.info(f"   시도 {attempt + 1}/{max_retries}")
                login_button.click()
                time.sleep(1)  # 로그인 처리 대기 (1초로 단축)
                break
            except Exception as e:
                logger.warning(f"   클릭 실패 (시도 {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(2)
                    # 버튼 다시 찾기
                    try:
                        login_button = WebDriverWait(driver, 1).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, login_button_selectors[0]))
                        )
                    except:
                        pass
                else:
                    raise
        
        # 스크린샷 저장
        # 스크린샷 제거 (성능 최적화)
        
        # 로그인 결과 확인
        current_url = driver.current_url
        page_title = driver.title
        logger.info(f"📍 로그인 후 URL: {current_url}")
        logger.info(f"📄 로그인 후 페이지 제목: {page_title}")
        
        # LearnUs 특화 성공 지표 확인
        learnus_success_indicators = [
            ".my-course-lists",  # LearnUs 과목 목록
            ".course-box",  # 과목 박스
            ".course-link",  # 과목 링크
            ".my-course",  # 내 강의
            ".course-list",  # 강의 목록
            "h3",  # 과목명이 있는 h3 태그
            ".course-title",  # 과목 제목
            ".course-name",  # 과목명
            "a[href*='course/view.php']"  # 강의 링크
        ]
        
        success = False
        for indicator in learnus_success_indicators:
            try:
                element = driver.find_element(By.CSS_SELECTOR, indicator)
                if element and element.is_displayed():
                    logger.info(f"✅ LearnUs 성공 지표 발견: {indicator}")
                    success = True
                    break
            except NoSuchElementException:
                continue
        
        # 페이지 제목으로도 확인
        if "LearnUs YONSEI" in page_title:
            logger.info("✅ LearnUs 페이지 제목 확인 - 로그인 성공")
            success = True
        
        # URL 확인
        if "ys.learnus.org" in current_url and "spLogin2.php" not in current_url:
            logger.info("✅ LearnUs 메인 페이지 URL 확인 - 로그인 성공")
            success = True
        
        if success:
            logger.info("🎉 로그인 성공!")
            
            # 3단계: 과목 정보 수집
            logger.info("📚 과목 정보 수집 시작...")
            courses = collect_course_info(driver)
            
            if courses:
                logger.info(f"✅ 총 {len(courses)}개 과목 정보 수집 완료!")
                for i, course in enumerate(courses, 1):
                    logger.info(f"   {i}. {course}")
                
                # 4단계: 이번주 강의 정보 수집
                logger.info("📚 이번주 강의 정보 수집 시작...")
                lectures = collect_this_week_lectures(driver)
                if lectures:
                    logger.info(f"✅ 총 {len(lectures)}개 이번주 강의 활동 수집 완료!")
                    for i, lecture in enumerate(lectures, 1):
                        activity_name = lecture.get('activity', '알 수 없음')
                        activity_type = lecture.get('type', '알 수 없음')
                        course_name = lecture.get('course', '알 수 없음')
                        logger.info(f"   {i}. {course_name} - {activity_name} ({activity_type})")
                else:
                    logger.warning("⚠️ 이번주 강의 정보를 찾을 수 없습니다")
                
                return True
            else:
                logger.warning("⚠️ 과목 정보를 찾을 수 없습니다")
                return False
        else:
            logger.warning("⚠️ 로그인 상태를 확인할 수 없습니다")
            return False
            
    except WebDriverException as e:
        logger.error(f"❌ WebDriver 오류: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ 예상치 못한 오류: {e}")
        return False
    finally:
        if driver:
            logger.info("🔚 드라이버 종료")
            driver.quit()

def test_automation_login(university, username, password, student_id):
    """자동화 로그인 테스트 (백엔드 API 호출)"""
    try:
        logger.info(f"🧪 백엔드 API 자동화 테스트 시작: {university}")
        
        # 백엔드 API 호출
        url = "http://localhost:8000/automation/test-login"
        payload = {
            "university": university,
            "username": username,
            "password": password,
            "student_id": student_id
        }
        
        logger.info(f"📡 API 호출: {url}")
        logger.info(f"📊 요청 데이터: {json.dumps(payload, ensure_ascii=False, indent=2)}")
        
        response = requests.post(
            url,
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=60  # 60초 타임아웃
        )
        
        logger.info(f"📈 응답 상태: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            logger.info("✅ 자동화 테스트 성공!")
            logger.info(f"📋 결과: {json.dumps(result, ensure_ascii=False, indent=2)}")
            return result
        else:
            error = response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
            logger.error(f"❌ 자동화 테스트 실패: {error}")
            return None
            
    except Exception as e:
        logger.error(f"❌ 자동화 테스트 오류: {e}")
        return None

def main():
    """메인 테스트 함수"""
    print("🚀 실제 자동화 테스트 시작")
    print("=" * 50)
    
    # 1. 백엔드 서버 연결 확인
    if not test_backend_connection():
        print("❌ 백엔드 서버가 실행되지 않았습니다.")
        print("💡 해결 방법: cd backend && python run_server.py")
        return
    
    # 2. 사용자 입력 받기
    print("\n📝 자동화 테스트를 위한 정보 입력")
    print("-" * 30)
    
    university_input = input("대학교 (예: 연세대학교) 또는 9887: ").strip()
    
    # 개발자용 꼼수: 9887 입력시 자동 설정
    if university_input == "9887":
        university = "연세대학교"
        username = "2024248012"
        password = "cjm9887@"
        student_id = "2024248012"
        print("🚀 개발자 모드: 연세대학교 자동 설정!")
        print(f"   대학교: {university}")
        print(f"   학번: {username}")
        print(f"   비밀번호: {password}")
        print(f"   학생 ID: {student_id}")
    else:
        university = university_input
        username = input("아이디/학번: ").strip()
        password = input("비밀번호: ").strip()
        student_id = input("학번 (선택사항): ").strip() or username
    
    if not all([university, username, password]):
        print("❌ 필수 정보가 누락되었습니다.")
        return
    
    print(f"\n🔍 입력된 정보:")
    print(f"   대학교: {university}")
    print(f"   아이디: {username}")
    print(f"   학번: {student_id}")
    print(f"   비밀번호: {'*' * len(password)}")
    
    # 3. 테스트 방법 선택
    print("\n🔧 테스트 방법 선택:")
    print("1. 직접 Selenium 테스트 (상세 디버깅)")
    print("2. 백엔드 API 테스트")
    print("3. 둘 다 실행")
    
    choice = input("선택 (1-3): ").strip()
    
    if choice == "1" or choice == "3":
        print(f"\n🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - 직접 Selenium 테스트 시작")
        logger.info("=" * 60)
        logger.info("직접 Selenium 테스트 시작")
        logger.info("=" * 60)
        
        selenium_result = test_direct_selenium(university, username, password, student_id)
        
        if selenium_result:
            print("\n✅ 직접 Selenium 테스트 성공!")
            logger.info("✅ 직접 Selenium 테스트 성공!")
        else:
            print("\n❌ 직접 Selenium 테스트 실패")
            logger.error("❌ 직접 Selenium 테스트 실패")
            print("📋 자세한 로그는 automation_debug.log 파일을 확인하세요")
    
    if choice == "2" or choice == "3":
        print(f"\n🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - 백엔드 API 테스트 시작")
        result = test_automation_login(university, username, password, student_id)
        
        # 4. 결과 분석
        if result:
            if result.get('success'):
                print("\n🎉 백엔드 API 테스트 성공!")
                print(f"📊 수집된 과제 수: {result.get('assignments_count', 0)}개")
                
                if result.get('assignments'):
                    print("\n📋 수집된 과제 목록:")
                    for i, assignment in enumerate(result['assignments'][:5], 1):
                        print(f"   {i}. {assignment.get('title', 'N/A')}")
                        print(f"      강의: {assignment.get('course', 'N/A')}")
                        print(f"      마감: {assignment.get('due_date', 'N/A')}")
                        print(f"      상태: {assignment.get('status', 'N/A')}")
                        print()
            else:
                print("\n❌ 백엔드 API 테스트 실패")
                print(f"💬 오류 메시지: {result.get('message', '알 수 없는 오류')}")
        else:
            print("\n❌ 백엔드 API 테스트 중 오류 발생")
    
    print("\n🏁 테스트 완료")
    print("📋 자세한 로그는 automation_debug.log 파일을 확인하세요")
    print("💾 페이지 소스는 debug_page_source.html 파일을 확인하세요")

if __name__ == "__main__":
    main()
