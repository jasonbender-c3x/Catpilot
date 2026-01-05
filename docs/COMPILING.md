# Compiling CatPilot

This guide covers how to build CatPilot from source for development, testing, and deployment to comma devices.

## Table of Contents

- [System Requirements](#system-requirements)
- [Quick Start](#quick-start)
- [Ubuntu 24.04 Setup](#ubuntu-2404-setup)
- [macOS Setup](#macos-setup)
- [Building CatPilot](#building-catpilot)
- [Cross-Compiling for Comma Devices](#cross-compiling-for-comma-devices)
- [Development Builds](#development-builds)
- [Production Builds](#production-builds)
- [Troubleshooting](#troubleshooting)
- [Advanced Topics](#advanced-topics)

---

## System Requirements

### Minimum Hardware
| Component | Requirement |
|-----------|-------------|
| CPU | 4+ cores (8+ recommended) |
| RAM | 8 GB minimum (16 GB recommended) |
| Storage | 50 GB free space |
| GPU | NVIDIA GPU recommended for simulation |

### Supported Operating Systems
- **Ubuntu 24.04 LTS** (primary development platform)
- **Ubuntu 22.04 LTS** (supported)
- **macOS 13+ (Ventura)** (Intel and Apple Silicon)

> **Note:** Windows is NOT supported. Use WSL2 with Ubuntu if on Windows, but some features (webcam, USB) may not work.

---

## Quick Start

For experienced developers, here's the fast path:

```bash
# Clone the repository
git clone https://github.com/commaai/catpilot.git
cd catpilot

# Run setup script (Ubuntu)
./tools/ubuntu_setup.sh

# Build everything
scons -j$(nproc)

# Authenticate with comma account
python3 tools/lib/auth.py
```

---

## Ubuntu 24.04 Setup

### Step 1: System Update

```bash
sudo apt update && sudo apt upgrade -y
```

### Step 2: Install Base Dependencies

```bash
sudo apt install -y \
  build-essential \
  git \
  git-lfs \
  curl \
  wget \
  cmake \
  ninja-build \
  ccache \
  clang \
  lld \
  python3 \
  python3-pip \
  python3-venv
```

### Step 3: Install Development Libraries

```bash
# OpenGL and graphics
sudo apt install -y \
  libgl1-mesa-dev \
  libgles2-mesa-dev \
  libegl1-mesa-dev \
  libglfw3-dev \
  libglew-dev

# Qt 5 for UI tools (Cabana, etc.)
sudo apt install -y \
  qtbase5-dev \
  qtdeclarative5-dev \
  qtmultimedia5-dev \
  libqt5svg5-dev \
  libqt5x11extras5-dev \
  qml-module-qtquick2 \
  qml-module-qtquick-controls2

# Media and codec libraries
sudo apt install -y \
  libavcodec-dev \
  libavformat-dev \
  libavutil-dev \
  libswscale-dev \
  libavdevice-dev \
  libavfilter-dev

# System libraries
sudo apt install -y \
  libssl-dev \
  libcurl4-openssl-dev \
  libsqlite3-dev \
  libbz2-dev \
  libffi-dev \
  liblzma-dev \
  libusb-1.0-0-dev \
  libzmq3-dev \
  libcapnp-dev \
  capnproto

# OpenCL for GPU acceleration
sudo apt install -y \
  ocl-icd-opencl-dev \
  pocl-opencl-icd
```

### Step 4: Install Python Dependencies

```bash
# Create virtual environment (recommended)
python3 -m venv .venv
source .venv/bin/activate

# Install Python packages
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 5: Run Setup Script

CatPilot includes an automated setup script:

```bash
./tools/ubuntu_setup.sh
```

This script:
- Verifies system dependencies
- Installs missing packages
- Sets up Git LFS
- Configures environment variables

---

## macOS Setup

### Step 1: Install Homebrew

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### Step 2: Install Dependencies

```bash
# Core tools
brew install \
  git \
  git-lfs \
  cmake \
  ninja \
  ccache \
  llvm

# Python
brew install python@3.11

# Qt 5 for UI tools
brew install qt@5

# Media libraries
brew install ffmpeg

# System libraries
brew install \
  openssl@3 \
  capnp \
  zeromq \
  libusb
```

### Step 3: Configure Environment

Add to your `~/.zshrc` or `~/.bash_profile`:

```bash
# Qt5 path
export PATH="/opt/homebrew/opt/qt@5/bin:$PATH"
export LDFLAGS="-L/opt/homebrew/opt/qt@5/lib"
export CPPFLAGS="-I/opt/homebrew/opt/qt@5/include"

# OpenSSL
export PATH="/opt/homebrew/opt/openssl@3/bin:$PATH"
export LDFLAGS="$LDFLAGS -L/opt/homebrew/opt/openssl@3/lib"
export CPPFLAGS="$CPPFLAGS -I/opt/homebrew/opt/openssl@3/include"
```

Reload your shell:

```bash
source ~/.zshrc
```

### Step 4: Run Setup Script

```bash
./tools/mac_setup.sh
```

---

## Building CatPilot

CatPilot uses **SCons** as its build system.

### Full Build

Build everything (first time takes 15-30 minutes):

```bash
scons -j$(nproc)
```

The `-j$(nproc)` flag uses all available CPU cores.

### Incremental Builds

After the initial build, subsequent builds are much faster:

```bash
scons -j$(nproc)
```

SCons automatically detects changed files and rebuilds only what's necessary.

### Building Specific Components

```bash
# Build only selfdrive
scons -j$(nproc) selfdrive/

# Build only tools
scons -j$(nproc) tools/

# Build Cabana
cd tools/cabana && scons -j$(nproc)

# Build Replay
cd tools/replay && scons -j$(nproc)

# Build PlotJuggler plugin
cd tools/plotjuggler && scons -j$(nproc)
```

### Clean Build

To start fresh:

```bash
# Clean build artifacts
scons -c

# Remove all generated files
rm -rf .sconsign.dblite
find . -name "*.o" -delete
find . -name "*.pyc" -delete

# Rebuild
scons -j$(nproc)
```

---

## Cross-Compiling for Comma Devices

CatPilot runs on comma 3 and comma 3X devices, which use ARM64 architecture.

### Option 1: Build on Device (Slow)

SSH into your comma device and build directly:

```bash
ssh comma@<device-ip>
cd /data/catpilot
scons -j4
```

> **Warning:** Building on-device is slow (1-2 hours) and may exhaust storage. Use cross-compilation for faster iteration.

### Option 2: Cross-Compile (Recommended)

Set up cross-compilation on your development machine:

```bash
# Install ARM64 cross-compiler
sudo apt install -y \
  gcc-aarch64-linux-gnu \
  g++-aarch64-linux-gnu \
  binutils-aarch64-linux-gnu

# Install QEMU for testing
sudo apt install -y qemu-user-static

# Build for ARM64
ARCH=aarch64 scons -j$(nproc)
```

### Deploying to Device

After building, deploy to your comma device:

```bash
# Sync built files to device
rsync -avz --progress \
  --exclude='.git' \
  --exclude='*.o' \
  --exclude='.venv' \
  ./ comma@<device-ip>:/data/catpilot/

# SSH in and restart
ssh comma@<device-ip>
tmux kill-session -t comma || true
/data/catpilot/launch_catpilot.sh
```

---

## Development Builds

### Debug Build

For debugging with symbols:

```bash
scons -j$(nproc) --debug-build
```

This enables:
- Debug symbols (`-g`)
- No optimization (`-O0`)
- Address sanitizer
- Verbose logging

### Release Build (with Debug Info)

```bash
scons -j$(nproc) --release-with-debug
```

### Using ccache

Speed up rebuilds with ccache:

```bash
# Install ccache
sudo apt install ccache

# Configure (add to ~/.bashrc)
export PATH="/usr/lib/ccache:$PATH"
export CCACHE_DIR="$HOME/.ccache"
export CCACHE_MAXSIZE="10G"

# Verify ccache is working
ccache -s
```

---

## Production Builds

### Building for Release

```bash
# Clean first
scons -c

# Build with optimizations
scons -j$(nproc) --release

# Strip debug symbols (smaller binaries)
find . -name "*.so" -exec strip {} \;
find . -name "*_pyx.cpython-*.so" -exec strip {} \;
```

### Creating a Release Package

```bash
# Build release
scons -j$(nproc) --release

# Create package
./release/build_release.sh
```

---

## Troubleshooting

### Common Build Errors

#### Error: "capnp: command not found"

```bash
# Install Cap'n Proto
sudo apt install capnproto libcapnp-dev
```

#### Error: "Qt5 not found"

```bash
# Install Qt5
sudo apt install qtbase5-dev qtdeclarative5-dev

# Set Qt5 path (if needed)
export QT_SELECT=qt5
```

#### Error: "OpenCL not found"

```bash
# Install OpenCL
sudo apt install ocl-icd-opencl-dev pocl-opencl-icd

# For NVIDIA GPUs
sudo apt install nvidia-opencl-dev
```

#### Error: "Python module not found"

```bash
# Ensure virtual environment is active
source .venv/bin/activate

# Reinstall requirements
pip install -r requirements.txt
```

#### Error: "scons: command not found"

```bash
pip install scons
```

#### Error: "Cython compilation failed"

```bash
# Update Cython
pip install --upgrade cython

# Clean Cython cache
find . -name "*.pyx" -exec rm -f {}.c \;
find . -name "*.pxd" -exec rm -f {}.c \;

# Rebuild
scons -j$(nproc)
```

#### Error: "Out of memory during build"

Reduce parallel jobs:

```bash
# Use fewer cores
scons -j4

# Or build sequentially
scons -j1
```

#### Error: "Permission denied" on comma device

```bash
# Fix permissions
ssh comma@<device-ip>
chmod -R 755 /data/catpilot
```

### Build Verification

After building, verify the installation:

```bash
# Check selfdrive builds
ls -la selfdrive/modeld/_modeld
ls -la selfdrive/ui/ui

# Check tools
ls -la tools/cabana/cabana
ls -la tools/replay/replay

# Run tests
pytest -v selfdrive/test/
```

---

## Advanced Topics

### Parallel Build Optimization

For faster builds on multi-core systems:

```bash
# Use ninja backend (faster than make)
scons -j$(nproc) --site-dir=site_scons

# Distribute builds with distcc
sudo apt install distcc
export DISTCC_HOSTS="localhost/8 192.168.1.100/4"
scons -j16 CC="distcc gcc" CXX="distcc g++"
```

### Custom Build Configurations

Create `site_scons/site_config.py`:

```python
# Custom build options
CCFLAGS = ['-march=native', '-mtune=native']
LINKFLAGS = ['-fuse-ld=lld']

# Enable LTO (Link Time Optimization)
LTO = True

# Custom paths
CAPNP_PATH = '/opt/capnproto'
QT5_PATH = '/opt/qt5'
```

### Building Individual Daemons

```bash
# Build specific daemon
scons -j$(nproc) selfdrive/modeld/modeld
scons -j$(nproc) selfdrive/controls/controlsd
scons -j$(nproc) selfdrive/locationd/locationd
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest selfdrive/test/test_models.py

# Run with coverage
pytest --cov=selfdrive --cov-report=html
```

---

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PYTHONPATH` | Python module search path | Auto-configured |
| `OPENPILOT_ROOT` | CatPilot installation directory | Current directory |
| `SIMULATION` | Enable simulation mode | `0` |
| `NOSENSOR` | Disable hardware sensors | `0` |
| `USE_WEBCAM` | Use webcam instead of comma cameras | `0` |
| `ZMQ` | Use ZeroMQ for messaging | `0` |

Set these before building or running:

```bash
export SIMULATION=1
export USE_WEBCAM=1
./launch_catpilot.sh
```

---

## Getting Help

- **GitHub Issues**: Report build problems
- **Wiki**: Additional documentation

---

## See Also

- [TOOLS.md](TOOLS.md) - Development tools guide
- [CONTRIBUTING.md](../CONTRIBUTING.md) - Contribution guidelines
- [README.md](../README.md) - Project overview
