#!/usr/bin/env python3
"""
상태 확인 최적화 모듈
- 한 번에 모든 활동의 완료 상태 확인
- 페이지 이동 최소화
- 상태 확인 시간 단축
"""

import logging
import time
from typing import List, Dict, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class StatusOptimizer:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)
        
    def get_all_completion_statuses(self, activities):
        """모든 활동의 완료 상태를 한 번에 확인"""
        try:
            logger.info(f"🔍 {len(activities)}개 활동의 완료 상태 확인 시작...")
            
            # 메인 페이지에서 모든 완료 상태 아이콘 수집
            completion_data = self.collect_all_completion_icons()
            
            # 각 활동의 상태 매핑
            for activity in activities:
                activity_url = activity.get('url', '')
                if activity_url:
                    # URL에서 활동 ID 추출
                    activity_id = self.extract_activity_id(activity_url)
                    if activity_id:
                        # 완료 상태 확인
                        status = self.get_completion_status_from_data(completion_data, activity_id)
                        activity['status'] = status
                    else:
                        activity['status'] = '❓ 상태 확인 불가'
                else:
                    activity['status'] = '❓ URL 없음'
            
            logger.info("✅ 모든 활동의 완료 상태 확인 완료")
            return activities
            
        except Exception as e:
            logger.error(f"❌ 상태 확인 실패: {e}")
            return activities
    
    def collect_all_completion_icons(self):
        """메인 페이지에서 모든 완료 상태 아이콘 수집"""
        try:
            completion_data = {
                'completed': [],
                'incomplete': [],
                'unknown': []
            }
            
            # 완료된 활동 아이콘 찾기
            completed_selectors = [
                "//span[@class='autocompletion']//img[@class='icon' and contains(@title, '완료함')]",
                "//span[@class='autocompletion']//img[@class='icon' and contains(@alt, '완료함')]",
                "//span[@class='autocompletion']//img[@class='icon' and contains(@src, 'completion-auto-y')]",
                "//img[@class='icon' and contains(@title, '완료함')]",
                "//img[@class='icon' and contains(@src, 'completion-auto-y')]"
            ]
            
            for selector in completed_selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    for element in elements:
                        # 부모 요소에서 활동 ID 추출
                        activity_id = self.extract_activity_id_from_element(element)
                        if activity_id:
                            completion_data['completed'].append(activity_id)
                except:
                    continue
            
            # 미완료 활동 아이콘 찾기
            incomplete_selectors = [
                "//span[@class='autocompletion']//img[@class='icon' and contains(@title, '완료하지 못함')]",
                "//span[@class='autocompletion']//img[@class='icon' and contains(@alt, '완료하지 못함')]",
                "//span[@class='autocompletion']//img[@class='icon' and contains(@src, 'completion-auto-n')]",
                "//img[@class='icon' and contains(@title, '완료하지 못함')]",
                "//img[@class='icon' and contains(@src, 'completion-auto-n')]"
            ]
            
            for selector in incomplete_selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    for element in elements:
                        # 부모 요소에서 활동 ID 추출
                        activity_id = self.extract_activity_id_from_element(element)
                        if activity_id:
                            completion_data['incomplete'].append(activity_id)
                except:
                    continue
            
            logger.info(f"📊 완료 상태 아이콘 수집 완료:")
            logger.info(f"   완료: {len(completion_data['completed'])}개")
            logger.info(f"   미완료: {len(completion_data['incomplete'])}개")
            
            return completion_data
            
        except Exception as e:
            logger.error(f"❌ 완료 상태 아이콘 수집 실패: {e}")
            return {'completed': [], 'incomplete': [], 'unknown': []}
    
    def extract_activity_id(self, activity_url):
        """활동 URL에서 활동 ID 추출"""
        try:
            if "id=" in activity_url:
                return activity_url.split("id=")[1].split("&")[0]
            return None
        except:
            return None
    
    def extract_activity_id_from_element(self, element):
        """요소에서 활동 ID 추출"""
        try:
            # 부모 요소에서 ID 찾기
            parent_li = element.find_element(By.XPATH, "./ancestor::li[contains(@id, 'module-')]")
            if parent_li:
                li_id = parent_li.get_attribute('id')
                if 'module-' in li_id:
                    return li_id.replace('module-', '')
            return None
        except:
            return None
    
    def get_completion_status_from_data(self, completion_data, activity_id):
        """수집된 데이터에서 특정 활동의 완료 상태 확인"""
        try:
            if activity_id in completion_data['completed']:
                return "✅ 완료"
            elif activity_id in completion_data['incomplete']:
                return "❌ 해야 할 과제"
            else:
                return "⏳ 대기 중"
        except:
            return "❓ 상태 확인 불가"
    
    def optimize_activity_extraction(self, soup, course_name):
        """활동 추출 최적화 (페이지 이동 없이)"""
        try:
            activities = []
            
            # 이번주 강의 섹션 찾기
            this_week_section = self.find_this_week_section_optimized(soup)
            if not this_week_section:
                return activities
            
            # 활동 링크 찾기
            activity_links = this_week_section.find_all('a', href=True)
            
            for link in activity_links:
                try:
                    activity_name = link.get_text().strip()
                    activity_url = link.get('href', '')
                    
                    if not activity_name or not activity_url:
                        continue
                    
                    # 활동 타입 판별
                    activity_type = self.determine_activity_type(activity_url)
                    
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
            logger.error(f"❌ 활동 추출 최적화 실패: {e}")
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
    
    def determine_activity_type(self, activity_url):
        """활동 타입 판별"""
        if "mod/assign/" in activity_url:
            return "과제"
        elif "mod/vod/" in activity_url:
            return "동영상"
        elif "mod/resource/" in activity_url or "mod/ubfile/" in activity_url:
            return "PDF 자료"
        elif "mod/ubboard/" in activity_url:
            return "게시판"
        elif "mod/quiz/" in activity_url:
            return "퀴즈"
        elif "mod/forum/" in activity_url:
            return "토론"
        elif "mod/lesson/" in activity_url:
            return "강의"
        elif "mod/page/" in activity_url:
            return "페이지"
        else:
            return "기타"
    
    def batch_status_check(self, all_activities):
        """배치 상태 확인 (모든 활동을 한 번에)"""
        try:
            logger.info(f"🔍 {len(all_activities)}개 활동의 배치 상태 확인 시작...")
            
            # 메인 페이지에서 모든 완료 상태 수집
            completion_data = self.collect_all_completion_icons()
            
            # 각 활동의 상태 업데이트
            for activity in all_activities:
                activity_url = activity.get('url', '')
                if activity_url:
                    activity_id = self.extract_activity_id(activity_url)
                    if activity_id:
                        status = self.get_completion_status_from_data(completion_data, activity_id)
                        activity['status'] = status
                    else:
                        activity['status'] = '❓ 상태 확인 불가'
                else:
                    activity['status'] = '❓ URL 없음'
            
            logger.info("✅ 배치 상태 확인 완료")
            return all_activities
            
        except Exception as e:
            logger.error(f"❌ 배치 상태 확인 실패: {e}")
            return all_activities

def optimize_automation_with_status_check(driver, activities):
    """상태 확인 최적화를 적용한 자동화"""
    try:
        optimizer = StatusOptimizer(driver)
        
        # 모든 활동의 상태를 한 번에 확인
        optimized_activities = optimizer.batch_status_check(activities)
        
        return optimized_activities
        
    except Exception as e:
        logger.error(f"❌ 상태 확인 최적화 실패: {e}")
        return activities
