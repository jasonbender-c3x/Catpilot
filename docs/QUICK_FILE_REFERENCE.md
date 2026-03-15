# Quick File Reference - "Where Are These Files?"

## TL;DR - Files You Can Access Right Now

### Python API (Main Interface)
```bash
/home/runner/work/Catpilot/Catpilot/panda/python/__init__.py
```
**What's in it**: Panda class, safety modes, CAN send/receive functions

### Main Firmware  
```bash
/home/runner/work/Catpilot/Catpilot/panda/board/main.c
```
**What's in it**: Safety mode enforcement, heartbeat, initialization (404 lines)

### GM/Bolt Control Files
```bash
/home/runner/work/Catpilot/Catpilot/selfdrive/car/gm/values.py          # STEER_MAX, vehicle params
/home/runner/work/Catpilot/Catpilot/selfdrive/car/gm/carcontroller.py   # Steering/brake control
/home/runner/work/Catpilot/Catpilot/selfdrive/car/gm/gmcan.py           # CAN message creation
/home/runner/work/Catpilot/Catpilot/selfdrive/car/gm/interface.py       # Bolt configuration
```

### Torque Tuning
```bash
/home/runner/work/Catpilot/Catpilot/selfdrive/car/torque_data/override.toml         # Custom values
/home/runner/work/Catpilot/Catpilot/selfdrive/car/torque_data/neural_ff_weights.json  # Neural net
```

---

## Files That DON'T Exist Here (But Are Referenced)

### Safety Hook Implementations
**Referenced**: `panda/board/safety/safety_gm.h`  
**Status**: ❌ Not in this repo  
**Where to find**: https://github.com/commaai/panda/tree/master/board/safety

### Driver Headers
**Referenced**: `panda/board/drivers/*.h`  
**Status**: ❌ Not in this repo  
**Where to find**: Upstream panda repo or STM32 SDK

---

## Complete File Listings

### All Panda Python Files (12 files)
```
panda/python/
├── __init__.py        ← Main Panda class (934 lines)
├── base.py           ← Base handle class
├── canhandle.py      ← CAN packet handling
├── ccp.py            ← CCP protocol
├── constants.py      ← MCU configs, addresses
├── dfu.py            ← Firmware update
├── isotp.py          ← ISO-TP protocol
├── serial.py         ← Serial/UART
├── spi.py            ← SPI communication
├── uds.py            ← UDS diagnostics
├── usb.py            ← USB communication
└── xcp.py            ← XCP protocol
```

### All GM/Bolt Files (8 files)
```
selfdrive/car/gm/
├── __init__.py
├── carcontroller.py   ← Main control logic (steering, brakes, gas)
├── carstate.py        ← Parse vehicle CAN messages
├── fingerprints.py    ← Vehicle identification
├── gmcan.py           ← Create CAN messages (steering, brake, etc.)
├── interface.py       ← Bolt config, tuning, pedal detection
├── radar_interface.py ← Radar processing
└── values.py          ← Parameters (STEER_MAX=300, Bolt specs)
```

### Panda Board Files (2 C files + scripts)
```
panda/board/
├── main.c            ← 404 lines, main firmware
├── bootstub.c        ← 91 lines, bootloader
├── flash.py          ← Flash tool
├── recover.py        ← Recovery tool
├── dfu_util_f4.sh    ← DFU for STM32F4
└── dfu_util_h7.sh    ← DFU for STM32H7
```

### Example Programs (7 files)
```
panda/examples/
├── can_logger.py              ← Log CAN messages
├── can_unique.py              ← Find unique messages
├── can_bit_transition.py      ← Analyze bit patterns
├── tesla_tester.py            ← Tesla example
├── query_fw_versions.py       ← ECU firmware query
└── query_vin_and_stats.py     ← VIN and stats
```

---

## Visual Directory Tree

```
Catpilot/
├── panda/                      # Hardware interface
│   ├── python/                 # ✅ Python API (12 files)
│   ├── board/                  # Firmware (partial)
│   │   ├── main.c             # ✅ Main firmware
│   │   ├── bootstub.c         # ✅ Bootloader
│   │   ├── safety/            # ❌ NOT HERE (need upstream)
│   │   └── drivers/           # ❌ NOT HERE (need upstream)
│   ├── drivers/linux/         # ✅ Kernel driver
│   ├── drivers/spi/           # ✅ SPI driver
│   └── examples/              # ✅ Example programs (7 files)
│
├── selfdrive/car/
│   ├── gm/                    # ✅ Bolt implementation (8 files)
│   ├── torque_data/           # ✅ Tuning files
│   └── interfaces.py          # ✅ Base interface
│
└── docs/
    ├── PANDA_COMPREHENSIVE_DOCUMENTATION.md  # 45KB main guide
    ├── PANDA_FILE_LOCATIONS.md              # 14KB detailed reference
    └── QUICK_FILE_REFERENCE.md              # This file
```

---

## What You Can Do With Files That Exist

### Modify Steering Torque (NO firmware needed)
Edit: `/selfdrive/car/gm/values.py`
```python
STEER_MAX = 350  # Increase from 300 (⚠️ test carefully!)
STEER_DELTA_UP = 15  # Faster response
```

### Enable Gas Pedal Interceptor
Already auto-detected in: `/selfdrive/car/gm/interface.py` line 102-104

### Log CAN Messages
Run: 
```bash
cd /home/runner/work/Catpilot/Catpilot/panda/examples
python can_logger.py
```

### Control Panda via Python
```python
from panda import Panda
p = Panda()
p.set_safety_mode(Panda.SAFETY_GM)
p.can_send(0x180, b"\x00\x01\x02", 0)
```

---

## What You CANNOT Do (Without Upstream Source)

### Modify Safety Hooks
**Need**: `panda/board/safety/safety_gm.h` from https://github.com/commaai/panda

### Recompile Firmware
**Need**: Full panda source with build system

### Add New Safety Modes
**Need**: Firmware source and ability to recompile

---

## How to Get Missing Files

### Option 1: Clone Upstream Panda
```bash
git clone https://github.com/commaai/panda.git
cd panda
ls board/safety/     # See all safety hooks
ls board/drivers/    # See all driver implementations
```

### Option 2: Just View Online
Browse: https://github.com/commaai/panda/tree/master/board

---

## Most Important Files for Your Use Case (2021 Bolt + Pedal)

1. **`/selfdrive/car/gm/interface.py`** - Bolt config, pedal detection (lines 102-104, 204-210)
2. **`/selfdrive/car/gm/values.py`** - Steering limits, Bolt specs (lines 13-24, 160-166)
3. **`/selfdrive/car/gm/carcontroller.py`** - Apply steering torque (lines 108-117)
4. **`/panda/python/__init__.py`** - Python API, safety modes (lines 119-144)
5. **`/selfdrive/car/torque_data/override.toml`** - Tune torque response

---

## Questions?

See the comprehensive guides:
- **PANDA_FILE_LOCATIONS.md** - Detailed reference with all paths
- **PANDA_COMPREHENSIVE_DOCUMENTATION.md** - How everything works

---

**Repository**: jasonbender-c3x/Catpilot  
**Last Updated**: 2026-03-15
