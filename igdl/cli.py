import argparse
import sys

from .config import get_download_dir, set_download_dir
from .downloader import download, login


def main() -> None:
    # Short-circuit URL detection before argparse sees it,
    # so subparsers don't conflict with bare URL arguments.
    if len(sys.argv) > 1 and sys.argv[1].startswith(("http://", "https://")):
        url = sys.argv[1]
        download_dir = get_download_dir()
        if not download_dir:
            print(
                "No download directory configured.\n"
                "Run: igdl config --dir ~/path/to/folder",
                file=sys.stderr,
            )
            sys.exit(1)
        download(url, download_dir)
        return

    parser = argparse.ArgumentParser(
        prog="igdl",
        description="Download images/videos from an Instagram post.",
        epilog="Usage: igdl <url>",
    )
    subparsers = parser.add_subparsers(dest="command")

    config_parser = subparsers.add_parser("config", help="Set configuration options")
    config_parser.add_argument("--dir", metavar="PATH", help="Set the download directory")

    login_parser = subparsers.add_parser("login", help="Save an Instagram session to bypass rate limits")
    login_parser.add_argument("username", help="Your Instagram username")

    args = parser.parse_args()

    if args.command == "config":
        if args.dir:
            resolved = set_download_dir(args.dir)
            print(f"Download directory set to: {resolved}")
        else:
            d = get_download_dir()
            if d:
                print(f"Download directory: {d}")
            else:
                print("No download directory set. Use: igdl config --dir <path>")
        return

    if args.command == "login":
        login(args.username)
        return

    parser.print_help()
