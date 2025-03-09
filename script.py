import os
from dotenv import load_dotenv
import librosa
import numpy as np
from moviepy.editor import AudioFileClip, ImageClip, ColorClip, CompositeVideoClip, TextClip, VideoClip
from PIL import Image, ImageDraw, ImageEnhance
import moviepy.config as mpconf

# Set ImageMagick path (adjust this if your setup's different)
mpconf.change_settings({"IMAGEMAGICK_BINARY": "/opt/homebrew/bin/convert"})

# Load environment variables
load_dotenv()
TRACK_PATH = os.getenv("TRACK_PATH", "do_the_loftwah.mp3")
IMAGE_PATH = os.getenv("IMAGE_PATH", "cover.jpg")
TITLE = os.getenv("TITLE", "Do the Loftwah")
OUTPUT_PATH = os.getenv("OUTPUT_PATH", "do_the_loftwah.mp4")

print(f"Creating video from {TRACK_PATH} and {IMAGE_PATH}")

# Load audio
audio = AudioFileClip(TRACK_PATH)
duration = audio.duration
y, sr = librosa.load(TRACK_PATH)
print(f"Audio duration: {duration:.2f} seconds")

# Analyze audio for beats and tempo
tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
beat_times = librosa.frames_to_time(beats, sr=sr)
print(f"Detected tempo: {float(tempo):.2f} BPM with {len(beat_times)} beats")

# Compute RMS for brightness adjustment
frame_length = 2048
hop_length = 512
rms = librosa.feature.rms(y=y, frame_length=frame_length, hop_length=hop_length)[0]
rms_times = librosa.times_like(rms, sr=sr, hop_length=hop_length)
min_rms = np.min(rms)
max_rms = np.max(rms)

# Video dimensions
w_video, h_video = 1920, 1080

# Black background
background = ColorClip(size=(w_video, h_video), color=(0, 0, 0)).set_duration(duration)

# Load image
image_clip = ImageClip(IMAGE_PATH).set_duration(duration)

# Panning effect (left to right)
def pan_func(t):
    start_x = -image_clip.w // 4
    end_x = w_video - image_clip.w * 3 // 4
    x = start_x + (end_x - start_x) * (t / duration)
    return (x, 'center')

image_clip = image_clip.set_position(pan_func)

# Patch the resizer function in moviepy to fix ANTIALIAS issue
def patched_resizer(image, newsize):
    pilim = Image.fromarray(image)
    
    # Handle if newsize contains floats instead of integers
    if isinstance(newsize, tuple) and len(newsize) == 2:
        # When newsize is a tuple of scaling factors
        h, w = image.shape[:2]
        if isinstance(newsize[0], (float, np.float64)):
            new_w = int(w * newsize[0])
            new_h = int(h * newsize[1])
            newsize = (new_w, new_h)
    
    # Ensure newsize contains integers
    newsize = tuple(int(round(x)) for x in newsize)
    
    # Use LANCZOS instead of ANTIALIAS (which is deprecated in newer PIL versions)
    resample_method = getattr(Image, "LANCZOS", getattr(Image.Resampling, "LANCZOS", Image.BICUBIC))
    
    # Reverse width and height for PIL's resize (it expects width, height)
    resized_pil = pilim.resize(newsize[::-1], resample_method)
    return np.array(resized_pil)

# Monkey patch the resizer function in moviepy
from moviepy.video.fx.resize import resizer
import moviepy.video.fx.resize
moviepy.video.fx.resize.resizer = patched_resizer

# Zoom on beats
def zoom_func(t):
    if len(beat_times) == 0:
        return 1
    idx = np.searchsorted(beat_times, t, side='right') - 1
    if idx >= 0:
        bt = beat_times[idx]
        time_since_beat = t - bt
        if time_since_beat < 0.5:  # 0.5s window
            return 1 + 0.1 * np.exp(-time_since_beat / 0.2)  # Max zoom 1.1, decays fast
    return 1

# Convert the zoom factor to a proper resize tuple
def apply_zoom(t):
    zoom = zoom_func(t)
    # Return a tuple of (width, height) representing the scale factor
    return (zoom, zoom)

image_clip = image_clip.resize(apply_zoom)

# Brightness adjustment based on RMS
def adjust_brightness(image, t):
    rms_value = np.interp(t, rms_times, rms)
    factor = 0.5 + (rms_value - min_rms) / (max_rms - min_rms) * 1.0  # 0.5 to 1.5 brightness
    enhancer = ImageEnhance.Brightness(Image.fromarray(image))
    return np.array(enhancer.enhance(factor))

image_clip = image_clip.fl(lambda gf, t: adjust_brightness(gf(t), t))

# Waveform visualization
def make_waveform_frame(t):
    window_duration = 1  # Last 1 second
    start_sample = max(0, int((t - window_duration) * sr))
    end_sample = int(t * sr)
    segment = y[start_sample:end_sample] if start_sample < end_sample else np.zeros(1)
    
    # Safe normalization to avoid NaN values
    max_abs = np.max(np.abs(segment))
    if max_abs > 0:  # Check if the segment contains any non-zero values
        segment = segment / max_abs  # Normalize
    else:
        segment = np.zeros(len(segment) if len(segment) > 0 else 1)
        
    waveform_width = 500
    waveform_height = 100
    img = Image.new('RGB', (waveform_width, waveform_height), color='black')
    draw = ImageDraw.Draw(img)
    color_factor = (np.interp(t, rms_times, rms) - min_rms) / (max_rms - min_rms)
    color = (int(255 * color_factor), 0, int(255 * (1 - color_factor)))  # Blue to red
    
    # Safety check for segment length
    if len(segment) <= 1:
        # Just draw a flat line in the middle if there's no valid audio segment
        draw.line([(0, waveform_height//2), (waveform_width, waveform_height//2)], fill=color, width=1)
    else:
        for i in range(waveform_width - 1):
            x0 = i
            idx1 = min(int(i / waveform_width * len(segment)), len(segment) - 1)
            idx2 = min(int((i + 1) / waveform_width * len(segment)), len(segment) - 1)
            
            # Ensure we don't get NaN values or index out of bounds
            y_val1 = segment[idx1] if not np.isnan(segment[idx1]) else 0
            y_val2 = segment[idx2] if not np.isnan(segment[idx2]) else 0
            
            y0 = int(waveform_height / 2 + (y_val1 * waveform_height / 2))
            x1 = i + 1
            y1 = int(waveform_height / 2 + (y_val2 * waveform_height / 2))
            
            draw.line([(x0, y0), (x1, y1)], fill=color, width=1)
            
    return np.array(img)

waveform_clip = VideoClip(make_frame=make_waveform_frame, duration=duration).set_position((100, h_video - 150))

# Flash effect on beats
def make_flash_mask(t):
    if len(beat_times) == 0:
        return 0
    idx = np.searchsorted(beat_times, t, side='right') - 1
    if idx >= 0:
        bt = beat_times[idx]
        time_since_beat = t - bt
        if time_since_beat < 0.1:  # 0.1s flash
            return 0.5 * np.exp(-time_since_beat / 0.05)  # Peak opacity 0.5
    return 0

# Create a VideoClip for opacity mask
flash_mask = VideoClip(lambda t: np.ones((h_video, w_video)) * make_flash_mask(t), 
                      duration=duration, ismask=True)
flash_clip = ColorClip(size=(w_video, h_video), color=(255, 255, 255)).set_duration(duration)
flash_clip = flash_clip.set_mask(flash_mask)

# Progress bar
def make_progress_frame(t):
    img = Image.new('RGB', (w_video, 20), color='black')
    draw = ImageDraw.Draw(img)
    progress_width = int(w_video * t / duration)
    draw.rectangle([0, 0, progress_width, 20], fill='white')
    return np.array(img)

progress_clip = VideoClip(make_frame=make_progress_frame, duration=duration).set_position(('center', h_video - 20))

# Title overlay
try:
    # Try with the specified font first
    title_clip = TextClip(TITLE, fontsize=48, color='white', font='Arial-Bold').set_duration(duration).set_position(('center', 'top'))
except Exception as e:
    print(f"Warning: Could not create text clip with specified font. Using default. Error: {e}")
    # Fall back to default font if Arial-Bold isn't available
    title_clip = TextClip(TITLE, fontsize=48, color='white').set_duration(duration).set_position(('center', 'top'))

# Smash it all together
video = CompositeVideoClip([background, image_clip, waveform_clip, flash_clip, progress_clip, title_clip])

# Add audio
video = video.set_audio(audio)

# Write the fucking video
print(f"Writing video to {OUTPUT_PATH}...")
video.write_videofile(OUTPUT_PATH, fps=24, codec='libx264', audio_codec='aac')
print("Done, motherfucker!")