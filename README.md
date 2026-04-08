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

The easiest way is with [pipx](https://pipx.pypa.io) for mac homebrew users, which handles all the Python environment setup automatically. pip also works if you use that instead.

```bash
pipx install igdl==0.1.0
```

If that didn't work, try this non PyPi install:

```bash
# Install pipx if you don't have it
brew install pipx

# Install igdl
pipx install git+https://github.com/viviciu/igdl
```

**zsh users:** add this to `~/.zshrc` to prevent zsh from misreading `?` in URLs:

```bash
alias igdl='noglob igdl'
```

Then reload: `source ~/.zshrc`

### Manual install (without pipx)

<details>
<summary>Expand</summary>

```bash
git clone https://github.com/viviciu/igdl ~/igdl
cd ~/igdl
python3 -m venv .venv
.venv/bin/pip install -e .
mkdir -p ~/.local/bin
ln -sf ~/igdl/.venv/bin/igdl ~/.local/bin/igdl
```

Make sure `~/.local/bin` is in your PATH (`export PATH="$PATH:$HOME/.local/bin"` in `~/.zshrc`), then add the `noglob` alias above.

</details>

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

---

# Why do we install this way? How does install work?

This section answers various questions I had along the way, to inform me about why certain dev decisions were made and in which scenarios I'd want to execute them again.

## Is a venv created every time you use the tool?

  No — it's created once when you install, and just sits at ~/igdl/.venv/
  permanently. Every time you run igdl, it uses that same existing environment.
  Nothing is recreated.
  
  ## Do most distributed CLI tools use a venv?

  No. The more common approaches for tools meant to be shared are:

  - pipx — the actual standard for Python CLI tools. It automatically creates an
   isolated environment per tool behind the scenes, so the user never thinks
  about it. pipx install igdl and you're done.
  - brew — macOS users expect brew install sometool. Homebrew handles isolation
  itself.
  - A single script — if the tool has no dependencies or uses only stdlib, just
  ship one .py file.

  Venvs are really a development tool, not a distribution mechanism. The way we
  set it up is fine for personal use, but if you were seriously publishing this
  for others, you'd set it up for pipx instead.
  
  
  ## We can't use a single script to run our CLI because we are using external dependencies.
 Instaloader is an external dependency so a
  single script won't work on its own. You'd need the user to have it
  pre-installed, which isn't a great experience.

  Where dependencies are declared: ~/igdl/pyproject.toml — the dependencies =
  ["instaloader"] line. That's the one source of truth. When pip installs the
  package, it reads that file and pulls instaloader in automatically.

  ---
  Every file/folder in ~/igdl/:

  ~/igdl/
  ├── pyproject.toml        # Package metadata: name, version, dependencies,
  │                         # and which function to run when you type `igdl`
  ├── README.md             # Documentation (what you're editing)
  ├── .gitignore            # Tells git which files/folders to never commit
  │
  ├── igdl/                 # The actual Python source code
  │   ├── __init__.py       # Makes this folder a Python package (can be empty)
  │   ├── cli.py            # Parses what you type and routes to the right action
  │   ├── config.py         # Reads/writes ~/.igdl/config.json
  │   └── downloader.py     # All the Instagram download logic
  │
  ├── igdl.egg-info/        # ← Auto-generated by pip when you ran `pip install -e .`
  │                         # Bookkeeping metadata pip uses to track the install.
  │                         # You never touch it, git ignores it, safe to delete
  │                         # (it regenerates itself next time you install)
  │
  └── .venv/                # Your isolated Python environment — Python itself,
                            pip, and instaloader all live here. Never committed.

  ## What is `egg-info`? pip's 'notes to self'
  
  egg-info is just pip's scratch notes about your local install. The name comes
  from an old Python packaging format called "eggs" that predates the current
  standard — the name stuck even though eggs themselves are gone.
  
  ## Whats `__pycache__`? Optimization.
   
  __init__.py doesn't create __pycache__ — Python itself does. Any time Python
  runs a .py file, it compiles it to bytecode (a faster, pre-parsed version) and
   caches it in __pycache__/. This happens automatically for every .py file that
   gets imported. It's just a performance optimization — Python skips re-parsing
   files it's already seen.

  ---
  ## Do the Python files communicate with each other?

  Yes, through import. Look at the top of `cli.py`:

  `from .config import get_download_dir, set_download_dir`
  `from .downloader import download, login`

  The . means "from this same package." So when you run igdl, Python loads
  `cli.py`, which pulls in specific functions from config.py and downloader.py.
  They don't run in parallel or send messages — it's more like **cli.py is in
  charge and borrows tools from the other files when it needs them.**

  The flow when you run igdl <url>:

  cli.py          ← entry point, reads your command
    → config.py   ← "what's the download directory?"
    → downloader.py ← "go download this URL"
      → instaloader ← (external library, lives in .venv)

## What's `__init__.py`?
  __init__.py just tells Python "this folder is a package, treat the files
  inside as importable modules." **Without it, the from .config import ... lines
  in cli.py wouldn't work.** It's essentially a flag file.
