FROM python:3.11-slim

# 작업 디렉토리 설정
WORKDIR /app

# 🔥 Cloud Run 환경을 위한 Chrome 설치 (DevToolsActivePort 오류 해결)
RUN apt-get update && apt-get install -y \
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
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/googlechrome-linux-keyring.gpg \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/googlechrome-linux-keyring.gpg] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# 🔥 Chrome 드라이버 설치 (수동 설치 - 안정화)
RUN CHROMEDRIVER_VERSION=$(curl -s "https://googlechromelabs.github.io/chrome-for-testing/LATEST_RELEASE_STABLE") \
    && echo "ChromeDriver 버전: $CHROMEDRIVER_VERSION" \
    && wget -O /tmp/chromedriver.zip "https://storage.googleapis.com/chrome-for-testing-public/${CHROMEDRIVER_VERSION}/linux64/chromedriver-linux64.zip" \
    && unzip /tmp/chromedriver.zip -d /tmp/ \
    && mv /tmp/chromedriver-linux64/chromedriver /usr/bin/chromedriver \
    && chmod +x /usr/bin/chromedriver \
    && rm -rf /tmp/chromedriver.zip /tmp/chromedriver-linux64 \
    && /usr/bin/chromedriver --version

# 🔥 WebDriver Manager 캐시 정리 (문제 해결)
RUN rm -rf /root/.wdm/drivers/chromedriver/ || true

# 🔥 Cloud Run 환경을 위한 권한 설정
RUN chmod 755 /usr/bin/chromedriver \
    && chmod 755 /usr/bin/google-chrome \
    && chmod 755 /usr/bin/chromium

# Python 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 앱 코드 복사
COPY . .

# 포트 노출 (Cloud Run은 8080 포트 사용)
EXPOSE 8080

# 🔥 Cloud Run 환경을 위한 환경 변수 설정
ENV DISPLAY=:99
ENV DEBIAN_FRONTEND=noninteractive
ENV CHROME_BIN=/usr/bin/google-chrome
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver
ENV PORT=8080
ENV CHROME_DISABLED=true
# Cloud Run 타임아웃 설정
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV UVICORN_TIMEOUT=300

# 🔥 Cloud Run 환경에서 앱 실행 (PORT 환경 변수 사용, 타임아웃 증가)
CMD ["sh", "-c", "echo 'Starting server on port ${PORT:-8080}' && echo 'Waiting for initialization...' && sleep 10 && python -m uvicorn scheduler_server:app --host 0.0.0.0 --port ${PORT:-8080} --workers 1 --timeout-keep-alive 300"]