#!/usr/bin/env python3
"""
가장 단순한 테스트 서버 - Cloud Run 시작 문제 진단용
"""

from fastapi import FastAPI
import uvicorn
import os
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Simple Test Server")

@app.get("/")
async def root():
    """기본 엔드포인트"""
    return {"message": "Simple test server is running!", "status": "ok"}

@app.get("/health")
async def health():
    """헬스 체크"""
    return {"status": "healthy", "port": os.environ.get('PORT', '8080')}

@app.get("/env")
async def env_check():
    """환경 변수 확인"""
    return {
        "PORT": os.environ.get('PORT', 'Not set'),
        "DISPLAY": os.environ.get('DISPLAY', 'Not set'),
        "CHROME_BIN": os.environ.get('CHROME_BIN', 'Not set'),
        "CHROMEDRIVER_PATH": os.environ.get('CHROMEDRIVER_PATH', 'Not set')
    }

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8080))
    logger.info(f"🚀 Simple test server starting on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
