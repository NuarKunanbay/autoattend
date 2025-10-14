# Auto Attendance Server

A 24/7 server that automatically handles attendance for KBTU online classes using Selenium WebDriver.

## Features

- 🕐 **Runs every minute** - Automatically checks for attendance opportunities
- 🌐 **Web server** - Provides status endpoints and monitoring
- 📊 **Logging** - Comprehensive logging to file and console
- 🔄 **Auto-restart** - Handles crashes and restarts automatically
- 🖥️ **Headless mode** - Runs without GUI for server environments
- ⚡ **Systemd integration** - Can run as a system service

## Quick Start

### 1. Setup

```bash
# Run the setup script
./setup.sh
```

### 2. Configure Credentials

Edit `main.py` and set your credentials:

```python
USERNAME = "your_username"
PASSWORD = "your_password"
```

### 3. Test Run

```bash
# Activate virtual environment
source venv/bin/activate

# Run the server
python main.py
```

The server will start on `http://localhost:5000`

## API Endpoints

- **GET /** - Home page with basic status
- **GET /status** - Detailed server status
- **GET /health** - Health check endpoint

## 24/7 Operation

### Option 1: Systemd Service (Recommended for Linux)

```bash
# Copy service file
sudo cp attendance-server.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable and start service
sudo systemctl enable attendance-server
sudo systemctl start attendance-server

# Check status
sudo systemctl status attendance-server

# View logs
sudo journalctl -u attendance-server -f
```

### Option 2: macOS LaunchAgent

```bash
# Copy plist to LaunchAgents directory
cp attendance-server.plist ~/Library/LaunchAgents/

# Load and start the service
launchctl load ~/Library/LaunchAgents/attendance-server.plist
launchctl start attendance-server

# Check status
launchctl list | grep attendance-server
```

### Option 3: Manual Background Process

```bash
# Run in background with nohup
nohup python main.py > server.log 2>&1 &

# Or use screen/tmux
screen -S attendance-server
python main.py
# Press Ctrl+A, D to detach
```

## Monitoring

### Log Files

- `attendance_server.log` - Application logs
- System logs (journalctl on Linux, Console.app on macOS)

### Status Monitoring

```bash
# Check server status
curl http://localhost:5000/status

# Health check
curl http://localhost:5000/health
```

### Example Status Response

```json
{
  "server_status": "running",
  "scheduler_running": true,
  "driver_initialized": true,
  "last_run_time": "2024-01-15T10:30:00",
  "last_run_status": "Successfully attended 2 classes",
  "total_runs": 150,
  "username_configured": true,
  "password_configured": true
}
```

## Configuration

### Environment Variables

- `SHOW_UI` - Set to `False` for headless mode (default)
- `UPDATE_INTERVAL` - How often to check (default: 60 seconds)
- `WAIT_TIME` - Selenium wait timeout (default: 10 seconds)

### Chrome Options

The server automatically configures Chrome with:
- Headless mode (when `SHOW_UI=False`)
- No sandbox mode
- Disabled GPU
- Optimized window size

## Troubleshooting

### Common Issues

1. **Chrome not found**
   ```bash
   # Install Chrome
   brew install --cask google-chrome  # macOS
   sudo apt-get install google-chrome-stable  # Ubuntu
   ```

2. **Permission denied**
   ```bash
   chmod +x setup.sh
   ```

3. **Port already in use**
   - Change port in `main.py`: `app.run(host='0.0.0.0', port=5001)`

4. **Login failures**
   - Check credentials in `main.py`
   - Verify network connectivity
   - Check if website structure changed

### Log Analysis

```bash
# View recent logs
tail -f attendance_server.log

# Search for errors
grep -i error attendance_server.log

# Count successful runs
grep -c "Successfully attended" attendance_server.log
```

## Security Notes

- Store credentials securely
- Use environment variables for production
- Consider using a dedicated user account
- Regularly update dependencies

## Dependencies

- Python 3.7+
- Chrome/Chromium browser
- Selenium WebDriver
- Flask (web server)
- APScheduler (task scheduling)

## License

This project is for educational purposes. Use responsibly and in accordance with your institution's policies.