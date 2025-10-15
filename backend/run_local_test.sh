#!/bin/bash

echo "🔧 Cloud Run 로컬 테스트 파이프라인"
echo "================================================"
echo

# 필요한 패키지 설치
echo "📦 필요한 패키지 설치 중..."
pip install requests

# 테스트 파이프라인 실행
echo "🚀 테스트 파이프라인 시작..."
python local_test_pipeline.py

echo
echo "📋 테스트 완료! pipeline_test.log 파일을 확인하세요."




