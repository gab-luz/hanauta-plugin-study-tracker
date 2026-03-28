#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QCursor
from PyQt6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget

PLUGIN_ROOT = Path(__file__).resolve().parent
STUDY_TRACKER_POPUP = PLUGIN_ROOT / "study_tracker_popup.py"
SERVICE_KEY = "study_tracker_widget"


def _open_study_tracker(window, api: dict[str, object]) -> None:
    entry_command = api.get("entry_command")
    run_bg = api.get("run_bg")
    command: list[str] = []
    if callable(entry_command):
        try:
            command = list(entry_command(STUDY_TRACKER_POPUP))
        except Exception:
            command = []
    if not command:
        command = ["python3", str(STUDY_TRACKER_POPUP)]
    if callable(run_bg):
        try:
            run_bg(command)
        except Exception:
            pass
    status = getattr(window, "study_tracker_status", None)
    if isinstance(status, QLabel):
        status.setText("Study Tracker popup launched.")


def build_study_tracker_service_section(window, api: dict[str, object]) -> QWidget:
    SettingsRow = api["SettingsRow"]
    SwitchButton = api["SwitchButton"]
    ExpandableServiceSection = api["ExpandableServiceSection"]
    material_icon = api["material_icon"]
    icon_path = str(api.get("plugin_icon_path", "")).strip()

    service = window.settings_state.setdefault("services", {}).setdefault(
        SERVICE_KEY,
        {
            "enabled": False,
            "show_in_notification_center": True,
            "show_in_bar": False,
        },
    )

    content = QWidget()
    layout = QVBoxLayout(content)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(10)

    window.study_tracker_bar_switch = SwitchButton(bool(service.get("show_in_bar", False)))
    window.study_tracker_bar_switch.toggledValue.connect(
        lambda enabled: window._set_service_bar_visibility(SERVICE_KEY, enabled)
    )
    window.service_display_switches[SERVICE_KEY] = window.study_tracker_bar_switch
    layout.addWidget(
        SettingsRow(
            material_icon("widgets"),
            "Show on bar",
            "Display a Study Tracker icon in the bar that opens a live progress popup.",
            window.icon_font,
            window.ui_font,
            window.study_tracker_bar_switch,
        )
    )

    open_button = QPushButton("Open Study Tracker")
    open_button.setObjectName("secondaryButton")
    open_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
    open_button.clicked.connect(lambda: _open_study_tracker(window, api))
    layout.addWidget(
        SettingsRow(
            material_icon("open_in_new"),
            "Open full app",
            "Launches the Study Tracker popup from the installed plugin.",
            window.icon_font,
            window.ui_font,
            open_button,
        )
    )

    window.study_tracker_status = QLabel(
        "Disabled by default. Enable this service to expose the Study Tracker popup from plugin modules."
    )
    window.study_tracker_status.setWordWrap(True)
    window.study_tracker_status.setStyleSheet("color: rgba(246,235,247,0.72);")
    layout.addWidget(window.study_tracker_status)

    section = ExpandableServiceSection(
        SERVICE_KEY,
        "Study Tracker",
        "Plugin-powered study stats popup for the bar.",
        "?",
        window.icon_font,
        window.ui_font,
        content,
        window._service_enabled(SERVICE_KEY),
        lambda enabled: window._set_service_enabled(SERVICE_KEY, enabled),
        icon_path=icon_path,
    )
    window.service_sections[SERVICE_KEY] = section
    return section


def register_hanauta_plugin() -> dict[str, object]:
    return {
        "id": SERVICE_KEY,
        "name": "Study Tracker",
        "service_sections": [
            {
                "key": SERVICE_KEY,
                "builder": build_study_tracker_service_section,
            }
        ],
    }
