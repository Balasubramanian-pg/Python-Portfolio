The script has three real problems:

1. `TOKEN = "diddy"` is a placeholder, not a usable GitHub token.
2. `update_ref(last_commit)` can crash if every file in a batch fails and `last_commit` is `None`.
3. The request wrapper should show the actual GitHub error body cleanly.

Here is a fixed version.

```python
import os
import time
import base64
import sys
from pathlib import Path

import requests

# ================= CONFIG =================

OWNER = "Balasubramanian-pg"
REPO = "Digtinctive"
BRANCH = "main"
REPO_PREFIX = "2026"

LOCAL_DIR = r"C:\Users\balasubramanian.pg\OneDrive - DIGTINCTIVE India Private Limited\2026"

# Set this in your environment instead of hardcoding it:
# set GITHUB_TOKEN=your_real_token_here
TOKEN = os.environ.get("GITHUB_TOKEN", "").strip()

CHAIN_SIZE = 10  # set to 1 for true one-file-at-a-time behavior

API_ROOT = f"https://api.github.com/repos/{OWNER}/{REPO}"

session = requests.Session()

# ================= CORE =================

def gh(method, endpoint, **kwargs):
    if not TOKEN:
        raise RuntimeError(
            "Missing GITHUB_TOKEN environment variable. "
            "A placeholder token will not work."
        )

    url = f"{API_ROOT}/{endpoint.lstrip('/')}"
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    r = session.request(method, url, headers=headers, timeout=60, **kwargs)

    if not (200 <= r.status_code < 300):
        body = r.text.strip()
        raise RuntimeError(
            f"{method.upper()} {endpoint} failed "
            f"with {r.status_code}:\n{body}"
        )

    if r.text.strip():
        return r.json()
    return None


def head_sha():
    return gh("GET", f"/git/ref/heads/{BRANCH}")["object"]["sha"]


def tree_sha(commit_sha):
    return gh("GET", f"/git/commits/{commit_sha}")["tree"]["sha"]


def create_blob(content):
    b64 = base64.b64encode(content).decode("ascii")
    return gh("POST", "/git/blobs", json={
        "content": b64,
        "encoding": "base64"
    })["sha"]


def create_tree(base_tree, items):
    return gh("POST", "/git/trees", json={
        "base_tree": base_tree,
        "tree": items
    })["sha"]


def create_commit(parent, tree, message):
    return gh("POST", "/git/commits", json={
        "message": message,
        "parents": [parent],
        "tree": tree
    })["sha"]


def update_ref(commit):
    if not commit:
        raise RuntimeError("update_ref called with empty commit SHA")
    gh("PATCH", f"/git/refs/heads/{BRANCH}", json={
        "sha": commit
    })


# ================= FILES =================

def collect_files():
    files = []
    for root, dirs, names in os.walk(LOCAL_DIR):
        dirs[:] = [d for d in dirs if d not in {".git", "__pycache__", ".vs", ".idea", ".vscode", "node_modules"}]
        for n in names:
            p = Path(root) / n
            files.append(p)
    return files


def repo_path(p: Path):
    rel = p.relative_to(LOCAL_DIR)
    return REPO_PREFIX + "/" + "/".join(rel.parts)


# ================= MAIN =================

def main():
    files = collect_files()
    total = len(files)

    print(f"Total files: {total}")

    if total == 0:
        print("No files found.")
        return

    parent = head_sha()
    base_tree_sha = tree_sha(parent)

    start = time.time()
    committed_count = 0

    for i in range(0, total, CHAIN_SIZE):
        chunk = files[i:i + CHAIN_SIZE]

        current_parent = parent
        current_tree = base_tree_sha
        last_commit = None
        successes = 0

        print(f"\nProcessing batch {i // CHAIN_SIZE + 1}")

        for j, path in enumerate(chunk, 1):
            try:
                raw = path.read_bytes()
                blob = create_blob(raw)

                new_tree = create_tree(current_tree, [{
                    "path": repo_path(path),
                    "mode": "100644",
                    "type": "blob",
                    "sha": blob
                }])

                new_commit = create_commit(
                    current_parent,
                    new_tree,
                    f"{path.name}"
                )

                current_parent = new_commit
                current_tree = new_tree
                last_commit = new_commit
                successes += 1
                committed_count += 1

                print(f"  [{j}/{len(chunk)}] committed: {path.name}")

            except Exception as e:
                print(f"  FAILED: {path} -> {e}")

        if last_commit is None:
            print("  No successful commits in this batch, skipping branch update.")
            continue

        update_ref(last_commit)

        parent = last_commit
        base_tree_sha = current_tree

        elapsed = time.time() - start
        rate = committed_count / max(elapsed, 1)

        print(f"Batch pushed. Successes in batch: {successes}/{len(chunk)}")
        print(f"Progress: {committed_count}/{total} | {rate:.2f} files/sec")

        # Small pause helps avoid secondary throttling.
        time.sleep(0.5)

    print("\nDone.")


if __name__ == "__main__":
    main()
```

Set `CHAIN_SIZE = 1` if you want exactly one commit per file with no batching. The code above is now safe either way.
