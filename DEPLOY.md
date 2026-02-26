# Putting the app on a server

Two ways to run it on a server: **Docker** (any cloud or VPS) or **plain Linux** (VPS with Chrome installed).

---

## Option 1: Docker (recommended)

Works on: your own server, Render, Railway, DigitalOcean App Platform, etc.

### On a server that has Docker

```bash
# Build and run (replace with your credentials)
docker build -t autoattend .
docker run -d --restart unless-stopped \
  -e USERNAME=your_username \
  -e PASSWORD=your_password \
  --name autoattend \
  autoattend
```

- Logs: `docker logs -f autoattend`
- Stop: `docker stop autoattend`

### On Render.com

1. New → Web Service → connect this repo.
2. Build: **Docker** (use Dockerfile).
3. Env vars: `USERNAME`, `PASSWORD` (and optionally `SHOW_UI=false`).
4. Deploy. The app runs in the background (no HTTP port needed for this script).

### On Railway.app

1. New project → Deploy from GitHub → select this repo.
2. Add variables: `USERNAME`, `PASSWORD`.
3. Railway will build from the Dockerfile and run the container.

---

## Option 2: Linux VPS (Ubuntu/Debian) without Docker

You need: Python 3, Chrome, ChromeDriver, and the app running as a service.

### 1. Install Chrome and ChromeDriver

```bash
sudo apt update && sudo apt install -y wget gnupg curl unzip

# Chrome
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo gpg --dearmor -o /usr/share/keyrings/googlechrome.gpg
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/googlechrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
sudo apt update && sudo apt install -y google-chrome-stable

# ChromeDriver
CHROMEDRIVER_VERSION=$(curl -sS https://googlechromelabs.github.io/chrome-for-testing/LATEST_RELEASE_STABLE)
wget -q https://storage.googleapis.com/chrome-for-testing-public/$CHROMEDRIVER_VERSION/linux64/chromedriver-linux64.zip -O /tmp/chromedriver.zip
sudo unzip -q /tmp/chromedriver.zip -d /tmp && sudo mv /tmp/chromedriver-linux64/chromedriver /usr/local/bin/ && sudo chmod +x /usr/local/bin/chromedriver
rm /tmp/chromedriver.zip
```

### 2. Clone repo and install Python deps

```bash
cd /opt  # or your preferred path
sudo git clone https://github.com/Asylniet/autoattend.git
cd autoattend
sudo python3 -m venv venv
sudo venv/bin/pip install -r requirements.txt
```

### 3. Run with env vars (no secrets in code)

```bash
export USERNAME=your_username
export PASSWORD=your_password
./venv/bin/python main.py
```

### 4. Run as a systemd service (starts on boot, restarts on crash)

```bash
sudo nano /etc/systemd/system/attendance.service
```

Paste (adjust paths and user):

```ini
[Unit]
Description=KBTU Auto Attendance
After=network.target

[Service]
Type=simple
User=YOUR_USER
WorkingDirectory=/opt/autoattend
Environment="USERNAME=your_username"
Environment="PASSWORD=your_password"
Environment="SHOW_UI=false"
ExecStart=/opt/autoattend/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Then:

```bash
sudo systemctl daemon-reload
sudo systemctl enable attendance
sudo systemctl start attendance
sudo systemctl status attendance
```

Logs: `journalctl -u attendance -f`

---

## Summary

| Where        | How                          |
|-------------|------------------------------|
| Any server  | Docker (Option 1)            |
| Render      | Docker + env vars            |
| Railway     | Docker + env vars            |
| Ubuntu VPS  | Chrome + venv + systemd (Option 2) |

Always set **USERNAME** and **PASSWORD** via environment (or in `main.py` only for local use). Never commit real credentials to the repo.
