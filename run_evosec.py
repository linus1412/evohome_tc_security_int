import argparse
import os
import sys
import logging
from enum import Enum
import requests
from typing import Optional
from dataclasses import dataclass

# Import from evosec.py
from evosec import SecurityConfig, SecuritySystem

# Simple function to load environment variables from .env file
def load_dotenv(dotenv_path='.env'):
    # Set up a basic logger for this function
    logger = logging.getLogger("evosec_dotenv")

    try:
        with open(dotenv_path) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#') or '=' not in line:
                    continue
                key, value = line.split('=', 1)
                os.environ[key] = value
    except Exception as e:
        logger.warning(f"Could not load .env file: {e}")

# [Previous SecuritySystem class code remains the same...]
# [Copy all the previous code here]

def create_parser():
    parser = argparse.ArgumentParser(description='Control Security System')

    # Add arguments for credentials
    parser.add_argument('--username', '-u',
                        help='Username for login (or use EVO_SECURITY_USERNAME env var)')
    parser.add_argument('--password', '-p',
                        help='Password for login (or use EVO_SECURITY_PASSWORD env var)')

    # Add argument for log level
    parser.add_argument('--log-level', '-l',
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        default='INFO',
                        help='Set the logging level (default: INFO)')

    # Add command subparsers
    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Status command
    subparsers.add_parser('status', help='Get current system status')

    # Arm commands
    subparsers.add_parser('disarm', help='Disarm the system')
    subparsers.add_parser('partial', help='Partially arm the system')
    subparsers.add_parser('total', help='Totally arm the system')

    return parser

def main():
    # Load environment variables from .env file
    load_dotenv()

    parser = create_parser()
    args = parser.parse_args()

    # Set up logging
    log_level = getattr(logging, args.log_level)
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger("evosec_cli")

    # Get credentials from args or environment
    username = args.username or os.environ.get('EVO_SECURITY_USERNAME')
    password = args.password or os.environ.get('EVO_SECURITY_PASSWORD')

    if not username or not password:
        logger.error("Username and password must be provided via arguments or environment variables")
        sys.exit(1)

    # Debug: Print masked credentials to verify they're loaded correctly
    masked_password = password[:2] + '*' * (len(password) - 4) + password[-2:] if password else None
    logger.debug(f"Using username: {username}")
    logger.debug(f"Using password: {masked_password}")

    # Initialize security system
    config = SecurityConfig(username=username, password=password, log_level=log_level)
    system = SecuritySystem(config)

    try:
        if args.command == 'status':
            status = system.get_status()
            logger.info(f"Current system status: {status.value if status else 'Unknown'}")

        elif args.command == 'disarm':
            if system.disarm():
                logger.info("System successfully disarmed")
            else:
                logger.error("Failed to disarm system")
                sys.exit(1)

        elif args.command == 'partial':
            if system.partial_arm():
                logger.info("System successfully set to partial arm")
            else:
                logger.error("Failed to set partial arm")
                sys.exit(1)

        elif args.command == 'total':
            if system.total_arm():
                logger.info("System successfully set to total arm")
            else:
                logger.error("Failed to set total arm")
                sys.exit(1)

        else:
            parser.print_help()
            sys.exit(1)

    except Exception as e:
        logger.error(f"Error: {str(e)}")
        sys.exit(1)
    finally:
        system.close()

if __name__ == "__main__":
    main()
