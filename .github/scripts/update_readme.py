"""Refresh the dynamic sections of the profile README from the GitHub API."""

import json
import os
import re
import urllib.request
from datetime import date, timedelta

import cards

USER = "dasmig"
README = "README.md"
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


def graphql(query):
    request = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": query}).encode(),
        headers={
            "Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}",
            "User-Agent": f"{USER}-profile-readme",
        },
    )
    with urllib.request.urlopen(request) as response:
        return json.load(response)["data"]


def contribution_days():
    """Daily contribution counts for the past year, oldest first."""
    data = graphql(
        'query { user(login: "%s") { contributionsCollection { contributionCalendar {'
        " weeks { contributionDays { date contributionCount } } } } } }" % USER
    )
    weeks = data["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
    return [(d["date"], d["contributionCount"]) for w in weeks for d in w["contributionDays"]]


def streaks(days):
    today = date.today().isoformat()
    counts = [c for d, c in days if d <= today]
    longest = run = 0
    for c in counts:
        run = run + 1 if c else 0
        longest = max(longest, run)
    # Today may not have contributions yet without breaking the streak.
    if counts and not counts[-1]:
        counts = counts[:-1]
    current = 0
    for c in reversed(counts):
        if not c:
            break
        current += 1
    return current, longest


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
    followers = api(f"/users/{USER}")["followers"]
    cards.write(
        "stats.svg",
        cards.tiles(
            "// open source",
            [(len(repos), "repositories"), (stars, "stars"), (followers, "followers")],
        ),
    )

    days = contribution_days()
    current, longest = streaks(days)
    cards.write(
        "streak.svg",
        cards.tiles(
            "// contributions, past year",
            [(sum(c for _, c in days), "total"), (current, "current streak"), (longest, "longest streak")],
            accent="#8b7bff",
        ),
    )

    stats = '<img src="assets/stats.svg" alt="Repositories, stars and followers" width="600">'

    with open(README, encoding="utf-8") as f:
        text = f.read()
    text = replace(text, "STATS", stats)
    with open(README, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


if __name__ == "__main__":
    main()
