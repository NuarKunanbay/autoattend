# Render Deployment Checklist & Fixes

## ✅ Fixes Applied

### 1. **Port Configuration** ✅ FIXED
- Updated `main.py` to use `PORT` environment variable (Render requirement)
- Falls back to port 5000 if PORT is not set

### 2. **Chrome Options for Containers** ✅ FIXED
- Added `--single-process` for low-memory environments (Render free tier)
- Added `--disable-setuid-sandbox` for container security
- Added `--disable-extensions` and `--disable-software-rasterizer`
- Added background throttling disables for stability

### 3. **ChromeDriver Path** ✅ FIXED
- Added explicit ChromeDriver path detection
- Falls back gracefully if path not found
- Updated Dockerfile to verify ChromeDriver installation

### 4. **ChromeDriver Version Matching** ✅ FIXED
- Updated Dockerfile to match ChromeDriver version with Chrome version
- Added version verification step

## 🔧 Render Configuration Steps

### Step 1: Environment Variables
In Render dashboard, set these environment variables:
```
USERNAME=a_kunanbayev
PASSWORD=Master2005.
PORT=5000  (Render may set this automatically, but verify)
```

### Step 2: Build Settings
- **Build Command**: `docker build -t attendance-server .`
- **Start Command**: `docker run -p $PORT:5000 -e USERNAME=$USERNAME -e PASSWORD=$PASSWORD attendance-server`
- OR if using Render's Docker deployment:
  - Just point to the Dockerfile
  - Render will handle the build automatically

### Step 3: Service Settings
- **Instance Type**: At least 512MB RAM (free tier might work, but 1GB recommended)
- **Auto-Deploy**: Enable if using GitHub
- **Health Check Path**: `/health`

## 🧪 Testing After Deployment

### 1. Check Health Endpoint
```bash
curl https://your-app.onrender.com/health
```

### 2. Check Status Endpoint
```bash
curl https://your-app.onrender.com/status
```

Expected response should show:
- `driver_initialized: true`
- `username_configured: true`
- `password_configured: true`

### 3. Check Logs
In Render dashboard, check logs for:
- ✅ "WebDriver initialized successfully"
- ✅ "Login attempt completed"
- ❌ Any Chrome/ChromeDriver errors
- ❌ Any timeout errors

## 🚨 Common Issues on Render

### Issue 1: ChromeDriver Not Found
**Symptoms**: `selenium.common.exceptions.WebDriverException: 'chromedriver' executable needs to be in PATH`

**Solution**: The code now handles this with fallback paths. If still failing, check Dockerfile build logs.

### Issue 2: Out of Memory
**Symptoms**: Container crashes, "Killed" messages in logs

**Solution**: 
- Upgrade to paid tier with more RAM
- Or reduce Chrome memory usage (already optimized with `--single-process`)

### Issue 3: Login Fails Silently
**Symptoms**: Status shows driver initialized but login never completes

**Solution**: 
- Check logs for specific error messages
- Verify credentials are set correctly in environment variables
- Check if website is accessible from Render's IP (some sites block cloud IPs)

### Issue 4: Port Binding Error
**Symptoms**: `Address already in use` or service won't start

**Solution**: 
- Ensure using `PORT` environment variable (already fixed)
- Render sets this automatically, but verify it's being used

### Issue 5: Timeout Errors
**Symptoms**: `TimeoutException` in logs

**Solution**:
- Increase `WAIT_TIME` in main.py (currently 30 seconds)
- Check network connectivity from Render to target site

## 📊 Monitoring

### Key Metrics to Watch:
1. **Last Run Time**: Should update every minute
2. **Last Run Status**: Should show success messages
3. **Total Runs**: Should increment
4. **Driver Initialized**: Should always be `true`

### Log Patterns to Monitor:
- ✅ `"Starting attendance check #X"` - Scheduler is running
- ✅ `"Login attempt completed"` - Login successful
- ✅ `"Successfully attended X classes"` - Attendance working
- ❌ `"Error during login"` - Login failing
- ❌ `"Driver not initialized"` - WebDriver issues
- ❌ `"Critical error"` - Major failures

## 🔍 Debugging Commands

If you have shell access to Render (paid tier):
```bash
# Check Chrome version
google-chrome --version

# Check ChromeDriver version
chromedriver --version

# Check environment variables
echo $USERNAME
echo $PASSWORD
echo $PORT

# Test Selenium import
python -c "from selenium import webdriver; print('OK')"
```

## 📝 Additional Notes

1. **Render Free Tier Limitations**:
   - Services sleep after 15 minutes of inactivity
   - Limited CPU and memory
   - May need to upgrade for reliable 24/7 operation

2. **Keep-Alive**:
   - The `/ping` endpoint can be used with external services (like UptimeRobot) to keep the service awake
   - Set up a cron job or monitoring service to ping `/ping` every 10 minutes

3. **Credentials Security**:
   - Never commit credentials to git
   - Always use environment variables
   - Rotate credentials if exposed

## ✅ Verification Checklist

Before considering deployment successful:
- [ ] Environment variables set in Render dashboard
- [ ] Docker build completes without errors
- [ ] Service starts and stays running
- [ ] `/health` endpoint returns 200
- [ ] `/status` shows `driver_initialized: true`
- [ ] Logs show "WebDriver initialized successfully"
- [ ] Logs show "Login attempt completed" (after first run)
- [ ] No Chrome/ChromeDriver errors in logs
- [ ] Service doesn't crash after a few minutes

