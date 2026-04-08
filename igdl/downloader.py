import re
import sys
from pathlib import Path

import instaloader
from instaloader import LoginRequiredException, Post

SESSION_DIR = Path.home() / ".igdl"
SHORTCODE_RE = re.compile(r"instagram\.com/(?:p|reel|tv)/([A-Za-z0-9_-]+)")


def extract_shortcode(url: str) -> str:
    m = SHORTCODE_RE.search(url)
    if not m:
        print("Error: could not parse Instagram URL. Expected a /p/, /reel/, or /tv/ link.", file=sys.stderr)
        sys.exit(1)
    return m.group(1)


def _loader(username: str | None = None, download_dir: Path | None = None) -> instaloader.Instaloader:
    L = instaloader.Instaloader(
        download_video_thumbnails=False,
        save_metadata=False,
        download_geotags=False,
        download_comments=False,
        post_metadata_txt_pattern="",
        dirname_pattern=str(download_dir) if download_dir else "{target}",
    )
    if username:
        session_file = SESSION_DIR / f"session_{username}"
        if session_file.exists():
            L.load_session_from_file(username, str(session_file))
    return L


def _saved_usernames() -> list[str]:
    return [
        f.name[len("session_"):]
        for f in SESSION_DIR.iterdir()
        if f.name.startswith("session_")
    ]


def download(url: str, download_dir: Path) -> None:
    shortcode = extract_shortcode(url)

    # Try with a saved session first, fall back to anonymous
    usernames = _saved_usernames()
    L = _loader(usernames[0] if usernames else None, download_dir=download_dir)

    try:
        post = Post.from_shortcode(L.context, shortcode)
        print(f"Downloading post by @{post.owner_username} to {download_dir}/")
        L.download_post(post, target=shortcode)
        print("Done.")
    except LoginRequiredException:
        print(
            "Error: Instagram requires a login to download this post.\n"
            "Run `igdl login` to save your session, then try again.",
            file=sys.stderr,
        )
        sys.exit(1)
    except instaloader.exceptions.InstaloaderException as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def login(username: str) -> None:
    L = instaloader.Instaloader()
    import getpass
    password = getpass.getpass(f"Instagram password for {username}: ")
    try:
        L.login(username, password)
        SESSION_DIR.mkdir(parents=True, exist_ok=True)
        session_file = str(SESSION_DIR / f"session_{username}")
        L.save_session_to_file(session_file)
        print(f"Session saved. You can now download private/rate-limited posts.")
    except instaloader.exceptions.BadCredentialsException:
        print("Error: incorrect username or password.", file=sys.stderr)
        sys.exit(1)
    except instaloader.exceptions.TwoFactorAuthRequiredException:
        code = input("Two-factor auth code: ")
        L.two_factor_login(code)
        session_file = str(SESSION_DIR / f"session_{username}")
        L.save_session_to_file(session_file)
        print("Session saved.")
