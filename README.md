# Samsung Galaxy Note 9 (SM-N960F / crownlte) Baseband & IMEI Restoration Blueprint

[![Device](https://img.shields.io/badge/Device-Samsung%20Galaxy%20Note%209%20(Exynos%209810)-blue.svg)](#)
[![Chipset](https://img.shields.io/badge/Modem-Shannon%20337%20Cat.18%20LTE-green.svg)](#)
[![OS](https://img.shields.io/badge/Android-10%20One%20UI%202.5%20(Bit%209)-orange.svg)](#)
[![Carrier](https://img.shields.io/badge/VoLTE-Jio%20India%20(INS)-purple.svg)](#)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An exhaustive, engineering-grade blueprint and diagnostic toolkit for diagnosing, recovering, and permanently restoring lost baseband, null/unknown IMEI, corrupted EFS/NVRAM partitions, and Jio VoLTE cellular calling on the Samsung Galaxy Note 9 (`SM-N960F`, Exynos 9810, `crownlte`).

---

## 📑 Table of Contents
1. [Root Cause Analysis (RCA)](#root-cause-analysis-rca)
2. [The Bit 9 Bootloader Constraint](#the-bit-9-bootloader-constraint)
3. [The 4-File Odin Restoration Architecture](#the-4-file-odin-restoration-architecture)
4. [Restoring Indian Carrier Configs & Jio VoLTE](#restoring-indian-carrier-configs--jio-volte)
5. [Hardware Camera Diagnostic Post-Mortem](#hardware-camera-diagnostic-post-mortem)
6. [Airtight EFS / NVRAM Partition Backup & Recovery](#airtight-efs--nvram-partition-backup--recovery)
7. [Automated Diagnostic Scripts](#automated-diagnostic-scripts)

---

## 1. Root Cause Analysis (RCA)

### The Shannon 337 Baseband Architecture
The European and Indian variants of the Galaxy Note 9 (`SM-N960F`) are powered by Samsung's **Exynos 9810** SoC, paired with the integrated **Shannon 337 Cat.18 LTE modem**. 

The cellular identity of the device is distributed across four distinct storage zones:
- **`EFS` (`/dev/block/sda3`, 20 MB):** Contains factory radio calibration files, MAC addresses, serial numbers, and cryptographic keys.
- **`CPEFS` (`/dev/block/sdd1`, 6 MB):** The dedicated Modem Processor EFS holding NVRAM runtime parameters.
- **`RPMB` (Replay Protected Memory Block):** An authenticated partition inside the UFS 2.1 chip containing the device's hardware root-of-trust.
- **TrustZone TEE Keystore:** Hardware-backed enclave validating the integrity of the EFS cryptographic signature on boot.

### Failure Mechanism
When custom ROMs, GSI builds, or improper regional CSC packages are flashed, the TrustZone keystore fails to validate the cryptographic hash of the `/efs` partition. When TrustZone rejects EFS:
1. The Radio Interface Layer (RIL) crashes during initialization.
2. The modem firmware reports `Baseband version: Unknown`.
3. The RIL daemon falls back to `IMEI: null` or generic dummy `00000000000000/01`.
4. SIM card slots fail to initialize, and all radio calling/data operations are hard-blocked by the kernel.

---

## 2. The Bit 9 Bootloader Constraint

Samsung enforces a hardware rollback prevention counter known as the **Binary / SW REV (Bit)**:
```text
SW REV: B:9 K:9 S:9
```
- If a device is on **Bit 9 (SW REV 9)** firmware, attempting to flash Bit 8 or older Android 8/9 stock firmware triggers an immediate Odin rollback error: `SW REV CHECK FAIL : [boot]Fused 9 > Binary 8`.
- Recovery **must** be executed using official stock **Android 10 Bit 9** binaries (`N960FXXU9FVG2`).

---

## 3. The 4-File Odin Restoration Architecture

Restoring baseband and re-establishing the TrustZone NVRAM binding requires a clean 4-file flash in **Odin3 v3.14.4**:

| Slot | File Name | Function |
| :--- | :--- | :--- |
| **BL** | `BL_N960FXXU9FVG2_...tar.md5` | Primary & Secondary Bootloaders (sboot, param, tz, keystore) |
| **AP** | `AP_N960FXXU9FVG2_...tar.md5` | Android System, Kernel (`boot.img`), Recovery, Vendor |
| **CP** | `CP_N960FXXU9FVG2_...tar.md5` | Shannon 337 Modem firmware (`modem.bin`), radio calibration |
| **CSC** | `CSC_OMC_OXM_N960FOXM9FVG2_...tar.md5` | Full PIT repartitioning and regional carrier payload (`INS`) |

> **CRITICAL:** Use standard `CSC_` (which enforces re-partitioning and restores clean NVRAM mount points), NOT `HOME_CSC_`.

### Execution:
1. Boot phone into Download Mode:
   ```bash
   adb reboot download
   ```
2. Verify Odin communication on Samsung USB Mobile Composite port (e.g., `COM6`).
3. Flash all 4 files. Ensure **Auto Reboot** and **F. Reset Time** are checked.
4. On reboot, the bootloader re-aligns the TrustZone cryptographic keys with the Shannon modem firmware.

---

## 4. Restoring Indian Carrier Configs & Jio VoLTE

Once the baseband is recovered, Indian VoLTE (specifically **Reliance Jio**, which is a pure 4G LTE/VoLTE network with no 2G/3G legacy fallback) requires active IMS registration.

### Verified Active IMS Framework Packages:
- `com.sec.ims` (Samsung IMS framework service)
- `com.sec.imsservice` (IMS protocol stack daemon)
- `com.samsung.ims.smk` (Samsung Multi-Carrier Kit)
- `com.samsung.advp.imssettings` (Advanced Calling settings)
- `com.sec.phone` & `com.android.phone` (RIL Telephony binding)

### Verification Commands:
```bash
adb shell getprop gsm.version.baseband
# Expected output: N960FXXU9FVG2

adb shell getprop gsm.sim.state
# Expected output: READY,NOT_READY (or READY,READY)

adb shell dumpsys telephony.registry | grep -i "mVoiceRegState"
# Expected output: mVoiceRegState=0 (IN_SERVICE)
```

---

## 5. Hardware Camera Diagnostic Post-Mortem

During the revival, the rear dual-camera exhibited a launch crash while the front camera worked flawlessly. Diagnostic investigation revealed:

### Secret Diagnostic Menu (`*#34971539#`):
- **Front Camera:**
  - Sensor Wide: `W08LLKF00AM`
  - Module ID: `AVLHA00E200B001` (100% Operational)
- **Rear Main Wide Sensor:**
  - Sensor Wide: `J12LLKL00SM`
  - Module ID: `SVLLD1F6E000A42` (EEPROM detected)
- **Rear Telephoto & OIS Sensor:**
  - Module ID: `null`
  - OIS Firmware: `null`

### Kernel Logcat Analysis:
```text
VIDIOC_S_INPUT (19 - No such device)
sensor_ak7372_aperture i2c communication failure
```
**Conclusion:** The failure is a physical hardware fault on the dual-lens flexible ribbon cable (Part `#GH96-11910A`), specifically on the I2C bus powering the dual mechanical aperture (`ak7372`) and OIS voice-coil motor. The front camera remains 100% functional for selfies and video calling.

---

## 6. Airtight EFS / NVRAM Partition Backup & Recovery

Before performing any further root operations, sector-level backups of the critical NVRAM partitions must be maintained:

```bash
# Dump raw EFS block
dd if=/dev/block/platform/11120000.ufs/by-name/EFS of=/sdcard/efs.img bs=4096

# Dump raw CPEFS block
dd if=/dev/block/platform/11120000.ufs/by-name/CPEFS of=/sdcard/cpefs.img bs=4096

# Pull to host PC
adb pull /sdcard/efs.img .
adb pull /sdcard/cpefs.img .
```

To restore in the event of corruption:
```bash
dd if=/sdcard/efs.img of=/dev/block/platform/11120000.ufs/by-name/EFS
dd if=/sdcard/cpefs.img of=/dev/block/platform/11120000.ufs/by-name/CPEFS
reboot
```

---

## 7. Automated Diagnostic Scripts

This repository includes turnkey Python scripts to verify device health:
- [`scripts/diagnose_modem.py`](scripts/diagnose_modem.py): Checks baseband, IMEI registration, and carrier signal.
- [`scripts/backup_efs.py`](scripts/backup_efs.py): Pulls binary images of EFS, CPEFS, and PARAM.
- [`scripts/diagnose_camera.py`](scripts/diagnose_camera.py): Performs sensor I2C polling check.

---

## 📜 License
Distributed under the MIT License. See [LICENSE](LICENSE) for more information.

