#!/bin/bash

# GCP 배포 스크립트

echo "🚀 GCP Cloud Run 배포 시작..."

# 1. 프로젝트 설정
export PROJECT_ID=univlabs-ai
gcloud config set project $PROJECT_ID

# 2. 필요한 API 활성화
echo "📡 API 활성화 중..."
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable containerregistry.googleapis.com

# 3. Docker 이미지 빌드 및 푸시
echo "🐳 Docker 이미지 빌드 중..."
gcloud builds submit --config cloudbuild.yaml

# 4. 환경 변수 설정
echo "🔐 환경 변수 설정 중..."
gcloud run services update learnus-backend \
    --region=asia-northeast3 \
    --set-env-vars="FIREBASE_PROJECT_ID=univlabs-ai" \
    --set-env-vars="FIREBASE_PRIVATE_KEY_ID=your_private_key_id" \
    --set-env-vars="FIREBASE_PRIVATE_KEY=your_private_key" \
    --set-env-vars="FIREBASE_CLIENT_EMAIL=firebase-adminsdk-fbsvc@univlabs-ai.iam.gserviceaccount.com" \
    --set-env-vars="FIREBASE_CLIENT_ID=your_client_id" \
    --set-env-vars="FIREBASE_AUTH_URI=https://accounts.google.com/o/oauth2/auth" \
    --set-env-vars="FIREBASE_TOKEN_URI=https://oauth2.googleapis.com/token"

# 5. 서비스 URL 확인
echo "✅ 배포 완료!"
echo "🌐 서비스 URL:"
gcloud run services describe learnus-backend --region=asia-northeast3 --format="value(status.url)"

echo "🎉 24시간 자동화 백엔드가 GCP에서 실행 중입니다!"
