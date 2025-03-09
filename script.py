import os
from dotenv import load_dotenv
import librosa
import numpy as np
from moviepy.editor import AudioFileClip, ImageClip, ColorClip, CompositeVideoClip, TextClip, VideoClip
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter
import moviepy.config as mpconf
import colorsys

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

# Video dimensions
w_video, h_video = 1920, 1080

# Black background
background = ColorClip(size=(w_video, h_video), color=(0, 0, 0)).set_duration(duration)

# Load image and make it less prominent
image_clip = ImageClip(IMAGE_PATH).set_duration(duration)

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
    img = enhancer.enhance(0.6)  # Dim the image
    
    return np.array(img)

# Apply the image processing
image_clip = image_clip.fl(lambda gf, t: process_bg_image(gf(t), t))

# Resize the image to fill the screen with some room for movement
image_clip = image_clip.resize(height=h_video * 1.1)  # Make it slightly larger than the screen

# Subtle position shift based on audio energy for background
def bg_position(t):
    # Subtle breathing effect for scale handled by video size
    
    # Get audio energy
    rms_value = np.interp(t, rms_times, rms)
    energy_factor = (rms_value - min_rms) / (max_rms - min_rms) * 0.5  # Scale to 0-0.5%
    
    # Calculate absolute position (subtle movement)
    x_shift = w_video * 0.01 * np.sin(t * 0.2) * energy_factor
    y_shift = h_video * 0.01 * np.cos(t * 0.15) * energy_factor
    
    # Return position as (x, y) tuple with the image centered and slight shift
    return ('center', 'center')

# Set position with subtle movement
image_clip = image_clip.set_position(bg_position)

# Title effects with enhanced waveform response
def create_title_clip():
    # Create the base title clip with larger font size
    try:
        base_title = TextClip(TITLE, fontsize=90, color='white', font='Arial-Bold', kerning=5)
    except Exception as e:
        print(f"Warning: Could not create text clip with specified font. Using default. Error: {e}")
        base_title = TextClip(TITLE, fontsize=90, color='white', kerning=5)
    
    # Make it last the entire duration
    base_title = base_title.set_duration(duration)
    
    # Position in center
    base_title = base_title.set_position('center')
    
    # Apply color and glow effects to the title based on audio
    def title_transform(image, t):
        # Get current audio features
        rms_value = np.interp(t, rms_times, rms)
        energy_factor = (rms_value - min_rms) / (max_rms - min_rms)
        
        # Get spectral information (brightness/tone of the sound)
        spectral_value = np.interp(t, spectral_times, spectral_centroid)
        spectral_factor = (spectral_value - np.min(spectral_centroid)) / (np.max(spectral_centroid) - np.min(spectral_centroid))
        
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
        
        # Color the title based on waveform characteristics
        # Higher frequencies = more blue, lower = more red
        hue = (0.6 + 0.4 * spectral_factor) % 1.0  # Hue ranges from blue-purple to red
        saturation = 0.8 - 0.2 * energy_factor  # Less saturation on louder parts
        lightness = 0.7 + 0.3 * energy_factor  # Brighter on louder parts
        
        r, g, b = [int(255 * c) for c in colorsys.hsv_to_rgb(hue, saturation, lightness)]
        
        # Create a colored version of the text
        colored_img = Image.new('RGBA', img.size)
        for x in range(img.width):
            for y in range(img.height):
                pixel = img.getpixel((x, y))
                if len(pixel) > 3 and pixel[3] > 0:  # If not fully transparent
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
            
            # Apply different hue shift for each layer
            layer_hue = (hue + i * 0.1) % 1.0
            layer_r, layer_g, layer_b = [int(255 * c) for c in colorsys.hsv_to_rgb(layer_hue, saturation, lightness)]
            
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
        
        # Finally add the sharp colored text on top
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
    draw.rectangle([0, 0, progress_width, 20], fill='white')
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
    
    # Check if we're on a beat
    on_beat = False
    for beat_time in beat_times:
        if abs(t - beat_time) < 0.1:  # Within 100ms of a beat
            on_beat = True
            break
    
    # Center of the screen
    center_x, center_y = w_video // 2, h_video // 2
    
    # Get spectral information
    spectral_value = np.interp(t, spectral_times, spectral_centroid)
    spectral_factor = (spectral_value - np.min(spectral_centroid)) / (np.max(spectral_centroid) - np.min(spectral_centroid))
    
    # Create a glow effect behind the title
    hue = (0.6 + 0.4 * spectral_factor) % 1.0
    r, g, b = [int(255 * c) for c in colorsys.hsv_to_rgb(hue, 0.8, 0.5 + 0.5 * energy_factor)]
    
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
        current_color = (r, g, b)
        
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
                
                # Draw waveform lines
                if len(points_above) > 1:
                    draw.line(points_above, fill=(r, g, b), width=2)
                if len(points_below) > 1:
                    draw.line(points_below, fill=(r, g, b), width=2)
    
    return np.array(img)

# Create clips
title_glow = VideoClip(make_frame=make_title_glow, duration=duration)
title_clip = create_title_clip()

# Composite all clips
video = CompositeVideoClip([
    background,
    image_clip,  # Background image
    title_glow,  # Glow and waveform effects
    title_clip,  # Centered title with effects
    progress_clip  # Progress bar at bottom
])

# Add audio
video = video.set_audio(audio)

# Write the video
print(f"Writing video to {OUTPUT_PATH}...")
video.write_videofile(OUTPUT_PATH, fps=24, codec='libx264', audio_codec='aac')
print("Done!")