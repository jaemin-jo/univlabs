#!/bin/bash

# MCP 서버용 Cloud Build 트리거 생성 스크립트

set -e

PROJECT_ID="univlabs-ai"
TRIGGER_NAME="gcp-mcp-server-trigger"
REPO_NAME="univlabs"
BRANCH_NAME="main"
BUILD_CONFIG="backend/cloudbuild.mcp.yaml"

echo "🔧 MCP 서버용 Cloud Build 트리거를 생성합니다..."

# Cloud Build 트리거 생성
gcloud builds triggers create github \
    --repo-name=$REPO_NAME \
    --repo-owner=jaemin-jo \
    --branch-pattern="^main$" \
    --build-config=$BUILD_CONFIG \
    --name=$TRIGGER_NAME \
    --project=$PROJECT_ID \
    --description="MCP 서버 자동 배포 트리거"

echo "✅ MCP 서버용 Cloud Build 트리거가 생성되었습니다!"
echo "📋 트리거 정보:"
echo "  - 이름: $TRIGGER_NAME"
echo "  - 저장소: $REPO_NAME"
echo "  - 브랜치: $BRANCH_NAME"
echo "  - 설정 파일: $BUILD_CONFIG"

echo ""
echo "🚀 트리거를 수동으로 실행하려면:"
echo "gcloud builds triggers run $TRIGGER_NAME --project=$PROJECT_ID"
