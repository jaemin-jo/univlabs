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
        logging.FileHandler('lecture_debug.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def extract_this_week_lectures(driver):
    """각 과목의 '이번주 강의' 섹션만 추출"""
    try:
        logger.info("🔍 각 과목의 '이번주 강의' 정보 수집 중...")
        
        # 현재 페이지의 HTML 소스 가져오기
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        
        # h3 태그로 과목 찾기
        course_elements = soup.find_all('h3')
        logger.info(f"   h3 태그 {len(course_elements)}개 발견")
        
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
                logger.info(f"   과목 {i+1}: {course_name} 처리 중...")
                
                # Selenium으로 과목 클릭
                try:
                    selenium_course_element = driver.find_element(By.XPATH, f"//h3[contains(text(), '{course_name}')]")
                    selenium_course_element.click()
                    time.sleep(1)
                    logger.info(f"   ✅ {course_name} 과목 페이지 진입")
                except Exception as e:
                    logger.warning(f"   ⚠️ {course_name} 과목 클릭 실패: {e}")
                    continue
                
                # BeautifulSoup으로 현재 페이지 분석
                try:
                    current_page_source = driver.page_source
                    current_soup = BeautifulSoup(current_page_source, 'html.parser')
                    
                    # "이번주 강의" 섹션 찾기
                    this_week_section = None
                    
                    # 모든 섹션 찾기
                    sections = current_soup.find_all('li', class_='section main')
                    logger.info(f"   {course_name}에서 {len(sections)}개 섹션 발견")
                    
                    # 각 섹션의 텍스트 확인
                    for idx, section in enumerate(sections):
                        section_text = section.get_text().lower()
                        logger.info(f"   섹션 {idx+1}: {section_text[:100]}...")
                        
                        # "이번주 강의" 키워드가 있는 섹션 찾기
                        if any(keyword in section_text for keyword in [
                            "이번주 강의", "이번주", "current week", "week", "주차"
                        ]):
                            # "강의 개요"는 제외
                            if "개요" not in section_text and "overview" not in section_text:
                                this_week_section = section
                                logger.info(f"   ✅ '이번주 강의' 섹션 발견: 섹션 {idx+1}")
                                break
                    
                    # 키워드로 찾지 못했으면 두 번째 섹션 시도
                    if not this_week_section and len(sections) > 1:
                        this_week_section = sections[1]  # 두 번째 섹션
                        logger.info(f"   🔍 키워드로 찾지 못함, 두 번째 섹션 사용")
                    
                    if this_week_section:
                        logger.info(f"   ✅ {course_name}에서 '이번주 강의' 섹션 발견")
                        
                        # 섹션 내의 모든 활동 링크 찾기
                        activity_links = this_week_section.find_all('a', href=True)
                        logger.info(f"   {len(activity_links)}개 링크 발견")
                        
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
                
            logger.info("💾 이번주 강의 정보가 assignment.txt 파일에 저장되었습니다")
        except Exception as e:
            logger.error(f"❌ 파일 저장 실패: {e}")
        
        return all_lectures
        
    except Exception as e:
        logger.error(f"❌ 이번주 강의 정보 수집 오류: {e}")
        return []

def main():
    """메인 함수"""
    print("🚀 간단한 이번주 강의 추출기")
    print("=" * 50)
    
    # Chrome 드라이버 설정
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        driver.set_page_load_timeout(30)
        driver.implicitly_wait(10)
        
        logger.info("✅ Chrome 드라이버 초기화 완료")
    except Exception as e:
        logger.error(f"❌ Chrome 드라이버 초기화 실패: {e}")
        return
    
    try:
        # LearnUs 메인 페이지 접속
        learnus_url = "https://ys.learnus.org/"
        logger.info(f"🌐 LearnUs 메인 페이지 접속: {learnus_url}")
        driver.get(learnus_url)
        time.sleep(2)
        
        # 이번주 강의 정보 수집
        lectures = extract_this_week_lectures(driver)
        
        if lectures:
            print(f"\n✅ 총 {len(lectures)}개 이번주 강의 활동 수집 완료!")
            print("📄 assignment.txt 파일을 확인하세요.")
        else:
            print("\n❌ 이번주 강의 활동을 찾을 수 없습니다.")
            print("📋 자세한 로그는 lecture_debug.log 파일을 확인하세요.")
        
    except Exception as e:
        logger.error(f"❌ 실행 오류: {e}")
    finally:
        try:
            driver.quit()
            logger.info("🔚 드라이버 종료")
        except:
            pass

if __name__ == "__main__":
    main()






















