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

# 🔥 Cloud Run 환경에서 Chrome 실행을 위한 스크립트 생성
RUN echo '#!/bin/bash\n\
# Cloud Run 환경에서 Chrome 실행을 위한 설정\n\
export DISPLAY=:99\n\
export CHROME_BIN=/usr/bin/google-chrome\n\
export CHROMEDRIVER_PATH=/usr/bin/chromedriver\n\
\n\
# 가상 디스플레이 시작 (DevToolsActivePort 오류 해결)\n\
Xvfb :99 -screen 0 1920x1080x24 -ac +extension GLX +render -noreset &\n\
\n\
# Chrome이 디스플레이에 접근할 수 있도록 권한 설정\n\
xhost +local:docker\n\
\n\
# Cloud Run 환경에서 Chrome 실행을 위한 추가 설정\n\
mkdir -p /tmp/.X11-unix\n\
chmod 1777 /tmp/.X11-unix\n\
\n\
# 잠시 대기 후 앱 실행\n\
sleep 3\n\
\n\
# 앱 실행\n\
exec "$@"' > /start.sh && chmod +x /start.sh

# 🔥 Cloud Run 환경에서 앱 실행
CMD ["/start.sh", "uvicorn", "scheduler_server:app", "--host", "0.0.0.0", "--port", "8080"]