import requests
import time
import json
import os
from collections import defaultdict

# Configuration
GITHUB_TOKEN = "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"
REPO_OWNER = "Balasubramanian-pg"
REPO_NAME = "Flipcarbon"
BRANCH = "main"

HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

BASE_URL = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}"

# Folder mappings: source → destination
FOLDER_MERGES = {
    "2. 2024": "2024",
    "3. 2025": "2025"
}

def get_repo_tree():
    """Get entire repository file tree."""
    print("🌳 Fetching repo tree...")
    url = f"{BASE_URL}/git/trees/{BRANCH}?recursive=1"
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code != 200:
        print(f"❌ Error: {response.status_code}")
        print(response.text)
        return None
    
    tree = response.json().get('tree', [])
    print(f"✅ Found {len(tree)} items\n")
    return tree

def get_files_in_folder(folder_name, tree):
    """Get all files in a specific folder."""
    files = []
    for item in tree:
        if item['type'] == 'blob' and item['path'].startswith(f"{folder_name}/"):
            files.append({
                'path': item['path'],
                'sha': item['sha']
            })
    return files

def get_branch_sha():
    """Get current branch SHA."""
    url = f"{BASE_URL}/git/refs/heads/{BRANCH}"
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code != 200:
        return None
    
    return response.json()['object']['sha']

def create_merge_commit(file_moves, commit_message):
    """Create a single commit that moves multiple files."""
    if not file_moves:
        return False
    
    # Get current commit
    current_sha = get_branch_sha()
    if not current_sha:
        print("❌ Failed to get branch SHA")
        return False
    
    commit_url = f"{BASE_URL}/git/commits/{current_sha}"
    commit_response = requests.get(commit_url, headers=HEADERS)
    
    if commit_response.status_code != 200:
        print("❌ Failed to get commit")
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
    
    if tree_response.status_code != 201:
        print(f"❌ Tree creation failed: {tree_response.status_code}")
        print(tree_response.text)
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
    
    if new_commit_response.status_code != 201:
        print(f"❌ Commit creation failed: {new_commit_response.status_code}")
        print(new_commit_response.text)
        return False
    
    new_commit_sha = new_commit_response.json()['sha']
    
    # Update branch
    ref_url = f"{BASE_URL}/git/refs/heads/{BRANCH}"
    ref_data = {"sha": new_commit_sha}
    ref_response = requests.patch(ref_url, headers=HEADERS, json=ref_data)
    
    if ref_response.status_code != 200:
        print(f"❌ Branch update failed: {ref_response.status_code}")
        print(ref_response.text)
        return False
    
    return True

def merge_folders(source_folder, target_folder, tree):
    """Merge all files from source folder into target folder."""
    print(f"\n{'='*60}")
    print(f"📂 Merging: {source_folder} → {target_folder}")
    print(f"{'='*60}")
    
    # Get files in source folder
    files = get_files_in_folder(source_folder, tree)
    
    if not files:
        print(f"⚠️ No files found in {source_folder}/")
        return 0
    
    print(f"📋 Found {len(files)} files to move")
    
    # Build move operations
    file_moves = []
    for file_info in files:
        old_path = file_info['path']
        # Replace source folder with target folder
        new_path = old_path.replace(f"{source_folder}/", f"{target_folder}/", 1)
        
        file_moves.append({
            'old_path': old_path,
            'new_path': new_path,
            'sha': file_info['sha']
        })
        print(f"  {old_path} → {new_path}")
    
    # Process in batches of 50
    batch_size = 50
    total_moved = 0
    
    for i in range(0, len(file_moves), batch_size):
        batch = file_moves[i:i+batch_size]
        batch_num = (i // batch_size) + 1
        total_batches = (len(file_moves) + batch_size - 1) // batch_size
        
        print(f"\n📦 Batch {batch_num}/{total_batches}: Moving {len(batch)} files...", end=" ")
        
        commit_msg = f"Merge {source_folder} into {target_folder} (batch {batch_num}/{total_batches})"
        success = create_merge_commit(batch, commit_msg)
        
        if success:
            print("✅")
            total_moved += len(batch)
        else:
            print("❌ FAILED")
            break
        
        time.sleep(0.5)  # Rate limit protection
    
    print(f"\n✅ Merged {total_moved}/{len(files)} files")
    return total_moved

def check_folder_exists(folder_name, tree):
    """Check if a folder exists in the tree."""
    for item in tree:
        if item['path'].startswith(f"{folder_name}/"):
            return True
    return False

def create_folder_with_readme(folder_name):
    """Create a folder by adding a README file."""
    print(f"\n📁 Creating {folder_name}/ folder...")
    
    url = f"{BASE_URL}/contents/{folder_name}/README.md"
    data = {
        "message": f"Create {folder_name} folder",
        "content": "",  # Empty file (base64 encoded empty string)
        "branch": BRANCH
    }
    
    response = requests.put(url, headers=HEADERS, json=data)
    
    if response.status_code in [200, 201]:
        print(f"✅ Created {folder_name}/")
        return True
    else:
        print(f"❌ Failed to create {folder_name}/: {response.status_code}")
        return False

def main():
    if GITHUB_TOKEN == "your_github_token_here":
        print("❌ Please set your GitHub token!")
        print("Generate at: https://github.com/settings/tokens")
        print("Required scope: 'repo'")
        return
    
    print("🚀 GitHub Folder Merge Tool")
    print(f"📦 Repo: {REPO_OWNER}/{REPO_NAME}\n")
    
    # Get repo tree
    tree = get_repo_tree()
    if not tree:
        return
    
    # Check which merges are needed
    print("🔍 Checking folder structure...")
    merges_needed = []
    
    for source, target in FOLDER_MERGES.items():
        source_exists = check_folder_exists(source, tree)
        target_exists = check_folder_exists(target, tree)
        
        print(f"  {source}: {'✅ exists' if source_exists else '❌ not found'}")
        print(f"  {target}: {'✅ exists' if target_exists else '❌ not found'}")
        
        if source_exists:
            merges_needed.append((source, target))
    
    if not merges_needed:
        print("\n✅ No duplicate folders found! Structure looks clean.")
        return
    
    print(f"\n📋 Merges to perform:")
    for source, target in merges_needed:
        files_count = len(get_files_in_folder(source, tree))
        print(f"  • {source} → {target} ({files_count} files)")
    
    # Check for 2026 folder
    has_2026 = check_folder_exists("2026", tree)
    if not has_2026:
        print(f"\n⚠️ 2026 folder doesn't exist yet")
        create_2026 = input("Create 2026 folder now? (y/n): ").lower().strip()
        if create_2026 == 'y':
            create_folder_with_readme("2026")
    else:
        print(f"\n✅ 2026 folder already exists")
    
    # Confirm before proceeding
    print("\n" + "="*60)
    confirm = input("Proceed with merge? (yes/no): ").lower().strip()
    
    if confirm != 'yes':
        print("❌ Cancelled")
        return
    
    # Perform merges
    total_moved = 0
    for source, target in merges_needed:
        moved = merge_folders(source, target, tree)
        total_moved += moved
        time.sleep(1)
    
    print("\n" + "="*60)
    print("🎉 MERGE COMPLETE!")
    print("="*60)
    print(f"✅ Total files moved: {total_moved}")
    print(f"\n📂 Final structure should have:")
    print(f"  • 2023/")
    print(f"  • 2024/")
    print(f"  • 2025/")
    print(f"  • 2026/")
    print(f"\n⚠️ Old duplicate folders (2. 2024, 3. 2025) will be empty")
    print(f"   You can delete them manually via GitHub web interface")

if __name__ == "__main__":
    main()