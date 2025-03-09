import os
from dotenv import load_dotenv
import numpy as np
from moviepy.editor import AudioFileClip, ImageClip, ColorClip, CompositeVideoClip
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import moviepy.config as mpconf
import tempfile
import math
import colorsys
import time

# Set ImageMagick path (adjust if needed)
mpconf.change_settings({"IMAGEMAGICK_BINARY": "/opt/homebrew/bin/convert"})

# Load environment variables
load_dotenv()
TRACK_PATH = os.getenv("TRACK_PATH", "do_the_loftwah.mp3")
IMAGE_PATH = os.getenv("IMAGE_PATH", "cover.jpg")
TITLE = os.getenv("TITLE", "Do the Loftwah")
OUTPUT_PATH = "style_options_test.mp4"

# Test settings
TEST_FPS = 24
SEGMENT_DURATION = 4

# Create temporary directory
temp_dir = tempfile.mkdtemp()
print(f"Created temporary directory: {temp_dir}")

# Load audio
full_audio = AudioFileClip(TRACK_PATH)

# Count how many styles we'll have to adjust duration
NUM_STYLES = 10  # Original 6 + 4 new styles
TEST_DURATION = NUM_STYLES * SEGMENT_DURATION
audio = full_audio.subclip(0, TEST_DURATION)
duration = audio.duration

# Video dimensions
TEST_RESOLUTION = (1280, 720)
w_video, h_video = TEST_RESOLUTION

print(f"Creating ENHANCED STYLE OPTIONS TEST video with {NUM_STYLES} styles")

# Load background image
try:
    bg_img = Image.open(IMAGE_PATH)
    bg_img = bg_img.resize((w_video, h_video), Image.LANCZOS)
    has_bg_image = True
    print(f"Loaded background image: {IMAGE_PATH}")
except Exception as e:
    print(f"Could not load background image: {e}")
    has_bg_image = False
    bg_img = Image.new("RGB", (w_video, h_video), (0, 0, 0))

# Font options
fonts_to_try = [
    "Arial", "Arial Bold", "Helvetica", "Helvetica Bold", "Impact", "Verdana",
    "Verdana Bold", "Times New Roman", "Times New Roman Bold", "Courier New",
    "Courier New Bold", "Georgia", "Georgia Bold", "Tahoma", "Tahoma Bold",
    "Trebuchet MS", "Trebuchet MS Bold", "Palatino", "Palatino Bold"
]

# Find available fonts
available_fonts = []
for font_name in fonts_to_try:
    try:
        ImageFont.truetype(font_name, 40)
        available_fonts.append(font_name)
        print(f"Found font: {font_name}")
    except Exception:
        pass

if not available_fonts:
    available_fonts = [None]
    print("No fonts found, using default")

# Define styles (Original 6 + 4 new styles)
styles = [
    {"name": "1. Clean White Text", "font": available_fonts[0], "size": 60, "color": (255, 255, 255), "bg_color": (0, 0, 0), "effects": "none"},
    {"name": "2. Soft Glow", "font": available_fonts[0], "size": 60, "color": (255, 255, 255), "bg_color": (0, 0, 0), "effects": "glow", "glow_color": (255, 255, 255), "glow_radius": 10},
    {"name": "3. Blue Glow", "font": available_fonts[0], "size": 60, "color": (255, 255, 255), "bg_color": (0, 0, 0), "effects": "glow", "glow_color": (0, 100, 255), "glow_radius": 15},
    {"name": "4. Drop Shadow", "font": available_fonts[0], "size": 60, "color": (255, 255, 255), "bg_color": (0, 0, 0), "effects": "shadow", "shadow_color": (0, 0, 0), "shadow_offset": (4, 4)},
    {"name": "5. Outlined Text", "font": available_fonts[1] if len(available_fonts) > 1 else available_fonts[0], "size": 60, "color": (255, 255, 255), "bg_color": (0, 0, 0), "effects": "outline", "outline_color": (0, 0, 0), "outline_width": 2},
    {"name": "6. Bold Yellow Text", "font": available_fonts[2] if len(available_fonts) > 2 else available_fonts[0], "size": 70, "color": (255, 255, 0), "bg_color": (0, 0, 0), "effects": "none"},
    {"name": "7. Enhanced Background", "font": available_fonts[0], "size": 60, "color": (255, 255, 255), "bg_color": (0, 0, 0), "effects": "enhanced_bg"},
    {"name": "8. Audio Reactive", "font": available_fonts[0], "size": 60, "color": (255, 255, 255), "bg_color": (0, 0, 0), "effects": "audio_reactive"},
    {"name": "9. Text Rotation", "font": available_fonts[0], "size": 60, "color": (255, 255, 255), "bg_color": (0, 0, 0), "effects": "rotation"},
    {"name": "10. Color Cycling", "font": available_fonts[0], "size": 60, "color": (255, 255, 255), "bg_color": (0, 0, 0), "effects": "color_cycle"}
]

# Generate frames for each style
style_frames = {}
for i, style in enumerate(styles):
    style_frames[i] = []
    print(f"Generating frames for style: {style['name']}")
    
    # Generate frames for each style
    for frame_idx in range(int(SEGMENT_DURATION * TEST_FPS)):
        t = frame_idx / TEST_FPS
        
        # Create simulated audio volume for reactive effects
        # This creates a wave pattern to simulate audio beats without needing the actual audio data
        simulated_volume = 0.5 + 0.5 * math.sin(t * 2 * math.pi)  # Values between 0 and 1
        
        # Create base image with alpha channel
        img = Image.new("RGBA", (w_video, h_video), (0, 0, 0, 0))
        
        # Add background
        if has_bg_image:
            overlay = bg_img.copy().convert("RGBA")
            
            # Special background effects for style 7
            if style["effects"] == "enhanced_bg":
                # Add zooming effect to background
                zoom_factor = 1.0 + 0.1 * math.sin(t * math.pi / 2)
                new_size = (int(w_video * zoom_factor), int(h_video * zoom_factor))
                zoomed = overlay.resize(new_size, Image.LANCZOS)
                
                # Crop to original size from center
                left = (zoomed.width - w_video) // 2
                top = (zoomed.height - h_video) // 2
                overlay = zoomed.crop((left, top, left + w_video, top + h_video))
                
                # Add a pulsing color overlay
                color_overlay = Image.new("RGBA", (w_video, h_video), 
                                         (0, 0, 255, int(30 + 20 * math.sin(t * math.pi))))
                overlay = Image.alpha_composite(overlay, color_overlay)
            else:
                # Standard background darkening
                enhancer = ImageEnhance.Brightness(overlay)
                overlay = enhancer.enhance(0.5)
            
            img.paste(overlay, (0, 0), overlay)
        
        # Prepare text
        draw = ImageDraw.Draw(img)
        font_size = style["size"]
        
        # Audio reactive text size for style 8
        if style["effects"] == "audio_reactive":
            # Scale font size based on simulated audio volume
            font_size = int(style["size"] * (1 + simulated_volume * 0.5))
        
        font = ImageFont.truetype(style["font"], font_size) if style["font"] else ImageFont.load_default()
        text = TITLE
        
        # Get text dimensions
        try:
            text_width, text_height = draw.textsize(text, font=font)
        except AttributeError:
            text_bbox = draw.textbbox((0, 0), text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
        
        # Text position
        x = (w_video - text_width) // 2
        y = (h_video - text_height) // 2
        
        # Color cycling for style 10
        text_color = style["color"]
        if style["effects"] == "color_cycle":
            # Convert HSV to RGB for smooth color cycling
            h = (t / SEGMENT_DURATION) % 1.0
            s = 1.0
            v = 1.0
            r, g, b = [int(c * 255) for c in colorsys.hsv_to_rgb(h, s, v)]
            text_color = (r, g, b)
        
        # Apply text rotation for style 9
        if style["effects"] == "rotation":
            # Create a separate image for the rotated text
            angle = 15 * math.sin(t * math.pi * 2)  # Oscillate between -15 and 15 degrees
            
            # For rotation, we need to create a separate image just for the text
            txt_img = Image.new("RGBA", (w_video, h_video), (0, 0, 0, 0))
            txt_draw = ImageDraw.Draw(txt_img)
            txt_draw.text((x, y), text, fill=text_color, font=font)
            
            # Rotate the text image
            rotated_txt = txt_img.rotate(angle, resample=Image.BICUBIC, center=(x + text_width//2, y + text_height//2))
            img = Image.alpha_composite(img, rotated_txt)
        else:
            # Apply standard effects
            if style["effects"] == "none" or style["effects"] == "audio_reactive" or style["effects"] == "enhanced_bg" or style["effects"] == "color_cycle":
                draw.text((x, y), text, fill=text_color, font=font)
            elif style["effects"] == "glow":
                # Make the glow strength audio reactive for style 8
                glow_radius = style["glow_radius"]
                if style["effects"] == "audio_reactive":
                    glow_radius = int(glow_radius * (1 + simulated_volume))
                
                text_img = Image.new("RGBA", (w_video, h_video), (0, 0, 0, 0))
                text_draw = ImageDraw.Draw(text_img)
                text_draw.text((x, y), text, fill=text_color, font=font)
                glow_img = text_img.filter(ImageFilter.GaussianBlur(glow_radius))
                glow_data = np.array(glow_img)
                r, g, b, a = glow_data.T
                colored_areas = a > 0
                glow_data[..., 0][colored_areas.T] = style["glow_color"][0]
                glow_data[..., 1][colored_areas.T] = style["glow_color"][1]
                glow_data[..., 2][colored_areas.T] = style["glow_color"][2]
                glow_img = Image.fromarray(glow_data)
                img = Image.alpha_composite(img, glow_img)
                img = Image.alpha_composite(img, text_img)
            elif style["effects"] == "shadow":
                shadow_img = Image.new("RGBA", (w_video, h_video), (0, 0, 0, 0))
                shadow_draw = ImageDraw.Draw(shadow_img)
                shadow_x = x + style["shadow_offset"][0]
                shadow_y = y + style["shadow_offset"][1]
                shadow_draw.text((shadow_x, shadow_y), text, fill=style["shadow_color"] + (150,), font=font)
                shadow_img = shadow_img.filter(ImageFilter.GaussianBlur(3))
                img = Image.alpha_composite(img, shadow_img)
                draw.text((x, y), text, fill=text_color, font=font)
            elif style["effects"] == "outline":
                outline_color = style["outline_color"]
                width = style["outline_width"]
                for offset_x in range(-width, width + 1):
                    for offset_y in range(-width, width + 1):
                        if offset_x == 0 and offset_y == 0:
                            continue
                        draw.text((x + offset_x, y + offset_y), text, fill=outline_color, font=font)
                draw.text((x, y), text, fill=text_color, font=font)
        
        # Always add the style name at the top
        small_font = ImageFont.truetype(style["font"], 30) if style["font"] else ImageFont.load_default()
        draw.text((20, 20), style["name"], fill=(255, 255, 255), font=small_font)
        
        # Convert to RGB for MoviePy
        bg = Image.new("RGB", img.size, (0, 0, 0))
        bg.paste(img, mask=img.split()[3])  # Use alpha channel as mask
        
        # Save frame
        frame_path = os.path.join(temp_dir, f"style_{i}_frame_{frame_idx:04d}.jpg")
        bg.save(frame_path, quality=95)
        style_frames[i].append(frame_path)

# Create transition frames
transition_frames = []
transition_font = ImageFont.truetype(available_fonts[0], 40) if available_fonts else ImageFont.load_default()
transition_text = "Changing style..."

for frame_idx in range(int(0.2 * TEST_FPS)):
    transition_img = Image.new("RGB", (w_video, h_video), (0, 0, 0))
    transition_draw = ImageDraw.Draw(transition_img)
    
    try:
        text_width, text_height = transition_draw.textsize(transition_text, font=transition_font)
    except AttributeError:
        text_bbox = transition_draw.textbbox((0, 0), transition_text, font=transition_font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
    
    transition_x = (w_video - text_width) // 2
    transition_y = (h_video - text_height) // 2
    transition_draw.text((transition_x, transition_y), transition_text, fill=(255, 255, 255), font=transition_font)
    
    frame_path = os.path.join(temp_dir, f"transition_frame_{frame_idx:04d}.jpg")
    transition_img.save(frame_path, quality=95)
    transition_frames.append(frame_path)

# Create instructions overlay
instructions_img = Image.new("RGBA", (w_video, h_video), (0, 0, 0, 0))
draw = ImageDraw.Draw(instructions_img)
instructions = "Which style looks best? Let me know the number."
small_font = ImageFont.truetype(available_fonts[0], 30) if available_fonts else ImageFont.load_default()

try:
    text_width, text_height = draw.textsize(instructions, font=small_font)
except AttributeError:
    text_bbox = draw.textbbox((0, 0), instructions, font=small_font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]

x = (w_video - text_width) // 2
y = h_video - text_height - 20
padding = 10
draw.rectangle(
    [x - padding, y - padding, x + text_width + padding, y + text_height + padding],
    fill=(0, 0, 0, 128)  # Semi-transparent black
)
draw.text((x, y), instructions, fill=(255, 255, 255), font=small_font)
instructions_path = os.path.join(temp_dir, "instructions.png")

# Convert to RGB for MoviePy
bg = Image.new("RGB", instructions_img.size, (0, 0, 0))
bg.paste(instructions_img, mask=instructions_img.split()[3])  # Use alpha channel as mask
bg.save(instructions_path)

# Create video clips
all_frames = []
segments = []

# First create all the clips
for i, style in enumerate(styles):
    style_start = i * SEGMENT_DURATION
    style_end = (i + 1) * SEGMENT_DURATION
    
    # Add this style segment
    segment = {
        'frames': style_frames[i],
        'start_time': style_start,
        'duration': SEGMENT_DURATION
    }
    segments.append(segment)
    
    # Add transition after each style (except the last one)
    if i < len(styles) - 1:
        transition_start = style_end - 0.2
        
        # Add transition segment
        segment = {
            'frames': transition_frames,
            'start_time': transition_start,
            'duration': 0.2
        }
        segments.append(segment)

# Create a single clip from each frame sequence
clips = []
background = ColorClip(size=TEST_RESOLUTION, color=(0, 0, 0), duration=duration)
clips.append(background)

for segment in segments:
    # Frames displayed at fps
    segment_clip = ImageClip(segment['frames'][0])
    
    for j in range(1, len(segment['frames'])):
        segment_clip = CompositeVideoClip([
            segment_clip,
            ImageClip(segment['frames'][j]).set_start(j/TEST_FPS)
        ])
    
    segment_clip = segment_clip.set_duration(segment['duration']).set_start(segment['start_time'])
    clips.append(segment_clip)

# Add instructions overlay
instructions_clip = ImageClip(instructions_path).set_duration(duration)
clips.append(instructions_clip)

# Combine all clips and add audio
print("Creating final video...")
video = CompositeVideoClip(clips)
video = video.set_audio(audio)

# Write video
print(f"Writing enhanced test video to {OUTPUT_PATH}...")
video.write_videofile(OUTPUT_PATH, fps=TEST_FPS, codec='libx264', audio_codec='aac')
print(f"Test complete! Please check {OUTPUT_PATH}")

# Clean up
import shutil
try:
    shutil.rmtree(temp_dir)
    print(f"Removed temporary directory {temp_dir}")
except Exception as e:
    print(f"Could not remove temporary directory: {e}")