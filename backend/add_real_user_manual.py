"""
실제 LearnUs 사용자 데이터를 수동으로 Firebase에 추가
"""

import firebase_admin
from firebase_admin import credentials, firestore
import os
from datetime import datetime

def initialize_firebase():
    """Firebase 초기화"""
    try:
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

def add_real_user_manual(db):
    """실제 LearnUs 사용자 데이터 수동 추가"""
    print("📝 실제 LearnUs 사용자 정보를 수동으로 추가합니다.")
    print("=" * 60)
    
    # 실제 사용자 정보 (여기에 실제 정보를 입력하세요)
    real_users = [
        {
            'uid': 'user_2024248012',
            'username': '2024248012',  # 실제 LearnUs 아이디
            'password': 'cjm9887@',     # 실제 LearnUs 비밀번호
            'studentId': '2024248012',
            'university': '연세대학교',
            'isActive': True,
            'createdAt': datetime.now(),
            'updatedAt': datetime.now(),
            'lastUsedAt': None
        }
        # 추가 사용자가 있다면 여기에 더 추가할 수 있습니다
    ]
    
    try:
        for user in real_users:
            # Firestore에 저장
            doc_ref = db.collection('learnus_credentials').document(user['uid'])
            doc_ref.set(user)
            
            print(f"✅ 사용자 데이터 추가 완료:")
            print(f"   - UID: {user['uid']}")
            print(f"   - 사용자명: {user['username']}")
            print(f"   - 대학교: {user['university']}")
            print(f"   - 학번: {user['studentId']}")
            print()
        
        print("🎯 이제 백엔드 서버를 실행하면 실제 LearnUs 정보로 자동화가 실행됩니다!")
        return True
        
    except Exception as e:
        print(f"❌ 사용자 데이터 추가 실패: {e}")
        return False

def check_users(db):
    """사용자 데이터 확인"""
    try:
        docs = db.collection('learnus_credentials').where('isActive', '==', True).get()
        
        print(f"📊 활성화된 사용자 데이터: {len(docs)}개")
        
        for doc in docs:
            data = doc.to_dict()
            print(f"   - {data.get('username', 'Unknown')} ({data.get('university', 'Unknown')}) - {data.get('studentId', 'Unknown')}")
        
        return len(docs)
        
    except Exception as e:
        print(f"❌ 사용자 데이터 확인 실패: {e}")
        return 0

if __name__ == "__main__":
    print("🚀 실제 LearnUs 사용자 데이터 수동 추가")
    print("=" * 60)
    
    # Firebase 초기화
    db = initialize_firebase()
    if not db:
        exit(1)
    
    # 기존 사용자 확인
    existing_count = check_users(db)
    
    print()
    if existing_count > 0:
        print(f"ℹ️ 이미 {existing_count}개의 활성화된 사용자가 있습니다.")
        print("백엔드 서버를 실행해보세요.")
    else:
        print("📝 실제 사용자 데이터를 추가합니다...")
        success = add_real_user_manual(db)
        
        if success:
            print()
            print("🎉 설정 완료!")
            print("이제 다음 명령어로 백엔드 서버를 실행하세요:")
            print("python scheduler_server.py")
        else:
            print("❌ 사용자 데이터 추가 실패")
