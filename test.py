import os
from dotenv import load_dotenv
import numpy as np
from moviepy.editor import AudioFileClip, ImageClip, ColorClip, CompositeVideoClip, VideoClip
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageOps
import moviepy.config as mpconf
import tempfile
import math

# Set ImageMagick path (adjust if needed)
mpconf.change_settings({"IMAGEMAGICK_BINARY": "/opt/homebrew/bin/convert"})

# Load environment variables
load_dotenv()
TRACK_PATH = os.getenv("TRACK_PATH", "do_the_loftwah.mp3")
IMAGE_PATH = os.getenv("IMAGE_PATH", "cover.jpg")
TITLE = os.getenv("TITLE", "Do the Loftwah")
OUTPUT_PATH = "style_options_test.mp4"

# Test settings
TEST_DURATION = 24  # 6 styles, 4 seconds each
TEST_RESOLUTION = (1280, 720)
TEST_FPS = 24
SEGMENT_DURATION = 4

print(f"Creating STYLE OPTIONS TEST video")

# Load audio segment
full_audio = AudioFileClip(TRACK_PATH)
audio = full_audio.subclip(0, TEST_DURATION)
duration = audio.duration

# Video dimensions
w_video, h_video = TEST_RESOLUTION

# Load background image
try:
    bg_img = Image.open(IMAGE_PATH)
    bg_img = bg_img.resize((w_video, h_video), Image.LANCZOS)
    has_bg_image = True
    print(f"Loaded background image: {IMAGE_PATH}")
except Exception as e:
    print(f"Could not load background image: {e}")
    has_bg_image = False

# Create temporary directory
temp_dir = tempfile.mkdtemp()
print(f"Created temporary directory: {temp_dir}")

# Font options
fonts_to_try = [
    "Arial", "Arial Bold", "Helvetica", "Helvetica Bold", "Impact", "Verdana",
    "Verdana Bold", "Times New Roman", "Times New Roman Bold", "Courier New",
    "Courier New Bold", "Georgia", "Georgia Bold", "Tahoma", "Tahoma Bold",
    "Trebuchet MS", "Trebuchet MS Bold", "Palatino", "Palatino Bold",
    "Lucida Grande", "Lucida Grande Bold", "DejaVu Sans", "DejaVu Sans Bold",
    "Ubuntu", "Ubuntu Bold", "Roboto", "Roboto Bold", "Open Sans", "Open Sans Bold"
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

# Style definitions
styles = [
    {"name": "1. Clean White Text", "font": available_fonts[0], "size": 60, "color": (255, 255, 255), "bg_color": (0, 0, 0), "effects": "none"},
    {"name": "2. Soft Glow", "font": available_fonts[0], "size": 60, "color": (255, 255, 255), "bg_color": (0, 0, 0), "effects": "glow", "glow_color": (255, 255, 255), "glow_radius": 10},
    {"name": "3. Blue Glow", "font": available_fonts[0], "size": 60, "color": (255, 255, 255), "bg_color": (0, 0, 0), "effects": "glow", "glow_color": (0, 100, 255), "glow_radius": 15},
    {"name": "4. Drop Shadow", "font": available_fonts[0], "size": 60, "color": (255, 255, 255), "bg_color": (0, 0, 0), "effects": "shadow", "shadow_color": (0, 0, 0), "shadow_offset": (4, 4)},
    {"name": "5. Outlined Text", "font": available_fonts[1] if len(available_fonts) > 1 else available_fonts[0], "size": 60, "color": (255, 255, 255), "bg_color": (0, 0, 0), "effects": "outline", "outline_color": (0, 0, 0), "outline_width": 2},
    {"name": "6. Bold Yellow Text", "font": available_fonts[2] if len(available_fonts) > 2 else available_fonts[0], "size": 70, "color": (255, 255, 0), "bg_color": (0, 0, 0), "effects": "none"}
]

# Create style images as RGBA
style_images = []
for i, style in enumerate(styles):
    img = Image.new("RGBA", (w_video, h_video), (0, 0, 0, 0))  # Transparent base
    if has_bg_image:
        overlay = bg_img.copy().convert("RGBA")
        enhancer = ImageEnhance.Brightness(overlay)
        overlay = enhancer.enhance(0.5)
        img.paste(overlay, (0, 0), overlay)
    
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(style["font"], style["size"]) if style["font"] else ImageFont.load_default()
    
    text = TITLE
    try:
        text_width, text_height = draw.textsize(text, font=font)
    except AttributeError:
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
    
    x = (w_video - text_width) // 2
    y = (h_video - text_height) // 2
    
    if style["effects"] == "none":
        draw.text((x, y), text, fill=style["color"], font=font)
    elif style["effects"] == "glow":
        text_img = Image.new("RGBA", (w_video, h_video), (0, 0, 0, 0))
        text_draw = ImageDraw.Draw(text_img)
        text_draw.text((x, y), text, fill=style["color"], font=font)
        glow_img = text_img.filter(ImageFilter.GaussianBlur(style["glow_radius"]))
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
        draw.text((x, y), text, fill=style["color"], font=font)
    elif style["effects"] == "outline":
        outline_color = style["outline_color"]
        width = style["outline_width"]
        for offset_x in range(-width, width + 1):
            for offset_y in range(-width, width + 1):
                if offset_x == 0 and offset_y == 0:
                    continue
                draw.text((x + offset_x, y + offset_y), text, fill=outline_color, font=font)
        draw.text((x, y), text, fill=style["color"], font=font)
    
    small_font = ImageFont.truetype(style["font"], 30) if style["font"] else ImageFont.load_default()
    draw.text((20, 20), style["name"], fill=(255, 255, 255), font=small_font)
    
    img_path = os.path.join(temp_dir, f"style_{i}.png")
    img.save(img_path)  # Save as RGBA
    style_images.append({"path": img_path, "name": style["name"]})
    print(f"Created style {style['name']}")

# Transition image as RGBA
transition_img = Image.new("RGBA", (w_video, h_video), (0, 0, 0, 255))  # Opaque black
transition_draw = ImageDraw.Draw(transition_img)
transition_font = ImageFont.truetype(available_fonts[0], 40) if available_fonts else ImageFont.load_default()
transition_text = "Changing style..."
try:
    text_width, text_height = transition_draw.textsize(transition_text, font=transition_font)
except AttributeError:
    text_bbox = transition_draw.textbbox((0, 0), transition_text, font=transition_font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
transition_x = (w_video - text_width) // 2
transition_y = (h_video - text_height) // 2
transition_draw.text((transition_x, transition_y), transition_text, fill=(255, 255, 255), font=transition_font)
transition_path = os.path.join(temp_dir, "transition.png")
transition_img.save(transition_path)

# Demo frame function (converts RGBA to RGB)
def make_demo_frame(t):
    style_idx = int(t / SEGMENT_DURATION)
    style_idx = min(style_idx, len(style_images) - 1)
    in_transition = (t % SEGMENT_DURATION) > (SEGMENT_DURATION - 0.2)
    if in_transition:
        img = Image.open(transition_path)  # Loads as RGBA
    else:
        img = Image.open(style_images[style_idx]["path"])  # Loads as RGBA
        # Apply pulse animation
        style_time = t % SEGMENT_DURATION
        animation_factor = style_time / SEGMENT_DURATION
        pulse = 1.0 + 0.05 * math.sin(animation_factor * 2 * math.pi * 2)
        if pulse != 1.0:
            orig_width, orig_height = img.size
            new_width = int(orig_width * pulse)
            new_height = int(orig_height * pulse)
            crop_x1 = (new_width - orig_width) // 2
            crop_y1 = (new_height - orig_height) // 2
            crop_x2 = crop_x1 + orig_width
            crop_y2 = crop_y1 + orig_height
            try:
                resized = img.resize((new_width, new_height), Image.LANCZOS)
                img = resized.crop((crop_x1, crop_y1, crop_x2, crop_y2))
            except Exception as e:
                print(f"Animation error: {e}")
    
    # Convert RGBA to RGB by compositing with black background
    bg = Image.new("RGB", img.size, (0, 0, 0))
    bg.paste(img, mask=img.split()[3])  # Use alpha channel as mask
    return np.array(bg)  # Returns RGB array (720, 1280, 3)

# Instructions frame function (converts RGBA to RGB)
def make_instructions_frame(t):
    img = Image.new("RGBA", (w_video, h_video), (0, 0, 0, 0))  # Transparent
    draw = ImageDraw.Draw(img)
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
    
    # Convert RGBA to RGB by compositing with transparent background
    # (this will be composited with the demo frame)
    bg = Image.new("RGB", img.size, (0, 0, 0))
    bg.paste(img, mask=img.split()[3])  # Use alpha channel as mask
    return np.array(bg)  # Returns RGB array (720, 1280, 3)

# Modified approach: use ImageClips instead of VideoClips with make_frame
def get_frame_array(make_frame, t):
    """Helper to ensure we get RGB frames"""
    frame = make_frame(t)
    if frame.shape[2] == 4:  # If RGBA
        # Create RGB version with black background
        rgb_frame = np.zeros((frame.shape[0], frame.shape[1], 3), dtype=np.uint8)
        # Apply alpha blending
        alpha = frame[:, :, 3:4] / 255.0
        rgb_frame = (frame[:, :, :3] * alpha + rgb_frame * (1 - alpha)).astype(np.uint8)
        return rgb_frame
    return frame

# Create a black background clip
background = ColorClip(size=TEST_RESOLUTION, color=(0, 0, 0), duration=duration)

# Create clips for each style
demo_clips = []
for i, style in enumerate(styles):
    start_time = i * SEGMENT_DURATION
    end_time = (i + 1) * SEGMENT_DURATION
    
    # Load image as ImageClip
    img_clip = ImageClip(style_images[i]["path"]).set_duration(SEGMENT_DURATION)
    
    # Set position to start at the right time
    img_clip = img_clip.set_start(start_time)
    
    demo_clips.append(img_clip)

# Add transition clip between segments
transition_clips = []
for i in range(len(styles) - 1):
    transition_time = (i + 1) * SEGMENT_DURATION - 0.2
    transition_clip = ImageClip(transition_path).set_duration(0.2)
    transition_clip = transition_clip.set_start(transition_time)
    transition_clips.append(transition_clip)

# Create instructions clip
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
instructions_img.save(instructions_path)
instructions_clip = ImageClip(instructions_path).set_duration(duration)

# Combine all clips
all_clips = [background] + demo_clips + transition_clips + [instructions_clip]
video = CompositeVideoClip(all_clips)
video = video.set_audio(audio)

# Write video
print(f"Writing test video to {OUTPUT_PATH}...")
video.write_videofile(OUTPUT_PATH, fps=TEST_FPS, codec='libx264', audio_codec='aac')
print(f"Test complete! Please check {OUTPUT_PATH}")

# Clean up
import shutil
try:
    shutil.rmtree(temp_dir)
    print(f"Removed temporary directory {temp_dir}")
except Exception as e:
    print(f"Could not remove temporary directory: {e}")