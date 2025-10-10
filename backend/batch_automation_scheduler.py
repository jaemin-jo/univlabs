#!/usr/bin/env python3
"""
배치 처리 자동화 스케줄러
- 사용자별 분할 처리
- 시간 제한 내에서 최대한 많은 사용자 처리
- 실패한 사용자는 다음 배치에서 재시도
"""

import asyncio
import json
import logging
import time
import os
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Optional
from firebase_service import get_all_active_users, update_user_last_used
from optimized_hybrid_automation import OptimizedHybridAutomation

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('batch_automation.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class BatchAutomationScheduler:
    def __init__(self, max_runtime_minutes=50, batch_size=3):
        """
        배치 처리 스케줄러 초기화
        
        Args:
            max_runtime_minutes: 최대 실행 시간 (분)
            batch_size: 한 번에 처리할 사용자 수
        """
        self.max_runtime_seconds = max_runtime_minutes * 60
        self.batch_size = batch_size
        self.start_time = None
        self.processed_users = []
        self.failed_users = []
        self.all_assignments = []
        
    def is_time_limit_reached(self):
        """시간 제한 확인"""
        if not self.start_time:
            return False
        
        elapsed_time = time.time() - self.start_time
        return elapsed_time >= self.max_runtime_seconds
    
    def get_remaining_time(self):
        """남은 시간 계산 (초)"""
        if not self.start_time:
            return self.max_runtime_seconds
        
        elapsed_time = time.time() - self.start_time
        return max(0, self.max_runtime_seconds - elapsed_time)
    
    def process_user_batch(self, users_batch):
        """사용자 배치 처리"""
        try:
            logger.info(f"🔄 배치 처리 시작: {len(users_batch)}명")
            
            batch_results = []
            
            # 각 사용자를 병렬로 처리
            with ThreadPoolExecutor(max_workers=min(self.batch_size, len(users_batch))) as executor:
                future_to_user = {
                    executor.submit(self.process_single_user, user): user 
                    for user in users_batch
                }
                
                # 완료된 작업들을 처리
                for future in as_completed(future_to_user):
                    user = future_to_user[future]
                    try:
                        result = future.result()
                        if result:
                            batch_results.extend(result)
                            self.processed_users.append(user.get('username', 'Unknown'))
                            logger.info(f"✅ {user.get('username', 'Unknown')} 처리 완료")
                        else:
                            self.failed_users.append(user.get('username', 'Unknown'))
                            logger.warning(f"⚠️ {user.get('username', 'Unknown')} 처리 실패")
                    except Exception as e:
                        self.failed_users.append(user.get('username', 'Unknown'))
                        logger.error(f"❌ {user.get('username', 'Unknown')} 처리 오류: {e}")
            
            return batch_results
            
        except Exception as e:
            logger.error(f"❌ 배치 처리 실패: {e}")
            return []
    
    def process_single_user(self, user):
        """단일 사용자 처리"""
        try:
            username = user.get('username', '')
            password = user.get('password', '')
            university = user.get('university', '연세대학교')
            student_id = user.get('studentId', '')
            
            logger.info(f"👤 {username} 처리 시작...")
            
            # 최적화된 자동화 실행
            automation = OptimizedHybridAutomation(max_workers=2)
            activities = automation.run_optimized_automation(username, password)
            
            if activities:
                # 사용자 정보 추가
                for activity in activities:
                    activity['user'] = username
                    activity['university'] = university
                    activity['student_id'] = student_id
                
                # 마지막 사용 시간 업데이트
                try:
                    update_user_last_used(user.get('uid', ''))
                    logger.info(f"📅 {username} 마지막 사용 시간 업데이트 완료")
                except Exception as e:
                    logger.warning(f"⚠️ {username} 마지막 사용 시간 업데이트 실패: {e}")
                
                logger.info(f"✅ {username} 처리 완료: {len(activities)}개 활동")
                return activities
            else:
                logger.warning(f"⚠️ {username} 처리 결과 없음")
                return []
                
        except Exception as e:
            logger.error(f"❌ {username} 처리 실패: {e}")
            return []
    
    def run_batch_automation(self):
        """배치 자동화 실행"""
        try:
            self.start_time = time.time()
            logger.info(f"🚀 배치 자동화 시작 (최대 {self.max_runtime_seconds//60}분)")
            
            # Firebase에서 활성화된 사용자 가져오기
            active_users = get_all_active_users()
            if not active_users:
                logger.warning("활성화된 사용자가 없습니다")
                return {
                    'assignments': [],
                    'total_count': 0,
                    'users_processed': 0,
                    'successful_users': 0,
                    'failed_users': 0,
                    'message': '활성화된 사용자가 없습니다',
                    'firebase_status': 'connected',
                    'user_count': 0
                }
            
            logger.info(f"👥 {len(active_users)}명의 활성화된 사용자 발견")
            
            # 사용자를 배치로 나누기
            user_batches = []
            for i in range(0, len(active_users), self.batch_size):
                batch = active_users[i:i + self.batch_size]
                user_batches.append(batch)
            
            logger.info(f"📦 {len(user_batches)}개 배치로 분할")
            
            # 각 배치를 순차적으로 처리
            for batch_index, user_batch in enumerate(user_batches):
                if self.is_time_limit_reached():
                    logger.warning(f"⏰ 시간 제한 도달, {batch_index}/{len(user_batches)} 배치 처리 완료")
                    break
                
                remaining_time = self.get_remaining_time()
                logger.info(f"🔄 배치 {batch_index + 1}/{len(user_batches)} 처리 시작 (남은 시간: {remaining_time//60}분)")
                
                batch_results = self.process_user_batch(user_batch)
                self.all_assignments.extend(batch_results)
                
                # 배치 간 대기 (서버 부하 방지)
                if batch_index < len(user_batches) - 1:
                    time.sleep(2)
            
            # 최종 결과 정리
            result = {
                'assignments': self.all_assignments,
                'total_count': len(self.all_assignments),
                'users_processed': len(self.processed_users),
                'successful_users': len(self.processed_users),
                'failed_users': len(self.failed_users),
                'firebase_status': 'connected',
                'user_count': len(active_users),
                'processed_user_list': self.processed_users,
                'failed_user_list': self.failed_users,
                'execution_time': time.time() - self.start_time
            }
            
            logger.info(f"🎉 배치 자동화 완료:")
            logger.info(f"   총 사용자: {len(active_users)}명")
            logger.info(f"   성공: {len(self.processed_users)}명")
            logger.info(f"   실패: {len(self.failed_users)}명")
            logger.info(f"   총 과제: {len(self.all_assignments)}개")
            logger.info(f"   실행 시간: {result['execution_time']:.2f}초")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ 배치 자동화 실패: {e}")
            return {
                'assignments': [],
                'total_count': 0,
                'users_processed': 0,
                'successful_users': 0,
                'failed_users': 0,
                'message': f'배치 자동화 실패: {e}',
                'firebase_status': 'disconnected',
                'user_count': 0
            }
    
    def save_batch_results(self, result):
        """배치 결과를 파일에 저장"""
        try:
            with open('batch_assignment.txt', 'w', encoding='utf-8') as f:
                f.write("📚 배치 처리 LearnUs 과제 정보\n")
                f.write("=" * 60 + "\n\n")
                f.write(f"수집 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"총 수집된 항목 수: {result['total_count']}개\n")
                f.write(f"처리된 사용자 수: {result['users_processed']}명\n")
                f.write(f"성공한 사용자: {result['successful_users']}명\n")
                f.write(f"실패한 사용자: {result['failed_users']}명\n")
                f.write(f"실행 시간: {result.get('execution_time', 0):.2f}초\n\n")
                
                if result['assignments']:
                    # 사용자별로 그룹화
                    user_groups = {}
                    for assignment in result['assignments']:
                        user = assignment.get('user', 'Unknown')
                        if user not in user_groups:
                            user_groups[user] = []
                        user_groups[user].append(assignment)
                    
                    # 사용자별로 출력
                    for user, user_assignments in user_groups.items():
                        f.write(f"👤 {user}\n")
                        f.write("-" * 50 + "\n")
                        
                        # 과목별로 그룹화
                        course_groups = {}
                        for assignment in user_assignments:
                            course = assignment.get('course', '알 수 없음')
                            if course not in course_groups:
                                course_groups[course] = []
                            course_groups[course].append(assignment)
                        
                        for course, course_assignments in course_groups.items():
                            f.write(f"  📖 {course}\n")
                            for assignment in course_assignments:
                                f.write(f"    • {assignment.get('activity', '알 수 없음')} ({assignment.get('type', '기타')}) - {assignment.get('status', '상태 불명')}\n")
                                if assignment.get('url'):
                                    f.write(f"      URL: {assignment['url']}\n")
                            f.write("\n")
                        f.write("\n")
                else:
                    f.write("⚠️ 과제 정보를 찾을 수 없습니다\n")
            
            logger.info("💾 배치 결과가 batch_assignment.txt 파일에 저장되었습니다")
            
        except Exception as e:
            logger.error(f"❌ 배치 결과 저장 실패: {e}")

def main():
    """메인 함수"""
    print("🚀 배치 처리 자동화 스케줄러")
    print("=" * 60)
    print("⚡ 사용자별 분할 처리")
    print("⏰ 시간 제한 내에서 최대 처리")
    print("🔄 실패한 사용자는 다음 배치에서 재시도")
    print()
    
    # 배치 설정
    max_runtime = int(input("최대 실행 시간 (분, 기본값 50): ") or "50")
    batch_size = int(input("배치 크기 (기본값 3): ") or "3")
    
    print()
    print("🔧 배치 자동화 시작...")
    
    # 배치 자동화 실행
    scheduler = BatchAutomationScheduler(
        max_runtime_minutes=max_runtime,
        batch_size=batch_size
    )
    
    result = scheduler.run_batch_automation()
    scheduler.save_batch_results(result)
    
    if result['assignments']:
        print(f"✅ 배치 자동화 완료: {result['total_count']}개 활동")
        print(f"👥 처리된 사용자: {result['users_processed']}명")
        print("📄 batch_assignment.txt 파일을 확인하세요.")
    else:
        print("❌ 배치 자동화 실패")

if __name__ == "__main__":
    main()
