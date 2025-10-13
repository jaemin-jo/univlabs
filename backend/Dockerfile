FROM python:3.11-slim

# 작업 디렉토리 설정
WORKDIR /app

# 🔥 Cloud Run 환경을 위한 Chrome 설치 (DevToolsActivePort 오류 해결)
RUN echo "🔧 [DOCKERFILE] Chrome 및 의존성 패키지 설치 시작..." && \
    apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    xvfb \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libdrm2 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libxss1 \
    libnss3 \
    libxkbcommon0 \
    libx11-6 \
    libx11-xcb1 \
    libxcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxi6 \
    libxrandr2 \
    libxrender1 \
    libxss1 \
    libxtst6 \
    ca-certificates \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libdrm2 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libxss1 \
    libnss3 \
    chromium \
    chromium-driver \
    && echo "🔧 [DOCKERFILE] Google Chrome 저장소 설정 중..." && \
    wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/googlechrome-linux-keyring.gpg \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/googlechrome-linux-keyring.gpg] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list \
    && echo "🔧 [DOCKERFILE] Google Chrome 설치 중..." && \
    apt-get update \
    && apt-get install -y google-chrome-stable \
    && echo "✅ [DOCKERFILE] Google Chrome 설치 완료" && \
    rm -rf /var/lib/apt/lists/*

# 🔥 Chrome 드라이버 설치 (수동 설치 - 안정화)
RUN echo "🔧 [DOCKERFILE] ChromeDriver 설치 시작..." && \
    CHROMEDRIVER_VERSION=$(curl -s "https://googlechromelabs.github.io/chrome-for-testing/LATEST_RELEASE_STABLE") \
    && echo "🔧 [DOCKERFILE] ChromeDriver 버전: $CHROMEDRIVER_VERSION" \
    && echo "🔧 [DOCKERFILE] ChromeDriver 다운로드 중..." && \
    wget -O /tmp/chromedriver.zip "https://storage.googleapis.com/chrome-for-testing-public/${CHROMEDRIVER_VERSION}/linux64/chromedriver-linux64.zip" \
    && echo "🔧 [DOCKERFILE] ChromeDriver 압축 해제 중..." && \
    unzip /tmp/chromedriver.zip -d /tmp/ \
    && echo "🔧 [DOCKERFILE] ChromeDriver 설치 중..." && \
    mv /tmp/chromedriver-linux64/chromedriver /usr/bin/chromedriver \
    && chmod +x /usr/bin/chromedriver \
    && echo "🔧 [DOCKERFILE] ChromeDriver 버전 확인 중..." && \
    /usr/bin/chromedriver --version \
    && echo "✅ [DOCKERFILE] ChromeDriver 설치 완료" && \
    rm -rf /tmp/chromedriver.zip /tmp/chromedriver-linux64

# 🔥 WebDriver Manager 캐시 정리 (문제 해결)
RUN rm -rf /root/.wdm/ || true
RUN rm -rf /root/.cache/ || true

# 🔥 Cloud Run 환경을 위한 권한 설정
RUN chmod 755 /usr/bin/chromedriver \
    && chmod 755 /usr/bin/google-chrome \
    && chmod 755 /usr/bin/chromium

# Python 의존성 설치
COPY requirements.txt .
RUN echo "🔧 [DOCKERFILE] Python 의존성 설치 시작..." && \
    pip install --no-cache-dir -r requirements.txt && \
    echo "✅ [DOCKERFILE] Python 의존성 설치 완료"

# 앱 코드 복사
COPY . .
RUN echo "🔧 [DOCKERFILE] 앱 코드 복사 완료" && \
    echo "📁 [DOCKERFILE] 복사된 파일 목록:" && \
    ls -la && \
    echo "✅ [DOCKERFILE] 앱 코드 복사 완료"

# 포트 노출 (Cloud Run은 8080 포트 사용)
EXPOSE 8080

# 🔥 Cloud Run 환경을 위한 환경 변수 설정
ENV DISPLAY=:99
ENV DEBIAN_FRONTEND=noninteractive
ENV CHROME_BIN=/usr/bin/google-chrome
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver
ENV PORT=8080
ENV CHROME_DISABLED=false
# Cloud Run 타임아웃 설정
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV UVICORN_TIMEOUT=300

# 🔥 Cloud Run 환경에서 Chrome 실행을 위한 스크립트 생성
RUN echo '#!/bin/bash\n\
# Cloud Run 환경에서 Chrome 실행을 위한 설정\n\
echo "🔧 [START.SH] Start script 시작..."\n\
echo "📅 [START.SH] 현재 시간: $(date)"\n\
echo "🖥️ [START.SH] 시스템 정보:"\n\
echo "  OS: $(uname -a)"\n\
echo "  메모리: $(free -h)"\n\
echo "  디스크: $(df -h /)"\n\
echo "  CPU: $(nproc) cores"\n\
echo "  사용자: $(whoami)"\n\
echo "  작업 디렉토리: $(pwd)"\n\
\n\
export DISPLAY=:99\n\
export CHROME_BIN=/usr/bin/google-chrome\n\
export CHROMEDRIVER_PATH=/usr/bin/chromedriver\n\
export WDM_LOG_LEVEL=0\n\
export PORT=${PORT:-8080}\n\
\n\
echo "🔧 [START.SH] 환경 변수 설정:"\n\
echo "  DISPLAY=$DISPLAY"\n\
echo "  CHROME_BIN=$CHROME_BIN"\n\
echo "  CHROMEDRIVER_PATH=$CHROMEDRIVER_PATH"\n\
echo "  PORT=$PORT"\n\
\n\
# X11 디렉토리 설정\n\
echo "📁 [START.SH] X11 디렉토리 설정..."\n\
mkdir -p /tmp/.X11-unix 2>/dev/null || true\n\
chmod 1777 /tmp/.X11-unix 2>/dev/null || true\n\
echo "✅ [START.SH] X11 디렉토리 설정 완료"\n\
\n\
# Chrome 설치 확인\n\
echo "🔍 [START.SH] Chrome 설치 확인:"\n\
if [ -f "$CHROME_BIN" ]; then\n\
    echo "  ✅ [START.SH] Chrome 설치됨: $CHROME_BIN"\n\
    $CHROME_BIN --version 2>/dev/null || echo "  ⚠️ [START.SH] Chrome 버전 확인 실패"\n\
else\n\
    echo "  ❌ [START.SH] Chrome 설치되지 않음: $CHROME_BIN"\n\
fi\n\
\n\
# ChromeDriver 설치 확인\n\
echo "🔍 [START.SH] ChromeDriver 설치 확인:"\n\
if [ -f "$CHROMEDRIVER_PATH" ]; then\n\
    echo "  ✅ [START.SH] ChromeDriver 설치됨: $CHROMEDRIVER_PATH"\n\
    $CHROMEDRIVER_PATH --version 2>/dev/null || echo "  ⚠️ [START.SH] ChromeDriver 버전 확인 실패"\n\
else\n\
    echo "  ❌ [START.SH] ChromeDriver 설치되지 않음: $CHROMEDRIVER_PATH"\n\
fi\n\
\n\
# 가상 디스플레이 시작 (백그라운드, 오류 무시)\n\
echo "🖥️ [START.SH] Xvfb 시작 시도..."\n\
Xvfb :99 -screen 0 1920x1080x24 -ac +extension GLX +render -noreset >/dev/null 2>&1 &\n\
XVFB_PID=$!\n\
echo "✅ [START.SH] Xvfb 시작됨 (PID: $XVFB_PID)"\n\
\n\
# Xvfb 시작 대기\n\
echo "⏳ [START.SH] Xvfb 초기화 대기 중..."\n\
sleep 5\n\
\n\
# Xvfb 프로세스 확인\n\
if ps -p $XVFB_PID > /dev/null; then\n\
    echo "✅ [START.SH] Xvfb 프로세스 실행 중 (PID: $XVFB_PID)"\n\
else\n\
    echo "❌ [START.SH] Xvfb 프로세스 종료됨"\n\
fi\n\
\n\
# Chrome 환경 변수 출력\n\
echo "🔍 [START.SH] 환경 변수 확인:"\n\
echo "  DISPLAY=$DISPLAY"\n\
echo "  CHROME_BIN=$CHROME_BIN"\n\
echo "  CHROMEDRIVER_PATH=$CHROMEDRIVER_PATH"\n\
echo "  PORT=$PORT"\n\
echo "  PYTHONPATH=$PYTHONPATH"\n\
echo "  PYTHONUNBUFFERED=$PYTHONUNBUFFERED"\n\
\n\
# Python 환경 확인\n\
echo "🐍 [START.SH] Python 환경 확인:"\n\
echo "  Python 버전: $(python --version)"\n\
echo "  Python 경로: $(which python)"\n\
echo "  작업 디렉토리: $(pwd)"\n\
echo "  파일 목록: $(ls -la)"\n\
\n\
# Python 패키지 확인\n\
echo "📦 [START.SH] Python 패키지 확인:"\n\
python -c "import selenium; print(f'  Selenium: {selenium.__version__}')" 2>/dev/null || echo "  ❌ Selenium 설치되지 않음"\n\
python -c "import fastapi; print(f'  FastAPI: {fastapi.__version__}')" 2>/dev/null || echo "  ❌ FastAPI 설치되지 않음"\n\
python -c "import firebase_admin; print('  Firebase Admin: 설치됨')" 2>/dev/null || echo "  ❌ Firebase Admin 설치되지 않음"\n\
\n\
# 애플리케이션 시작\n\
echo "🚀 [START.SH] 애플리케이션 시작..."\n\
echo "📅 [START.SH] 시작 시간: $(date)"\n\
exec "$@"' > /start.sh && chmod +x /start.sh

# 🔥 Cloud Run 환경에서 앱 실행 (단순화된 방법)
CMD ["python", "scheduler_server.py"]