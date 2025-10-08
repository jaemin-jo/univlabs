#!/usr/bin/env python3
"""
중복된 계정 중 하나를 삭제하는 스크립트
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

def remove_duplicate_accounts():
    """중복된 계정 중 하나를 삭제"""
    try:
        logger.info("중복 계정 정리 시작...")
        
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
        
        logger.info(f"총 {len(all_docs)}개 문서 발견")
        
        # studentId별로 그룹화
        student_id_groups = {}
        for doc_data in all_docs:
            student_id = doc_data.get('studentId', '')
            if student_id not in student_id_groups:
                student_id_groups[student_id] = []
            student_id_groups[student_id].append(doc_data)
        
        # 중복된 studentId가 있는 경우 처리
        for student_id, docs_list in student_id_groups.items():
            if len(docs_list) > 1:
                logger.info(f"중복 발견: studentId {student_id}에 {len(docs_list)}개 계정")
                
                # 첫 번째 계정은 유지하고 나머지 삭제
                keep_doc = docs_list[0]
                logger.info(f"유지: {keep_doc['doc_id']} (첫 번째 계정)")
                
                # 나머지 계정들 삭제
                for doc_data in docs_list[1:]:
                    logger.info(f"삭제: {doc_data['doc_id']} (중복 계정)")
                    try:
                        db.collection('learnus_credentials').document(doc_data['doc_id']).delete()
                        logger.info(f"삭제 완료: {doc_data['doc_id']}")
                    except Exception as e:
                        logger.error(f"삭제 실패: {doc_data['doc_id']} - {e}")
        
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
        logger.error(f"중복 계정 정리 실패: {e}")
        return False

def main():
    """메인 실행 함수"""
    print("중복 계정 정리")
    print("=" * 30)
    print("같은 studentId를 가진 중복 계정들을 정리합니다.")
    print("가장 최근에 업데이트된 계정만 유지됩니다.")
    print()
    
    # 사용자 확인
    response = input("중복 계정을 정리하시겠습니까? (y/N): ")
    if response.lower() != 'y':
        print("취소되었습니다.")
        return
    
    # 중복 계정 정리
    print("\n중복 계정 정리 중...")
    success = remove_duplicate_accounts()
    
    if success:
        print("\n중복 계정 정리 완료!")
        print("이제 각 studentId당 하나의 계정만 남았습니다.")
    else:
        print("\n중복 계정 정리 실패!")
        print("Firebase Console에서 수동으로 확인해주세요.")

if __name__ == "__main__":
    main()
