#!/bin/bash

# MCP 서버를 Cloud Run에 배포하는 스크립트

set -e

# 환경 변수 설정
PROJECT_ID="univlabs-ai"
SERVICE_NAME="gcp-mcp-server"
REGION="asia-northeast3"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

echo "🚀 MCP 서버를 Cloud Run에 배포합니다..."

# 1. Docker 이미지 빌드
echo "📦 Docker 이미지 빌드 중..."
docker build -f Dockerfile.mcp -t ${IMAGE_NAME} .

# 2. Google Container Registry에 푸시
echo "📤 이미지를 Container Registry에 푸시 중..."
docker push ${IMAGE_NAME}

# 3. Cloud Run에 배포
echo "🚀 Cloud Run에 배포 중..."
gcloud run deploy ${SERVICE_NAME} \
    --image ${IMAGE_NAME} \
    --platform managed \
    --region ${REGION} \
    --project ${PROJECT_ID} \
    --allow-unauthenticated \
    --port 8080 \
    --memory 1Gi \
    --cpu 1 \
    --timeout 3600 \
    --max-instances 10

# 4. 서비스 URL 출력
echo "✅ MCP 서버 배포 완료!"
echo "🌐 서비스 URL:"
gcloud run services describe ${SERVICE_NAME} \
    --platform managed \
    --region ${REGION} \
    --project ${PROJECT_ID} \
    --format 'value(status.url)'

echo ""
echo "📋 MCP 클라이언트 설정:"
echo "서비스 URL을 MCP 클라이언트 설정에 추가하세요."
echo "예: http://gcp-mcp-server-xxx-uc.a.run.app"
