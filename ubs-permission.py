#!/usr/bin/env bash

RULE_FILE="/etc/udev/rules.d/99-custom_usb.rules"
DEVICE_NAME="Future Technology Devices"  # String to look for in lsusb output

print_usage() {
    echo "Usage:"
    echo "  $0 <VENDOR_ID> <PRODUCT_ID>"
    echo "     Add a udev rule for a device with the given Vendor and Product ID."
    echo ""
    echo "  $0 -a | --auto"
    echo "     Attempt to auto-detect a device whose lsusb line contains \"${DEVICE_NAME}\"."
    echo "     If one device is found, it will use that automatically."
    echo "     If multiple are found, it will prompt you to select one."
    echo ""
    echo "If you don't know the Vendor and Product ID, you can run:"
    echo "  lsusb"
    echo "to list connected USB devices. Find a line that includes \"${DEVICE_NAME}\""
    echo "and note the Vendor (VID) and Product (PID) portions of 'ID VVVV:PPPP'."
    echo ""
    echo "Example:"
    echo "  $0 0403 6001"
    echo "  $0 --auto"
}

auto_detect_device() {
    # Gather all devices matching the DEVICE_NAME string
    # Format of lsusb line: Bus XXX Device XXX: ID VVVV:PPPP Description
    local devices
    IFS=$'\n' devices=( $(lsusb | grep -i "$DEVICE_NAME") )
    unset IFS

    if [ ${#devices[@]} -eq 0 ]; then
        echo "No devices containing \"${DEVICE_NAME}\" found via lsusb."
        exit 1
    elif [ ${#devices[@]} -eq 1 ]; then
        # Single device found, extract VID and PID
        VID=$(echo "${devices[0]}" | awk '{print $6}' | cut -d':' -f1)
        PID=$(echo "${devices[0]}" | awk '{print $6}' | cut -d':' -f2)
    else
        echo "Multiple devices containing \"${DEVICE_NAME}\" found:"
        i=1
        for dev in "${devices[@]}"; do
            echo "[$i]: $dev"
            i=$((i+1))
        done

        # Prompt user to select a device
        echo -n "Select a device number (1-${#devices[@]}): "
        read choice

        if ! [[ "$choice" =~ ^[0-9]+$ ]] || [ "$choice" -lt 1 ] || [ "$choice" -gt ${#devices[@]} ]; then
            echo "Invalid selection."
            exit 1
        fi

        # Extract chosen device details
        chosen_dev="${devices[$((choice-1))]}"
        VID=$(echo "$chosen_dev" | awk '{print $6}' | cut -d':' -f1)
        PID=$(echo "$chosen_dev" | awk '{print $6}' | cut -d':' -f2)
    fi
}

# Main script logic
if [ $# -eq 0 ]; then
    print_usage
    exit 1
fi

if [ "$1" == "-a" ] || [ "$1" == "--auto" ]; then
    # Auto-detect mode
    auto_detect_device
else
    # Expecting two arguments: VENDOR_ID and PRODUCT_ID
    if [ $# -ne 2 ]; then
        print_usage
        exit 1
    fi
    VID="$1"
    PID="$2"
fi

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root or with sudo."
    exit 1
fi

# Add or append the rule
echo "Adding udev rule for device VID:$VID PID:$PID..."
echo "SUBSYSTEM==\"usb\", ATTR{idVendor}==\"$VID\", ATTR{idProduct}==\"$PID\", MODE=\"0666\"" >> "$RULE_FILE"

# Reload and trigger udev rules
echo "Reloading udev rules..."
udevadm control --reload-rules
udevadm trigger

echo "Udev rule added or updated successfully."
echo "Please re-plug the device if it's currently connected for changes to take effect."

