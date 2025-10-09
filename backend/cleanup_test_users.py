#!/usr/bin/env python3
"""
Firebase에서 테스트 계정들을 삭제하고 실제 계정만 남기는 스크립트
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

def cleanup_test_users():
    """테스트 계정들을 삭제하고 실제 계정만 남기기"""
    try:
        logger.info("Firebase 테스트 계정 정리 시작...")
        
        # Firebase 서비스 import
        from firebase_service import get_all_active_users, delete_user
        
        # 현재 활성화된 사용자 조회
        active_users = get_all_active_users()
        logger.info(f"현재 활성화된 사용자: {len(active_users)}명")
        
        # 실제 계정 (유지할 계정)
        real_accounts = [
            "2024248012",  # 실제 계정
            "cjm9887@"     # 실제 이메일
        ]
        
        # 삭제할 테스트 계정들
        test_keywords = [
            "test", "your_learnus_id", "learnus_user", 
            "demo", "sample", "temp", "fake"
        ]
        
        deleted_count = 0
        kept_count = 0
        
        for user in active_users:
            username = user.get('username', '')
            user_id = user.get('id', '')
            
            # 실제 계정인지 확인
            is_real_account = False
            for real_account in real_accounts:
                if real_account in username:
                    is_real_account = True
                    break
            
            # 테스트 계정인지 확인
            is_test_account = False
            for keyword in test_keywords:
                if keyword.lower() in username.lower():
                    is_test_account = True
                    break
            
            if is_real_account:
                logger.info(f"✅ 유지: {username} (실제 계정)")
                kept_count += 1
            elif is_test_account:
                logger.info(f"🗑️ 삭제: {username} (테스트 계정)")
                try:
                    delete_user(user_id)
                    deleted_count += 1
                except Exception as e:
                    logger.error(f"❌ {username} 삭제 실패: {e}")
            else:
                logger.info(f"❓ 확인 필요: {username} (분류 불명)")
        
        logger.info(f"정리 완료: {kept_count}명 유지, {deleted_count}명 삭제")
        
        # 정리 후 상태 확인
        remaining_users = get_all_active_users()
        logger.info(f"남은 사용자: {len(remaining_users)}명")
        
        for user in remaining_users:
            logger.info(f"  - {user.get('username', '')} ({user.get('university', '')})")
        
        return True
        
    except Exception as e:
        logger.error(f"테스트 계정 정리 실패: {e}")
        return False

def add_real_user_manually():
    """실제 사용자 정보를 수동으로 추가"""
    try:
        logger.info("실제 사용자 정보 추가 중...")
        
        from firebase_service import add_user
        
        # 실제 사용자 정보 (예시 - 실제 정보로 수정 필요)
        real_user = {
            "username": "2024248012",
            "password": "your_actual_password",  # 실제 비밀번호로 변경
            "university": "연세대학교",
            "studentId": "2024248012",
            "isActive": True
        }
        
        # 사용자 추가
        result = add_user(
            username=real_user["username"],
            password=real_user["password"],
            university=real_user["university"],
            student_id=real_user["studentId"]
        )
        
        if result:
            logger.info("✅ 실제 사용자 정보 추가 완료")
        else:
            logger.error("❌ 실제 사용자 정보 추가 실패")
            
        return result
        
    except Exception as e:
        logger.error(f"실제 사용자 추가 실패: {e}")
        return False

def main():
    """메인 실행 함수"""
    print("Firebase 테스트 계정 정리 도구")
    print("=" * 50)
    print("1. 테스트 계정들을 삭제합니다")
    print("2. 실제 계정만 남깁니다")
    print("3. 실제 계정: 2024248012")
    print()
    
    # 1. 테스트 계정 정리
    print("1단계: 테스트 계정 정리 중...")
    cleanup_success = cleanup_test_users()
    
    if cleanup_success:
        print("✅ 테스트 계정 정리 완료!")
    else:
        print("❌ 테스트 계정 정리 실패!")
        return
    
    print()
    print("2단계: 실제 사용자 정보 확인...")
    
    # 2. 남은 사용자 확인
    try:
        from firebase_service import get_all_active_users
        remaining_users = get_all_active_users()
        
        if remaining_users:
            print(f"✅ 남은 사용자: {len(remaining_users)}명")
            for user in remaining_users:
                print(f"  - {user.get('username', '')} ({user.get('university', '')})")
        else:
            print("⚠️ 활성화된 사용자가 없습니다.")
            print("💡 Flutter 앱에서 LearnUs 정보를 설정해주세요.")
            
    except Exception as e:
        print(f"❌ 사용자 확인 실패: {e}")
    
    print()
    print("정리 완료!")
    print("이제 Flutter 앱에서 LearnUs 정보를 설정하면 정상 작동할 것입니다.")

if __name__ == "__main__":
    main()











