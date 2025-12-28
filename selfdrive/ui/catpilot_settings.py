#!/usr/bin/env python3
"""
CatPilot Settings UI
A settings panel matching The Pound's design for the on-device interface.
"""
import os
import signal
from pathlib import Path

signal.signal(signal.SIGINT, signal.SIG_DFL)

from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QSize
from PyQt5.QtWidgets import (
    QLabel, QWidget, QVBoxLayout, QHBoxLayout, QScrollArea,
    QApplication, QFrame, QPushButton, QStackedWidget
)
from PyQt5.QtGui import QFont, QColor, QIcon, QPixmap

import json

def hex_to_rgba(hex_color, alpha=1.0):
    """Convert hex color to rgba() CSS string."""
    hex_color = hex_color.lstrip('#')
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return f"rgba({r}, {g}, {b}, {alpha})"

def rgba_to_hex(color_dict):
    """Convert theme color dict {red, green, blue, alpha} to hex string."""
    if not color_dict:
        return None
    r = color_dict.get('red', 0)
    g = color_dict.get('green', 0)
    b = color_dict.get('blue', 0)
    return f"#{r:02x}{g:02x}{b:02x}"

def load_theme_colors():
    """Load colors from active theme or fall back to stock theme."""
    assets_path = Path(__file__).parent.parent.parent / "catpilot" / "assets"
    colors_file = assets_path / "active_theme" / "colors" / "colors.json"
    if not colors_file.exists():
        colors_file = assets_path / "stock_theme" / "colors" / "colors.json"
    
    if colors_file.exists():
        try:
            with open(colors_file) as f:
                return json.load(f)
        except:
            pass
    return {}

def get_theme_palette():
    """
    Get color palette from theme with fallbacks.
    
    Theme JSON colors mapped to UI:
    - Path → cyan (primary accent)
    - PathEdge → cyan_dark (accent dark variant)
    - Sidebar1 → text (primary text color)
    - Sidebar2 → text_secondary (secondary text)
    - LeadMarker → danger (alert/danger color)
    """
    theme = load_theme_colors()
    path_color = rgba_to_hex(theme.get('Path'))
    path_edge = rgba_to_hex(theme.get('PathEdge'))
    sidebar1 = rgba_to_hex(theme.get('Sidebar1'))
    sidebar2 = rgba_to_hex(theme.get('Sidebar2'))
    lead_marker = rgba_to_hex(theme.get('LeadMarker'))
    
    return {
        'cyan': path_color or "#00bcd4",
        'cyan_dark': path_edge or "#00838f",
        'bg': "#0a0a0a",
        'bg_secondary': "#1a1a1a",
        'bg_tertiary': "#252525",
        'text': sidebar1 or "#ffffff",
        'text_secondary': sidebar2 or "#b0bec5",
        'danger': lead_marker or "#f44336",
    }

THEME = get_theme_palette()
CATPILOT_CYAN = THEME['cyan']
CATPILOT_CYAN_DARK = THEME['cyan_dark']
CATPILOT_BG = THEME['bg']
CATPILOT_BG_SECONDARY = THEME['bg_secondary']
CATPILOT_BG_TERTIARY = THEME['bg_tertiary']
CATPILOT_TEXT = THEME['text']
CATPILOT_TEXT_SECONDARY = THEME['text_secondary']
CATPILOT_BORDER = hex_to_rgba(CATPILOT_CYAN, 0.3)

TOGGLE_ICONS_PATH = Path(__file__).parent.parent.parent / "catpilot" / "assets" / "toggle_icons"


class SettingsCategory:
    def __init__(self, id, title, icon, description=""):
        self.id = id
        self.title = title
        self.icon = icon
        self.description = description


SETTINGS_CATEGORIES = [
    SettingsCategory("device", "Device", "🐱", "Device settings and status"),
    SettingsCategory("display", "Display", "🖥️", "Screen and visual settings"),
    SettingsCategory("controls", "Controls", "🎮", "Driving control settings"),
    SettingsCategory("navigation", "Navigation", "🗺️", "Navigation preferences"),
    SettingsCategory("sounds", "Sounds", "🔊", "Alert and notification sounds"),
    SettingsCategory("themes", "Themes", "🎨", "Customize appearance"),
    SettingsCategory("advanced", "Advanced", "⚙️", "Advanced settings"),
    SettingsCategory("about", "About", "ℹ️", "Version and system info"),
]


class ToggleSwitch(QFrame):
    toggled = pyqtSignal(bool)
    
    def __init__(self, initial_state=False, parent=None):
        super().__init__(parent)
        self._checked = initial_state
        self.setFixedSize(60, 32)
        self._update_style()
        self.setCursor(Qt.PointingHandCursor)
    
    def _update_style(self):
        if self._checked:
            self.setStyleSheet(f"""
                ToggleSwitch {{
                    background-color: {CATPILOT_CYAN};
                    border-radius: 16px;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                ToggleSwitch {{
                    background-color: {CATPILOT_BG_TERTIARY};
                    border-radius: 16px;
                    border: 2px solid {CATPILOT_TEXT_SECONDARY};
                }}
            """)
    
    def mousePressEvent(self, event):
        self._checked = not self._checked
        self._update_style()
        self.toggled.emit(self._checked)
    
    def isChecked(self):
        return self._checked
    
    def setChecked(self, checked):
        self._checked = checked
        self._update_style()


class SettingItem(QFrame):
    def __init__(self, title, description="", toggle=False, value="", parent=None):
        super().__init__(parent)
        self.setMinimumHeight(80)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(16)
        
        text_layout = QVBoxLayout()
        text_layout.setSpacing(4)
        
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet(f"""
            font-size: 18px;
            font-weight: 600;
            color: {CATPILOT_TEXT};
        """)
        text_layout.addWidget(self.title_label)
        
        if description:
            self.desc_label = QLabel(description)
            self.desc_label.setStyleSheet(f"""
                font-size: 14px;
                color: {CATPILOT_TEXT_SECONDARY};
            """)
            self.desc_label.setWordWrap(True)
            text_layout.addWidget(self.desc_label)
        
        layout.addLayout(text_layout, 1)
        
        if toggle:
            self.toggle = ToggleSwitch()
            layout.addWidget(self.toggle)
        elif value:
            self.value_label = QLabel(value)
            self.value_label.setStyleSheet(f"""
                font-size: 16px;
                color: {CATPILOT_CYAN};
                font-weight: 500;
            """)
            layout.addWidget(self.value_label)
            
            arrow = QLabel("›")
            arrow.setStyleSheet(f"""
                font-size: 24px;
                color: {CATPILOT_TEXT_SECONDARY};
            """)
            layout.addWidget(arrow)
        else:
            arrow = QLabel("›")
            arrow.setStyleSheet(f"""
                font-size: 24px;
                color: {CATPILOT_TEXT_SECONDARY};
            """)
            layout.addWidget(arrow)
        
        self.setStyleSheet(f"""
            SettingItem {{
                background-color: {CATPILOT_BG_SECONDARY};
                border-radius: 12px;
                border: 1px solid {CATPILOT_BORDER};
            }}
            SettingItem:hover {{
                background-color: {CATPILOT_BG_TERTIARY};
                border: 1px solid {CATPILOT_CYAN};
            }}
        """)
        self.setCursor(Qt.PointingHandCursor)


class CategoryButton(QPushButton):
    def __init__(self, category, parent=None):
        super().__init__(parent)
        self.category = category
        self.setFixedHeight(70)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(12)
        
        icon_label = QLabel(category.icon)
        icon_label.setStyleSheet("font-size: 28px;")
        icon_label.setFixedSize(40, 40)
        icon_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon_label)
        
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)
        
        title = QLabel(category.title)
        title.setStyleSheet(f"""
            font-size: 18px;
            font-weight: 600;
            color: {CATPILOT_TEXT};
        """)
        text_layout.addWidget(title)
        
        if category.description:
            desc = QLabel(category.description)
            desc.setStyleSheet(f"""
                font-size: 12px;
                color: {CATPILOT_TEXT_SECONDARY};
            """)
            text_layout.addWidget(desc)
        
        layout.addLayout(text_layout, 1)
        
        arrow = QLabel("›")
        arrow.setStyleSheet(f"""
            font-size: 24px;
            color: {CATPILOT_TEXT_SECONDARY};
        """)
        layout.addWidget(arrow)
        
        self.setStyleSheet(f"""
            CategoryButton {{
                background-color: {CATPILOT_BG_SECONDARY};
                border-radius: 12px;
                border: 1px solid {CATPILOT_BORDER};
                text-align: left;
            }}
            CategoryButton:hover {{
                background-color: {CATPILOT_BG_TERTIARY};
                border: 1px solid {CATPILOT_CYAN};
            }}
            CategoryButton:pressed {{
                background-color: {hex_to_rgba(CATPILOT_CYAN, 0.2)};
            }}
        """)
        self.setCursor(Qt.PointingHandCursor)


class SettingsHeader(QFrame):
    back_clicked = pyqtSignal()
    
    def __init__(self, title="Settings", show_back=False, parent=None):
        super().__init__(parent)
        self.setFixedHeight(60)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 8, 16, 8)
        layout.setSpacing(12)
        
        if show_back:
            back_btn = QPushButton("‹ Back")
            back_btn.setStyleSheet(f"""
                QPushButton {{
                    font-size: 16px;
                    font-weight: 500;
                    color: {CATPILOT_CYAN};
                    background: transparent;
                    border: none;
                    padding: 8px 16px;
                }}
                QPushButton:hover {{
                    color: {CATPILOT_TEXT};
                }}
            """)
            back_btn.setCursor(Qt.PointingHandCursor)
            back_btn.clicked.connect(self.back_clicked.emit)
            layout.addWidget(back_btn)
        
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet(f"""
            font-size: 22px;
            font-weight: 700;
            color: {CATPILOT_TEXT};
        """)
        self.title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title_label, 1)
        
        if show_back:
            spacer = QLabel("")
            spacer.setFixedWidth(80)
            layout.addWidget(spacer)
        
        self.setStyleSheet(f"""
            SettingsHeader {{
                background-color: {CATPILOT_BG_SECONDARY};
                border-bottom: 1px solid {CATPILOT_BORDER};
            }}
        """)
    
    def set_title(self, title):
        self.title_label.setText(title)


class MainSettingsPage(QWidget):
    category_selected = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        header = SettingsHeader("⚙️ CatPilot Settings")
        layout.addWidget(header)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(f"""
            QScrollArea {{
                background-color: {CATPILOT_BG};
                border: none;
            }}
            QScrollBar:vertical {{
                background-color: {CATPILOT_BG};
                width: 8px;
            }}
            QScrollBar::handle:vertical {{
                background-color: {CATPILOT_CYAN};
                border-radius: 4px;
            }}
        """)
        
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(16, 16, 16, 16)
        content_layout.setSpacing(12)
        
        for category in SETTINGS_CATEGORIES:
            btn = CategoryButton(category)
            btn.clicked.connect(lambda checked, c=category: self.category_selected.emit(c.id))
            content_layout.addWidget(btn)
        
        content_layout.addStretch()
        
        version_label = QLabel("CatPilot v0.9.8 • The Pound")
        version_label.setAlignment(Qt.AlignCenter)
        version_label.setStyleSheet(f"""
            font-size: 12px;
            color: {CATPILOT_TEXT_SECONDARY};
            padding: 20px;
        """)
        content_layout.addWidget(version_label)
        
        scroll.setWidget(content)
        layout.addWidget(scroll)


class DeviceSettingsPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        layout.addWidget(SettingItem(
            "Dongle ID",
            "Your unique device identifier",
            value="abc123..."
        ))
        
        layout.addWidget(SettingItem(
            "Software Update",
            "Check for CatPilot updates"
        ))
        
        layout.addWidget(SettingItem(
            "Wi-Fi Settings",
            "Manage network connections"
        ))
        
        layout.addWidget(SettingItem(
            "SSH Access",
            "Enable remote access for development",
            toggle=True
        ))
        
        layout.addWidget(SettingItem(
            "Upload Logs",
            "Automatically upload driving logs",
            toggle=True
        ))
        
        layout.addWidget(SettingItem(
            "Reset to Defaults",
            "Reset all settings to factory defaults"
        ))
        
        layout.addStretch()


class DisplaySettingsPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        layout.addWidget(SettingItem(
            "Screen Brightness",
            "Adjust display brightness",
            value="Auto"
        ))
        
        layout.addWidget(SettingItem(
            "Show Speed",
            "Display current speed on screen",
            toggle=True
        ))
        
        layout.addWidget(SettingItem(
            "Show Speed Limit",
            "Display detected speed limits",
            toggle=True
        ))
        
        layout.addWidget(SettingItem(
            "Show Lead Car Distance",
            "Display distance to car ahead",
            toggle=True
        ))
        
        layout.addWidget(SettingItem(
            "Driver Camera Preview",
            "Show driver monitoring camera feed",
            toggle=True
        ))
        
        layout.addWidget(SettingItem(
            "Wide Camera View",
            "Use wide-angle camera for driving view",
            toggle=True
        ))
        
        layout.addStretch()


class CatPilotSettings(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("catpilot_settings")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        self.header = SettingsHeader("Settings", show_back=False)
        self.header.back_clicked.connect(self.go_back)
        layout.addWidget(self.header)
        
        self.stack = QStackedWidget()
        
        self.main_page = MainSettingsPage()
        self.main_page.category_selected.connect(self.show_category)
        self.stack.addWidget(self.main_page)
        
        self.device_page = DeviceSettingsPage()
        self.stack.addWidget(self.device_page)
        
        self.display_page = DisplaySettingsPage()
        self.stack.addWidget(self.display_page)
        
        layout.addWidget(self.stack)
        
        self.setStyleSheet(f"""
            #catpilot_settings {{
                background-color: {CATPILOT_BG};
            }}
        """)
        
        self.current_category = None
    
    def show_category(self, category_id):
        self.current_category = category_id
        
        category = next((c for c in SETTINGS_CATEGORIES if c.id == category_id), None)
        if category:
            self.header = SettingsHeader(f"{category.icon} {category.title}", show_back=True)
            self.header.back_clicked.connect(self.go_back)
            self.layout().replaceWidget(self.layout().itemAt(0).widget(), self.header)
        
        if category_id == "device":
            self.stack.setCurrentWidget(self.device_page)
        elif category_id == "display":
            self.stack.setCurrentWidget(self.display_page)
    
    def go_back(self):
        self.stack.setCurrentWidget(self.main_page)
        self.header = SettingsHeader("⚙️ CatPilot Settings", show_back=False)
        self.layout().replaceWidget(self.layout().itemAt(0).widget(), self.header)
        self.current_category = None


def main():
    app = QApplication([])
    app.setStyle("Fusion")
    
    win = CatPilotSettings()
    win.resize(1080, 1920)
    win.show()
    
    app.exec_()


if __name__ == "__main__":
    main()
