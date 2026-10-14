"""Post-deploy smoke test: every item defined in the repo exists in the target workspace."""
import argparse
import json
import pathlib
import sys

import requests
from azure.identity import AzureCliCredential

API = "https://api.fabric.microsoft.com/v1"


def repo_items(repo_dir: str) -> set[tuple[str, str]]:
    found = set()
    for p in pathlib.Path(repo_dir).rglob(".platform"):
        meta = json.loads(p.read_text(encoding="utf-8")).get("metadata", {})
        if meta.get("type") and meta.get("displayName"):
            found.add((meta["type"], meta["displayName"]))
    return found


def workspace_items(workspace_id: str, token: str) -> set[tuple[str, str]]:
    headers = {"Authorization": f"Bearer {token}"}
    url = f"{API}/workspaces/{workspace_id}/items"
    items: set[tuple[str, str]] = set()
    cont = None
    while True:
        r = requests.get(url, headers=headers, params={"continuationToken": cont} if cont else {}, timeout=60)
        r.raise_for_status()
        body = r.json()
        items |= {(i["type"], i["displayName"]) for i in body.get("value", [])}
        cont = body.get("continuationToken")
        if not cont:
            return items


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--workspace-id", required=True)
    p.add_argument("--repo-dir", default="workspace")
    args = p.parse_args()

    token = AzureCliCredential().get_token("https://api.fabric.microsoft.com/.default").token
    missing = repo_items(args.repo_dir) - workspace_items(args.workspace_id, token)
    for t, n in sorted(missing):
        print(f"SMOKE FAIL: {t} '{n}' is in the repo but not in the workspace")
    if not missing:
        print("Smoke test passed")
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())