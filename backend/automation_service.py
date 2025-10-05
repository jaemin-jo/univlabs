"""
LearnUs 자동화 서비스
서버에서 실행되는 자동화 로직
"""

import asyncio
import logging
from typing import Dict, List, Optional
from datetime import datetime
import json
import os

# 기존 자동화 스크립트 import
from test_real_automation_hybrid import (
    setup_driver, login_to_learnus, collect_this_week_lectures_hybrid,
    check_completion_status_on_main_page
)

logger = logging.getLogger(__name__)

class LearnUsAutomationService:
    """LearnUs 자동화 서비스 클래스"""
    
    def __init__(self):
        self.driver = None
        self.is_logged_in = False
    
    async def run_automation_for_user(
        self, 
        username: str, 
        password: str, 
        user_id: int
    ) -> Dict:
        """특정 사용자의 자동화 작업 실행"""
        try:
            logger.info(f"사용자 {user_id} ({username})의 자동화 작업 시작")
            
            # 드라이버 초기화
            self.driver = setup_driver()
            if not self.driver:
                return {"success": False, "error": "드라이버 초기화 실패"}
            
            # 로그인
            login_success = await self._login_user(username, password)
            if not login_success:
                return {"success": False, "error": "로그인 실패"}
            
            # 강의 정보 수집
            lectures = await self._collect_lectures()
            if not lectures:
                return {"success": False, "error": "강의 정보 수집 실패"}
            
            # 결과 처리
            result = await self._process_results(lectures, user_id)
            
            logger.info(f"사용자 {user_id}의 자동화 작업 완료: {len(result.get('assignments', []))}개 활동")
            return result
            
        except Exception as e:
            logger.error(f"사용자 {user_id}의 자동화 작업 실패: {e}")
            return {"success": False, "error": str(e)}
        finally:
            if self.driver:
                self.driver.quit()
    
    async def _login_user(self, username: str, password: str) -> bool:
        """사용자 로그인"""
        try:
            return login_to_learnus(self.driver, username, password)
        except Exception as e:
            logger.error(f"로그인 실패: {e}")
            return False
    
    async def _collect_lectures(self) -> List[Dict]:
        """강의 정보 수집"""
        try:
            return collect_this_week_lectures_hybrid(self.driver)
        except Exception as e:
            logger.error(f"강의 정보 수집 실패: {e}")
            return []
    
    async def _process_results(self, lectures: List[Dict], user_id: int) -> Dict:
        """결과 처리 및 저장"""
        try:
            assignments = []
            
            for lecture in lectures:
                if lecture['activity'] in ['이번주 강의 활동 없음', '이번주 강의 섹션 없음']:
                    continue
                
                # 완료 상태 확인
                status = "⏳ 대기 중"
                if lecture.get('url'):
                    status = check_completion_status_on_main_page(
                        self.driver, lecture['url']
                    )
                
                assignment = {
                    'user_id': user_id,
                    'course': lecture['course'],
                    'activity': lecture['activity'],
                    'type': lecture['type'],
                    'url': lecture['url'],
                    'status': status,
                    'created_at': datetime.utcnow().isoformat()
                }
                assignments.append(assignment)
            
            # 결과 파일 저장 (사용자별)
            await self._save_user_results(user_id, assignments)
            
            return {
                "success": True,
                "assignments": assignments,
                "total_count": len(assignments),
                "incomplete_count": len([a for a in assignments if '해야 할 과제' in a['status'] or '미완료' in a['status']])
            }
            
        except Exception as e:
            logger.error(f"결과 처리 실패: {e}")
            return {"success": False, "error": str(e)}
    
    async def _save_user_results(self, user_id: int, assignments: List[Dict]):
        """사용자별 결과 저장"""
        try:
            # 사용자별 디렉토리 생성
            user_dir = f"backend/user_results/{user_id}"
            os.makedirs(user_dir, exist_ok=True)
            
            # 결과 파일 저장
            result_file = f"{user_dir}/assignments_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(assignments, f, ensure_ascii=False, indent=2)
            
            # 최신 결과 파일 업데이트
            latest_file = f"{user_dir}/latest_assignments.json"
            with open(latest_file, 'w', encoding='utf-8') as f:
                json.dump(assignments, f, ensure_ascii=False, indent=2)
            
            logger.info(f"사용자 {user_id}의 결과 저장 완료: {result_file}")
            
        except Exception as e:
            logger.error(f"사용자 {user_id}의 결과 저장 실패: {e}")

# 전역 서비스 인스턴스
automation_service = LearnUsAutomationService()

# 비동기 실행 함수
async def run_automation_for_user(username: str, password: str, user_id: int) -> Dict:
    """사용자 자동화 실행 (외부 호출용)"""
    return await automation_service.run_automation_for_user(username, password, user_id)

# 배치 처리 함수
async def run_batch_automation(user_list: List[Dict]) -> Dict:
    """여러 사용자의 배치 자동화 실행"""
    results = {}
    
    for user in user_list:
        try:
            result = await run_automation_for_user(
                username=user['username'],
                password=user['password'],
                user_id=user['user_id']
            )
            results[user['user_id']] = result
        except Exception as e:
            results[user['user_id']] = {"success": False, "error": str(e)}
    
    return results

if __name__ == "__main__":
    # 테스트 실행
    async def test_automation():
        result = await run_automation_for_user("test_user", "test_password", 1)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    asyncio.run(test_automation())


