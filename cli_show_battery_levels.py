#!/usr/bin/env python3
"""CLI utility to show bluetooth battery levels in MacOS."""

import plistlib
import subprocess


def get_ioreg_data() -> list:
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
            name = f"Unknown Bluetooth Device (ProductID={pid})"
    return name


def show_battery_levels() -> None:
    devices = get_ioreg_data()

    for device in devices:
        name = get_device_name(device)
        battery_percent = device.get('BatteryPercent')

        # Skip entries that don't have a valid battery integer
        if battery_percent is None:
            continue

        print(f'{name}:\t{battery_percent}%')


def main() -> None:
    show_battery_levels()


if __name__ == "__main__":
    main()
