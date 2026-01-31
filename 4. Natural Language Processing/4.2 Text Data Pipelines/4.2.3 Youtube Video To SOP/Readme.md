# Business Requirements Document (BRD)
## YouTube Video Frame Extraction & Markdown Documentation Tool

## 1. PROJECT OVERVIEW

**Objective:** Build a Python script that automatically extracts distinct frames from a YouTube video, generates contextual filenames using video transcripts, and compiles everything into a structured Markdown document.

**Use Case:** Creating visual documentation, tutorials, or step-by-step guides from video content without manual screenshot capture.

## 2. FUNCTIONAL REQUIREMENTS

### 2.1 Core Features

| Feature | Description | Priority |
|---------|-------------|----------|
| **YouTube URL Input** | Accept any valid YouTube video URL | MUST HAVE |
| **Frame Change Detection** | Capture screenshots only when visual content changes significantly | MUST HAVE |
| **Transcript Extraction** | Download and parse YouTube video transcript/captions | MUST HAVE |
| **Contextual Naming** | Generate meaningful filenames based on transcript content at frame timestamp | MUST HAVE |
| **Markdown Generation** | Create a single markdown file with embedded screenshots | MUST HAVE |
| **Custom Output Path** | Allow user to specify where markdown and images are saved | MUST HAVE |

### 2.2 Detailed Requirements

#### A. Frame Extraction Logic
- **Change Detection Threshold:** Define sensitivity (e.g., 5% pixel difference = new frame)
- **Minimum Frame Interval:** Prevent capturing nearly identical frames (e.g., minimum 1-2 seconds between captures)
- **Image Format:** Save as PNG or JPEG (PNG recommended for quality)
- **Resolution:** Match source video resolution or allow downscaling option

#### B. Transcript Processing
- **Source Priority:** 
  1. Auto-generated captions (if available)
  2. Manual captions (if available)
  3. Fallback: Generic timestamps if no transcript exists
- **Timestamp Alignment:** Match screenshot timestamp to nearest transcript line
- **Context Window:** Use surrounding transcript text for filename (e.g., ±5 seconds)

#### C. Filename Generation
- **Format:** `[timestamp]_[descriptive_text].png`
  - Example: `00:45_explaining_data_modeling_concepts.png`
- **Text Cleaning:** 
  - Remove special characters
  - Replace spaces with underscores
  - Limit length (e.g., max 100 characters)
  - Handle non-English characters appropriately

#### D. Markdown Structure
```markdown
# [Video Title]

**Source:** [YouTube URL]  
**Duration:** [Video Length]  
**Captured:** [Date/Time]

---

## Frame 1 - [Timestamp]
![Description](path/to/screenshot1.png)

**Transcript Context:**
> [Relevant transcript text]

---

## Frame 2 - [Timestamp]
...
```

## 3. TECHNICAL REQUIREMENTS

### 3.1 Python Libraries (Recommended)

| Library | Purpose | Installation |
|---------|---------|--------------|
| `yt-dlp` | YouTube video download & transcript extraction | `pip install yt-dlp` |
| `opencv-python` | Video processing & frame extraction | `pip install opencv-python` |
| `Pillow` | Image processing & optimization | `pip install Pillow` |
| `imagehash` | Perceptual hashing for frame comparison | `pip install imagehash` |
| `youtube-transcript-api` | Alternative transcript fetching | `pip install youtube-transcript-api` |

### 3.2 Performance Considerations

- **Video Download:** Option to stream vs. full download (streaming preferred for large videos)
- **Memory Management:** Process frames in batches to avoid RAM overload
- **Parallel Processing:** Consider async operations for transcript + video processing
- **Storage Estimate:** 1080p video ≈ 0.5-2 MB per screenshot (depends on content complexity)

## 4. USER INPUTS & CONFIGURATION

### 4.1 Required Inputs
```python
{
    "youtube_url": "https://www.youtube.com/watch?v=...",
    "output_directory": "/path/to/save/markdown/and/images",
}
```

### 4.2 Optional Configuration
```python
{
    "sensitivity": 0.05,  # Frame change threshold (0-1)
    "min_interval_seconds": 2,  # Minimum seconds between captures
    "image_format": "png",  # or "jpg"
    "max_filename_length": 80,
    "include_transcript_in_markdown": True,
    "downscale_resolution": None  # or tuple like (1280, 720)
}
```

## 5. ERROR HANDLING & EDGE CASES

| Scenario | Handling Strategy |
|----------|-------------------|
| **No transcript available** | Use generic timestamp-based naming (`frame_00:45.png`) |
| **Private/restricted video** | Graceful error with clear message |
| **Very long videos (>2 hours)** | Progress bar + option to limit frame count |
| **No significant frame changes** | Set minimum capture (e.g., 1 frame per minute as fallback) |
| **Invalid output path** | Validate path, create directory if doesn't exist |
| **YouTube API rate limiting** | Implement retry logic with exponential backoff |

## 6. OUTPUT STRUCTURE

```
output_directory/
├── video_title.md
└── screenshots/
    ├── 00:00:15_introduction_to_topic.png
    ├── 00:01:32_showing_example_code.png
    └── 00:03:45_explaining_key_concept.png
```

## 7. SUCCESS CRITERIA

✅ Script successfully downloads video and transcript  
✅ Captures only visually distinct frames (no duplicates)  
✅ Generates human-readable filenames from transcript  
✅ Creates well-formatted Markdown document  
✅ Handles errors gracefully with informative messages  
✅ Completes processing within reasonable time (< 5 min for 10-min video)  

## 8. OPEN QUESTIONS FOR YOU

Before we start coding, I need clarity on:

1. **Frame Detection Sensitivity:** How aggressive should frame change detection be? (Low = more frames, High = fewer frames)
2. **Transcript Context Length:** How many words from transcript should be in filename? (e.g., 5-10 words?)
3. **Markdown Image Embedding:** Relative paths or absolute paths for images?
4. **Language Support:** Should we handle non-English transcripts?
5. **Video Download:** Keep downloaded video file or delete after processing?
6. **Duplicate Handling:** If script runs twice on same video, overwrite or create new folder?

## 9. NEXT STEPS

Once you confirm the above, I'll:
1. Build the core frame extraction logic
2. Implement transcript fetching & alignment
3. Create the filename generation algorithm
4. Build the Markdown generator
5. Add error handling & logging
6. Provide usage examples and documentation
