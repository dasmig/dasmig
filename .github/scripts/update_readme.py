"""Refresh the dynamic sections of the profile README from the GitHub API."""

import json
import os
import re
import urllib.request
from datetime import datetime, timezone

USER = "dasmig"
README = "README.md"
RECENT_COUNT = 5
# Forks of other repos that are still maintained as my own project.
INCLUDED_FORKS = {"name-generator"}


def api(path):
    request = urllib.request.Request(
        f"https://api.github.com{path}",
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}",
            "User-Agent": f"{USER}-profile-readme",
        },
    )
    with urllib.request.urlopen(request) as response:
        return json.load(response)


def ago(timestamp):
    then = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    days = (datetime.now(timezone.utc) - then).days
    if days < 1:
        return "today"
    if days < 30:
        return f"{days}d ago"
    if days < 365:
        return f"{days // 30}mo ago"
    return f"{days // 365}y ago"


def replace(text, marker, body):
    pattern = re.compile(
        rf"(<!--{marker}:START-->).*?(<!--{marker}:END-->)", re.DOTALL
    )
    return pattern.sub(rf"\1\n{body}\n\2", text)


def main():
    repos = [
        r
        for r in api(f"/users/{USER}/repos?per_page=100&type=owner&sort=pushed")
        if (not r["fork"] or r["name"] in INCLUDED_FORKS)
        and not r["archived"]
        and r["name"] != USER
    ]

    stars = sum(r["stargazers_count"] for r in repos)
    stats = (
        f"![Repositories](https://img.shields.io/badge/repositories-{len(repos)}-42dca3?style=flat-square) "
        f"![Stars](https://img.shields.io/badge/stars-{stars}-42dca3?style=flat-square) "
        f"![Followers](https://img.shields.io/badge/followers-{api(f'/users/{USER}')['followers']}-42dca3?style=flat-square)"
    )

    rows = ["| Repository | Last push | |", "|---|---|---|"]
    for r in sorted(repos, key=lambda r: r["pushed_at"], reverse=True)[:RECENT_COUNT]:
        rows.append(
            f"| [**{r['name']}**]({r['html_url']}) | {ago(r['pushed_at'])} "
            f"| ![Stars](https://img.shields.io/github/stars/{USER}/{r['name']}?style=flat-square&color=42dca3) |"
        )

    with open(README, encoding="utf-8") as f:
        text = f.read()
    text = replace(text, "STATS", stats)
    text = replace(text, "RECENT", "\n".join(rows))
    with open(README, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


if __name__ == "__main__":
    main()
