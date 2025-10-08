#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LearnUs 자동화 - 하이브리드 백업 버전 기반 수정
기존 검증된 로직 + 살짝 개선된 Stale Element 처리
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
        logging.FileHandler('automation_hybrid_fixed.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

def setup_driver():
    """Chrome 드라이버 설정 (하이브리드 백업 버전 기반)"""
    try:
        logger.info("🔧 Chrome 드라이버 설정 중...")
        
        chrome_options = Options()
        
        # 필수 옵션들 (하이브리드 백업 버전에서 검증된 것들)
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--remote-debugging-port=0")
        
        # 자동화 감지 우회 (하이브리드 백업 버전에서 검증된 것들)
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
    """LearnUs 로그인 (하이브리드 백업 버전 기반)"""
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

def collect_this_week_lectures_hybrid_fixed(driver, university, username, password):
    """하이브리드 백업 버전 기반 강의 수집 (살짝 개선)"""
    try:
        logger.info("📚 하이브리드 백업 버전 기반 강의 수집 시작...")
        
        # 메인 페이지로 이동
        driver.get("https://ys.learnus.org/")
        time.sleep(2)
        
        # 과목 목록 찾기
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
        
        if len(course_elements) == 0:
            logger.warning("과목을 찾을 수 없습니다.")
            return []
        
        logger.info(f"📚 총 {len(course_elements)}개 과목 발견")
        
        # 과목별 처리
        all_lectures = []
        processed_courses = set()
        current_course_index = 0
        
        while current_course_index < len(course_elements):
            try:
                logger.info(f"🔍 과목 {current_course_index+1}/{len(course_elements)} 처리 시작...")
                
                # 🔧 살짝 개선: Stale Element Reference 방지 강화
                try:
                    # 매번 새로운 요소 찾기로 Stale Element 방지
                    fresh_course_elements = driver.find_elements(By.CSS_SELECTOR, ".course-title h3")
                    if len(fresh_course_elements) == 0:
                        # 다른 선택자들로 재시도
                        alternative_selectors = [
                            "h3", ".course-box h3", ".course-name h3",
                            "a[href*='course/view.php'] h3", ".my-course-lists h3",
                            "a[href*='course']", ".card a", ".course-card a"
                        ]
                        for selector in alternative_selectors:
                            fresh_course_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                            if len(fresh_course_elements) > 0:
                                break

                    if current_course_index >= len(fresh_course_elements):
                        logger.warning(f"과목 {current_course_index+1}을 찾을 수 없음, 건너뜀")
                        current_course_index += 1
                        continue

                    course_element = fresh_course_elements[current_course_index]
                    course_name = course_element.text.strip()

                except Exception as stale_error:
                    logger.warning(f"Stale element 감지, 요소 재찾기: {stale_error}")
                    # 요소 재찾기
                    fresh_course_elements = driver.find_elements(By.CSS_SELECTOR, ".course-title h3")
                    if len(fresh_course_elements) == 0:
                        # 다른 선택자들로 재시도
                        alternative_selectors = [
                            "h3", ".course-box h3", ".course-name h3",
                            "a[href*='course/view.php'] h3", ".my-course-lists h3",
                            "a[href*='course']", ".card a", ".course-card a"
                        ]
                        for selector in alternative_selectors:
                            fresh_course_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                            if len(fresh_course_elements) > 0:
                                break

                    if current_course_index < len(fresh_course_elements):
                        course_element = fresh_course_elements[current_course_index]
                        course_name = course_element.text.strip()
                    else:
                        logger.warning(f"과목 {current_course_index+1}을 재찾을 수 없음, 건너뜀")
                        current_course_index += 1
                        continue
                
                # 과목명 정리
                if not course_name or len(course_name) < 3:
                    logger.info(f"   ⚠️ 과목명이 너무 짧음: '{course_name}' (길이: {len(course_name)})")
                    current_course_index += 1
                    continue
                
                # 중복 과목 처리 방지
                if course_name in processed_courses:
                    logger.info(f"   ⚠️ 중복 과목 건너뜀: '{course_name}' (이미 처리됨)")
                    current_course_index += 1
                    continue
                
                processed_courses.add(course_name)
                logger.info(f"   ✅ 과목 {current_course_index+1}: '{course_name}' 처리 시작")
                
                # 🔧 살짝 개선: 과목 클릭 시 Stale Element 방지 강화
                try:
                    # WebDriverWait를 사용한 안정적인 과목 클릭
                    logger.info(f"   📄 {course_name} 과목 클릭 시작...")
                    
                    # 과목 요소가 클릭 가능할 때까지 대기
                    WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, ".course-title h3"))
                    )
                    
                    # 현재 인덱스에 해당하는 과목 요소를 다시 찾기
                    clickable_elements = driver.find_elements(By.CSS_SELECTOR, ".course-title h3")
                    if current_course_index < len(clickable_elements):
                        clickable_elements[current_course_index].click()
                        logger.info(f"   ✅ {course_name} 과목 클릭 성공")
                    else:
                        logger.warning(f"   ⚠️ {course_name} 과목 클릭 실패 - 인덱스 범위 초과")
                        current_course_index += 1
                        continue
                    
                except Exception as click_error:
                    logger.warning(f"   ⚠️ {course_name} 과목 클릭 실패: {click_error}")
                    current_course_index += 1
                    continue
                
                # 과목 페이지 로딩 대기
                time.sleep(3)
                
                # 🔧 살짝 개선: 강의 활동 수집 로직 강화
                try:
                    # 강의 섹션 찾기
                    sections = driver.find_elements(By.CSS_SELECTOR, ".course-content .section, .course-content .week, .course-content .topic")
                    
                    if len(sections) > 0:
                        logger.info(f"   📚 {len(sections)}개 섹션 발견")
                        
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
                                            all_lectures.append({
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
                    else:
                        logger.info(f"   📝 {course_name}: 강의 섹션 없음")
                        all_lectures.append({
                            'course': course_name,
                            'activity': '이번주 강의 활동 없음',
                            'type': '정보',
                            'url': '',
                            'status': '활동 없음'
                        })
                        
                except Exception as collect_error:
                    logger.warning(f"   ⚠️ {course_name} 강의 활동 수집 실패: {collect_error}")
                    all_lectures.append({
                        'course': course_name,
                        'activity': '이번주 강의 활동 없음',
                        'type': '정보',
                        'url': '',
                        'status': '활동 없음'
                    })
                
                # 🔧 살짝 개선: 메인 페이지 복귀 시 안정성 강화
                try:
                    # 메인 페이지로 돌아가기
                    driver.back()
                    time.sleep(2)
                    logger.info(f"   ✅ {course_name} 메인 페이지 복귀 완료")
                    
                    # 메인 페이지 로딩 확인
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".course-title h3"))
                    )
                    logger.info(f"   ✅ {course_name} 메인 페이지 로딩 확인 완료")
                    
                except Exception as back_error:
                    logger.warning(f"   ⚠️ {course_name} 메인 페이지 복귀 실패: {back_error}")
                    # 메인 페이지로 직접 이동
                    try:
                        driver.get("https://ys.learnus.org/")
                        time.sleep(2)
                        logger.info(f"   ✅ {course_name} 메인 페이지 직접 이동 완료")
                    except Exception as direct_error:
                        logger.error(f"   ❌ {course_name} 메인 페이지 직접 이동 실패: {direct_error}")
                
                # 과목 처리 완료 후 인덱스 증가
                current_course_index += 1
                logger.info(f"   ✅ {course_name} 처리 완료, 다음 과목으로 이동 (인덱스: {current_course_index})")
                
            except Exception as e:
                logger.error(f"❌ 과목 {current_course_index+1} 처리 실패: {e}")
                current_course_index += 1
                continue
        
        logger.info(f"🎉 모든 과목 처리 완료: 총 {len(all_lectures)}개 활동 수집")
        return all_lectures
        
    except Exception as e:
        logger.error(f"❌ 강의 수집 실패: {e}")
        return []

def test_direct_selenium_fixed(university, username, password, student_id):
    """하이브리드 백업 버전 기반 직접 Selenium 테스트"""
    driver = None
    try:
        logger.info("=" * 80)
        logger.info("🚀 LearnUs 하이브리드 백업 버전 자동화 시작")
        logger.info(f"   대학: {university}")
        logger.info(f"   사용자명: {username}")
        logger.info(f"   학생ID: {student_id}")
        logger.info("=" * 80)
        
        # Chrome 드라이버 초기화
        driver = setup_driver()
        if not driver:
            logger.error("❌ Chrome 드라이버 초기화 실패")
            return []
        
        # 로그인
        if not login_to_learnus(driver, university, username, password):
            logger.error("❌ 로그인 실패")
            return []
        
        # 강의 수집
        lectures = collect_this_week_lectures_hybrid_fixed(driver, university, username, password)
        
        # 결과 저장
        try:
            with open('assignment.txt', 'w', encoding='utf-8') as f:
                f.write("📚 LearnUs 과목 및 이번주 강의 활동 목록 (하이브리드 백업 버전)\n")
                f.write("=" * 60 + "\n\n")
                f.write(f"수집 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"총 수집된 항목 수: {len(lectures)}개\n\n")
                
                if lectures:
                    # 과목별로 그룹화
                    course_groups = {}
                    for lecture in lectures:
                        course = lecture['course']
                        if course not in course_groups:
                            course_groups[course] = []
                        course_groups[course].append(lecture)
                    
                    # 과목별로 출력
                    for course, course_lectures in course_groups.items():
                        f.write(f"📖 {course}\n")
                        f.write("-" * 50 + "\n")
                        
                        for lecture in course_lectures:
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
        
        logger.info(f"🎉 하이브리드 백업 버전 자동화 완료: 총 {len(lectures)}개 활동 수집")
        return lectures
        
    except Exception as e:
        logger.error(f"❌ 하이브리드 백업 버전 자동화 실패: {e}")
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
    result = test_direct_selenium_fixed(
        university="연세대학교",
        username="2024248012",
        password="cjm9887@",
        student_id="2024248012"
    )
    
    print(f"수집된 활동 수: {len(result)}개")