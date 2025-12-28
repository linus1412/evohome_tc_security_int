# Integration Architecture

This document describes the architecture of the EvoHome Total Connect Security integration for Home Assistant.

## Overview

The integration follows a layered architecture that separates concerns and promotes reusability:

```
┌─────────────────────────────────────────────────────────┐
│           Home Assistant UI / Automations               │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│    Home Assistant Integration Layer                     │
│    (custom_components/evohome_security/)                │
│    ┌─────────────────────────────────────────────────┐  │
│    │ config_flow.py - Secure credential config      │  │
│    │ __init__.py - Component initialization         │  │
│    │ alarm_control_panel.py - Entity implementation │  │
│    └─────────────────────────────────────────────────┘  │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│    Library Wrapper Layer                                │
│    (evohome_security.py)                                │
│    ┌─────────────────────────────────────────────────┐  │
│    │ - EvoHomeSecurityClient                        │  │
│    │ - AlarmState enum (HA-compatible states)       │  │
│    │ - Clean, Pythonic interface                    │  │
│    │ - Can be used independently                    │  │
│    └─────────────────────────────────────────────────┘  │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│    Core Client Layer                                    │
│    (evosec2.py)                                         │
│    ┌─────────────────────────────────────────────────┐  │
│    │ - TotalConnectClient                           │  │
│    │ - HTTP session management                      │  │
│    │ - Authentication & API calls                   │  │
│    │ - ArmStatus enum (API states)                  │  │
│    └─────────────────────────────────────────────────┘  │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│    Total Connect API                                    │
│    (https://tc20e.total-connect.eu)                     │
└─────────────────────────────────────────────────────────┘
```

## Layer Descriptions

### 1. Core Client Layer (evosec2.py)

**Purpose**: Handle low-level HTTP communication with Total Connect API

**Responsibilities**:
- HTTP session management with proper headers and cookies
- Authentication flow (login/logout)
- API request/response handling
- Status retrieval
- Logging of HTTP traffic

**Key Classes**:
- `TotalConnectClient`: Main client for API communication
- `ArmStatus`: Enum for API-level status values (DISARMED, PARTIAL_ARM, TOTAL_ARM)
- `LoggingSession`: Custom requests.Session with logging

**Design Notes**:
- Uses requests library for HTTP
- Handles session tokens and cookies
- Implements the specific authentication flow required by Total Connect
- Currently only implements status retrieval (control commands not yet added)

### 2. Library Wrapper Layer (evohome_security.py)

**Purpose**: Provide a clean, Pythonic interface that can be used standalone

**Responsibilities**:
- Wrap evosec2.py with a simpler API
- Map API states to Home Assistant-compatible states
- Provide a consistent interface for both standalone and HA use
- Handle exceptions and provide clear error messages

**Key Classes**:
- `EvoHomeSecurityClient`: Main wrapper class
- `AlarmState`: Enum for HA-compatible states (DISARMED, ARMED_HOME, ARMED_AWAY, UNKNOWN)

**Design Notes**:
- Can be used independently without Home Assistant
- Maps PARTIAL_ARM → ARMED_HOME and TOTAL_ARM → ARMED_AWAY
- Uses NotImplementedError for unimplemented control functions
- Provides property for authentication status

**State Mapping**:
```python
ArmStatus.DISARMED → AlarmState.DISARMED
ArmStatus.PARTIAL_ARM → AlarmState.ARMED_HOME
ArmStatus.TOTAL_ARM → AlarmState.ARMED_AWAY
None → AlarmState.UNKNOWN
```

### 3. Home Assistant Integration Layer

**Purpose**: Integrate the library into Home Assistant following HA patterns

**Components**:

#### config_flow.py
- Implements config flow for UI-based setup
- Validates credentials before saving
- Uses HA's async executor for blocking I/O
- Stores credentials in encrypted config entries
- Prevents duplicate configurations

#### __init__.py
- Initializes the integration
- Creates the client instance
- Validates authentication on setup
- Manages component lifecycle (setup/unload)
- Stores client in hass.data for entity access

#### alarm_control_panel.py
- Implements AlarmControlPanelEntity
- Polls for status updates (30-second interval)
- Provides arm/disarm services
- Handles NotImplementedError gracefully
- Uses async/await patterns correctly
- Runs blocking I/O in executor

**Design Patterns**:
- **Config Entry**: All configuration via UI, no YAML
- **Entity Model**: Native AlarmControlPanelEntity
- **Async/Await**: Non-blocking operations
- **Executor Pattern**: Blocking I/O in thread pool
- **State Management**: Proper state updates
- **Error Handling**: Graceful degradation

### 4. Home Assistant UI / Automations

**Purpose**: User interface and automation capabilities

**Features**:
- Alarm control panel card in dashboard
- Status display
- Arm/disarm controls (UI disabled until implemented)
- Integration with automations
- Service calls for scripting

## Security Considerations

### Credential Storage
1. Credentials entered through UI config flow
2. Validated before storage
3. Stored in HA's encrypted config entries
4. Never stored in configuration.yaml
5. Never logged in plain text

### Network Security
1. All API communication over HTTPS
2. Session tokens managed securely
3. Proper logout to terminate sessions
4. No credential caching

### Error Handling
1. Authentication failures logged safely
2. Network errors handled gracefully
3. No sensitive data in error messages
4. Proper cleanup on failures

## Data Flow

### Authentication Flow
```
User Input → Config Flow → Validate Credentials → Create Entry
                ↓
        Create Client → Authenticate → Store Client
                ↓
        Setup Entities → Register Services
```

### Status Update Flow
```
Timer (30s) → Entity.async_update() → Run in Executor
                ↓
        Client.get_status() → API Request → Parse Response
                ↓
        Map State → Update Entity State → UI Update
```

### Control Flow (Future)
```
User Action → Service Call → Entity.async_alarm_arm_away()
                ↓
        Run in Executor → Client.arm_away() → API Request
                ↓
        Verify Success → Update Status → UI Update
```

## Extension Points

### Adding Control Commands

To implement arm/disarm functionality:

1. **In evosec2.py**:
   - Add methods: `arm_total()`, `arm_partial()`, `disarm(code)`
   - Implement API calls for each command
   - Handle API responses

2. **In evohome_security.py**:
   - Replace NotImplementedError with actual calls
   - Map to appropriate evosec2.py methods
   - Handle errors appropriately

3. **In alarm_control_panel.py**:
   - Remove NotImplementedError handling
   - Add code parameter support if needed
   - Update error messages

### Adding Zone/Sensor Support

To add individual zone monitoring:

1. Create new sensor entity type
2. Parse zone information from API
3. Create entities for each zone
4. Update status polling to include zones

### Adding Event History

To show alarm events:

1. Add event retrieval to evosec2.py
2. Create event sensor entities
3. Store recent events in entity state
4. Display in UI

## Testing Strategy

### Unit Tests
- Mock TotalConnectClient for library tests
- Test state mappings
- Test error handling
- Test NotImplementedError cases

### Integration Tests (Future)
- Test with mock API server
- Test config flow validation
- Test entity state updates
- Test service calls

### Manual Testing
- Test with real credentials
- Verify status updates
- Check error handling
- Verify UI display

## Dependencies

### Python Requirements
- `requests>=2.31.0`: HTTP library
- Home Assistant: `>=2023.1.0` (recommended)

### Home Assistant Components
- `alarm_control_panel`: Base entity class
- `config_entries`: Configuration flow
- Standard HA helpers

## Future Enhancements

1. **Real-time Updates**: Implement webhook support if API allows
2. **Multiple Panels**: Support for multiple security panels
3. **Zone Support**: Individual zone monitoring
4. **Event History**: Show alarm events and history
5. **Diagnostics**: Add diagnostic sensors (signal strength, battery, etc.)
6. **Options Flow**: Allow changing poll interval, etc.

## Maintenance

### Updating the Integration

When making changes:

1. Update version in manifest.json
2. Update changelog
3. Test thoroughly
4. Update documentation
5. Consider backward compatibility

### Debugging

Enable debug logging in configuration.yaml:
```yaml
logger:
  default: info
  logs:
    custom_components.evohome_security: debug
    evohome_security: debug
    evosec2: debug
```

Check logs at: Settings → System → Logs

## References

- [Home Assistant Developer Docs](https://developers.home-assistant.io/)
- [Alarm Control Panel Entity](https://developers.home-assistant.io/docs/core/entity/alarm-control-panel)
- [Config Flow](https://developers.home-assistant.io/docs/config_entries_config_flow_handler)
- Total Connect API: https://tc20e.total-connect.eu
