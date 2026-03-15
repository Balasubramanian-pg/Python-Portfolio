import requests
import time
from datetime import datetime
import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict

# Configuration
GITHUB_TOKEN = "diddyyyyyy"  # Generate at https://github.com/settings/tokens
REPO_OWNER = "Balasubramanian-pg"
REPO_NAME = "Flipcarbon"
BRANCH = "main"

HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

BASE_URL = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}"
PROGRESS_FILE = "migration_progress.json"
MAX_WORKERS = 5  # Parallel workers for API calls
BATCH_SIZE = 50  # Files per batch commit

class RateLimiter:
    """Smart rate limiting based on GitHub API headers."""
    
    def __init__(self):
        self.remaining = 5000
        self.reset_time = time.time()
    
    def update(self, response):
        """Update rate limit info from response headers."""
        self.remaining = int(response.headers.get('X-RateLimit-Remaining', self.remaining))
        self.reset_time = int(response.headers.get('X-RateLimit-Reset', self.reset_time))
    
    def wait_if_needed(self):
        """Sleep only if approaching rate limit."""
        if self.remaining < 100:
            sleep_time = max(0, self.reset_time - time.time() + 5)
            print(f"  ⏸️ Rate limit low ({self.remaining} left). Sleeping {sleep_time:.0f}s...")
            time.sleep(sleep_time)
            self.remaining = 5000  # Reset after waiting
        else:
            time.sleep(0.1)  # Minimal delay to be respectful

rate_limiter = RateLimiter()

def load_progress():
    """Load list of already-processed folders."""
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, 'r') as f:
            return json.load(f)
    return {"completed_folders": [], "skipped_files": [], "moved_files": []}

def save_progress(progress):
    """Save progress to file."""
    with open(PROGRESS_FILE, 'w') as f:
        json.dump(progress, f, indent=2)

def get_repo_tree():
    """Get entire repository file tree in one API call."""
    print("  🌳 Fetching entire repo tree...")
    url = f"{BASE_URL}/git/trees/{BRANCH}?recursive=1"
    response = requests.get(url, headers=HEADERS)
    rate_limiter.update(response)
    
    if response.status_code != 200:
        print(f"  ❌ Error fetching tree: {response.status_code}")
        return None
    
    tree_data = response.json()
    print(f"  ✅ Fetched {len(tree_data.get('tree', []))} items from repo")
    return tree_data.get('tree', [])

def get_top_level_folders(tree):
    """Extract top-level folders from tree, excluding year folders."""
    folders = set()
    for item in tree:
        if item['type'] == 'tree':
            top_folder = item['path'].split('/')[0]
            if top_folder not in ['2023', '2024', '2025', '.git', '.github']:
                folders.add(top_folder)
    return sorted(folders)

def get_files_in_folder(folder_name, tree):
    """Get all files in a specific folder from the tree."""
    files = []
    for item in tree:
        if item['type'] == 'blob' and item['path'].startswith(f"{folder_name}/"):
            files.append({
                'path': item['path'],
                'sha': item['sha'],
                'size': item.get('size', 0)
            })
    return files

def get_file_commit_year(file_path):
    """Get the year of the last commit for a file."""
    url = f"{BASE_URL}/commits"
    params = {"path": file_path, "per_page": 1}
    
    response = requests.get(url, headers=HEADERS, params=params)
    rate_limiter.update(response)
    
    if response.status_code != 200:
        return None
    
    commits = response.json()
    if not commits:
        return None
    
    commit_date = commits[0]["commit"]["committer"]["date"]
    year = datetime.fromisoformat(commit_date.replace("Z", "+00:00")).year
    return str(year)

def process_single_file(file_info):
    """Process a single file - get commit year and return move plan."""
    old_path = file_info['path']
    
    # Get commit year
    year = get_file_commit_year(old_path)
    rate_limiter.wait_if_needed()
    
    if year not in ["2023", "2024", "2025"]:
        return {
            'status': 'skipped',
            'path': old_path,
            'reason': f'year_{year}'
        }
    
    new_path = f"{year}/{old_path}"
    
    return {
        'status': 'move',
        'old_path': old_path,
        'new_path': new_path,
        'sha': file_info['sha'],
        'year': year
    }

def get_branch_sha():
    """Get the current SHA of the branch."""
    url = f"{BASE_URL}/git/refs/heads/{BRANCH}"
    response = requests.get(url, headers=HEADERS)
    rate_limiter.update(response)
    
    if response.status_code != 200:
        return None
    
    return response.json()['object']['sha']

def create_batch_commit(file_moves, commit_message):
    """Create a single commit that moves multiple files."""
    if not file_moves:
        return False
    
    # Get current commit SHA
    current_sha = get_branch_sha()
    if not current_sha:
        print("  ❌ Failed to get current branch SHA")
        return False
    
    # Get current commit to get tree SHA
    commit_url = f"{BASE_URL}/git/commits/{current_sha}"
    commit_response = requests.get(commit_url, headers=HEADERS)
    rate_limiter.update(commit_response)
    
    if commit_response.status_code != 200:
        print("  ❌ Failed to get current commit")
        return False
    
    base_tree_sha = commit_response.json()['tree']['sha']
    
    # Build tree changes
    tree_items = []
    for move in file_moves:
        # Add file at new location
        tree_items.append({
            "path": move['new_path'],
            "mode": "100644",
            "type": "blob",
            "sha": move['sha']
        })
        # Remove file from old location
        tree_items.append({
            "path": move['old_path'],
            "mode": "100644",
            "type": "blob",
            "sha": None
        })
    
    # Create new tree
    tree_url = f"{BASE_URL}/git/trees"
    tree_data = {
        "base_tree": base_tree_sha,
        "tree": tree_items
    }
    tree_response = requests.post(tree_url, headers=HEADERS, json=tree_data)
    rate_limiter.update(tree_response)
    
    if tree_response.status_code != 201:
        print(f"  ❌ Failed to create tree: {tree_response.status_code}")
        return False
    
    new_tree_sha = tree_response.json()['sha']
    
    # Create commit
    commit_create_url = f"{BASE_URL}/git/commits"
    commit_data = {
        "message": commit_message,
        "tree": new_tree_sha,
        "parents": [current_sha]
    }
    new_commit_response = requests.post(commit_create_url, headers=HEADERS, json=commit_data)
    rate_limiter.update(new_commit_response)
    
    if new_commit_response.status_code != 201:
        print(f"  ❌ Failed to create commit: {new_commit_response.status_code}")
        return False
    
    new_commit_sha = new_commit_response.json()['sha']
    
    # Update branch reference
    ref_url = f"{BASE_URL}/git/refs/heads/{BRANCH}"
    ref_data = {"sha": new_commit_sha}
    ref_response = requests.patch(ref_url, headers=HEADERS, json=ref_data)
    rate_limiter.update(ref_response)
    
    if ref_response.status_code != 200:
        print(f"  ❌ Failed to update branch: {ref_response.status_code}")
        return False
    
    return True

def process_folder(folder_name, tree, progress):
    """Process a single folder with parallel processing and batch commits."""
    print(f"\n{'='*60}")
    print(f"📁 Processing folder: {folder_name}")
    print(f"{'='*60}")
    
    # Get all files in this folder from tree
    files = get_files_in_folder(folder_name, tree)
    print(f"  📋 Found {len(files)} files in {folder_name}/")
    
    if not files:
        print(f"  ✅ Folder is empty")
        return
    
    # Process files in parallel to get commit years
    print(f"  🔍 Checking commit dates (parallel, {MAX_WORKERS} workers)...")
    file_plans = []
    
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(process_single_file, file): file for file in files}
        
        for i, future in enumerate(as_completed(futures), 1):
            if i % 10 == 0:
                print(f"    Progress: {i}/{len(files)} files checked")
            
            try:
                result = future.result()
                file_plans.append(result)
            except Exception as e:
                file = futures[future]
                print(f"    ❌ Error processing {file['path']}: {e}")
                progress["skipped_files"].append({
                    "path": file['path'], 
                    "reason": f"error_{str(e)}"
                })
    
    # Separate moves from skips
    to_move = [p for p in file_plans if p['status'] == 'move']
    skipped = [p for p in file_plans if p['status'] == 'skipped']
    
    print(f"  ✅ Analysis complete: {len(to_move)} to move, {len(skipped)} to skip")
    
    # Track skipped files
    for skip in skipped:
        progress["skipped_files"].append({
            "path": skip['path'],
            "reason": skip['reason']
        })
    
    if not to_move:
        print(f"  ℹ️ No files to move in this folder")
        return
    
    # Group files by year for better commit messages
    by_year = defaultdict(list)
    for move in to_move:
        by_year[move['year']].append(move)
    
    # Process each year group in batches
    total_moved = 0
    for year, year_moves in by_year.items():
        print(f"\n  📅 Moving {len(year_moves)} files to {year}/")
        
        # Process in batches
        for batch_num in range(0, len(year_moves), BATCH_SIZE):
            batch = year_moves[batch_num:batch_num + BATCH_SIZE]
            batch_end = min(batch_num + BATCH_SIZE, len(year_moves))
            
            print(f"    Batch {batch_num//BATCH_SIZE + 1}: files {batch_num+1}-{batch_end}...", end=" ")
            
            commit_message = f"Move {len(batch)} files from {folder_name}/ to {year}/"
            success = create_batch_commit(batch, commit_message)
            
            if success:
                print(f"✅")
                total_moved += len(batch)
                for move in batch:
                    progress["moved_files"].append({
                        "from": move['old_path'],
                        "to": move['new_path']
                    })
            else:
                print(f"❌")
                for move in batch:
                    progress["skipped_files"].append({
                        "path": move['old_path'],
                        "reason": "batch_commit_failed"
                    })
            
            rate_limiter.wait_if_needed()
            
            # Save progress after each batch
            save_progress(progress)
    
    print(f"\n  ✅ Folder complete: {total_moved} files moved, {len(skipped)} skipped")
    progress["completed_folders"].append(folder_name)
    save_progress(progress)

def main():
    if GITHUB_TOKEN == "your_github_token_here":
        print("❌ Please set your GitHub token in the script!")
        print("Generate one at: https://github.com/settings/tokens")
        print("Required scopes: 'repo'")
        return
    
    print(f"🚀 OPTIMIZED GitHub Migration for {REPO_OWNER}/{REPO_NAME}")
    print(f"⚡ Features: Tree API, Parallel Processing, Batch Commits")
    print(f"📊 Progress saved to {PROGRESS_FILE}")
    print(f"⏸️ Stop anytime with Ctrl+C - safe to resume\n")
    
    # Load progress
    progress = load_progress()
    
    # Get entire repo tree (1 API call!)
    tree = get_repo_tree()
    if not tree:
        print("❌ Failed to fetch repository tree")
        return
    
    # Get top-level folders
    folders = get_top_level_folders(tree)
    print(f"\n📂 Found {len(folders)} top-level folders")
    
    # Filter out completed folders
    remaining_folders = [f for f in folders if f not in progress["completed_folders"]]
    
    if not remaining_folders:
        print("\n✅ All folders already processed!")
        print(f"Total files moved: {len(progress.get('moved_files', []))}")
        print(f"Total files skipped: {len(progress.get('skipped_files', []))}")
        return
    
    print(f"\n📋 Remaining: {len(remaining_folders)} folders")
    print(f"✅ Completed: {len(progress['completed_folders'])} folders")
    print(f"📦 Batch size: {BATCH_SIZE} files per commit")
    print(f"🔄 Workers: {MAX_WORKERS} parallel threads")
    
    input("\nPress Enter to start (or Ctrl+C to cancel)...")
    
    # Process each folder
    start_time = time.time()
    try:
        for i, folder in enumerate(remaining_folders, 1):
            print(f"\n[{i}/{len(remaining_folders)}] Starting: {folder}")
            process_folder(folder, tree, progress)
            
            elapsed = time.time() - start_time
            print(f"⏱️ Elapsed: {elapsed/60:.1f} minutes")
    
    except KeyboardInterrupt:
        print("\n\n⏸️ Stopped by user. Progress saved.")
        print(f"Resume by running script again.")
        save_progress(progress)
        return
    
    total_time = time.time() - start_time
    print("\n" + "="*60)
    print("🎉 MIGRATION COMPLETE!")
    print("="*60)
    print(f"✅ Folders processed: {len(progress['completed_folders'])}")
    print(f"📦 Files moved: {len(progress.get('moved_files', []))}")
    print(f"⚠️ Files skipped: {len(progress['skipped_files'])}")
    print(f"⏱️ Total time: {total_time/60:.1f} minutes")
    print(f"⚡ Speed: ~{len(progress.get('moved_files', []))/(total_time/60):.0f} files/minute")

if __name__ == "__main__":
    main()