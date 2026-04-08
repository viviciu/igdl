# igdl

A minimal CLI tool that downloads all images and videos from an Instagram post to a local folder. Paste a link, get the files.

- Supports posts, reels, carousels, and IGTV
- Downloads all slides in a carousel in one command
- Optional login to bypass Instagram rate limits
- Configurable download directory and file naming

---

## Requirements

- Python 3.8+
- macOS or Linux (Windows untested)

---

## Install

```bash
# 1. Clone the repo
git clone https://github.com/yourusername/igdl ~/igdl

# 2. Create a virtual environment and install
cd ~/igdl
python3 -m venv .venv
.venv/bin/pip install -e .

# 3. Symlink the binary so it's available everywhere
mkdir -p ~/.local/bin
ln -sf ~/igdl/.venv/bin/igdl ~/.local/bin/igdl
```

Make sure `~/.local/bin` is in your PATH. Add to `~/.zshrc` or `~/.bashrc` if needed:

```bash
export PATH="$PATH:$HOME/.local/bin"
```

**zsh users:** add this alias to prevent zsh from glob-expanding `?` in URLs:

```bash
alias igdl='noglob igdl'
```

Then reload your shell:

```bash
source ~/.zshrc
```

---

## Setup

Set your download directory once:

```bash
igdl config --dir ~/Downloads/Instagram
```

This saves to `~/.igdl/config.json`. Run `igdl config` with no flags to see the current setting.

---

## Usage

```bash
# Download a post (images, videos, or carousels)
igdl https://www.instagram.com/p/SHORTCODE/

# Reels and IGTV work too
igdl https://www.instagram.com/reel/SHORTCODE/
igdl https://www.instagram.com/tv/SHORTCODE/
```

Instagram rate-limits anonymous requests. Log in once to avoid this:

```bash
igdl login your_username
```

Your session is saved to `~/.igdl/session_<username>` and reused automatically on future downloads.

---

## Customizing file naming

Files are named using [instaloader's filename pattern](https://instaloader.github.io/module/instaloader.html#instaloader.Instaloader). The default is `{date_utc}_UTC` (e.g. `2026-04-08_11-09-53_UTC_1.jpg`).

To change it, edit `igdl/downloader.py` in the `_loader()` function and add a `filename_pattern` argument to the `Instaloader()` constructor:

```python
L = instaloader.Instaloader(
    filename_pattern="{owner_username}_{shortcode}",  # ← change this
    ...
)
```

Available variables:

| Variable | Example |
|---|---|
| `{date_utc}` | `2026-04-08_11-09-53` |
| `{shortcode}` | `DW3lV16CO5K` |
| `{owner_username}` | `folchstudio` |
| `{mediaid}` | `3612345678901234567` |
| `{typename}` | `GraphImage`, `GraphVideo` |

---

## Project structure

```
igdl/
  pyproject.toml       # package metadata and dependencies
  igdl/
    cli.py             # argument parsing and command routing
    config.py          # read/write ~/.igdl/config.json
    downloader.py      # instaloader wrapper — core download logic
    __init__.py
```

Runtime data (created automatically, not in the repo):

```
~/.igdl/
  config.json          # stores your configured download directory
  session_<username>   # saved Instagram session from igdl login
```

---

## Dependencies

- [instaloader](https://instaloader.github.io) — handles Instagram auth, carousels, and all media types
