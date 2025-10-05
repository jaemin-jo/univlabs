#!/usr/bin/env python3
"""
Firebase에 테스트 사용자 데이터를 추가하는 스크립트
"""

import os
import json
from datetime import datetime
from firebase_admin import credentials, firestore, initialize_app

def add_test_user_to_firebase():
    """Firebase에 테스트 사용자 데이터 추가"""
    try:
        # Firebase 초기화
        cred = credentials.Certificate('firebase_service_account.json')
        initialize_app(cred)
        db = firestore.client()
        print("✅ Firebase 초기화 완료")

        # 테스트 사용자 데이터
        user_data = {
            'uid': 'test_user_001',
            'username': 'your_learnus_id',  # 실제 LearnUs 아이디로 변경
            'password': 'your_short_password',  # 짧은 비밀번호로 변경
            'studentId': '2024248012',
            'university': '연세대학교',
            'isActive': True,
            'createdAt': datetime.utcnow().isoformat() + 'Z',
            'updatedAt': datetime.utcnow().isoformat() + 'Z',
            'lastUsedAt': datetime.utcnow().isoformat() + 'Z'
        }

        # Firestore에 저장
        db.collection('learnus_credentials').document('test_user_001').set(user_data)
        print("✅ 사용자 데이터가 Firebase에 저장되었습니다!")
        print("이제 백엔드 자동화가 이 정보를 사용할 수 있습니다.")
        
        # 저장된 데이터 확인
        doc = db.collection('learnus_credentials').document('test_user_001').get()
        if doc.exists:
            print("📄 저장된 데이터:", doc.to_dict())
        else:
            print("❌ 데이터 저장 실패")

    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    add_test_user_to_firebase()
