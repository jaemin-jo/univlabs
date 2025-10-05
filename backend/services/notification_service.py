"""
알림 서비스
새로운 과제 및 마감 임박 과제 알림 발송
"""

import logging
from typing import List
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from models.assignment import Assignment

logger = logging.getLogger(__name__)

class NotificationService:
    def __init__(self):
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.email = "your-email@gmail.com"  # 실제 이메일로 변경 필요
        self.password = "your-app-password"  # 실제 앱 비밀번호로 변경 필요
    
    async def send_new_assignment_notification(self, new_assignments: List[Assignment]):
        """새로운 과제 알림 발송"""
        try:
            if not new_assignments:
                return
            
            logger.info(f"새로운 과제 알림 발송: {len(new_assignments)}개")
            
            # 이메일 제목
            subject = f"새로운 과제 {len(new_assignments)}개가 등록되었습니다"
            
            # 이메일 내용
            body = self._create_new_assignment_email_body(new_assignments)
            
            # 이메일 발송
            await self._send_email(subject, body)
            
            # 로그 기록
            logger.info("새로운 과제 알림 발송 완료")
            
        except Exception as e:
            logger.error(f"새로운 과제 알림 발송 오류: {e}")
    
    async def send_upcoming_deadline_notification(self, upcoming_assignments: List[Assignment]):
        """마감 임박 과제 알림 발송"""
        try:
            if not upcoming_assignments:
                return
            
            logger.info(f"마감 임박 과제 알림 발송: {len(upcoming_assignments)}개")
            
            # 이메일 제목
            subject = f"마감 임박 과제 {len(upcoming_assignments)}개가 있습니다"
            
            # 이메일 내용
            body = self._create_upcoming_deadline_email_body(upcoming_assignments)
            
            # 이메일 발송
            await self._send_email(subject, body)
            
            # 로그 기록
            logger.info("마감 임박 과제 알림 발송 완료")
            
        except Exception as e:
            logger.error(f"마감 임박 과제 알림 발송 오류: {e}")
    
    def _create_new_assignment_email_body(self, assignments: List[Assignment]) -> str:
        """새로운 과제 이메일 내용 생성"""
        body = f"""
새로운 과제가 {len(assignments)}개 등록되었습니다.

과제 목록:
"""
        
        for i, assignment in enumerate(assignments, 1):
            body += f"""
{i}. {assignment.title}
   - 과목: {assignment.course_name} ({assignment.course_code})
   - 마감일: {assignment.due_date.strftime('%Y년 %m월 %d일 %H:%M')}
   - 상태: {assignment.status.value}
   - 우선순위: {assignment.priority.value}
"""
        
        body += f"""
총 {len(assignments)}개의 새로운 과제가 있습니다.
앱에서 자세한 내용을 확인해주세요.

발송 시간: {datetime.now().strftime('%Y년 %m월 %d일 %H:%M:%S')}
"""
        
        return body
    
    def _create_upcoming_deadline_email_body(self, assignments: List[Assignment]) -> str:
        """마감 임박 과제 이메일 내용 생성"""
        body = f"""
마감이 임박한 과제가 {len(assignments)}개 있습니다.

과제 목록:
"""
        
        for i, assignment in enumerate(assignments, 1):
            days_left = assignment.days_until_due()
            body += f"""
{i}. {assignment.title}
   - 과목: {assignment.course_name} ({assignment.course_code})
   - 마감일: {assignment.due_date.strftime('%Y년 %m월 %d일 %H:%M')}
   - 남은 시간: {days_left}일
   - 상태: {assignment.status.value}
   - 우선순위: {assignment.priority.value}
"""
        
        body += f"""
총 {len(assignments)}개의 마감 임박 과제가 있습니다.
빠른 시일 내에 제출해주세요.

발송 시간: {datetime.now().strftime('%Y년 %m월 %d일 %H:%M:%S')}
"""
        
        return body
    
    async def _send_email(self, subject: str, body: str):
        """이메일 발송"""
        try:
            # 이메일 메시지 생성
            msg = MIMEMultipart()
            msg['From'] = self.email
            msg['To'] = self.email  # 실제 사용자 이메일로 변경 필요
            msg['Subject'] = subject
            
            # 본문 추가
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            # SMTP 서버 연결 및 이메일 발송
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email, self.password)
            
            text = msg.as_string()
            server.sendmail(self.email, self.email, text)
            server.quit()
            
            logger.info("이메일 발송 완료")
            
        except Exception as e:
            logger.error(f"이메일 발송 오류: {e}")
            raise
    
    async def send_test_notification(self):
        """테스트 알림 발송"""
        try:
            subject = "학교 자동화 시스템 테스트 알림"
            body = f"""
학교 자동화 시스템이 정상적으로 작동하고 있습니다.

테스트 시간: {datetime.now().strftime('%Y년 %m월 %d일 %H:%M:%S')}
"""
            
            await self._send_email(subject, body)
            logger.info("테스트 알림 발송 완료")
            
        except Exception as e:
            logger.error(f"테스트 알림 발송 오류: {e}")
