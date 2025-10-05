"""
자격증명 보안 관리 서비스
- 암호화된 저장
- 자동 갱신
- 보안 로깅
"""

import os
import json
import base64
from cryptography.fernet import Fernet
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

class CredentialManager:
    def __init__(self):
        self._key = self._get_or_create_key()
        self._cipher = Fernet(self._key)
        self._credentials_file = "encrypted_credentials.json"
    
    def _get_or_create_key(self) -> bytes:
        """암호화 키 생성 또는 로드"""
        key_file = "encryption.key"
        if os.path.exists(key_file):
            with open(key_file, "rb") as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(key_file, "wb") as f:
                f.write(key)
            return key
    
    def save_credentials(self, user_id: str, university: str, 
                        username: str, password: str, student_id: str) -> bool:
        """자격증명 암호화 저장"""
        try:
            credentials = {
                "user_id": user_id,
                "university": university,
                "username": username,
                "password": password,  # 암호화됨
                "student_id": student_id,
                "created_at": str(datetime.now()),
                "last_used": None
            }
            
            # 암호화
            encrypted_data = self._cipher.encrypt(json.dumps(credentials).encode())
            
            # 파일에 저장
            with open(self._credentials_file, "wb") as f:
                f.write(encrypted_data)
            
            logger.info(f"✅ 자격증명 암호화 저장 완료: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 자격증명 저장 오류: {e}")
            return False
    
    def get_credentials(self, user_id: str) -> Optional[Dict]:
        """자격증명 복호화 조회"""
        try:
            if not os.path.exists(self._credentials_file):
                return None
            
            with open(self._credentials_file, "rb") as f:
                encrypted_data = f.read()
            
            # 복호화
            decrypted_data = self._cipher.decrypt(encrypted_data)
            credentials = json.loads(decrypted_data.decode())
            
            if credentials["user_id"] == user_id:
                return credentials
            return None
            
        except Exception as e:
            logger.error(f"❌ 자격증명 조회 오류: {e}")
            return None
    
    def update_last_used(self, user_id: str) -> bool:
        """마지막 사용 시간 업데이트"""
        try:
            credentials = self.get_credentials(user_id)
            if credentials:
                credentials["last_used"] = str(datetime.now())
                return self.save_credentials(
                    user_id, 
                    credentials["university"],
                    credentials["username"],
                    credentials["password"],
                    credentials["student_id"]
                )
            return False
        except Exception as e:
            logger.error(f"❌ 사용 시간 업데이트 오류: {e}")
            return False
