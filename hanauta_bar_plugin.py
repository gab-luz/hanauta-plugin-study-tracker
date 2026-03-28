#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

SERVICE_KEY = "study_tracker_widget"
PROCESS_ATTR = "_plugin_study_tracker_popup_process"


def register_hanauta_bar_plugin(bar, api: dict[str, object]) -> None:
    plugin_dir = Path(str(api.get("plugin_dir", ""))).expanduser()
    popup_path = plugin_dir / "study_tracker_popup.py"
    if not popup_path.exists():
        return

    material_icon = api["material_icon"]
    add_status_button = api["add_status_button"]
    toggle_singleton_process = api["toggle_singleton_process"]
    sync_popup_button = api["sync_popup_button"]
    load_service_settings = api["load_service_settings"]
    register_hook = api["register_hook"]
    apply_icon = api["apply_icon"]

    def on_click() -> None:
        active = bool(
            toggle_singleton_process(
                PROCESS_ATTR,
                popup_path,
                python_bin=bar._python_bin(),
            )
        )
        button.setChecked(active)

    button = add_status_button(
        "study_tracker_widget",
        material_icon("school"),
        tooltip="Study Tracker",
        checkable=True,
        on_click=on_click,
        font_size=16,
    )

    def sync_visibility() -> None:
        services = load_service_settings()
        service = services.get(SERVICE_KEY, {}) if isinstance(services, dict) else {}
        if not isinstance(service, dict):
            service = {}
        enabled = bool(service.get("enabled", False))
        show_in_bar = bool(service.get("show_in_bar", False))
        button.setVisible(enabled and show_in_bar)

    def sync_button() -> None:
        sync_popup_button(
            button,
            PROCESS_ATTR,
            popup_path,
            tooltip="Study Tracker",
        )

    def sync_icons() -> None:
        apply_icon(button, "school", material_icon("school"), 20)

    def on_close() -> None:
        process = getattr(bar, PROCESS_ATTR, None)
        if process is not None and process.poll() is None:
            process.terminate()

    register_hook("settings_reloaded", sync_visibility)
    register_hook("poll", sync_button)
    register_hook("icons", sync_icons)
    register_hook("close", on_close)

    sync_visibility()
    sync_icons()
    sync_button()
