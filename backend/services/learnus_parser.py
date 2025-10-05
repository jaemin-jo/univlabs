"""
연세대학교 LearnUs 전용 파서
LearnUs 사이트의 특수한 구조에 맞춘 과제 정보 파싱
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

class LearnUsParser:
    def __init__(self):
        self.learnus_selectors = {
            # LearnUs 메인 페이지 선택자
            "course_list": ".course-list, .my-courses, .enrolled-courses",
            "course_item": ".course-item, .course-card, .course-tile",
            "course_title": ".course-title, .course-name, h3, h4",
            "course_link": "a[href*='course']",
            
            # 과제 관련 선택자
            "assignment_section": ".assignments, .tasks, .homework",
            "assignment_list": ".assignment-list, .task-list, .homework-list",
            "assignment_item": ".assignment-item, .task-item, .homework-item",
            "assignment_title": ".assignment-title, .task-title, .homework-title",
            "assignment_description": ".assignment-description, .task-description",
            "assignment_due_date": ".due-date, .deadline, .due-time",
            "assignment_status": ".assignment-status, .task-status, .submission-status",
            
            # 강의 정보 선택자
            "course_info": ".course-info, .course-details",
            "course_name": ".course-name, .subject-name",
            "course_code": ".course-code, .subject-code, .course-id",
            "instructor": ".instructor, .professor, .teacher",
            
            # 공지사항 선택자
            "announcement_list": ".announcements, .notices, .news",
            "announcement_item": ".announcement-item, .notice-item, .news-item",
            "announcement_title": ".announcement-title, .notice-title, .news-title",
            "announcement_date": ".announcement-date, .notice-date, .news-date",
        }
    
    async def parse_learnus_assignments(self, driver: WebDriver, student_id: str) -> List[Assignment]:
        """LearnUs에서 과제 정보 파싱"""
        try:
            logger.info("LearnUs 과제 정보 파싱 시작...")
            
            # 먼저 강의 목록 페이지로 이동
            await self._navigate_to_courses(driver)
            
            # 각 강의에서 과제 정보 수집
            assignments = []
            course_links = await self._get_course_links(driver)
            
            for course_link in course_links:
                try:
                    course_assignments = await self._parse_course_assignments(driver, course_link, student_id)
                    assignments.extend(course_assignments)
                except Exception as e:
                    logger.error(f"강의 과제 파싱 오류: {e}")
                    continue
            
            logger.info(f"LearnUs 과제 파싱 완료: {len(assignments)}개")
            return assignments
            
        except Exception as e:
            logger.error(f"LearnUs 과제 파싱 오류: {e}")
            return []
    
    async def _navigate_to_courses(self, driver: WebDriver):
        """강의 목록 페이지로 이동"""
        try:
            # LearnUs 메인 페이지에서 강의 목록 찾기
            course_selectors = [
                "a[href*='course']",
                "a[href*='class']",
                "a[href*='subject']",
                ".course-link",
                ".class-link",
            ]
            
            for selector in course_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        logger.info(f"강의 링크 {len(elements)}개 발견: {selector}")
                        break
                except Exception as e:
                    logger.debug(f"선택자 {selector} 시도 실패: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"강의 목록 이동 오류: {e}")
    
    async def _get_course_links(self, driver: WebDriver) -> List[str]:
        """강의 링크 목록 가져오기"""
        course_links = []
        
        try:
            # 다양한 선택자로 강의 링크 찾기
            link_selectors = [
                "a[href*='course']",
                "a[href*='class']",
                "a[href*='subject']",
                ".course-link",
                ".class-link",
                ".subject-link",
            ]
            
            for selector in link_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        href = element.get_attribute('href')
                        if href and href not in course_links:
                            course_links.append(href)
                    
                    if course_links:
                        logger.info(f"강의 링크 {len(course_links)}개 발견")
                        break
                        
                except Exception as e:
                    logger.debug(f"선택자 {selector} 시도 실패: {e}")
                    continue
            
            return course_links[:10]  # 최대 10개 강의만 처리
            
        except Exception as e:
            logger.error(f"강의 링크 수집 오류: {e}")
            return []
    
    async def _parse_course_assignments(self, driver: WebDriver, course_url: str, student_id: str) -> List[Assignment]:
        """특정 강의의 과제 정보 파싱"""
        assignments = []
        
        try:
            # 강의 페이지로 이동
            driver.get(course_url)
            await self._wait_for_page_load(driver)
            
            # 강의 정보 추출
            course_info = await self._extract_course_info(driver)
            
            # 과제 섹션 찾기
            assignment_sections = await self._find_assignment_sections(driver)
            
            for section in assignment_sections:
                try:
                    section_assignments = await self._parse_assignment_section(
                        driver, section, course_info, student_id
                    )
                    assignments.extend(section_assignments)
                except Exception as e:
                    logger.error(f"과제 섹션 파싱 오류: {e}")
                    continue
            
            return assignments
            
        except Exception as e:
            logger.error(f"강의 과제 파싱 오류: {e}")
            return []
    
    async def _extract_course_info(self, driver: WebDriver) -> dict:
        """강의 정보 추출"""
        course_info = {
            'name': '알 수 없는 강의',
            'code': 'UNKNOWN',
            'instructor': '알 수 없음',
        }
        
        try:
            # 강의명 추출
            title_selectors = [
                "h1", "h2", "h3", ".course-title", ".class-title", ".subject-title",
                ".page-title", ".main-title", ".course-name", ".class-name"
            ]
            
            for selector in title_selectors:
                try:
                    element = driver.find_element(By.CSS_SELECTOR, selector)
                    if element.text.strip():
                        course_info['name'] = element.text.strip()
                        break
                except NoSuchElementException:
                    continue
            
            # 강의 코드 추출
            code_selectors = [
                ".course-code", ".class-code", ".subject-code", ".course-id",
                ".class-id", ".subject-id", ".course-number", ".class-number"
            ]
            
            for selector in code_selectors:
                try:
                    element = driver.find_element(By.CSS_SELECTOR, selector)
                    if element.text.strip():
                        course_info['code'] = element.text.strip()
                        break
                except NoSuchElementException:
                    continue
            
            # 교수명 추출
            instructor_selectors = [
                ".instructor", ".professor", ".teacher", ".lecturer",
                ".course-instructor", ".class-instructor"
            ]
            
            for selector in instructor_selectors:
                try:
                    element = driver.find_element(By.CSS_SELECTOR, selector)
                    if element.text.strip():
                        course_info['instructor'] = element.text.strip()
                        break
                except NoSuchElementException:
                    continue
            
        except Exception as e:
            logger.error(f"강의 정보 추출 오류: {e}")
        
        return course_info
    
    async def _find_assignment_sections(self, driver: WebDriver) -> List:
        """과제 섹션 찾기"""
        sections = []
        
        try:
            # 과제 관련 섹션 찾기
            section_selectors = [
                ".assignments", ".tasks", ".homework", ".assignments-section",
                ".task-section", ".homework-section", ".assignment-list",
                ".task-list", ".homework-list", "[class*='assignment']",
                "[class*='task']", "[class*='homework']"
            ]
            
            for selector in section_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    sections.extend(elements)
                    if elements:
                        logger.info(f"과제 섹션 {len(elements)}개 발견: {selector}")
                except Exception as e:
                    logger.debug(f"선택자 {selector} 시도 실패: {e}")
                    continue
            
            return sections
            
        except Exception as e:
            logger.error(f"과제 섹션 찾기 오류: {e}")
            return []
    
    async def _parse_assignment_section(self, driver: WebDriver, section, course_info: dict, student_id: str) -> List[Assignment]:
        """과제 섹션에서 과제 정보 파싱"""
        assignments = []
        
        try:
            # 과제 아이템들 찾기
            item_selectors = [
                ".assignment-item", ".task-item", ".homework-item",
                ".assignment", ".task", ".homework", "li", ".item",
                "[class*='assignment']", "[class*='task']", "[class*='homework']"
            ]
            
            assignment_items = []
            for selector in item_selectors:
                try:
                    items = section.find_elements(By.CSS_SELECTOR, selector)
                    if items:
                        assignment_items = items
                        logger.info(f"과제 아이템 {len(items)}개 발견: {selector}")
                        break
                except Exception as e:
                    logger.debug(f"선택자 {selector} 시도 실패: {e}")
                    continue
            
            # 각 과제 아이템 파싱
            for i, item in enumerate(assignment_items):
                try:
                    assignment = await self._parse_single_assignment(item, course_info, student_id, i)
                    if assignment:
                        assignments.append(assignment)
                except Exception as e:
                    logger.error(f"과제 {i} 파싱 오류: {e}")
                    continue
            
            return assignments
            
        except Exception as e:
            logger.error(f"과제 섹션 파싱 오류: {e}")
            return []
    
    async def _parse_single_assignment(self, item, course_info: dict, student_id: str, index: int) -> Optional[Assignment]:
        """단일 과제 정보 파싱"""
        try:
            # 제목 추출
            title = await self._extract_text_safely(item, [
                ".assignment-title", ".task-title", ".homework-title",
                "h1", "h2", "h3", "h4", ".title", ".name", ".subject"
            ])
            
            if not title:
                return None
            
            # 설명 추출
            description = await self._extract_text_safely(item, [
                ".assignment-description", ".task-description", ".homework-description",
                ".description", ".content", ".detail", ".summary", ".info"
            ])
            
            # 마감일 추출
            due_date_text = await self._extract_text_safely(item, [
                ".due-date", ".deadline", ".due-time", ".date", ".time",
                ".deadline-date", ".due-date-time", ".submission-date"
            ])
            
            due_date = self._parse_due_date(due_date_text) if due_date_text else datetime.now() + timedelta(days=7)
            
            # 상태 추출
            status_text = await self._extract_text_safely(item, [
                ".assignment-status", ".task-status", ".submission-status",
                ".status", ".state", ".progress"
            ])
            
            status = self._parse_status(status_text)
            
            # 우선순위 결정
            priority = self._determine_priority(due_date, status)
            
            # 과제 ID 생성
            assignment_id = f"learnus_{student_id}_{index}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            # 태그 생성
            tags = self._generate_tags(title, description, course_info['name'])
            
            # 새로운 과제 여부 확인
            is_new = self._is_new_assignment(due_date)
            
            # 마감 임박 여부 확인
            is_upcoming = self._is_upcoming_assignment(due_date)
            
            assignment = Assignment(
                id=assignment_id,
                title=title,
                description=description or "",
                course_name=course_info['name'],
                course_code=course_info['code'],
                due_date=due_date,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                status=status,
                priority=priority,
                tags=tags,
                is_new=is_new,
                is_upcoming=is_upcoming,
                university="연세대학교",
                student_id=student_id,
            )
            
            return assignment
            
        except Exception as e:
            logger.error(f"단일 과제 파싱 오류: {e}")
            return None
    
    async def _extract_text_safely(self, element, selectors: List[str]) -> str:
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
            # LearnUs 특화 날짜 형식 처리
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
                "%d/%m/%Y %H:%M",
                "%d/%m/%Y",
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
        if not status_text:
            return AssignmentStatus.pending
        
        status_text = status_text.lower()
        
        if "완료" in status_text or "submitted" in status_text or "제출완료" in status_text:
            return AssignmentStatus.submitted
        elif "진행" in status_text or "in progress" in status_text or "진행중" in status_text:
            return AssignmentStatus.inProgress
        elif "채점" in status_text or "graded" in status_text or "채점완료" in status_text:
            return AssignmentStatus.graded
        elif "지남" in status_text or "overdue" in status_text or "마감지남" in status_text:
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
        title_keywords = ["과제", "프로젝트", "시험", "퀴즈", "보고서", "발표", "실습", "숙제"]
        for keyword in title_keywords:
            if keyword in title:
                tags.append(keyword)
        
        # 강의명에서 키워드 추출
        if course_name and course_name != "알 수 없는 강의":
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
    
    async def _wait_for_page_load(self, driver: WebDriver, timeout: int = 10):
        """페이지 로딩 대기"""
        try:
            WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
        except TimeoutException:
            logger.warning("페이지 로딩 타임아웃")
