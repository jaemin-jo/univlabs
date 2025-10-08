#!/usr/bin/env python3
"""
클라우드 데이터를 주기적으로 로컬로 동기화하는 스케줄러
"""

import schedule
import time
import logging
import threading
from datetime import datetime
from sync_cloud_data import CloudDataSyncer

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AutoSyncScheduler:
    def __init__(self, sync_interval_minutes: int = 30):
        self.syncer = CloudDataSyncer()
        self.sync_interval = sync_interval_minutes
        self.running = False
        self.scheduler_thread = None
    
    def sync_job(self):
        """스케줄된 동기화 작업"""
        logger.info(f"🔄 자동 동기화 시작 ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})")
        
        try:
            success = self.syncer.sync()
            if success:
                logger.info("✅ 자동 동기화 완료")
            else:
                logger.error("❌ 자동 동기화 실패")
        except Exception as e:
            logger.error(f"❌ 자동 동기화 중 오류: {e}")
    
    def start_scheduler(self):
        """스케줄러 시작"""
        if self.running:
            logger.warning("스케줄러가 이미 실행 중입니다.")
            return
        
        logger.info(f"🕐 자동 동기화 스케줄러 시작 (간격: {self.sync_interval}분)")
        
        # 스케줄 등록
        schedule.every(self.sync_interval).minutes.do(self.sync_job)
        
        # 즉시 한 번 실행
        logger.info("🚀 초기 동기화 실행...")
        self.sync_job()
        
        self.running = True
        
        # 백그라운드에서 스케줄러 실행
        self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.scheduler_thread.start()
        
        logger.info("✅ 자동 동기화 스케줄러가 백그라운드에서 시작되었습니다.")
    
    def stop_scheduler(self):
        """스케줄러 중지"""
        if not self.running:
            logger.warning("스케줄러가 실행 중이 아닙니다.")
            return
        
        self.running = False
        schedule.clear()
        logger.info("⏹️ 자동 동기화 스케줄러가 중지되었습니다.")
    
    def _run_scheduler(self):
        """스케줄러 실행 루프"""
        while self.running:
            try:
                schedule.run_pending()
                time.sleep(60)  # 1분마다 체크
            except Exception as e:
                logger.error(f"스케줄러 실행 중 오류: {e}")
                time.sleep(60)
    
    def get_status(self):
        """스케줄러 상태 확인"""
        return {
            'running': self.running,
            'sync_interval': self.sync_interval,
            'next_run': schedule.next_run() if schedule.jobs else None
        }

def main():
    """메인 실행 함수"""
    print("🔄 LearnUs 자동 동기화 스케줄러")
    print("=" * 50)
    
    # 동기화 간격 설정 (기본: 30분)
    sync_interval = 30  # 분
    
    print(f"⏰ 동기화 간격: {sync_interval}분")
    print("🔄 스케줄러 시작 중...")
    
    scheduler = AutoSyncScheduler(sync_interval_minutes=sync_interval)
    
    try:
        # 스케줄러 시작
        scheduler.start_scheduler()
        
        print("✅ 자동 동기화 스케줄러가 시작되었습니다.")
        print(f"   동기화 간격: {sync_interval}분")
        print("   종료하려면 Ctrl+C를 누르세요.")
        print()
        
        # 상태 모니터링
        while True:
            status = scheduler.get_status()
            if status['running']:
                next_run = status['next_run']
                if next_run:
                    print(f"⏰ 다음 동기화: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
                else:
                    print("⏰ 다음 동기화: 스케줄 없음")
            else:
                print("⏹️ 스케줄러가 중지되었습니다.")
                break
            
            time.sleep(300)  # 5분마다 상태 출력
            
    except KeyboardInterrupt:
        print("\n⏹️ 사용자에 의해 중지됨")
        scheduler.stop_scheduler()
        print("✅ 자동 동기화 스케줄러가 중지되었습니다.")
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        scheduler.stop_scheduler()

if __name__ == "__main__":
    main()










