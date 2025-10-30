# ngrok Windows Service Setup Guide

This guide explains how to set up ngrok as a Windows service that automatically starts with the OPIc Practice Portal.

## Prerequisites

- NSSM (Non-Sucking Service Manager) installed at `C:\nssm\nssm.exe`
- ngrok installed (version 3.24.0 or later)
- Administrator privileges
- ngrok account with authtoken

## Step-by-Step Setup

### Step 1: Configure ngrok Authentication

Before running ngrok as a service, you must configure your authtoken.

**Option A: Run the setup script (Easiest)**
1. Double-click `setup_ngrok_auth.bat`
2. Wait for confirmation message

**Option B: Manual setup**
```cmd
ngrok config add-authtoken 34dgsPtlKj96hrKsQlEkwMApokS_3vSTFeE2F3akyRM1iWDP3
```

### Step 2: Test ngrok Manually

Before installing the service, test that ngrok works:

```cmd
ngrok http https://localhost:5000 --region=ap --host-header=localhost:5000
```

You should see:
- ngrok web interface at `http://localhost:4040`
- A forwarding URL like `https://xxxxxx.ngrok-free.app`
- No authentication errors

Press `Ctrl+C` to stop when satisfied.

### Step 3: Install the ngrok Service

1. Right-click `reinstall_ngrok_service.bat`
2. Select **"Run as administrator"**
3. Wait for the installation to complete
4. Check the service status in the output

### Step 4: Verify Service is Running

Check the service status:
```cmd
C:\nssm\nssm.exe status NgrokOPIc
```

Should return: `SERVICE_RUNNING`

Check ngrok web interface:
- Visit `http://localhost:4040`
- You should see the tunnel status and forwarding URL

Check logs:
- Output: `D:\OPP\logs\ngrok_output.log`
- Errors: `D:\OPP\logs\ngrok_error.log`

## Service Configuration Details

| Setting | Value |
|---------|-------|
| **Service Name** | `NgrokOPIc` |
| **Command** | `D:\OPP\start_ngrok.bat` |
| **Working Directory** | `D:\OPP` |
| **Startup Type** | Automatic |
| **Dependencies** | Starts after `OPIcPracticePortal` |
| **Log Files** | `logs\ngrok_output.log`, `logs\ngrok_error.log` |
| **Web Interface** | `http://localhost:4040` |

## ngrok Command Parameters

```
ngrok http https://localhost:5000 --region=ap --host-header=localhost:5000
```

- `http` - HTTP/HTTPS tunnel type
- `https://localhost:5000` - Backend URL (your Flask app with SSL)
- `--region=ap` - Asia-Pacific region (lower latency for your location)
- `--host-header=localhost:5000` - Preserves the original host header

## Management Scripts

### Install/Reinstall Service
```cmd
reinstall_ngrok_service.bat  (Run as Administrator)
```
- Removes old service if exists
- Installs fresh service configuration
- Starts the service
- Shows status and logs

### Restart Service
```cmd
restart_ngrok_service.bat  (Run as Administrator)
```
- Restarts the ngrok service
- Useful after configuration changes
- Shows updated status

### Uninstall Service
```cmd
uninstall_ngrok_service.bat  (Run as Administrator)
```
- Stops the service
- Removes the service completely

### Setup Authentication
```cmd
setup_ngrok_auth.bat
```
- Configures ngrok authtoken
- Run this BEFORE installing the service

## Troubleshooting

### Service stops immediately

**Symptom:** Service shows `SERVICE_STOPPED` right after starting

**Causes:**
1. Authentication not configured
2. Port 5000 not accessible
3. ngrok.exe path incorrect

**Solutions:**
1. Run `setup_ngrok_auth.bat` to configure authtoken
2. Ensure OPIc app is running (`https://localhost:5000` accessible)
3. Check `logs\ngrok_error.log` for specific errors

### Authentication errors

**Error:**
```
ERROR: authentication failed: Usage of ngrok requires a verified account and authtoken.
```

**Solution:**
1. Run `setup_ngrok_auth.bat`
2. Or manually: `ngrok config add-authtoken YOUR_TOKEN`

### Port 5000 not accessible

**Error:**
```
ERROR: failed to start tunnel: dial tcp 127.0.0.1:5000: connect: connection refused
```

**Solution:**
1. Ensure `OPIcPracticePortal` service is running
2. Check if app is listening: `netstat -ano | findstr :5000`
3. Verify SSL certificates exist: `ssl\cert.pem` and `ssl\key.pem`

### Cannot access from LAN using ngrok URL

**This is expected behavior** (NAT hairpinning issue)

**Solution:**
- **For LAN devices:** Use local IP `https://10.84.206.173:5000`
- **For WAN devices:** Use ngrok URL `https://xxxxx.ngrok-free.app`

## Logs and Monitoring

### Check Service Status
```cmd
C:\nssm\nssm.exe status NgrokOPIc
```

### View Live Logs
```cmd
# Output log
tail -f logs\ngrok_output.log

# Error log
tail -f logs\ngrok_error.log
```

### ngrok Web Interface
Visit `http://localhost:4040` to see:
- Current tunnel status
- Public URL
- Request history
- Traffic inspection

### Get Tunnel URL Programmatically
```bash
curl http://localhost:4040/api/tunnels
```

## Service Auto-Start Behavior

The ngrok service is configured to:
1. **Start automatically** when Windows boots
2. **Start after** the main `OPIcPracticePortal` service
3. **Restart automatically** if it crashes
4. **Wait 5 seconds** before restarting (to prevent rapid restart loops)

## Files Created

- `start_ngrok.bat` - Wrapper script that NSSM runs
- `setup_ngrok_auth.bat` - Configure ngrok authentication
- `reinstall_ngrok_service.bat` - Install/reinstall service
- `restart_ngrok_service.bat` - Restart service
- `uninstall_ngrok_service.bat` - Remove service
- `logs\ngrok_output.log` - Service output log
- `logs\ngrok_error.log` - Service error log

## Security Considerations

- **Authtoken Security:** The authtoken is stored in ngrok's config file (`~/.ngrok2/ngrok.yml`)
- **HTTPS Backend:** Using `https://localhost:5000` ensures encrypted connection between ngrok and your app
- **ngrok Free Plan:** Displays a browser warning page before accessing your app
- **Access Control:** Consider implementing additional authentication in your Flask app

## Getting Your Tunnel URL

After the service is running, you can get your public URL:

1. **Via Web Interface:** Visit `http://localhost:4040`
2. **Via API:**
   ```bash
   curl http://localhost:4040/api/tunnels | jq -r '.tunnels[0].public_url'
   ```
3. **From Logs:**
   ```cmd
   type logs\ngrok_output.log | findstr "https://"
   ```

## Additional Resources

- ngrok Documentation: https://ngrok.com/docs
- NSSM Documentation: https://nssm.cc/usage
- Your ngrok Dashboard: https://dashboard.ngrok.com/

## Support

If you encounter issues:

1. Check service status: `C:\nssm\nssm.exe status NgrokOPIc`
2. Review error logs: `logs\ngrok_error.log`
3. Test manually: `ngrok http https://localhost:5000 --region=ap --host-header=localhost:5000`
4. Verify main app is running: `curl -k https://localhost:5000`

