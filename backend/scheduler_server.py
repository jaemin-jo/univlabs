#!/usr/bin/env python3
"""
주기적 자동화 실행 서버
LearnUs에서 주기적으로 정보를 수집하여 assignment.txt 파일에 저장
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import asyncio
import logging
import schedule
import time
import threading
import json
import os
import subprocess
import signal
from datetime import datetime
# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 핵심 모듈들 (안전한 import)
logger.info("🔧 [SCHEDULER] 핵심 모듈 로딩 시작...")
try:
    logger.info("🔧 [SCHEDULER] test_real_automation_hybrid 모듈 로딩 중...")
    from test_real_automation_hybrid import test_direct_selenium
    logger.info("✅ [SCHEDULER] test_real_automation_hybrid 모듈 로드 성공")
    
    logger.info("🔧 [SCHEDULER] firebase_service 모듈 로딩 중...")
    from firebase_service import get_all_active_users, update_user_last_used
    logger.info("✅ [SCHEDULER] firebase_service 모듈 로드 성공")
    
    CORE_MODULES_AVAILABLE = True
    logger.info("✅ [SCHEDULER] 모든 핵심 모듈들 로드 성공")
except ImportError as e:
    logger.error(f"❌ [SCHEDULER] 핵심 모듈들 로드 실패: {e}")
    logger.error(f"🔍 [SCHEDULER] ImportError 상세: {type(e).__name__}")
    logger.error(f"🔍 [SCHEDULER] ImportError 메시지: {str(e)}")
    import traceback
    logger.error(f"🔍 [SCHEDULER] ImportError 스택 트레이스:\n{traceback.format_exc()}")
    test_direct_selenium = None
    get_all_active_users = None
    update_user_last_used = None
    CORE_MODULES_AVAILABLE = False

# 최적화된 모듈들 (선택적 import) - 임시 비활성화
logger.info("🔧 [SCHEDULER] 최적화된 모듈들 로딩 시작...")
try:
    logger.info("🔧 [SCHEDULER] batch_automation_scheduler 모듈 로딩 시도...")
    # from batch_automation_scheduler import BatchAutomationScheduler
    logger.info("🔧 [SCHEDULER] optimized_hybrid_automation 모듈 로딩 시도...")
    # from optimized_hybrid_automation import OptimizedHybridAutomation
    BatchAutomationScheduler = None
    OptimizedHybridAutomation = None
    OPTIMIZED_MODULES_AVAILABLE = False
    logger.info("⚠️ [SCHEDULER] 최적화된 모듈들 임시 비활성화 (순환 import 방지)")
except ImportError as e:
    logger.warning(f"⚠️ [SCHEDULER] 최적화된 모듈들 로드 실패: {e}")
    logger.warning(f"🔍 [SCHEDULER] ImportError 상세: {type(e).__name__}")
    logger.warning(f"🔍 [SCHEDULER] ImportError 메시지: {str(e)}")
    BatchAutomationScheduler = None
    OptimizedHybridAutomation = None
    OPTIMIZED_MODULES_AVAILABLE = False

# 로깅 설정 (상세한 로그 출력)
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('/app/automation.log', mode='a')
    ]
)
logger = logging.getLogger(__name__)

# 상세한 시스템 정보 로깅
logger.info("🔍 시스템 정보:")
logger.info(f"  Python 버전: {os.sys.version}")
logger.info(f"  작업 디렉토리: {os.getcwd()}")
logger.info(f"  환경 변수 개수: {len(os.environ)}")
logger.info(f"  현재 사용자: {os.environ.get('USER', 'unknown')}")
logger.info(f"  현재 시간: {datetime.now().isoformat()}")

# 환경 변수 설정 (가장 단순한 방식)
os.environ['DISPLAY'] = ':99'
os.environ['CHROME_BIN'] = '/usr/bin/google-chrome'
os.environ['CHROMEDRIVER_PATH'] = '/usr/bin/chromedriver'

# Cloud Run 환경에서 Chrome 실행 비활성화 (디버깅용)
CHROME_DISABLED = os.environ.get('CHROME_DISABLED', 'false').lower() == 'true'

def run_basic_automation(active_users):
    """기본 자동화 실행 (최적화된 모듈이 없을 때 사용)"""
    all_assignments = []
    successful_users = 0
    failed_users = 0
    
    # Chrome 비활성화된 경우 더미 데이터 반환 (디버깅용)
    if CHROME_DISABLED:
        logger.info("🔧 Chrome 비활성화 모드 - 더미 데이터 생성")
        for user in active_users:
            username = user.get('username', 'Unknown')
            logger.info(f"🔄 사용자 {username} 더미 자동화 처리...")
            
            # 더미 과제 데이터 생성
            dummy_assignments = [
                {
                    'title': f'{username}의 더미 과제 1',
                    'status': '미완료',
                    'deadline': '2024-12-31',
                    'course': '테스트 과목'
                },
                {
                    'title': f'{username}의 더미 과제 2',
                    'status': '완료',
                    'deadline': '2024-12-25',
                    'course': '테스트 과목'
                }
            ]
            all_assignments.extend(dummy_assignments)
            successful_users += 1
            logger.info(f"사용자 {username} 더미 자동화 완료: {len(dummy_assignments)}개 과제")
        
        return {
            'assignments': all_assignments,
            'total_count': len(all_assignments),
            'users_processed': len(active_users),
            'successful_users': successful_users,
            'failed_users': failed_users,
            'firebase_status': 'connected',
            'user_count': len(active_users)
        }
    
    # 실제 Chrome 자동화 실행
    logger.info("🌐 실제 Chrome 자동화 실행...")
    
    for user in active_users:
        try:
            username = user.get('username', 'Unknown')
            university = user.get('university', '연세대학교')
            student_id = user.get('studentId', '')
            
            logger.info(f"🔄 사용자 {username} 자동화 시작...")
            logger.info(f"   대학교: {university}")
            logger.info(f"   학번: {student_id}")
            
            # 사용자별 자동화 실행 (모듈 사용 가능한 경우에만)
            if CORE_MODULES_AVAILABLE and test_direct_selenium:
                logger.info(f"🌐 Chrome 자동화 시작 - 사용자: {username}")
                logger.info(f"   대학교: {university}")
                logger.info(f"   학번: {student_id}")
                
                try:
                    user_result = test_direct_selenium(
                        university,
                        username,
                        user.get('password', ''),
                        student_id
                    )
                    logger.info(f"✅ Chrome 자동화 완료 - 사용자: {username}")
                except Exception as chrome_error:
                    logger.error(f"❌ Chrome 자동화 실패 - 사용자: {username}: {chrome_error}")
                    user_result = None
            else:
                logger.warning("핵심 모듈이 사용 불가능 - 더미 데이터 생성")
                user_result = [
                    {
                        'title': f'{username}의 더미 과제',
                        'status': '미완료',
                        'deadline': '2024-12-31',
                        'course': '테스트 과목'
                    }
                ]
            
            if user_result:
                # user_result가 리스트인지 딕셔너리인지 확인
                if isinstance(user_result, list):
                    user_assignments = user_result
                    all_assignments.extend(user_assignments)
                elif isinstance(user_result, dict):
                    user_assignments = user_result.get('assignments', [])
                    all_assignments.extend(user_assignments)
                
                # 마지막 사용 시간 업데이트
                try:
                    update_user_last_used(user.get('uid', ''))
                    logger.info(f"사용자 {username} 마지막 사용 시간 업데이트 완료")
                except Exception as update_error:
                    logger.warning(f"사용자 {username} 마지막 사용 시간 업데이트 실패: {update_error}")
                
                successful_users += 1
                logger.info(f"사용자 {username} 자동화 완료: {len(user_assignments)}개 과제")
            else:
                failed_users += 1
                logger.warning(f"사용자 {username} 자동화 결과 없음")
                
        except Exception as user_error:
            failed_users += 1
            logger.error(f"사용자 {user.get('username', 'Unknown')} 자동화 실패: {user_error}")
            continue
    
    return {
        'assignments': all_assignments,
        'total_count': len(all_assignments),
        'users_processed': len(active_users),
        'successful_users': successful_users,
        'failed_users': failed_users,
        'firebase_status': 'connected',
        'user_count': len(active_users)
    }

# Xvfb 프로세스 관리
xvfb_process = None

def start_xvfb():
    """Xvfb 가상 디스플레이 시작"""
    global xvfb_process
    try:
        logger.info("🔧 [SCHEDULER] Xvfb 가상 디스플레이 시작...")
        xvfb_process = subprocess.Popen([
            'Xvfb', ':99', '-screen', '0', '1920x1080x24', 
            '-ac', '+extension', 'GLX', '+render', '-noreset'
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(3)  # Xvfb 시작 대기
        logger.info("✅ [SCHEDULER] Xvfb 시작 완료")
        return True
    except Exception as e:
        logger.error(f"❌ [SCHEDULER] Xvfb 시작 실패: {e}")
        return False

def stop_xvfb():
    """Xvfb 가상 디스플레이 종료"""
    global xvfb_process
    if xvfb_process:
        try:
            logger.info("🔧 [SCHEDULER] Xvfb 종료 중...")
            xvfb_process.terminate()
            xvfb_process.wait(timeout=5)
            logger.info("✅ [SCHEDULER] Xvfb 종료 완료")
        except Exception as e:
            logger.error(f"❌ [SCHEDULER] Xvfb 종료 실패: {e}")

# FastAPI 앱 생성
logger.info("🔧 [SCHEDULER] FastAPI 앱 생성 시작...")
app = FastAPI(title="LearnUs Scheduler Server", version="1.0.0")
logger.info("✅ [SCHEDULER] FastAPI 앱 생성 완료")

# FastAPI 이벤트 핸들러
@app.on_event("startup")
async def startup_event():
    """애플리케이션 시작 시 Xvfb 시작"""
    logger.info("🚀 [SCHEDULER] 애플리케이션 시작 이벤트")
    
    # 환경 변수 설정
    os.environ['DISPLAY'] = ':99'
    os.environ['CHROME_BIN'] = '/usr/bin/google-chrome'
    os.environ['CHROMEDRIVER_PATH'] = '/usr/bin/chromedriver'
    os.environ['WDM_LOG_LEVEL'] = '0'
    
    logger.info("🔧 [SCHEDULER] 환경 변수 설정 완료")
    logger.info(f"   DISPLAY: {os.environ.get('DISPLAY')}")
    logger.info(f"   CHROME_BIN: {os.environ.get('CHROME_BIN')}")
    logger.info(f"   CHROMEDRIVER_PATH: {os.environ.get('CHROMEDRIVER_PATH')}")
    
    # Xvfb 시작
    if start_xvfb():
        logger.info("✅ [SCHEDULER] Xvfb 시작 성공")
    else:
        logger.error("❌ [SCHEDULER] Xvfb 시작 실패")
    
    logger.info("✅ [SCHEDULER] 애플리케이션 시작 완료")

@app.on_event("shutdown")
async def shutdown_event():
    """애플리케이션 종료 시 Xvfb 종료"""
    logger.info("🔚 [SCHEDULER] 애플리케이션 종료 이벤트")
    stop_xvfb()
    logger.info("✅ [SCHEDULER] 애플리케이션 종료 완료")

# Health Check 엔드포인트 (Cloud Run 타임아웃 방지)
@app.get("/health")
async def health_check():
    """Cloud Run Health Check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "learnus-backend"
    }

@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "message": "LearnUs Scheduler Server",
        "status": "running",
        "version": "1.0.0"
    }

# 스케줄러 함수 정의 (start_scheduler_auto보다 먼저 정의)
def start_scheduler():
    """스케줄러 시작"""
    logger.info("스케줄러 시작...")
    
    # 즉시 한 번 실행 (서버 시작 시)
    logger.info("서버 시작 시 즉시 자동화 실행...")
    run_automation_job()
    
    # 매일 오전 9시, 오후 6시에 자동화 실행
    schedule.every().day.at("09:00").do(run_automation_job)
    schedule.every().day.at("18:00").do(run_automation_job)
    
    # 개발용: 5분마다 실행 (테스트용)
    schedule.every(5).minutes.do(run_automation_job)
    
    while True:
        schedule.run_pending()
        time.sleep(60)  # 1분마다 체크

def start_scheduler_optimized():
    """Cloud Run 환경에 최적화된 스케줄러"""
    print("Cloud Run 최적화 스케줄러 시작...")
    logger.info("Cloud Run 최적화 스케줄러 시작")
    
    try:
        # 즉시 첫 실행
        print("🚀 즉시 자동화 실행 시작...")
        logger.info("🚀 즉시 자동화 실행 시작...")
        run_automation_job()
        
        # 개발용: 5분마다 실행
        schedule.every(5).minutes.do(run_automation_job)
        
        # 운영용: 매일 09:00, 18:00 실행
        # schedule.every().day.at("09:00").do(run_automation_job)
        # schedule.every().day.at("18:00").do(run_automation_job)
        
        print("스케줄 등록 완료: 즉시 실행 + 5분마다 자동화 실행")
        logger.info("스케줄 등록 완료: 즉시 실행 + 5분마다 자동화 실행")
        
        # Cloud Run 환경에서 안정적인 스케줄러 실행
        while True:
            try:
                schedule.run_pending()
                time.sleep(60)  # 1분마다 체크
            except Exception as e:
                logger.error(f"스케줄러 실행 중 오류: {e}")
                print(f"⚠️ 스케줄러 실행 중 오류: {e}")
                time.sleep(60)  # 오류 발생 시 1분 대기 후 재시도
                
    except Exception as e:
        logger.error(f"Cloud Run 스케줄러 시작 실패: {e}")
        print(f"Cloud Run 스케줄러 시작 실패: {e}")

# FastAPI startup 이벤트로 스케줄러 시작
@app.on_event("startup")
async def startup_event():
    """FastAPI 앱 시작 시 스케줄러 자동 시작"""
    print("LearnUs 스케줄러 서버 시작 중...")
    print("서버 주소: http://0.0.0.0:8080")
    print("API 문서: http://0.0.0.0:8080/docs")
    print("헬스체크: http://0.0.0.0:8080/health")
    print("과제 정보: http://0.0.0.0:8080/assignments")
    print("자동화 실행: 매일 09:00, 18:00 (개발용: 5분마다)")
    
    # Cloud Run 환경에 최적화된 스케줄러 시작
    try:
        # 백그라운드에서 스케줄러 시작 (서버 시작을 블로킹하지 않음)
        scheduler_thread = threading.Thread(target=start_scheduler_optimized, daemon=True)
        scheduler_thread.start()
        print("Cloud Run 최적화 스케줄러 백그라운드 시작됨")
        
    except Exception as e:
        print(f"스케줄러 시작 실패: {e}")
        logger.error(f"스케줄러 시작 실패: {e}")
        # 스케줄러 실패해도 서버는 계속 실행

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 전역 변수
_automation_running = False
_last_update_time = None
_assignment_data = []

def run_automation_job():
    """주기적으로 실행되는 자동화 작업 (최적화된 버전)"""
    global _automation_running, _last_update_time, _assignment_data
    
    if _automation_running:
        logger.info("⏳ 자동화가 이미 실행 중입니다. 건너뜁니다.")
        return
    
    try:
        _automation_running = True
        logger.info("🤖 최적화된 자동화 시작...")
        
        # 상세한 환경 정보 로깅
        logger.info("🔍 환경 변수 확인:")
        logger.info(f"   DISPLAY: {os.environ.get('DISPLAY', 'NOT SET')}")
        logger.info(f"   CHROME_BIN: {os.environ.get('CHROME_BIN', 'NOT SET')}")
        logger.info(f"   WORKSPACE_DIR: {os.environ.get('WORKSPACE_DIR', 'NOT SET')}")
        logger.info(f"   PYTHONPATH: {os.environ.get('PYTHONPATH', 'NOT SET')}")
        logger.info(f"   PATH: {os.environ.get('PATH', 'NOT SET')[:200]}...")
        
        # WORKSPACE_DIR 환경 변수가 설정되지 않았을 때 기본값 설정
        if not os.environ.get('WORKSPACE_DIR'):
            os.environ['WORKSPACE_DIR'] = '/app/workspace'
            logger.info(f"🔧 WORKSPACE_DIR 환경 변수 설정: {os.environ['WORKSPACE_DIR']}")
        else:
            logger.info(f"✅ WORKSPACE_DIR 환경 변수 이미 설정됨: {os.environ['WORKSPACE_DIR']}")
        
        # 시스템 정보 로깅
        logger.info("🔍 시스템 정보:")
        logger.info(f"   Python 버전: {os.sys.version}")
        logger.info(f"   현재 작업 디렉토리: {os.getcwd()}")
        logger.info(f"   사용 가능한 파일: {os.listdir('.')[:10]}")
        
        # Firebase 연결 상태 확인
        logger.info("Firebase 연결 상태 확인 중...")
        try:
            # Firebase에서 활성화된 사용자 정보 가져오기
            active_users = get_all_active_users()
            logger.info(f"Firebase에서 {len(active_users)}명의 활성화된 사용자 조회")
            
            if not active_users:
                logger.warning("활성화된 사용자가 없습니다. 실제 LearnUs 사용자 정보를 Firebase에 추가해주세요.")
                logger.info("해결방법: Flutter 앱에서 LearnUs 정보를 설정하거나, add_real_user_manual.py를 실행하세요.")
                
                # 실제 사용자 데이터 생성 (디버깅용)
                logger.info("🔧 디버깅용 실제 사용자 데이터 생성...")
                active_users = [
                    {
                        'uid': 'user_2024248012',
                        'username': '2024248012',
                        'password': 'cjm9887@',
                        'studentId': '2024248012',
                        'university': '연세대학교',
                        'isActive': True
                    }
                ]
                logger.info(f"✅ 실제 사용자 데이터 생성 완료: {len(active_users)}명")
            else:
                logger.info(f"{len(active_users)}명의 활성화된 사용자 발견")
                
                # 🚀 최적화된 배치 자동화 실행 (가능한 경우)
                if OPTIMIZED_MODULES_AVAILABLE and BatchAutomationScheduler:
                    logger.info("🚀 최적화된 배치 자동화 시작...")
                    try:
                        scheduler = BatchAutomationScheduler(
                            max_runtime_minutes=50,  # 50분 제한 (Cloud Run 60분 내에서 안전하게)
                            batch_size=3  # 한 번에 3명씩 처리
                        )
                        
                        result = scheduler.run_batch_automation()
                        scheduler.save_batch_results(result)
                        
                        logger.info(f"🎉 최적화된 배치 자동화 완료:")
                        logger.info(f"   총 사용자: {result.get('user_count', 0)}명")
                        logger.info(f"   성공: {result.get('successful_users', 0)}명")
                        logger.info(f"   실패: {result.get('failed_users', 0)}명")
                        logger.info(f"   총 과제: {result.get('total_count', 0)}개")
                        logger.info(f"   실행 시간: {result.get('execution_time', 0):.2f}초")
                    except Exception as optimized_error:
                        logger.error(f"❌ 최적화된 배치 자동화 실패: {optimized_error}")
                        logger.info("🔄 기본 자동화 방식으로 전환...")
                        result = run_basic_automation(active_users)
                else:
                    logger.info("🔄 기본 자동화 방식 사용...")
                    result = run_basic_automation(active_users)
                
        except Exception as firebase_error:
            logger.error(f"Firebase 연결 실패: {firebase_error}")
            result = {
                'assignments': [],
                'total_count': 0,
                'users_processed': 0,
                'message': f'Firebase 연결 실패: {firebase_error}',
                'firebase_status': 'disconnected',
                'user_count': 0
            }
        
        # 결과를 assignment.txt 파일에 저장
        save_assignment_data(result)
        
        _last_update_time = datetime.now()
        logger.info("최적화된 자동화 완료")
        
    except Exception as e:
        logger.error(f"자동화 실행 실패: {e}")
    finally:
        _automation_running = False

def save_assignment_data(automation_result):
    """자동화 결과를 assignment.txt 파일에 저장"""
    try:
        logger.info(f"🔍 save_assignment_data 호출됨")
        logger.info(f"🔍 automation_result 타입: {type(automation_result)}")
        logger.info(f"🔍 automation_result 내용: {automation_result}")
        
        # assignment.txt 파일 경로 (backend 디렉토리에 저장)
        backend_dir = os.path.dirname(os.path.abspath(__file__))
        assignment_file = os.path.join(backend_dir, "assignment.txt")
        logger.info(f"🔍 저장 경로: {assignment_file}")
        
        # 파일이 존재하면 읽어서 기존 데이터와 병합
        existing_data = []
        if os.path.exists(assignment_file):
            try:
                with open(assignment_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # 간단한 파싱 (실제로는 더 정교한 파싱 필요)
                    if "이번주 해야 할 과제 목록" in content:
                        existing_data = parse_assignment_file(content)
            except Exception as e:
                logger.warning(f"기존 파일 읽기 실패: {e}")
        
        # automation_result에서 실제 과제 데이터 추출
        new_assignments = []
        if automation_result and isinstance(automation_result, dict):
            # automation_result에 assignments 키가 있으면 직접 사용
            if 'assignments' in automation_result:
                logger.info(f"🔍 직접 assignments 추출: {len(automation_result['assignments'])}개")
                new_assignments = automation_result.get('assignments', [])
            else:
                # 각 사용자의 결과에서 과제 추출 (이전 방식)
                for user_id, user_result in automation_result.items():
                    if isinstance(user_result, dict) and user_result.get('success'):
                        user_assignments = user_result.get('assignments', [])
                        new_assignments.extend(user_assignments)
        
        # 전역 변수 업데이트
        global _assignment_data
        _assignment_data = new_assignments
        
        # 파일에 저장
        with open(assignment_file, 'w', encoding='utf-8') as f:
            f.write(f"=== LearnUs 과제 정보 업데이트 ===\n")
            f.write(f"업데이트 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            if _assignment_data:
                f.write("이번주 해야 할 과제 목록:\n")
                for assignment in _assignment_data:
                    course = assignment.get('course', '알 수 없음')
                    # title 키를 우선 사용 (실제 데이터 구조에 맞춤)
                    activity = assignment.get('title') or assignment.get('activity', '알 수 없음')
                    status = assignment.get('status', '상태 불명')
                    f.write(f"  • {course}: {activity} - {status}\n")
            else:
                f.write("이번주 과제가 없습니다.\n")
        
        logger.info(f"assignment.txt 파일 업데이트 완료")
        
    except Exception as e:
        logger.error(f"파일 저장 실패: {e}")

def parse_assignment_file(content):
    """assignment.txt 파일을 파싱하여 구조화된 데이터로 변환"""
    assignments = []
    lines = content.split('\n')
    
    for line in lines:
        if '•' in line and ':' in line:
            try:
                # "• 과목명: 활동명 - 상태" 형식 파싱
                parts = line.split('•')[1].strip()
                if ':' in parts and '-' in parts:
                    course_part, activity_part = parts.split(':', 1)
                    if '-' in activity_part:
                        activity, status = activity_part.rsplit('-', 1)
                        assignments.append({
                            'course': course_part.strip(),
                            'activity': activity.strip(),
                            'status': status.strip(),
                            'type': '과제',  # 기본값
                            'url': ''
                        })
            except Exception as e:
                logger.debug(f"파싱 실패: {line} - {e}")
    
    # 파일이 비어있을 경우 빈 리스트 반환 (더미 데이터 제거)
    if not assignments:
        logger.warning("⚠️ assignment.txt 파일이 비어있거나 파싱할 수 없습니다.")
        logger.info("💡 자동화가 실행되지 않았거나 실패했을 가능성이 있습니다.")
        assignments = []
    
    return assignments

@app.get("/health")
async def health_check():
    """헬스체크 엔드포인트"""
    return {
        "status": "healthy", 
        "message": "스케줄러 서버가 정상적으로 실행 중입니다",
        "last_update": _last_update_time.isoformat() if _last_update_time else None,
        "automation_running": _automation_running
    }

@app.get("/assignments")
async def get_assignments():
    """현재 저장된 과제 정보 조회"""
    try:
        global _assignment_data
        
        # assignment.txt 파일에서 최신 데이터 로드 (backend 디렉토리)
        backend_dir = os.path.dirname(os.path.abspath(__file__))
        assignment_file = os.path.join(backend_dir, "assignment.txt")
        if os.path.exists(assignment_file):
            with open(assignment_file, 'r', encoding='utf-8') as f:
                content = f.read()
                _assignment_data = parse_assignment_file(content)
        
        return {
            "assignments": _assignment_data,
            "total_count": len(_assignment_data),
            "incomplete_count": len([a for a in _assignment_data if "미완료" in a.get('status', '')]),
            "last_update": _last_update_time.isoformat() if _last_update_time else None
        }
    except Exception as e:
        logger.error(f"과제 정보 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/assignments/raw")
async def get_raw_assignments():
    """assignment.txt 파일 내용을 직접 반환"""
    try:
        # Docker 컨테이너 내부의 assignment.txt 파일 경로
        assignment_file = "/app/assignment.txt"
        if os.path.exists(assignment_file):
            with open(assignment_file, "r", encoding="utf-8") as f:
                content = f.read()
            return {"content": content, "status": "success"}
        else:
            return {"content": "assignment.txt 파일이 존재하지 않습니다.", "status": "error"}
    except Exception as e:
        logger.error(f"assignment.txt 파일 읽기 실패: {e}")
        return {"content": f"파일 읽기 실패: {str(e)}", "status": "error"}

@app.post("/automation/run")
async def run_automation_now():
    """즉시 자동화 실행"""
    try:
        if _automation_running:
            return {"message": "자동화가 이미 실행 중입니다", "status": "running"}
        
        # 백그라운드에서 실행
        threading.Thread(target=run_automation_job, daemon=True).start()
        
        return {"message": "자동화가 시작되었습니다", "status": "started"}
    except Exception as e:
        logger.error(f"자동화 실행 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/status")
async def get_status():
    """서버 상태 및 자동화 상태 조회"""
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    assignment_file = os.path.join(backend_dir, "assignment.txt")
    
    return {
        "server_status": "running",
        "automation_running": _automation_running,
        "last_update": _last_update_time.isoformat() if _last_update_time else None,
        "next_scheduled": "매일 09:00, 18:00 (개발용: 5분마다)",
        "assignment_file_exists": os.path.exists(assignment_file),
        "assignment_file_path": assignment_file
    }

# 앱 시작 시 실행
@app.on_event("startup")
async def startup_event():
    """앱 시작 시 실행"""
    logger.info("🚀 애플리케이션 시작...")
    
    # 초기화 대기 시간 추가
    logger.info("⏳ 초기화 대기 중...")
    import time
    time.sleep(5)  # 5초 대기
    
    # 환경 변수 확인
    logger.info("🔍 환경 변수 확인:")
    logger.info(f"   PORT: {os.environ.get('PORT', 'NOT SET')}")
    logger.info(f"   CHROME_DISABLED: {os.environ.get('CHROME_DISABLED', 'NOT SET')}")
    logger.info(f"   DISPLAY: {os.environ.get('DISPLAY', 'NOT SET')}")
    
    # 스케줄러 시작
    try:
        threading.Thread(target=start_scheduler_optimized, daemon=True).start()
        logger.info("📅 스케줄러 시작됨")
    except Exception as e:
        logger.error(f"❌ 스케줄러 시작 실패: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """앱 종료 시 실행"""
    logger.info("🛑 애플리케이션 종료...")

# Cloud Run에서는 uvicorn이 자동으로 실행됨
# 로컬 테스트용 (개발 시에만 사용)
if __name__ == "__main__":
    # FastAPI 서버 시작 (Cloud Run 환경 변수 처리)
    port = int(os.environ.get("PORT", 8080))
    logger.info(f"🚀 서버 시작 - PORT: {port}")
    logger.info(f"🔍 환경 변수 확인 - PORT: {os.environ.get('PORT', 'Not set')}")
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=port,
        log_level="info",
        workers=1
    )
