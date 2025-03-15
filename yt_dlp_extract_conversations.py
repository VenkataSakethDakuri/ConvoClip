#!/usr/bin/env python3
import os
import argparse
from yt_dlp_video_analyzer import YtDlpVideoAnalyzer

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Extract segments from YouTube videos where multiple people are talking in a static frame."
    )
    
    parser.add_argument(
        "--url", 
        type=str, 
        help="YouTube video URL"
    )
    
    parser.add_argument(
        "--sampling-rate", 
        type=float, 
        default=0.5,
        help="Number of frames to sample per second (default: 0.5)"
    )
    
    parser.add_argument(
        "--min-duration", 
        type=float, 
        default=3.0,
        help="Minimum duration of conversation segments in seconds (default: 3.0)"
    )
    
    parser.add_argument(
        "--output-dir", 
        type=str, 
        default="segments",
        help="Directory to save the extracted segments (default: 'segments')"
    )
    
    parser.add_argument(
        "--video-dir", 
        type=str, 
        default="videos",
        help="Directory to save the downloaded videos (default: 'videos')"
    )
    
    parser.add_argument(
        "--frames-dir", 
        type=str, 
        default="frames",
        help="Directory to save the extracted frames (default: 'frames')"
    )
    
    return parser.parse_args()

def main():
    """Main function."""
    args = parse_args()
    
    # Get YouTube URL
    youtube_url = args.url
    if not youtube_url:
        youtube_url = input("Enter the YouTube video URL: ")
    
    # Initialize the analyzer
    analyzer = YtDlpVideoAnalyzer(sampling_rate=args.sampling_rate)
    
    # Download the video
    video_path = analyzer.download_youtube_video(youtube_url, output_path=args.video_dir)
    
    if video_path is None:
        print("Failed to download the video. Exiting.")
        return
    
    # Extract frames
    frames_info = analyzer.extract_frames(video_path, output_path=args.frames_dir)
    
    # Find conversation segments
    segments = analyzer.find_conversation_segments(video_path, frames_info)
    
    # Filter segments by minimum duration
    segments = [s for s in segments if s["duration"] >= args.min_duration]
    
    # Extract segments
    segment_paths = analyzer.extract_segments(video_path, segments, output_path=args.output_dir)
    
    print(f"Extracted {len(segment_paths)} conversation segments")
    for path in segment_paths:
        print(f"- {path}")

if __name__ == "__main__":
    main() 