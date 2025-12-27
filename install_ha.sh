#!/bin/bash
# Installation script for EvoHome Security Home Assistant Integration
#
# This script helps you install the EvoHome Security integration into your
# Home Assistant installation.
#
# Usage:
#   ./install_ha.sh /path/to/homeassistant/config

set -e

# Check if config directory is provided
if [ -z "$1" ]; then
    echo "Usage: $0 <path-to-home-assistant-config>"
    echo "Example: $0 /config"
    echo "         $0 ~/.homeassistant"
    exit 1
fi

HA_CONFIG_DIR="$1"

# Verify the directory exists
if [ ! -d "$HA_CONFIG_DIR" ]; then
    echo "Error: Directory $HA_CONFIG_DIR does not exist"
    exit 1
fi

# Create custom_components directory if it doesn't exist
CUSTOM_COMPONENTS_DIR="$HA_CONFIG_DIR/custom_components"
mkdir -p "$CUSTOM_COMPONENTS_DIR"

# Create the integration directory
INTEGRATION_DIR="$CUSTOM_COMPONENTS_DIR/evohome_security"
mkdir -p "$INTEGRATION_DIR"
mkdir -p "$INTEGRATION_DIR/translations"

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "Installing EvoHome Security integration..."

# Copy integration files
echo "Copying integration files..."
cp "$SCRIPT_DIR/custom_components/evohome_security/__init__.py" "$INTEGRATION_DIR/"
cp "$SCRIPT_DIR/custom_components/evohome_security/manifest.json" "$INTEGRATION_DIR/"
cp "$SCRIPT_DIR/custom_components/evohome_security/config_flow.py" "$INTEGRATION_DIR/"
cp "$SCRIPT_DIR/custom_components/evohome_security/alarm_control_panel.py" "$INTEGRATION_DIR/"
cp "$SCRIPT_DIR/custom_components/evohome_security/services.yaml" "$INTEGRATION_DIR/"
cp "$SCRIPT_DIR/custom_components/evohome_security/translations/en.json" "$INTEGRATION_DIR/translations/"

# Copy library files
echo "Copying library files..."
cp "$SCRIPT_DIR/evosec2.py" "$INTEGRATION_DIR/"
cp "$SCRIPT_DIR/evohome_security.py" "$INTEGRATION_DIR/"

echo ""
echo "✓ Installation complete!"
echo ""
echo "Next steps:"
echo "1. Restart Home Assistant"
echo "2. Go to Settings → Devices & Services"
echo "3. Click '+ ADD INTEGRATION'"
echo "4. Search for 'EvoHome Security'"
echo "5. Enter your Total Connect credentials"
echo ""
echo "Installation location: $INTEGRATION_DIR"
