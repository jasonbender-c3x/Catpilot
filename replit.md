# CatPilot - The Pound Web Interface 🐱

## Project Overview

**CatPilot** is a fully open-sourced fork of openpilot, featuring clear and concise commits and serving as a resource for the openpilot developer community. This Replit project showcases **The Pound**, CatPilot's lightweight web-based interface for managing comma devices.

**Important Note**: This is a **demo version** of The Pound running in the Replit environment. Full functionality requires actual comma.ai hardware (comma 3/3X device). The demo version provides a preview of the user interface and basic API structure.

### What is openpilot?

openpilot is an open source driver assistance system that performs:
- Adaptive Cruise Control (ACC)
- Automated Lane Centering (ALC)
- Forward Collision Warning (FCW)
- Lane Departure Warning (LDW)

### What is The Pound?

The Pound is a web-based management interface that allows users to:
- View driving statistics
- Manage device settings and toggles
- Access error logs and screen recordings
- View recorded driving routes
- Configure navigation destinations

## Project Structure

```
.
├── catpilot/              # CatPilot-specific code
│   └── system/
│       └── the_pond/      # Web UI components (The Pound)
│           ├── assets/    # JavaScript, CSS, images
│           ├── templates/ # HTML templates
│           ├── the_pond.py  # Full Flask application (requires hardware)
│           └── utilities.py
├── demo_pond.py           # Demo version for Replit (THIS IS WHAT RUNS)
├── cereal/                # Messaging system (Cap'n Proto)
├── opendbc/               # CAN bus databases
├── panda/                 # Interface to comma hardware
├── system/                # Core openpilot systems
└── selfdrive/             # Autonomous driving logic
```

## Technology Stack

### Backend
- **Python 3.11** - Main programming language
- **Flask** - Web framework
- **Cap'n Proto** - Messaging protocol (via pycapnp)

### Frontend
- **Arrow.js** - Minimal reactive framework
- **Bootstrap Icons** - Icon library
- **Mapbox GL** - Map rendering (for navigation features)
- Pure JavaScript (ES modules) - No build step required

## Running in Replit

The project runs a simplified demo version (`demo_pond.py`) that:
- Serves the web UI on port 5000
- Provides stub API endpoints
- Works without comma.ai hardware dependencies
- Displays "Demo Mode" messages

### Current Setup
- **Workflow**: "The Pound Web UI" - Runs automatically
- **Port**: 5000 (configured for Replit webview)
- **Host**: 0.0.0.0 (allows Replit proxy to work)

## Development

### Adding Features to Demo

Edit `demo_pond.py` to add new API endpoints:

```python
@app.route("/api/your_endpoint", methods=["GET"])
def your_endpoint():
    return jsonify({"data": "value"})
```

### Frontend Development

The frontend uses Arrow.js with ES modules. Files are in:
- `catpilot/system/the_pond/assets/components/` - UI components
- `catpilot/system/the_pond/assets/js/` - Utilities
- `catpilot/system/the_pond/templates/` - HTML templates

No build step is needed - just edit and refresh!

## Deployment

Deployment is configured using Replit's autoscale mode:
- **Type**: autoscale (stateless web app)
- **Command**: `python3 demo_pond.py`
- Scales automatically with traffic

## Limitations in Replit

The demo version has limitations compared to running on actual hardware:
- No real driving data or routes
- No hardware controls (doors, camera, etc.)
- No CAN bus integration
- No real-time vehicle data
- Mock responses for most API endpoints

## Full CatPilot Installation

To run the full version, you need:
1. A comma 3 or comma 3X device
2. Install via: `catpilot.download`
3. Connect to a supported vehicle

## Recent Changes

### December 8, 2025
- Imported from GitHub
- Created demo version for Replit
- Configured Flask server for port 5000
- Set up workflow and deployment
- Added stub API endpoints for demo mode
- Renamed from "The Pond" to "The Pound" with cat theme

## Resources

- [CatPilot GitHub](https://github.com/CatAi/CatPilot)
- [CatPilot Discord](https://discord.gg/catpilot)
- [openpilot Documentation](https://github.com/commaai/openpilot)
- [comma.ai](https://comma.ai)

## Architecture Notes

### Original System (Full Version)
- Uses SoCons build system for C/Cython components
- Requires msgq (shared memory IPC), cereal (messaging), opendbc (CAN)
- Designed for embedded Linux (AGNOS) on comma devices
- Real-time processing of sensor and vehicle data

### Demo Version (This Replit)
- Pure Python Flask application
- No compiled dependencies
- Stub implementations for hardware features
- Serves static frontend with mock API responses
