"""
LearnUs 자동화 서비스 - 완전히 새로운 버전
데이터 구조 문제를 근본적으로 해결
"""

import asyncio
import logging
from typing import Dict, List, Optional, Union
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
    """LearnUs 자동화 서비스 클래스 - 완전히 새로운 버전"""
    
    def __init__(self):
        self.driver = None
        self.is_logged_in = False
    
    async def run_automation_for_user(
        self, 
        username: str, 
        password: str, 
        user_id: int
    ) -> Dict:
        """특정 사용자의 자동화 작업 실행 - 완전히 새로운 방식"""
        try:
            logger.info(f"🚀 사용자 {user_id} ({username})의 자동화 작업 시작 (새로운 방식)")
            
            # 드라이버 초기화
            self.driver = setup_driver()
            if not self.driver:
                return {"success": False, "error": "드라이버 초기화 실패"}
            
            # 로그인
            login_success = await self._login_user(username, password)
            if not login_success:
                return {"success": False, "error": "로그인 실패"}
            
            # 🎯 완전히 새로운 강의 정보 수집 방식
            lectures_result = await self._collect_lectures_new_way()
            if not lectures_result.get("success", False):
                return {"success": False, "error": lectures_result.get("error", "강의 정보 수집 실패")}
            
            # 🎯 완전히 새로운 결과 처리 방식
            result = await self._process_results_new_way(lectures_result, user_id)
            
            logger.info(f"✅ 사용자 {user_id}의 자동화 작업 완료: {len(result.get('assignments', []))}개 활동")
            return result
            
        except Exception as e:
            logger.error(f"❌ 사용자 {user_id}의 자동화 작업 실패: {e}")
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
    
    async def _collect_lectures_new_way(self) -> Dict:
        """강의 정보 수집 - 완전히 새로운 방식"""
        try:
            logger.info("🔍 강의 정보 수집 시작 (완전히 새로운 방식)")
            
            # collect_this_week_lectures_hybrid 함수 호출
            raw_data = collect_this_week_lectures_hybrid(self.driver)
            
            # 🔍 데이터 타입과 내용 상세 분석
            logger.info(f"🔍 수집된 원본 데이터 타입: {type(raw_data)}")
            logger.info(f"🔍 수집된 원본 데이터 내용: {raw_data}")
            
            # 🎯 collect_this_week_lectures_hybrid는 딕셔너리를 반환함
            if isinstance(raw_data, dict):
                logger.info("📋 딕셔너리 형태의 데이터 처리")
                success = raw_data.get('success', False)
                lectures = raw_data.get('lectures', [])
                message = raw_data.get('message', '강의 정보 수집 완료')
                
                return {
                    "success": success,
                    "message": message,
                    "lectures": lectures,
                    "data_type": "dict_original",
                    "count": len(lectures)
                }
            elif isinstance(raw_data, list):
                logger.info("📋 리스트 형태의 데이터를 딕셔너리로 변환")
                return {
                    "success": True,
                    "message": f"{len(raw_data)}개 강의 정보 수집 완료",
                    "lectures": raw_data,
                    "data_type": "list_converted",
                    "count": len(raw_data)
                }
            else:
                logger.error(f"❌ 예상치 못한 데이터 타입: {type(raw_data)}")
                return {
                    "success": False,
                    "error": f"잘못된 데이터 타입: {type(raw_data)}",
                    "lectures": [],
                    "count": 0
                }
                
        except Exception as e:
            logger.error(f"강의 정보 수집 실패: {e}")
            return {
                "success": False,
                "error": f"강의 정보 수집 실패: {str(e)}",
                "lectures": [],
                "count": 0
            }
    
    async def _process_results_new_way(self, lectures_result: Dict, user_id: int) -> Dict:
        """결과 처리 및 저장 - 완전히 새로운 방식"""
        try:
            assignments = []
            
            # 🔍 디버깅: lectures_result 타입과 내용 확인
            logger.info(f"🔍 _process_results_new_way 호출됨")
            logger.info(f"🔍 lectures_result 타입: {type(lectures_result)}")
            logger.info(f"🔍 lectures_result 내용: {lectures_result}")
            
            # 🎯 완전히 새로운 데이터 처리 로직
            if not isinstance(lectures_result, dict):
                logger.error(f"❌ lectures_result가 딕셔너리가 아님: {type(lectures_result)}")
                return {
                    "success": False,
                    "error": f"잘못된 lectures_result 타입: {type(lectures_result)}"
                }
            
            # 성공 여부 확인
            if not lectures_result.get("success", False):
                logger.warning(f"강의 수집 실패: {lectures_result.get('error', '알 수 없는 오류')}")
                return {
                    "success": True,
                    "assignments": [],
                    "total_count": 0,
                    "incomplete_count": 0
                }
            
            # lectures 리스트 추출
            lectures = lectures_result.get("lectures", [])
            logger.info(f"✅ 수집된 강의 정보: {len(lectures)}개 항목")
            
            if not lectures:
                logger.warning("수집된 강의 정보가 없습니다")
                return {
                    "success": True,
                    "assignments": [],
                    "total_count": 0,
                    "incomplete_count": 0
                }
            
            # lectures 리스트 처리
            for i, lecture in enumerate(lectures):
                logger.info(f"🔍 항목 {i+1} 처리 중 - 타입: {type(lecture)}")
                logger.info(f"🔍 항목 {i+1} 내용: {lecture}")
                
                # lecture가 딕셔너리인지 확인
                if not isinstance(lecture, dict):
                    logger.warning(f"⚠️ 항목 {i+1}이 딕셔너리가 아님: {type(lecture)} - {lecture}")
                    continue
                    
                if lecture.get('activity') in ['이번주 강의 활동 없음', '이번주 강의 섹션 없음']:
                    continue
                
                # 완료 상태 확인
                status = "⏳ 대기 중"
                if lecture.get('url'):
                    try:
                        status = check_completion_status_on_main_page(
                            self.driver, lecture['url']
                        )
                    except Exception as status_error:
                        logger.warning(f"상태 확인 실패: {status_error}")
                        status = "❓ 상태 불명"
                
                assignment = {
                    'user_id': user_id,
                    'course': lecture.get('course', ''),
                    'activity': lecture.get('activity', ''),
                    'type': lecture.get('type', ''),
                    'url': lecture.get('url', ''),
                    'status': status,
                    'created_at': datetime.utcnow().isoformat()
                }
                assignments.append(assignment)
                logger.info(f"✅ 과제 {i+1} 처리 완료: {assignment['activity']}")
            
            # 결과 파일 저장 (사용자별)
            await self._save_user_results(user_id, assignments)
            
            logger.info(f"🎯 최종 결과: {len(assignments)}개 과제 처리 완료")
            return {
                "success": True,
                "assignments": assignments,
                "total_count": len(assignments),
                "incomplete_count": len([a for a in assignments if '해야 할 과제' in a['status'] or '미완료' in a['status']])
            }
            
        except Exception as e:
            logger.error(f"❌ 결과 처리 실패: {e}")
            logger.error(f"❌ 오류 상세: {str(e)}")
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