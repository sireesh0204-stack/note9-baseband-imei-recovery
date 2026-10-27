import subprocess

print("=" * 60)
print(" NOTE 9 DUAL-CAMERA SENSOR I2C DIAGNOSTIC")
print("=" * 60)

res = subprocess.run("adb logcat -d | grep -i -E 'camera|sensor_ak7372|vidioc'", shell=True, capture_output=True, text=True)
lines = [l for l in res.stdout.splitlines() if any(k in l.lower() for k in ['fail', 'error', 'vidioc', 'ak7372', 'module id'])]

print(f"[*] Found {len(lines)} camera sensor log entries:")
for l in lines[-15:]:
    print(f"  {l}")

print("=" * 60)
print("Diagnostic summary: Check if sensor_ak7372 I2C bus failed to determine ribbon cable fault.")
