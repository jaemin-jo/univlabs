"""
학교 홈페이지 자동화 백엔드 서버
Flutter 앱과 통신하여 실제 로그인 및 과제 정보 수집
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import asyncio
import json
import os
from datetime import datetime, timedelta
import logging

from services.school_automation import SchoolAutomationService
from services.assignment_parser import AssignmentParser
from services.notification_service import NotificationService
from services.schedule_parser import ScheduleParser

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="School Automation API", version="1.0.0")

# CORS 설정 (Flutter 앱과 통신)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 특정 도메인으로 제한
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 서비스 인스턴스
automation_service = SchoolAutomationService()
assignment_parser = AssignmentParser()
notification_service = NotificationService()
schedule_parser = ScheduleParser()

# 요청 모델
class LoginRequest(BaseModel):
    university: str
    username: str
    password: str
    studentId: str

class AssignmentResponse(BaseModel):
    id: str
    title: str
    description: str
    course_name: str
    course_code: str
    due_date: str
    created_at: str
    updated_at: str
    status: str
    priority: str
    attachment_url: Optional[str] = None
    submission_url: Optional[str] = None
    tags: List[str] = []
    is_new: bool = False
    is_upcoming: bool = False
    university: str
    student_id: str

class AutomationStatus(BaseModel):
    status: str
    message: str
    last_check: Optional[str] = None
    next_check: Optional[str] = None
    assignments_count: int = 0
    new_assignments_count: int = 0
    upcoming_assignments_count: int = 0

# 헬스 체크
@app.get("/health")
async def health_check():
    """서버 상태 확인"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# 학사일정 관련 API
@app.get("/schedules")
async def get_all_schedules():
    """모든 학사일정 조회"""
    try:
        schedules = schedule_parser.get_all_schedules()
        return {"success": True, "data": schedules, "count": len(schedules)}
    except Exception as e:
        logger.error(f"학사일정 조회 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/schedules/upcoming")
async def get_upcoming_schedules(days: int = 30):
    """다가오는 학사일정 조회"""
    try:
        schedules = schedule_parser.get_upcoming_schedules(days)
        return {"success": True, "data": schedules, "count": len(schedules)}
    except Exception as e:
        logger.error(f"다가오는 학사일정 조회 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/schedules/important")
async def get_important_schedules():
    """중요한 학사일정 조회"""
    try:
        schedules = schedule_parser.get_important_schedules()
        return {"success": True, "data": schedules, "count": len(schedules)}
    except Exception as e:
        logger.error(f"중요 학사일정 조회 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/schedules/type/{schedule_type}")
async def get_schedules_by_type(schedule_type: str):
    """타입별 학사일정 조회"""
    try:
        schedules = schedule_parser.get_schedules_by_type(schedule_type)
        return {"success": True, "data": schedules, "count": len(schedules)}
    except Exception as e:
        logger.error(f"타입별 학사일정 조회 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# 로그인
@app.post("/login")
async def login(credentials: LoginRequest):
    """학교 홈페이지에 로그인"""
    try:
        success = await automation_service.login(
            university=credentials.university,
            username=credentials.username,
            password=credentials.password,
            student_id=credentials.studentId
        )
        
        if success:
            return {"message": "로그인 성공", "success": True}
        else:
            raise HTTPException(status_code=401, detail="로그인 실패")
            
    except Exception as e:
        logger.error(f"로그인 오류: {e}")
        raise HTTPException(status_code=500, detail=f"로그인 오류: {str(e)}")

# 모든 과제 조회
@app.get("/assignments")
async def get_assignments():
    """모든 과제 정보 조회"""
    try:
        assignments = await automation_service.get_all_assignments()
        return {"assignments": [assignment.to_dict() for assignment in assignments]}
        
    except Exception as e:
        logger.error(f"과제 조회 오류: {e}")
        raise HTTPException(status_code=500, detail=f"과제 조회 오류: {str(e)}")

# 새로운 과제 조회
@app.get("/assignments/new")
async def get_new_assignments():
    """새로운 과제 조회"""
    try:
        new_assignments = await automation_service.get_new_assignments()
        return {"new_assignments": [assignment.to_dict() for assignment in new_assignments]}
        
    except Exception as e:
        logger.error(f"새로운 과제 조회 오류: {e}")
        raise HTTPException(status_code=500, detail=f"새로운 과제 조회 오류: {str(e)}")

# 마감 임박 과제 조회
@app.get("/assignments/upcoming")
async def get_upcoming_assignments():
    """마감 임박 과제 조회"""
    try:
        upcoming_assignments = await automation_service.get_upcoming_assignments()
        return {"upcoming_assignments": [assignment.to_dict() for assignment in upcoming_assignments]}
        
    except Exception as e:
        logger.error(f"마감 임박 과제 조회 오류: {e}")
        raise HTTPException(status_code=500, detail=f"마감 임박 과제 조회 오류: {str(e)}")

# 자동화 시작
@app.post("/automation/start")
async def start_automation():
    """자동화 작업 시작"""
    try:
        success = await automation_service.start_automation()
        if success:
            return {"message": "자동화 작업이 시작되었습니다", "success": True}
        else:
            raise HTTPException(status_code=500, detail="자동화 작업 시작 실패")
            
    except Exception as e:
        logger.error(f"자동화 시작 오류: {e}")
        raise HTTPException(status_code=500, detail=f"자동화 시작 오류: {str(e)}")

# 자동화 중지
@app.post("/automation/stop")
async def stop_automation():
    """자동화 작업 중지"""
    try:
        success = await automation_service.stop_automation()
        if success:
            return {"message": "자동화 작업이 중지되었습니다", "success": True}
        else:
            raise HTTPException(status_code=500, detail="자동화 작업 중지 실패")
            
    except Exception as e:
        logger.error(f"자동화 중지 오류: {e}")
        raise HTTPException(status_code=500, detail=f"자동화 중지 오류: {str(e)}")

# 자동화 상태 확인
@app.get("/automation/status")
async def get_automation_status():
    """자동화 상태 확인"""
    try:
        status = await automation_service.get_status()
        return status
        
    except Exception as e:
        logger.error(f"자동화 상태 확인 오류: {e}")
        raise HTTPException(status_code=500, detail=f"자동화 상태 확인 오류: {str(e)}")

# 수동 과제 업데이트
@app.post("/assignments/refresh")
async def refresh_assignments():
    """수동으로 과제 정보 업데이트"""
    try:
        success = await automation_service.refresh_assignments()
        if success:
            return {"message": "과제 정보가 업데이트되었습니다", "success": True}
        else:
            raise HTTPException(status_code=500, detail="과제 정보 업데이트 실패")
            
    except Exception as e:
        logger.error(f"과제 정보 업데이트 오류: {e}")
        raise HTTPException(status_code=500, detail=f"과제 정보 업데이트 오류: {str(e)}")

# 자동화 기능 테스트
class TestLoginRequest(BaseModel):
    university: str
    username: str
    password: str
    student_id: str

@app.post("/automation/test-login")
async def test_login(request: TestLoginRequest):
    """자동화 로그인 기능 테스트"""
    try:
        logger.info(f"🧪 자동화 로그인 테스트 시작: {request.university}")
        
        # 로그인 시도
        success = await automation_service.login(request.university, request.username, request.password, request.student_id)
        
        if success:
            # 로그인 성공 시 과제 정보 수집 테스트
            assignments = await automation_service.get_all_assignments()
            
            return {
                "success": True,
                "message": "로그인 및 과제 수집 성공",
                "login_status": "성공",
                "assignments_count": len(assignments),
                "assignments": [
                    {
                        "title": a.title,
                        "course": a.course_name,
                        "due_date": a.due_date.isoformat() if a.due_date else None,
                        "status": a.status.value,
                        "priority": a.priority.value
                    } for a in assignments[:5]  # 최대 5개만 반환
                ]
            }
        else:
            return {
                "success": False,
                "message": "로그인 실패",
                "login_status": "실패",
                "error": "인증 정보가 올바르지 않거나 사이트 구조가 변경되었습니다"
            }
            
    except Exception as e:
        logger.error(f"자동화 테스트 오류: {e}")
        return {
            "success": False,
            "message": f"자동화 테스트 오류: {str(e)}",
            "login_status": "오류",
            "error": str(e)
        }

# 자동화 디버그 정보
@app.get("/automation/debug")
async def get_automation_debug():
    """자동화 시스템 디버그 정보"""
    try:
        return {
            "automation_running": automation_service.automation_running,
            "is_logged_in": automation_service.is_logged_in,
            "current_university": automation_service.current_university,
            "current_student_id": automation_service.current_student_id,
            "driver_status": "활성" if automation_service.driver else "비활성",
            "supported_universities": [
                "연세대학교", "고려대학교", "서울대학교", 
                "한국과학기술원", "포스텍"
            ],
            "test_endpoints": {
                "login_test": "/automation/test-login",
                "status": "/automation/status",
                "refresh": "/assignments/refresh"
            }
        }
        
    except Exception as e:
        logger.error(f"디버그 정보 조회 오류: {e}")
        raise HTTPException(status_code=500, detail=f"디버그 정보 조회 오류: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
