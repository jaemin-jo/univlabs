#!/usr/bin/env python3
"""
MCP (Model Context Protocol) Server for Google Cloud Platform
Cloud Run에서 GCP 리소스를 자동으로 관리할 수 있는 MCP 서버
"""

import asyncio
import json
import logging
import os
import subprocess
import sys
from typing import Any, Dict, List, Optional
from datetime import datetime

# MCP 서버 구현을 위한 라이브러리
try:
    from mcp.server import Server
    from mcp.server.models import InitializationOptions
    from mcp.server.stdio import stdio_server
    from mcp.types import (
        CallToolRequest,
        CallToolResult,
        ListResourcesRequest,
        ListResourcesResult,
        ListToolsRequest,
        ListToolsResult,
        ReadResourceRequest,
        ReadResourceResult,
        Resource,
        Tool,
    )
except ImportError:
    print("MCP 라이브러리가 설치되지 않았습니다. 설치 중...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "mcp"])
    from mcp.server import Server
    from mcp.server.models import InitializationOptions
    from mcp.server.stdio import stdio_server
    from mcp.types import (
        CallToolRequest,
        CallToolResult,
        ListResourcesRequest,
        ListResourcesResult,
        ListToolsRequest,
        ListToolsResult,
        ReadResourceRequest,
        ReadResourceResult,
        Resource,
        Tool,
    )

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GCPMCPServer:
    """GCP 리소스를 관리하는 MCP 서버"""
    
    def __init__(self):
        self.server = Server("gcp-mcp-server")
        self.setup_handlers()
        
    def setup_handlers(self):
        """MCP 서버 핸들러 설정"""
        
        @self.server.list_tools()
        async def list_tools() -> ListToolsResult:
            """사용 가능한 GCP 도구 목록 반환"""
            tools = [
                Tool(
                    name="gcp_list_projects",
                    description="Google Cloud Platform 프로젝트 목록 조회",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "filter": {
                                "type": "string",
                                "description": "프로젝트 필터 (선택사항)"
                            }
                        }
                    }
                ),
                Tool(
                    name="gcp_list_services",
                    description="Cloud Run 서비스 목록 조회",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "project_id": {
                                "type": "string",
                                "description": "GCP 프로젝트 ID"
                            },
                            "region": {
                                "type": "string",
                                "description": "리전 (예: asia-northeast3)"
                            }
                        },
                        "required": ["project_id"]
                    }
                ),
                Tool(
                    name="gcp_deploy_service",
                    description="Cloud Run 서비스 배포",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "project_id": {
                                "type": "string",
                                "description": "GCP 프로젝트 ID"
                            },
                            "service_name": {
                                "type": "string",
                                "description": "서비스 이름"
                            },
                            "image_url": {
                                "type": "string",
                                "description": "컨테이너 이미지 URL"
                            },
                            "region": {
                                "type": "string",
                                "description": "리전 (예: asia-northeast3)"
                            }
                        },
                        "required": ["project_id", "service_name", "image_url"]
                    }
                ),
                Tool(
                    name="gcp_get_logs",
                    description="Cloud Run 서비스 로그 조회",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "project_id": {
                                "type": "string",
                                "description": "GCP 프로젝트 ID"
                            },
                            "service_name": {
                                "type": "string",
                                "description": "서비스 이름"
                            },
                            "region": {
                                "type": "string",
                                "description": "리전 (예: asia-northeast3)"
                            },
                            "lines": {
                                "type": "integer",
                                "description": "조회할 로그 라인 수 (기본값: 100)"
                            }
                        },
                        "required": ["project_id", "service_name"]
                    }
                ),
                Tool(
                    name="gcp_trigger_build",
                    description="Cloud Build 트리거 실행",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "project_id": {
                                "type": "string",
                                "description": "GCP 프로젝트 ID"
                            },
                            "trigger_name": {
                                "type": "string",
                                "description": "트리거 이름"
                            }
                        },
                        "required": ["project_id", "trigger_name"]
                    }
                ),
                Tool(
                    name="gcp_get_service_status",
                    description="Cloud Run 서비스 상태 조회",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "project_id": {
                                "type": "string",
                                "description": "GCP 프로젝트 ID"
                            },
                            "service_name": {
                                "type": "string",
                                "description": "서비스 이름"
                            },
                            "region": {
                                "type": "string",
                                "description": "리전 (예: asia-northeast3)"
                            }
                        },
                        "required": ["project_id", "service_name"]
                    }
                )
            ]
            return ListToolsResult(tools=tools)
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
            """GCP 도구 실행"""
            try:
                if name == "gcp_list_projects":
                    return await self._list_projects(arguments)
                elif name == "gcp_list_services":
                    return await self._list_services(arguments)
                elif name == "gcp_deploy_service":
                    return await self._deploy_service(arguments)
                elif name == "gcp_get_logs":
                    return await self._get_logs(arguments)
                elif name == "gcp_trigger_build":
                    return await self._trigger_build(arguments)
                elif name == "gcp_get_service_status":
                    return await self._get_service_status(arguments)
                else:
                    return CallToolResult(
                        content=[{"type": "text", "text": f"알 수 없는 도구: {name}"}],
                        isError=True
                    )
            except Exception as e:
                logger.error(f"도구 실행 오류: {e}")
                return CallToolResult(
                    content=[{"type": "text", "text": f"오류 발생: {str(e)}"}],
                    isError=True
                )
    
    async def _list_projects(self, args: Dict[str, Any]) -> CallToolResult:
        """GCP 프로젝트 목록 조회"""
        try:
            cmd = ["gcloud", "projects", "list", "--format=json"]
            if args.get("filter"):
                cmd.extend(["--filter", args["filter"]])
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            projects = json.loads(result.stdout)
            
            content = f"📋 GCP 프로젝트 목록 ({len(projects)}개):\n\n"
            for project in projects:
                content += f"• {project.get('name', 'N/A')} ({project.get('projectId', 'N/A')})\n"
                content += f"  상태: {project.get('lifecycleState', 'N/A')}\n"
                content += f"  생성일: {project.get('createTime', 'N/A')}\n\n"
            
            return CallToolResult(
                content=[{"type": "text", "text": content}]
            )
        except subprocess.CalledProcessError as e:
            return CallToolResult(
                content=[{"type": "text", "text": f"프로젝트 목록 조회 실패: {e.stderr}"}],
                isError=True
            )
    
    async def _list_services(self, args: Dict[str, Any]) -> CallToolResult:
        """Cloud Run 서비스 목록 조회"""
        try:
            project_id = args["project_id"]
            region = args.get("region", "asia-northeast3")
            
            cmd = [
                "gcloud", "run", "services", "list",
                f"--project={project_id}",
                f"--region={region}",
                "--format=json"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            services = json.loads(result.stdout)
            
            content = f"🚀 Cloud Run 서비스 목록 ({len(services)}개):\n\n"
            for service in services:
                content += f"• {service.get('metadata', {}).get('name', 'N/A')}\n"
                content += f"  URL: {service.get('status', {}).get('url', 'N/A')}\n"
                content += f"  상태: {service.get('status', {}).get('conditions', [{}])[0].get('status', 'N/A')}\n"
                content += f"  리전: {service.get('metadata', {}).get('labels', {}).get('cloud.googleapis.com/location', 'N/A')}\n\n"
            
            return CallToolResult(
                content=[{"type": "text", "text": content}]
            )
        except subprocess.CalledProcessError as e:
            return CallToolResult(
                content=[{"type": "text", "text": f"서비스 목록 조회 실패: {e.stderr}"}],
                isError=True
            )
    
    async def _deploy_service(self, args: Dict[str, Any]) -> CallToolResult:
        """Cloud Run 서비스 배포"""
        try:
            project_id = args["project_id"]
            service_name = args["service_name"]
            image_url = args["image_url"]
            region = args.get("region", "asia-northeast3")
            
            cmd = [
                "gcloud", "run", "deploy", service_name,
                f"--image={image_url}",
                f"--project={project_id}",
                f"--region={region}",
                "--platform=managed",
                "--allow-unauthenticated"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            content = f"✅ Cloud Run 서비스 배포 완료:\n\n"
            content += f"• 서비스: {service_name}\n"
            content += f"• 이미지: {image_url}\n"
            content += f"• 프로젝트: {project_id}\n"
            content += f"• 리전: {region}\n\n"
            content += f"배포 로그:\n{result.stdout}"
            
            return CallToolResult(
                content=[{"type": "text", "text": content}]
            )
        except subprocess.CalledProcessError as e:
            return CallToolResult(
                content=[{"type": "text", "text": f"서비스 배포 실패: {e.stderr}"}],
                isError=True
            )
    
    async def _get_logs(self, args: Dict[str, Any]) -> CallToolResult:
        """Cloud Run 서비스 로그 조회"""
        try:
            project_id = args["project_id"]
            service_name = args["service_name"]
            region = args.get("region", "asia-northeast3")
            lines = args.get("lines", 100)
            
            cmd = [
                "gcloud", "logging", "read",
                f"resource.type=cloud_run_revision AND resource.labels.service_name={service_name}",
                f"--project={project_id}",
                f"--limit={lines}",
                "--format=json"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            logs = json.loads(result.stdout)
            
            content = f"📋 {service_name} 서비스 로그 (최근 {lines}개):\n\n"
            for log in logs:
                timestamp = log.get('timestamp', 'N/A')
                severity = log.get('severity', 'INFO')
                message = log.get('textPayload', log.get('jsonPayload', {}).get('message', 'N/A'))
                content += f"[{timestamp}] {severity}: {message}\n"
            
            return CallToolResult(
                content=[{"type": "text", "text": content}]
            )
        except subprocess.CalledProcessError as e:
            return CallToolResult(
                content=[{"type": "text", "text": f"로그 조회 실패: {e.stderr}"}],
                isError=True
            )
    
    async def _trigger_build(self, args: Dict[str, Any]) -> CallToolResult:
        """Cloud Build 트리거 실행"""
        try:
            project_id = args["project_id"]
            trigger_name = args["trigger_name"]
            
            cmd = [
                "gcloud", "builds", "triggers", "run", trigger_name,
                f"--project={project_id}"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            content = f"🔨 Cloud Build 트리거 실행 완료:\n\n"
            content += f"• 트리거: {trigger_name}\n"
            content += f"• 프로젝트: {project_id}\n\n"
            content += f"실행 결과:\n{result.stdout}"
            
            return CallToolResult(
                content=[{"type": "text", "text": content}]
            )
        except subprocess.CalledProcessError as e:
            return CallToolResult(
                content=[{"type": "text", "text": f"빌드 트리거 실행 실패: {e.stderr}"}],
                isError=True
            )
    
    async def _get_service_status(self, args: Dict[str, Any]) -> CallToolResult:
        """Cloud Run 서비스 상태 조회"""
        try:
            project_id = args["project_id"]
            service_name = args["service_name"]
            region = args.get("region", "asia-northeast3")
            
            cmd = [
                "gcloud", "run", "services", "describe", service_name,
                f"--project={project_id}",
                f"--region={region}",
                "--format=json"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            service = json.loads(result.stdout)
            
            status = service.get('status', {})
            conditions = status.get('conditions', [])
            
            content = f"📊 {service_name} 서비스 상태:\n\n"
            content += f"• URL: {status.get('url', 'N/A')}\n"
            content += f"• 최신 리비전: {status.get('latestReadyRevisionName', 'N/A')}\n"
            content += f"• 트래픽 할당: {status.get('traffic', [{}])[0].get('percent', 'N/A')}%\n\n"
            
            content += "상태 조건:\n"
            for condition in conditions:
                content += f"• {condition.get('type', 'N/A')}: {condition.get('status', 'N/A')}\n"
            
            return CallToolResult(
                content=[{"type": "text", "text": content}]
            )
        except subprocess.CalledProcessError as e:
            return CallToolResult(
                content=[{"type": "text", "text": f"서비스 상태 조회 실패: {e.stderr}"}],
                isError=True
            )
    
    async def run(self):
        """MCP 서버 실행"""
        logger.info("🚀 GCP MCP 서버 시작...")
        
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="gcp-mcp-server",
                    server_version="1.0.0",
                    capabilities=self.server.get_capabilities(
                        notification_options=None,
                        experimental_capabilities=None,
                    ),
                ),
            )

async def main():
    """메인 함수"""
    server = GCPMCPServer()
    await server.run()

if __name__ == "__main__":
    asyncio.run(main())
