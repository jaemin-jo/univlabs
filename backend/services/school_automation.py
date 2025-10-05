"""
학교 홈페이지 자동화 서비스
Selenium을 사용하여 실제 로그인 및 과제 정보 수집
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

from models.assignment import Assignment, AssignmentStatus, AssignmentPriority
from services.assignment_parser import AssignmentParser
from services.learnus_parser import LearnUsParser
from services.notification_service import NotificationService

logger = logging.getLogger(__name__)

class SchoolAutomationService:
    def __init__(self):
        self.driver: Optional[webdriver.Chrome] = None
        self.is_logged_in = False
        self.current_university = None
        self.current_student_id = None
        self.assignment_parser = AssignmentParser()
        self.learnus_parser = LearnUsParser()
        self.notification_service = NotificationService()
        self.automation_running = False
        
    async def login(self, university: str, username: str, password: str, student_id: str) -> bool:
        """학교 홈페이지에 로그인"""
        try:
            logger.info(f"🔐 {university} 로그인 시도 중...")
            logger.info(f"   사용자: {username}")
            logger.info(f"   학번: {student_id}")
            logger.info(f"   시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Chrome 드라이버 설정
            await self._setup_driver()
            
            # 대학교별 로그인 URL 및 설정
            login_config = self._get_login_config(university)
            if not login_config:
                logger.error(f"❌ 지원하지 않는 대학교: {university}")
                return False
            
            # 1단계: LearnUs 메인 페이지 접속
            logger.info(f"🌐 LearnUs 메인 페이지 접속: {login_config['login_url']}")
            self.driver.get(login_config['login_url'])
            await asyncio.sleep(3)  # 페이지 로딩 대기
            
            # 연세포털 로그인 버튼 찾기 및 클릭
            logger.info("🔍 연세포털 로그인 버튼 찾는 중...")
            portal_login_button = None
            
            # 개선된 선택자 목록
            button_selectors = [
                "a.btn.btn-sso",  # 정확한 클래스 조합
                "a[href='https://ys.learnus.org/passni/sso/spLogin2.php']",  # 정확한 href
                "a[href*='spLogin2.php']",  # 부분 매칭
                "a[href*='passni/sso']",  # 중간 경로
                "a[href*='portal']",
                "a[href*='login']",
                ".login-btn",
                ".portal-btn"
            ]
            
            # 1단계: CSS 선택자로 찾기
            for i, selector in enumerate(button_selectors):
                try:
                    logger.info(f"   시도 중 ({i+1}/{len(button_selectors)}): {selector}")
                    portal_login_button = WebDriverWait(self.driver, 15).until(  # 타임아웃 증가
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
                    "//a[contains(text(), '연세포털')]"
                ]
                
                for i, xpath in enumerate(xpath_selectors):
                    try:
                        logger.info(f"   XPath 시도 중 ({i+1}/{len(xpath_selectors)}): {xpath}")
                        portal_login_button = WebDriverWait(self.driver, 15).until(
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
                    all_links = self.driver.find_elements(By.TAG_NAME, "a")
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
            
            if not portal_login_button:
                logger.error("❌ 연세포털 로그인 버튼을 찾을 수 없습니다")
                logger.info("🔍 페이지에서 사용 가능한 링크들:")
                try:
                    links = self.driver.find_elements(By.TAG_NAME, "a")
                    for i, link in enumerate(links[:10]):  # 처음 10개만
                        href = link.get_attribute("href")
                        text = link.text.strip()
                        if href and text:
                            logger.info(f"   링크 {i+1}: {text} -> {href}")
                except Exception as e:
                    logger.error(f"링크 정보 수집 실패: {e}")
                return False
            
            # 연세포털 로그인 버튼 클릭
            logger.info("🖱️ 연세포털 로그인 버튼 클릭...")
            portal_login_button.click()
            await asyncio.sleep(3)  # 페이지 이동 대기
            
            # 2단계: 연세포털 로그인 페이지에서 실제 로그인
            logger.info("🌐 연세포털 로그인 페이지로 이동...")
            
            # 사용자명 필드 찾기 (실제 필드명: loginId)
            username_field = None
            username_selectors = [
                f"input[id='{login_config['username_field']}']",  # loginId
                f"input[name='{login_config['username_field']}']",
                "input[type='text']",
                "input[placeholder*='학번']",
                "input[placeholder*='ID']",
            ]
            
            for selector in username_selectors:
                try:
                    username_field = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    logger.info(f"✅ 사용자명 필드 발견: {selector}")
                    break
                except TimeoutException:
                    continue
            
            if not username_field:
                logger.error("❌ 사용자명 필드를 찾을 수 없습니다")
                return False
            
            # 비밀번호 필드 찾기 (실제 필드명: loginPasswd)
            password_field = None
            password_selectors = [
                f"input[id='{login_config['password_field']}']",  # loginPasswd
                f"input[name='{login_config['password_field']}']",
                "input[type='password']",
                "input[placeholder*='비밀번호']",
                "input[placeholder*='Password']",
            ]
            
            for selector in password_selectors:
                try:
                    password_field = self.driver.find_element(By.CSS_SELECTOR, selector)
                    logger.info(f"✅ 비밀번호 필드 발견: {selector}")
                    break
                except NoSuchElementException:
                    continue
            
            if not password_field:
                logger.error("❌ 비밀번호 필드를 찾을 수 없습니다")
                return False
            
            # 기존 내용 지우기
            username_field.clear()
            password_field.clear()
            
            # 로그인 정보 입력
            logger.info("📝 로그인 정보 입력 중...")
            username_field.send_keys(username)
            password_field.send_keys(password)
            
            # 로그인 버튼 찾기 및 클릭
            login_button = None
            button_selectors = login_config['login_button'].split(', ')
            
            for selector in button_selectors:
                try:
                    login_button = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    logger.info(f"✅ 로그인 버튼 발견: {selector}")
                    break
                except (TimeoutException, NoSuchElementException):
                    logger.debug(f"로그인 버튼 선택자 실패: {selector}")
                    continue
            
            if not login_button:
                logger.error("❌ 로그인 버튼을 찾을 수 없습니다")
                return False
            
            # 로그인 버튼 클릭
            logger.info("🖱️ 로그인 버튼 클릭...")
            login_button.click()
            
            # 로그인 결과 확인
            await asyncio.sleep(3)  # 페이지 로딩 대기
            
            # 로그인 성공 여부 확인
            logger.info("🔍 로그인 결과 확인 중...")
            current_url = self.driver.current_url
            page_title = self.driver.title
            logger.info(f"📍 현재 URL: {current_url}")
            logger.info(f"📄 페이지 제목: {page_title}")
            
            success = await self._check_login_success(login_config)
            if success:
                logger.info("✅ 로그인 성공!")
                self.is_logged_in = True
                self.current_university = university
                self.current_student_id = student_id
                return True
            else:
                logger.error("❌ 로그인 실패 - 잘못된 인증 정보 또는 사이트 구조 변경")
                logger.info("🔍 페이지에서 오류 메시지 찾는 중...")
                try:
                    error_elements = self.driver.find_elements(By.CSS_SELECTOR, ".error, .alert, .warning, .login-error, .login-fail")
                    for element in error_elements:
                        if element.is_displayed():
                            error_text = element.text.strip()
                            if error_text:
                                logger.error(f"   오류 메시지: {error_text}")
                except Exception as e:
                    logger.debug(f"오류 메시지 수집 실패: {e}")
                return False
                
        except Exception as e:
            logger.error(f"❌ 로그인 오류: {e}")
            return False
        finally:
            if not self.is_logged_in and self.driver:
                self.driver.quit()
                self.driver = None
    
    async def _check_login_success(self, login_config: Dict[str, str]) -> bool:
        """로그인 성공 여부 확인"""
        try:
            # 성공 지표 확인
            if 'success_indicators' in login_config:
                for indicator in login_config['success_indicators']:
                    try:
                        element = WebDriverWait(self.driver, 5).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, indicator))
                        )
                        if element:
                            logger.info(f"✅ 로그인 성공 지표 발견: {indicator}")
                            return True
                    except TimeoutException:
                        continue
            
            # 실패 지표 확인
            if 'error_indicators' in login_config:
                for indicator in login_config['error_indicators']:
                    try:
                        element = self.driver.find_element(By.CSS_SELECTOR, indicator)
                        if element and element.is_displayed():
                            logger.error(f"❌ 로그인 실패 지표 발견: {indicator}")
                            return False
                    except NoSuchElementException:
                        continue
            
            # URL 변경 확인
            current_url = self.driver.current_url
            if login_config['login_url'] not in current_url:
                logger.info(f"✅ URL 변경 감지: {current_url}")
                return True
            
            # 페이지 제목 확인
            page_title = self.driver.title
            if any(keyword in page_title.lower() for keyword in ['dashboard', 'main', 'home', 'welcome']):
                logger.info(f"✅ 대시보드 페이지 감지: {page_title}")
                return True
            
            logger.warning("⚠️ 로그인 상태를 확인할 수 없습니다")
            return False
            
        except Exception as e:
            logger.error(f"❌ 로그인 상태 확인 오류: {e}")
            return False
    
    async def get_all_assignments(self) -> List[Assignment]:
        """모든 과제 정보 수집"""
        if not self.is_logged_in:
            logger.error("로그인이 필요합니다")
            return []
        
        try:
            logger.info("과제 정보 수집 시작...")
            
            # 과제 페이지로 이동
            assignment_config = self._get_assignment_config(self.current_university)
            self.driver.get(assignment_config['assignment_url'])
            
            # 페이지 로딩 대기
            await asyncio.sleep(3)
            
            # 대학교별 전용 파서 사용
            if self.current_university == "연세대학교":
                assignments = await self.learnus_parser.parse_learnus_assignments(
                    self.driver, 
                    self.current_student_id
                )
            else:
                assignments = await self.assignment_parser.parse_assignments(
                    self.driver, 
                    self.current_university,
                    self.current_student_id
                )
            
            logger.info(f"과제 정보 수집 완료: {len(assignments)}개")
            return assignments
            
        except Exception as e:
            logger.error(f"과제 정보 수집 오류: {e}")
            return []
    
    async def get_new_assignments(self) -> List[Assignment]:
        """새로운 과제 조회"""
        all_assignments = await self.get_all_assignments()
        
        # 최근 7일 이내에 생성된 과제만 필터링
        recent_date = datetime.now() - timedelta(days=7)
        new_assignments = [
            assignment for assignment in all_assignments
            if assignment.created_at >= recent_date
        ]
        
        return new_assignments
    
    async def get_upcoming_assignments(self) -> List[Assignment]:
        """마감 임박 과제 조회 (3일 이내)"""
        all_assignments = await self.get_all_assignments()
        
        # 3일 이내 마감 과제 필터링
        upcoming_date = datetime.now() + timedelta(days=3)
        upcoming_assignments = [
            assignment for assignment in all_assignments
            if assignment.due_date <= upcoming_date and assignment.due_date >= datetime.now()
        ]
        
        return upcoming_assignments
    
    async def start_automation(self) -> bool:
        """자동화 작업 시작"""
        try:
            if self.automation_running:
                logger.warning("자동화가 이미 실행 중입니다")
                return True
            
            self.automation_running = True
            logger.info("자동화 작업 시작")
            
            # 백그라운드에서 주기적으로 과제 정보 수집
            asyncio.create_task(self._automation_loop())
            
            return True
            
        except Exception as e:
            logger.error(f"자동화 시작 오류: {e}")
            return False
    
    async def stop_automation(self) -> bool:
        """자동화 작업 중지"""
        try:
            self.automation_running = False
            logger.info("자동화 작업 중지")
            return True
            
        except Exception as e:
            logger.error(f"자동화 중지 오류: {e}")
            return False
    
    async def get_status(self) -> Dict[str, Any]:
        """자동화 상태 조회"""
        try:
            all_assignments = await self.get_all_assignments()
            new_assignments = await self.get_new_assignments()
            upcoming_assignments = await self.get_upcoming_assignments()
            
            return {
                "status": "running" if self.automation_running else "stopped",
                "message": "자동화가 실행 중입니다" if self.automation_running else "자동화가 중지되었습니다",
                "last_check": datetime.now().isoformat(),
                "next_check": (datetime.now() + timedelta(hours=1)).isoformat(),
                "assignments_count": len(all_assignments),
                "new_assignments_count": len(new_assignments),
                "upcoming_assignments_count": len(upcoming_assignments),
            }
            
        except Exception as e:
            logger.error(f"상태 조회 오류: {e}")
            return {
                "status": "error",
                "message": f"상태 조회 오류: {str(e)}",
            }
    
    async def refresh_assignments(self) -> bool:
        """수동으로 과제 정보 업데이트"""
        try:
            logger.info("과제 정보 수동 업데이트 시작...")
            
            # 과제 정보 수집
            assignments = await self.get_all_assignments()
            
            # 새로운 과제가 있으면 알림 발송
            new_assignments = await self.get_new_assignments()
            if new_assignments:
                await self.notification_service.send_new_assignment_notification(new_assignments)
            
            # 마감 임박 과제가 있으면 알림 발송
            upcoming_assignments = await self.get_upcoming_assignments()
            if upcoming_assignments:
                await self.notification_service.send_upcoming_deadline_notification(upcoming_assignments)
            
            logger.info("과제 정보 수동 업데이트 완료")
            return True
            
        except Exception as e:
            logger.error(f"과제 정보 업데이트 오류: {e}")
            return False
    
    async def _setup_driver(self):
        """Chrome 드라이버 설정"""
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")  # 백그라운드 실행
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
        except Exception as e:
            logger.error(f"드라이버 설정 오류: {e}")
            raise
    
    def _get_login_config(self, university: str) -> Optional[Dict[str, str]]:
        """대학교별 로그인 설정"""
        configs = {
            "연세대학교": {
                # 1단계: LearnUs 메인 페이지에서 연세포털 로그인 버튼 클릭
                "login_url": "https://ys.learnus.org/",
                "portal_login_button": "a.btn.btn-sso, a[href*='spLogin2.php']",  # 연세포털 로그인 버튼
                
                # 2단계: 연세포털 로그인 페이지 설정
                "portal_login_url": "https://ys.learnus.org/passni/sso/spLogin2.php",
                "username_field": "loginId",  # 실제 필드명 (이미지에서 확인)
                "password_field": "loginPasswd",  # 실제 필드명 (이미지에서 확인)
                "login_button": "#loginBtn, a.submit, a[id='loginBtn'], a[class*='submit'], button[type='submit'], input[type='submit'], .login-btn, input[value*='로그인'], button[value*='로그인'], .btn-login, .submit-btn, input[name='login']",  # 로그인 버튼
                
                # 로그인 성공/실패 확인
                "success_indicators": [".dashboard", ".main-content", ".user-info", ".logout", ".course-list"],
                "error_indicators": [".error", ".alert", ".warning", ".login-error", ".login-fail"],
            },
            "고려대학교": {
                "login_url": "https://lms.korea.ac.kr/",
                "username_field": "username",
                "password_field": "password",
                "login_button": "button[type='submit']",
            },
            "서울대학교": {
                "login_url": "https://snu.blackboard.com/",
                "username_field": "username",
                "password_field": "password",
                "login_button": "button[type='submit']",
            },
            "한국과학기술원": {
                "login_url": "https://klms.kaist.ac.kr/",
                "username_field": "username",
                "password_field": "password",
                "login_button": "button[type='submit']",
            },
            "포스텍": {
                "login_url": "https://lms.postech.ac.kr/",
                "username_field": "username",
                "password_field": "password",
                "login_button": "button[type='submit']",
            },
        }
        
        return configs.get(university)
    
    def _get_assignment_config(self, university: str) -> Optional[Dict[str, str]]:
        """대학교별 과제 페이지 설정"""
        configs = {
            "연세대학교": {
                "assignment_url": "https://ys.learnus.org/",
                "assignment_list": ".course-list, .assignment-list",
                "assignment_item": ".course-item, .assignment-item",
                "title": ".course-title, .assignment-title",
                "description": ".course-description, .assignment-description",
                "due_date": ".due-date, .deadline",
                "course_name": ".course-name, .subject-name",
                "course_code": ".course-code, .subject-code",
                "status": ".assignment-status, .course-status",
            },
            "고려대학교": {
                "assignment_url": "https://lms.korea.ac.kr/",
                "assignment_list": ".task-list, .assignment-list",
                "assignment_item": ".task-item, .assignment-item",
                "title": ".task-title, .assignment-title",
                "description": ".task-description, .assignment-description",
                "due_date": ".deadline, .due-date",
                "course_name": ".subject-name, .course-name",
                "course_code": ".subject-code, .course-code",
                "status": ".task-status, .assignment-status",
            },
            "서울대학교": {
                "assignment_url": "https://snu.blackboard.com/",
                "assignment_list": ".content-list, .assignment-list",
                "assignment_item": ".content-item, .assignment-item",
                "title": ".content-title, .assignment-title",
                "description": ".content-description, .assignment-description",
                "due_date": ".due-date, .deadline",
                "course_name": ".course-name, .subject-name",
                "course_code": ".course-code, .subject-code",
                "status": ".content-status, .assignment-status",
            },
            "한국과학기술원": {
                "assignment_url": "https://klms.kaist.ac.kr/",
                "assignment_list": ".course-list, .assignment-list",
                "assignment_item": ".course-item, .assignment-item",
                "title": ".course-title, .assignment-title",
                "description": ".course-description, .assignment-description",
                "due_date": ".due-date, .deadline",
                "course_name": ".course-name, .subject-name",
                "course_code": ".course-code, .subject-code",
                "status": ".course-status, .assignment-status",
            },
            "포스텍": {
                "assignment_url": "https://lms.postech.ac.kr/",
                "assignment_list": ".course-list, .assignment-list",
                "assignment_item": ".course-item, .assignment-item",
                "title": ".course-title, .assignment-title",
                "description": ".course-description, .assignment-description",
                "due_date": ".due-date, .deadline",
                "course_name": ".course-name, .subject-name",
                "course_code": ".course-code, .subject-code",
                "status": ".course-status, .assignment-status",
            },
        }
        
        return configs.get(university)
    
    def _check_login_success(self) -> bool:
        """로그인 성공 여부 확인"""
        try:
            # 로그인 성공 후 나타나는 요소 확인
            # (대학교별로 다를 수 있음)
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, "user-info"))
            )
            return True
        except TimeoutException:
            return False
    
    async def _automation_loop(self):
        """자동화 루프 (백그라운드 실행)"""
        while self.automation_running:
            try:
                logger.info("자동화 루프 실행 중...")
                
                # 과제 정보 업데이트
                await self.refresh_assignments()
                
                # 1시간 대기
                await asyncio.sleep(3600)
                
            except Exception as e:
                logger.error(f"자동화 루프 오류: {e}")
                await asyncio.sleep(300)  # 5분 후 재시도
    
    def __del__(self):
        """소멸자 - 드라이버 정리"""
        if self.driver:
            self.driver.quit()
