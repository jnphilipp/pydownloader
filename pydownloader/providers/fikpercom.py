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
"""pydownloader providers fikpercom."""

import re
import requests

from dataclasses import dataclass
from pathlib import Path
from typing import Final

from .base import Provider


@dataclass
class FikperCom(Provider):
    """Provider for fikper.com."""

    api_key: str
    API_URL: Final[str] = "https://sapi.fikper.com/api/"
    PATTERN: Final[str] = r"https?://fikper\.com/(?P<id>\w+)/(?P<name>[\w\.\-_]+).html"

    def download(self, url: str, target_dir: Path, name: str | None = None) -> None:
        """Download a file from fikper.com."""
        groups = self.match(url)
        if groups is None:
            raise ValueError(f"Pattern din't match URL {url}.")

        r = requests.get(
            f"{self.API_URL}/file/download/{groups['id']}",
            headers={"x-api-key": self.api_key},
        )
        r.raise_for_status()
        return super().download(
            r.text,
            target_dir,
            name if name is not None else groups["name"],
        )

    def match(self, url: str) -> dict[str, str] | None:
        """Match a given URL."""
        m = re.fullmatch(self.PATTERN, url)
        if m is None:
            return None
        return m.groupdict()
