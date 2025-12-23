from ayon_server.settings import BaseSettingsModel, SettingsField


class RVIntegrationSettings(BaseSettingsModel):
    rv_executable_path: str = SettingsField(
        "",
        title="RV Executable Path",
        description="Path to RV executable (leave empty for auto-detection)"
    )
    auto_dock_activity_panel: bool = SettingsField(
        True,
        title="Auto-dock Activity Panel to RV"
    )


class FilterSettings(BaseSettingsModel):
    default_date_filter: str = SettingsField(
        "ALL",
        title="Default Date Filter",
        enum=["ALL", "TODAY", "YESTERDAY", "THIS_WEEK", "THIS_MONTH"]
    )
    persist_filters_per_project: bool = SettingsField(
        True,
        title="Persist Filters Per Project"
    )


class UISettings(BaseSettingsModel):
    thumbnail_size: int = SettingsField(
        100,
        title="Thumbnail Size (pixels)",
        ge=50,
        le=300
    )
    auto_refresh_interval: int = SettingsField(
        0,
        title="Auto-refresh Interval (seconds, 0=disabled)",
        ge=0
    )
    show_version_thumbnails: bool = SettingsField(
        True,
        title="Show Version Thumbnails"
    )


class ActivitySettings(BaseSettingsModel):
    max_activities_display: int = SettingsField(
        50,
        title="Max Activities to Display",
        ge=10,
        le=500
    )
    enable_activity_animations: bool = SettingsField(
        True,
        title="Enable Activity Animations"
    )


class ReviewBrowserSettings(BaseSettingsModel):
    enabled: bool = SettingsField(
        True,
        title="Enable Review Browser"
    )
    rv_integration: RVIntegrationSettings = SettingsField(
        default_factory=RVIntegrationSettings,
        title="RV Integration"
    )
    filters: FilterSettings = SettingsField(
        default_factory=FilterSettings,
        title="Filter Settings"
    )
    ui: UISettings = SettingsField(
        default_factory=UISettings,
        title="UI Settings"
    )
    activity: ActivitySettings = SettingsField(
        default_factory=ActivitySettings,
        title="Activity Panel Settings"
    )


DEFAULT_VALUES = {
    "enabled": True,
    "rv_integration": {
        "rv_executable_path": "",
        "auto_dock_activity_panel": True
    },
    "filters": {
        "default_date_filter": "ALL",
        "persist_filters_per_project": True
    },
    "ui": {
        "thumbnail_size": 100,
        "auto_refresh_interval": 0,
        "show_version_thumbnails": True
    },
    "activity": {
        "max_activities_display": 50,
        "enable_activity_animations": True
    }
}
