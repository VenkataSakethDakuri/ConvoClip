import os
import cv2
import numpy as np
import time
import subprocess
from moviepy.editor import VideoFileClip
from tqdm import tqdm

class YtDlpVideoAnalyzer:
    def __init__(self, sampling_rate=1):
        """
        Initialize the YtDlpVideoAnalyzer. 
        
        Args:
            sampling_rate (int): Number of frames to sample per second
        """
        self.sampling_rate = sampling_rate
        
        # Load the face detector
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
    def download_youtube_video(self, youtube_url, output_path="videos"):
        """
        Download a YouTube video using yt-dlp.
        
        Args:
            youtube_url (str): URL of the YouTube video
            output_path (str): Directory to save the video
            
        Returns:
            str: Path to the downloaded video file
        """
        print(f"Downloading video from {youtube_url}...")
        
        # Create output directory if it doesn't exist
        if not os.path.exists(output_path):
            os.makedirs(output_path)
            
        # Generate a filename based on the video ID
        video_id = youtube_url.split("v=")[1].split("&")[0]
        filepath = os.path.join(output_path, f"{video_id}.mp4")
        
        # Download the video if it doesn't already exist
        if not os.path.exists(filepath):
            # Use yt-dlp to download the video
            command = [
                "yt-dlp", 
                "-f", "best[ext=mp4]", 
                "-o", filepath, 
                youtube_url
            ]
            
            try:
                subprocess.run(command, check=True)
                print(f"Video downloaded to {filepath}")
            except subprocess.CalledProcessError as e:
                print(f"Error downloading video: {e}")
                return None
            
        else:
            print(f"Video already exists at {filepath}")
            
        return filepath
    
    def extract_frames(self, video_path, output_path="frames"):
        """
        Extract frames from the video at regular intervals.
        
        Args:
            video_path (str): Path to the video file
            output_path (str): Directory to save the frames
            
        Returns:
            list: List of dictionaries containing frame information
        """
        print(f"Extracting frames from {video_path}...")
        
        # Create output directory if it doesn't exist
        if not os.path.exists(output_path):
            os.makedirs(output_path)
            
        # Open the video
        cap = cv2.VideoCapture(video_path)
        
        # Get video properties
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = frame_count / fps
        
        print(f"Video properties: {fps} FPS, {frame_count} frames, {duration:.2f} seconds")
        
        # Calculate frame interval based on sampling rate
        frame_interval = int(fps / self.sampling_rate)
        
        frames_info = []
        frame_idx = 0
        
        # Calculate total frames to process
        total_frames_to_process = frame_count // frame_interval + 1
        
        # Create progress bar
        pbar = tqdm(total=total_frames_to_process, desc="Extracting frames")
        
        while True:
            ret, frame = cap.read()
            
            if not ret:
                break
                
            # Process only every nth frame based on sampling rate
            if frame_idx % frame_interval == 0:
                timestamp = frame_idx / fps
                frame_path = os.path.join(output_path, f"frame_{frame_idx}.jpg")
                
                # Save the frame
                cv2.imwrite(frame_path, frame)
                
                frames_info.append({
                    "frame_idx": frame_idx,
                    "timestamp": timestamp,
                    "path": frame_path
                })
                
                # Update progress bar
                pbar.update(1)
                
            frame_idx += 1
            
        cap.release()
        pbar.close()
        print(f"Extracted {len(frames_info)} frames")
        return frames_info
    
    def analyze_frame(self, frame_path):
        """
        Analyze a frame using OpenCV to detect faces.
        
        Args:
            frame_path (str): Path to the frame image
            
        Returns:
            dict: Analysis results including number of people and if it's a static frame
        """
        # Read the image
        img = cv2.imread(frame_path)
        
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Detect faces
        faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
        
        # Count the number of faces
        people_count = len(faces)
        
        # Determine if it's a static frame (simple heuristic: if there are 2+ faces, it's likely a conversation)
        is_static_conversation = people_count >= 2
        
        return {
            "people_count": people_count,
            "is_static_conversation": is_static_conversation
        }
    
    def find_conversation_segments(self, video_path, frames_info):
        """
        Find segments in the video where multiple people are talking in a static frame.
        
        Args:
            video_path (str): Path to the video file
            frames_info (list): List of dictionaries containing frame information
            
        Returns:
            list: List of dictionaries containing segment information
        """
        print("Analyzing frames to find conversation segments...")
        
        # Analyze each frame with a progress bar
        for i, frame_info in enumerate(tqdm(frames_info, desc="Analyzing frames")):
            analysis = self.analyze_frame(frame_info["path"])
            
            # Add analysis results to frame info
            frames_info[i]["people_count"] = analysis["people_count"]
            frames_info[i]["is_static_conversation"] = analysis["is_static_conversation"]
        
        # Find segments with multiple people in static conversation
        segments = []
        current_segment = None
        
        print("Identifying conversation segments...")
        for i, frame_info in enumerate(frames_info):
            if frame_info["is_static_conversation"]:
                # Start a new segment or extend the current one
                if current_segment is None:
                    current_segment = {
                        "start_time": frame_info["timestamp"],
                        "start_frame": frame_info["frame_idx"],
                        "frames": [frame_info]
                    }
                else:
                    current_segment["frames"].append(frame_info)
            elif current_segment is not None:
                # End the current segment
                current_segment["end_time"] = frames_info[i-1]["timestamp"]
                current_segment["end_frame"] = frames_info[i-1]["frame_idx"]
                current_segment["duration"] = current_segment["end_time"] - current_segment["start_time"]
                
                # Only add segments that are long enough (at least 3 seconds)
                if current_segment["duration"] >= 3:
                    segments.append(current_segment)
                
                current_segment = None
        
        # Handle the last segment if it exists
        if current_segment is not None:
            current_segment["end_time"] = frames_info[-1]["timestamp"]
            current_segment["end_frame"] = frames_info[-1]["frame_idx"]
            current_segment["duration"] = current_segment["end_time"] - current_segment["start_time"]
            
            if current_segment["duration"] >= 3:
                segments.append(current_segment)
        
        print(f"Found {len(segments)} conversation segments")
        return segments
    
    def extract_segments(self, video_path, segments, output_path="segments"):
        """
        Extract the identified segments from the video.
        
        Args:
            video_path (str): Path to the video file
            segments (list): List of dictionaries containing segment information
            output_path (str): Directory to save the segments
            
        Returns:
            list: List of paths to the extracted segment videos
        """
        print(f"Extracting {len(segments)} segments from {video_path}...")
        
        # Create output directory if it doesn't exist
        if not os.path.exists(output_path):
            os.makedirs(output_path)
            
        segment_paths = []
        
        # Load the video
        video = VideoFileClip(video_path)
        
        # Create progress bar
        pbar = tqdm(total=len(segments), desc="Extracting segments")
        
        for i, segment in enumerate(segments):
            start_time = segment["start_time"]
            end_time = segment["end_time"]
            
            # Extract the segment
            segment_clip = video.subclip(start_time, end_time)
            
            # Generate a filename
            segment_path = os.path.join(output_path, f"segment_{i+1}_{start_time:.2f}_{end_time:.2f}.mp4")
            
            # Save the segment
            segment_clip.write_videofile(segment_path, codec="libx264", audio_codec="aac", verbose=False, logger=None)
            
            segment_paths.append(segment_path)
            pbar.update(1)
        
        # Close the video and progress bar
        video.close()
        pbar.close()
        
        return segment_paths

def main():
    # Get YouTube URL from user input
    youtube_url = input("Enter the YouTube video URL: ")
    
    # Initialize the analyzer
    analyzer = YtDlpVideoAnalyzer(sampling_rate=0.5)  # Sample 1 frame every 2 seconds
    
    # Download the video
    video_path = analyzer.download_youtube_video(youtube_url)
    
    if video_path is None:
        print("Failed to download the video. Exiting.")
        return
    
    # Extract frames
    frames_info = analyzer.extract_frames(video_path)
    
    # Find conversation segments
    segments = analyzer.find_conversation_segments(video_path, frames_info)
    
    # Extract segments
    segment_paths = analyzer.extract_segments(video_path, segments)
    
    print(f"Extracted {len(segment_paths)} conversation segments")
    for path in segment_paths:
        print(f"- {path}")

if __name__ == "__main__":
    main() 