# YouTube Frame Extractor Script

I'll build this incrementally so you understand each component. Here's the complete production-ready script:---

## 📦 Installation Instructions

```bash
# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install required packages
pip install yt-dlp opencv-python pillow imagehash youtube-transcript-api
```

---

## 🚀 How to Use

### Basic Usage:
```python
from youtube_frame_extractor import YouTubeFrameExtractor

# Replace these with your values
extractor = YouTubeFrameExtractor(
    youtube_url="https://www.youtube.com/watch?v=YOUR_VIDEO_ID",
    output_directory="./my_video_frames"
)

# Run the extraction
extractor.process()
```

### Advanced Configuration:
```python
extractor = YouTubeFrameExtractor(
    youtube_url="YOUR_URL",
    output_directory="./output",
    sensitivity=0.03,  # More sensitive (more frames)
    min_interval_seconds=3,  # Capture max every 3 seconds
    image_format="jpg",  # Use JPG instead of PNG
    max_filename_length=60  # Shorter filenames
)

extractor.process(keep_video=True)  # Keep downloaded video
```

---

## 🔧 Key Features Implemented

✅ **Frame Change Detection** - Uses perceptual hashing (imagehash) to detect visual changes  
✅ **Transcript Integration** - Automatically fetches YouTube captions  
✅ **Smart Naming** - Generates contextual filenames from transcript  
✅ **Progress Logging** - Clear console output at each step  
✅ **Error Handling** - Graceful fallbacks when transcript unavailable  
✅ **Markdown Generation** - Clean, structured documentation  
✅ **Cleanup Option** - Can delete video file after processing  

---

## 📊 What Happens:

1. **Downloads video** using yt-dlp
2. **Fetches transcript** via YouTube Transcript API
3. **Processes frames** using OpenCV
4. **Detects changes** with perceptual hashing
5. **Names files** based on transcript context
6. **Generates markdown** with embedded images

---

## ⚙️ Tuning Parameters:

- **`sensitivity`**: `0.01` = very sensitive (many frames), `0.1` = less sensitive (fewer frames)
- **`min_interval_seconds`**: Prevents capturing nearly identical frames
- **`image_format`**: `"png"` = higher quality, `"jpg"` = smaller files

---

## 🐛 Troubleshooting:

**"No transcript available"** → Video doesn't have captions. Script will use generic timestamps.

**"Invalid YouTube URL"** → Check URL format. Should be `youtube.com/watch?v=...` or `youtu.be/...`

**Memory issues on long videos** → Increase `min_interval_seconds` or process shorter sections.

---

**Want me to add any features?** (e.g., progress bars, video section selection, OCR text extraction?)
