"""
자동화 스케줄링 서비스
- 정기적인 크롤링
- 백그라운드 실행
- 상태 모니터링
"""

import asyncio
import schedule
import time
from datetime import datetime, timedelta
from typing import Dict, List
import logging
from .school_automation import SchoolAutomationService
from .credential_manager import CredentialManager

logger = logging.getLogger(__name__)

class SchedulerService:
    def __init__(self):
        self.automation_service = SchoolAutomationService()
        self.credential_manager = CredentialManager()
        self.is_running = False
        self.active_users = {}  # 활성 사용자 추적
    
    async def start_scheduler(self):
        """스케줄러 시작"""
        logger.info("🕐 자동화 스케줄러 시작")
        
        # 매일 오전 8시, 오후 2시, 오후 8시에 실행
        schedule.every().day.at("08:00").do(self._run_automation_for_all_users)
        schedule.every().day.at("14:00").do(self._run_automation_for_all_users)
        schedule.every().day.at("20:00").do(self._run_automation_for_all_users)
        
        # 매주 월요일 오전 9시에 전체 스캔
        schedule.every().monday.at("09:00").do(self._run_weekly_scan)
        
        self.is_running = True
        
        # 스케줄러 루프 실행
        while self.is_running:
            schedule.run_pending()
            await asyncio.sleep(60)  # 1분마다 체크
    
    async def _run_automation_for_all_users(self):
        """모든 활성 사용자에 대해 자동화 실행"""
        logger.info("🔄 모든 사용자 자동화 실행 시작")
        
        # Firebase에서 활성 사용자 조회 (구현 필요)
        active_users = await self._get_active_users()
        
        for user in active_users:
            try:
                await self._run_automation_for_user(user)
            except Exception as e:
                logger.error(f"❌ 사용자 {user['id']} 자동화 오류: {e}")
    
    async def _run_automation_for_user(self, user: Dict):
        """특정 사용자 자동화 실행"""
        user_id = user["id"]
        credentials = self.credential_manager.get_credentials(user_id)
        
        if not credentials:
            logger.warning(f"⚠️ 사용자 {user_id}의 자격증명을 찾을 수 없음")
            return
        
        try:
            # 로그인 시도
            success = await self.automation_service.login(
                credentials["university"],
                credentials["username"],
                credentials["password"],
                credentials["student_id"]
            )
            
            if success:
                # 과제 정보 수집
                assignments = await self.automation_service.get_all_assignments()
                
                # Firebase에 저장 (구현 필요)
                await self._save_assignments_to_firebase(user_id, assignments)
                
                # 사용 시간 업데이트
                self.credential_manager.update_last_used(user_id)
                
                logger.info(f"✅ 사용자 {user_id} 자동화 성공: {len(assignments)}개 과제 수집")
            else:
                logger.warning(f"⚠️ 사용자 {user_id} 로그인 실패")
                
        except Exception as e:
            logger.error(f"❌ 사용자 {user_id} 자동화 오류: {e}")
    
    async def _get_active_users(self) -> List[Dict]:
        """Firebase에서 활성 사용자 조회"""
        # TODO: Firebase 연동 구현
        return [
            {"id": "user1", "university": "연세대학교"},
            {"id": "user2", "university": "서울대학교"},
        ]
    
    async def _save_assignments_to_firebase(self, user_id: str, assignments: List):
        """과제 정보를 Firebase에 저장"""
        # TODO: Firebase 연동 구현
        logger.info(f"💾 사용자 {user_id}의 {len(assignments)}개 과제 Firebase 저장")
    
    async def _run_weekly_scan(self):
        """주간 전체 스캔"""
        logger.info("📅 주간 전체 스캔 시작")
        await self._run_automation_for_all_users()
    
    def stop_scheduler(self):
        """스케줄러 중지"""
        self.is_running = False
        logger.info("🛑 자동화 스케줄러 중지")
