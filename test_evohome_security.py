"""Basic tests for evohome_security library.

Note: These tests verify the library structure and basic functionality
without requiring actual credentials or network access.
"""

import unittest
from unittest.mock import Mock, patch
from evohome_security import EvoHomeSecurityClient, AlarmState
from evosec2 import ArmStatus


class TestEvoHomeSecurityClient(unittest.TestCase):
    """Test cases for EvoHomeSecurityClient."""

    def setUp(self):
        """Set up test fixtures."""
        self.username = "test_user"
        self.password = "test_pass"
        
    @patch('evohome_security.TotalConnectClient')
    def test_client_initialization(self, mock_client_class):
        """Test client initialization."""
        client = EvoHomeSecurityClient(self.username, self.password)
        
        # Verify TotalConnectClient was initialized with correct parameters
        mock_client_class.assert_called_once()
        args, kwargs = mock_client_class.call_args
        self.assertEqual(kwargs['username'], self.username)
        self.assertEqual(kwargs['password'], self.password)
        
    @patch('evohome_security.TotalConnectClient')
    def test_authenticate_success(self, mock_client_class):
        """Test successful authentication."""
        mock_client = Mock()
        mock_client.authenticate.return_value = True
        mock_client_class.return_value = mock_client
        
        client = EvoHomeSecurityClient(self.username, self.password)
        result = client.authenticate()
        
        self.assertTrue(result)
        self.assertTrue(client.is_authenticated)
        mock_client.authenticate.assert_called_once()
        
    @patch('evohome_security.TotalConnectClient')
    def test_authenticate_failure(self, mock_client_class):
        """Test failed authentication."""
        mock_client = Mock()
        mock_client.authenticate.return_value = False
        mock_client_class.return_value = mock_client
        
        client = EvoHomeSecurityClient(self.username, self.password)
        result = client.authenticate()
        
        self.assertFalse(result)
        self.assertFalse(client.is_authenticated)
        
    @patch('evohome_security.TotalConnectClient')
    def test_get_status_mapping(self, mock_client_class):
        """Test status mapping from TotalConnect to AlarmState."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        client = EvoHomeSecurityClient(self.username, self.password)
        
        # Test DISARMED mapping
        mock_client.get_status.return_value = ArmStatus.DISARMED
        self.assertEqual(client.get_status(), AlarmState.DISARMED)
        
        # Test PARTIAL_ARM mapping
        mock_client.get_status.return_value = ArmStatus.PARTIAL_ARM
        self.assertEqual(client.get_status(), AlarmState.ARMED_HOME)
        
        # Test TOTAL_ARM mapping
        mock_client.get_status.return_value = ArmStatus.TOTAL_ARM
        self.assertEqual(client.get_status(), AlarmState.ARMED_AWAY)
        
        # Test None mapping
        mock_client.get_status.return_value = None
        self.assertEqual(client.get_status(), AlarmState.UNKNOWN)
        
    @patch('evohome_security.TotalConnectClient')
    def test_disarm_not_implemented(self, mock_client_class):
        """Test that disarm raises NotImplementedError."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        client = EvoHomeSecurityClient(self.username, self.password)
        
        with self.assertRaises(NotImplementedError) as context:
            client.disarm()
        
        self.assertIn("not yet implemented", str(context.exception).lower())
        
    @patch('evohome_security.TotalConnectClient')
    def test_arm_away_not_implemented(self, mock_client_class):
        """Test that arm_away raises NotImplementedError."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        client = EvoHomeSecurityClient(self.username, self.password)
        
        with self.assertRaises(NotImplementedError) as context:
            client.arm_away()
        
        self.assertIn("not yet implemented", str(context.exception).lower())
        
    @patch('evohome_security.TotalConnectClient')
    def test_arm_home_not_implemented(self, mock_client_class):
        """Test that arm_home raises NotImplementedError."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        client = EvoHomeSecurityClient(self.username, self.password)
        
        with self.assertRaises(NotImplementedError) as context:
            client.arm_home()
        
        self.assertIn("not yet implemented", str(context.exception).lower())
        
    @patch('evohome_security.TotalConnectClient')
    def test_logout(self, mock_client_class):
        """Test logout functionality."""
        mock_client = Mock()
        mock_client.logout.return_value = True
        mock_client_class.return_value = mock_client
        
        client = EvoHomeSecurityClient(self.username, self.password)
        client._authenticated = True
        
        result = client.logout()
        
        self.assertTrue(result)
        self.assertFalse(client.is_authenticated)
        mock_client.logout.assert_called_once()
        
    @patch('evohome_security.TotalConnectClient')
    def test_close(self, mock_client_class):
        """Test close functionality."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        client = EvoHomeSecurityClient(self.username, self.password)
        client.close()
        
        mock_client.close.assert_called_once()


if __name__ == '__main__':
    unittest.main()
