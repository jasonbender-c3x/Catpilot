# CatPilot - Complete User Interface System 🐱

## Project Overview

**CatPilot** is a fully open-sourced fork of openpilot, featuring clear and concise commits and serving as a resource for the catpilot developer community. This project includes two distinct user interfaces:

1. **The Pound** - Web-based management interface (port 8082)
2. **On-Device UI** - In-vehicle display on comma 3X screen

**Note**: This Replit runs a demo version of The Pound. Full functionality requires comma.ai hardware (comma 3/3X device).

### What is CatPilot?

CatPilot is an open source driver assistance system that performs:
- Adaptive Cruise Control (ACC)
- Automated Lane Centering (ALC)
- Forward Collision Warning (FCW)
- Lane Departure Warning (LDW)

## Two User Interfaces

### 1. The Pound (Web Interface)

**Access**: Connect to your comma 3X over the Internet on port 8082

The Pound is a web-based management interface that allows users to:
- View driving statistics and routes
- Manage device settings and toggles
- Access error logs and screen recordings
- Configure navigation destinations
- Download and manage themes

**Design Features**:
- Dark cyan/teal color scheme (#00bcd4)
- Cat-themed branding throughout
- Mobile-responsive with PWA support
- 44px touch targets for accessibility

**Location**: `catpilot/system/the_pond/`

### 2. On-Device UI (In-Vehicle Display)

**Access**: Displayed on the comma 3X screen when driving

The on-device UI shows:
- Current speed (large, centered display)
- Engagement status (CatPilot Ready/Engaged/Override)
- Driver alerts and warnings
- System status indicators (GPS, Camera, Model, Panda)
- Real-time vehicle information

**Design Features**:
- Matches The Pound's dark cyan theme
- Cat emoji status indicators (🐱 😺 🚫)
- High-contrast for daylight visibility
- Glowing cyan accents for night driving

**Location**: `selfdrive/ui/`
- `catpilot_ui.py` - Main driving HUD
- `catpilot_settings.py` - Settings panel

## Project Structure

```
.
├── catpilot/                    # CatPilot-specific code
│   ├── assets/                  # UI assets and themes
│   │   ├── active_theme/        # Currently active theme
│   │   ├── holiday_themes/      # Seasonal themes
│   │   ├── stock_theme/         # Default theme
│   │   │   ├── colors/          # Color definitions (JSON)
│   │   │   ├── distance_icons/  # Following distance icons
│   │   │   ├── icons/           # UI icons
│   │   │   └── steering_wheel/  # Steering wheel image
│   │   ├── toggle_icons/        # Settings menu icons
│   │   └── theme_manager.py     # Theme download/management
│   └── system/
│       └── the_pond/            # Web UI (The Pound)
│           ├── assets/          # JS, CSS, images
│           ├── templates/       # HTML templates
│           └── the_pond.py      # Flask application
├── selfdrive/                   # Driving system
│   └── ui/                      # On-device UI
│       ├── catpilot_ui.py       # Main driving interface
│       ├── catpilot_settings.py # Settings panel
│       ├── ui.py                # Legacy UI
│       └── translations/        # Language files
├── demo_pond.py                 # Demo for Replit
├── cereal/                      # Messaging (Cap'n Proto)
├── opendbc/                     # CAN bus databases
└── panda/                       # Hardware interface
```

## Technology Stack

### The Pound (Web UI)
- **Python 3.11** with **Flask** - Backend
- **Arrow.js** - Minimal reactive framework
- **Bootstrap Icons** - Icon library
- **Mapbox GL** - Map rendering
- Pure JavaScript ES modules

### On-Device UI
- **Python 3.11** with **PyQt5** - GUI framework
- **cereal** - Inter-process messaging
- Custom cat-themed widgets

## Design System

Both interfaces share a consistent design language:

### Colors
| Color | Hex | Usage |
|-------|-----|-------|
| Cyan Primary | `#00bcd4` | Accents, active states |
| Cyan Dark | `#00838f` | Pressed states |
| Cyan Light | `#4dd0e1` | Highlights |
| Background | `#0a0a0a` | Main background |
| Background Secondary | `#1a1a1a` | Cards, panels |
| Text Primary | `#ffffff` | Main text |
| Text Secondary | `#b0bec5` | Descriptions |
| Warning | `#ff9800` | Caution alerts |
| Danger | `#f44336` | Critical alerts |

### Cat-Themed Elements
- 🐱 CatPilot Ready
- 😺 CatPilot Engaged  
- 🚫 Not Available
- Holiday themes (Christmas, Halloween, World Cat Day)

## Running in Replit

The demo version (`demo_pond.py`) provides a preview of The Pound:
- Serves web UI on port 5000
- Stub API endpoints
- Mock data responses

### Current Setup
- **Workflow**: "The Pound Web UI"
- **Port**: 5000 (Replit webview)
- **Host**: 0.0.0.0

## Theme System

CatPilot supports extensive theming:

### Theme Components
- **Colors** - Color scheme definitions (JSON)
- **Icons** - UI button icons (PNG)
- **Distance Icons** - Following distance indicators
- **Steering Wheel** - Custom wheel images
- **Sounds** - Alert and notification sounds
- **Turn Signals** - Turn signal animations

### Holiday Themes
Automatic themes for special days:
- New Year's Day
- Valentine's Day
- St. Patrick's Day
- World Cat Day (March 20)
- Easter
- May the Fourth
- Cinco de Mayo
- Stitch Day
- Fourth of July
- Halloween Week
- Thanksgiving Week
- Christmas Week

## Documentation

- **[docs/COMPILING.md](docs/COMPILING.md)** - Build and compilation guide
- **[docs/TOOLS.md](docs/TOOLS.md)** - Development tools reference
- **[docs/MEDIA_ASSETS.md](docs/MEDIA_ASSETS.md)** - Media asset catalog
- **[CAR_ASSETS_INVENTORY.md](CAR_ASSETS_INVENTORY.md)** - Vehicle assets inventory

## Development Tools

### Core Tools
| Tool | Purpose |
|------|---------|
| **Cabana** | CAN message analyzer |
| **Replay** | Drive replay for testing |
| **PlotJuggler** | Data visualization |
| **Simulator** | Virtual driving (MetaDrive) |

### Customization Tools
| Tool | Purpose |
|------|---------|
| **The Pound** | Web device management |
| **Theme Maker** | Custom UI themes |
| **Model Selector** | AI model switching |
| **Lateral Tuner** | Steering tuning |
| **Longitudinal Tuner** | Acceleration tuning |

See [docs/TOOLS.md](docs/TOOLS.md) for complete instructions.

## Recent Changes

### December 28, 2025
- Created enhanced on-device UI (`catpilot_ui.py`)
- Added settings panel (`catpilot_settings.py`)
- Unified design system across both interfaces
- Implemented full theme integration:
  - Colors loaded from `active_theme/colors/colors.json` with fallback to stock_theme
  - Theme JSON colors mapped to UI: Path→cyan, PathEdge→cyan_dark, Sidebar1→text, Sidebar2→text_secondary, Sidebar3→cyan_light, LeadMarker→danger
  - All hardcoded rgba/hex values replaced with dynamic theme-aware values
  - Both catpilot_ui.py and catpilot_settings.py use consistent theme loading
- Updated documentation for dual-interface architecture

### December 8, 2025
- Imported from GitHub
- Created Replit demo version
- Complete rebranding to CatPilot
- Generated cat-themed assets
- Mobile-responsive The Pound interface

## Resources

- [CatPilot GitHub](https://github.com/CatAi/CatPilot)
- [CatPilot Discord](https://discord.gg/catpilot)
- [comma.ai](https://comma.ai)

## Architecture Notes

### Production (comma 3X)
- SoCons build system for C/Cython
- Real-time sensor processing
- Inter-process messaging (msgq, cereal)
- Embedded Linux (AGNOS)

### Demo (Replit)
- Pure Python Flask application
- Mock API responses
- Static frontend serving
