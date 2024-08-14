################################################################################
"""
WordWall - Simple, Self-Hosted Collaborative Word Cloud Generator.

(c) 2024 | Stanley Solutions | Joe Stanley
License: MIT
"""
################################################################################

import os
from pathlib import Path

from simple_toml_configurator import Configuration

CONFIG_FILE_PATH = Path(os.getenv("CONFIG_FILE", "./config/app.conf"))

DEFAULT_CONFIGURATION = {
    "application": {
        "site_url": "",
        "site_name": "WordWall",
        "cross_site_origins": [],
        "storage_path": "",
    },
}

# pylint: disable=no-member
class ConfigurationSettings(Configuration):
    """Base Configuration Data for Application."""

    @property
    def recordings_file_path(self) -> Path:
        """Evaluate the Correct Path, and Confirm that it Exists."""


settings = ConfigurationSettings()
settings.init_config(
    config_path=CONFIG_FILE_PATH,
    defaults=DEFAULT_CONFIGURATION,
    config_file_name="app"
)
