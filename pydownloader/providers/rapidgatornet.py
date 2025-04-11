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
"""pydownloader providers rapidgatornet."""

import re
import requests

from dataclasses import dataclass
from pathlib import Path
from typing import Final

from .base import Provider
from .. import passwordstore


@dataclass
class RapidgatorNet(Provider):
    """Provider for rapidgator.net."""

    username: str
    password: str
    otp: str | None
    API_URL: Final[str] = "https://rapidgator.net/api/v2/"
    PATTERN: Final[str] = r"https?://rapidgator\.net/file/(?P<id>\w+)/[\w\.\-_]+\.html"

    def _login(self) -> str:
        """Login and obtain a token."""
        r = requests.post(
            f"{self.API_URL}user/login",
            json={
                "login": self.username,
                "password": (
                    passwordstore.get_password(self.password[5:])
                    if self.password.startswith("pass:")
                    else self.password
                ),
            }
            | (
                {}
                if self.otp is None
                else {
                    "code": (
                        passwordstore.get_otp(self.otp[5:])
                        if self.otp.startswith("pass:")
                        else self.otp
                    ),
                }
            ),
        )
        r.raise_for_status()
        return r.json()["response"]["token"]

    def _file_info(self, token: str, file_id: str) -> dict:
        """Get file info."""
        r = requests.post(
            f"{self.API_URL}file/info",
            json={"token": token, "file_id": file_id},
        )
        r.raise_for_status()
        return r.json()

    def _file_download(self, token: str, file_id: str) -> str:
        """Get download URL."""
        r = requests.post(
            f"{self.API_URL}file/download",
            json={"token": token, "file_id": file_id},
        )
        r.raise_for_status()
        return r.json()["response"]["download_url"]

    def download(self, url: str, target_dir: Path, name: str | None = None) -> None:
        """Download a file."""
        groups = self.match(url)
        if groups is None:
            raise ValueError(f"Pattern din't match URL {url}.")
        token = self._login()
        name = self._file_info(token, groups["id"])["response"]["file"]["name"]
        return super().download(
            self._file_download(token, groups["id"]),
            target_dir,
            name,
        )

    def match(self, url: str) -> dict[str, str] | None:
        """Match a given URL."""
        m = re.fullmatch(self.PATTERN, url)
        if m is None:
            return None
        return m.groupdict()
