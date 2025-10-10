#!/bin/bash

# MCP 서버 수동 배포 스크립트 (Cloud Build 사용)

set -e

PROJECT_ID="univlabs-ai"
SERVICE_NAME="gcp-mcp-server"
REGION="asia-northeast3"
BUILD_CONFIG="backend/cloudbuild.mcp.yaml"

echo "🚀 MCP 서버를 Cloud Build로 배포합니다..."

# 1. Cloud Build 트리거 실행
echo "🔨 Cloud Build 트리거 실행 중..."
gcloud builds triggers run gcp-mcp-server-trigger \
    --project=$PROJECT_ID \
    --branch=main

echo "⏳ 빌드 진행 중... (예상 시간: 5-10분)"
echo "📋 빌드 상태를 확인하려면:"
echo "gcloud builds list --project=$PROJECT_ID --limit=5"

# 2. 배포 완료 후 서비스 URL 출력
echo ""
echo "✅ MCP 서버 배포가 완료되면 서비스 URL을 확인하세요:"
echo "gcloud run services describe $SERVICE_NAME --platform=managed --region=$REGION --project=$PROJECT_ID --format='value(status.url)'"

echo ""
echo "📋 MCP 클라이언트 설정:"
echo "서비스 URL을 받은 후 mcp_client_config.json에 설정하세요."
