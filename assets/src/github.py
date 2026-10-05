"""Collect the numbers the cards show from the GitHub GraphQL API."""
import datetime as dt
import json
import time
import urllib.error
import urllib.request

API = "https://api.github.com/graphql"

LAST_YEAR = """
query($login: String!) {
  user(login: $login) {
    createdAt
    pullRequests(states: MERGED) { totalCount }
    contributionsCollection {
      totalCommitContributions
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount } }
      }
    }
  }
}
"""

ONE_YEAR = """
query($login: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $login) {
    contributionsCollection(from: $from, to: $to) {
      contributionCalendar {
        weeks { contributionDays { date contributionCount } }
      }
    }
  }
}
"""


def graphql(query, variables, token, attempts=3):
    body = json.dumps({"query": query, "variables": variables}).encode()
    headers = {"Authorization": f"bearer {token}", "Content-Type": "application/json", "User-Agent": "quartz-code-profile"}
    for attempt in range(attempts):
        try:
            with urllib.request.urlopen(urllib.request.Request(API, body, headers), timeout=30) as resp:
                payload = json.load(resp)
            if payload.get("errors") or not (payload.get("data") or {}).get("user"):
                raise RuntimeError(f"GraphQL error: {payload.get('errors') or payload}")
            return payload["data"]["user"]
        except (urllib.error.URLError, TimeoutError, RuntimeError):
            if attempt == attempts - 1:
                raise
            time.sleep(10 * (attempt + 1))


def calendar_days(calendar):
    return {d["date"]: d["contributionCount"] for w in calendar["weeks"] for d in w["contributionDays"]}


def longest_streak(days):
    """Longest run of consecutive days with at least one contribution."""
    best = run = 0
    prev = None
    for date in sorted(days):
        day = dt.date.fromisoformat(date)
        if days[date] == 0:
            run = 0
        elif run and prev is not None and day - prev == dt.timedelta(days=1):
            run += 1
        else:
            run = 1
        best = max(best, run)
        prev = day
    return best


def fetch(login, token, now=None):
    now = now or dt.datetime.now(dt.timezone.utc)
    user = graphql(LAST_YEAR, {"login": login}, token)
    contributions = user["contributionsCollection"]
    calendar = contributions["contributionCalendar"]
    since = dt.date.fromisoformat(user["createdAt"][:10])

    days = calendar_days(calendar)                    # whole history, one calendar year per request
    for year in range(since.year, now.year + 1):
        end = now if year == now.year else dt.datetime(year, 12, 31, 23, 59, 59, tzinfo=dt.timezone.utc)
        span = {"login": login, "from": f"{year}-01-01T00:00:00Z", "to": end.strftime("%Y-%m-%dT%H:%M:%SZ")}
        days.update(calendar_days(graphql(ONE_YEAR, span, token)["contributionsCollection"]["contributionCalendar"]))

    return {
        "since": since.year,
        "year_total": calendar["totalContributions"],
        "commits_year": contributions["totalCommitContributions"],
        "prs_merged": user["pullRequests"]["totalCount"],
        "streak_longest": longest_streak(days),
        "weeks": [{"start": w["contributionDays"][0]["date"], "count": sum(d["contributionCount"] for d in w["contributionDays"])}
                  for w in calendar["weeks"] if w["contributionDays"]],
    }
