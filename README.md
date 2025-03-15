# YouTube Conversation Segment Extractor

This tool extracts segments from YouTube videos where two or more people are talking in a static frame (like interviews, panels, or conversations).

## Features

- Downloads YouTube videos using the provided URL via yt-dlp
- Extracts frames at regular intervals
- Analyzes frames using OpenCV's face detection to identify those with multiple people
- Identifies continuous segments where multiple people are talking in a static frame
- Extracts these segments as separate video files

## Requirements

- Python 3.7+
- OpenCV
- yt-dlp

## Installation

1. Clone this repository or download the files
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

Run the script:

```bash
python yt_dlp_video_analyzer.py
```

When prompted, enter the YouTube video URL.

### Command-Line Interface

For more flexibility, use the command-line interface:

```bash
python yt_dlp_extract_conversations.py --url "https://www.youtube.com/watch?v=VIDEO_ID"
```

#### Available Options

- `--url`: YouTube video URL
- `--sampling-rate`: Number of frames to sample per second (default: 0.5)
- `--min-duration`: Minimum duration of conversation segments in seconds (default: 3.0)
- `--output-dir`: Directory to save the extracted segments (default: 'segments')
- `--video-dir`: Directory to save the downloaded videos (default: 'videos')
- `--frames-dir`: Directory to save the extracted frames (default: 'frames')

Example:

```bash
python yt_dlp_extract_conversations.py --url "https://www.youtube.com/watch?v=VIDEO_ID" --sampling-rate 1.0 --min-duration 5.0
```

## How It Works

1. **Download**: The script downloads the YouTube video using yt-dlp
2. **Frame Extraction**: It extracts frames at regular intervals based on the sampling rate
3. **Frame Analysis**: Each frame is analyzed using OpenCV's face detection to:
   - Count the number of faces in the frame
   - Determine if it's a static conversation setting (2+ faces)
4. **Segment Identification**: Continuous sequences of frames with 2+ faces are identified as segments
5. **Segment Extraction**: These segments are extracted as separate video files

## Output

The script creates the following directories:

- `videos`: Contains the downloaded YouTube videos
- `frames`: Contains the extracted frames
- `segments`: Contains the extracted video segments

## Notes

- The accuracy of segment detection depends on the quality of OpenCV's face detection
- Processing long videos may take significant time
- Adjust the sampling rate to balance accuracy vs. processing time (higher sampling rate = more accurate but slower) 


## Tuning Recommendations
For longer videos (>30 minutes):
-Reduce the sampling rate (e.g., 0.25 or 0.1) to speed up processing
-Increase the minimum duration (e.g., 5.0 or 10.0) to focus on significant conversation segments
-For higher precision:
-Increase the sampling rate (e.g., 1.0 or 2.0) for more accurate segment boundaries
-You may need to modify the face detection parameters in the code for better face detection
-For videos with quick cuts or brief conversations:
-Increase the sampling rate (e.g., 1.0 or higher)
-Decrease the minimum duration (e.g., 1.0 or 2.0)
-For panel discussions or interviews:
-The default parameters usually work well
-Consider increasing the minimum duration if you want to focus on extended discussions
