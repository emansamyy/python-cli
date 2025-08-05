#!/usr/bin/env python3

import argparse
import logging
import sys
import requests
import gzip
import io
from collections import defaultdict
from operator import itemgetter
from typing import Dict
import os

DEBIAN_MIRROR = "http://ftp.uk.debian.org/debian/dists/stable/main/"

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s"
)


class DownloadError(Exception):
    """Custom exception for download-related issues."""
    pass


def parse_arguments():
    """
    Parse command-line arguments.

    Returns:
        argparse.Namespace: Parsed arguments with 'arch' and 'top'.
    """
    parser = argparse.ArgumentParser(
        description="Analyze Debian package statistics from Contents files."
    )
    parser.add_argument(
        "arch",
        type=str,
        help="Architecture name (e.g., amd64, arm64, mips)"
    )
    parser.add_argument(
        "-n", "--top",
        type=int,
        default=10,
        help="Number of top packages to display (default: 10)"
    )
    parser.add_argument(
    "--mirror",
    type=str,
    default=os.getenv("DEBIAN_MIRROR"),
    help="Base URL of Debian mirror (or set DEBIAN_MIRROR env variable or use .env file)"
)
    return parser.parse_args()


def download_contents_file(arch: str, mirror_base: str) -> io.BytesIO:
    """
    Downloads and returns the Contents-ARCH.gz file as a BytesIO stream.

    Args:
        arch (str): Architecture name.
        mirror_base (str): Base URL of the Debian mirror.

    Returns:
        io.BytesIO: Gzipped file stream.

    Raises:
        DownloadError: If the file cannot be downloaded.
    """
    url = f"{mirror_base}Contents-{arch}.gz"
    logging.info(f"Downloading: {url}")

    try:
        response = requests.get(url, stream=True, timeout=10)
        response.raise_for_status()
        return io.BytesIO(response.content)
    except requests.HTTPError as e:
        raise DownloadError(f"HTTP error: {e}")
    except requests.RequestException as e:
        raise DownloadError(f"Network error: {e}")


def parse_contents_file(gzipped_file: io.BytesIO) -> Dict[str, int]:
    """
    Parses a Contents file and returns package -> file count mapping.

    Args:
        gzipped_file (io.BytesIO): Gzipped Debian Contents file.

    Returns:
        dict: Mapping of package names to number of files.
    """
    package_file_count = defaultdict(int)

    try:
        with gzip.open(gzipped_file, 'rt', encoding='utf-8', errors='ignore') as f:
            for line in f:
                parts = line.strip().rsplit(None, 1)
                if len(parts) != 2:
                    continue
                _, packages = parts
                for package in packages.split(','):
                    package_file_count[package] += 1
    except OSError as e:
        logging.error(f"Error reading gzip file: {e}")
        sys.exit(1)

    return package_file_count


def print_top_packages(package_file_count: Dict[str, int], top_n: int = 10):
    """
    Prints the top N packages with the most files.

    Args:
        package_file_count (dict): Mapping of package names to file count.
        top_n (int): Number of top packages to display.
    """
    sorted_packages = sorted(package_file_count.items(), key=itemgetter(1), reverse=True)
    logging.info(f"\nTop {top_n} packages by number of files:\n")
    for pkg, count in sorted_packages[:top_n]:
        print(f"{pkg:30} {count}")


def main():
    args = parse_arguments()
    arch = args.arch
    top_n = args.top

    try:
        gzipped_file = download_contents_file(arch, DEBIAN_MIRROR)
    except DownloadError as e:
        logging.error(str(e))
        sys.exit(1)

    package_file_count = parse_contents_file(gzipped_file)
    print_top_packages(package_file_count, top_n)


if __name__ == "__main__":
    main()
