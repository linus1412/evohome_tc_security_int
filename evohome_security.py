"""Library wrapper for EvoHome Total Connect Security System.

This module provides a clean interface to the TotalConnectClient from evosec2.py,
making it easier to use in both standalone scripts and Home Assistant integrations.
"""

import logging
from typing import Optional
from enum import Enum

from evosec2 import TotalConnectClient, ArmStatus


class AlarmState(Enum):
    """Alarm states compatible with Home Assistant."""
    DISARMED = "disarmed"
    ARMED_AWAY = "armed_away"
    ARMED_HOME = "armed_home"
    UNKNOWN = "unknown"


class EvoHomeSecurityClient:
    """Wrapper class for EvoHome security system operations."""

    def __init__(self, username: str, password: str, base_url: str = "https://tc20e.total-connect.eu"):
        """Initialize the EvoHome security client.

        Args:
            username: Total Connect username
            password: Total Connect password
            base_url: Base URL for Total Connect API
        """
        self.logger = logging.getLogger(__name__)
        self._client = TotalConnectClient(
            username=username,
            password=password,
            base_url=base_url,
            log_level=logging.INFO
        )
        self._authenticated = False

    def authenticate(self) -> bool:
        """Authenticate with the Total Connect system.

        Returns:
            bool: True if authentication successful, False otherwise
        """
        try:
            self._authenticated = self._client.authenticate()
            return self._authenticated
        except Exception as e:
            self.logger.error(f"Authentication failed: {e}")
            self._authenticated = False
            return False

    def get_status(self) -> AlarmState:
        """Get the current alarm state.

        Returns:
            AlarmState: Current state of the alarm system
        """
        try:
            status = self._client.get_status()
            if status is None:
                return AlarmState.UNKNOWN

            # Map TotalConnect status to Home Assistant alarm states
            if status == ArmStatus.DISARMED:
                return AlarmState.DISARMED
            elif status == ArmStatus.PARTIAL_ARM:
                return AlarmState.ARMED_HOME
            elif status == ArmStatus.TOTAL_ARM:
                return AlarmState.ARMED_AWAY
            else:
                return AlarmState.UNKNOWN

        except Exception as e:
            self.logger.error(f"Error getting status: {e}")
            return AlarmState.UNKNOWN

    def disarm(self) -> bool:
        """Disarm the alarm system.

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # The current evosec2.py only has get_status, not control methods
            # For now, return False and log that this feature needs implementation
            self.logger.warning("Disarm functionality not yet implemented in evosec2.py")
            return False
        except Exception as e:
            self.logger.error(f"Error disarming: {e}")
            return False

    def arm_away(self) -> bool:
        """Arm the alarm system in away mode (total arm).

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # The current evosec2.py only has get_status, not control methods
            # For now, return False and log that this feature needs implementation
            self.logger.warning("Arm away functionality not yet implemented in evosec2.py")
            return False
        except Exception as e:
            self.logger.error(f"Error arming away: {e}")
            return False

    def arm_home(self) -> bool:
        """Arm the alarm system in home mode (partial arm).

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # The current evosec2.py only has get_status, not control methods
            # For now, return False and log that this feature needs implementation
            self.logger.warning("Arm home functionality not yet implemented in evosec2.py")
            return False
        except Exception as e:
            self.logger.error(f"Error arming home: {e}")
            return False

    def logout(self) -> bool:
        """Logout from the Total Connect system.

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            result = self._client.logout()
            self._authenticated = False
            return result
        except Exception as e:
            self.logger.error(f"Error logging out: {e}")
            return False

    def close(self) -> None:
        """Close the client session."""
        try:
            self._client.close()
        except Exception as e:
            self.logger.error(f"Error closing client: {e}")

    @property
    def is_authenticated(self) -> bool:
        """Check if client is authenticated.

        Returns:
            bool: True if authenticated, False otherwise
        """
        return self._authenticated


# Example usage
if __name__ == "__main__":
    import os
    
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Get credentials from environment
    username = os.getenv("EVO_SECURITY_USERNAME")
    password = os.getenv("EVO_SECURITY_PASSWORD")
    
    if not username or not password:
        print("Please set EVO_SECURITY_USERNAME and EVO_SECURITY_PASSWORD environment variables")
        exit(1)
    
    # Create client
    client = EvoHomeSecurityClient(username, password)
    
    try:
        # Authenticate
        if client.authenticate():
            print("✓ Authentication successful")
            
            # Get status
            status = client.get_status()
            print(f"✓ Current status: {status.value}")
            
            # Logout
            if client.logout():
                print("✓ Logout successful")
        else:
            print("✗ Authentication failed")
    finally:
        client.close()
