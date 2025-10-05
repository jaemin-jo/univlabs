"""
Firebase 연동 서비스
백엔드에서 Firebase Firestore에 접근하여 사용자 인증 정보를 가져옴
"""

import firebase_admin
from firebase_admin import credentials, firestore
import json
import os
from typing import List, Dict, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class FirebaseService:
    """Firebase Firestore 서비스"""
    
    def __init__(self):
        self.db = None
        self._initialize_firebase()
    
    def _initialize_firebase(self):
        """Firebase 초기화"""
        try:
            # Firebase Admin SDK 자격 증명 설정
            # 방법 1: 서비스 계정 키 파일 사용
            service_account_path = "firebase_service_account.json"
            if os.path.exists(service_account_path):
                cred = credentials.Certificate(service_account_path)
                firebase_admin.initialize_app(cred)
                logger.info("Firebase Admin SDK 초기화 완료 (서비스 계정 키)")
            else:
                # 방법 2: 환경 변수 사용 (클라우드 배포시)
                if os.getenv("FIREBASE_PROJECT_ID"):
                    firebase_admin.initialize_app()
                    logger.info("Firebase Admin SDK 초기화 완료 (환경 변수)")
                else:
                    logger.warning("Firebase 설정 파일을 찾을 수 없습니다. 테스트 모드로 실행합니다.")
                    # 테스트용 더미 데이터 사용
                    self.db = None
                    return
            
            self.db = firestore.client()
            logger.info("Firebase Firestore 클라이언트 초기화 완료")
            
        except Exception as e:
            logger.error(f"Firebase 초기화 실패: {e}")
            logger.warning("테스트 모드로 실행합니다.")
            self.db = None
    
    def get_all_active_learnus_credentials(self) -> List[Dict]:
        """활성화된 모든 LearnUs 인증 정보 가져오기"""
        if not self.db:
            logger.error("Firebase가 초기화되지 않았습니다.")
            return []
        
        try:
            # learnus_credentials 컬렉션에서 활성화된 사용자들 조회
            docs = self.db.collection('learnus_credentials')\
                .where('isActive', '==', True)\
                .get()
            
            credentials_list = []
            for doc in docs:
                data = doc.to_dict()
                data['uid'] = doc.id
                credentials_list.append(data)
            
            logger.info(f"활성화된 LearnUs 인증 정보 {len(credentials_list)}개 조회 완료")
            return credentials_list
            
        except Exception as e:
            logger.error(f"LearnUs 인증 정보 조회 실패: {e}")
            return []
    
    def get_user_learnus_credentials(self, uid: str) -> Optional[Dict]:
        """특정 사용자의 LearnUs 인증 정보 가져오기"""
        if not self.db:
            logger.error("Firebase가 초기화되지 않았습니다.")
            return None
        
        try:
            doc = self.db.collection('learnus_credentials').document(uid).get()
            
            if doc.exists:
                data = doc.to_dict()
                data['uid'] = doc.id
                logger.info(f"사용자 {uid}의 LearnUs 인증 정보 조회 완료")
                return data
            else:
                logger.warning(f"사용자 {uid}의 LearnUs 인증 정보를 찾을 수 없습니다.")
                return None
                
        except Exception as e:
            logger.error(f"사용자 {uid}의 LearnUs 인증 정보 조회 실패: {e}")
            return None
    
    def update_last_used_time(self, uid: str) -> bool:
        """마지막 사용 시간 업데이트"""
        if not self.db:
            return False
        
        try:
            self.db.collection('learnus_credentials').document(uid).update({
                'lastUsedAt': firestore.SERVER_TIMESTAMP,
                'updatedAt': firestore.SERVER_TIMESTAMP
            })
            logger.info(f"사용자 {uid}의 마지막 사용 시간 업데이트 완료")
            return True
            
        except Exception as e:
            logger.error(f"마지막 사용 시간 업데이트 실패: {e}")
            return False
    
    def deactivate_user_credentials(self, uid: str) -> bool:
        """사용자 인증 정보 비활성화"""
        if not self.db:
            return False
        
        try:
            self.db.collection('learnus_credentials').document(uid).update({
                'isActive': False,
                'updatedAt': firestore.SERVER_TIMESTAMP
            })
            logger.info(f"사용자 {uid}의 인증 정보 비활성화 완료")
            return True
            
        except Exception as e:
            logger.error(f"사용자 {uid}의 인증 정보 비활성화 실패: {e}")
            return False

# 전역 Firebase 서비스 인스턴스
firebase_service = FirebaseService()

def get_all_active_users() -> List[Dict]:
    """모든 활성화된 사용자 정보 가져오기 (스케줄러용)"""
    return firebase_service.get_all_active_learnus_credentials()

def get_user_credentials(uid: str) -> Optional[Dict]:
    """특정 사용자 인증 정보 가져오기"""
    return firebase_service.get_user_learnus_credentials(uid)

def update_user_last_used(uid: str) -> bool:
    """사용자 마지막 사용 시간 업데이트"""
    return firebase_service.update_last_used_time(uid)

if __name__ == "__main__":
    # 테스트 실행
    print("Firebase 서비스 테스트 시작...")
    
    # 모든 활성화된 사용자 조회
    users = get_all_active_users()
    print(f"활성화된 사용자 수: {len(users)}")
    
    for user in users:
        print(f"- {user.get('university', 'Unknown')}: {user.get('username', 'Unknown')}")
