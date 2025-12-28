# HACS Installation Guide

This integration can be easily installed and managed through HACS (Home Assistant Community Store).

## Prerequisites

1. **HACS must be installed** in your Home Assistant instance
   - If you don't have HACS, follow the installation guide at https://hacs.xyz/docs/setup/download

2. **Total Connect Account** - European/International version
   - You need valid credentials for https://tc20e.total-connect.eu

## Installation Steps

### 1. Add Custom Repository to HACS

1. Open Home Assistant
2. Go to **HACS** (in the sidebar)
3. Click on **Integrations**
4. Click the **three dots menu** (⋮) in the top right corner
5. Select **Custom repositories**
6. In the dialog that appears:
   - **Repository**: `https://github.com/linus1412/evohome_tc_security_int`
   - **Category**: Select `Integration`
7. Click **Add**

### 2. Install the Integration

1. Still in HACS → Integrations
2. Click the **blue + button** in the bottom right corner
3. Search for **"EvoHome Total Connect Security"**
4. Click on the integration
5. Click **Download**
6. Select the latest version
7. Click **Download** again to confirm

### 3. Restart Home Assistant

After installation, you must restart Home Assistant:
1. Go to **Settings → System**
2. Click **Restart**
3. Confirm the restart
4. Wait for Home Assistant to come back online

### 4. Configure the Integration

1. Go to **Settings → Devices & Services**
2. Click **+ ADD INTEGRATION** (bottom right)
3. Search for **"EvoHome Security"**
4. Click on it to start configuration
5. Enter your credentials:
   - **Username**: Your Total Connect username
   - **Password**: Your Total Connect password
6. Click **Submit**

The integration will:
- Validate your credentials
- Connect to Total Connect
- Create the alarm control panel entity

### 5. Verify Installation

After configuration, you should see:
- A new device: **EvoHome Security System**
- An entity: `alarm_control_panel.evohome_security_system`

You can now:
- Add the alarm panel to your dashboard
- Create automations
- Control the alarm through the UI

## Updating

HACS will automatically notify you when updates are available:

1. Go to **HACS → Integrations**
2. Look for **EvoHome Total Connect Security** with an update badge
3. Click on it
4. Click **Update**
5. Restart Home Assistant after the update

## Troubleshooting

### Integration Not Found in HACS

If you can't find the integration after adding the custom repository:
1. Verify the repository URL is correct
2. Make sure you selected "Integration" as the category
3. Restart Home Assistant and check again
4. Clear your browser cache

### Installation Fails

If installation fails:
1. Check the HACS logs: **HACS → ... → Information → Download Log**
2. Ensure you have a stable internet connection
3. Try removing and re-adding the custom repository
4. Check GitHub for any known issues

### Configuration Fails

If configuration fails:
1. Verify your Total Connect credentials at https://tc20e.total-connect.eu
2. Check Home Assistant logs: **Settings → System → Logs**
3. Ensure Home Assistant can reach the Total Connect servers
4. Try removing and re-adding the integration

## Uninstalling

To uninstall the integration:

1. **Remove the Integration**:
   - Go to **Settings → Devices & Services**
   - Find **EvoHome Security System**
   - Click the three dots (⋮) → **Delete**

2. **Uninstall from HACS** (optional):
   - Go to **HACS → Integrations**
   - Find **EvoHome Total Connect Security**
   - Click the three dots (⋮) → **Uninstall**
   - Restart Home Assistant

## Support

- **Documentation**: [README.md](https://github.com/linus1412/evohome_tc_security_int/blob/main/README.md)
- **Quick Start**: [QUICKSTART.md](https://github.com/linus1412/evohome_tc_security_int/blob/main/QUICKSTART.md)
- **Issues**: [GitHub Issues](https://github.com/linus1412/evohome_tc_security_int/issues)

## Features

Once installed, you get:
- ✅ Real-time alarm status monitoring
- ✅ Full control (arm away, arm home, disarm)
- ✅ Native Home Assistant alarm panel
- ✅ Automation and script support
- ✅ Secure credential storage
- ✅ Easy updates through HACS
