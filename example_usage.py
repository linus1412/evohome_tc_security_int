#!/usr/bin/env python3
"""Example script demonstrating the EvoHome Security library usage.

This script shows how to use the evohome_security library to interact
with the EvoHome Total Connect Security system.

Usage:
    python3 example_usage.py

Requirements:
    Set EVO_SECURITY_USERNAME and EVO_SECURITY_PASSWORD environment variables
    or create a .env file with these values.
"""

import os
import sys
import logging
from evohome_security import EvoHomeSecurityClient, AlarmState


def main():
    """Main function demonstrating library usage."""
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    # Get credentials from environment
    username = os.getenv("EVO_SECURITY_USERNAME")
    password = os.getenv("EVO_SECURITY_PASSWORD")
    
    if not username or not password:
        logger.error("Please set EVO_SECURITY_USERNAME and EVO_SECURITY_PASSWORD environment variables")
        logger.info("Example:")
        logger.info("  export EVO_SECURITY_USERNAME='your_username'")
        logger.info("  export EVO_SECURITY_PASSWORD='your_password'")
        sys.exit(1)
    
    # Create client
    logger.info("Creating EvoHome Security client...")
    client = EvoHomeSecurityClient(username, password)
    
    try:
        # Authenticate
        logger.info("Authenticating with Total Connect...")
        if client.authenticate():
            logger.info("✓ Authentication successful")
            
            # Get status
            logger.info("Getting current alarm status...")
            status = client.get_status()
            logger.info(f"✓ Current status: {status.value}")
            
            # Show status in a user-friendly way
            if status == AlarmState.DISARMED:
                print("\n🟢 The alarm system is currently DISARMED")
            elif status == AlarmState.ARMED_HOME:
                print("\n🟡 The alarm system is currently ARMED (HOME)")
            elif status == AlarmState.ARMED_AWAY:
                print("\n🔴 The alarm system is currently ARMED (AWAY)")
            else:
                print("\n⚪ The alarm system status is UNKNOWN")
            
            # Demonstrate control functions (currently not implemented)
            print("\n--- Control Functions ---")
            print("Note: Control functions are not yet implemented in evosec2.py")
            print("Attempting to call them will raise NotImplementedError")
            
            try:
                client.disarm()
            except NotImplementedError as e:
                logger.info(f"Expected: {e}")
            
            try:
                client.arm_home()
            except NotImplementedError as e:
                logger.info(f"Expected: {e}")
            
            try:
                client.arm_away()
            except NotImplementedError as e:
                logger.info(f"Expected: {e}")
            
            # Logout
            logger.info("Logging out...")
            if client.logout():
                logger.info("✓ Logout successful")
            else:
                logger.warning("Logout may have failed")
                
        else:
            logger.error("✗ Authentication failed")
            logger.error("Please check your credentials and try again")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("\nInterrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        sys.exit(1)
    finally:
        # Always close the client
        logger.info("Closing client...")
        client.close()
        logger.info("Done!")


if __name__ == "__main__":
    main()
