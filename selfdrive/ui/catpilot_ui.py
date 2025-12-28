#!/usr/bin/env python3
"""
CatPilot On-Device UI
A polished driving interface for comma 3X devices matching The Pound's design.
"""
import os
import signal
import json
from pathlib import Path
from datetime import datetime

signal.signal(signal.SIGINT, signal.SIG_DFL)

import cereal.messaging as messaging
from catpilot.system.hardware import HARDWARE

from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, pyqtProperty, QPoint
from PyQt5.QtWidgets import (
    QLabel, QWidget, QVBoxLayout, QHBoxLayout, QStackedLayout, 
    QApplication, QFrame, QGraphicsDropShadowEffect, QGraphicsOpacityEffect
)
from PyQt5.QtGui import QFont, QFontDatabase, QColor, QPainter, QPainterPath, QLinearGradient

try:
    from catpilot.selfdrive.ui.qt.python_helpers import set_main_window
except ImportError:
    def set_main_window(widget):
        pass

ASSETS_PATH = Path(__file__).parent.parent.parent / "catpilot" / "assets"
ACTIVE_THEME_PATH = ASSETS_PATH / "active_theme"
STOCK_THEME_PATH = ASSETS_PATH / "stock_theme"

def rgba_to_hex(color_dict):
    """Convert theme color dict {red, green, blue, alpha} to hex string."""
    if not color_dict:
        return None
    r = color_dict.get('red', 0)
    g = color_dict.get('green', 0)
    b = color_dict.get('blue', 0)
    return f"#{r:02x}{g:02x}{b:02x}"

def hex_to_rgba(hex_color, alpha=1.0):
    """Convert hex color to rgba() CSS string."""
    hex_color = hex_color.lstrip('#')
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return f"rgba({r}, {g}, {b}, {alpha})"

def load_theme_colors():
    """Load colors from active theme or fall back to stock theme."""
    colors_file = ACTIVE_THEME_PATH / "colors" / "colors.json"
    if not colors_file.exists():
        colors_file = STOCK_THEME_PATH / "colors" / "colors.json"
    
    if colors_file.exists():
        try:
            with open(colors_file) as f:
                return json.load(f)
        except:
            pass
    return {}

def get_theme_palette():
    """
    Get color palette from theme, with fallback defaults.
    
    Theme JSON supports these driving overlay colors:
    - Path: Main driving path color (used as UI accent)
    - PathEdge: Path edge/border color (used as accent dark variant)
    - LaneLines: Lane line overlay color
    - LeadMarker: Lead vehicle marker color (used as danger/alert)
    - Sidebar1/2/3: Sidebar text colors
    
    UI colors (bg, text) use sensible defaults as they're
    not part of the theme schema.
    """
    theme = load_theme_colors()
    
    path_color = rgba_to_hex(theme.get('Path'))
    path_edge = rgba_to_hex(theme.get('PathEdge'))
    lead_marker = rgba_to_hex(theme.get('LeadMarker'))
    sidebar1 = rgba_to_hex(theme.get('Sidebar1'))
    sidebar2 = rgba_to_hex(theme.get('Sidebar2'))
    sidebar3 = rgba_to_hex(theme.get('Sidebar3'))
    
    return {
        'cyan': path_color or "#00bcd4",
        'cyan_dark': path_edge or "#00838f",
        'cyan_light': sidebar3 or "#4dd0e1",
        'bg': "#0a0a0a",
        'bg_secondary': "#1a1a1a",
        'bg_tertiary': "#0d0d0d",
        'text': sidebar1 or "#ffffff",
        'text_secondary': sidebar2 or "#b0bec5",
        'success': path_color or "#00bcd4",
        'warning': "#ff9800",
        'danger': lead_marker or "#f44336",
    }

THEME = get_theme_palette()
CATPILOT_CYAN = THEME['cyan']
CATPILOT_CYAN_DARK = THEME['cyan_dark']
CATPILOT_CYAN_LIGHT = THEME['cyan_light']
CATPILOT_BG = THEME['bg']
CATPILOT_BG_SECONDARY = THEME['bg_secondary']
CATPILOT_BG_TERTIARY = THEME['bg_tertiary']
CATPILOT_TEXT = THEME['text']
CATPILOT_TEXT_SECONDARY = THEME['text_secondary']
CATPILOT_SUCCESS = THEME['success']
CATPILOT_WARNING = THEME['warning']
CATPILOT_DANGER = THEME['danger']


class StatusIndicator(QFrame):
    def __init__(self, icon_text="", label_text="", parent=None):
        super().__init__(parent)
        self.setFixedSize(120, 80)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)
        
        self.icon = QLabel(icon_text)
        self.icon.setAlignment(Qt.AlignCenter)
        self.icon.setStyleSheet(f"""
            font-size: 28px;
            color: {CATPILOT_CYAN};
        """)
        
        self.label = QLabel(label_text)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet(f"""
            font-size: 12px;
            font-weight: 500;
            color: {CATPILOT_TEXT_SECONDARY};
            text-transform: uppercase;
            letter-spacing: 1px;
        """)
        
        layout.addWidget(self.icon)
        layout.addWidget(self.label)
        
        self.setStyleSheet(f"""
            StatusIndicator {{
                background-color: {CATPILOT_BG_SECONDARY};
                border-radius: 12px;
                border: 1px solid {hex_to_rgba(CATPILOT_CYAN, 0.2)};
            }}
        """)
    
    def set_value(self, value, color=None):
        self.icon.setText(str(value))
        if color:
            self.icon.setStyleSheet(f"font-size: 28px; color: {color};")


class SpeedDisplay(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(200, 200)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(0)
        layout.setAlignment(Qt.AlignCenter)
        
        self.speed_value = QLabel("0")
        self.speed_value.setAlignment(Qt.AlignCenter)
        self.speed_value.setStyleSheet(f"""
            font-size: 72px;
            font-weight: 700;
            color: {CATPILOT_TEXT};
            font-family: 'Inter', 'Segoe UI', sans-serif;
        """)
        
        self.speed_unit = QLabel("MPH")
        self.speed_unit.setAlignment(Qt.AlignCenter)
        self.speed_unit.setStyleSheet(f"""
            font-size: 16px;
            font-weight: 500;
            color: {CATPILOT_CYAN};
            text-transform: uppercase;
            letter-spacing: 2px;
        """)
        
        layout.addWidget(self.speed_value)
        layout.addWidget(self.speed_unit)
        
        self.setStyleSheet(f"""
            SpeedDisplay {{
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 {hex_to_rgba(CATPILOT_CYAN, 0.15)},
                    stop: 1 {hex_to_rgba(CATPILOT_CYAN, 0.05)}
                );
                border-radius: 100px;
                border: 3px solid {CATPILOT_CYAN};
            }}
        """)
        
        cyan_hex = CATPILOT_CYAN.lstrip('#')
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(int(cyan_hex[0:2], 16), int(cyan_hex[2:4], 16), int(cyan_hex[4:6], 16), 80))
        shadow.setOffset(0, 0)
        self.setGraphicsEffect(shadow)
    
    def set_speed(self, speed, is_metric=False):
        self.speed_value.setText(str(int(speed)))
        self.speed_unit.setText("KM/H" if is_metric else "MPH")


class EngagementStatus(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(60)
        self.setMinimumWidth(300)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 10, 20, 10)
        layout.setSpacing(12)
        
        self.status_icon = QLabel("🐱")
        self.status_icon.setStyleSheet("font-size: 32px;")
        
        self.status_text = QLabel("CatPilot Ready")
        self.status_text.setStyleSheet(f"""
            font-size: 18px;
            font-weight: 600;
            color: {CATPILOT_TEXT};
        """)
        
        layout.addWidget(self.status_icon)
        layout.addWidget(self.status_text)
        layout.addStretch()
        
        self._update_style("ready")
    
    def _update_style(self, state):
        colors = {
            "ready": (CATPILOT_CYAN, hex_to_rgba(CATPILOT_CYAN, 0.15)),
            "engaged": (CATPILOT_SUCCESS, hex_to_rgba(CATPILOT_SUCCESS, 0.15)),
            "overriding": (CATPILOT_WARNING, hex_to_rgba(CATPILOT_WARNING, 0.15)),
            "disengaged": (CATPILOT_TEXT_SECONDARY, hex_to_rgba(CATPILOT_TEXT_SECONDARY, 0.1)),
            "error": (CATPILOT_DANGER, hex_to_rgba(CATPILOT_DANGER, 0.15))
        }
        
        border_color, bg_color = colors.get(state, colors["ready"])
        
        self.setStyleSheet(f"""
            EngagementStatus {{
                background-color: {bg_color};
                border-radius: 30px;
                border: 2px solid {border_color};
            }}
        """)
    
    def set_status(self, state, enabled, engageable):
        if not engageable:
            self.status_icon.setText("🚫")
            self.status_text.setText("Not Available")
            self._update_style("error")
        elif enabled:
            if state in ("overriding", "preEnabled"):
                self.status_icon.setText("🐱")
                self.status_text.setText("Driver Override")
                self._update_style("overriding")
            else:
                self.status_icon.setText("😺")
                self.status_text.setText("CatPilot Engaged")
                self._update_style("engaged")
        else:
            self.status_icon.setText("🐱")
            self.status_text.setText("CatPilot Ready")
            self._update_style("ready")


class AlertBanner(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(80)
        self.setMaximumHeight(120)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 16, 24, 16)
        layout.setSpacing(4)
        
        self.alert_primary = QLabel("")
        self.alert_primary.setAlignment(Qt.AlignCenter)
        self.alert_primary.setWordWrap(True)
        self.alert_primary.setStyleSheet(f"""
            font-size: 24px;
            font-weight: 600;
            color: {CATPILOT_TEXT};
        """)
        
        self.alert_secondary = QLabel("")
        self.alert_secondary.setAlignment(Qt.AlignCenter)
        self.alert_secondary.setWordWrap(True)
        self.alert_secondary.setStyleSheet(f"""
            font-size: 16px;
            font-weight: 400;
            color: {CATPILOT_TEXT_SECONDARY};
        """)
        
        layout.addWidget(self.alert_primary)
        layout.addWidget(self.alert_secondary)
        
        self.hide()
        
        self._update_style("info")
    
    def _update_style(self, alert_type):
        colors = {
            "info": (CATPILOT_CYAN, hex_to_rgba(CATPILOT_CYAN, 0.2)),
            "warning": (CATPILOT_WARNING, hex_to_rgba(CATPILOT_WARNING, 0.2)),
            "critical": (CATPILOT_DANGER, hex_to_rgba(CATPILOT_DANGER, 0.25)),
            "success": (CATPILOT_SUCCESS, hex_to_rgba(CATPILOT_SUCCESS, 0.2))
        }
        
        border_color, bg_color = colors.get(alert_type, colors["info"])
        
        self.setStyleSheet(f"""
            AlertBanner {{
                background-color: {bg_color};
                border-radius: 16px;
                border: 2px solid {border_color};
            }}
        """)
    
    def set_alert(self, text1, text2="", alert_type="info"):
        if text1:
            self.alert_primary.setText(text1)
            self.alert_secondary.setText(text2)
            self._update_style(alert_type)
            self.show()
        else:
            self.hide()


class SteeringWheelIndicator(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(80, 80)
        self.setAlignment(Qt.AlignCenter)
        self.setText("🎡")
        self.setStyleSheet(f"""
            font-size: 48px;
            background-color: transparent;
        """)
        self._rotation = 0
    
    def set_rotation(self, angle):
        self._rotation = angle


class TopBar(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(50)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 8, 20, 8)
        layout.setSpacing(16)
        
        self.logo = QLabel("🐱 CatPilot")
        self.logo.setStyleSheet(f"""
            font-size: 18px;
            font-weight: 700;
            color: {CATPILOT_CYAN};
            letter-spacing: 1px;
        """)
        
        self.time_label = QLabel("")
        self.time_label.setStyleSheet(f"""
            font-size: 14px;
            font-weight: 500;
            color: {CATPILOT_TEXT_SECONDARY};
        """)
        
        self.temp_label = QLabel("--°C")
        self.temp_label.setStyleSheet(f"""
            font-size: 14px;
            font-weight: 500;
            color: {CATPILOT_TEXT_SECONDARY};
        """)
        
        self.network_label = QLabel("📶")
        self.network_label.setStyleSheet(f"""
            font-size: 16px;
        """)
        
        layout.addWidget(self.logo)
        layout.addStretch()
        layout.addWidget(self.time_label)
        layout.addWidget(QLabel("•"))
        layout.addWidget(self.temp_label)
        layout.addWidget(self.network_label)
        
        self.setStyleSheet(f"""
            TopBar {{
                background-color: {hex_to_rgba(CATPILOT_BG_SECONDARY, 0.9)};
                border-bottom: 1px solid {hex_to_rgba(CATPILOT_CYAN, 0.3)};
            }}
        """)
    
    def update_time(self):
        self.time_label.setText(datetime.now().strftime("%H:%M"))
    
    def update_temp(self, temp_c):
        self.temp_label.setText(f"{temp_c:.0f}°C")


class BottomBar(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(80)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 10, 20, 10)
        layout.setSpacing(20)
        
        self.indicators = {}
        
        indicator_data = [
            ("gps", "📍", "GPS"),
            ("panda", "🐼", "PANDA"),
            ("camera", "📷", "CAMERA"),
            ("model", "🧠", "MODEL"),
        ]
        
        for key, icon, label in indicator_data:
            indicator = StatusIndicator(icon, label)
            self.indicators[key] = indicator
            layout.addWidget(indicator)
        
        layout.addStretch()
        
        self.setStyleSheet(f"""
            BottomBar {{
                background-color: {hex_to_rgba(CATPILOT_BG_SECONDARY, 0.9)};
                border-top: 1px solid {hex_to_rgba(CATPILOT_CYAN, 0.3)};
            }}
        """)
    
    def update_indicator(self, key, value, color=None):
        if key in self.indicators:
            self.indicators[key].set_value(value, color)


class CatPilotUI(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.init_messaging()
        self.start_update_timer()
    
    def init_ui(self):
        self.setObjectName("catpilot_main")
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        self.top_bar = TopBar()
        main_layout.addWidget(self.top_bar)
        
        center_widget = QWidget()
        center_layout = QVBoxLayout(center_widget)
        center_layout.setContentsMargins(40, 20, 40, 20)
        center_layout.setSpacing(20)
        
        self.engagement_status = EngagementStatus()
        status_container = QHBoxLayout()
        status_container.addStretch()
        status_container.addWidget(self.engagement_status)
        status_container.addStretch()
        center_layout.addLayout(status_container)
        
        speed_container = QHBoxLayout()
        speed_container.addStretch()
        self.speed_display = SpeedDisplay()
        speed_container.addWidget(self.speed_display)
        speed_container.addStretch()
        center_layout.addLayout(speed_container)
        
        center_layout.addStretch()
        
        alert_container = QHBoxLayout()
        alert_container.addStretch()
        self.alert_banner = AlertBanner()
        self.alert_banner.setMinimumWidth(600)
        self.alert_banner.setMaximumWidth(800)
        alert_container.addWidget(self.alert_banner)
        alert_container.addStretch()
        center_layout.addLayout(alert_container)
        
        center_layout.addStretch()
        
        main_layout.addWidget(center_widget, 1)
        
        self.bottom_bar = BottomBar()
        main_layout.addWidget(self.bottom_bar)
        
        self.setStyleSheet(f"""
            #catpilot_main {{
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 {CATPILOT_BG},
                    stop: 0.5 {CATPILOT_BG_TERTIARY},
                    stop: 1 {CATPILOT_BG}
                );
            }}
            QLabel {{
                background-color: transparent;
            }}
        """)
    
    def init_messaging(self):
        self.sm = messaging.SubMaster([
            'deviceState', 
            'controlsState', 
            'carState',
            'pandaStates',
            'liveLocationKalman'
        ])
    
    def start_update_timer(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(50)
        
        self.time_timer = QTimer()
        self.time_timer.timeout.connect(self.top_bar.update_time)
        self.time_timer.start(1000)
        self.top_bar.update_time()
    
    def update(self):
        self.sm.update(0)
        
        onroad = self.sm.all_checks(['deviceState']) and self.sm['deviceState'].started
        
        if onroad:
            cs = self.sm['controlsState']
            car = self.sm['carState'] if self.sm.valid['carState'] else None
            
            self.engagement_status.set_status(
                str(cs.state),
                cs.enabled,
                cs.engageable
            )
            
            if car:
                speed_ms = car.vEgo
                speed_mph = speed_ms * 2.237
                self.speed_display.set_speed(speed_mph, is_metric=False)
            
            if cs.alertText1:
                alert_type = "info"
                if "warning" in cs.alertText1.lower() or "caution" in cs.alertText1.lower():
                    alert_type = "warning"
                elif "danger" in cs.alertText1.lower() or "brake" in cs.alertText1.lower():
                    alert_type = "critical"
                
                self.alert_banner.set_alert(cs.alertText1, cs.alertText2, alert_type)
            else:
                self.alert_banner.set_alert("")
            
            if not self.sm.alive['controlsState']:
                self.alert_banner.set_alert(
                    "Waiting for controls...",
                    "CatPilot is initializing",
                    "info"
                )
            
            ds = self.sm['deviceState'] if self.sm.valid['deviceState'] else None
            if ds:
                self.top_bar.update_temp(ds.cpuTempC[0] if ds.cpuTempC else 0)
            
            self.bottom_bar.update_indicator("gps", "✓", CATPILOT_SUCCESS)
            self.bottom_bar.update_indicator("panda", "✓", CATPILOT_SUCCESS)
            self.bottom_bar.update_indicator("camera", "✓", CATPILOT_SUCCESS)
            self.bottom_bar.update_indicator("model", "✓", CATPILOT_SUCCESS)
        else:
            self.speed_display.set_speed(0)
            self.engagement_status.set_status("", False, True)
            self.alert_banner.set_alert(
                "Vehicle Off",
                "Start the vehicle to engage CatPilot",
                "info"
            )
            
            self.bottom_bar.update_indicator("gps", "—", CATPILOT_TEXT_SECONDARY)
            self.bottom_bar.update_indicator("panda", "—", CATPILOT_TEXT_SECONDARY)
            self.bottom_bar.update_indicator("camera", "—", CATPILOT_TEXT_SECONDARY)
            self.bottom_bar.update_indicator("model", "—", CATPILOT_TEXT_SECONDARY)
        
        HARDWARE.set_screen_brightness(100 if onroad else 40)
        
        try:
            os.system("echo 0 > /sys/class/backlight/panel0-backlight/bl_power 2>/dev/null")
        except:
            pass


def main():
    app = QApplication([])
    
    app.setStyle("Fusion")
    
    win = CatPilotUI()
    set_main_window(win)
    
    win.showFullScreen()
    
    app.exec_()


if __name__ == "__main__":
    main()
