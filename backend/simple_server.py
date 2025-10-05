#!/usr/bin/env python3
"""
간단한 테스트 서버
FastAPI + Selenium 자동화 테스트
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import asyncio
import logging
from test_real_automation_hybrid import test_direct_selenium

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI 앱 생성
app = FastAPI(title="LearnUs Automation Server", version="1.0.0")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    """헬스체크 엔드포인트"""
    return {"status": "healthy", "message": "서버가 정상적으로 실행 중입니다"}

@app.post("/users/register")
async def register_user(username: str, password: str, learnus_id: str):
    """사용자 등록 및 자동화 실행"""
    try:
        logger.info(f"🔐 사용자 등록 요청: {username}")
        logger.info(f"🤖 LearnUs 자동화 시작...")
        
        # 실제 자동화 실행 (비동기로 실행)
        result = await asyncio.get_event_loop().run_in_executor(
            None, 
            test_direct_selenium, 
            "연세대학교", 
            username, 
            password, 
            "test_student_id"
        )
        
        logger.info(f"✅ 자동화 완료: {result}")
        
        return {
            "message": "사용자가 성공적으로 등록되었습니다",
            "user_id": 1,
            "automation_result": result,
            "status": "success"
        }
    except Exception as e:
        logger.error(f"❌ 사용자 등록 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/users/{user_id}/assignments")
async def get_user_assignments(user_id: int):
    """사용자의 과제 목록 조회"""
    try:
        logger.info(f"📋 사용자 {user_id}의 과제 목록 조회")
        
        # 실제 자동화 결과를 기반으로 한 과제 데이터
        # (실제로는 데이터베이스에서 조회하지만, 여기서는 자동화 결과를 시뮬레이션)
        assignments = [
            {
                "id": 1,
                "course_name": "AI응용수학",
                "activity_name": "5주차 과제",
                "activity_type": "과제",
                "activity_url": "https://ys.learnus.org/mod/assign/view.php?id=123",
                "status": "❌ 해야 할 과제",
                "due_date": None,
                "updated_at": "2025-10-03T02:00:00"
            },
            {
                "id": 2,
                "course_name": "딥러닝입문",
                "activity_name": "5주차 동영상",
                "activity_type": "동영상",
                "activity_url": "https://ys.learnus.org/mod/video/view.php?id=125",
                "status": "❌ 해야 할 과제",
                "due_date": None,
                "updated_at": "2025-10-03T02:00:00"
            },
            {
                "id": 3,
                "course_name": "기초AI알고리즘",
                "activity_name": "4주차 퀴즈",
                "activity_type": "퀴즈",
                "activity_url": "https://ys.learnus.org/mod/quiz/view.php?id=126",
                "status": "✅ 완료",
                "due_date": None,
                "updated_at": "2025-10-03T02:00:00"
            },
            {
                "id": 4,
                "course_name": "AI시스템프로그래밍",
                "activity_name": "5주차 프로젝트",
                "activity_type": "프로젝트",
                "activity_url": "https://ys.learnus.org/mod/assign/view.php?id=127",
                "status": "❌ 해야 할 과제",
                "due_date": None,
                "updated_at": "2025-10-03T02:00:00"
            }
        ]
        
        logger.info(f"✅ {len(assignments)}개 과제 조회 완료")
        
        return {
            "user_id": user_id,
            "assignments": assignments,
            "total_count": len(assignments),
            "incomplete_count": len([a for a in assignments if "❌" in a["status"]])
        }
    except Exception as e:
        logger.error(f"❌ 과제 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/users/{user_id}/automation/run")
async def run_automation_now(user_id: int):
    """즉시 자동화 작업 실행"""
    try:
        logger.info(f"자동화 실행 요청: 사용자 {user_id}")
        
        # 실제 자동화 실행 (백그라운드)
        # result = await run_automation_for_user("test_user", "test_password", user_id)
        
        return {"message": "자동화 작업이 시작되었습니다"}
    except Exception as e:
        logger.error(f"자동화 실행 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    print("🚀 LearnUs 자동화 서버 시작 중...")
    print("📡 서버 주소: http://localhost:8000")
    print("📋 API 문서: http://localhost:8000/docs")
    print("🔍 헬스체크: http://localhost:8000/health")
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        log_level="info"
    )
