# EvoHome Total Connect Security

Control your EvoHome Total Connect Security system (European/International version) through Home Assistant.

## Features

- **Full Alarm Control**: Arm away, arm home, and disarm your security system
- **Real-time Status**: Monitor alarm status with 30-second polling
- **Native Integration**: Standard Home Assistant alarm control panel entity
- **Secure Configuration**: UI-based setup with encrypted credential storage
- **Automation Ready**: Integrate with Home Assistant automations and scripts

## Installation via HACS

1. Add this repository as a custom repository in HACS
2. Search for "EvoHome Total Connect Security"
3. Click Download
4. Restart Home Assistant
5. Go to Settings → Devices & Services → Add Integration
6. Search for "EvoHome Security" and configure with your credentials

## Usage

Once configured, the integration creates an alarm control panel entity:
- `alarm_control_panel.evohome_security_system`

Use it in:
- **Dashboard**: Add an alarm panel card
- **Automations**: Arm/disarm based on presence, time, etc.
- **Scripts**: Control via service calls

### Example Automation

```yaml
automation:
  # Disarm when arriving home
  - trigger:
      platform: zone
      entity_id: person.john
      zone: zone.home
      event: enter
    action:
      service: alarm_control_panel.alarm_disarm
      target:
        entity_id: alarm_control_panel.evohome_security_system
      data:
        code: "1234"  # Optional

  # Arm away when leaving
  - trigger:
      platform: zone
      entity_id: person.john
      zone: zone.home
      event: leave
    action:
      service: alarm_control_panel.alarm_arm_away
      target:
        entity_id: alarm_control_panel.evohome_security_system
```

## Support

- [Documentation](https://github.com/linus1412/evohome_tc_security_int/blob/main/README.md)
- [Issue Tracker](https://github.com/linus1412/evohome_tc_security_int/issues)
- [Quick Start Guide](https://github.com/linus1412/evohome_tc_security_int/blob/main/QUICKSTART.md)

## Requirements

- Total Connect Security account (European/International version)
- Home Assistant 2023.1.0 or later
