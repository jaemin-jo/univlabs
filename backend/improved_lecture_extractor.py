#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import logging
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('lecture_extractor.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class LectureExtractor:
    def __init__(self):
        self.driver = None
        self.wait = None
        
    def setup_driver(self):
        """Chrome 드라이버 설정 및 초기화"""
        try:
            chrome_options = Options()
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # User-Agent 설정 (봇 감지 방지)
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # 자동화 감지 방지
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            # 대기 시간 설정
            self.driver.set_page_load_timeout(30)
            self.driver.implicitly_wait(10)
            self.wait = WebDriverWait(self.driver, 10)
            
            logger.info("✅ Chrome 드라이버 초기화 완료")
            return True
            
        except Exception as e:
            logger.error(f"❌ Chrome 드라이버 초기화 실패: {e}")
            return False
    
    def safe_click(self, element):
        """안전한 클릭 (JavaScript 사용)"""
        try:
            self.driver.execute_script("arguments[0].click();", element)
            return True
        except Exception as e:
            logger.warning(f"JavaScript 클릭 실패: {e}")
            try:
                element.click()
                return True
            except Exception as e2:
                logger.error(f"일반 클릭도 실패: {e2}")
                return False
    
    def find_this_week_section(self, soup, course_name):
        """이번주 강의 섹션 찾기 (개선된 방법)"""
        sections = soup.find_all('li', class_='section main')
        logger.info(f"   {course_name}: {len(sections)}개 섹션 발견")
        
        # 각 섹션의 텍스트와 제목 확인
        for idx, section in enumerate(sections):
            try:
                # 섹션 제목 찾기
                section_title = section.find('h3') or section.find('div', class_='section-title')
                if section_title:
                    title_text = section_title.get_text().strip().lower()
                    logger.info(f"   섹션 {idx+1} 제목: {title_text}")
                    
                    # 이번주 강의 관련 키워드 확인
                    if any(keyword in title_text for keyword in [
                        "이번주 강의", "이번주", "current week", "week", "주차", "이번 주"
                    ]):
                        # 강의 개요는 제외
                        if "개요" not in title_text and "overview" not in title_text:
                            logger.info(f"   ✅ '이번주 강의' 섹션 발견: {title_text}")
                            return section
                
                # 섹션 전체 텍스트로도 확인
                section_text = section.get_text().lower()
                if any(keyword in section_text for keyword in [
                    "이번주 강의", "이번주", "current week", "week", "주차"
                ]):
                    if "개요" not in section_text and "overview" not in section_text:
                        logger.info(f"   ✅ '이번주 강의' 섹션 발견 (텍스트): {section_text[:50]}...")
                        return section
                        
            except Exception as e:
                logger.debug(f"   섹션 {idx+1} 분석 실패: {e}")
                continue
        
        # 키워드로 찾지 못했으면 두 번째 섹션 시도 (첫 번째는 보통 강의 개요)
        if len(sections) > 1:
            logger.info(f"   🔍 키워드로 찾지 못함, 두 번째 섹션 사용")
            return sections[1]
        
        # 마지막 수단: 첫 번째 섹션
        if sections:
            logger.info(f"   🔍 첫 번째 섹션 사용")
            return sections[0]
        
        return None
    
    def extract_lecture_activities(self, section, course_name):
        """섹션에서 강의 활동 추출"""
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
    
    def extract_all_lectures(self):
        """모든 과목의 이번주 강의 추출"""
        try:
            logger.info("🔍 이번주 강의 정보 수집 시작...")
            
            # 메인 페이지 소스 가져오기
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # 과목 찾기
            course_elements = soup.find_all('h3')
            logger.info(f"📚 {len(course_elements)}개 과목 발견")
            
            all_lectures = []
            processed_courses = set()
            
            for i, course_element in enumerate(course_elements):
                try:
                    course_name = course_element.get_text().strip()
                    if not course_name or len(course_name) < 3:
                        continue
                    
                    if course_name in processed_courses:
                        continue
                    
                    processed_courses.add(course_name)
                    logger.info(f"\n📖 과목 {i+1}: {course_name}")
                    
                    # 과목 클릭
                    try:
                        course_link = self.driver.find_element(By.XPATH, f"//h3[contains(text(), '{course_name}')]")
                        if self.safe_click(course_link):
                            time.sleep(2)  # 페이지 로딩 대기
                            logger.info(f"   ✅ 과목 페이지 진입")
                        else:
                            logger.warning(f"   ⚠️ 과목 클릭 실패")
                            continue
                    except Exception as e:
                        logger.warning(f"   ⚠️ 과목 클릭 실패: {e}")
                        continue
                    
                    # 현재 페이지 분석
                    current_page_source = self.driver.page_source
                    current_soup = BeautifulSoup(current_page_source, 'html.parser')
                    
                    # 이번주 강의 섹션 찾기
                    this_week_section = self.find_this_week_section(current_soup, course_name)
                    
                    if this_week_section:
                        # 섹션에서 활동 추출
                        course_activities = self.extract_lecture_activities(this_week_section, course_name)
                        
                        if course_activities:
                            all_lectures.extend(course_activities)
                            logger.info(f"   📚 {len(course_activities)}개 활동 발견")
                        else:
                            logger.info(f"   📭 활동 없음")
                    else:
                        logger.info(f"   📭 '이번주 강의' 섹션 없음")
                    
                    # 메인 페이지로 돌아가기
                    try:
                        self.driver.back()
                        time.sleep(1)
                    except:
                        self.driver.get("https://ys.learnus.org/")
                        time.sleep(1)
                        
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
                f.write("📚 이번주 강의 활동 목록\n")
                f.write("=" * 50 + "\n\n")
                f.write(f"수집 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"총 수집된 활동 수: {len(lectures)}개\n\n")
                
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
                        f.write("-" * 40 + "\n")
                        
                        for activity in activities:
                            f.write(f"  • {activity['activity']} ({activity['type']})\n")
                            f.write(f"    URL: {activity['url']}\n\n")
                        
                        f.write("\n")
                else:
                    f.write("❌ 수집된 이번주 강의 활동이 없습니다.\n")
                    f.write("🔍 디버깅 정보:\n")
                    f.write("- 각 과목의 페이지 구조를 확인해보세요.\n")
                    f.write("- 로그 파일(lecture_extractor.log)을 확인해보세요.\n")
                
            logger.info("💾 assignment.txt 파일에 저장 완료")
            return True
            
        except Exception as e:
            logger.error(f"❌ 파일 저장 실패: {e}")
            return False
    
    def run(self):
        """메인 실행 함수"""
        print("🚀 개선된 이번주 강의 추출기")
        print("=" * 50)
        
        if not self.setup_driver():
            return False
        
        try:
            # LearnUs 메인 페이지 접속
            logger.info("🌐 LearnUs 메인 페이지 접속 중...")
            self.driver.get("https://ys.learnus.org/")
            time.sleep(3)
            
            # 이번주 강의 정보 수집
            lectures = self.extract_all_lectures()
            
            # 결과 저장
            if self.save_to_file(lectures):
                print(f"\n✅ 총 {len(lectures)}개 이번주 강의 활동 수집 완료!")
                print("📄 assignment.txt 파일을 확인하세요.")
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
    extractor = LectureExtractor()
    extractor.run()

if __name__ == "__main__":
    main()









