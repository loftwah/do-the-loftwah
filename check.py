import os
from dotenv import load_dotenv
import numpy as np
import librosa
# Don't import moviepy until after this script runs

# Load environment variables
load_dotenv()
TRACK_PATH = os.getenv("TRACK_PATH")
IMAGE_PATH = os.getenv("IMAGE_PATH")
TITLE = os.getenv("TITLE")
OUTPUT_PATH = os.getenv("OUTPUT_PATH")

print("Environment variables loaded:")
print(f"TRACK_PATH: {TRACK_PATH}")
print(f"IMAGE_PATH: {IMAGE_PATH}")
print(f"TITLE: {TITLE}")
print(f"OUTPUT_PATH: {OUTPUT_PATH}")

# Verify files exist
print(f"\nChecking if files exist:")
print(f"TRACK_PATH exists: {os.path.exists(TRACK_PATH)}")
print(f"IMAGE_PATH exists: {os.path.exists(IMAGE_PATH)}")

# Test librosa load
print("\nTesting librosa load...")
try:
    y, sr = librosa.load(TRACK_PATH, duration=10)  # Just load first 10 seconds for testing
    print(f"Successfully loaded audio with librosa: {len(y)} samples at {sr}Hz")
    
    # Test beat detection
    tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
    print(f"Detected tempo: {tempo} BPM with {len(beats)} beats")
except Exception as e:
    print(f"Error loading audio with librosa: {e}")

print("\nDiagnostics complete. Now try running the full script after reinstalling moviepy.")