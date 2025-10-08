#!/usr/bin/env python3
"""
Firebase에서 남은 테스트 계정들을 완전히 삭제하는 스크립트
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

def delete_remaining_test_accounts():
    """남은 테스트 계정들을 완전히 삭제"""
    try:
        logger.info("Firebase 남은 테스트 계정 삭제 시작...")
        
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
        
        # learnus_credentials 컬렉션의 모든 문서 조회
        docs = db.collection('learnus_credentials').stream()
        
        all_docs = []
        for doc in docs:
            doc_data = doc.to_dict()
            doc_data['doc_id'] = doc.id
            all_docs.append(doc_data)
        
        logger.info(f"learnus_credentials 컬렉션에서 {len(all_docs)}개 문서 발견")
        
        # 실제 계정 (유지할 계정)
        real_student_ids = ["2024248012"]
        
        deleted_count = 0
        kept_count = 0
        
        for doc_data in all_docs:
            doc_id = doc_data['doc_id']
            student_id = doc_data.get('studentId', '')
            username = doc_data.get('username', '')
            
            # 실제 계정인지 확인
            is_real_account = any(real_id in student_id for real_id in real_student_ids)
            
            if is_real_account:
                logger.info(f"유지: {doc_id} (실제 계정 - studentId: {student_id})")
                kept_count += 1
            else:
                logger.info(f"삭제: {doc_id} (테스트 계정 - studentId: {student_id}, username: {username})")
                try:
                    # 문서 완전 삭제
                    db.collection('learnus_credentials').document(doc_id).delete()
                    deleted_count += 1
                    logger.info(f"삭제 완료: {doc_id}")
                except Exception as e:
                    logger.error(f"삭제 실패: {doc_id} - {e}")
        
        logger.info(f"정리 완료: {kept_count}개 유지, {deleted_count}개 삭제")
        
        # 정리 후 상태 확인
        remaining_docs = db.collection('learnus_credentials').stream()
        remaining_count = 0
        for doc in remaining_docs:
            doc_data = doc.to_dict()
            logger.info(f"남은 문서: {doc.id} (studentId: {doc_data.get('studentId', '')})")
            remaining_count += 1
        
        logger.info(f"최종 남은 문서: {remaining_count}개")
        return True
        
    except Exception as e:
        logger.error(f"테스트 계정 삭제 실패: {e}")
        return False

def main():
    """메인 실행 함수"""
    print("Firebase 남은 테스트 계정 완전 삭제")
    print("=" * 50)
    print("주의: 이 작업은 되돌릴 수 없습니다!")
    print("실제 계정 (studentId: 2024248012)만 유지됩니다.")
    print()
    
    # 사용자 확인
    response = input("정말로 테스트 계정들을 삭제하시겠습니까? (y/N): ")
    if response.lower() != 'y':
        print("취소되었습니다.")
        return
    
    # 테스트 계정 삭제
    print("\n테스트 계정 삭제 중...")
    success = delete_remaining_test_accounts()
    
    if success:
        print("\n테스트 계정 삭제 완료!")
        print("이제 실제 계정만 남았습니다.")
    else:
        print("\n테스트 계정 삭제 실패!")
        print("Firebase Console에서 수동으로 확인해주세요.")

if __name__ == "__main__":
    main()
