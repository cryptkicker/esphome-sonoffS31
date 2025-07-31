import csv
import subprocess
import tempfile
import shutil
import os
import time

TEMPLATE_PATH = "sonoffS31-template.yaml"

def run_cmd(cmd, cwd=None):
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"ERROR: {result.stderr}")
    return result.returncode == 0

with open("devices.csv") as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row['device_name'].startswith('#'):
            continue
        device_name = row["device_name"]
        friendly_name = row["friendly_name"]
        ip = row["ip"]
        restore_state = row["restore_state"]

        print(f"\n🔧 Working on {device_name} ({ip}) ...")

        # Create a temporary directory for build
        with tempfile.TemporaryDirectory(delete=True) as tempdir:
            shutil.copy(TEMPLATE_PATH, tempdir) or die("failed to copy file to tempdir")
            shutil.copy("secrets.yaml", tempdir) or die("failed to copy file to tempdir")
            shutil.copy("wifi-sonoff.yaml", tempdir) or die("failed to copy file to tempdir")
            temp_yaml = os.path.join(tempdir, f"{device_name}.yaml")

            # Write temporary YAML with substitutions
            with open(temp_yaml, "w") as outf:
                outf.write(f"""substitutions:
  device_name: {device_name}
  friendly_devicename: {friendly_name}
  static_ip: {ip}
  restore_state: {restore_state}

<<: !include {TEMPLATE_PATH}
""")

            # Compile firmware
            print("🔨 Compiling ...")
            if not run_cmd(["esphome", "compile", temp_yaml]):
                print(f"❌ Compile failed for {device_name}")
                continue

            # Locate firmware.bin and gzip it
            bin_path = os.path.join(tempdir, ".esphome", "build", device_name, ".pioenvs", device_name, "firmware.bin")
            gz_path = bin_path + ".gz"
            if os.path.exists(bin_path):
                print("📦 Compressing firmware ...")
                #shutil.copy(bin_path, gz_path[:-3])
                subprocess.run(["gzip", "-f", gz_path[:-3]])
            else:
                print(f"❌ Firmware binary not found for {device_name}")
                continue

            # Upload firmware OTA
            print("📡 Uploading OTA ...")
            success = run_cmd([
                "esphome", "upload", temp_yaml,
                "--device", ip,
                "--file", gz_path
            ])

            if success:
                print(f"✅ Upload successful: {device_name}")
            else:
                print(f"❌ Upload failed: {device_name}")

            time.sleep(3)  # Optional delay between devices

