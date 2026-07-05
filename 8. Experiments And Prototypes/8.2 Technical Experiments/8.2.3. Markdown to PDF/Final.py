import os
import re
import sys
import subprocess
import tempfile
import urllib.request
from pathlib import Path
from datetime import datetime

# ==========================================
# AUTO-INSTALL DEPENDENCIES IF MISSING
# ==========================================
try:
    import markdown
except ImportError:
    print("Installing lightweight Markdown parser (pure Python)...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "markdown"])
    import markdown

try:
    from pygments.formatters import HtmlFormatter
except ImportError:
    print("Installing Pygments for proper syntax highlighting...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pygments"])
    from pygments.formatters import HtmlFormatter

# ==========================================
# CONFIGURATION
# ==========================================
ROOT_FOLDER = r"C:\Users\balasubramanian.pg\Videos\Obsidian\MSc\Trimester 1\Data Preprocessing"
OUTPUT_PDF_PATH = Path(ROOT_FOLDER) / "Data_Preprocessing_Book.pdf"

BOOK_TITLE = "Data Preprocessing"
AUTHOR = "Balasubramanian"
SUBTITLE = "MSc Trimester 1 — Lecture Notes"

SKIP_FOLDERS = {'assets', 'images', 'img', 'static', 'w0'}
SKIP_FILES = {'readme.md', 'module.md', 'intro.md', 'learning path.md'}

# Match Week naming convention (e.g., W01, Week 2, WEEK-03)
WEEK_PATTERN = re.compile(r'^(?:w|week)[\s\-_.]*0*\d+\b', re.IGNORECASE)

def is_week_node(name: str) -> bool:
    return bool(WEEK_PATTERN.match(name.strip()))

EDGE_PATHS = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    "msedge"
]

def find_edge_path():
    for path in EDGE_PATHS:
        if Path(path).exists() or path == "msedge":
            return path
    return None

# ==========================================
# TIER 3: LOCAL ASSET CACHING SYSTEM
# ==========================================
def get_local_or_download(url: str, cache_dir: Path, filename: str) -> Path:
    local_path = cache_dir / filename
    if not local_path.exists():
        print(f"Caching {filename} locally for offline stability...")
        try:
            req = urllib.request.Request(
                url, 
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            )
            with urllib.request.urlopen(req, timeout=15) as response:
                with open(local_path, 'wb') as f:
                    f.write(response.read())
        except Exception as e:
            print(f"Warning: Could not download {filename} ({e}). Falling back to CDN link.")
            return None
    return local_path

# ==========================================
# NATURAL SORTING
# ==========================================
def natural_sort_key(s):
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', str(s))]

# ==========================================
# LATEX COMPLEXITY HEURISTIC ENGINE (Namespace Safe)
# ==========================================
def should_be_display_math(math_content: str) -> bool:
    """
    Analyzes mathematical content to verify if it represents a major, complex
    equation that warrants dedicated centering (display layout), or a minor
    symbolic explanation that should flow inline.
    """
    c = math_content.strip()
    if not c:
        return False
    
    # High-confidence structural and operator indicators for display-level math
    display_indicators = [
        r'\sum', r'\prod', r'\coprod', r'\int', r'\oint', r'\iint', r'\iiint',
        r'\frac', r'\dfrac', r'\tfrac', r'\cfrac', r'\over',
        r'\begin', r'\end', r'\cases', r'\matrix', r'\pmatrix', r'\bmatrix',
        r'\align', r'\split', r'\gather', r'\multline', r'\array',
        r'\lim', r'\max', r'\min', r'\sup', r'\inf',
        r'\sqrt', r'\partial', r'\nabla'
    ]
    
    if any(ind in c for ind in display_indicators):
        return True
        
    # Length-based rule: complex equations are usually longer
    if len(c) > 35:
        return True
        
    # If it contains relation operators
    relation_operators = ['=', r'\ne', r'\approx', r'\le', r'\ge', r'\lt', r'\gt', '<', '>']
    if any(op in c for op in relation_operators) and len(c) > 18:
        return True
        
    return False

# ==========================================
# OBSIDIAN CLEANERS & PARSERS
# ==========================================
def clean_obsidian_markdown(content: str) -> str:
    content = re.sub(r'%%.*?%%', '', content, flags=re.DOTALL)
    content = re.sub(r'\[\[([^\]|]+)\|([^\]]+)\]\]', r'*\2*', content)
    content = re.sub(r'\[\[([^\]]+)\]\]', r'*\1*', content)
    content = re.sub(r'!\[\[([^\]]+)\]\]', r'![](\1)', content)
    return content

def convert_mermaid_blocks(content: str) -> str:
    pattern = r'```mermaid\s*\n(.*?)\n```'
    return re.sub(pattern, r'<div class="mermaid">\1</div>', content, flags=re.DOTALL)

def clean_redundant_headers(content: str) -> str:
    lines = content.split('\n')
    if lines and lines[0].strip().startswith('#'):
        lines.pop(0)
    return '\n'.join(lines)

def dedent_code_blocks(content: str) -> str:
    lines = content.split('\n')
    out = []
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        fence_match = re.match(r'^(\s*)```(\w*)\s*$', line)
        if fence_match:
            lang = fence_match.group(2)
            out.append(f"```{lang}")
            i += 1
            block_lines = []
            while i < n and not re.match(r'^\s*```\s*$', lines[i]):
                block_lines.append(lines[i])
                i += 1
            while block_lines and block_lines[0].strip() == '':
                block_lines.pop(0)
            while block_lines and block_lines[-1].strip() == '':
                block_lines.pop()
            non_blank = [l for l in block_lines if l.strip() != '']
            if non_blank:
                min_indent = min(len(l) - len(l.lstrip(' ')) for l in non_blank)
                block_lines = [l[min_indent:] if len(l) >= min_indent else l.lstrip(' ') for l in block_lines]
            out.extend(block_lines)
            if i < n:
                out.append("```")
                i += 1
            continue
        out.append(line)
        i += 1
    return '\n'.join(out)

def get_svg_icon(callout_type: str) -> str:
    icons = {
        "note": '<svg class="octicon" viewBox="0 0 16 16" width="16" height="16" fill="currentColor"><path d="M0 8a8 8 0 1 1 16 0A8 8 0 0 1 0 8Zm8-3a1 1 0 1 0 0-2 1 1 0 0 0 0 2Zm1.5 5.25a.75.75 0 0 0-1.5 0v3a.75.75 0 0 0 1.5 0v-3ZM8 6.75a.75.75 0 1 0 0-1.5.75.75 0 0 0 0 1.5Z"></path></svg>',
        "tip": '<svg class="octicon" viewBox="0 0 16 16" width="16" height="16" fill="currentColor"><path d="M8 0a.75.75 0 0 1 .75.75v1.5a.75.75 0 0 1-1.5 0V.75A.75.75 0 0 1 8 0Zm0 13a.75.75 0 0 1 .75.75v1.5a.75.75 0 0 1-1.5 0v-1.5A.75.75 0 0 1 8 13Zm5.303-10.303a.75.75 0 0 1 0 1.06l-1.06 1.06a.75.75 0 1 1-1.06-1.06l1.06-1.06a.75.75 0 0 1 1.06 0Zm-9.193 9.193a.75.75 0 0 1 0 1.06l-1.06 1.06a.75.75 0 1 1-1.06-1.06l1.06-1.06a.75.75 0 0 1 1.06 0ZM15 8a.75.75 0 0 1-.75.75h-1.5a.75.75 0 0 1 0-1.5h1.5A.75.75 0 0 1 15 8ZM3 8a.75.75 0 0 1-.75.75H.75a.75.75 0 0 1 0-1.5h1.5A.75.75 0 0 1 3 8Zm10.303 5.303a.75.75 0 0 1-1.06 0l-1.06-1.06a.75.75 0 1 1 1.06-1.06l1.06 1.06a.75.75 0 0 1 0 1.06ZM3.81 3.81a.75.75 0 0 1-1.06 0L1.69 2.75a.75.75 0 1 1 1.06-1.06L3.81 2.75a.75.75 0 0 1 0 1.06ZM8 4a4 4 0 1 1 0 8 4 4 0 0 1 0-8Z"></path></svg>',
        "warning": '<svg class="octicon" viewBox="0 0 16 16" width="16" height="16" fill="currentColor"><path d="M6.457 1.047c.659-1.14 2.302-1.14 2.962 0l6.457 11.17C16.536 13.36 15.712 14 14.5 14H1.5c-1.213 0-2.037-.64-1.376-1.783l6.333-11.17ZM8 5a.75.75 0 0 0-.75.75v3.5a.75.75 0 0 0 1.5 0v-3.5A.75.75 0 0 0 8 5Zm0 6a1 1 0 1 0 0-2 1 1 0 0 0 0 2Z"></path></svg>',
        "important": '<svg class="octicon" viewBox="0 0 16 16" width="16" height="16" fill="currentColor"><path d="M0 8a8 8 0 1 1 16 0A8 8 0 0 1 0 8Zm8-4.5a.75.75 0 0 0-.75.75v5.5a.75.75 0 0 0 1.5 0v-5.5A.75.75 0 0 0 8 3.5ZM8 11a1 1 0 1 0 0-2 1 1 0 0 0 0 2Z"></path></svg>'
    }
    return icons.get(callout_type, icons["note"])

def convert_obsidian_callouts(content: str) -> str:
    lines = content.split('\n')
    processed_lines = []
    in_callout = False
    callout_type = ""
    callout_title = ""
    callout_lines = []
    i = 0
    n = len(lines)

    def flush():
        nonlocal in_callout, callout_lines
        processed_lines.append(render_callout_html(callout_type, callout_title, callout_lines))
        in_callout = False
        callout_lines = []

    while i < n:
        line = lines[i]
        stripped = line.strip()
        if stripped.startswith('>'):
            m = re.match(r'^>\s*\[!(\w+)\](.*)', stripped)
            if m:
                if in_callout:
                    flush()
                in_callout = True
                callout_type = m.group(1).lower()
                callout_title = m.group(2).strip()
                callout_lines = []
            elif in_callout:
                inner_text = re.sub(r'^>\s?', '', line)
                callout_lines.append(inner_text)
            else:
                processed_lines.append(line)
        elif in_callout and stripped == '':
            if i + 1 < n and lines[i + 1].strip().startswith('>'):
                callout_lines.append('')
            else:
                flush()
        else:
            if in_callout:
                flush()
            processed_lines.append(line)
        i += 1

    if in_callout:
        flush()

    return '\n'.join(processed_lines)

def render_callout_html(callout_type: str, title: str, lines: list) -> str:
    inner_markdown = '\n'.join(lines).strip('\n')
    inner_html = markdown.markdown(inner_markdown, extensions=['extra', 'tables'])
    header_title = title if title else callout_type.upper()
    svg_icon = get_svg_icon(callout_type)
    return f"""<div class="markdown-alert markdown-alert-{callout_type}">
<p class="markdown-alert-title">{svg_icon}<span>{header_title}</span></p>
<div class="markdown-alert-content">
{inner_html}
</div>
</div>"""

def remove_markdown_dividers(content: str) -> str:
    lines = content.split('\n')
    cleaned_lines = []
    in_code_block = False
    for line in lines:
        if line.strip().startswith('```'):
            in_code_block = not in_code_block
        if not in_code_block:
            if re.match(r'^\s*([-*_])\s*\1\s*\1\s*$', line.strip()) or re.match(r'^\s*[-*_]{3,}\s*$', line.strip()):
                continue
        cleaned_lines.append(line)
    return '\n'.join(cleaned_lines)

# ==========================================
# SMART LATEX LINE-COHESION ENGINE
# ==========================================
def normalize_latex_line_breaks(content: str) -> str:
    INLINE_MAX_LINES = 4

    lines = content.split('\n')
    out = []
    in_code_block = False
    in_display = False
    in_inline = False
    display_buf = []
    inline_buf = []

    def is_structural_boundary(line: str) -> bool:
        s = line.strip()
        if s == '':
            return True
        if s.startswith('#'):
            return True
        if s.startswith('```'):
            return True
        if s.startswith('>'):
            return True
        if re.match(r'^[-*+]\s', s) or re.match(r'^\d+\.\s', s):
            return True
        if s.startswith('|'):
            return True
        return False

    def dollar_count_excl_escaped_and_double(line: str) -> int:
        stripped = re.sub(r'\\\$', '', line)
        no_dd = stripped.replace('$$', '')
        return no_dd.count('$')

    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        next_line = lines[i + 1] if i + 1 < n else ''

        if re.match(r'^\s*```', line):
            if in_display:
                out.append(' '.join(display_buf)); display_buf = []; in_display = False
            if in_inline:
                out.append(' '.join(inline_buf)); inline_buf = []; in_inline = False
            in_code_block = not in_code_block
            out.append(line)
            i += 1
            continue

        if in_code_block:
            out.append(line)
            i += 1
            continue

        if in_display:
            display_buf.append(line)
            closes_here = (line.count('$$') % 2 == 1)
            force_close = (i + 1 >= n) or is_structural_boundary(next_line)
            if closes_here or force_close:
                out.append(' '.join(display_buf))
                display_buf = []
                in_display = False
            i += 1
            continue

        if in_inline:
            inline_buf.append(line)
            closes_here = (dollar_count_excl_escaped_and_double(line) % 2 == 1)
            force_close = (i + 1 >= n) or is_structural_boundary(next_line)
            if closes_here or force_close:
                out.append(' '.join(inline_buf))
                inline_buf = []
                in_inline = False
            elif len(inline_buf) >= INLINE_MAX_LINES:
                out.extend(inline_buf)
                inline_buf = []
                in_inline = False
            i += 1
            continue

        if line.count('$$') % 2 == 1:
            in_display = True
            display_buf = [line]
            i += 1
            continue

        if dollar_count_excl_escaped_and_double(line) % 2 == 1:
            in_inline = True
            inline_buf = [line]
            i += 1
            continue

        out.append(line)
        i += 1

    if display_buf:
        out.append(' '.join(display_buf))
    if inline_buf:
        out.append(' '.join(inline_buf))

    return '\n'.join(out)

def preserve_math_and_convert(markdown_text: str) -> str:
    markdown_text = remove_markdown_dividers(markdown_text)
    markdown_text = dedent_code_blocks(markdown_text)
    markdown_text = normalize_latex_line_breaks(markdown_text)

    # Clean display math (remove spaces after $$ and before $$) and replace with placeholder
    display_math_matches = re.findall(r'(\$\$.*?\$\$)', markdown_text, flags=re.DOTALL)
    display_math = []
    
    for match in display_math_matches:
        inner = match[2:-2].strip()
        
        # Check complexity: complex formulas stay as display blocks; simple variables degrade to inline
        if should_be_display_math(inner):
            cleaned = f"$${inner}$$"
            display_math.append(cleaned)
            markdown_text = markdown_text.replace(match, f"MATHEXPRDISPLAYX{len(display_math)-1}X", 1)
        else:
            # Downconvert display math to inline math
            downconverted = f"${inner}$"
            markdown_text = markdown_text.replace(match, downconverted, 1)

    # Extract and format inline math blocks. Guard against multi-paragraph runaways.
    inline_math_matches = re.findall(r'((?<!\\)\$.*?(?<!\\)\$)', markdown_text, flags=re.DOTALL)
    inline_math = []
    for match in inline_math_matches:
        inner = match[1:-1].strip()
        if '\n\n' in inner:
            continue
        cleaned = f"${inner}$"
        inline_math.append(cleaned)
        markdown_text = markdown_text.replace(match, f"MATHINLINE{len(inline_math)-1}EXP", 1)

    cleaned_md = clean_obsidian_markdown(markdown_text)
    cleaned_md = convert_mermaid_blocks(cleaned_md)
    cleaned_md = convert_obsidian_callouts(cleaned_md)

    html = markdown.markdown(
        cleaned_md,
        extensions=['extra', 'codehilite', 'tables', 'fenced_code'],
        extension_configs={
            'codehilite': {
                'guess_lang': False,
                'use_pygments': True,
                'noclasses': False,
                'linenums': False,
            }
        }
    )

    # Re-apply the isolated mathematical symbols and equations
    for i, math_str in enumerate(display_math):
        html = html.replace(f"MATHEXPRDISPLAYX{i}X", math_str)
    for i, math_str in enumerate(inline_math):
        html = html.replace(f"MATHINLINE{i}EXP", math_str)

    return html

# ==========================================
# LANGUAGE DETECTION SAFEGUARD
# ==========================================
def force_python_lang_fences(content: str) -> str:
    lines = content.split('\n')
    out = []
    i = 0
    n = len(lines)
    py_signal = re.compile(r'^\s*(import\s+\w|from\s+\w+\s+import|def\s+\w+\(|class\s+\w+[:\(]|print\()')
    while i < n:
        m = re.match(r'^(\s*)```(\w*)\s*$', lines[i])
        if m:
            indent, lang = m.group(1), m.group(2)
            j = i + 1
            block = []
            while j < n and not re.match(r'^\s*```\s*$', lines[j]):
                block.append(lines[j])
                j += 1
            if (not lang or lang.lower() in ('sql', 'text', 'txt')) and any(py_signal.match(l) for l in block):
                lang = 'python'
            out.append(f"{indent}```{lang}")
            out.extend(block)
            if j < n:
                out.append(lines[j])
                j += 1
            i = j
            continue
        out.append(lines[i])
        i += 1
    return '\n'.join(out)

# ==========================================
# RELATIVE HEADING LEVEL SHIFTER
# ==========================================
def shift_markdown_headings(content: str, base_level: int) -> str:
    """
    Shifts all markdown headings (#...######) down relative to the resolved
    base hierarchy level of the file to prevent internal headings from breaking
    the global sequential PDF outline hierarchy.
    """
    lines = content.split('\n')
    out = []
    in_code_block = False
    for line in lines:
        if line.strip().startswith('```'):
            in_code_block = not in_code_block
            out.append(line)
            continue
        if in_code_block:
            out.append(line)
            continue
        
        m = re.match(r'^(\s*)(#{1,6})\s+(.*)$', line)
        if m:
            indent = m.group(1)
            hashes = m.group(2)
            title_text = m.group(3)
            current_level = len(hashes)
            new_level = min(current_level + base_level, 6)
            new_hashes = '#' * new_level
            out.append(f"{indent}{new_hashes} {title_text}")
        else:
            out.append(line)
    return '\n'.join(out)

# ==========================================
# TREE PARSER & DOCUMENT GENERATOR
# ==========================================
def compile_notes_to_html(root_dir: Path):
    toc_entries = []
    html_content_blocks = []
    page_styles = []
    heading_counter = 0
    outlier_warnings = []

    def resolve_header_level(name: str, depth: int, week_anchor_depth):
        """
        Rule: ONLY a node whose name matches the Week convention (W01,
        Week 1, ...) may ever become H1. Everything else is leveled
        RELATIVE to the nearest ancestor Week node (never below H2).
        """
        if is_week_node(name):
            return 1, depth, False

        if week_anchor_depth is not None:
            relative = depth - week_anchor_depth
            level = min(max(relative + 1, 2), 6)
            return level, week_anchor_depth, False

        level = min(depth + 1, 6)
        return level, week_anchor_depth, True

    def traverse(current_dir: Path, depth: int, week_anchor_depth, current_week_page_id=None):
        nonlocal heading_counter
        items = list(current_dir.iterdir())

        subdirs = sorted([d for d in items if d.is_dir() and d.name.lower() not in SKIP_FOLDERS and not d.name.startswith('.')], key=lambda x: natural_sort_key(x.name))
        md_files = sorted([f for f in items if f.is_file() and f.suffix.lower() == '.md' and f.name.lower() not in SKIP_FILES], key=lambda x: natural_sort_key(x.name))

        for file_path in md_files:
            heading_counter += 1
            file_title = file_path.stem
            anchor_id = f"heading-{heading_counter}"

            header_level, _, is_outlier = resolve_header_level(file_title, depth, week_anchor_depth)
            if is_outlier:
                outlier_warnings.append(f"'{file_title}' (file) has no Week ancestor -> fallback H{header_level}")

            active_page_id = current_week_page_id
            if header_level == 1:
                active_page_id = f"week_page_{heading_counter}"
                page_styles.append(f"""
                @page {active_page_id} {{
                    @bottom-left {{
                        content: "{file_title}";
                        font-family: 'Afacad', 'Abadi', 'Segoe UI', sans-serif;
                        font-size: 8.5pt;
                        color: #777;
                    }}
                }}
                """)

            toc_entries.append((header_level, file_title, anchor_id))

            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    file_body = f.read()

                file_body = clean_redundant_headers(file_body)
                file_body = shift_markdown_headings(file_body, header_level)
                file_body = force_python_lang_fences(file_body)
                converted_html = preserve_math_and_convert(file_body)

                is_major = (header_level == 1)
                section_class = "doc-section level-{} {}".format(header_level, "force-break" if is_major else "")
                
                # Apply named page context to section style
                page_style_attr = f'style="page: {active_page_id};"' if active_page_id else ''
                
                html_block = f"""
                <section class="{section_class.strip()}" {page_style_attr}>
                    <h{header_level} id="{anchor_id}">{file_title}</h{header_level}>
                    {converted_html}
                </section>
                """
                html_content_blocks.append(html_block)

            except Exception as e:
                print(f"Skipping file: {file_path}. Details: {e}")

        for subdir in subdirs:
            heading_counter += 1
            folder_title = subdir.name
            anchor_id = f"heading-{heading_counter}"

            header_level, new_anchor, is_outlier = resolve_header_level(folder_title, depth, week_anchor_depth)
            if is_outlier:
                outlier_warnings.append(f"'{folder_title}' (folder) has no Week ancestor -> fallback H{header_level}")

            active_page_id = current_week_page_id
            if header_level == 1:
                active_page_id = f"week_page_{heading_counter}"
                page_styles.append(f"""
                @page {active_page_id} {{
                    @bottom-left {{
                        content: "{folder_title}";
                        font-family: 'Afacad', 'Abadi', 'Segoe UI', sans-serif;
                        font-size: 8.5pt;
                        color: #777;
                    }}
                }}
                """)

            toc_entries.append((header_level, folder_title, anchor_id))

            break_class = "folder-header" + (" force-break" if header_level == 1 else "")
            page_style_attr = f'style="page: {active_page_id};"' if active_page_id else ''
            
            html_content_blocks.append(f'<h{header_level} id="{anchor_id}" class="{break_class}" {page_style_attr}>{folder_title}</h{header_level}>')

            traverse(subdir, depth + 1, new_anchor, current_week_page_id=active_page_id)

    traverse(root_dir, depth=0, week_anchor_depth=None, current_week_page_id=None)

    if outlier_warnings:
        print("\n⚠ Heading hierarchy outliers detected (fallback levels applied):")
        for w in outlier_warnings:
            print(f"  - {w}")

    return toc_entries, "\n".join(html_content_blocks), "\n".join(page_styles)

# ==========================================
# HTML TEMPLATE BUILDER
# ==========================================
def build_html_document(toc_entries, content_html, page_styles_css, mathjax_src, mermaid_src) -> str:
    toc_html = ["<div class='toc-wrapper'>", "<h1>Table of Contents</h1>", "<ul>"]
    for level, title, anchor_id in toc_entries:
        indent_class = f"toc-indent-{level}"
        toc_html.append(f"<li class='{indent_class}'><a href='#{anchor_id}'>{title}</a></li>")
    toc_html.append("</ul></div>")
    toc_block = "\n".join(toc_html)

    pygments_css = HtmlFormatter(style='friendly').get_style_defs('.codehilite')

    html_template = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{BOOK_TITLE}</title>

    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Afacad:ital,wght@0,400..700;1,400..700&display=swap" rel="stylesheet">

    <script>
        window.MathJax = {{
            tex: {{
                inlineMath: [['$', '$'], ['\\\\(', '\\\\)']],
                displayMath: [['$$', '$$'], ['\\\\[', '\\\\]']]
            }}
        }};
    </script>
    <script src="{mathjax_src}"></script>

    <script src="{mermaid_src}"></script>
    <script>
        mermaid.initialize({{
            startOnLoad: true,
            theme: 'default',
            themeVariables: {{
                fontFamily: '"Geom", "Century Gothic", Arial, sans-serif',
                fontSize: '10px',
                primaryColor: '#004C87',
                edgeLabelBackground: '#ffffff'
            }}
        }});
    </script>

    <style>
        /* NATIVE CHROMIUM PAGE STYLING, THIN WORD-STYLE PAGE BORDERS, AND FOOTERS (Chrome 131+) */
        @page {{
            size: A4;
            margin: 16mm 16mm 20mm 16mm; /* Margins outside the thin page border frame */
            border: 1px solid #dcdcdc; /* Thin, elegant, mild gray native page border around the page area */
            padding: 6mm; /* Breathing space inside the border so text never intersects it */
            
            @bottom-right {{
                content: counter(page);
                font-family: 'Afacad', 'Abadi', 'Segoe UI', sans-serif;
                font-size: 8.5pt;
                color: #555; /* Mild black/subtle gray page numbers */
                padding-top: 4mm;
            }}
        }}
        @page :first {{
            border: none !important;
            padding: 0 !important;
            @bottom-right {{ content: none !important; }}
            @bottom-left {{ content: none !important; }}
        }}
        
        /* Inject dynamically generated named page rules for week-by-week footers */
        {page_styles_css}

        @media print, screen {{
            body {{
                font-family: 'Afacad', 'Abadi', 'Segoe UI', sans-serif;
                font-size: 11pt;
                line-height: 1.5;
                color: #222;
                background: #fff;
            }}
            h1, h2, h3, h4, h5, h6, .cover-title, .cover-subtitle, .toc-wrapper h1 {{
                font-family: 'Geom', 'Century Gothic', Arial, sans-serif;
                font-weight: 700 !important;
            }}
            strong, b {{ font-weight: 700 !important; }}

            /* Only true Week nodes (H1) force a new page */
            .force-break {{ page-break-before: always; }}
            h1, h2, h3, h4, h5, h6 {{ page-break-after: avoid; }}
            h1:not(.force-break), h2, h3, h4, h5, h6 {{ page-break-before: avoid; }}
            pre, blockquote, table, img, .mermaid, .markdown-alert {{
                page-break-inside: avoid;
            }}
            p {{ orphans: 3; widows: 3; }}
        }}
        
        @media print {{
            /* Eliminate active browser spinner widgets and scroll indicators inside the printed PDF */
            mjx-container[display="true"], 
            mjx-container:not([display="true"]),
            mjx-math {{
                overflow: visible !important;
                overflow-x: visible !important;
                overflow-y: visible !important;
            }}
        }}

        body {{ max-width: 900px; margin: 0 auto; padding: 20px; }}

        .cover-page {{
            height: 90vh; display: flex; flex-direction: column;
            justify-content: center; align-items: center; text-align: center;
            page-break-after: always;
        }}
        .cover-title {{ font-size: 38pt; font-weight: bold; margin-bottom: 10px; color: #004C87; }}
        .cover-subtitle {{ font-size: 18pt; color: #555; margin-bottom: 50px; }}
        .cover-author {{ font-size: 14pt; font-weight: bold; margin-top: 100px; }}
        .cover-date {{ font-size: 11pt; color: #888; }}

        .toc-wrapper {{ page-break-after: always; margin-top: 50px; }}
        .toc-wrapper h1 {{ page-break-before: avoid; border-bottom: 2px solid #004C87; padding-bottom: 10px; }}
        .toc-wrapper ul {{ list-style: none; padding: 0; }}
        .toc-wrapper li {{ margin-bottom: 6px; }}
        .toc-wrapper a {{ text-decoration: none; color: #004C87; font-size: 11pt; }}
        .toc-indent-1 {{ font-weight: bold; margin-top: 15px; }}
        .toc-indent-2 {{ padding-left: 20px; }}
        .toc-indent-3 {{ padding-left: 40px; font-size: 10pt; }}
        .toc-indent-4 {{ padding-left: 60px; font-size: 9pt; }}
        .toc-indent-5 {{ padding-left: 80px; font-size: 8.5pt; }}
        .toc-indent-6 {{ padding-left: 100px; font-size: 8pt; }}

        h1 {{ font-size: 24pt; border-bottom: 1px solid #ddd; padding-bottom: 8px; margin-top: 40px; }}
        h2 {{ font-size: 18pt; margin-top: 25px; border-bottom: 1px solid #eee; padding-bottom: 4px; }}
        h3 {{ font-size: 14pt; margin-top: 20px; }}

        /* Normalize math alignment, margins, color, and prevent vertical descender clipping */
        mjx-container[display="true"] {{
            margin: 0.8em 0 !important;
            font-size: 100% !important;
            overflow: visible !important;
            overflow-x: visible !important;
            overflow-y: visible !important;
        }}
        mjx-container:not([display="true"]) {{
            font-size: 96% !important;
            white-space: nowrap;
            overflow: visible !important;
            overflow-x: visible !important;
            overflow-y: visible !important;
        }}
        mjx-container, .MathJax, .MathJax_Display, mjx-math, .MathJax * {{
            color: #004C87 !important; /* Theme-matching Medium Navy Blue for all equations */
        }}

        .markdown-alert {{
            border-left: 4px solid;
            background-color: #f9f9f9;
            padding: 12px 16px;
            margin: 15px 0;
            border-radius: 2px !important;
        }}
        .markdown-alert-note {{ border-color: #004C87; background-color: #f0f7ff; }}
        .markdown-alert-tip {{ border-color: #1a7f37; background-color: #f0fdf4; }}
        .markdown-alert-warning {{ border-color: #9a6700; background-color: #fffbeb; }}
        .markdown-alert-important {{ border-color: #8250df; background-color: #fbf5ff; }}

        .markdown-alert-title {{
            font-weight: 700 !important;
            font-size: 10pt;
            margin: 0 0 6px 0;
            display: flex;
            align-items: center;
            gap: 6px;
        }}
        .markdown-alert-title svg {{ width: 16px; height: 16px; flex-shrink: 0; }}
        .markdown-alert-content p {{ margin-bottom: 0; color: #24292f; }}
        .markdown-alert-content p:not(:last-child) {{ margin-bottom: 8px; }}

        blockquote {{
            border-left: 4px solid #004C87;
            background-color: #f9f9f9;
            padding: 8px 15px;
            margin: 10px 0;
            color: #444;
        }}

        pre, code {{
            font-family: Consolas, 'Courier New', monospace;
        }}
        code {{
            padding: 2px 4px;
            font-size: 8.5pt;
            background-color: #f6f8fa;
            border-radius: 2px;
        }}
        div.codehilite {{
            background-color: #F7F7F7;
            border: 1px solid #cfcfcf;
            border-left: 3px solid #4e8098;
            border-radius: 2px;
            padding: 10px 12px;
            margin: 10px 0;
            overflow-x: auto;
        }}
        div.codehilite pre {{
            margin: 0;
            padding: 0;
            border: none;
            background: transparent;
            font-size: 9.5pt;
            line-height: 1.45;
        }}
        {pygments_css}
        .codehilite .c, .codehilite .c1, .codehilite .ch, .codehilite .cm,
        .codehilite .cp, .codehilite .cpf, .codehilite .cs {{
            color: #008000 !important;
            font-style: italic;
        }}

        /* Table Column Header and Aesthetic Styling */
        table {{ border-collapse: collapse; width: 100%; margin: 12px 0; font-size: 9.5pt; }}
        table th, table td {{ border: 1px solid #ddd; padding: 8px 12px; text-align: left; }}
        table th {{ 
            background-color: #004C87 !important; /* Navy Blue background fill */
            color: #ffffff !important; /* White text inside just the column header */
            font-family: 'Geom', 'Century Gothic', Arial, sans-serif;
            font-weight: bold !important;
            border: 1px solid #004C87 !important;
        }}
        table tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}
        img {{ max-width: 100%; height: auto; display: block; margin: 10px auto; }}
        
        /* Mermaid Graph Aesthetics */
        .mermaid {{ margin: 15px 0; text-align: center; }}
        .mermaid, .mermaid *, .mermaid text, .mermaid tspan, .mermaid .node text {{
            font-family: 'Geom', 'Century Gothic', Arial, sans-serif !important;
            font-size: 10px !important;
        }}
    </style>
</head>
<body>
    <div class="cover-page">
        <div class="cover-title">{BOOK_TITLE}</div>
        <div class="cover-subtitle">{SUBTITLE}</div>
        <div class="cover-author">Prepared by: {AUTHOR}</div>
        <div class="cover-date">{datetime.now().strftime('%B %d, %Y')}</div>
    </div>

    {toc_block}

    <div class="book-content">
        {content_html}
    </div>
</body>
</html>
"""
    return html_template

# ==========================================
# MAIN ASSEMBLY & RENDERING
# ==========================================
def main():
    root_path = Path(ROOT_FOLDER)
    if not root_path.exists():
        print(f"Error: Directory path '{ROOT_FOLDER}' was not found.")
        return

    temp_dir = Path(tempfile.gettempdir())
    temp_html_path = temp_dir / "temp_book.html"

    # Offline Script Resolution
    mathjax_local = get_local_or_download(
        "https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js",
        temp_dir,
        "mathjax_tex_mml_chtml.js"
    )
    mermaid_local = get_local_or_download(
        "https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js",
        temp_dir,
        "mermaid_10_min.js"
    )

    mathjax_src = f"file:///{mathjax_local.resolve()}" if mathjax_local else "https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"
    mermaid_src = f"file:///{mermaid_local.resolve()}" if mermaid_local else "https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"

    print("Step 1 (Tier 1): Compiling notes and restructuring hierarchy...")
    toc_entries, content_html, page_styles_css = compile_notes_to_html(root_path)

    print("Step 2 (Tier 3): Injecting asset buffers and styling document...")
    final_html = build_html_document(toc_entries, content_html, page_styles_css, mathjax_src, mermaid_src)

    with open(temp_html_path, 'w', encoding='utf-8') as f:
        f.write(final_html)

    print("Step 3: Finding native Microsoft Edge engine...")
    edge_bin = find_edge_path()
    if not edge_bin:
        print("Error: Could not locate Microsoft Edge. Please verify your Windows environment.")
        return

    print("Step 4: Executing print process with virtual rendering budget...")
    cmd = [
        edge_bin,
        "--headless=old",
        "--disable-gpu",
        "--no-pdf-header-footer",
        "--generate-pdf-document-outline",
        "--virtual-time-budget=25000",
        "--run-all-compositor-stages-before-draw",
        f"--print-to-pdf={OUTPUT_PDF_PATH.resolve()}",
        f"file:///{temp_html_path.resolve()}"
    ]

    try:
        subprocess.run(cmd, check=True, capture_output=True)
        print(f"\nSuccess! Your book PDF is generated at:\n{OUTPUT_PDF_PATH.resolve()}")
    except subprocess.CalledProcessError as e:
        print("\nError: Microsoft Edge rendering failed.")
        print(e.stderr)
    finally:
        if temp_html_path.exists():
            temp_html_path.unlink()

if __name__ == "__main__":
    main()
