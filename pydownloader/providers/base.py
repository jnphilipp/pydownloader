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
"""pydownloader providers base."""

import logging
import requests

from dataclasses import dataclass
from pathlib import Path


@dataclass
class Provider:
    """Base class for Providers."""

    def download(self, url: str, target_dir: Path, name: str | None = None) -> None:
        """Download the given URL to the target directory using the optional name."""
        if name is None:
            name = url.split("/")[-1]
        if not target_dir.exists():
            target_dir.mkdir()
        elif (target_dir / name).exists():
            raise RuntimeError("File already exists.")
        with requests.get(url, stream=True) as r:
            if r.status_code == requests.codes.ok:
                with open(target_dir / name, "wb") as f:
                    for chunk in r.iter_content(chunk_size=2**20):
                        f.write(chunk)
                logging.info("Downloaded successfully.")
        r.raise_for_status()

    def match(self, url: str) -> dict[str, str] | None:
        """Check wether this provider is a match for the given URL."""
        raise NotImplementedError()
