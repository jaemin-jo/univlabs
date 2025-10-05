"""
Firebase에 테스트용 사용자 데이터 추가
"""

import firebase_admin
from firebase_admin import credentials, firestore
import json
import os
from datetime import datetime

def initialize_firebase():
    """Firebase 초기화"""
    try:
        # 서비스 계정 키 파일 사용
        service_account_path = "firebase_service_account.json"
        if os.path.exists(service_account_path):
            cred = credentials.Certificate(service_account_path)
            firebase_admin.initialize_app(cred)
            print("✅ Firebase Admin SDK 초기화 완료")
        else:
            print("❌ Firebase 서비스 계정 키 파일을 찾을 수 없습니다.")
            return None
        
        db = firestore.client()
        print("✅ Firebase Firestore 클라이언트 초기화 완료")
        return db
        
    except Exception as e:
        print(f"❌ Firebase 초기화 실패: {e}")
        return None

def add_test_user(db):
    """테스트용 사용자 데이터 추가"""
    try:
        # 테스트용 사용자 데이터
        test_user = {
            'uid': 'test_user_12345',
            'username': 'test_learnus_user',
            'password': 'test_password_123',
            'studentId': '2024123456',
            'university': '연세대학교',
            'isActive': True,
            'createdAt': datetime.now(),
            'updatedAt': datetime.now(),
            'lastUsedAt': None
        }
        
        # Firestore에 저장
        doc_ref = db.collection('learnus_credentials').document(test_user['uid'])
        doc_ref.set(test_user)
        
        print(f"✅ 테스트 사용자 데이터 추가 완료: {test_user['uid']}")
        print(f"   - 사용자명: {test_user['username']}")
        print(f"   - 대학교: {test_user['university']}")
        print(f"   - 학번: {test_user['studentId']}")
        
        return True
        
    except Exception as e:
        print(f"❌ 테스트 사용자 데이터 추가 실패: {e}")
        return False

def check_existing_users(db):
    """기존 사용자 데이터 확인"""
    try:
        docs = db.collection('learnus_credentials').get()
        
        print(f"📊 기존 사용자 데이터: {len(docs)}개")
        
        for doc in docs:
            data = doc.to_dict()
            print(f"   - {data.get('username', 'Unknown')} ({data.get('university', 'Unknown')})")
        
        return len(docs)
        
    except Exception as e:
        print(f"❌ 기존 사용자 데이터 확인 실패: {e}")
        return 0

if __name__ == "__main__":
    print("🚀 Firebase 테스트 사용자 데이터 추가 시작...")
    
    # Firebase 초기화
    db = initialize_firebase()
    if not db:
        exit(1)
    
    # 기존 사용자 확인
    existing_count = check_existing_users(db)
    
    if existing_count == 0:
        print("📝 테스트 사용자 데이터 추가 중...")
        success = add_test_user(db)
        
        if success:
            print("✅ 테스트 사용자 데이터 추가 완료!")
            print("이제 백엔드 서버를 다시 실행하면 Selenium이 실행됩니다.")
        else:
            print("❌ 테스트 사용자 데이터 추가 실패")
    else:
        print(f"ℹ️ 이미 {existing_count}개의 사용자 데이터가 있습니다.")
        print("백엔드 서버를 다시 실행해보세요.")

