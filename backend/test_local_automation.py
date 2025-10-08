#!/usr/bin/env python3
"""
로컬에서 클라우드와 동일한 자동화 코드 실행
"""

import sys
import os
import logging
from datetime import datetime

# 현재 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_local_automation():
    """로컬에서 자동화 테스트"""
    try:
        logger.info("🔧 로컬 자동화 테스트 시작")
        
        # 1. Firebase 사용자 조회
        logger.info("📋 Firebase에서 활성화된 사용자 조회 중...")
        try:
            from firebase_service import get_all_active_users
            active_users = get_all_active_users()
            logger.info(f"✅ Firebase 연결 성공: {len(active_users)}명의 사용자 발견")
            
            if not active_users:
                logger.warning("⚠️ 활성화된 사용자가 없습니다.")
                logger.info("💡 해결방법:")
                logger.info("   1. Flutter 앱에서 LearnUs 정보 설정")
                logger.info("   2. 또는 add_real_user_manual.py 실행")
                return
                
        except Exception as e:
            logger.error(f"❌ Firebase 연결 실패: {e}")
            logger.info("💡 Firebase 설정을 확인해주세요.")
            return
        
        # 2. 자동화 실행
        logger.info("🤖 자동화 실행 중...")
        try:
            from test_real_automation_hybrid import test_direct_selenium
            
            all_assignments = []
            for i, user in enumerate(active_users, 1):
                username = user.get('username', '')
                password = user.get('password', '')
                university = user.get('university', '')
                student_id = user.get('studentId', '')
                
                logger.info(f"👤 사용자 {i}/{len(active_users)}: {username} ({university})")
                
                if username and password:
                    try:
                        # 자동화 실행
                        result = test_direct_selenium(university, username, password, student_id)
                        
                        if result and result.get('assignments'):
                            assignments = result['assignments']
                            all_assignments.extend(assignments)
                            logger.info(f"✅ {username}: {len(assignments)}개 과제 발견")
                        else:
                            logger.warning(f"⚠️ {username}: 과제 없음")
                            
                    except Exception as user_error:
                        logger.error(f"❌ {username} 자동화 실패: {user_error}")
                        continue
                else:
                    logger.warning(f"⚠️ {username}: 로그인 정보 불완전")
            
            # 3. 결과 저장
            if all_assignments:
                logger.info(f"📊 전체 결과: {len(all_assignments)}개 과제")
                
                # assignment.txt 파일에 저장
                save_assignments_to_file(all_assignments)
                logger.info("💾 assignment.txt 파일에 저장 완료")
                
            else:
                logger.warning("⚠️ 수집된 과제가 없습니다.")
                
        except Exception as e:
            logger.error(f"❌ 자동화 실행 실패: {e}")
            return
            
    except Exception as e:
        logger.error(f"❌ 전체 테스트 실패: {e}")

def save_assignments_to_file(assignments):
    """과제 정보를 파일에 저장"""
    try:
        with open("assignment.txt", "w", encoding="utf-8") as f:
            f.write("=== LearnUs 과제 정보 업데이트 ===\n")
            f.write(f"업데이트 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("로컬 테스트 실행\n\n")
            
            if assignments:
                f.write("과제 목록:\n")
                for assignment in assignments:
                    f.write(f"  • {assignment['course']}: {assignment['activity']} - {assignment['status']}\n")
            else:
                f.write("이번주 과제가 없습니다.\n")
        
        logger.info("✅ assignment.txt 파일 업데이트 완료")
        
    except Exception as e:
        logger.error(f"❌ 파일 저장 실패: {e}")

def main():
    """메인 실행 함수"""
    print("LearnUs 로컬 자동화 테스트")
    print("=" * 50)
    print("이 스크립트는 클라우드에서 실행되는 것과 동일한 코드를 로컬에서 테스트합니다.")
    print()
    
    test_local_automation()
    
    print("\n테스트 완료!")
    print("assignment.txt 파일을 확인해보세요.")

if __name__ == "__main__":
    main()
