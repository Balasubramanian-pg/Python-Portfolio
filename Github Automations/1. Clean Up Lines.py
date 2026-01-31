import os
import re
import subprocess
import sys
import tempfile
import shutil
from pathlib import Path
from typing import List, Tuple, Optional
import getpass

class SecureMarkdownCleaner:
    def __init__(self, repo_url: str, github_token: str):
        """
        Initialize the cleaner with repository URL and GitHub token.
        
        Args:
            repo_url: Full GitHub repository URL
            github_token: GitHub personal access token
        """
        self.repo_url = repo_url
        self.original_token = github_token
        
        # Create authenticated URL
        self.auth_repo_url = self.repo_url.replace(
            'https://github.com/',
            f'https://{github_token}@github.com/'
        )
        
        # Create a temporary directory for the clone
        self.temp_dir = tempfile.mkdtemp(prefix="github_clean_")
        self.repo_path = Path(self.temp_dir) / "repo"
        
        print(f"Temporary directory: {self.temp_dir}")
        print("=" * 60)
    
    def __del__(self):
        """Clean up temporary directory."""
        if hasattr(self, 'temp_dir') and os.path.exists(self.temp_dir):
            print(f"\nCleaning up temporary directory: {self.temp_dir}")
            try:
                shutil.rmtree(self.temp_dir)
                print("✓ Temporary directory cleaned up")
            except Exception as e:
                print(f"⚠ Warning: Could not clean up temp directory: {e}")
    
    def clone_repository(self) -> bool:
        """Clone the repository using authenticated URL."""
        print(f"Cloning repository: {self.repo_url}")
        
        try:
            # Mask token in command display
            safe_url = self.repo_url.replace(
                'https://github.com/',
                'https://[TOKEN]@github.com/'
            )
            print(f"Using authenticated URL: {safe_url}")
            
            result = subprocess.run(
                ['git', 'clone', self.auth_repo_url, str(self.repo_path)],
                capture_output=True,
                text=True,
                check=True
            )
            
            print("✓ Repository cloned successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"✗ Error cloning repository:")
            print(f"  Error: {e.stderr}")
            
            # Check for common errors
            if "Authentication failed" in e.stderr:
                print("\n  Possible issues:")
                print("  1. Invalid GitHub token")
                print("  2. Token doesn't have repo permissions")
                print("  3. Token might be expired")
            elif "not found" in e.stderr:
                print(f"\n  Repository not found: {self.repo_url}")
            
            return False
        except Exception as e:
            print(f"✗ Unexpected error: {e}")
            return False
    
    def configure_git(self) -> bool:
        """Configure git with safe settings."""
        try:
            os.chdir(self.repo_path)
            
            # Set git user info (important for commits)
            subprocess.run(['git', 'config', 'user.email', 'cleanup-script@example.com'], 
                         check=True, capture_output=True)
            subprocess.run(['git', 'config', 'user.name', 'Markdown Cleanup Script'], 
                         check=True, capture_output=True)
            
            # Don't store credentials
            subprocess.run(['git', 'config', 'credential.helper', 'cache'], 
                         check=True, capture_output=True)
            
            os.chdir(self.temp_dir)
            return True
            
        except Exception as e:
            print(f"Error configuring git: {e}")
            return False
    
    def find_markdown_files(self) -> List[Path]:
        """Find all markdown files in the repository."""
        markdown_files = []
        
        print(f"\nScanning for markdown files in {self.repo_path}...")
        
        for root, dirs, files in os.walk(self.repo_path):
            # Skip .git directory
            if '.git' in dirs:
                dirs.remove('.git')
            
            for file in files:
                if file.lower().endswith(('.md', '.markdown')):
                    full_path = Path(root) / file
                    # Get relative path for display
                    rel_path = full_path.relative_to(self.repo_path)
                    markdown_files.append(full_path)
        
        print(f"Found {len(markdown_files)} markdown files")
        return markdown_files
    
    def remove_dashes_from_file(self, file_path: Path) -> Tuple[bool, int]:
        """
        Remove all occurrences of '---' from a markdown file.
        
        Returns:
            Tuple of (changed: bool, count_removed: int)
        """
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Count occurrences before removal
            original_count = content.count('---')
            
            if original_count == 0:
                return False, 0
            
            # Remove all occurrences of '---'
            new_content = content.replace('---', '')
            
            # Only write if content actually changed
            if new_content != content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                return True, original_count
            else:
                return False, 0
            
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            return False, 0
    
    def git_commit(self, file_path: Path, commit_message: str) -> bool:
        """Commit a single file with a descriptive message."""
        try:
            os.chdir(self.repo_path)
            
            # Get relative path for git commands
            rel_path = file_path.relative_to(self.repo_path)
            
            # Add the specific file
            add_result = subprocess.run(
                ['git', 'add', str(rel_path)], 
                capture_output=True,
                text=True
            )
            
            if add_result.returncode != 0:
                print(f"  Git add error: {add_result.stderr}")
                return False
            
            # Check if there are actually changes to commit
            status_result = subprocess.run(
                ['git', 'status', '--porcelain', str(rel_path)],
                capture_output=True,
                text=True
            )
            
            if not status_result.stdout.strip():
                # No changes to commit
                return False
            
            # Commit with message
            commit_result = subprocess.run(
                ['git', 'commit', '-m', commit_message],
                capture_output=True,
                text=True
            )
            
            if commit_result.returncode == 0:
                # Get the short commit hash
                hash_result = subprocess.run(
                    ['git', 'rev-parse', '--short', 'HEAD'],
                    capture_output=True,
                    text=True
                )
                commit_hash = hash_result.stdout.strip()
                print(f"  ✓ Committed: {commit_hash} - {commit_message}")
                return True
            else:
                print(f"  ✗ Commit failed: {commit_result.stderr}")
                return False
            
        except Exception as e:
            print(f"  ✗ Error during commit: {e}")
            return False
    
    def git_push(self) -> bool:
        """Push all commits to remote repository."""
        try:
            os.chdir(self.repo_path)
            
            print("\n" + "=" * 60)
            print("Pushing changes to GitHub...")
            
            push_result = subprocess.run(
                ['git', 'push'],
                capture_output=True,
                text=True
            )
            
            if push_result.returncode == 0:
                print("✓ All changes pushed successfully!")
                return True
            else:
                print(f"✗ Push failed: {push_result.stderr}")
                return False
            
        except Exception as e:
            print(f"✗ Error during push: {e}")
            return False
    
    def show_changes_summary(self, changed_files: List[Tuple[Path, int]]):
        """Show a summary of all changes made."""
        if not changed_files:
            print("\n" + "=" * 60)
            print("No changes were made to any files.")
            return
        
        print("\n" + "=" * 60)
        print("CHANGES SUMMARY")
        print("=" * 60)
        
        total_removed = 0
        for file_path, count in changed_files:
            rel_path = file_path.relative_to(self.repo_path)
            print(f"{rel_path}: {count} '---' removed")
            total_removed += count
        
        print("-" * 60)
        print(f"Total files changed: {len(changed_files)}")
        print(f"Total '---' removed: {total_removed}")
        print("=" * 60)
    
    def show_git_log(self):
        """Show the git log of recent commits."""
        try:
            os.chdir(self.repo_path)
            
            print("\n" + "=" * 60)
            print("RECENT COMMITS")
            print("=" * 60)
            
            log_result = subprocess.run(
                ['git', 'log', '--oneline', '-10', '--'],
                capture_output=True,
                text=True
            )
            
            if log_result.stdout.strip():
                print(log_result.stdout)
            else:
                print("No commits yet")
            
            print("=" * 60)
            
        except Exception as e:
            print(f"Error showing git log: {e}")
    
    def run(self) -> bool:
        """Main execution method."""
        print("Secure Markdown Cleaner")
        print("=" * 60)
        
        # Clone repository
        if not self.clone_repository():
            return False
        
        # Configure git
        if not self.configure_git():
            print("Warning: Git configuration failed, but continuing...")
        
        # Find all markdown files
        markdown_files = self.find_markdown_files()
        
        if not markdown_files:
            print("No markdown files found in the repository!")
            return True  # Success, just nothing to do
        
        # Process each file
        changed_files = []  # List of (file_path, count_removed)
        files_processed = 0
        
        for file_path in markdown_files:
            files_processed += 1
            rel_path = file_path.relative_to(self.repo_path)
            
            print(f"\n[{files_processed}/{len(markdown_files)}] Processing: {rel_path}")
            
            # Remove dashes from file
            changed, count_removed = self.remove_dashes_from_file(file_path)
            
            if changed:
                # Create commit message
                commit_message = f"Remove {count_removed} '---' from {rel_path}"
                
                # Commit this change
                if self.git_commit(file_path, commit_message):
                    changed_files.append((file_path, count_removed))
                else:
                    print(f"  ⚠ File changed but not committed")
            elif count_removed > 0:
                print(f"  ⚠ Found {count_removed} '---' but file didn't change (possible encoding issue)")
            else:
                print(f"  ✓ No '---' found")
        
        # Show summary
        self.show_changes_summary(changed_files)
        
        # Show git log
        self.show_git_log()
        
        # Push changes if any were made
        if changed_files:
            push_choice = input("\nDo you want to push these changes to GitHub? (y/n): ").lower().strip()
            
            if push_choice == 'y':
                if self.git_push():
                    return True
                else:
                    print("\n⚠ Push failed. You can manually push from:")
                    print(f"  cd {self.repo_path}")
                    print(f"  git push")
                    return False
            else:
                print("\n⚠ Changes were not pushed. You can manually push from:")
                print(f"  cd {self.repo_path}")
                print(f"  git push")
                return True
        else:
            return True

def get_github_token() -> str:
    """Securely get GitHub token from user input."""
    print("\nGitHub Token Setup")
    print("=" * 60)
    print("You need a GitHub Personal Access Token with 'repo' permissions.")
    print("Create one at: https://github.com/settings/tokens")
    print("\nThe token will only be used for this session and not saved.")
    print("=" * 60)
    
    token = getpass.getpass("Enter your GitHub token (hidden input): ").strip()
    
    if not token:
        print("✗ No token provided. Exiting.")
        sys.exit(1)
    
    return token

def main():
    """Main function."""
    # Repository URL
    repo_url = "https://github.com/Balasubramanian-pg/Healthcare-Projects"
    
    print("Markdown Cleanup Script")
    print("=" * 60)
    print(f"Repository: {repo_url}")
    print("This script will:")
    print("1. Clone the repository to a temporary directory")
    print("2. Remove all '---' from every markdown file")
    print("3. Commit each file change separately")
    print("4. Push changes back to GitHub")
    print("=" * 60)
    
    # Get GitHub token securely
    github_token = get_github_token()
    
    # Confirm before proceeding
    print("\n" + "=" * 60)
    confirm = input("Proceed with cleanup? (y/n): ").lower().strip()
    
    if confirm != 'y':
        print("Operation cancelled.")
        sys.exit(0)
    
    # Create and run cleaner
    cleaner = SecureMarkdownCleaner(repo_url, github_token)
    
    try:
        success = cleaner.run()
        
        if success:
            print("\n✓ Operation completed successfully!")
            sys.exit(0)
        else:
            print("\n✗ Operation failed.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⚠ Operation interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
