#!/usr/bin/env python3

"""
macOS Bluetooth Battery Monitor

A state-aware background utility designed to be executed periodically via a 
macOS launchd LaunchAgent. It monitors the battery levels of connected 
Bluetooth peripherals and displays a native modal alert when a device's 
battery drops below a defined threshold.

Architecture & State Management:
- Uses `ioreg` to extract system hardware registry data as an XML Property List.
- Parses the XML natively using Python's `plistlib`.
- Utilizes `osascript` to trigger native blocking modal alerts in the GUI.
- Maintains state by writing temporary flag files to `/tmp/`. This ensures 
  that a user is only alerted once per device per low-battery cycle, preventing 
  alert spam on subsequent launchd executions. Flag files are automatically 
  cleared when the device is charged or when the system reboots.

Deployment:
Designed to run as a Global LaunchAgent. The script and its accompanying 
.plist file must be deployed with appropriate root:wheel permissions in 
/Library/LaunchAgents/ to function across multiple user sessions.

Dependencies:
- Python 3.x
- macOS (requires native `ioreg` and `osascript` utilities)
"""

import getpass
import os
import plistlib
import subprocess

THRESHOLD: int = 15


def get_battery_data() -> list:
    """Fetches and parses ioreg battery data into a Python dictionary."""
    try:
        # Fetch the ioreg data formatted as XML
        result = subprocess.run(
            ['ioreg', '-a', '-r', '-l', '-k', 'BatteryPercent'],
            capture_output=True,
            check=True
        )
        return plistlib.loads(result.stdout)
    except (subprocess.CalledProcessError, plistlib.InvalidFileException):
        return []


def get_device_name(device: dict) -> str:
    name = device.get('Product')
    if not name:
        # Try based on ProductID. (Note that macOS system python does not have
        # match-case feature yet.)
        pid = device.get('ProductID')
        if pid == 617:
            name = "Magic Mouse"
        elif pid == 666:
            name = "Magic Keyboard"
        else:
            name = "Unknown Bluetooth Device"
    return name


def check_batteries() -> None:
    """Evaluates battery levels and triggers alerts if necessary."""
    devices = get_battery_data()
    current_user = getpass.getuser()

    subprocess.run(['logger', '[BluetoothBatteryCheck] check executed for '
                    f'user: {current_user}'])

    for device in devices:
        name = get_device_name(device)
        battery = device.get('BatteryPercent')

        # Skip entries that don't have a valid battery integer
        if battery is None:
            continue

        # Create a safe string for the flag filename
        safe_name = name.replace(' ', '_').replace("’", '_')
        flag_file = f"/tmp/.low_battery_{safe_name}_{current_user}.flag"

        if battery < THRESHOLD:
            # Trigger alert only if the flag file does not exist
            if not os.path.exists(flag_file):
                # Halts execution until the user clicks "OK"
                script = (f'display alert "Low Battery Alert" message '
                          f'"{name} is at {battery}%"')
                subprocess.run(['osascript', '-e', script],
                               stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL)
                
                # Create the flag file so it doesn't alert again for this device
                with open(flag_file, 'w') as f:
                    f.write('Alert triggered.\n')
        else:
            # Battery is above threshold; clean up the flag if it exists
            if os.path.exists(flag_file):
                os.remove(flag_file)


def main() -> None:
    check_batteries()


if __name__ == "__main__":
    main()
