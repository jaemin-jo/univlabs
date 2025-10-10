#!/usr/bin/env python3
"""
Firebase에서 테스트 계정들을 비활성화하는 스크립트
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

def remove_test_users():
    """테스트 계정들을 비활성화"""
    try:
        logger.info("Firebase 테스트 계정 비활성화 시작...")
        
        # Firebase 연결
        import firebase_admin
        from firebase_admin import credentials, firestore
        
        # Firebase 초기화 (이미 초기화되어 있으면 무시)
        try:
            cred = credentials.Certificate('firebase_service_account.json')
            firebase_admin.initialize_app(cred)
            logger.info("Firebase Admin SDK 초기화 완료 (새 인스턴스)")
        except ValueError:
            # 이미 초기화된 경우
            logger.info("Firebase Admin SDK 이미 초기화됨")
        
        db = firestore.client()
        
        # 현재 활성화된 사용자 조회
        users_ref = db.collection('users')
        docs = users_ref.where('isActive', '==', True).stream()
        
        active_users = []
        for doc in docs:
            user_data = doc.to_dict()
            user_data['uid'] = doc.id
            active_users.append(user_data)
        
        logger.info(f"현재 활성화된 사용자: {len(active_users)}명")
        
        # 실제 계정 (유지할 계정)
        real_accounts = [
            "2024248012",  # 실제 계정
            "cjm9887"      # 실제 이메일 (부분 매칭)
        ]
        
        # 삭제할 테스트 계정 키워드들
        test_keywords = [
            "test", "your_learnus_id", "learnus_user", 
            "demo", "sample", "temp", "fake"
        ]
        
        deactivated_count = 0
        kept_count = 0
        
        for user in active_users:
            username = user.get('username', '')
            uid = user.get('uid', '')
            
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
                logger.info(f"유지: {username} (실제 계정)")
                kept_count += 1
            elif is_test_account:
                logger.info(f"비활성화: {username} (테스트 계정)")
                try:
                    # 사용자 비활성화
                    db.collection('users').document(uid).update({
                        'isActive': False,
                        'updatedAt': firestore.SERVER_TIMESTAMP,
                        'deactivatedAt': firestore.SERVER_TIMESTAMP,
                        'reason': '테스트 계정 정리'
                    })
                    deactivated_count += 1
                    logger.info(f"비활성화 완료: {username}")
                except Exception as e:
                    logger.error(f"비활성화 실패: {username} - {e}")
            else:
                logger.info(f"확인 필요: {username} (분류 불명)")
        
        logger.info(f"정리 완료: {kept_count}명 유지, {deactivated_count}명 비활성화")
        
        # 정리 후 상태 확인
        remaining_docs = users_ref.where('isActive', '==', True).stream()
        remaining_users = []
        for doc in remaining_docs:
            user_data = doc.to_dict()
            user_data['uid'] = doc.id
            remaining_users.append(user_data)
        
        logger.info(f"남은 활성 사용자: {len(remaining_users)}명")
        
        for user in remaining_users:
            logger.info(f"  - {user.get('username', '')} ({user.get('university', '')})")
        
        return True
        
    except Exception as e:
        logger.error(f"테스트 계정 정리 실패: {e}")
        return False

def main():
    """메인 실행 함수"""
    print("Firebase 테스트 계정 정리 도구")
    print("=" * 50)
    print("1. 테스트 계정들을 비활성화합니다")
    print("2. 실제 계정만 활성 상태로 유지합니다")
    print("3. 실제 계정: 2024248012")
    print()
    
    # 사용자 확인
    response = input("계속 진행하시겠습니까? (y/N): ")
    if response.lower() != 'y':
        print("취소되었습니다.")
        return
    
    # 테스트 계정 정리
    print("\n테스트 계정 정리 중...")
    cleanup_success = remove_test_users()
    
    if cleanup_success:
        print("\n테스트 계정 정리 완료!")
        print("이제 Flutter 앱에서 LearnUs 정보를 설정하면 정상 작동할 것입니다.")
    else:
        print("\n테스트 계정 정리 실패!")
        print("수동으로 Firebase Console에서 확인해주세요.")

if __name__ == "__main__":
    main()













