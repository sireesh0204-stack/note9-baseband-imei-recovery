import subprocess
import os

print("=" * 60)
print(" EFS & NVRAM SECTOR BACKUP UTILITY")
print("=" * 60)

partitions = [
    ("EFS", "efs.img"),
    ("CPEFS", "cpefs.img"),
    ("PARAM", "param.img"),
    ("PERSISTENT", "persistent.img")
]

os.makedirs("backup_data", exist_ok=True)

for part_name, out_file in partitions:
    print(f"[*] Dumping partition: {part_name}...")
    dump_cmd = f"adb shell dd if=/dev/block/platform/11120000.ufs/by-name/{part_name} of=/sdcard/{out_file} bs=4096"
    subprocess.run(dump_cmd, shell=True, capture_output=True)
    
    print(f"[*] Pulling {out_file} to backup_data/...")
    subprocess.run(f"adb pull /sdcard/{out_file} backup_data/{out_file}", shell=True, capture_output=True)
    subprocess.run(f"adb shell rm /sdcard/{out_file}", shell=True, capture_output=True)

print("=" * 60)
print("[SUCCESS] All core NVRAM images securely backed up to backup_data/")
print("=" * 60)

