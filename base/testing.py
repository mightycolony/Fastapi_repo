import os
import re

def update_iso_path(file_path, iso):
    iso_path = "/home/iso/{}".format(iso)
    print(f"Updating ISO path to: {iso_path}")  # Debugging output
    
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    
    pattern = re.compile(r'^ISO\s*=\s*')
   
    with open(file_path, 'w', encoding='utf-8') as file:
        for line in lines:
            if pattern.match(line.strip()):
                file.write(f"\tISO={iso_path}\n")
            else:
                file.write(line)

# Define paths
isopath = "/home/karthi/Desktop/FIRE/FAST_UPGRADE_SERVER/base/freebsd-update-server/iso"
os_version = "13.1-RELEASE"
update_server_path = "/home/karthi/Desktop/FIRE/FAST_UPGRADE_SERVER/base/freebsd-update-server"

# Check if the build.subr file exists
build_subr_path = os.path.join(update_server_path, "scripts", "build.subr")
if os.path.isfile(build_subr_path):
    iso = None
    for filename in os.listdir(isopath):
        if os_version in filename:
            iso = filename
            break  # Exit loop once the correct file is found
    
    if iso:
        print(f"ISO file found: {iso}")
        update_iso_path(build_subr_path, iso)
    else:
        print(f"No ISO file matching version {os_version} found in {isopath}.")
else:
    print(f"File not found: {build_subr_path}")
