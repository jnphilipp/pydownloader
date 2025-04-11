# Copyright (C) 2025 J. Nathanael Philipp (jnphilipp) <nathanael@philipp.land>
#
# pydownloader
#
# This file is part of pydownloader.
#
# pydownloader is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pydownloader is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pydownloader. If not, see <http://www.gnu.org/licenses/>
"""pydownloader settings."""

import json

from dataclasses import dataclass, field
from pathlib import Path

from .providers import Provider, FikperCom, RapidgatorNet


@dataclass
class Settings:
    """Load settings from config file."""

    download_dir: Path
    use_provider_subdir: bool = True
    providers: dict[str, Provider] = field(default_factory=dict)

    @classmethod
    def from_file(cls, path: Path):
        """Load settings from file."""
        if not path.exists():
            return Settings(Path("~/Downloads").expanduser())
        with open(path, "r", encoding="utf8") as f:
            data = json.loads(f.read())

        providers: dict[str, Provider] = {}
        for k, v in data["providers"].items():
            if k == "fikper.com":
                providers[k] = FikperCom(api_key=v["api_key"])
            elif k == "rapidgator.net":
                providers[k] = RapidgatorNet(
                    username=v["username"],
                    password=v["password"],
                    otp=v["otp"],
                )

        return cls(
            download_dir=data.get("download_dir", Path("~/Downloads").expanduser()),
            use_provider_subdir=data.get("use_provider_subdir", True),
            providers=providers,
        )
