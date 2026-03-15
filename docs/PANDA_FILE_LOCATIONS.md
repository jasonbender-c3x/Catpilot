# Panda File Locations Reference Guide

## Overview

This document provides a comprehensive mapping of file locations referenced in the panda documentation. Some files exist in the repository, while others are generated during build or are part of external dependencies.

---

## Files That EXIST in Repository

### Python Interface (User-Level API)

**Directory**: `/home/runner/work/Catpilot/Catpilot/panda/python/`

| File | Purpose | Documentation Reference |
|------|---------|------------------------|
| `__init__.py` | Main Panda class, CAN send/receive, safety modes | Lines 119-144 (safety modes), 769-842 (CAN API) |
| `constants.py` | MCU configurations, firmware paths | MCU types, addresses |
| `usb.py` | USB communication handler | USB connection handling |
| `spi.py` | SPI communication handler | SPI connection handling |
| `base.py` | Base handle class | Abstract interface |
| `isotp.py` | ISO-TP protocol implementation | Diagnostic communication |
| `uds.py` | UDS protocol implementation | Vehicle diagnostics |
| `dfu.py` | Device Firmware Update utilities | Firmware flashing |
| `serial.py` | Serial port handling | UART communication |
| `canhandle.py` | CAN packet handling | Message parsing |
| `ccp.py` | CCP protocol | Calibration protocol |
| `xcp.py` | XCP protocol | Measurement/calibration |

**Key Python File**:
```
/home/runner/work/Catpilot/Catpilot/panda/python/__init__.py
```
Contains: Panda class, safety modes (SAFETY_GM, SAFETY_ALLOUTPUT, etc.), CAN send/recv functions

---

### Board Firmware (Embedded C Code)

**Directory**: `/home/runner/work/Catpilot/Catpilot/panda/board/`

| File | Purpose | Lines of Code | Key Content |
|------|---------|---------------|-------------|
| `main.c` | Main firmware application | 404 | Initialization, heartbeat, safety mode switching |
| `bootstub.c` | Bootloader stub | 91 | DFU mode entry, firmware validation |

**Firmware Scripts**:
- `flash.py` - Flash firmware to panda via USB
- `recover.py` - Recovery mode for bricked pandas
- `dfu_util_f4.sh` - DFU utility for STM32F4
- `dfu_util_h7.sh` - DFU utility for STM32H7

**Key Firmware File**:
```
/home/runner/work/Catpilot/Catpilot/panda/board/main.c
```
Contains: Safety mode enforcement, heartbeat mechanism, CAN initialization

---

### Platform-Specific Files

**STM32F4 Directory**: `/home/runner/work/Catpilot/Catpilot/panda/board/stm32f4/`
- `startup_stm32f413xx.s` - Assembly startup code
- `stm32f4_flash.ld` - Linker script for flash layout

**STM32H7 Directory**: `/home/runner/work/Catpilot/Catpilot/panda/board/stm32h7/`
- `startup_stm32h7x5xx.s` - Assembly startup code
- `stm32h7x5_flash.ld` - Linker script for flash layout

---

### Linux Kernel Drivers

**Directory**: `/home/runner/work/Catpilot/Catpilot/panda/drivers/linux/`

| File | Purpose |
|------|---------|
| `panda.c` | Linux kernel module for panda USB device |
| `Makefile` | Build system for kernel module |
| `dkms.conf` | Dynamic Kernel Module Support config |
| `README.md` | Driver installation instructions |

**Installation**:
```bash
cd /home/runner/work/Catpilot/Catpilot/panda/drivers/linux
make
sudo insmod panda.ko
```

---

### SPI Drivers

**Directory**: `/home/runner/work/Catpilot/Catpilot/panda/drivers/spi/`

| File | Purpose |
|------|---------|
| `spidev_panda.c` | SPI device driver for panda |
| `Makefile` | Build system |
| `load.sh` | Load SPI driver |
| `pull-src.sh` | Download SPI source dependencies |

---

### Example Programs

**Directory**: `/home/runner/work/Catpilot/Catpilot/panda/examples/`

| File | Purpose | Use Case |
|------|---------|----------|
| `can_logger.py` | Log CAN messages to console | Reverse engineering CAN messages |
| `can_unique.py` | Find unique CAN messages | Identify new messages |
| `can_bit_transition.py` | Analyze bit transitions | Message format analysis |
| `tesla_tester.py` | Tesla-specific testing | Example of vehicle-specific testing |
| `query_fw_versions.py` | Query ECU firmware versions | Vehicle diagnostics |
| `query_vin_and_stats.py` | Query VIN and statistics | Vehicle info retrieval |

**Example Usage**:
```bash
cd /home/runner/work/Catpilot/Catpilot/panda/examples
python can_logger.py
```

---

### Documentation

| File | Content |
|------|---------|
| `/panda/README.md` | Main panda documentation, safety model, usage |
| `/panda/board/README.md` | Board-specific notes |
| `/panda/examples/can_unique.md` | CAN analysis guide |
| `/panda/examples/can_bit_transition.md` | Bit transition analysis guide |
| `/docs/PANDA_COMPREHENSIVE_DOCUMENTATION.md` | **THIS comprehensive guide** (45KB) |

---

## Files That DO NOT EXIST (Referenced but Missing)

### Header Files Referenced in main.c

These files are **#included** in `board/main.c` but are **NOT** in the repository:

| Include Statement | Expected Location | Status |
|-------------------|-------------------|--------|
| `#include "config.h"` | `panda/board/config.h` | ❌ Not in repo |
| `#include "safety.h"` | `panda/board/safety.h` | ❌ Not in repo |
| `#include "drivers/pwm.h"` | `panda/board/drivers/pwm.h` | ❌ Not in repo |
| `#include "drivers/usb.h"` | `panda/board/drivers/usb.h` | ❌ Not in repo |
| `#include "drivers/simple_watchdog.h"` | `panda/board/drivers/simple_watchdog.h` | ❌ Not in repo |
| `#include "drivers/bootkick.h"` | `panda/board/drivers/bootkick.h` | ❌ Not in repo |
| `#include "early_init.h"` | `panda/board/early_init.h` | ❌ Not in repo |
| `#include "provision.h"` | `panda/board/provision.h` | ❌ Not in repo |
| `#include "health.h"` | `panda/board/health.h` | ❌ Not in repo |
| `#include "drivers/can_common.h"` | `panda/board/drivers/can_common.h` | ❌ Not in repo |
| `#include "drivers/fdcan.h"` | `panda/board/drivers/fdcan.h` | ❌ Not in repo (H7 only) |
| `#include "drivers/bxcan.h"` | `panda/board/drivers/bxcan.h` | ❌ Not in repo (F4 only) |
| `#include "power_saving.h"` | `panda/board/power_saving.h` | ❌ Not in repo |
| `#include "can_comms.h"` | `panda/board/can_comms.h` | ❌ Not in repo |
| `#include "main_comms.h"` | `panda/board/main_comms.h` | ❌ Not in repo |

### Safety Hook Files (Critical for Understanding)

**Expected Directory**: `panda/board/safety/` (does NOT exist in this repo)

In the upstream comma.ai/panda repository, this directory contains:
- `safety_gm.h` - GM safety hooks
- `safety_toyota.h` - Toyota safety hooks
- `safety_honda.h` - Honda safety hooks
- `safety_defaults.h` - Default safety implementations
- (many others for each car manufacturer)

**Purpose**: These files define the TX message validation logic for each safety mode.

### Why Are These Files Missing?

**Three possibilities**:

1. **Build System Generates Them**
   - Some headers may be auto-generated during compilation
   - `obj/gitversion.h` is definitely generated (contains git commit hash)

2. **Part of Upstream Panda Repository**
   - Catpilot may be using precompiled panda firmware
   - Source code not needed for operation, only for modification
   - Original panda source: https://github.com/commaai/panda

3. **STM32 SDK/HAL Not Included**
   - Driver headers may come from STM32CubeF4/STM32CubeH7 SDKs
   - These are typically downloaded separately
   - Not committed to avoid repository bloat

---

## How to Access Missing Files

### Option 1: Clone Upstream Panda Repository

```bash
# Get the full panda source code
git clone https://github.com/commaai/panda.git
cd panda
ls board/safety/  # View safety hooks
ls board/drivers/ # View driver implementations
```

### Option 2: Download STM32 SDK

For STM32F4:
```bash
# Download STM32CubeF4
wget https://github.com/STMicroelectronics/STM32CubeF4/archive/refs/heads/master.zip
unzip master.zip
# Headers in: STM32CubeF4-master/Drivers/
```

For STM32H7:
```bash
# Download STM32CubeH7
wget https://github.com/STMicroelectronics/STM32CubeH7/archive/refs/heads/master.zip
unzip master.zip
# Headers in: STM32CubeH7-master/Drivers/
```

### Option 3: Build From Catpilot

If panda firmware build is integrated into Catpilot:
```bash
cd /home/runner/work/Catpilot/Catpilot/panda/board
# Check for Makefile or build script
ls -la
# May require: make, SCons, or other build system
```

---

## GM-Specific Files (selfdrive)

### Chevrolet Bolt Implementation

**Directory**: `/home/runner/work/Catpilot/Catpilot/selfdrive/car/gm/`

| File | Purpose | Key Content |
|------|---------|-------------|
| `values.py` | Vehicle parameters, constants | STEER_MAX=300, Bolt specs (lines 160-194) |
| `carcontroller.py` | Steering/brake/gas control logic | Torque application (lines 108-117) |
| `gmcan.py` | GM CAN message creation | create_steering_control() (lines 44-52) |
| `interface.py` | Car interface, tuning | Bolt config (lines 204-210), pedal detection (102-104) |
| `carstate.py` | Vehicle state parsing | CAN message parsing |
| `fingerprints.py` | CAN message fingerprints | Vehicle identification |
| `radar_interface.py` | Radar data processing | (if equipped) |

**Key GM Files**:
```
/home/runner/work/Catpilot/Catpilot/selfdrive/car/gm/values.py          # Parameters
/home/runner/work/Catpilot/Catpilot/selfdrive/car/gm/carcontroller.py   # Control logic
/home/runner/work/Catpilot/Catpilot/selfdrive/car/gm/gmcan.py           # CAN messages
```

---

### Common Selfdrive Files

**Directory**: `/home/runner/work/Catpilot/Catpilot/selfdrive/`

| File/Directory | Purpose |
|----------------|---------|
| `car/__init__.py` | Common car interface functions |
| `car/interfaces.py` | Base car interface class |
| `car/torque_data/` | Torque tuning parameters |
| `controls/lib/latcontrol_torque.py` | Lateral torque controller |
| `controls/lib/drive_helpers.py` | Driving helper functions |

**Torque Configuration**:
```
/home/runner/work/Catpilot/Catpilot/selfdrive/car/torque_data/override.toml
/home/runner/work/Catpilot/Catpilot/selfdrive/car/torque_data/params.toml
/home/runner/work/Catpilot/Catpilot/selfdrive/car/torque_data/neural_ff_weights.json
```

---

## Quick Reference: File Paths by Topic

### Safety Modes
- **Python Constants**: `/panda/python/__init__.py` (lines 119-144)
- **Firmware Switching**: `/panda/board/main.c` (lines 60-122)
- **Safety Hooks**: ❌ Not in repo (upstream: `panda/board/safety/safety_gm.h`)

### CAN Communication
- **Python API**: `/panda/python/__init__.py` (can_send, can_recv)
- **Firmware**: `/panda/board/main.c` (can_init_all)
- **GM Messages**: `/selfdrive/car/gm/gmcan.py`

### Steering Control
- **GM Parameters**: `/selfdrive/car/gm/values.py` (STEER_MAX, etc.)
- **Control Logic**: `/selfdrive/car/gm/carcontroller.py`
- **Torque Controller**: `/selfdrive/controls/lib/latcontrol_torque.py`

### 2021 Bolt Configuration
- **Vehicle Specs**: `/selfdrive/car/gm/values.py` (lines 160-166)
- **Tuning**: `/selfdrive/car/gm/interface.py` (lines 204-210)
- **Neural Network**: `/selfdrive/car/torque_data/neural_ff_weights.json`

### Gas Pedal Interceptor
- **Detection**: `/selfdrive/car/gm/interface.py` (lines 102-104)
- **Calculation**: `/selfdrive/car/gm/carcontroller.py` (lines 59-71)
- **Message Creation**: `/selfdrive/car/__init__.py` (create_gas_interceptor_command)

---

## Directory Tree Summary

```
/home/runner/work/Catpilot/Catpilot/
├── panda/                          # Panda hardware interface
│   ├── python/                     # ✅ Python API (11 files)
│   │   ├── __init__.py            # Main Panda class
│   │   ├── constants.py           # MCU configs
│   │   └── ...
│   ├── board/                      # Firmware (partially present)
│   │   ├── main.c                 # ✅ Main firmware (404 lines)
│   │   ├── bootstub.c             # ✅ Bootloader
│   │   ├── safety/                # ❌ NOT in repo
│   │   ├── drivers/               # ❌ NOT in repo
│   │   ├── stm32f4/               # ✅ Platform files
│   │   └── stm32h7/               # ✅ Platform files
│   ├── drivers/                    # Kernel drivers
│   │   ├── linux/                 # ✅ Linux kernel module
│   │   └── spi/                   # ✅ SPI driver
│   ├── examples/                   # ✅ Example programs (7 files)
│   └── README.md                   # ✅ Main documentation
│
├── selfdrive/                      # Catpilot driving logic
│   ├── car/                        # Car-specific implementations
│   │   ├── gm/                    # ✅ GM/Bolt files (8 files)
│   │   │   ├── values.py          # Vehicle parameters
│   │   │   ├── carcontroller.py   # Control logic
│   │   │   └── gmcan.py           # CAN messages
│   │   ├── torque_data/           # ✅ Torque tuning
│   │   └── interfaces.py          # Base interface
│   └── controls/                   # Control algorithms
│       └── lib/                    # Control libraries
│           └── latcontrol_torque.py  # ✅ Torque controller
│
└── docs/                           # Documentation
    ├── PANDA_COMPREHENSIVE_DOCUMENTATION.md  # ✅ Main guide (45KB)
    └── PANDA_FILE_LOCATIONS.md              # ✅ This file
```

**Legend**:
- ✅ = Files exist in repository
- ❌ = Files referenced but not in repository

---

## Common Questions

### Q: Where are the safety hooks?
**A**: Not in this repository. See upstream panda: https://github.com/commaai/panda/tree/master/board/safety

### Q: Can I modify steering torque limits without firmware source?
**A**: Yes! Modify `/selfdrive/car/gm/values.py` (STEER_MAX, STEER_DELTA_UP/DOWN). See documentation section "How to Modify Torque Limits".

### Q: Where are the CAN message definitions?
**A**: DBC files are in `/opendbc/` directory (submodule or separate repo). GM DBC used by `/selfdrive/car/gm/` files.

### Q: How do I recompile panda firmware?
**A**: You need the full panda repository with build system:
```bash
git clone https://github.com/commaai/panda.git
cd panda/board
make
```

### Q: Where is the neural network for Bolt steering?
**A**: `/selfdrive/car/torque_data/neural_ff_weights.json` - exists in repo!

---

## How to Use This Guide

1. **For Python development**: Use files in `/panda/python/` - all present
2. **For understanding firmware**: Read `/panda/board/main.c` and reference upstream for details
3. **For modifying Bolt behavior**: Edit files in `/selfdrive/car/gm/`
4. **For torque tuning**: Edit `/selfdrive/car/torque_data/override.toml`
5. **For safety modifications**: Need upstream panda repository

---

## Additional Resources

- **Upstream Panda**: https://github.com/commaai/panda
- **Catpilot**: https://github.com/commaai/catpilot  
- **OpenDBC**: https://github.com/commaai/opendbc (CAN message definitions)
- **STM32CubeF4**: https://github.com/STMicroelectronics/STM32CubeF4
- **STM32CubeH7**: https://github.com/STMicroelectronics/STM32CubeH7

---

**Last Updated**: 2026-03-15  
**Repository**: jasonbender-c3x/Catpilot  
**Branch**: copilot/document-panda-code
