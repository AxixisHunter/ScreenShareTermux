#!/usr/bin/python

import os
import sys
import time
import subprocess
import requests
import shutil
from os import get_terminal_size

version = "1.0.0"

# ANSI color codes for terminal output
RESET = "\033[0m"
GREEN = "\033[1;32m"
RED = "\033[1;31m"
BLUE = "\033[1;34m"
CYAN = "\033[1;36m"
YELLOW = "\033[1;33m"
GRAY = "\033[1;30m"

def print_header():
    """Print the tool header with version information"""
    os.system("clear")
    terminal_width = get_terminal_size().columns
    ver = f"ScreenShare {version}"
    b = '━' * (len(ver) + 4)
    p = ' ' * ((terminal_width - len(b)) // 2)
    header = f"\n{p}┏{b}┓\n{p}┃  {ver}  ┃\n{p}┗{b}┛"
    print(f"{header} ━ {GREEN}share your screen via OTG{RESET}")

def check_dependencies():
    """Check if required dependencies are installed"""
    dependencies = ["adb", "scrcpy"]
    missing = []
    
    for dep in dependencies:
        if subprocess.run(f"which {dep}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).returncode != 0:
            missing.append(dep)
    
    if missing:
        print(f"\n{RED}Missing dependencies: {', '.join(missing)}{RESET}")
        print(f"\nPlease install them using:")
        print(f"\n{GREEN}pkg install {' '.join(missing)}{RESET}\n")
        return False
    return True

def check_storage_permission():
    """Check if storage permission is granted"""
    if not os.path.isdir(os.path.expanduser('~/storage')):
        print(f"\n{RED}Storage permission not granted!{RESET}")
        print(f"\nPlease grant permission via command:")
        print(f"{GREEN}termux-setup-storage{RESET}")
        print(f"\nThen restart the tool\n")
        return False
    return True

def check_adb_connection():
    """Check ADB connection and verify device is connected"""
    spinner = "|/-\\"
    print(f"\n{BLUE}Checking device connection...{RESET}")
    
    for _ in range(20):  # Try for ~5 seconds
        for char in spinner:
            sys.stdout.write(f"\r{YELLOW}Searching for device {char}{RESET}")
            sys.stdout.flush()
            
            result = subprocess.run(["adb", "devices"], capture_output=True, text=True)
            devices = result.stdout.strip().split('\n')[1:]
            connected_devices = [d for d in devices if '\tdevice' in d]
            
            if connected_devices:
                sys.stdout.write('\r\033[K')
                device_name = get_device_name(connected_devices[0].split('\t')[0])
                print(f"\n{GREEN}✓ Device connected: {device_name}{RESET}\n")
                return True
                
            time.sleep(0.25)
    
    print(f"\n{RED}No devices found!{RESET}")
    print(f"\nPlease ensure:")
    print(f"1. USB debugging is enabled on the target device")
    print(f"2. The device is connected via OTG")
    print(f"3. You've authorized USB debugging on the device\n")
    return False

def get_device_name(device_id):
    """Get the device model name"""
    try:
        result = subprocess.run(
            ["adb", "-s", device_id, "shell", "getprop", "ro.product.model"], 
            capture_output=True, 
            text=True
        )
        name = result.stdout.strip()
        if name:
            return name
        return device_id
    except:
        return device_id

def start_screen_sharing(options=None):
    """Start screen sharing with scrcpy"""
    if options is None:
        options = {}
    
    cmd = ["scrcpy"]
    
    # Add options based on user preferences
    if options.get("bitrate"):
        cmd.extend(["--bit-rate", str(options["bitrate"])])
    if options.get("max_size"):
        cmd.extend(["--max-size", str(options["max_size"])])
    if options.get("no_audio", False):
        cmd.append("--no-audio")
    if options.get("stay_awake", True):
        cmd.append("--stay-awake")
    if options.get("turn_screen_off", False):
        cmd.append("--turn-screen-off")
    
    print(f"\n{BLUE}Starting screen sharing...{RESET}")
    print(f"{GRAY}(Press Ctrl+C to stop){RESET}\n")
    
    try:
        subprocess.run(cmd)
        print(f"\n{GREEN}Screen sharing ended{RESET}\n")
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Screen sharing stopped by user{RESET}\n")
    except Exception as e:
        print(f"\n{RED}Error during screen sharing: {str(e)}{RESET}\n")

def get_sharing_options():
    """Get user preferences for screen sharing"""
    options = {
        "bitrate": 8000000,  # Default: 8 Mbps
        "max_size": 0,       # Default: no limit
        "no_audio": False,   # Default: with audio
        "stay_awake": True,  # Default: stay awake
        "turn_screen_off": False  # Default: keep screen on
    }
    
    print(f"\n{CYAN}Screen Sharing Options:{RESET}")
    print(f"\n1. Bitrate: {options['bitrate'] // 1000000} Mbps")
    print(f"2. Max screen size: {'No limit' if options['max_size'] == 0 else options['max_size']}")
    print(f"3. Audio: {'Disabled' if options['no_audio'] else 'Enabled'}")
    print(f"4. Stay awake: {'Yes' if options['stay_awake'] else 'No'}")
    print(f"5. Turn screen off: {'Yes' if options['turn_screen_off'] else 'No'}")
    print(f"6. Start with default settings")
    print(f"7. Advanced options")
    
    while True:
        choice = input(f"\nEnter your {GREEN}choice{RESET} (or press Enter for default): ")
        
        if not choice:
            return options
        
        if choice == "1":
            try:
                bitrate = int(input(f"Enter bitrate in Mbps (1-20): "))
                if 1 <= bitrate <= 20:
                    options["bitrate"] = bitrate * 1000000
                else:
                    print(f"{RED}Invalid bitrate. Using default.{RESET}")
            except:
                print(f"{RED}Invalid input. Using default.{RESET}")
        
        elif choice == "2":
            try:
                size = input(f"Enter max size (e.g., 1080, or 0 for no limit): ")
                options["max_size"] = int(size)
            except:
                print(f"{RED}Invalid input. Using default.{RESET}")
        
        elif choice == "3":
            options["no_audio"] = not options["no_audio"]
            print(f"Audio: {'Disabled' if options['no_audio'] else 'Enabled'}")
        
        elif choice == "4":
            options["stay_awake"] = not options["stay_awake"]
            print(f"Stay awake: {'Yes' if options['stay_awake'] else 'No'}")
        
        elif choice == "5":
            options["turn_screen_off"] = not options["turn_screen_off"]
            print(f"Turn screen off: {'Yes' if options['turn_screen_off'] else 'No'}")
        
        elif choice == "6":
            return options
        
        elif choice == "7":
            print(f"\n{YELLOW}Advanced options will be available in a future update{RESET}")
        
        else:
            print(f"{RED}Invalid choice!{RESET}")

def show_help():
    """Display help information"""
    terminal_width = get_terminal_size().columns
    
    print(f"\n{GRAY}━{'━' * (terminal_width - 2)}━{RESET}")
    print(f"ScreenShare allows you to share your Android screen to another device via OTG connection")
    print(f"\nRequirements:")
    print(f"- USB debugging enabled on the target Android device")
    print(f"- OTG connection between devices")
    print(f"- adb and scrcpy packages installed in Termux")
    print(f"\nCommands:")
    print(f"- {GREEN}screensh{RESET} - Start the tool")
    print(f"- {GREEN}screensh help{RESET} - Show this help")
    print(f"- {GREEN}screensh quick{RESET} - Start with default settings")
    print(f"{GRAY}━{'━' * (terminal_width - 2)}━{RESET}")

def main():
    """Main function"""
    if len(sys.argv) > 1:
        if sys.argv[1] in ["h", "help", "--help"]:
            print_header()
            show_help()
            return
        elif sys.argv[1] in ["q", "quick"]:
            print_header()
            if not check_dependencies() or not check_storage_permission():
                return
            if check_adb_connection():
                start_screen_sharing()
            return
    
    print_header()
    
    if not check_dependencies() or not check_storage_permission():
        return
    
    if check_adb_connection():
        options = get_sharing_options()
        start_screen_sharing(options)

if __name__ == "__main__":
    main()
