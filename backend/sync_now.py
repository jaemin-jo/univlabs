#!/usr/bin/env python3
"""
즉시 클라우드 데이터를 로컬로 동기화하는 간단한 스크립트
"""

import sys
import os

# 현재 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sync_cloud_data import CloudDataSyncer

def main():
    print("LearnUs 클라우드 데이터 즉시 동기화")
    print("=" * 40)
    
    syncer = CloudDataSyncer()
    
    print("클라우드에서 최신 데이터 가져오는 중...")
    success = syncer.sync()
    
    if success:
        print("동기화 완료!")
        print("assignment.txt 파일이 업데이트되었습니다.")
        print("Flutter 앱에서 최신 과제 정보를 확인할 수 있습니다.")
    else:
        print("동기화 실패!")
        print("클라우드 서버 연결을 확인해주세요.")

if __name__ == "__main__":
    main()
