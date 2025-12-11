# CatPilot Development Tools

This document covers all the development and debugging tools available in CatPilot. These tools help with analyzing drives, debugging issues, porting new cars, and testing without a vehicle.

## Table of Contents

- [Quick Start](#quick-start)
- [Tool Overview](#tool-overview)
- [Cabana - CAN Bus Analyzer](#cabana---can-bus-analyzer)
- [Replay - Drive Playback](#replay---drive-playback)
- [PlotJuggler - Data Visualization](#plotjuggler---data-visualization)
- [Joystick - Manual Control](#joystick---manual-control)
- [CameraStream - Remote Camera Viewing](#camerastream---remote-camera-viewing)
- [Simulator - Virtual Driving](#simulator---virtual-driving)
- [Webcam - PC-Based CatPilot](#webcam---pc-based-catpilot)
- [The Pound - Web Management Interface](#the-pound---web-management-interface)
- [Theme Maker](#theme-maker)
- [Lateral Tuner](#lateral-tuner)
- [Longitudinal Tuner](#longitudinal-tuner)
- [Model Selector](#model-selector)
- [Force Car Recognition](#force-car-recognition)
- [Legacy Debug Tools](#legacy-debug-tools)
- [Build Instructions](#build-instructions)
- [Troubleshooting](#troubleshooting)

---

## Quick Start

Before using any tools, set up your development environment:

```bash
# Clone CatPilot
git clone https://github.com/commaai/catpilot.git
cd catpilot

# Install dependencies (Ubuntu 24.04 / macOS)
./tools/ubuntu_setup.sh   # or ./tools/mac_setup.sh

# Build
scons -j$(nproc)

# Authenticate with comma account (for cloud routes)
python3 tools/lib/auth.py
```

---

## Tool Overview

### Core Development Tools

| Tool | Purpose | Hardware Required |
|------|---------|-------------------|
| **Cabana** | CAN message analyzer & DBC editor | Optional |
| **Replay** | Replay recorded drives | No |
| **PlotJuggler** | Time-series data visualization | No |
| **Joystick** | Control car with joystick/keyboard | Panda + Car |
| **CameraStream** | Stream cameras over network | Comma device |
| **Simulator** | Virtual driving with MetaDrive | No |
| **Webcam** | Run CatPilot on PC with webcams | Panda + Webcam |

### Web Interface & Customization

| Tool | Purpose | Hardware Required |
|------|---------|-------------------|
| **The Pound** | Web-based device management | Comma device |
| **Theme Maker** | Create custom UI themes | Comma device |
| **Model Selector** | Switch AI driving models | Comma device |
| **Force Car Recognition** | Manual vehicle fingerprinting | Comma device |

### Tuning Tools

| Tool | Purpose | Hardware Required |
|------|---------|-------------------|
| **Lateral Tuner** | Fine-tune steering control | Comma device + Car |
| **Longitudinal Tuner** | Fine-tune acceleration/braking | Comma device + Car |

### Legacy Tools

| Tool | Purpose | Hardware Required |
|------|---------|-------------------|
| **unlogger.py** | Legacy drive replay | No |
| **selfdrive/debug/** | Debug scripts & log filters | No |
| **carcontrols/** | Legacy joystick control | Panda + Car |

---

## Cabana - CAN Bus Analyzer

Cabana is a powerful tool for viewing, plotting, and analyzing CAN bus messages. Essential for reverse engineering new cars and debugging CAN issues.

### Features
- Binary and hex visualization of CAN frames
- DBC file loading and signal decoding
- Real-time plotting of decoded signals
- Live connection to panda or replay from logs
- Share routes via URL

### Building Cabana

```bash
# From catpilot root directory
cd tools/cabana
scons -j$(nproc)
```

### Usage

```bash
# View a recorded route
./cabana "a2a0ccea32023010|2023-07-27--13-01-19"

# Demo mode
./cabana --demo

# Live from panda
./cabana --panda

# With specific DBC file
./cabana --dbc opendbc/honda_civic.dbc <route>

# From local files
./cabana --data_dir /path/to/route <route-name>
```

### Command Line Options

| Option | Description |
|--------|-------------|
| `--demo` | Use demo route |
| `--auto` | Auto-load from best source |
| `--qcam` | Load qcamera |
| `--ecam` | Load wide road camera |
| `--panda` | Read live from panda |
| `--panda-serial <serial>` | Specific panda device |
| `--socketcan <device>` | Read from SocketCAN |
| `--zmq <ip>` | Read from ZMQ |
| `--dbc <file>` | DBC file to load |
| `--data_dir <path>` | Local route directory |

### Finding Your Routes
Visit [connect.comma.ai](https://connect.comma.ai) to find your recorded drives.

---

## Replay - Drive Playback

Replay allows you to simulate a driving session by replaying all logged messages. Perfect for testing changes without a car.

### Building Replay

```bash
cd tools/replay
scons -j$(nproc)
```

### Usage

```bash
# Authenticate first
python3 tools/lib/auth.py

# Replay a route
tools/replay/replay "a2a0ccea32023010|2023-07-27--13-01-19"

# Demo route
tools/replay/replay --demo

# Local route
tools/replay/replay <route> --data_dir="/path/to/routes"

# With ZMQ messaging
ZMQ=1 tools/replay/replay <route>
```

### Command Line Options

| Option | Description |
|--------|-------------|
| `-a, --allow <list>` | Whitelist services (comma-separated) |
| `-b, --block <list>` | Blacklist services |
| `-c, --cache <n>` | Cache n segments in memory (default: 5) |
| `-s, --start <sec>` | Start from seconds |
| `-x <speed>` | Playback speed (0.2 - 3.0) |
| `--demo` | Use demo route |
| `--dcam` | Load driver camera |
| `--ecam` | Load wide camera |
| `--qcam` | Load qcamera |
| `--no-loop` | Stop at end |
| `--no-vipc` | No video output |
| `--all` | Output all messages |

### Visualize with UI

```bash
# Terminal 1: Start replay
tools/replay/replay <route>

# Terminal 2: Start UI
cd selfdrive/ui && ./ui.py
```

### Watch All Cameras (watch3)

```bash
# Start replay with all cameras
tools/replay/replay --demo --dcam --ecam

# Start watch3
cd selfdrive/ui && ./watch3.py
```

---

## PlotJuggler - Data Visualization

PlotJuggler is a powerful tool for visualizing time-series data from CatPilot logs.

### Installation

```bash
cd tools/plotjuggler
./juggle.py --install
```

### Usage

```bash
# Plot a route
./juggle.py "a2a0ccea32023010|2023-07-27--13-01-19"

# Demo with tuning layout
./juggle.py --demo --layout=layouts/tuning.xml

# Segment range
./juggle.py "route/0:5"

# Live streaming
./juggle.py --stream
```

### Command Line Options

| Option | Description |
|--------|-------------|
| `--demo` | Use demo route |
| `--can` | Parse CAN data |
| `--stream` | Streaming mode |
| `--layout <file>` | Pre-defined layout |
| `--install` | Install/update PlotJuggler |
| `--dbc <name>` | DBC for CAN parsing |

### Streaming from Device

```bash
# On comma device via SSH:
cd /data/catpilot && ./cereal/messaging/bridge

# On your laptop (connected to device hotspot):
ZMQ=1 ./juggle.py --stream
```

### Layouts

- `layouts/tuning.xml` - For tuning PRs and car porting
- Custom layouts can be saved and shared

---

## Joystick - Manual Control

Control your car's steering and acceleration using a joystick or keyboard. Useful for testing and car porting.

### Usage

#### Keyboard Control (SSH into device)
```bash
tools/joystick/joystick_control.py --keyboard
```

**Keys:**
- WASD - Gas/brake/steering in 5% increments

#### USB Joystick on Comma Device
```bash
# Plug joystick into aux USB-C port
tools/joystick/joystick_control.py
```

#### Network Joystick (Laptop to Device)

```bash
# On comma device:
echo -n "1" > /data/params/d/JoystickDebugMode
cereal/messaging/bridge {LAPTOP_IP} testJoystick

# On laptop:
export ZMQ=1
tools/joystick/joystick_control.py
```

### Safety Notes
- Car must be OFF and CatPilot offroad before starting
- Ensure panda conditions allow controls (e.g., cruise engaged)
- Start car after joystick_control is running

---

## CameraStream - Remote Camera Viewing

Stream camera feeds from your comma device to a PC over the network.

### On the Comma Device (SSH)

```bash
# Run all three in separate terminals or:
(
  cd /data/catpilot/cereal/messaging/ && ./bridge &
  cd /data/catpilot/system/camerad/ && ./camerad &
  cd /data/catpilot/system/loggerd/ && ./encoderd &
  wait
)
# Ctrl+C stops all
```

### On Your PC

```bash
# Decode stream
cd tools/camerastream
./compressed_vipc.py <device-ip>

# View stream
cd selfdrive/ui && ./watch3.py
```

### Options

| Option | Description |
|--------|-------------|
| `--nvidia` | Use NVIDIA decoder |
| `--cams <n>` | Which cameras (0, 1, 2) |
| `--silent` | Suppress debug output |

### Example

```bash
./compressed_vipc.py comma-ffffffff --cams 0
```

---

## Simulator - Virtual Driving

Run CatPilot in the MetaDrive simulator for development without a car.

### Setup

```bash
# Install MetaDrive
pip install metadrive-simulator
```

### Usage

```bash
# Terminal 1: Launch CatPilot
./tools/sim/launch_openpilot.sh

# Terminal 2: Launch bridge
./tools/sim/run_bridge.py
```

### Controls

| Key | Action |
|-----|--------|
| 1 | Cruise Resume/Accel |
| 2 | Cruise Set/Decel |
| 3 | Cruise Cancel |
| r | Reset Simulation |
| i | Toggle Ignition |
| q | Exit |
| WASD | Manual control |

### Bridge Options

```bash
./run_bridge.py --joystick      # Use joystick
./run_bridge.py --high_quality  # Better graphics
./run_bridge.py --dual_camera   # Enable dual camera
```

---

## Webcam - PC-Based CatPilot

Run CatPilot on a regular PC using USB webcams instead of comma hardware.

### Requirements

- Ubuntu 24.04 or macOS (WSL2 NOT supported)
- GPU recommended
- USB webcam: 720p+, 78° FOV (e.g., Logitech C920)
- Comma car harness
- Panda
- USB-A to USB-A cable

### Setup

```bash
# Install OpenCL (Ubuntu)
sudo apt install pocl-opencl-icd

# Build catpilot
scons -j$(nproc)
```

### Hardware Connection

1. Connect webcam
2. Connect PC to panda via USB

### Running

```bash
USE_WEBCAM=1 system/manager/manager.py
```

### Specify Camera Devices

```bash
# Use /dev/video1 for road camera
USE_WEBCAM=1 ROAD_CAM=1 system/manager/manager.py

# Multiple cameras
USE_WEBCAM=1 ROAD_CAM=0 DRIVER_CAM=1 WIDE_CAM=2 system/manager/manager.py
```

---

## The Pound - Web Management Interface

The Pound is CatPilot's web-based fleet management interface, accessible from any browser on the same network as your comma device.

### Access

Open a web browser and navigate to:
```
http://YOUR.DEVICE.IP:8082
```

### Features

| Section | Functionality |
|---------|---------------|
| **Home** | Driving statistics, disk usage, software info |
| **Navigation** | Set destinations, manage Mapbox keys |
| **Recordings** | View dashcam routes, screen recordings |
| **Tailscale** | Network connectivity status |
| **Tools** | Theme Maker, Speed Limits, Error Logs, Toggles |
| **Settings** | Device configuration, model selection |

### Finding Your Device IP

```bash
# On the comma device via SSH:
ip addr show wlan0 | grep inet
```

Or check your router's connected devices list.

---

## Theme Maker

Create custom visual themes for your CatPilot interface.

### Access

Navigate to The Pound → Tools → Theme Maker

### Customization Options

- **Colors**: Primary accent colors, background shades
- **Icons**: Custom steering wheel, turn signals, alerts
- **Sounds**: Engagement/disengagement alerts, chimes
- **Animations**: Turn signal styles, path visualization

### Pre-Built Themes

CatPilot includes seasonal and custom themes:
- Default Cat Theme
- Holiday themes (seasonal)
- Community-submitted themes

### Sharing Themes

Export your theme and share it with the community via Discord or GitHub.

---

## Lateral Tuner

Fine-tune steering (lateral) control parameters for your specific vehicle.

### Access

Settings → Driving Controls → Steering → Advanced Lateral Tuning

### Parameters

| Parameter | Description |
|-----------|-------------|
| **Steer Ratio** | Steering wheel turns lock-to-lock |
| **Steer Rate Cost** | How quickly steering changes (smoothness) |
| **Steer Actuator Delay** | Latency compensation |
| **Tire Stiffness Factor** | Grip modeling |
| **NNFF Models** | Neural Network Feedforward models |

### NNFF (Neural Network Feedforward)

Location: `catpilot/assets/nnff_models/`

Pre-trained models for specific vehicles that improve steering accuracy based on real-world data.

### Tuning Tips

1. Start with stock values
2. Adjust one parameter at a time
3. Test on straight roads first, then curves
4. Use PlotJuggler to analyze steering behavior

---

## Longitudinal Tuner

Fine-tune acceleration and braking (longitudinal) control.

### Access

Settings → Driving Controls → Gas/Brake → Advanced Longitudinal Tuning

### Parameters

| Parameter | Description |
|-----------|-------------|
| **Acceleration Profile** | Comfort, Normal, Sport |
| **Following Distance** | Time gap to lead vehicle (0.5s - 3.0s) |
| **Stopping Distance** | How close to stop behind lead |
| **Jerk Limits** | Smoothness of speed changes |

### Traffic Mode

Dynamic following distance that adjusts based on speed:
- 0.5s @ 0 mph (stopped)
- 1.0s @ 55 mph (highway)

Great for dense city traffic.

---

## Model Selector

Switch between different AI driving models without reinstalling.

### Access

Settings → Software → Current Driving Model

### Available Models

Models are downloaded on-demand and cached locally:

| Model | Characteristics |
|-------|-----------------|
| **Blue Diamond** | Smooth, good lane centering |
| **Notre Dame** | Latest general-purpose model |
| **Custom** | User-trained or community models |

### Model Caching

Downloaded models are stored locally for offline switching:
```
/data/catpilot/models/
```

### Switching Models

1. Park the vehicle (cannot switch while driving)
2. Go to Model Selector
3. Select desired model
4. Wait for download (if not cached)
5. Restart openpilot

---

## Force Car Recognition

Manually specify your vehicle when automatic fingerprinting fails.

### Access

Settings → Vehicle → Force Car Recognition

### When to Use

- New/unsupported vehicle variants
- Modified vehicles with non-standard CAN messages
- Debugging fingerprinting issues

### Usage

1. Select your car make
2. Select model/year
3. Confirm selection
4. Reboot device

### Supported Platforms

Works with most vehicles including:
- GM (Chevrolet, Cadillac, GMC, Buick)
- Toyota/Lexus
- Honda/Acura
- Hyundai/Kia/Genesis
- And many more...

---

## Legacy Debug Tools

These tools are from earlier openpilot builds and remain useful for development and debugging.

### unlogger.py - Drive Data Replay (Legacy)

Replays recorded drive data locally for debugging.

```bash
python tools/replay/unlogger.py '<route-name>' <data-directory>

# Example:
python tools/replay/unlogger.py '99c94dc769b5d96e|2018-11-14--13-31-42' ~/data
```

**Note:** Modern CatPilot uses the C++ `replay` tool instead. Use unlogger only for legacy compatibility.

### selfdrive/debug/ - Debug Scripts

Location: `selfdrive/debug/`

| Script | Purpose |
|--------|---------|
| `filter_log_message.py` | Filter specific log messages from replay |
| `test_car_model.py` | Automated testing for car ports |
| `dump_car_info.py` | Dump car fingerprint and parameters |

### carcontrols/ - Manual Joystick Control (Legacy)

Direct car control via joystick for reverse engineering.

**Hardware Required:**
- Panda
- Car harness
- USB Joystick

```bash
# Terminal 1: Start joystick daemon
python carcontrols/joystickd.py

# Terminal 2: Start board daemon
selfdrive/boardd/tests/boardd_old.py

# Terminal 3: Debug controls
python carcontrols/debug_controls.py
```

**Warning:** Requires bypassing safety checks. Use only in controlled environments.

### CAN Replay to Device

Replay CAN messages from PC to comma device using two pandas.

**Hardware:**
- 2x Panda devices
- Debug board
- Comma 3/3X

```bash
# Terminal 1: Mock board daemon
MOCK=1 tools/replay/boardd.py

# Terminal 2: Unlogger
python tools/replay/unlogger.py <route> <data-dir>
```

---

## Build Instructions

### Prerequisites

#### Ubuntu 24.04
```bash
sudo apt update
sudo apt install -y build-essential git python3 python3-pip cmake
sudo apt install -y libgl1-mesa-dev libgles2-mesa-dev
sudo apt install -y libavcodec-dev libavformat-dev libswscale-dev
sudo apt install -y qtbase5-dev qtdeclarative5-dev
sudo apt install -y libssl-dev libcurl4-openssl-dev
sudo apt install -y libsqlite3-dev libbz2-dev
sudo apt install -y ocl-icd-opencl-dev pocl-opencl-icd
```

#### macOS
```bash
brew install cmake python@3.11 qt@5 ffmpeg openssl
```

### Building All Tools

```bash
# From catpilot root
scons -j$(nproc)

# Build specific tool
cd tools/cabana && scons -j$(nproc)
cd tools/replay && scons -j$(nproc)
```

### Installing Python Dependencies

```bash
pip install -r requirements.txt
```

### PlotJuggler Installation

```bash
cd tools/plotjuggler
./juggle.py --install
```

---

## Troubleshooting

### Common Issues

#### "No module named 'cereal'"
```bash
# Build the project first
scons -j$(nproc)
```

#### Authentication Errors
```bash
# Re-authenticate
python3 tools/lib/auth.py
```

#### Video Decoder Issues
```bash
# Try software decoder
./replay --no-hw-decoder <route>
```

#### Qt/GUI Not Working on Linux
```bash
export QT_QPA_PLATFORM=xcb
```

#### Permission Denied on panda
```bash
# Add udev rule
echo 'SUBSYSTEM=="usb", ATTR{idVendor}=="bbaa", MODE="0666"' | \
  sudo tee /etc/udev/rules.d/99-panda.rules
sudo udevadm control --reload-rules
```

### Getting Help

- [CatPilot Discord](https://discord.gg/catpilot)
- [GitHub Issues](https://github.com/commaai/catpilot/issues)
- [comma.ai Wiki](https://github.com/commaai/openpilot/wiki)

---

## Credits

**Fork Maintainers:** Jason Bender & Replit Agent (Claude by Anthropic)

**Original:** The Compiler, comma.ai team

---

*Last updated: December 2025*
