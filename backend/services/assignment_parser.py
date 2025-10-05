"""
과제 정보 파싱 서비스
Selenium으로 수집한 HTML에서 과제 정보 추출
"""

import logging
from datetime import datetime, timedelta
from typing import List, Optional
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from models.assignment import Assignment, AssignmentStatus, AssignmentPriority

logger = logging.getLogger(__name__)

class AssignmentParser:
    def __init__(self):
        self.assignment_selectors = {
            "연세대학교": {
                "assignment_list": ".assignment-list",
                "assignment_item": ".assignment-item",
                "title": ".assignment-title",
                "description": ".assignment-description",
                "due_date": ".due-date",
                "course_name": ".course-name",
                "course_code": ".course-code",
                "status": ".assignment-status",
            },
            "고려대학교": {
                "assignment_list": ".task-list",
                "assignment_item": ".task-item",
                "title": ".task-title",
                "description": ".task-description",
                "due_date": ".deadline",
                "course_name": ".subject-name",
                "course_code": ".subject-code",
                "status": ".task-status",
            },
            "서울대학교": {
                "assignment_list": ".content-list",
                "assignment_item": ".content-item",
                "title": ".content-title",
                "description": ".content-description",
                "due_date": ".due-date",
                "course_name": ".course-name",
                "course_code": ".course-code",
                "status": ".content-status",
            },
        }
    
    async def parse_assignments(self, driver: WebDriver, university: str, student_id: str) -> List[Assignment]:
        """과제 정보 파싱"""
        try:
            logger.info(f"{university} 과제 정보 파싱 시작...")
            
            # 대학교별 선택자 가져오기
            selectors = self.assignment_selectors.get(university)
            if not selectors:
                logger.error(f"지원하지 않는 대학교: {university}")
                return []
            
            # 과제 목록 요소 찾기
            try:
                assignment_list = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selectors["assignment_list"]))
                )
            except TimeoutException:
                logger.warning("과제 목록을 찾을 수 없습니다. 대체 방법 시도...")
                return await self._parse_assignments_fallback(driver, university, student_id)
            
            # 과제 아이템들 찾기
            assignment_items = assignment_list.find_elements(By.CSS_SELECTOR, selectors["assignment_item"])
            logger.info(f"과제 아이템 {len(assignment_items)}개 발견")
            
            assignments = []
            for i, item in enumerate(assignment_items):
                try:
                    assignment = await self._parse_single_assignment(item, selectors, university, student_id, i)
                    if assignment:
                        assignments.append(assignment)
                except Exception as e:
                    logger.error(f"과제 {i} 파싱 오류: {e}")
                    continue
            
            logger.info(f"과제 파싱 완료: {len(assignments)}개")
            return assignments
            
        except Exception as e:
            logger.error(f"과제 파싱 오류: {e}")
            return []
    
    async def _parse_single_assignment(self, item, selectors: dict, university: str, student_id: str, index: int) -> Optional[Assignment]:
        """단일 과제 정보 파싱"""
        try:
            # 제목 추출
            title_element = item.find_element(By.CSS_SELECTOR, selectors["title"])
            title = title_element.text.strip()
            
            # 설명 추출
            try:
                description_element = item.find_element(By.CSS_SELECTOR, selectors["description"])
                description = description_element.text.strip()
            except NoSuchElementException:
                description = ""
            
            # 마감일 추출
            try:
                due_date_element = item.find_element(By.CSS_SELECTOR, selectors["due_date"])
                due_date_text = due_date_element.text.strip()
                due_date = self._parse_due_date(due_date_text)
            except NoSuchElementException:
                due_date = datetime.now() + timedelta(days=7)  # 기본값
            
            # 과목명 추출
            try:
                course_name_element = item.find_element(By.CSS_SELECTOR, selectors["course_name"])
                course_name = course_name_element.text.strip()
            except NoSuchElementException:
                course_name = "알 수 없는 과목"
            
            # 과목 코드 추출
            try:
                course_code_element = item.find_element(By.CSS_SELECTOR, selectors["course_code"])
                course_code = course_code_element.text.strip()
            except NoSuchElementException:
                course_code = f"COURSE_{index}"
            
            # 상태 추출
            try:
                status_element = item.find_element(By.CSS_SELECTOR, selectors["status"])
                status_text = status_element.text.strip()
                status = self._parse_status(status_text)
            except NoSuchElementException:
                status = AssignmentStatus.pending
            
            # 우선순위 결정
            priority = self._determine_priority(due_date, status)
            
            # 과제 ID 생성
            assignment_id = f"{university}_{student_id}_{index}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            # 태그 생성
            tags = self._generate_tags(title, description, course_name)
            
            # 새로운 과제 여부 확인
            is_new = self._is_new_assignment(due_date)
            
            # 마감 임박 여부 확인
            is_upcoming = self._is_upcoming_assignment(due_date)
            
            assignment = Assignment(
                id=assignment_id,
                title=title,
                description=description,
                course_name=course_name,
                course_code=course_code,
                due_date=due_date,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                status=status,
                priority=priority,
                tags=tags,
                is_new=is_new,
                is_upcoming=is_upcoming,
                university=university,
                student_id=student_id,
            )
            
            return assignment
            
        except Exception as e:
            logger.error(f"단일 과제 파싱 오류: {e}")
            return None
    
    async def _parse_assignments_fallback(self, driver: WebDriver, university: str, student_id: str) -> List[Assignment]:
        """대체 방법으로 과제 정보 파싱"""
        try:
            logger.info("대체 방법으로 과제 정보 파싱 시도...")
            
            # 일반적인 선택자들로 시도
            fallback_selectors = [
                ".assignment",
                ".task",
                ".homework",
                ".project",
                ".assignment-item",
                ".task-item",
                ".content-item",
                "tr[class*='assignment']",
                "div[class*='assignment']",
            ]
            
            assignments = []
            for selector in fallback_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        logger.info(f"대체 선택자 '{selector}'로 {len(elements)}개 요소 발견")
                        
                        for i, element in enumerate(elements):
                            try:
                                # 기본 정보 추출
                                title = self._extract_text_safely(element, [
                                    ".title", ".name", ".subject", "h1", "h2", "h3", "h4"
                                ])
                                
                                if not title:
                                    continue
                                
                                description = self._extract_text_safely(element, [
                                    ".description", ".content", ".detail", ".summary"
                                ])
                                
                                due_date_text = self._extract_text_safely(element, [
                                    ".due-date", ".deadline", ".date", ".time"
                                ])
                                
                                due_date = self._parse_due_date(due_date_text) if due_date_text else datetime.now() + timedelta(days=7)
                                
                                # 과제 객체 생성
                                assignment_id = f"{university}_{student_id}_fallback_{i}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
                                
                                assignment = Assignment(
                                    id=assignment_id,
                                    title=title,
                                    description=description or "",
                                    course_name="알 수 없는 과목",
                                    course_code=f"COURSE_{i}",
                                    due_date=due_date,
                                    created_at=datetime.now(),
                                    updated_at=datetime.now(),
                                    status=AssignmentStatus.pending,
                                    priority=AssignmentPriority.medium,
                                    tags=self._generate_tags(title, description or "", "알 수 없는 과목"),
                                    is_new=self._is_new_assignment(due_date),
                                    is_upcoming=self._is_upcoming_assignment(due_date),
                                    university=university,
                                    student_id=student_id,
                                )
                                
                                assignments.append(assignment)
                                
                            except Exception as e:
                                logger.error(f"대체 방법 과제 {i} 파싱 오류: {e}")
                                continue
                        
                        break  # 성공한 선택자에서 중단
                        
                except Exception as e:
                    logger.error(f"대체 선택자 '{selector}' 시도 오류: {e}")
                    continue
            
            logger.info(f"대체 방법으로 {len(assignments)}개 과제 파싱 완료")
            return assignments
            
        except Exception as e:
            logger.error(f"대체 방법 파싱 오류: {e}")
            return []
    
    def _extract_text_safely(self, element, selectors: List[str]) -> str:
        """안전하게 텍스트 추출"""
        for selector in selectors:
            try:
                sub_element = element.find_element(By.CSS_SELECTOR, selector)
                text = sub_element.text.strip()
                if text:
                    return text
            except NoSuchElementException:
                continue
        return ""
    
    def _parse_due_date(self, date_text: str) -> datetime:
        """마감일 텍스트를 datetime으로 변환"""
        try:
            # 다양한 날짜 형식 처리
            date_formats = [
                "%Y-%m-%d %H:%M",
                "%Y-%m-%d",
                "%m/%d/%Y %H:%M",
                "%m/%d/%Y",
                "%Y.%m.%d %H:%M",
                "%Y.%m.%d",
                "%m월 %d일 %H:%M",
                "%m월 %d일",
                "%Y년 %m월 %d일 %H:%M",
                "%Y년 %m월 %d일",
            ]
            
            for date_format in date_formats:
                try:
                    return datetime.strptime(date_text, date_format)
                except ValueError:
                    continue
            
            # 파싱 실패 시 기본값
            return datetime.now() + timedelta(days=7)
            
        except Exception as e:
            logger.error(f"날짜 파싱 오류: {e}")
            return datetime.now() + timedelta(days=7)
    
    def _parse_status(self, status_text: str) -> AssignmentStatus:
        """상태 텍스트를 AssignmentStatus로 변환"""
        status_text = status_text.lower()
        
        if "완료" in status_text or "submitted" in status_text:
            return AssignmentStatus.submitted
        elif "진행" in status_text or "in progress" in status_text:
            return AssignmentStatus.inProgress
        elif "채점" in status_text or "graded" in status_text:
            return AssignmentStatus.graded
        elif "지남" in status_text or "overdue" in status_text:
            return AssignmentStatus.overdue
        else:
            return AssignmentStatus.pending
    
    def _determine_priority(self, due_date: datetime, status: AssignmentStatus) -> AssignmentPriority:
        """우선순위 결정"""
        if status == AssignmentStatus.overdue:
            return AssignmentPriority.high
        
        days_until_due = (due_date - datetime.now()).days
        
        if days_until_due <= 1:
            return AssignmentPriority.high
        elif days_until_due <= 3:
            return AssignmentPriority.medium
        else:
            return AssignmentPriority.low
    
    def _generate_tags(self, title: str, description: str, course_name: str) -> List[str]:
        """태그 생성"""
        tags = []
        
        # 제목에서 키워드 추출
        title_keywords = ["과제", "프로젝트", "시험", "퀴즈", "보고서", "발표", "실습"]
        for keyword in title_keywords:
            if keyword in title:
                tags.append(keyword)
        
        # 과목명에서 키워드 추출
        if course_name and course_name != "알 수 없는 과목":
            tags.append(course_name)
        
        # 기본 태그
        if not tags:
            tags.append("과제")
        
        return tags
    
    def _is_new_assignment(self, due_date: datetime) -> bool:
        """새로운 과제 여부 확인 (7일 이내 생성)"""
        return (due_date - datetime.now()).days <= 7
    
    def _is_upcoming_assignment(self, due_date: datetime) -> bool:
        """마감 임박 과제 여부 확인 (3일 이내)"""
        days_until_due = (due_date - datetime.now()).days
        return 0 <= days_until_due <= 3
