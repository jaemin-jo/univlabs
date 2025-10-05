#!/usr/bin/env python3
"""
GCP Cloud Run에 환경 변수를 설정하는 스크립트
"""

import os
import json
from firebase_service_account import firebase_config

def set_environment_variables():
    """환경 변수 설정"""
    
    # Firebase 서비스 계정 키 파일 읽기
    with open('firebase_service_account.json', 'r') as f:
        firebase_key = json.load(f)
    
    # 환경 변수 설정
    env_vars = {
        'FIREBASE_PROJECT_ID': firebase_key['project_id'],
        'FIREBASE_PRIVATE_KEY_ID': firebase_key['private_key_id'],
        'FIREBASE_PRIVATE_KEY': firebase_key['private_key'],
        'FIREBASE_CLIENT_EMAIL': firebase_key['client_email'],
        'FIREBASE_CLIENT_ID': firebase_key['client_id'],
        'FIREBASE_AUTH_URI': firebase_key['auth_uri'],
        'FIREBASE_TOKEN_URI': firebase_key['token_uri']
    }
    
    print("환경 변수 설정:")
    for key, value in env_vars.items():
        print(f"{key}={value}")
    
    return env_vars

if __name__ == "__main__":
    set_environment_variables()
