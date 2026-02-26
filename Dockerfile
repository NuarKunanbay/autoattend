# Auto-attend: Chrome + ChromeDriver + Python
FROM python:3.11-slim

WORKDIR /app

# Install Chrome and dependencies
RUN apt-get update && apt-get install -y \
    wget gnupg curl unzip ca-certificates \
    libnss3 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 libxkbcommon0 \
    libxcomposite1 libxdamage1 libxfixes3 libxrandr2 libgbm1 libasound2 \
    && wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/googlechrome.gpg \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/googlechrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# ChromeDriver: install version that matches installed Chrome (major version)
RUN CHROME_MAJOR=$(google-chrome --version | sed 's/.* \([0-9]*\)\..*/\1/') \
    && echo "Chrome major version: $CHROME_MAJOR" \
    && CHROMEDRIVER_VERSION=$(curl -sS "https://googlechromelabs.github.io/chrome-for-testing/LATEST_RELEASE_${CHROME_MAJOR}") \
    && echo "ChromeDriver version: $CHROMEDRIVER_VERSION" \
    && wget -q "https://storage.googleapis.com/chrome-for-testing-public/${CHROMEDRIVER_VERSION}/linux64/chromedriver-linux64.zip" -O /tmp/chromedriver.zip \
    && unzip -q /tmp/chromedriver.zip -d /tmp \
    && mv /tmp/chromedriver-linux64/chromedriver /usr/local/bin/ \
    && chmod +x /usr/local/bin/chromedriver \
    && rm -rf /tmp/chromedriver.zip /tmp/chromedriver-linux64 \
    && chromedriver --version

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY main.py .

# No USER switch so chromedriver can run; adjust if you need non-root
CMD ["python", "main.py"]
