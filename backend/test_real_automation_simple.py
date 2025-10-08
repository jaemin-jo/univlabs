#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LearnUs 자동화 - 완전히 새로운 단순한 접근 방식
과목별 독립적 처리로 Stale Element 문제 완전 해결
"""

import os
import sys
import time
import logging
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('automation_simple.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

def setup_driver():
    """Chrome 드라이버 설정 (단순화된 버전)"""
    try:
        logger.info("🔧 Chrome 드라이버 설정 중...")
        
        chrome_options = Options()
        
        # 필수 옵션들만 사용
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--remote-debugging-port=0")
        
        # 자동화 감지 우회
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        driver = webdriver.Chrome(options=chrome_options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        logger.info("✅ Chrome 드라이버 설정 완료")
        return driver
        
    except Exception as e:
        logger.error(f"❌ Chrome 드라이버 설정 실패: {e}")
        return None

def login_to_learnus(driver, university, username, password):
    """LearnUs 로그인"""
    try:
        logger.info(f"🔐 LearnUs 로그인 시작: {university}")
        
        # LearnUs 메인 페이지로 이동
        driver.get("https://ys.learnus.org/")
        time.sleep(2)
        
        # 로그인 버튼 클릭
        login_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href*='login']"))
        )
        login_button.click()
        time.sleep(2)
        
        # 사용자명 입력
        username_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "username"))
        )
        username_field.clear()
        username_field.send_keys(username)
        
        # 비밀번호 입력
        password_field = driver.find_element(By.NAME, "password")
        password_field.clear()
        password_field.send_keys(password)
        
        # 로그인 버튼 클릭
        submit_button = driver.find_element(By.CSS_SELECTOR, "input[type='submit']")
        submit_button.click()
        time.sleep(3)
        
        # 로그인 성공 확인
        if "learnus.org" in driver.current_url and "login" not in driver.current_url:
            logger.info("✅ 로그인 성공")
            return True
        else:
            logger.error("❌ 로그인 실패")
            return False
            
    except Exception as e:
        logger.error(f"❌ 로그인 중 오류: {e}")
        return False

def process_single_course(driver, course_name, course_index, university, username, password):
    """단일 과목 처리 (독립적 세션)"""
    try:
        logger.info(f"📖 과목 {course_index}: '{course_name}' 처리 시작...")
        
        # 1단계: 메인 페이지로 이동
        driver.get("https://ys.learnus.org/")
        time.sleep(2)
        
        # 2단계: 과목 찾기 및 클릭
        course_found = False
        course_elements = driver.find_elements(By.CSS_SELECTOR, ".course-title h3")
        
        if len(course_elements) == 0:
            # 다른 선택자들로 재시도
            alternative_selectors = [
                "h3", ".course-box h3", ".course-name h3",
                "a[href*='course/view.php'] h3", ".my-course-lists h3",
                "a[href*='course']", ".card a", ".course-card a"
            ]
            for selector in alternative_selectors:
                course_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if len(course_elements) > 0:
                    break
        
        for i, element in enumerate(course_elements):
            try:
                element_text = element.text.strip()
                if course_name in element_text or element_text in course_name:
                    logger.info(f"   ✅ 과목 '{course_name}' 발견 (인덱스: {i})")
                    element.click()
                    course_found = True
                    break
            except Exception as e:
                logger.warning(f"   ⚠️ 과목 {i+1} 클릭 실패: {e}")
                continue
        
        if not course_found:
            logger.warning(f"   ⚠️ 과목 '{course_name}'을 찾을 수 없음")
            return []
        
        # 3단계: 과목 페이지 로딩 대기
        time.sleep(3)
        
        # 4단계: 강의 활동 수집
        lectures = []
        
        # 강의 섹션 찾기
        try:
            # 다양한 강의 섹션 선택자 시도
            section_selectors = [
                ".course-content .section",
                ".course-content .week",
                ".course-content .topic",
                ".course-content .activity",
                ".course-content .lecture"
            ]
            
            for selector in section_selectors:
                sections = driver.find_elements(By.CSS_SELECTOR, selector)
                if len(sections) > 0:
                    logger.info(f"   📚 {len(sections)}개 섹션 발견")
                    break
            
            # 각 섹션에서 활동 수집
            for section in sections:
                try:
                    section_title = section.find_element(By.CSS_SELECTOR, "h3, h4, .section-title").text.strip()
                    
                    # 활동 요소들 찾기
                    activity_elements = section.find_elements(By.CSS_SELECTOR, "a[href*='mod'], .activity-item, .lecture-item")
                    
                    for activity in activity_elements:
                        try:
                            activity_name = activity.text.strip()
                            activity_url = activity.get_attribute("href")
                            
                            if activity_name and len(activity_name) > 3:
                                lectures.append({
                                    'course': course_name,
                                    'activity': activity_name,
                                    'type': '강의 활동',
                                    'url': activity_url,
                                    'status': '활동 있음'
                                })
                        except Exception as e:
                            continue
                            
                except Exception as e:
                    continue
                    
        except Exception as e:
            logger.warning(f"   ⚠️ 강의 활동 수집 실패: {e}")
        
        # 5단계: 결과 로깅
        if lectures:
            logger.info(f"   ✅ 과목 '{course_name}': {len(lectures)}개 활동 수집 완료")
        else:
            logger.info(f"   📝 과목 '{course_name}': 활동 없음")
            lectures.append({
                'course': course_name,
                'activity': '이번주 강의 활동 없음',
                'type': '정보',
                'url': '',
                'status': '활동 없음'
            })
        
        return lectures
        
    except Exception as e:
        logger.error(f"❌ 과목 '{course_name}' 처리 실패: {e}")
        return []

def test_simple_automation(university, username, password, student_id):
    """단순한 자동화 테스트"""
    driver = None
    try:
        logger.info("=" * 80)
        logger.info("🚀 LearnUs 단순 자동화 시작")
        logger.info(f"   대학: {university}")
        logger.info(f"   사용자명: {username}")
        logger.info(f"   학생ID: {student_id}")
        logger.info("=" * 80)
        
        # 1단계: 드라이버 초기화
        logger.info("🔧 1단계: Chrome 드라이버 초기화...")
        driver = setup_driver()
        if not driver:
            logger.error("❌ Chrome 드라이버 초기화 실패")
            return []
        
        # 2단계: 로그인
        logger.info("🔐 2단계: LearnUs 로그인...")
        if not login_to_learnus(driver, university, username, password):
            logger.error("❌ 로그인 실패")
            return []
        
        # 3단계: 모든 과목명 수집
        logger.info("📋 3단계: 모든 과목명 수집...")
        all_course_names = []
        
        try:
            course_elements = driver.find_elements(By.CSS_SELECTOR, ".course-title h3")
            if len(course_elements) == 0:
                alternative_selectors = [
                    "h3", ".course-box h3", ".course-name h3",
                    "a[href*='course/view.php'] h3", ".my-course-lists h3",
                    "a[href*='course']", ".card a", ".course-card a"
                ]
                for selector in alternative_selectors:
                    course_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    if len(course_elements) > 0:
                        break
            
            for i, element in enumerate(course_elements):
                try:
                    course_name = element.text.strip()
                    if course_name and len(course_name) > 3:
                        all_course_names.append(course_name)
                        logger.info(f"   📖 과목 {i+1}: '{course_name}'")
                except Exception as e:
                    logger.warning(f"   ⚠️ 과목 {i+1} 텍스트 추출 실패: {e}")
            
            logger.info(f"✅ 총 {len(all_course_names)}개 과목명 수집 완료")
            
        except Exception as e:
            logger.error(f"❌ 과목명 수집 실패: {e}")
            return []
        
        # 4단계: 각 과목별 독립적 처리
        logger.info("🔄 4단계: 각 과목별 독립적 처리...")
        all_lectures = []
        
        for course_index, course_name in enumerate(all_course_names):
            try:
                logger.info(f"🔍 과목 {course_index+1}/{len(all_course_names)}: '{course_name}' 처리...")
                
                # 각 과목마다 독립적으로 처리
                course_lectures = process_single_course(driver, course_name, course_index+1, university, username, password)
                if course_lectures:
                    all_lectures.extend(course_lectures)
                    logger.info(f"✅ 과목 {course_index+1}: '{course_name}' 완료 ({len(course_lectures)}개 활동)")
                else:
                    logger.warning(f"⚠️ 과목 {course_index+1}: '{course_name}' 실패")
                    
            except Exception as e:
                logger.error(f"❌ 과목 {course_index+1}: '{course_name}' 오류: {e}")
                continue
        
        # 5단계: 결과 저장
        logger.info("💾 5단계: 결과 저장...")
        try:
            with open('assignment.txt', 'w', encoding='utf-8') as f:
                f.write("📚 LearnUs 과목 및 이번주 강의 활동 목록 (단순 자동화)\n")
                f.write("=" * 60 + "\n\n")
                f.write(f"수집 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"총 수집된 항목 수: {len(all_lectures)}개\n")
                f.write(f"처리된 과목 수: {len(all_course_names)}개\n\n")
                
                if all_lectures:
                    # 과목별로 그룹화
                    course_groups = {}
                    for lecture in all_lectures:
                        course = lecture['course']
                        if course not in course_groups:
                            course_groups[course] = []
                        course_groups[course].append(lecture)
                    
                    # 과목별로 출력
                    for course, lectures in course_groups.items():
                        f.write(f"📖 {course}\n")
                        f.write("-" * 50 + "\n")
                        
                        for lecture in lectures:
                            f.write(f"  • {lecture['activity']} ({lecture['type']}) - {lecture.get('status', '상태 불명')}\n")
                            if lecture['url']:
                                f.write(f"    URL: {lecture['url']}\n")
                            f.write("\n")
                        f.write("\n")
                else:
                    f.write("📝 수집된 활동이 없습니다.\n")
            
            logger.info("✅ 결과 저장 완료: assignment.txt")
            
        except Exception as e:
            logger.error(f"❌ 결과 저장 실패: {e}")
        
        logger.info(f"🎉 단순 자동화 완료: 총 {len(all_lectures)}개 활동 수집")
        return all_lectures
        
    except Exception as e:
        logger.error(f"❌ 단순 자동화 실패: {e}")
        return []
        
    finally:
        if driver:
            try:
                driver.quit()
                logger.info("✅ Chrome 드라이버 종료")
            except:
                pass

if __name__ == "__main__":
    # 테스트 실행
    result = test_simple_automation(
        university="연세대학교",
        username="2024248012",
        password="cjm9887@",
        student_id="2024248012"
    )
    
    print(f"수집된 활동 수: {len(result)}개")
