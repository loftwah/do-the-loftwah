import os
from dotenv import load_dotenv
import librosa
import numpy as np
from moviepy.editor import AudioFileClip, ImageClip, CompositeVideoClip, TextClip, ColorClip, vfx
from moviepy.video.fx.resize import resize
from moviepy.video.fx.blackwhite import blackwhite
import PIL
from PIL import Image
import moviepy.config as mpconf
import math
import random

# Add ANTIALIAS if it doesn't exist (for Pillow 9.0.0+)
if not hasattr(Image, 'ANTIALIAS'):
    Image.ANTIALIAS = Image.LANCZOS  # LANCZOS is the replacement for ANTIALIAS

# Set ImageMagick path for MoviePy (installed via Homebrew on macOS)
mpconf.change_settings({"IMAGEMAGICK_BINARY": "/opt/homebrew/bin/convert"})

# Load environment variables
load_dotenv()
TRACK_PATH = os.getenv("TRACK_PATH", "do_the_loftwah.mp3")
IMAGE_PATH = os.getenv("IMAGE_PATH", "cover.jpg")
TITLE = os.getenv("TITLE", "Do the Loftwah")
OUTPUT_PATH = os.getenv("OUTPUT_PATH", "do_the_loftwah.mp4")
BG_COLOR = os.getenv("BG_COLOR", "#000000")  # Default to black background

print(f"Creating video from {TRACK_PATH} and {IMAGE_PATH}")

# Video settings
WIDTH, HEIGHT = 1920, 1080
FPS = 24

# Load audio
audio = AudioFileClip(TRACK_PATH)
duration = audio.duration
print(f"Audio duration: {duration:.2f} seconds")

# Analyze audio for beats and amplitude
y, sr = librosa.load(TRACK_PATH)
tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
beat_times = librosa.frames_to_time(beats, sr=sr)
print(f"Detected tempo: {float(tempo):.2f} BPM with {len(beat_times)} beats")

# Calculate amplitude for visualization effects
hop_length = 512
amplitude = np.abs(librosa.stft(y, hop_length=hop_length))
amplitude_db = librosa.amplitude_to_db(amplitude, ref=np.max)
amplitude_norm = (amplitude_db - amplitude_db.min()) / (amplitude_db.max() - amplitude_db.min())

# Create a function to get amplitude at a specific time
def get_amplitude_at_time(t):
    frame_idx = int(t * sr / hop_length)
    if frame_idx >= amplitude_norm.shape[1]:
        frame_idx = amplitude_norm.shape[1] - 1
    # Take mean across frequency bins for overall energy
    return np.mean(amplitude_norm[:, frame_idx])

# Create background
background = ColorClip((WIDTH, HEIGHT), color=BG_COLOR).set_duration(duration)

# Load image and apply initial effects
img = ImageClip(IMAGE_PATH)
# Make sure image maintains aspect ratio but fits nicely in frame
img_w, img_h = img.size
target_size = min(WIDTH * 0.6, HEIGHT * 0.6)  # Take up 60% of the smaller dimension
scale = min(target_size / img_w, target_size / img_h)
img = img.resize(width=img_w * scale)

# Create more dynamic visual effects that respond to the music
def dynamic_zoom_and_pulse(t):
    # Base size modulation on beat proximity and amplitude
    amp = get_amplitude_at_time(t) * 0.5  # Scale amplitude effect
    
    # Check if on or near beat
    on_beat = False
    beat_intensity = 0
    for bt in beat_times:
        beat_distance = abs(t - bt)
        if beat_distance < 0.1:  # Within 100ms of a beat
            on_beat = True
            beat_intensity = max(beat_intensity, 1 - (beat_distance * 10))  # Higher for closer beats
    
    # Base zoom that gradually varies with time for subtle movement
    base_zoom = 1.0 + 0.05 * math.sin(t * 0.5)
    
    # Add pulse on beats
    if on_beat:
        # Stronger effect on the beat
        zoom = base_zoom + (0.2 * beat_intensity)
    else:
        # Subtle amplitude-based effect between beats
        zoom = base_zoom + (0.1 * amp)
    
    return zoom

# Apply the dynamic effect
img_fx = img.fx(
    resize, 
    lambda t: dynamic_zoom_and_pulse(t)
)

# Add a subtle rotation effect based on beats
def rotate_on_beat(gf, t):
    img = gf(t)
    
    # Check if near a beat
    for bt in beat_times:
        beat_distance = abs(t - bt)
        if beat_distance < 0.1:
            # Apply subtle rotation on beats, more pronounced closer to the beat
            intensity = 1 - (beat_distance * 10)
            angle = 2 * intensity * math.sin(t * 4)  # Small oscillating rotation
            return vfx.rotate(img, angle)
    
    return img

# Apply rotation effect
img_fx = img_fx.fl(rotate_on_beat)

# Add a pulsing glow/shadow effect
def add_glow_effect(gf, t):
    # Create glow based on music amplitude
    amp = get_amplitude_at_time(t)
    
    # Base image
    img = gf(t)
    
    # Only apply glow on strong beats or high amplitude
    on_strong_beat = False
    for bt in beat_times:
        if abs(t - bt) < 0.05:  # Even tighter timing for glow effect
            on_strong_beat = True
            break
    
    if on_strong_beat or amp > 0.7:  # Only on strong beats or high amplitude
        # Amount of blur/glow depends on amplitude
        glow_amount = max(0.5, amp) * 5
        glow = vfx.gaussian_blur(img, glow_amount)
        return vfx.add_plugin(img, glow, amp)
    
    return img

# Apply the glow effect (wrapped in try-except in case the effect isn't available)
try:
    img_fx = img_fx.fl(add_glow_effect)
except:
    print("Warning: Could not apply glow effect. Continuing without it.")

# Create primary title text with better styling
title_font = 'Arial-Bold' if os.path.exists('/Library/Fonts/Arial Bold.ttf') else 'Arial'
main_text = TextClip(
    TITLE,
    fontsize=100,
    color='white',
    font=title_font,
    stroke_color='black',
    stroke_width=3,
    method='label'
)

# Add text animation
def animate_text(t):
    # Get current amplitude
    amp = get_amplitude_at_time(t)
    
    # Base scale varies slightly with time for continuous movement
    scale = 1.0 + 0.02 * math.sin(t * 2)
    
    # Enhanced scale on beats
    for bt in beat_times:
        if abs(t - bt) < 0.1:
            intensity = 1 - (abs(t - bt) * 10)
            scale += 0.1 * intensity
    
    # Add amplitude influence
    scale += 0.05 * amp
    
    return scale

# Apply text animation
main_text = main_text.fx(
    resize,
    lambda t: animate_text(t)
)

# Position at the bottom center with proper margin
main_text = main_text.set_position(('center', HEIGHT - 150)).set_duration(duration)

# Add subtitle text (tempo and beat info)
info_text = f"{float(tempo):.1f} BPM"
sub_text = TextClip(
    info_text,
    fontsize=40,
    color='white',
    font='Arial',
    method='label'
)
sub_text = sub_text.set_position(('center', HEIGHT - 80)).set_duration(duration)

# Create a pulsing circle visualization in the background
def make_beat_circle(t):
    # Create a circle that pulses with the beats
    circle_size = (WIDTH, HEIGHT)
    circle = ColorClip(circle_size, col=(0, 0, 0, 0))  # Transparent background
    
    # Draw circles on/near beats
    for bt in beat_times:
        time_diff = t - bt
        # Only show expanding circles for 1 second after each beat
        if 0 <= time_diff < 1:
            # Circle expands outward from the beat
            radius = int(time_diff * 500)  # Expands to 500px in 1 second
            opacity = max(0, 1 - time_diff)  # Fade out over 1 second
            
            # Draw circle (this is just a placeholder since we can't actually draw here)
            # In a real implementation, you'd need to use PIL to draw on the circle
            
    return circle

# Combine all elements with proper layering
video = CompositeVideoClip([
    background,
    img_fx.set_position('center'),
    main_text,
    sub_text
], size=(WIDTH, HEIGHT))

# Add subtle zoom in/out effect to the entire composition
def subtle_zoom(t):
    # Very subtle zoom effect that varies with time
    return 1 + 0.01 * math.sin(t * 0.7)

# Apply a very subtle zoom to the whole composition
video = video.fx(resize, lambda t: subtle_zoom(t))

# Add audio
final_video = video.set_audio(audio)

# Write video file
print(f"Writing video to {OUTPUT_PATH}...")
final_video.write_videofile(OUTPUT_PATH, fps=FPS, codec='libx264', audio_codec='aac')
print("Done!")