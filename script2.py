import os
from dotenv import load_dotenv
import librosa
import numpy as np
from moviepy.editor import AudioFileClip, ImageClip, ColorClip, CompositeVideoClip, TextClip, VideoClip
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter
import moviepy.config as mpconf
import colorsys
import sys

# ======== COLOR SETTINGS (EASY TO CUSTOMIZE) ========
# Main colors - Change these to customize the look of your video
TITLE_TEXT_COLOR = 'white'       # Color of the title text
PROGRESS_BAR_COLOR = 'white'     # Color of the progress bar
BACKGROUND_COLOR = (0, 0, 0)     # Background color (RGB tuple)

# Color theme controls (HSV model)
# Base value for hue (0-1) - Controls the starting color of effects
BASE_HUE = 0.6                   # 0.6 = blue, 0.0 = red, 0.3 = green, etc.
COLOR_SATURATION = 0.8           # 0-1, higher = more vivid colors
COLOR_BRIGHTNESS = 0.7           # 0-1, higher = brighter colors

# Image settings
IMAGE_OPACITY = 0.8              # 0-1, higher = more visible background image
IMAGE_BRIGHTNESS = 0.6           # 0-1, higher = brighter background image

# ======== END COLOR SETTINGS ========

# Set ImageMagick path (adjust this if your setup's different)
mpconf.change_settings({"IMAGEMAGICK_BINARY": "/opt/homebrew/bin/convert"})

# Load environment variables
load_dotenv()
TRACK_PATH = os.getenv("TRACK_PATH", "do_the_loftwah.mp3")
IMAGE_PATH = os.getenv("IMAGE_PATH", "cover.jpg")
TITLE = os.getenv("TITLE", "Do the Loftwah")
OUTPUT_PATH = os.getenv("OUTPUT_PATH2", "do_the_loftwah-2.mp4")

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

# Compute RMS for visual effects
frame_length = 2048
hop_length = 512
rms = librosa.feature.rms(y=y, frame_length=frame_length, hop_length=hop_length)[0]
rms_times = librosa.times_like(rms, sr=sr, hop_length=hop_length)
min_rms = np.min(rms)
max_rms = np.max(rms)

# Compute spectral features for more advanced effects
spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
spectral_times = librosa.times_like(spectral_centroid, sr=sr)
min_spectral = np.min(spectral_centroid)
max_spectral = np.max(spectral_centroid)

# Video dimensions
w_video, h_video = 1920, 1080

# Black background
background = ColorClip(size=(w_video, h_video), color=BACKGROUND_COLOR).set_duration(duration)

# Load image with error handling
try:
    print(f"Loading image: {IMAGE_PATH}")
    image_clip = ImageClip(IMAGE_PATH).set_duration(duration)
    image_loaded = True
except Exception as e:
    print(f"Error loading image: {e}")
    print("Creating a solid color background instead")
    image_clip = ColorClip(size=(w_video, h_video), color=(30, 30, 30)).set_duration(duration)
    image_loaded = False

# Patch the resizer function in moviepy to fix ANTIALIAS issue
def patched_resizer(image, newsize):
    pilim = Image.fromarray(image)
    
    # Handle if newsize contains floats instead of integers
    if isinstance(newsize, tuple) and len(newsize) == 2:
        # When newsize is a tuple of scaling factors
        h, w = image.shape[:2]
        if isinstance(newsize[0], (float, np.float64, np.float32)):
            new_w = int(w * newsize[0])
            new_h = int(h * newsize[1])
            newsize = (new_w, new_h)
    
    # Ensure newsize contains integers
    if not isinstance(newsize[0], int):
        newsize = tuple(int(round(float(x))) for x in newsize)
    
    # Use LANCZOS instead of ANTIALIAS (which is deprecated in newer PIL versions)
    resample_method = getattr(Image, "LANCZOS", getattr(Image.Resampling, "LANCZOS", Image.BICUBIC))
    
    # Reverse width and height for PIL's resize (it expects width, height)
    resized_pil = pilim.resize(newsize[::-1], resample_method)
    return np.array(resized_pil)

# Monkey patch the resizer function in moviepy
from moviepy.video.fx.resize import resizer
import moviepy.video.fx.resize
moviepy.video.fx.resize.resizer = patched_resizer

# Apply subtle movement to image
def process_bg_image(image, t):
    # Convert PIL image to numpy array, apply blur and reduce opacity
    img = Image.fromarray(image)
    
    # Blur amount based on audio energy
    rms_value = np.interp(t, rms_times, rms)
    blur_amount = 2 + (rms_value - min_rms) / (max_rms - min_rms) * 3  # Blur between 2 and 5
    img = img.filter(ImageFilter.GaussianBlur(radius=blur_amount))
    
    # Reduce brightness and add a slight tint
    enhancer = ImageEnhance.Brightness(img)
    img = enhancer.enhance(IMAGE_BRIGHTNESS)  # Control image brightness
    
    return np.array(img)

if image_loaded:
    # Apply the image processing
    image_clip = image_clip.fl(lambda gf, t: process_bg_image(gf(t), t))
    
    try:
        # Resize the image to fill the screen with some room for movement
        image_clip = image_clip.resize(height=h_video * 1.1)  # Make it slightly larger than the screen
        print("Successfully resized background image")
    except Exception as e:
        print(f"Error resizing image: {e}")
        print("Using original image size")

    # Set position with subtle movement
    image_clip = image_clip.set_position('center')

    # Set image opacity
    image_clip = image_clip.set_opacity(IMAGE_OPACITY)

# Title effects with enhanced waveform response
def create_title_clip():
    # Create the base title clip with larger font size - FORCE RGB WHITE
    try:
        # Force white color using RGB tuple instead of string
        base_title = TextClip(TITLE, fontsize=90, color=(255, 255, 255), font='Arial-Bold', kerning=5)
        print("Created title with custom font")
    except Exception as e:
        print(f"Warning: Could not create text clip with specified font. Using default. Error: {e}")
        # Force white color using RGB tuple instead of string
        base_title = TextClip(TITLE, fontsize=90, color=(255, 255, 255), kerning=5)
        print("Created title with default font")
    
    # Make it last the entire duration
    base_title = base_title.set_duration(duration)
    
    # Position in center
    base_title = base_title.set_position('center')
    
    # Apply glow effects to the title based on audio
    def title_transform(image, t):
        # Get current audio features
        rms_value = np.interp(t, rms_times, rms)
        energy_factor = (rms_value - min_rms) / (max_rms - min_rms)
        
        # Get current spectral centroid for rainbow color
        spectral_value = np.interp(t, spectral_times, spectral_centroid)
        spectral_factor = (spectral_value - min_spectral) / (max_spectral - min_spectral)
        
        # Calculate a time-based rainbow hue that cycles slowly
        time_hue = (t / 10) % 1.0  # Complete color cycle every 10 seconds
        # Add spectral influence to create audio-reactive rainbow
        rainbow_hue = (BASE_HUE + time_hue + 0.3 * spectral_factor) % 1.0
        
        # Check if we're on a beat
        on_beat = False
        beat_distance = 1.0
        for beat_time in beat_times:
            dist = abs(t - beat_time)
            if dist < beat_distance:
                beat_distance = dist
            if dist < 0.1:  # Within 100ms of a beat
                on_beat = True
                break
        
        # Convert to PIL image for processing
        img = Image.fromarray(image)
        
        # For debugging - print the actual colors in the image
        if t < 0.1:  # Only at the start to avoid console spam
            has_white = False
            for x in range(0, img.width, 10):  # Sample every 10 pixels
                for y in range(0, img.height, 10):
                    pixel = img.getpixel((x, y))
                    if len(pixel) > 3 and pixel[3] > 0:  # Non-transparent
                        if pixel[0] > 240 and pixel[1] > 240 and pixel[2] > 240:  # Near white
                            has_white = True
            print(f"Image has white pixels: {has_white}")
        
        # Always keep text pure white for better visibility
        r, g, b = 255, 255, 255
        
        # Create a colored version of the text
        colored_img = Image.new('RGBA', img.size)
        
        for x in range(img.width):
            for y in range(img.height):
                pixel = img.getpixel((x, y))
                if len(pixel) > 3 and pixel[3] > 0:  # If not fully transparent
                    # Force white for text
                    colored_img.putpixel((x, y), (r, g, b, pixel[3]))
                else:
                    colored_img.putpixel((x, y), (0, 0, 0, 0))
        
        # Apply glow effect based on audio energy
        result = Image.new('RGBA', img.size, (0, 0, 0, 0))
        
        # Determine glow intensity based on beat and energy
        if on_beat:
            # Stronger glow on beats
            glow_strength = 1.0 + energy_factor
            glow_radius = 5 + energy_factor * 10
        else:
            # Subtle glow otherwise
            glow_strength = 0.5 + (energy_factor * 0.5)
            glow_radius = 2 + energy_factor * 5
        
        # Create the glow effect with multiple layers
        for i in range(3):
            # Different radius for each layer
            current_radius = glow_radius * (1 - i * 0.3)
            
            # Create rainbow-colored glow layers
            layer_hue = (rainbow_hue + i * 0.2) % 1.0  # Each layer gets a different hue
            layer_r, layer_g, layer_b = [int(255 * c) for c in colorsys.hsv_to_rgb(
                layer_hue, COLOR_SATURATION, COLOR_BRIGHTNESS)]
            
            # Create colored layer
            glow_layer = Image.new('RGBA', img.size)
            for x in range(img.width):
                for y in range(img.height):
                    pixel = img.getpixel((x, y))
                    if len(pixel) > 3 and pixel[3] > 0:
                        alpha = min(255, int(pixel[3] * glow_strength * (1 - i * 0.3)))
                        glow_layer.putpixel((x, y), (layer_r, layer_g, layer_b, alpha))
                    else:
                        glow_layer.putpixel((x, y), (0, 0, 0, 0))
            
            # Blur the layer
            glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(radius=current_radius))
            
            # Composite onto result
            result = Image.alpha_composite(result, glow_layer)
        
        # Finally add the sharp WHITE text on top
        result = Image.alpha_composite(result, colored_img)
        
        # Apply scaling directly to the image (instead of using resize)
        if on_beat:
            # Quick expansion on beat
            scale_factor = 1.0 + 0.1 * (1.0 - beat_distance * 10) * energy_factor
            if scale_factor > 1.0:
                # Calculate new dimensions
                new_width = int(img.width * scale_factor)
                new_height = int(img.height * scale_factor)
                
                # Calculate offsets to keep centered
                offset_x = (new_width - img.width) // 2
                offset_y = (new_height - img.height) // 2
                
                # Create a new larger image with the scaled result
                scaled_result = Image.new('RGBA', (new_width, new_height), (0, 0, 0, 0))
                scaled_result.paste(result, (offset_x, offset_y))
                result = scaled_result
        
        # Convert to RGB before returning (this is crucial to avoid alpha channel issues)
        rgb_result = Image.new('RGB', result.size, (0, 0, 0))
        rgb_result.paste(result, (0, 0), result)
        
        return np.array(rgb_result)
    
    # Apply the transformation
    return base_title.fl(lambda gf, t: title_transform(gf(t), t))

# Progress bar
def make_progress_frame(t):
    img = Image.new('RGB', (w_video, 20), color='black')
    draw = ImageDraw.Draw(img)
    progress_width = int(w_video * t / duration)
    draw.rectangle([0, 0, progress_width, 20], fill=PROGRESS_BAR_COLOR)
    return np.array(img)

progress_clip = VideoClip(make_frame=make_progress_frame, duration=duration).set_position(('center', h_video - 20))

# Title glowing effect
def make_title_glow(t):
    # Create a transparent image
    img = Image.new('RGB', (w_video, h_video), color=(0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Get current RMS value for intensity
    rms_value = np.interp(t, rms_times, rms)
    energy_factor = (rms_value - min_rms) / (max_rms - min_rms)
    
    # Get current spectral centroid for rainbow color
    spectral_value = np.interp(t, spectral_times, spectral_centroid)
    spectral_factor = (spectral_value - min_spectral) / (max_spectral - min_spectral)
    
    # Check if we're on a beat
    on_beat = False
    for beat_time in beat_times:
        if abs(t - beat_time) < 0.1:  # Within 100ms of a beat
            on_beat = True
            break
    
    # Center of the screen
    center_x, center_y = w_video // 2, h_video // 2
    
    # Create a rainbow glow effect behind the title
    # Calculate a time-based rainbow hue that cycles slowly
    time_hue = (t / 10) % 1.0  # Complete color cycle every 10 seconds
    # Add spectral influence to create audio-reactive rainbow
    rainbow_hue = (BASE_HUE + time_hue + 0.3 * spectral_factor) % 1.0
    
    # Get the RGB values for the current hue
    r, g, b = [int(255 * c) for c in colorsys.hsv_to_rgb(
        rainbow_hue, COLOR_SATURATION, COLOR_BRIGHTNESS + 0.3 * energy_factor)]
    
    # Calculate title dimensions (approximate)
    title_width = len(TITLE) * 55  # Rough estimate based on 90px font
    title_height = 120  # Rough estimate
    
    # Draw glow behind title
    glow_radius = 200 + 100 * energy_factor
    if on_beat:
        glow_radius += 50  # Extra glow on beats
        
    for i in range(3):
        current_radius = glow_radius * (1 - i * 0.3)
        alpha = int(100 * (1 - i * 0.3) * energy_factor)
        
        # Draw radial gradient
        for radius in range(int(current_radius), 0, -20):
            # Reduce alpha as we move outward
            circle_alpha = int(alpha * (radius / current_radius))
            draw.ellipse(
                [center_x - radius, center_y - radius, center_x + radius, center_y + radius],
                outline=(r, g, b, circle_alpha),
                width=10
            )
    
    # Draw waveform above and below title
    window_duration = 0.1  # 100ms window
    start_sample = max(0, int((t - window_duration/2) * sr))
    end_sample = min(int((t + window_duration/2) * sr), len(y))
    
    if start_sample < end_sample:
        segment = y[start_sample:end_sample]
        if len(segment) > 0:
            # Normalize segment
            max_val = np.max(np.abs(segment))
            if max_val > 0:
                segment = segment / max_val
                
                # Draw waveform
                waveform_top = center_y - title_height - 60
                waveform_bottom = center_y + title_height + 60
                
                # Number of points to plot
                n_points = min(len(segment), 200)
                step = len(segment) // n_points if len(segment) > n_points else 1
                
                points_above = []
                points_below = []
                
                for i in range(0, len(segment), step):
                    if len(points_above) >= n_points:
                        break
                        
                    # X position spans from left of title to right of title
                    x = center_x - title_width + (title_width * 2 * i / len(segment))
                    
                    # Y position based on audio sample value
                    y_offset = segment[i] * 50 * (1 + energy_factor)
                    
                    # Points above and below title
                    points_above.append((x, waveform_top + y_offset))
                    points_below.append((x, waveform_bottom - y_offset))
                
                # Draw waveform lines with rainbow colors
                if len(points_above) > 1:
                    # Create a different hue for each waveform
                    wave_hue = (rainbow_hue + 0.5) % 1.0  # Complementary color to main glow
                    wave_r, wave_g, wave_b = [int(255 * c) for c in colorsys.hsv_to_rgb(
                        wave_hue, COLOR_SATURATION, COLOR_BRIGHTNESS)]
                    draw.line(points_above, fill=(wave_r, wave_g, wave_b), width=2)
                if len(points_below) > 1:
                    # Slightly different hue for bottom waveform
                    wave_hue2 = (rainbow_hue + 0.3) % 1.0
                    wave_r2, wave_g2, wave_b2 = [int(255 * c) for c in colorsys.hsv_to_rgb(
                        wave_hue2, COLOR_SATURATION, COLOR_BRIGHTNESS)]
                    draw.line(points_below, fill=(wave_r2, wave_g2, wave_b2), width=2)
    
    return np.array(img)

# Create clips - Create simplified title for better visibility if needed
try:
    title_glow = VideoClip(make_frame=make_title_glow, duration=duration)
    title_clip = create_title_clip()
    print("Successfully created title and glow effects")
    
    # Add an extra plain white text on top for guaranteed visibility
    try:
        plain_title = TextClip(TITLE, fontsize=90, color='white', method='label')
        plain_title = plain_title.set_duration(duration).set_position('center')
        has_plain_title = True
        print("Created additional plain title for visibility")
    except Exception as e:
        print(f"Could not create plain title: {e}")
        has_plain_title = False
except Exception as e:
    print(f"Error creating title effects: {e}")
    sys.exit(1)

# Composite all clips
clips_to_composite = [background]
if image_loaded:
    clips_to_composite.append(image_clip)
clips_to_composite.extend([
    title_glow,     # Glow and waveform effects
    title_clip,     # Centered title with effects
])

# Add the plain white title on top if we created one
if has_plain_title:
    clips_to_composite.append(plain_title)  # Extra plain white text for visibility

# Add progress bar last so it's always on top
clips_to_composite.append(progress_clip)

video = CompositeVideoClip(clips_to_composite)

# Add audio
video = video.set_audio(audio)

# Write the video
print(f"Writing video to {OUTPUT_PATH}...")
video.write_videofile(OUTPUT_PATH, fps=24, codec='libx264', audio_codec='aac')
print("Done!")