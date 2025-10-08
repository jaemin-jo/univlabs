#!/usr/bin/env python3
"""
실제 사용자 정보만 Firebase에 추가하는 스크립트
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

def add_real_user():
    """실제 사용자 정보 추가"""
    try:
        logger.info("실제 사용자 정보 추가 시작...")
        
        # Firebase 연결
        import firebase_admin
        from firebase_admin import credentials, firestore
        
        # Firebase 초기화
        try:
            cred = credentials.Certificate('firebase_service_account.json')
            firebase_admin.initialize_app(cred)
            logger.info("Firebase Admin SDK 초기화 완료")
        except ValueError:
            logger.info("Firebase Admin SDK 이미 초기화됨")
        
        db = firestore.client()
        
        # 실제 사용자 정보
        real_user = {
            'username': '2024248012',
            'password': 'cjm9887@',  # 실제 비밀번호
            'university': '연세대학교',
            'studentId': '2024248012',
            'isActive': True,
            'createdAt': firestore.SERVER_TIMESTAMP,
            'updatedAt': firestore.SERVER_TIMESTAMP,
            'lastUsedAt': firestore.SERVER_TIMESTAMP
        }
        
        # 기존 사용자 확인
        existing_users = db.collection('users').where('username', '==', '2024248012').stream()
        existing_count = len(list(existing_users))
        
        if existing_count > 0:
            logger.info("기존 사용자 발견, 업데이트 중...")
            # 기존 사용자 업데이트
            for doc in db.collection('users').where('username', '==', '2024248012').stream():
                doc.reference.update({
                    'password': real_user['password'],
                    'isActive': True,
                    'updatedAt': firestore.SERVER_TIMESTAMP,
                    'lastUsedAt': firestore.SERVER_TIMESTAMP
                })
                logger.info(f"사용자 업데이트 완료: {doc.id}")
        else:
            logger.info("새 사용자 추가 중...")
            # 새 사용자 추가
            doc_ref = db.collection('users').add(real_user)
            logger.info(f"새 사용자 추가 완료: {doc_ref[1].id}")
        
        # 추가된 사용자 확인
        active_users = db.collection('users').where('isActive', '==', True).stream()
        active_count = 0
        for doc in active_users:
            user_data = doc.to_dict()
            logger.info(f"활성 사용자: {user_data.get('username', '')} ({user_data.get('university', '')})")
            active_count += 1
        
        logger.info(f"총 활성 사용자: {active_count}명")
        return True
        
    except Exception as e:
        logger.error(f"실제 사용자 추가 실패: {e}")
        return False

def main():
    """메인 실행 함수"""
    print("실제 사용자 정보 추가")
    print("=" * 30)
    print("사용자: 2024248012")
    print("대학: 연세대학교")
    print()
    
    # 사용자 확인
    response = input("실제 사용자 정보를 추가하시겠습니까? (y/N): ")
    if response.lower() != 'y':
        print("취소되었습니다.")
        return
    
    # 실제 사용자 추가
    print("\n실제 사용자 정보 추가 중...")
    success = add_real_user()
    
    if success:
        print("\n실제 사용자 정보 추가 완료!")
        print("이제 클라우드 자동화가 정상 작동할 것입니다.")
    else:
        print("\n실제 사용자 정보 추가 실패!")
        print("Firebase 설정을 확인해주세요.")

if __name__ == "__main__":
    main()










