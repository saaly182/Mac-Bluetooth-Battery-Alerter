# Mac Bluetooth Battery Alerter

A state-aware background utility designed to be executed periodically via a macOS launchd LaunchAgent. It monitors the battery levels of connected Bluetooth peripherals and displays a native modal alert when a device's battery drops below 15%. This is especially useful for wireless keyboards and mice.

## Features and Architecture

* Uses `ioreg` to extract system hardware registry data as an XML Property List.
* Parses the XML natively using Python's `plistlib`.
* Utilizes `osascript` to trigger native blocking modal alerts in the GUI.
* Maintains state by writing temporary flag files to `/tmp/`.
* Ensures that a user is only alerted once per device per low-battery cycle, preventing alert spam on subsequent launchd executions.
* Flag files are automatically cleared when the device is charged or when the system reboots.
* The LaunchAgent evaluates the battery conditions every hour.

## Dependencies

* Python 3.x
* macOS (requires native `ioreg` and `osascript` utilities)

## Deployment and Installation

This utility is designed to run as a Global LaunchAgent. 

### 1. Install the `bluetooth_battery_check.py` script
Move the Python script to the execution directory defined in the `.plist`:
`/usr/local/bin/bluetooth_battery_check.py`

### 2. Install the `.plist` LaunchAgent
Move the `.plist` file to the global LaunchAgents directory:
`/Library/LaunchAgents/com.local.bluetoothbattery.plist`

### 3. Apply Permissions
The script and its accompanying `.plist` file must be deployed with appropriate file ownership and permissions to function across multiple user sessions. Open `Terminal` and run:

```bash
sudo chown root:wheel /Library/LaunchAgents/com.local.bluetoothbattery.plist
sudo chown root:wheel /usr/local/bin/bluetooth_battery_check.py
sudo chmod +x /usr/local/bin/bluetooth_battery_check.py
```

### 4. Load the LaunchAgent
Load the `.plist` file into the system background manager so it runs automatically:

```bash
sudo launchctl bootstrap system /Library/LaunchAgents/com.local.bluetoothbattery.plist
```

Verify that it loaded with:

```bash
launchctl list | grep bluetoothbattery
```
