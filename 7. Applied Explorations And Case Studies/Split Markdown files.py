import os
import re

# ================= CONFIGURATION =================
SOURCE_FILE_PATH = r"C:\Users\ASUS\Videos\AnyDesk\Balasubramanian PG\01. Personal\Books\Praxis Framework An integrated guide to Project Management\chapters\09_Praxis_Framework.md"
# =================================================

# FIXED REGEX: Handles Markdown headers (#), bold markers (**), and whitespace
SECTION_PATTERN = re.compile(r'^\s*#{0,6}\s*[\*_]{0,2}(\d+(?:\.\d+)+)[\*_]{0,2}\s+(.+)', re.UNICODE)
FIGURE_PATTERN = re.compile(r'^\s*#{0,6}\s*[\*_]{0,2}(Figure\s+\d+(?:\.\d+)*)[\*_]{0,2}\s+(.+)', re.UNICODE)

def clean_filename(text):
    """Sanitizes text for Windows filenames."""
    clean = re.sub(r'[\*_`]', '', text)  # Remove Markdown markers
    clean = re.sub(r'[<>:"/\\|?*]', '', clean)  # Remove illegal chars
    return clean.strip()[:100]

def get_parent_id(section_id):
    """Returns parent ID (e.g., '1.2.1' → '1.2')."""
    parts = section_id.split('.')
    return '.'.join(parts[:-1]) if len(parts) > 1 else None

def main():
    if not os.path.exists(SOURCE_FILE_PATH):
        print(f"❌ Error: File not found at {SOURCE_FILE_PATH}")
        return

    base_dir = os.path.dirname(SOURCE_FILE_PATH)
    filename_no_ext = os.path.splitext(os.path.basename(SOURCE_FILE_PATH))[0]
    root_output_dir = os.path.join(base_dir, filename_no_ext)
    os.makedirs(root_output_dir, exist_ok=True)

    print(f"✅ Processing sections into: {root_output_dir}")
    print("🔍 Debug: Showing detected sections (uncomment lines 68-70 to see all matches)\n")

    with open(SOURCE_FILE_PATH, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    id_to_folder_map = {}
    current_file_handle = None
    current_folder_path = root_output_dir

    def close_current_file():
        nonlocal current_file_handle
        if current_file_handle:
            current_file_handle.close()
            current_file_handle = None

    for line_num, line in enumerate(lines, 1):
        stripped_line = line.strip()
        
        # DEBUG: Uncomment to see ALL lines being processed
        # if stripped_line:
        #     print(f"Line {line_num}: '{stripped_line[:50]}'")

        # CHECK 1: Numbered section (handles #, **, __, mixed formatting)
        section_match = SECTION_PATTERN.match(stripped_line)
        
        # CHECK 2: Figure caption
        figure_match = FIGURE_PATTERN.match(stripped_line)

        if section_match:
            close_current_file()
            
            sec_id = section_match.group(1).strip()  # e.g., "1.3"
            raw_title = section_match.group(2).strip()  # e.g., "Context"
            
            # DEBUG: Show detected sections
            print(f"📁 DETECTED SECTION {sec_id}: '{raw_title}' (line {line_num})")
            
            parent_id = get_parent_id(sec_id)
            parent_dir = id_to_folder_map.get(parent_id, root_output_dir)
            
            folder_name = clean_filename(f"{sec_id} {raw_title}")
            new_folder_path = os.path.join(parent_dir, folder_name)
            os.makedirs(new_folder_path, exist_ok=True)
            
            id_to_folder_map[sec_id] = new_folder_path
            current_folder_path = new_folder_path
            
            # Create section file (same name as folder)
            file_path = os.path.join(new_folder_path, f"{folder_name}.md")
            current_file_handle = open(file_path, 'w', encoding='utf-8')
            current_file_handle.write(line)  # Preserve original formatting

        elif figure_match:
            close_current_file()
            
            fig_id = figure_match.group(1).strip()  # e.g., "Figure 1.2"
            fig_title = figure_match.group(2).strip()
            
            # DEBUG: Show detected figures
            # print(f"🖼️ DETECTED FIGURE: '{fig_id} {fig_title}' (line {line_num})")
            
            filename = clean_filename(f"{fig_id} {fig_title}.md")
            file_path = os.path.join(current_folder_path, filename)
            
            current_file_handle = open(file_path, 'w', encoding='utf-8')
            current_file_handle.write(line)

        else:
            # Write non-header content to current section file
            if current_file_handle:
                current_file_handle.write(line)

    close_current_file()
    print(f"\n✅ Done! Processed {len(id_to_folder_map)} sections into {root_output_dir}")
    print(f"📊 Section IDs found: {sorted(id_to_folder_map.keys())}")

if __name__ == "__main__":
    main()