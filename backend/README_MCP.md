# GCP MCP 서버

Google Cloud Platform 리소스를 자동으로 관리할 수 있는 MCP (Model Context Protocol) 서버입니다.

## 🚀 기능

- **프로젝트 관리**: GCP 프로젝트 목록 조회
- **Cloud Run 관리**: 서비스 배포, 상태 조회, 로그 확인
- **Cloud Build**: 빌드 트리거 실행
- **자동화**: GCP 리소스 자동 관리

## 📋 사용 가능한 도구

### 1. gcp_list_projects
GCP 프로젝트 목록을 조회합니다.

```json
{
  "name": "gcp_list_projects",
  "arguments": {
    "filter": "lifecycleState:ACTIVE"
  }
}
```

### 2. gcp_list_services
Cloud Run 서비스 목록을 조회합니다.

```json
{
  "name": "gcp_list_services",
  "arguments": {
    "project_id": "univlabs-ai",
    "region": "asia-northeast3"
  }
}
```

### 3. gcp_deploy_service
Cloud Run 서비스를 배포합니다.

```json
{
  "name": "gcp_deploy_service",
  "arguments": {
    "project_id": "univlabs-ai",
    "service_name": "learnus-backend",
    "image_url": "gcr.io/univlabs-ai/learnus-backend",
    "region": "asia-northeast3"
  }
}
```

### 4. gcp_get_logs
Cloud Run 서비스 로그를 조회합니다.

```json
{
  "name": "gcp_get_logs",
  "arguments": {
    "project_id": "univlabs-ai",
    "service_name": "learnus-backend",
    "region": "asia-northeast3",
    "lines": 100
  }
}
```

### 5. gcp_trigger_build
Cloud Build 트리거를 실행합니다.

```json
{
  "name": "gcp_trigger_build",
  "arguments": {
    "project_id": "univlabs-ai",
    "trigger_name": "learnus-backend-trigger"
  }
}
```

### 6. gcp_get_service_status
Cloud Run 서비스 상태를 조회합니다.

```json
{
  "name": "gcp_get_service_status",
  "arguments": {
    "project_id": "univlabs-ai",
    "service_name": "learnus-backend",
    "region": "asia-northeast3"
  }
}
```

## 🛠️ 배포 방법

### 1. MCP 서버 배포

```bash
# 배포 스크립트 실행
chmod +x deploy_mcp_server.sh
./deploy_mcp_server.sh
```

### 2. MCP 클라이언트 설정

배포 완료 후 받은 서비스 URL을 `mcp_client_config.json`에 설정하세요.

```json
{
  "mcpServers": {
    "gcp-mcp-server": {
      "command": "npx",
      "args": [
        "-y",
        "mcp-remote",
        "http://실제-서비스-URL/sse"
      ]
    }
  }
}
```

## 🔧 로컬 개발

### 1. 의존성 설치

```bash
pip install -r requirements.mcp.txt
```

### 2. MCP 서버 실행

```bash
python mcp_server.py
```

## 📊 사용 예시

MCP 서버를 통해 다음과 같은 자동화가 가능합니다:

1. **자동 배포**: 코드 변경 시 자동으로 Cloud Run에 배포
2. **상태 모니터링**: 서비스 상태를 실시간으로 모니터링
3. **로그 분석**: 서비스 로그를 자동으로 분석하고 문제점 파악
4. **리소스 관리**: GCP 리소스를 자동으로 관리하고 최적화

## 🔐 인증

MCP 서버는 Google Cloud SDK를 사용하여 GCP 리소스에 접근합니다. 
배포 시 서비스 계정 키를 설정하거나 Workload Identity를 사용하세요.

## 📝 로그

MCP 서버의 로그는 Cloud Run 로그에서 확인할 수 있습니다:

```bash
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=gcp-mcp-server" --limit=50
```
