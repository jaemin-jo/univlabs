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
            logger.info("🔧 Firebase 초기화 시작...")
            logger.info(f"🔍 현재 작업 디렉토리: {os.getcwd()}")
            logger.info(f"🔍 사용 가능한 파일: {os.listdir('.')[:10]}")
            
            # 🔍 환경 변수 상세 확인
            logger.info("🔍 Firebase 관련 환경 변수 확인:")
            firebase_project_id = os.getenv("FIREBASE_PROJECT_ID")
            firebase_private_key = os.getenv("FIREBASE_PRIVATE_KEY")
            firebase_client_email = os.getenv("FIREBASE_CLIENT_EMAIL")
            google_application_credentials = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
            
            logger.info(f"   FIREBASE_PROJECT_ID: {firebase_project_id}")
            logger.info(f"   FIREBASE_PRIVATE_KEY: {'설정됨' if firebase_private_key else 'NOT SET'}")
            logger.info(f"   FIREBASE_CLIENT_EMAIL: {firebase_client_email}")
            logger.info(f"   GOOGLE_APPLICATION_CREDENTIALS: {google_application_credentials}")
            
            # Firebase Admin SDK 자격 증명 설정
            # 방법 1: 서비스 계정 키 파일 사용
            service_account_path = "firebase_service_account.json"
            logger.info(f"🔍 서비스 계정 키 파일 확인: {service_account_path}")
            
            if os.path.exists(service_account_path):
                logger.info("✅ 서비스 계정 키 파일 발견")
                try:
                    cred = credentials.Certificate(service_account_path)
                    firebase_admin.initialize_app(cred)
                    logger.info("✅ Firebase Admin SDK 초기화 완료 (서비스 계정 키)")
                except Exception as file_error:
                    logger.error(f"❌ 서비스 계정 키 파일 초기화 실패: {file_error}")
                    raise file_error
            else:
                logger.warning("⚠️ 서비스 계정 키 파일을 찾을 수 없음")
                # 방법 2: 환경 변수 사용 (클라우드 배포시)
                if firebase_project_id:
                    logger.info("✅ FIREBASE_PROJECT_ID 환경 변수 발견")
                    try:
                        firebase_admin.initialize_app()
                        logger.info("✅ Firebase Admin SDK 초기화 완료 (환경 변수)")
                    except Exception as env_error:
                        logger.error(f"❌ 환경 변수 초기화 실패: {env_error}")
                        raise env_error
                else:
                    logger.warning("⚠️ Firebase 설정 파일과 환경 변수를 찾을 수 없습니다.")
                    logger.info("🔧 테스트 모드로 실행합니다.")
                    # 테스트용 더미 데이터 사용
                    self.db = None
                    return
            
            self.db = firestore.client()
            logger.info("✅ Firebase Firestore 클라이언트 초기화 완료")
            
        except Exception as e:
            logger.error(f"❌ Firebase 초기화 실패: {e}")
            logger.error(f"❌ 오류 상세: {str(e)}")
            logger.error(f"❌ 오류 타입: {type(e).__name__}")
            import traceback
            logger.error(f"❌ 스택 트레이스: {traceback.format_exc()}")
            
            # 🔍 추가 디버깅 정보
            logger.info("🔍 추가 디버깅 정보:")
            logger.info(f"   현재 작업 디렉토리: {os.getcwd()}")
            logger.info(f"   Python 버전: {os.sys.version}")
            logger.info(f"   사용 가능한 환경 변수: {list(os.environ.keys())}")
            
            # Firebase 관련 환경 변수 재확인
            firebase_vars = ['FIREBASE_PROJECT_ID', 'FIREBASE_PRIVATE_KEY', 'FIREBASE_CLIENT_EMAIL', 'GOOGLE_APPLICATION_CREDENTIALS']
            for var in firebase_vars:
                value = os.getenv(var)
                logger.info(f"   {var}: {'설정됨' if value else 'NOT SET'}")
            
            # 🔧 Firebase 초기화 실패 시 대안 방법 시도
            logger.info("🔧 Firebase 초기화 실패 시 대안 방법 시도...")
            
            # 방법 3: Google Cloud 기본 인증 사용
            try:
                logger.info("🔧 Google Cloud 기본 인증 시도...")
                firebase_admin.initialize_app()
                self.db = firestore.client()
                logger.info("✅ Google Cloud 기본 인증으로 Firebase 초기화 성공")
                return
            except Exception as gcp_error:
                logger.warning(f"⚠️ Google Cloud 기본 인증 실패: {gcp_error}")
            
            # 방법 4: 환경 변수에서 직접 인증 정보 구성
            try:
                if firebase_project_id and firebase_private_key and firebase_client_email:
                    logger.info("🔧 환경 변수에서 직접 인증 정보 구성 시도...")
                    import json
                    service_account_info = {
                        "type": "service_account",
                        "project_id": firebase_project_id,
                        "private_key_id": "dummy",
                        "private_key": firebase_private_key,
                        "client_email": firebase_client_email,
                        "client_id": "dummy",
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                        "client_x509_cert_url": f"https://www.googleapis.com/robot/v1/metadata/x509/{firebase_client_email}"
                    }
                    
                    cred = credentials.Certificate(service_account_info)
                    firebase_admin.initialize_app(cred)
                    self.db = firestore.client()
                    logger.info("✅ 환경 변수에서 직접 인증 정보 구성으로 Firebase 초기화 성공")
                    return
            except Exception as env_auth_error:
                logger.warning(f"⚠️ 환경 변수 인증 정보 구성 실패: {env_auth_error}")
            
            logger.warning("🔧 모든 Firebase 초기화 방법 실패, 테스트 모드로 실행합니다.")
            self.db = None
    
    def get_all_active_learnus_credentials(self) -> List[Dict]:
        """활성화된 모든 LearnUs 인증 정보 가져오기"""
        if not self.db:
            logger.warning("Firebase가 초기화되지 않았습니다. 테스트용 더미 데이터를 사용합니다.")
            # 테스트용 더미 데이터 반환 (실제 Firebase 데이터와 동일하게 설정)
            return [{
                'uid': 'gNnogdUW3Wc6Bb9IdyciicycKB42',
                'student_id': '2024248012',
                'university': '연세대학교',
                'username': '2024248012',
                'password': 'cjm9887@',
                'isActive': True
            }]
        
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
