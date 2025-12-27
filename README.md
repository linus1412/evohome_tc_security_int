# EvoHome Total Connect Security Integration

This project provides both a standalone Python library and a Home Assistant custom component for controlling EvoHome Total Connect Security systems (European/International version).

## Features

- **Standalone Library**: Use the `evohome_security.py` module independently in your Python projects
- **Home Assistant Integration**: Native alarm control panel integration with secure credential storage
- **Alarm Control**: Monitor and control your alarm system (disarm, arm home, arm away)
- **Secure Configuration**: Credentials stored securely using Home Assistant's config flow
- **Status Monitoring**: Real-time alarm status updates

## Project Structure

```
evohome_tc_security_int/
├── evosec2.py                          # Core Total Connect client
├── evohome_security.py                 # Standalone library wrapper
├── run_evosec.py                       # CLI tool (legacy)
└── custom_components/
    └── evohome_security/               # Home Assistant integration
        ├── __init__.py
        ├── manifest.json
        ├── config_flow.py              # Secure credential configuration
        ├── alarm_control_panel.py      # Alarm entity implementation
        └── translations/
            └── en.json
```

## Installation

### Option 1: Home Assistant Custom Component (Recommended)

1. **Copy the integration to your Home Assistant**:
   ```bash
   cd /config  # Your Home Assistant config directory
   mkdir -p custom_components
   cp -r /path/to/repo/custom_components/evohome_security custom_components/
   ```

   Note: The integration includes all necessary files (evosec2.py and evohome_security.py) 
   within the component directory, so no additional file copying is needed.

2. **Restart Home Assistant**

3. **Add the integration**:
   - Go to Settings → Devices & Services
   - Click "+ ADD INTEGRATION"
   - Search for "EvoHome Security"
   - Enter your Total Connect username and password
   - The integration will validate your credentials and add the alarm control panel

### Option 2: Standalone Library

Use the library in your own Python scripts:

```python
from evohome_security import EvoHomeSecurityClient, AlarmState

# Create client
client = EvoHomeSecurityClient(
    username="your_username",
    password="your_password"
)

try:
    # Authenticate
    if client.authenticate():
        print("✓ Authentication successful")
        
        # Get status
        status = client.get_status()
        print(f"Current status: {status.value}")
        
        # Control the alarm (when implemented)
        # client.arm_away()
        # client.arm_home()
        # client.disarm()
        
        # Logout
        client.logout()
finally:
    client.close()
```

## Home Assistant Usage

Once configured, the integration adds an alarm control panel entity:

### In the UI
- View current alarm status in the dashboard
- Use the alarm panel card to control the alarm
- Arm/Disarm directly from the interface

### In Automations
```yaml
# Example: Disarm when arriving home
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

# Example: Arm away when leaving
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

## Security Considerations

### Credential Storage
- Credentials are stored securely using Home Assistant's encrypted config entry storage
- Passwords are never stored in plain text in configuration.yaml
- The config flow UI ensures credentials are entered securely

### Network Security
- All communication uses HTTPS to the Total Connect API
- Session tokens are managed automatically
- Proper logout ensures sessions are terminated

### Best Practices
1. Use strong, unique passwords for your Total Connect account
2. Enable two-factor authentication on your Total Connect account (if available)
3. Regularly review Home Assistant logs for unauthorized access attempts
4. Keep Home Assistant and the integration updated

## Architecture

### Library Layer (evohome_security.py)
The library provides a clean, Pythonic interface to the Total Connect API:
- Wraps `evosec2.py` for easier use
- Provides enum-based state management
- Handles authentication and session management
- Can be used independently of Home Assistant

### Home Assistant Integration Layer
Follows Home Assistant best practices:
- **Config Flow**: UI-based configuration with validation
- **Async/Await**: Non-blocking I/O operations
- **Entity Model**: Native AlarmControlPanelEntity implementation
- **State Management**: Proper state updates and polling
- **Error Handling**: Graceful degradation and error reporting

## Development

### Testing the Library
```bash
# Set credentials
export EVO_SECURITY_USERNAME="your_username"
export EVO_SECURITY_PASSWORD="your_password"

# Run the library test
python evohome_security.py
```

### Testing in Home Assistant
1. Copy files to your Home Assistant development environment
2. Restart Home Assistant
3. Add the integration through the UI
4. Check logs: `Settings → System → Logs`

## Known Limitations

1. **Control Functions Not Implemented**: The current `evosec2.py` only implements status checking. Control functions (arm/disarm) need to be added to the base client.
2. **Polling Only**: The integration polls for status updates every 30 seconds. Real-time updates would require webhook support from Total Connect.
3. **Single Panel**: Currently supports one security panel per account.

## Future Enhancements

- [ ] Implement arm/disarm commands in evosec2.py
- [ ] Add zone/sensor support
- [ ] Support multiple security panels
- [ ] Add event history
- [ ] Implement webhooks for real-time updates
- [ ] Add support for additional Total Connect features

## Troubleshooting

### Authentication Fails
- Verify your username and password are correct
- Check that your account is active on the Total Connect website
- Ensure your Home Assistant can reach https://tc20e.total-connect.eu

### Entity Not Updating
- Check the Home Assistant logs for errors
- Verify network connectivity
- Try removing and re-adding the integration

### Control Commands Don't Work
- Control functions (arm/disarm) are currently not implemented in evosec2.py
- Status monitoring works, but control requires additional implementation

## Contributing

Contributions are welcome! Areas that need work:
1. Implementing control commands in evosec2.py
2. Adding zone/sensor support
3. Improving error handling
4. Adding unit tests
5. Documentation improvements

## License

This project is provided as-is for integration with EvoHome Total Connect Security systems.

## Credits

Based on the original `evosec2.py` implementation by the repository owner.
