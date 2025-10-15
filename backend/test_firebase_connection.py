#!/usr/bin/env python3
"""
Firebase 연결 테스트 스크립트
Docker 환경에서 Firebase 연결이 제대로 되는지 확인
"""

import os
import sys
import logging
from datetime import datetime

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_firebase_connection():
    """Firebase 연결 테스트"""
    try:
        logger.info("🧪 Firebase 연결 테스트 시작...")
        
        # 1. 환경 변수 확인
        logger.info("🔍 환경 변수 확인:")
        firebase_vars = [
            'FIREBASE_PROJECT_ID',
            'FIREBASE_PRIVATE_KEY',
            'FIREBASE_CLIENT_EMAIL',
            'GOOGLE_APPLICATION_CREDENTIALS'
        ]
        
        for var in firebase_vars:
            value = os.getenv(var)
            if value:
                if var == 'FIREBASE_PRIVATE_KEY':
                    logger.info(f"   {var}: {'설정됨 (길이: ' + str(len(value)) + ')'}")
                else:
                    logger.info(f"   {var}: {value}")
            else:
                logger.warning(f"   {var}: NOT SET")
        
        # 2. Firebase 서비스 계정 키 파일 확인
        service_account_path = "firebase_service_account.json"
        if os.path.exists(service_account_path):
            logger.info(f"✅ 서비스 계정 키 파일 발견: {service_account_path}")
        else:
            logger.warning(f"⚠️ 서비스 계정 키 파일 없음: {service_account_path}")
        
        # 3. Firebase Admin SDK 초기화 테스트
        logger.info("🔧 Firebase Admin SDK 초기화 테스트...")
        try:
            import firebase_admin
            from firebase_admin import credentials, firestore
            
            # 기존 앱이 있으면 삭제
            try:
                firebase_admin.delete_app(firebase_admin.get_app())
            except:
                pass
            
            # 서비스 계정 키 파일로 초기화
            if os.path.exists(service_account_path):
                cred = credentials.Certificate(service_account_path)
                app = firebase_admin.initialize_app(cred)
                logger.info("✅ Firebase Admin SDK 초기화 성공 (서비스 계정 키)")
            else:
                # 환경 변수로 초기화
                app = firebase_admin.initialize_app()
                logger.info("✅ Firebase Admin SDK 초기화 성공 (환경 변수)")
            
            # 4. Firestore 연결 테스트
            logger.info("🔧 Firestore 연결 테스트...")
            db = firestore.client()
            
            # 5. 실제 데이터 조회 테스트
            logger.info("🔍 실제 데이터 조회 테스트...")
            try:
                # learnus_credentials 컬렉션에서 활성화된 사용자들 조회
                docs = db.collection('learnus_credentials')\
                    .where('isActive', '==', True)\
                    .get()
                
                users = []
                for doc in docs:
                    data = doc.to_dict()
                    data['uid'] = doc.id
                    users.append(data)
                
                logger.info(f"✅ Firebase 연결 성공!")
                logger.info(f"   활성화된 사용자 수: {len(users)}명")
                
                for user in users:
                    logger.info(f"   - {user.get('university', 'Unknown')}: {user.get('username', 'Unknown')}")
                
                return {
                    "success": True,
                    "message": "Firebase 연결 성공",
                    "user_count": len(users),
                    "users": users
                }
                
            except Exception as db_error:
                logger.error(f"❌ Firestore 데이터 조회 실패: {db_error}")
                return {
                    "success": False,
                    "message": f"Firestore 데이터 조회 실패: {db_error}",
                    "user_count": 0,
                    "users": []
                }
                
        except Exception as firebase_error:
            logger.error(f"❌ Firebase 초기화 실패: {firebase_error}")
            return {
                "success": False,
                "message": f"Firebase 초기화 실패: {firebase_error}",
                "user_count": 0,
                "users": []
            }
            
    except Exception as e:
        logger.error(f"❌ Firebase 연결 테스트 실패: {e}")
        return {
            "success": False,
            "message": f"Firebase 연결 테스트 실패: {e}",
            "user_count": 0,
            "users": []
        }

def test_docker_environment():
    """Docker 환경 테스트"""
    logger.info("🔍 Docker 환경 테스트...")
    
    # 현재 작업 디렉토리
    logger.info(f"   현재 작업 디렉토리: {os.getcwd()}")
    
    # 사용 가능한 파일들
    try:
        files = os.listdir('.')
        logger.info(f"   사용 가능한 파일: {files[:10]}")
    except Exception as e:
        logger.error(f"   파일 목록 조회 실패: {e}")
    
    # Python 버전
    logger.info(f"   Python 버전: {sys.version}")
    
    # 환경 변수 개수
    logger.info(f"   환경 변수 개수: {len(os.environ)}")

if __name__ == "__main__":
    print("🚀 Firebase 연결 테스트 시작...")
    print("=" * 50)
    
    # Docker 환경 테스트
    test_docker_environment()
    print()
    
    # Firebase 연결 테스트
    result = test_firebase_connection()
    print()
    
    # 결과 출력
    print("=" * 50)
    print("📋 테스트 결과:")
    print(f"   성공: {result['success']}")
    print(f"   메시지: {result['message']}")
    print(f"   사용자 수: {result['user_count']}")
    
    if result['success']:
        print("✅ Firebase 연결이 정상적으로 작동합니다!")
    else:
        print("❌ Firebase 연결에 문제가 있습니다.")
        print("💡 해결방법:")
        print("   1. firebase_service_account.json 파일이 올바른 위치에 있는지 확인")
        print("   2. Docker 환경변수가 올바르게 설정되었는지 확인")
        print("   3. GCP VM에서 Firebase API 접근 권한이 있는지 확인")
