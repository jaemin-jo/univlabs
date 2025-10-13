#!/usr/bin/env python3
"""
고급 로컬 테스트 파이프라인 - 상세한 디버깅 및 오류 분석
Cloud Run 배포 과정의 모든 단계를 상세히 분석하고 오류 지점을 정확히 찾아냄
"""

import os
import sys
import subprocess
import time
import logging
import requests
import json
import re
from datetime import datetime
from pathlib import Path

# 로깅 설정
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('advanced_pipeline_test.log')
    ]
)
logger = logging.getLogger(__name__)

class AdvancedTestPipeline:
    def __init__(self):
        self.project_dir = os.path.dirname(os.path.abspath(__file__))
        self.docker_image = "learnus-backend-advanced-test"
        self.container_name = "learnus-backend-advanced-test-container"
        self.port = 8080
        self.test_results = {}
        self.docker_logs = []
        self.application_logs = []
        
    def log_step(self, step_name, status, message="", details=None):
        """테스트 단계 상세 로깅"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        status_icon = "✅" if status == "SUCCESS" else "❌" if status == "FAILED" else "🔧"
        logger.info(f"{status_icon} [{timestamp}] {step_name}: {status}")
        if message:
            logger.info(f"   📝 {message}")
        if details:
            logger.info(f"   🔍 상세: {details}")
        
        self.test_results[step_name] = {
            "status": status,
            "message": message,
            "details": details,
            "timestamp": timestamp
        }
    
    def run_command_with_analysis(self, command, description="", timeout=300):
        """명령어 실행 및 상세 분석"""
        try:
            logger.info(f"🔧 실행 중: {command}")
            if description:
                logger.info(f"   📝 {description}")
            
            start_time = time.time()
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True, 
                cwd=self.project_dir,
                timeout=timeout
            )
            end_time = time.time()
            duration = end_time - start_time
            
            logger.info(f"⏱️ 실행 시간: {duration:.2f}초")
            
            if result.returncode == 0:
                logger.info(f"✅ 성공: {command}")
                if result.stdout:
                    logger.info(f"   📤 표준 출력:")
                    for line in result.stdout.strip().split('\n'):
                        if line.strip():
                            logger.info(f"      {line}")
                return True, result.stdout, result.stderr, duration
            else:
                logger.error(f"❌ 실패: {command}")
                logger.error(f"   📤 오류 코드: {result.returncode}")
                if result.stderr:
                    logger.error(f"   📤 오류 출력:")
                    for line in result.stderr.strip().split('\n'):
                        if line.strip():
                            logger.error(f"      {line}")
                return False, result.stdout, result.stderr, duration
                
        except subprocess.TimeoutExpired:
            logger.error(f"⏰ 타임아웃: {command} (>{timeout}초)")
            return False, "", "Command timeout", timeout
        except Exception as e:
            logger.error(f"❌ 명령어 실행 예외: {e}")
            return False, "", str(e), 0
    
    def analyze_docker_build_logs(self, logs):
        """Docker 빌드 로그 분석"""
        logger.info("🔍 Docker 빌드 로그 분석 중...")
        
        # 일반적인 Docker 빌드 오류 패턴
        error_patterns = [
            (r"ERROR.*", "Docker 빌드 오류"),
            (r"failed to solve.*", "의존성 해결 실패"),
            (r"no such file.*", "파일 없음 오류"),
            (r"permission denied.*", "권한 오류"),
            (r"connection.*refused.*", "연결 거부"),
            (r"timeout.*", "타임아웃 오류"),
            (r"SyntaxError.*", "Python 구문 오류"),
            (r"ImportError.*", "Python 모듈 import 오류"),
            (r"ModuleNotFoundError.*", "Python 모듈 없음 오류")
        ]
        
        found_errors = []
        for pattern, description in error_patterns:
            matches = re.findall(pattern, logs, re.IGNORECASE)
            if matches:
                found_errors.append(f"{description}: {matches[0]}")
        
        if found_errors:
            logger.error("🚨 발견된 오류:")
            for error in found_errors:
                logger.error(f"   ❌ {error}")
        else:
            logger.info("✅ 특별한 오류 패턴이 발견되지 않음")
        
        return found_errors
    
    def analyze_container_logs(self, logs):
        """컨테이너 로그 분석"""
        logger.info("🔍 컨테이너 로그 분석 중...")
        
        # 애플리케이션 시작 관련 로그
        startup_patterns = [
            (r"Starting server.*", "서버 시작"),
            (r"FastAPI.*", "FastAPI 시작"),
            (r"Uvicorn.*", "Uvicorn 시작"),
            (r"Listening on.*", "포트 리스닝"),
            (r"Application startup complete.*", "애플리케이션 시작 완료")
        ]
        
        # 오류 관련 로그
        error_patterns = [
            (r"ERROR.*", "일반 오류"),
            (r"CRITICAL.*", "치명적 오류"),
            (r"Exception.*", "예외 발생"),
            (r"Traceback.*", "스택 트레이스"),
            (r"SyntaxError.*", "구문 오류"),
            (r"ImportError.*", "Import 오류"),
            (r"ModuleNotFoundError.*", "모듈 없음 오류"),
            (r"Connection.*refused.*", "연결 거부"),
            (r"Port.*already in use.*", "포트 사용 중"),
            (r"Permission.*denied.*", "권한 거부")
        ]
        
        startup_events = []
        error_events = []
        
        for pattern, description in startup_patterns:
            matches = re.findall(pattern, logs, re.IGNORECASE)
            for match in matches:
                startup_events.append(f"{description}: {match}")
        
        for pattern, description in error_patterns:
            matches = re.findall(pattern, logs, re.IGNORECASE)
            for match in matches:
                error_events.append(f"{description}: {match}")
        
        logger.info("📊 시작 이벤트:")
        for event in startup_events:
            logger.info(f"   ✅ {event}")
        
        if error_events:
            logger.error("🚨 오류 이벤트:")
            for event in error_events:
                logger.error(f"   ❌ {event}")
        else:
            logger.info("✅ 오류 이벤트 없음")
        
        return startup_events, error_events
    
    def step_1_environment_analysis(self):
        """1단계: 환경 상세 분석"""
        logger.info("=" * 80)
        logger.info("🔧 1단계: 환경 상세 분석")
        logger.info("=" * 80)
        
        # 시스템 정보
        success, output, error, duration = self.run_command_with_analysis("python --version", "Python 버전")
        if success:
            self.log_step("Python 버전", "SUCCESS", output.strip())
        else:
            self.log_step("Python 버전", "FAILED", error)
            return False
        
        # Docker 상세 정보
        success, output, error, duration = self.run_command_with_analysis("docker --version", "Docker 버전")
        if success:
            self.log_step("Docker 버전", "SUCCESS", output.strip())
        else:
            self.log_step("Docker 버전", "FAILED", error)
            return False
        
        # Docker 데몬 상태
        success, output, error, duration = self.run_command_with_analysis("docker info", "Docker 데몬 상태")
        if success:
            self.log_step("Docker 데몬", "SUCCESS", "Docker 데몬 실행 중")
        else:
            self.log_step("Docker 데몬", "FAILED", "Docker 데몬이 실행되지 않음")
            return False
        
        # 파일 구조 분석
        logger.info("📁 파일 구조 분석:")
        required_files = [
            "Dockerfile",
            "requirements.txt", 
            "scheduler_server.py",
            "test_real_automation_hybrid.py",
            "simple_test_server.py"
        ]
        
        for file in required_files:
            file_path = os.path.join(self.project_dir, file)
            if os.path.exists(file_path):
                size = os.path.getsize(file_path)
                logger.info(f"   ✅ {file}: {size} bytes")
            else:
                logger.error(f"   ❌ {file}: 파일 없음")
                self.log_step("필수 파일 확인", "FAILED", f"누락된 파일: {file}")
                return False
        
        # Python 모듈 import 테스트
        logger.info("🐍 Python 모듈 import 테스트:")
        test_imports = [
            "import fastapi",
            "import uvicorn", 
            "import selenium",
            "import requests",
            "import schedule"
        ]
        
        for import_cmd in test_imports:
            success, output, error, duration = self.run_command_with_analysis(f"python -c \"{import_cmd}\"", f"Python 모듈 테스트: {import_cmd}")
            if success:
                logger.info(f"   ✅ {import_cmd}")
            else:
                logger.error(f"   ❌ {import_cmd}: {error}")
        
        self.log_step("환경 분석", "SUCCESS", "환경 분석 완료")
        return True
    
    def step_2_docker_build_analysis(self):
        """2단계: Docker 빌드 상세 분석"""
        logger.info("=" * 80)
        logger.info("🔧 2단계: Docker 빌드 상세 분석")
        logger.info("=" * 80)
        
        # 기존 리소스 정리
        logger.info("🧹 기존 리소스 정리 중...")
        self.run_command_with_analysis(f"docker stop {self.container_name} || true", "기존 컨테이너 중지")
        self.run_command_with_analysis(f"docker rm {self.container_name} || true", "기존 컨테이너 제거")
        self.run_command_with_analysis(f"docker rmi {self.docker_image} || true", "기존 이미지 제거")
        
        # Docker 빌드 실행
        build_command = f"docker build -t {self.docker_image} ."
        success, output, error, duration = self.run_command_with_analysis(
            build_command, 
            "Docker 이미지 빌드", 
            timeout=600
        )
        
        if success:
            self.log_step("Docker 빌드", "SUCCESS", f"빌드 완료 ({duration:.2f}초)")
            
            # 빌드 로그 분석
            all_logs = output + error
            build_errors = self.analyze_docker_build_logs(all_logs)
            
            if build_errors:
                self.log_step("빌드 로그 분석", "WARNING", f"발견된 문제: {len(build_errors)}개")
            else:
                self.log_step("빌드 로그 분석", "SUCCESS", "빌드 로그에 문제 없음")
            
            return True
        else:
            self.log_step("Docker 빌드", "FAILED", f"빌드 실패 ({duration:.2f}초)")
            
            # 빌드 실패 로그 분석
            all_logs = output + error
            build_errors = self.analyze_docker_build_logs(all_logs)
            
            self.log_step("빌드 실패 분석", "FAILED", f"발견된 오류: {len(build_errors)}개")
            return False
    
    def step_3_container_start_analysis(self):
        """3단계: 컨테이너 시작 상세 분석"""
        logger.info("=" * 80)
        logger.info("🔧 3단계: 컨테이너 시작 상세 분석")
        logger.info("=" * 80)
        
        # 컨테이너 시작
        start_command = f"docker run -d --name {self.container_name} -p {self.port}:8080 {self.docker_image}"
        success, output, error, duration = self.run_command_with_analysis(start_command, "컨테이너 시작")
        
        if not success:
            self.log_step("컨테이너 시작", "FAILED", f"시작 실패: {error}")
            return False
        
        self.log_step("컨테이너 시작", "SUCCESS", f"시작 완료 ({duration:.2f}초)")
        
        # 컨테이너 상태 모니터링
        logger.info("📊 컨테이너 상태 모니터링 중...")
        for i in range(30):  # 30초간 모니터링
            success, output, error, duration = self.run_command_with_analysis(f"docker ps | grep {self.container_name}", "컨테이너 상태 확인")
            if success:
                logger.info(f"   ✅ 컨테이너 실행 중 ({i+1}/30)")
            else:
                logger.error(f"   ❌ 컨테이너 중지됨 ({i+1}/30)")
                break
            time.sleep(1)
        
        # 컨테이너 로그 수집 및 분석
        logger.info("📋 컨테이너 로그 수집 중...")
        success, logs, error, duration = self.run_command_with_analysis(f"docker logs {self.container_name}", "컨테이너 로그 수집")
        
        if success:
            self.docker_logs = logs
            startup_events, error_events = self.analyze_container_logs(logs)
            
            if error_events:
                self.log_step("컨테이너 로그 분석", "FAILED", f"오류 이벤트: {len(error_events)}개")
            else:
                self.log_step("컨테이너 로그 분석", "SUCCESS", f"시작 이벤트: {len(startup_events)}개")
        
        return True
    
    def step_4_application_deep_test(self):
        """4단계: 애플리케이션 심층 테스트"""
        logger.info("=" * 80)
        logger.info("🔧 4단계: 애플리케이션 심층 테스트")
        logger.info("=" * 80)
        
        # HTTP 엔드포인트 상세 테스트
        test_endpoints = [
            ("/", "루트 엔드포인트"),
            ("/health", "헬스 체크"),
            ("/env", "환경 변수"),
            ("/docs", "API 문서")
        ]
        
        for endpoint, description in test_endpoints:
            url = f"http://localhost:{self.port}{endpoint}"
            try:
                logger.info(f"🌐 테스트 중: {url} ({description})")
                response = requests.get(url, timeout=10)
                
                if response.status_code == 200:
                    self.log_step(f"HTTP 테스트: {endpoint}", "SUCCESS", f"상태: {response.status_code}")
                    logger.info(f"   📤 응답 길이: {len(response.text)} 문자")
                    logger.info(f"   📤 응답 미리보기: {response.text[:100]}...")
                else:
                    self.log_step(f"HTTP 테스트: {endpoint}", "FAILED", f"상태: {response.status_code}")
                    logger.error(f"   📤 응답: {response.text[:200]}")
                    
            except requests.exceptions.ConnectionError:
                self.log_step(f"HTTP 테스트: {endpoint}", "FAILED", "연결 거부 - 서버가 시작되지 않음")
            except requests.exceptions.Timeout:
                self.log_step(f"HTTP 테스트: {endpoint}", "FAILED", "타임아웃 - 서버 응답 없음")
            except Exception as e:
                self.log_step(f"HTTP 테스트: {endpoint}", "FAILED", f"예외: {str(e)}")
        
        # 컨테이너 내부 프로세스 확인
        logger.info("🔍 컨테이너 내부 프로세스 확인:")
        success, output, error, duration = self.run_command_with_analysis(f"docker exec {self.container_name} ps aux", "컨테이너 내부 프로세스")
        if success:
            logger.info("   📊 실행 중인 프로세스:")
            for line in output.split('\n'):
                if 'python' in line or 'uvicorn' in line:
                    logger.info(f"      {line}")
        
        # 포트 리스닝 확인
        logger.info("🔍 포트 리스닝 확인:")
        success, output, error, duration = self.run_command_with_analysis(f"docker exec {self.container_name} netstat -tlnp", "포트 리스닝 상태")
        if success:
            logger.info("   📊 리스닝 포트:")
            for line in output.split('\n'):
                if ':8080' in line or ':80' in line:
                    logger.info(f"      {line}")
        
        return True
    
    def step_5_cleanup_and_report(self):
        """5단계: 정리 및 상세 리포트"""
        logger.info("=" * 80)
        logger.info("🔧 5단계: 정리 및 상세 리포트")
        logger.info("=" * 80)
        
        # 컨테이너 중지 및 제거
        self.run_command_with_analysis(f"docker stop {self.container_name}", "컨테이너 중지")
        self.run_command_with_analysis(f"docker rm {self.container_name}", "컨테이너 제거")
        self.run_command_with_analysis(f"docker rmi {self.docker_image}", "이미지 제거")
        
        self.log_step("정리", "SUCCESS", "테스트 환경 정리 완료")
        
        # 상세 리포트 생성
        self.generate_detailed_report()
        
        return True
    
    def generate_detailed_report(self):
        """상세 테스트 결과 리포트 생성"""
        logger.info("=" * 80)
        logger.info("📊 상세 테스트 결과 리포트")
        logger.info("=" * 80)
        
        total_steps = len(self.test_results)
        success_steps = sum(1 for result in self.test_results.values() if result["status"] == "SUCCESS")
        failed_steps = sum(1 for result in self.test_results.values() if result["status"] == "FAILED")
        
        logger.info(f"📈 전체 단계: {total_steps}")
        logger.info(f"✅ 성공: {success_steps}")
        logger.info(f"❌ 실패: {failed_steps}")
        logger.info(f"📊 성공률: {(success_steps/total_steps)*100:.1f}%")
        
        logger.info("\n📋 상세 결과:")
        for step_name, result in self.test_results.items():
            status_icon = "✅" if result["status"] == "SUCCESS" else "❌"
            logger.info(f"   {status_icon} {step_name}: {result['status']}")
            if result["message"]:
                logger.info(f"      📝 {result['message']}")
            if result.get("details"):
                logger.info(f"      🔍 {result['details']}")
        
        # 실패한 단계 상세 분석
        if failed_steps > 0:
            logger.info("\n🔍 실패한 단계 상세 분석:")
            for step_name, result in self.test_results.items():
                if result["status"] == "FAILED":
                    logger.info(f"\n❌ {step_name}:")
                    logger.info(f"   시간: {result['timestamp']}")
                    logger.info(f"   오류: {result['message']}")
                    if result.get("details"):
                        logger.info(f"   상세: {result['details']}")
        
        # 권장사항
        logger.info("\n💡 권장사항:")
        if failed_steps == 0:
            logger.info("   🎉 모든 테스트가 성공했습니다!")
            logger.info("   🚀 Cloud Run 배포 준비가 완료되었습니다!")
        else:
            logger.info("   🔧 실패한 단계를 수정한 후 다시 테스트하세요.")
            logger.info("   📋 advanced_pipeline_test.log 파일을 확인하여 상세 오류를 분석하세요.")
        
        return success_steps == total_steps
    
    def run_advanced_pipeline(self):
        """고급 파이프라인 실행"""
        logger.info("🚀 고급 로컬 테스트 파이프라인 시작")
        logger.info(f"📁 프로젝트 디렉토리: {self.project_dir}")
        logger.info(f"🐳 Docker 이미지: {self.docker_image}")
        logger.info(f"📦 컨테이너 이름: {self.container_name}")
        logger.info(f"🌐 포트: {self.port}")
        
        start_time = time.time()
        
        try:
            # 1단계: 환경 상세 분석
            if not self.step_1_environment_analysis():
                logger.error("❌ 환경 분석 실패 - 파이프라인 중단")
                return False
            
            # 2단계: Docker 빌드 상세 분석
            if not self.step_2_docker_build_analysis():
                logger.error("❌ Docker 빌드 실패 - 파이프라인 중단")
                return False
            
            # 3단계: 컨테이너 시작 상세 분석
            if not self.step_3_container_start_analysis():
                logger.error("❌ 컨테이너 시작 실패 - 파이프라인 중단")
                return False
            
            # 4단계: 애플리케이션 심층 테스트
            if not self.step_4_application_deep_test():
                logger.error("❌ 애플리케이션 테스트 실패")
            
            # 5단계: 정리 및 상세 리포트
            self.step_5_cleanup_and_report()
            
        except Exception as e:
            logger.error(f"❌ 파이프라인 실행 중 예외 발생: {e}")
            self.step_5_cleanup_and_report()
            return False
        
        finally:
            end_time = time.time()
            duration = end_time - start_time
            
            logger.info(f"\n⏱️ 총 실행 시간: {duration:.2f}초")
            
            success = self.generate_detailed_report()
            
            if success:
                logger.info("🎉 고급 파이프라인 테스트 성공!")
            else:
                logger.info("💥 고급 파이프라인 테스트 실패!")
            
            return success

def main():
    """메인 함수"""
    print("🔧 Cloud Run 고급 로컬 테스트 파이프라인")
    print("=" * 80)
    print("이 파이프라인은 Cloud Run 배포 과정을 로컬에서 상세히 분석합니다.")
    print("환경 분석 → Docker 빌드 분석 → 컨테이너 시작 분석 → 애플리케이션 심층 테스트 → 상세 리포트")
    print("=" * 80)
    
    pipeline = AdvancedTestPipeline()
    success = pipeline.run_advanced_pipeline()
    
    if success:
        print("\n✅ 모든 테스트가 성공했습니다!")
        print("🚀 Cloud Run 배포 준비 완료!")
    else:
        print("\n❌ 일부 테스트가 실패했습니다.")
        print("🔍 advanced_pipeline_test.log 파일을 확인하여 상세 오류를 분석하세요.")
        sys.exit(1)

if __name__ == "__main__":
    main()
