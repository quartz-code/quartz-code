"""Draw the profile cards (dark + light) into ../

    pip install -r requirements.txt
    python build.py           # draw from ../data.json
    python build.py --fetch   # refresh ../data.json from GitHub first (needs GITHUB_TOKEN)

Text is converted to outlines, so the cards look the same everywhere (GitHub
shows them as <img>, where web fonts don't load). Fonts come from Google Fonts
and are cached in ./fonts; logos are from simple-icons (CC0).
"""
import argparse
import json
import os

import cards
import github
from theme import HERE, THEMES

OUT = HERE.parent
DATA = OUT / "data.json"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--fetch", action="store_true", help="refresh data.json from the GitHub API first")
    args = parser.parse_args()
    if args.fetch:
        login = os.environ.get("GITHUB_REPOSITORY_OWNER", "quartz-code")
        data = github.fetch(login, os.environ["GITHUB_TOKEN"])
        DATA.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    data = json.loads(DATA.read_text(encoding="utf-8"))
    for name, theme in THEMES.items():
        for card, svg in (("hero", cards.hero(theme)), ("passport", cards.passport(theme, data)),
                          ("stack", cards.stack(theme)), ("druse", cards.druse(theme, data))):
            path = OUT / f"{card}-{name}.svg"
            path.write_text(svg, encoding="utf-8")
            print(f"{path.relative_to(OUT.parent)}  {len(svg) // 1024} KB")


if __name__ == "__main__":
    main()
