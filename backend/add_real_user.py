"""
실제 LearnUs 사용자 데이터를 Firebase에 추가
"""

import firebase_admin
from firebase_admin import credentials, firestore
import json
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

def add_real_user(db):
    """실제 LearnUs 사용자 데이터 추가"""
    print("📝 실제 LearnUs 사용자 정보를 입력해주세요:")
    print("=" * 50)
    
    # 사용자 정보 입력
    uid = input("Firebase 사용자 UID (또는 Enter로 자동 생성): ").strip()
    if not uid:
        uid = f"user_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    username = input("LearnUs 아이디: ").strip()
    password = input("LearnUs 비밀번호: ").strip()
    student_id = input("학번: ").strip()
    university = input("대학교 (기본값: 연세대학교): ").strip() or "연세대학교"
    
    if not username or not password or not student_id:
        print("❌ 필수 정보가 누락되었습니다.")
        return False
    
    try:
        # 실제 사용자 데이터
        real_user = {
            'uid': uid,
            'username': username,
            'password': password,
            'studentId': student_id,
            'university': university,
            'isActive': True,
            'createdAt': datetime.now(),
            'updatedAt': datetime.now(),
            'lastUsedAt': None
        }
        
        # Firestore에 저장
        doc_ref = db.collection('learnus_credentials').document(real_user['uid'])
        doc_ref.set(real_user)
        
        print(f"✅ 실제 사용자 데이터 추가 완료!")
        print(f"   - UID: {real_user['uid']}")
        print(f"   - 사용자명: {real_user['username']}")
        print(f"   - 대학교: {real_user['university']}")
        print(f"   - 학번: {real_user['studentId']}")
        print()
        print("🎯 이제 백엔드 서버를 다시 실행하면 실제 LearnUs 정보로 자동화가 실행됩니다!")
        
        return True
        
    except Exception as e:
        print(f"❌ 실제 사용자 데이터 추가 실패: {e}")
        return False

def check_existing_users(db):
    """기존 사용자 데이터 확인"""
    try:
        docs = db.collection('learnus_credentials').where('isActive', '==', True).get()
        
        print(f"📊 활성화된 사용자 데이터: {len(docs)}개")
        
        for doc in docs:
            data = doc.to_dict()
            print(f"   - {data.get('username', 'Unknown')} ({data.get('university', 'Unknown')}) - {data.get('studentId', 'Unknown')}")
        
        return len(docs)
        
    except Exception as e:
        print(f"❌ 기존 사용자 데이터 확인 실패: {e}")
        return 0

if __name__ == "__main__":
    print("🚀 실제 LearnUs 사용자 데이터 추가")
    print("=" * 50)
    
    # Firebase 초기화
    db = initialize_firebase()
    if not db:
        exit(1)
    
    # 기존 사용자 확인
    existing_count = check_existing_users(db)
    
    print()
    if existing_count > 0:
        print(f"ℹ️ 이미 {existing_count}개의 활성화된 사용자가 있습니다.")
        add_more = input("추가로 사용자를 등록하시겠습니까? (y/n): ").strip().lower()
        if add_more != 'y':
            print("✅ 기존 사용자 데이터로 백엔드 서버를 실행하세요.")
            exit(0)
    
    # 실제 사용자 데이터 추가
    success = add_real_user(db)
    
    if success:
        print()
        print("🎉 설정 완료!")
        print("이제 다음 명령어로 백엔드 서버를 실행하세요:")
        print("python scheduler_server.py")
    else:
        print("❌ 사용자 데이터 추가 실패")

