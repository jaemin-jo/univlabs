#!/usr/bin/env python3
"""
로컬 테스트 파이프라인 - Cloud Run 배포 과정 전체 테스트
Docker 빌드, 컨테이너 실행, 애플리케이션 테스트까지 모든 과정을 로컬에서 검증
"""

import os
import sys
import subprocess
import time
import logging
import requests
import json
from datetime import datetime

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('pipeline_test.log')
    ]
)
logger = logging.getLogger(__name__)

class LocalTestPipeline:
    def __init__(self):
        self.project_dir = os.path.dirname(os.path.abspath(__file__))
        self.docker_image = "learnus-backend-test"
        self.container_name = "learnus-backend-test-container"
        self.port = 8080
        self.test_results = {}
        
    def log_step(self, step_name, status, message=""):
        """테스트 단계 로깅"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        status_icon = "✅" if status == "SUCCESS" else "❌" if status == "FAILED" else "🔧"
        logger.info(f"{status_icon} [{timestamp}] {step_name}: {status}")
        if message:
            logger.info(f"   📝 {message}")
        
        self.test_results[step_name] = {
            "status": status,
            "message": message,
            "timestamp": timestamp
        }
    
    def run_command(self, command, description=""):
        """명령어 실행 및 결과 반환"""
        try:
            logger.info(f"🔧 실행 중: {command}")
            if description:
                logger.info(f"   📝 {description}")
            
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True, 
                cwd=self.project_dir
            )
            
            if result.returncode == 0:
                logger.info(f"✅ 성공: {command}")
                if result.stdout:
                    logger.info(f"   📤 출력: {result.stdout.strip()}")
                return True, result.stdout
            else:
                logger.error(f"❌ 실패: {command}")
                logger.error(f"   📤 오류: {result.stderr.strip()}")
                return False, result.stderr
                
        except Exception as e:
            logger.error(f"❌ 명령어 실행 예외: {e}")
            return False, str(e)
    
    def step_1_check_environment(self):
        """1단계: 환경 확인"""
        logger.info("=" * 60)
        logger.info("🔧 1단계: 환경 확인")
        logger.info("=" * 60)
        
        # Python 버전 확인
        success, output = self.run_command("python --version", "Python 버전 확인")
        if success:
            self.log_step("Python 버전 확인", "SUCCESS", output.strip())
        else:
            self.log_step("Python 버전 확인", "FAILED", output)
            return False
        
        # Docker 확인
        success, output = self.run_command("docker --version", "Docker 버전 확인")
        if success:
            self.log_step("Docker 확인", "SUCCESS", output.strip())
        else:
            self.log_step("Docker 확인", "FAILED", output)
            return False
        
        # 필요한 파일들 확인
        required_files = [
            "Dockerfile",
            "requirements.txt", 
            "scheduler_server.py",
            "test_real_automation_hybrid.py",
            "simple_test_server.py"
        ]
        
        missing_files = []
        for file in required_files:
            if not os.path.exists(os.path.join(self.project_dir, file)):
                missing_files.append(file)
        
        if missing_files:
            self.log_step("필수 파일 확인", "FAILED", f"누락된 파일: {missing_files}")
            return False
        else:
            self.log_step("필수 파일 확인", "SUCCESS", "모든 필수 파일 존재")
        
        return True
    
    def step_2_docker_build(self):
        """2단계: Docker 이미지 빌드"""
        logger.info("=" * 60)
        logger.info("🔧 2단계: Docker 이미지 빌드")
        logger.info("=" * 60)
        
        # 기존 컨테이너 정리
        self.run_command(f"docker stop {self.container_name} || true", "기존 컨테이너 정리")
        self.run_command(f"docker rm {self.container_name} || true", "기존 컨테이너 제거")
        
        # Docker 이미지 빌드
        build_command = f"docker build -t {self.docker_image} ."
        success, output = self.run_command(build_command, "Docker 이미지 빌드")
        
        if success:
            self.log_step("Docker 빌드", "SUCCESS", "이미지 빌드 완료")
            return True
        else:
            self.log_step("Docker 빌드", "FAILED", output)
            return False
    
    def step_3_container_start(self):
        """3단계: 컨테이너 시작"""
        logger.info("=" * 60)
        logger.info("🔧 3단계: 컨테이너 시작")
        logger.info("=" * 60)
        
        # 컨테이너 시작
        start_command = f"docker run -d --name {self.container_name} -p {self.port}:8080 {self.docker_image}"
        success, output = self.run_command(start_command, "컨테이너 시작")
        
        if success:
            self.log_step("컨테이너 시작", "SUCCESS", "컨테이너 시작 완료")
            
            # 컨테이너 시작 대기
            logger.info("⏳ 컨테이너 시작 대기 중...")
            time.sleep(10)
            
            # 컨테이너 상태 확인
            success, output = self.run_command(f"docker ps | grep {self.container_name}", "컨테이너 상태 확인")
            if success:
                self.log_step("컨테이너 상태", "SUCCESS", "컨테이너 실행 중")
                return True
            else:
                self.log_step("컨테이너 상태", "FAILED", "컨테이너가 실행되지 않음")
                return False
        else:
            self.log_step("컨테이너 시작", "FAILED", output)
            return False
    
    def step_4_application_test(self):
        """4단계: 애플리케이션 테스트"""
        logger.info("=" * 60)
        logger.info("🔧 4단계: 애플리케이션 테스트")
        logger.info("=" * 60)
        
        # 컨테이너 로그 확인
        logger.info("📋 컨테이너 로그 확인...")
        success, output = self.run_command(f"docker logs {self.container_name}", "컨테이너 로그 확인")
        if success:
            logger.info("📋 컨테이너 로그:")
            for line in output.split('\n')[-20:]:  # 마지막 20줄만 표시
                if line.strip():
                    logger.info(f"   {line}")
        
        # HTTP 엔드포인트 테스트
        test_urls = [
            f"http://localhost:{self.port}/",
            f"http://localhost:{self.port}/health",
            f"http://localhost:{self.port}/env"
        ]
        
        for url in test_urls:
            try:
                logger.info(f"🌐 테스트 중: {url}")
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    self.log_step(f"HTTP 테스트: {url}", "SUCCESS", f"상태 코드: {response.status_code}")
                    logger.info(f"   📤 응답: {response.text[:200]}...")
                else:
                    self.log_step(f"HTTP 테스트: {url}", "FAILED", f"상태 코드: {response.status_code}")
            except Exception as e:
                self.log_step(f"HTTP 테스트: {url}", "FAILED", str(e))
        
        return True
    
    def step_5_cleanup(self):
        """5단계: 정리"""
        logger.info("=" * 60)
        logger.info("🔧 5단계: 정리")
        logger.info("=" * 60)
        
        # 컨테이너 중지 및 제거
        self.run_command(f"docker stop {self.container_name}", "컨테이너 중지")
        self.run_command(f"docker rm {self.container_name}", "컨테이너 제거")
        
        self.log_step("정리", "SUCCESS", "테스트 환경 정리 완료")
        return True
    
    def generate_report(self):
        """테스트 결과 리포트 생성"""
        logger.info("=" * 60)
        logger.info("📊 테스트 결과 리포트")
        logger.info("=" * 60)
        
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
        
        # 실패한 단계가 있으면 상세 로그 출력
        if failed_steps > 0:
            logger.info("\n🔍 실패한 단계 상세 로그:")
            for step_name, result in self.test_results.items():
                if result["status"] == "FAILED":
                    logger.info(f"\n❌ {step_name}:")
                    logger.info(f"   시간: {result['timestamp']}")
                    logger.info(f"   오류: {result['message']}")
        
        return success_steps == total_steps
    
    def run_full_pipeline(self):
        """전체 파이프라인 실행"""
        logger.info("🚀 로컬 테스트 파이프라인 시작")
        logger.info(f"📁 프로젝트 디렉토리: {self.project_dir}")
        logger.info(f"🐳 Docker 이미지: {self.docker_image}")
        logger.info(f"📦 컨테이너 이름: {self.container_name}")
        logger.info(f"🌐 포트: {self.port}")
        
        start_time = time.time()
        
        try:
            # 1단계: 환경 확인
            if not self.step_1_check_environment():
                logger.error("❌ 환경 확인 실패 - 파이프라인 중단")
                return False
            
            # 2단계: Docker 빌드
            if not self.step_2_docker_build():
                logger.error("❌ Docker 빌드 실패 - 파이프라인 중단")
                return False
            
            # 3단계: 컨테이너 시작
            if not self.step_3_container_start():
                logger.error("❌ 컨테이너 시작 실패 - 파이프라인 중단")
                return False
            
            # 4단계: 애플리케이션 테스트
            if not self.step_4_application_test():
                logger.error("❌ 애플리케이션 테스트 실패")
            
            # 5단계: 정리
            self.step_5_cleanup()
            
        except Exception as e:
            logger.error(f"❌ 파이프라인 실행 중 예외 발생: {e}")
            self.step_5_cleanup()
            return False
        
        finally:
            # 최종 리포트 생성
            end_time = time.time()
            duration = end_time - start_time
            
            logger.info(f"\n⏱️ 총 실행 시간: {duration:.2f}초")
            
            success = self.generate_report()
            
            if success:
                logger.info("🎉 파이프라인 테스트 성공!")
            else:
                logger.info("💥 파이프라인 테스트 실패!")
            
            return success

def main():
    """메인 함수"""
    print("🔧 Cloud Run 로컬 테스트 파이프라인")
    print("=" * 60)
    print("이 파이프라인은 Cloud Run 배포 과정을 로컬에서 완전히 테스트합니다.")
    print("Docker 빌드 → 컨테이너 시작 → 애플리케이션 테스트 → 정리")
    print("=" * 60)
    
    pipeline = LocalTestPipeline()
    success = pipeline.run_full_pipeline()
    
    if success:
        print("\n✅ 모든 테스트가 성공했습니다!")
        print("🚀 Cloud Run 배포 준비 완료!")
    else:
        print("\n❌ 일부 테스트가 실패했습니다.")
        print("🔍 pipeline_test.log 파일을 확인하여 상세 오류를 확인하세요.")
        sys.exit(1)

if __name__ == "__main__":
    main()
