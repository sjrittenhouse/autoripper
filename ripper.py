import os
import sys
import subprocess
import urllib.request
import shutil
import time

# --- CONFIGURATION ---
BIN_FOLDER = os.path.join(os.getcwd(), "bin")
HANDBRAKE_URL = "https://github.com/HandBrake/HandBrake/releases/download/1.7.3/HandBrakeCLI-1.7.3-Win_GUI.zip" # Example CLI link
DVDCSS_URL = "https://github.com/allienx/libdvdcss-dll/raw/main/1.4.3/64-bit/libdvdcss-2.dll"
HB_EXE = os.path.join(BIN_FOLDER, "HandBrakeCLI.exe")
CSS_DLL = os.path.join(BIN_FOLDER, "libdvdcss-2.dll")

def setup_environment():
    """Checks for bin folder, HandBrake, and libdvdcss."""
    if not os.path.exists(BIN_FOLDER):
        print("Creating bin folder...")
        os.makedirs(BIN_FOLDER)

    # 1. Check/Download libdvdcss
    if not os.path.exists(CSS_DLL):
        print("Downloading libdvdcss for DVD decryption...")
        urllib.request.urlretrieve(DVDCSS_URL, CSS_DLL)
        print("[✓] libdvdcss installed.")

    # 2. Check/Download HandBrakeCLI
    if not os.path.exists(HB_EXE):
        print("HandBrakeCLI not found in bin. Please ensure HandBrakeCLI.exe is in the bin folder.")
        # Note: Auto-downloading/unzipping HandBrake is complex in a script; 
        # usually best to bundle it or ask user to provide it.
        sys.exit(1)

def get_disc_drive():
    """Wait for a DVD to be inserted."""
    print("Checking for DVD...")
    # This searches for the first drive that has a 'VIDEO_TS' folder (Standard DVD)
    import string
    available_drives = ['%s:' % d for d in string.ascii_uppercase if os.path.exists('%s:' % d)]
    
    while True:
        for drive in available_drives:
            if os.path.exists(os.path.join(drive, "VIDEO_TS")):
                print(f"[✓] DVD Detected in drive {drive}")
                return drive
        
        input("No DVD found. Please insert a DVD and press Enter to try again...")

def rip_movie():
    setup_environment()
    drive_path = get_disc_drive()
    
    # 3. Get Movie Name
    movie_name = input("What is the name of the movie? ").strip()
    output_file = f"{movie_name}.mp4"

    # 4. Execute HandBrake
    # We set the environment variable so HandBrake finds the DLL in our bin folder
    my_env = os.environ.copy()
    my_env["PATH"] = BIN_FOLDER + os.pathsep + my_env["PATH"]

    print(f"Starting Rip: {movie_name}...")
    
    # Simple HQ 1080p Preset
    cmd = [
        HB_EXE,
        "-i", drive_path,
        "-o", output_file,
        "--preset", "General/HQ 1080p30 Surround"
    ]

    try:
        # Run the process and show output in console
        subprocess.run(cmd, env=my_env, check=True)
        print(f"Successfully encoded {output_file}!")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred during encoding: {e}")

if __name__ == "__main__":
    rip_movie()