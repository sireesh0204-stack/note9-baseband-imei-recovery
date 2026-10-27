import subprocess
import re

def run_cmd(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True).stdout.strip()

print("=" * 60)
print(" SAMSUNG GALAXY NOTE 9 MODEM & BASEBAND DIAGNOSTIC")
print("=" * 60)

# Check Baseband
baseband = run_cmd("adb shell getprop gsm.version.baseband")
print(f"[*] Baseband Version: {baseband if baseband else 'UNKNOWN / CORRUPTED'}")

# Check SIM States
sim_state = run_cmd("adb shell getprop gsm.sim.state")
print(f"[*] SIM Slot States: {sim_state}")

# Check Operator Numeric
operator = run_cmd("adb shell getprop gsm.operator.alpha")
numeric = run_cmd("adb shell getprop gsm.operator.numeric")
print(f"[*] Registered Network: {operator} ({numeric})")

# Check RIL Daemons
ril_status = run_cmd("adb shell ps -A | grep -E 'rild|cbd'")
print(f"[*] RIL / Modem Daemons:\n{ril_status}")

print("=" * 60)
if baseband and "N960F" in baseband:
    print("[PASS] Shannon 337 Modem & Baseband are fully functional!")
else:
    print("[FAIL] Baseband is NULL. TrustZone / EFS reflash required.")
print("=" * 60)

