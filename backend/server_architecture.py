"""
백엔드 서버 아키텍처 설계
LearnUs 자동화 시스템을 위한 서버 구조
"""

from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import asyncio
import schedule
import time
from typing import List, Dict, Optional
import logging

# FastAPI 앱 초기화
app = FastAPI(title="LearnUs Automation Server", version="1.0.0")

# CORS 설정 (모바일 앱과의 통신을 위해)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 특정 도메인으로 제한
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 데이터베이스 설정
DATABASE_URL = "sqlite:///./learnus_automation.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 데이터베이스 모델
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    learnus_id = Column(String, unique=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow)

class Assignment(Base):
    __tablename__ = "assignments"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    course_name = Column(String)
    activity_name = Column(String)
    activity_type = Column(String)  # 과제, 동영상, 퀴즈 등
    activity_url = Column(String)
    status = Column(String)  # 완료, 미완료, 대기중
    due_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

class AutomationLog(Base):
    __tablename__ = "automation_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    status = Column(String)  # 성공, 실패, 진행중
    message = Column(Text)
    execution_time = Column(DateTime, default=datetime.utcnow)

# 데이터베이스 테이블 생성
Base.metadata.create_all(bind=engine)

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 의존성 주입
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 스케줄러 설정
class AutomationScheduler:
    def __init__(self):
        self.running = False
        self.tasks = {}
    
    async def start_scheduler(self):
        """스케줄러 시작"""
        self.running = True
        while self.running:
            # 매 시간마다 실행
            schedule.run_pending()
            await asyncio.sleep(60)  # 1분마다 체크
    
    def stop_scheduler(self):
        """스케줄러 중지"""
        self.running = False
    
    def schedule_user_automation(self, user_id: int, interval_hours: int = 6):
        """특정 사용자의 자동화 작업 스케줄링"""
        schedule.every(interval_hours).hours.do(
            self.run_automation_for_user, user_id
        )
        logger.info(f"사용자 {user_id}의 자동화 작업이 {interval_hours}시간마다 실행되도록 스케줄링됨")
    
    async def run_automation_for_user(self, user_id: int):
        """특정 사용자의 자동화 작업 실행"""
        try:
            logger.info(f"사용자 {user_id}의 자동화 작업 시작")
            
            # 데이터베이스에서 사용자 정보 가져오기
            db = SessionLocal()
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                logger.error(f"사용자 {user_id}를 찾을 수 없음")
                return
            
            # 자동화 스크립트 실행
            from test_real_automation_hybrid import run_automation_for_user
            
            # 사용자별 자동화 실행
            result = await run_automation_for_user(
                username=user.username,
                password=user.password,
                user_id=user_id
            )
            
            # 결과를 데이터베이스에 저장
            if result.get('success'):
                # 과제 정보 업데이트
                for assignment in result.get('assignments', []):
                    existing = db.query(Assignment).filter(
                        Assignment.user_id == user_id,
                        Assignment.activity_url == assignment['url']
                    ).first()
                    
                    if existing:
                        existing.status = assignment['status']
                        existing.updated_at = datetime.utcnow()
                    else:
                        new_assignment = Assignment(
                            user_id=user_id,
                            course_name=assignment['course'],
                            activity_name=assignment['activity'],
                            activity_type=assignment['type'],
                            activity_url=assignment['url'],
                            status=assignment['status']
                        )
                        db.add(new_assignment)
                
                # 로그 저장
                log = AutomationLog(
                    user_id=user_id,
                    status="성공",
                    message=f"자동화 작업 완료: {len(result.get('assignments', []))}개 활동 처리"
                )
                db.add(log)
            else:
                # 실패 로그 저장
                log = AutomationLog(
                    user_id=user_id,
                    status="실패",
                    message=result.get('error', '알 수 없는 오류')
                )
                db.add(log)
            
            db.commit()
            logger.info(f"사용자 {user_id}의 자동화 작업 완료")
            
        except Exception as e:
            logger.error(f"사용자 {user_id}의 자동화 작업 실패: {e}")
            # 실패 로그 저장
            db = SessionLocal()
            log = AutomationLog(
                user_id=user_id,
                status="실패",
                message=str(e)
            )
            db.add(log)
            db.commit()
        finally:
            db.close()

# 전역 스케줄러 인스턴스
scheduler = AutomationScheduler()

# API 엔드포인트들
@app.post("/users/register")
async def register_user(
    username: str,
    password: str,
    learnus_id: str,
    db: SessionLocal = Depends(get_db)
):
    """사용자 등록"""
    # 중복 확인
    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="이미 등록된 사용자입니다")
    
    # 새 사용자 생성
    user = User(
        username=username,
        password=password,
        learnus_id=learnus_id
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # 자동화 작업 스케줄링
    scheduler.schedule_user_automation(user.id, interval_hours=6)
    
    return {"message": "사용자가 성공적으로 등록되었습니다", "user_id": user.id}

@app.get("/users/{user_id}/assignments")
async def get_user_assignments(
    user_id: int,
    status: Optional[str] = None,
    db: SessionLocal = Depends(get_db)
):
    """사용자의 과제 목록 조회"""
    query = db.query(Assignment).filter(Assignment.user_id == user_id)
    
    if status:
        query = query.filter(Assignment.status == status)
    
    assignments = query.all()
    
    return {
        "user_id": user_id,
        "assignments": [
            {
                "id": assignment.id,
                "course_name": assignment.course_name,
                "activity_name": assignment.activity_name,
                "activity_type": assignment.activity_type,
                "activity_url": assignment.activity_url,
                "status": assignment.status,
                "due_date": assignment.due_date,
                "updated_at": assignment.updated_at
            }
            for assignment in assignments
        ]
    }

@app.get("/users/{user_id}/assignments/incomplete")
async def get_incomplete_assignments(
    user_id: int,
    db: SessionLocal = Depends(get_db)
):
    """미완료 과제만 조회"""
    incomplete_assignments = db.query(Assignment).filter(
        Assignment.user_id == user_id,
        Assignment.status.in_(["❌ 해야 할 과제", "❌ 미완료", "❌ 미시청"])
    ).all()
    
    return {
        "user_id": user_id,
        "incomplete_assignments": [
            {
                "id": assignment.id,
                "course_name": assignment.course_name,
                "activity_name": assignment.activity_name,
                "activity_type": assignment.activity_type,
                "activity_url": assignment.activity_url,
                "status": assignment.status,
                "due_date": assignment.due_date,
                "updated_at": assignment.updated_at
            }
            for assignment in incomplete_assignments
        ]
    }

@app.post("/users/{user_id}/automation/run")
async def run_automation_now(
    user_id: int,
    background_tasks: BackgroundTasks,
    db: SessionLocal = Depends(get_db)
):
    """즉시 자동화 작업 실행"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다")
    
    # 백그라운드에서 자동화 작업 실행
    background_tasks.add_task(scheduler.run_automation_for_user, user_id)
    
    return {"message": "자동화 작업이 시작되었습니다"}

@app.get("/users/{user_id}/logs")
async def get_user_logs(
    user_id: int,
    limit: int = 10,
    db: SessionLocal = Depends(get_db)
):
    """사용자의 자동화 로그 조회"""
    logs = db.query(AutomationLog).filter(
        AutomationLog.user_id == user_id
    ).order_by(AutomationLog.execution_time.desc()).limit(limit).all()
    
    return {
        "user_id": user_id,
        "logs": [
            {
                "id": log.id,
                "status": log.status,
                "message": log.message,
                "execution_time": log.execution_time
            }
            for log in logs
        ]
    }

# 서버 시작 시 스케줄러 시작
@app.on_event("startup")
async def startup_event():
    """서버 시작 시 실행"""
    logger.info("LearnUs 자동화 서버 시작")
    # 스케줄러 시작
    asyncio.create_task(scheduler.start_scheduler())

@app.on_event("shutdown")
async def shutdown_event():
    """서버 종료 시 실행"""
    logger.info("LearnUs 자동화 서버 종료")
    scheduler.stop_scheduler()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


















