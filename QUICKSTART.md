# Quick Start Guide

Get up and running with the EvoHome Security integration in minutes!

## For Home Assistant Users

### 1. Install the Integration

Use the provided installation script:

```bash
# Clone or download the repository
cd /path/to/evohome_tc_security_int

# Run the installation script
./install_ha.sh /config  # Replace with your HA config directory
```

Or manually copy files:

```bash
# Copy the integration to your Home Assistant
cp -r custom_components/evohome_security /config/custom_components/
```

### 2. Restart Home Assistant

Restart Home Assistant to load the new integration:
- Go to Settings → System → Restart
- Or run: `ha core restart` (if using HA OS)

### 3. Add the Integration

1. Go to **Settings → Devices & Services**
2. Click **+ ADD INTEGRATION** (bottom right)
3. Search for **"EvoHome Security"**
4. Click on it to start setup

### 4. Enter Your Credentials

Enter your Total Connect credentials:
- **Username**: Your Total Connect username
- **Password**: Your Total Connect password

Click **Submit** - the integration will validate your credentials.

### 5. Done! 

Your alarm panel is now available:
- Entity: `alarm_control_panel.evohome_security_system`
- Status updates every 30 seconds

## For Python Developers

### 1. Install Dependencies

```bash
pip install requests
```

### 2. Set Credentials

```bash
export EVO_SECURITY_USERNAME="your_username"
export EVO_SECURITY_PASSWORD="your_password"
```

### 3. Run Example

```python
from evohome_security import EvoHomeSecurityClient, AlarmState

# Create and authenticate
client = EvoHomeSecurityClient(username, password)
if client.authenticate():
    # Get status
    status = client.get_status()
    print(f"Alarm status: {status.value}")
    
    # Logout
    client.logout()
    
client.close()
```

Or run the example script:

```bash
python3 example_usage.py
```

## Using in Home Assistant

### Dashboard Card

Add an alarm panel card to your dashboard:

1. Edit dashboard
2. Add card → Alarm Panel
3. Select entity: `alarm_control_panel.evohome_security_system`

### Automations

#### Disarm when arriving home

```yaml
automation:
  - alias: "Disarm when home"
    trigger:
      - platform: zone
        entity_id: person.john
        zone: zone.home
        event: enter
    action:
      - service: alarm_control_panel.alarm_disarm
        target:
          entity_id: alarm_control_panel.evohome_security_system
```

#### Arm when leaving

```yaml
automation:
  - alias: "Arm when leaving"
    trigger:
      - platform: zone
        entity_id: person.john
        zone: zone.home
        event: leave
    action:
      - service: alarm_control_panel.alarm_arm_away
        target:
          entity_id: alarm_control_panel.evohome_security_system
```

#### Notify on status change

```yaml
automation:
  - alias: "Alarm status changed"
    trigger:
      - platform: state
        entity_id: alarm_control_panel.evohome_security_system
    action:
      - service: notify.mobile_app_phone
        data:
          message: "Alarm is now {{ states('alarm_control_panel.evohome_security_system') }}"
```

### Scripts

Create scripts for common actions:

```yaml
script:
  arm_alarm_away:
    alias: "Arm Alarm (Away)"
    sequence:
      - service: alarm_control_panel.alarm_arm_away
        target:
          entity_id: alarm_control_panel.evohome_security_system

  arm_alarm_home:
    alias: "Arm Alarm (Home)"
    sequence:
      - service: alarm_control_panel.alarm_arm_home
        target:
          entity_id: alarm_control_panel.evohome_security_system

  disarm_alarm:
    alias: "Disarm Alarm"
    sequence:
      - service: alarm_control_panel.alarm_disarm
        target:
          entity_id: alarm_control_panel.evohome_security_system
```

## Troubleshooting

### Authentication Fails

**Problem**: "Invalid username or password" error

**Solutions**:
1. Verify credentials at https://tc20e.total-connect.eu
2. Check for typos in username/password
3. Ensure account is active

### Entity Not Showing

**Problem**: Can't find the alarm entity

**Solutions**:
1. Check Home Assistant logs: Settings → System → Logs
2. Verify integration is loaded: Settings → Devices & Services
3. Restart Home Assistant
4. Try removing and re-adding the integration

### Status Not Updating

**Problem**: Status shows as unavailable or doesn't update

**Solutions**:
1. Check logs for errors
2. Verify network connectivity to Total Connect
3. Check if credentials are still valid
4. Wait 30 seconds (polling interval)

### Control Commands Don't Work

**Problem**: Can't arm/disarm the alarm

**Solutions**:
1. Check the Home Assistant logs for specific error messages
2. Verify your Total Connect account has permission to control the alarm
3. Ensure you're using the correct disarm code if required
4. Verify the system is not in a transitional state (e.g., already arming)
5. Check network connectivity to Total Connect

## Getting Help

### Enable Debug Logging

Add to `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    custom_components.evohome_security: debug
    evohome_security: debug
```

Then restart Home Assistant and check the logs.

### Check Logs

Go to Settings → System → Logs and look for errors related to:
- `custom_components.evohome_security`
- Authentication failures
- Network errors

### Community Support

- Open an issue on GitHub
- Check existing issues for solutions
- Include relevant log entries (remove passwords!)

## Next Steps

### Current Features
- ✅ View alarm status in real-time
- ✅ Arm/disarm the alarm via HA UI or automations
- ✅ Integration with Home Assistant dashboard
- ✅ Secure credential storage
- ✅ Status monitoring every 30 seconds
- ✅ Full control of alarm system

### Future Features
- ⏳ Individual zone monitoring
- ⏳ Event history
- ⏳ Real-time push notifications

### Contributing

Want to help add features? Check out:
- `ARCHITECTURE.md` - Understand the design
- `README.md` - Full documentation
- GitHub issues - See what needs work

## Reference

- **Repository**: https://github.com/linus1412/evohome_tc_security_int
- **Total Connect**: https://tc20e.total-connect.eu
- **Home Assistant Docs**: https://www.home-assistant.io/integrations/alarm_control_panel/

---

**Need more help?** Check the full README.md or open an issue on GitHub!
