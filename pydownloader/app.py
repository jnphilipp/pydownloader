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
"""pydownloader app."""

import logging
import sys

from argparse import (
    ArgumentDefaultsHelpFormatter,
    ArgumentParser,
    RawTextHelpFormatter,
)
from pathlib import Path
from xdg_base_dirs import xdg_config_home

from . import __app_name__, VERSION
from .settings import Settings

# from .api import transkribus_rest_api
# from .types import UploadPage


class ArgFormatter(ArgumentDefaultsHelpFormatter, RawTextHelpFormatter):
    """Combination of ArgumentDefaultsHelpFormatter and RawTextHelpFormatter."""

    pass


def filter_info(rec: logging.LogRecord) -> bool:
    """Log record filter for info and lower levels.

    Args:
     * rec: LogRecord object
    """
    return rec.levelno <= logging.INFO


def main():
    """Run the command line interface."""
    parser = ArgumentParser(prog=__app_name__, formatter_class=ArgFormatter)
    parser.add_argument("-V", "--version", action="version", version=VERSION)
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="verbosity level; multiple times increases the level, the maximum is 3, "
        + "for debugging.",
    )
    parser.add_argument(
        "--log-format",
        default="%(message)s",
        help="set logging format.",
    )
    parser.add_argument(
        "--log-file",
        type=lambda p: Path(p).absolute(),
        help="log output to a file.",
    )

    parser.add_argument(
        "-c",
        "--config-dir",
        type=lambda p: Path(p).absolute(),
        default=xdg_config_home() / __app_name__,
        help="path to config dir.",
    )
    parser.add_argument(
        "--download-dir",
        type=lambda p: Path(p).absolute(),
        help="download dir, overrides config.",
    )

    parser.add_argument("URLS", nargs="+", help="URLs to download.")

    args = parser.parse_args()

    if args.verbose == 0:
        level = logging.WARNING
    elif args.verbose == 1:
        level = logging.INFO
    else:
        level = logging.DEBUG

    handlers: list[logging.Handler] = []
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(level)
    stdout_handler.addFilter(filter_info)
    handlers.append(stdout_handler)

    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setLevel(logging.WARNING)
    if "%(levelname)s" not in args.log_format:
        stderr_handler.setFormatter(
            logging.Formatter(f"[%(levelname)s] {args.log_format}")
        )
    handlers.append(stderr_handler)

    if args.log_file:
        file_handler = logging.FileHandler(args.log_file)
        file_handler.setLevel(level)
        if args.log_file_format:
            file_handler.setFormatter(logging.Formatter(args.log_file_format))
        handlers.append(file_handler)

    logging.basicConfig(
        format=args.log_format,
        level=logging.DEBUG,
        handlers=handlers,
    )

    settings = Settings.from_file(args.config_dir / "config.json")
    download_dir = args.download_dir if args.download_dir else settings.download_dir
    for url in args.URLS:
        for k, provider in settings.providers.items():
            if provider.match(url) is not None:
                provider.download(
                    url,
                    (
                        (download_dir / k)
                        if settings.use_provider_subdir
                        else download_dir
                    ),
                )
