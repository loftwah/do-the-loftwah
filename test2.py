import os
from dotenv import load_dotenv
import numpy as np
from moviepy.editor import AudioFileClip, ImageClip, ColorClip, CompositeVideoClip
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageChops
import moviepy.config as mpconf
import tempfile
import math
import colorsys
import random

# Set ImageMagick path (adjust if needed)
mpconf.change_settings({"IMAGEMAGICK_BINARY": "/opt/homebrew/bin/convert"})

# Load environment variables
load_dotenv()
TRACK_PATH = os.getenv("TRACK_PATH", "do_the_loftwah.mp3")
IMAGE_PATH = os.getenv("IMAGE_PATH", "cover.jpg")
TITLE = os.getenv("TITLE", "Do the Loftwah")
OUTPUT_PATH = "visual_effects_demo.mp4"

# Test settings
TEST_FPS = 24
SEGMENT_DURATION = 5  # Slightly longer to showcase effects

# Create temporary directory
temp_dir = tempfile.mkdtemp()
print(f"Created temporary directory: {temp_dir}")

# Load audio
full_audio = AudioFileClip(TRACK_PATH)

# Count how many visual effects we'll showcase
NUM_EFFECTS = 10
TEST_DURATION = NUM_EFFECTS * SEGMENT_DURATION
audio = full_audio.subclip(0, TEST_DURATION)
duration = audio.duration

# Video dimensions
TEST_RESOLUTION = (1280, 720)
w_video, h_video = TEST_RESOLUTION

print(f"Creating MUSIC VIDEO VISUAL EFFECTS demo with {NUM_EFFECTS} effects")

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

# Define visual effects
effects = [
    {"name": "1. Visual Equalizer Bars", "effect_type": "equalizer"},
    {"name": "2. Pulsing Particles", "effect_type": "particles"},
    {"name": "3. Wave Distortion Background", "effect_type": "wave_bg"},
    {"name": "4. Audio Reactive Rings", "effect_type": "reactive_rings"},
    {"name": "5. Text With Trails", "effect_type": "text_trails"},
    {"name": "6. Glitch Effect", "effect_type": "glitch"},
    {"name": "7. Geometric Patterns", "effect_type": "geometric"},
    {"name": "8. Color Filter Pulses", "effect_type": "color_pulse"},
    {"name": "9. Flying Particles Text", "effect_type": "particle_text"},
    {"name": "10. Kaleidoscope Effect", "effect_type": "kaleidoscope"}
]

# Initialize effect_frames dictionary
effect_frames = {}
for i in range(NUM_EFFECTS):
    effect_frames[i] = []

# Generate frames for each effect
for effect_idx, effect in enumerate(effects):
    print(f"Generating frames for effect: {effect['name']}")
    
    # Generate frames for this effect
    for frame_idx in range(int(SEGMENT_DURATION * TEST_FPS)):
        t = frame_idx / TEST_FPS
        
        # Create simulated audio volume for reactive effects
        # This creates a wave pattern to simulate audio beats without needing the actual audio data
        beat_freq = 1.0  # beats per second
        simulated_volume = 0.5 + 0.5 * math.sin(t * 2 * math.pi * beat_freq)  # Values between 0 and 1
        
        # Create base image
        img = Image.new("RGBA", (w_video, h_video), (0, 0, 0, 255))
        draw = ImageDraw.Draw(img)
        
        # Always start with darkened background
        if has_bg_image:
            overlay = bg_img.copy().convert("RGBA")
            enhancer = ImageEnhance.Brightness(overlay)
            overlay = enhancer.enhance(0.3)  # Darker to make effects stand out
            img.paste(overlay, (0, 0), overlay)
            
        # Add specific effect
        if effect["effect_type"] == "equalizer":
            # Visual equalizer bars
            bar_width = 30
            bar_spacing = 10
            num_bars = 20
            total_width = num_bars * (bar_width + bar_spacing) - bar_spacing
            start_x = (w_video - total_width) // 2
            
            for bar in range(num_bars):
                # Generate random heights based on position and time
                bar_height = int(150 + 100 * math.sin((bar/num_bars + t) * math.pi * 2))
                
                # Make center bars more reactive
                center_factor = 1 - abs(bar - (num_bars/2)) / (num_bars/2)
                bar_height = int(bar_height * (0.7 + 0.6 * center_factor * simulated_volume))
                
                # Calculate position
                x1 = start_x + bar * (bar_width + bar_spacing)
                y1 = h_video - bar_height
                x2 = x1 + bar_width
                y2 = h_video
                
                # Calculate color based on height (green to yellow to red)
                height_ratio = bar_height / 250
                if height_ratio < 0.5:
                    r = int(255 * height_ratio * 2)
                    g = 255
                else:
                    r = 255
                    g = int(255 * (2 - height_ratio * 2))
                b = 0
                
                # Draw bar
                draw.rectangle([x1, y1, x2, y2], fill=(r, g, b, 220))
            
            # Add title text at top
            font = ImageFont.truetype(available_fonts[0], 60)
            text_color = (255, 255, 255)
            text = TITLE
            try:
                text_width, text_height = draw.textsize(text, font=font)
            except AttributeError:
                text_bbox = draw.textbbox((0, 0), text, font=font)
                text_width = text_bbox[2] - text_bbox[0]
                text_height = text_bbox[3] - text_bbox[1]
                
            x = (w_video - text_width) // 2
            y = 100
            draw.text((x, y), text, fill=text_color, font=font)
            
        elif effect["effect_type"] == "particles":
            # Pulsing particles around the text
            # First draw the text
            font = ImageFont.truetype(available_fonts[0], 70)
            text_color = (255, 255, 255)
            text = TITLE
            try:
                text_width, text_height = draw.textsize(text, font=font)
            except AttributeError:
                text_bbox = draw.textbbox((0, 0), text, font=font)
                text_width = text_bbox[2] - text_bbox[0]
                text_height = text_bbox[3] - text_bbox[1]
                
            x = (w_video - text_width) // 2
            y = (h_video - text_height) // 2
            draw.text((x, y), text, fill=text_color, font=font)
            
            # Now draw particles
            num_particles = 100
            center_x = w_video // 2
            center_y = h_video // 2
            max_radius = 300 + 100 * simulated_volume
            
            for p in range(num_particles):
                # Calculate particle angle based on particle number and time
                angle = (p / num_particles) * 2 * math.pi + t * 0.5
                
                # Calculate radius with some randomization
                seed = p / num_particles
                radius = max_radius * (0.4 + 0.6 * seed) * (0.8 + 0.2 * simulated_volume)
                
                # Calculate position
                particle_x = center_x + math.cos(angle) * radius
                particle_y = center_y + math.sin(angle) * radius
                
                # Calculate color (cycle around hue)
                h = (seed + t * 0.1) % 1.0
                s = 1.0
                v = 1.0
                r, g, b = [int(c * 255) for c in colorsys.hsv_to_rgb(h, s, v)]
                
                # Calculate size (larger with beat)
                size = int(3 + 5 * simulated_volume * (0.5 + 0.5 * seed))
                
                # Draw particle
                draw.ellipse([particle_x-size, particle_y-size, particle_x+size, particle_y+size], 
                             fill=(r, g, b, 180))
            
        elif effect["effect_type"] == "wave_bg":
            # Wave distortion background
            # Create a separate layer for the waves
            wave_img = Image.new("RGBA", (w_video, h_video), (0, 0, 0, 0))
            wave_draw = ImageDraw.Draw(wave_img)
            
            # Draw horizontal waves
            num_waves = 20
            wave_height = 150 * simulated_volume
            for y_pos in range(0, h_video, h_video // num_waves):
                points = []
                for x_pos in range(-20, w_video + 21, 5):
                    # Calculate wave y position
                    wave_y = y_pos + wave_height * math.sin((x_pos / w_video + t) * 2 * math.pi)
                    points.append((x_pos, wave_y))
                
                # Color changes over time
                r = int(128 + 127 * math.sin(t * 0.7))
                g = int(128 + 127 * math.sin(t * 0.8 + 2))
                b = int(128 + 127 * math.sin(t * 0.9 + 4))
                alpha = 100  # Semi-transparent
                
                if len(points) > 2:
                    wave_draw.line(points, fill=(r, g, b, alpha), width=3)
            
            # Blend the waves with the background
            img = Image.alpha_composite(img, wave_img)
            
            # Add text with glow on top
            font = ImageFont.truetype(available_fonts[0], 70)
            text_color = (255, 255, 255)
            text = TITLE
            
            # Create text layer
            text_img = Image.new("RGBA", (w_video, h_video), (0, 0, 0, 0))
            text_draw = ImageDraw.Draw(text_img)
            
            try:
                text_width, text_height = text_draw.textsize(text, font=font)
            except AttributeError:
                text_bbox = text_draw.textbbox((0, 0), text, font=font)
                text_width = text_bbox[2] - text_bbox[0]
                text_height = text_bbox[3] - text_bbox[1]
                
            x = (w_video - text_width) // 2
            y = (h_video - text_height) // 2
            
            # Draw text
            text_draw.text((x, y), text, fill=text_color, font=font)
            
            # Add glow
            glow = text_img.filter(ImageFilter.GaussianBlur(10))
            img = Image.alpha_composite(img, glow)
            img = Image.alpha_composite(img, text_img)
            
        elif effect["effect_type"] == "reactive_rings":
            # Audio reactive rings
            num_rings = 5
            center_x = w_video // 2
            center_y = h_video // 2
            max_radius = 350
            
            # Draw rings from outside in
            for ring in range(num_rings, 0, -1):
                ring_factor = ring / num_rings
                
                # Radius grows with beat
                radius = max_radius * ring_factor * (0.7 + 0.3 * simulated_volume)
                
                # Width changes with beat
                width = int(5 + 10 * simulated_volume * (1 - ring_factor))
                
                # Color cycles over time and rings
                h = (ring_factor + t * 0.2) % 1.0
                s = 0.8
                v = 1.0
                r, g, b = [int(c * 255) for c in colorsys.hsv_to_rgb(h, s, v)]
                
                # Calculate coordinates for the ring
                x1 = center_x - radius
                y1 = center_y - radius
                x2 = center_x + radius
                y2 = center_y + radius
                
                # Draw ring
                draw.ellipse([x1, y1, x2, y2], outline=(r, g, b, 200), width=width)
            
            # Add center text
            font = ImageFont.truetype(available_fonts[0], 70)
            text_color = (255, 255, 255)
            text = TITLE
            try:
                text_width, text_height = draw.textsize(text, font=font)
            except AttributeError:
                text_bbox = draw.textbbox((0, 0), text, font=font)
                text_width = text_bbox[2] - text_bbox[0]
                text_height = text_bbox[3] - text_bbox[1]
                
            x = (w_video - text_width) // 2
            y = (h_video - text_height) // 2
            draw.text((x, y), text, fill=text_color, font=font)
            
        elif effect["effect_type"] == "text_trails":
            # Text with trails effect
            font = ImageFont.truetype(available_fonts[0], 70)
            text_color = (255, 255, 255)
            text = TITLE
            
            try:
                text_width, text_height = draw.textsize(text, font=font)
            except AttributeError:
                text_bbox = draw.textbbox((0, 0), text, font=font)
                text_width = text_bbox[2] - text_bbox[0]
                text_height = text_bbox[3] - text_bbox[1]
            
            # Base position
            x = (w_video - text_width) // 2
            y = (h_video - text_height) // 2
            
            # Draw multiple instances of the text with varying transparency and position
            num_trails = 12
            for trail in range(num_trails, 0, -1):
                trail_factor = trail / num_trails
                alpha = int(255 * trail_factor)
                
                # Oscillating offset based on audio and trail
                x_offset = int(10 * (1 - trail_factor) * math.sin(t * 5) * simulated_volume)
                y_offset = int(5 * (1 - trail_factor) * math.cos(t * 7) * simulated_volume)
                
                # Draw this trail instance
                current_color = (text_color[0], text_color[1], text_color[2], alpha)
                draw.text((x + x_offset, y + y_offset), text, fill=current_color, font=font)
            
        elif effect["effect_type"] == "glitch":
            # Glitch effect
            # First create text
            font = ImageFont.truetype(available_fonts[0], 70)
            text = TITLE
            
            # Create layers for offset color channels
            r_layer = Image.new("RGBA", (w_video, h_video), (0, 0, 0, 0))
            g_layer = Image.new("RGBA", (w_video, h_video), (0, 0, 0, 0))
            b_layer = Image.new("RGBA", (w_video, h_video), (0, 0, 0, 0))
            
            r_draw = ImageDraw.Draw(r_layer)
            g_draw = ImageDraw.Draw(g_layer)
            b_draw = ImageDraw.Draw(b_layer)
            
            try:
                text_width, text_height = draw.textsize(text, font=font)
            except AttributeError:
                text_bbox = draw.textbbox((0, 0), text, font=font)
                text_width = text_bbox[2] - text_bbox[0]
                text_height = text_bbox[3] - text_bbox[1]
            
            # Base position
            x = (w_video - text_width) // 2
            y = (h_video - text_height) // 2
            
            # Calculate glitch offsets (more intense with beat)
            glitch_amount = 15 * simulated_volume
            r_offset_x = int(random.uniform(-glitch_amount, glitch_amount))
            r_offset_y = int(random.uniform(-glitch_amount/2, glitch_amount/2))
            
            g_offset_x = int(random.uniform(-glitch_amount, glitch_amount))
            g_offset_y = int(random.uniform(-glitch_amount/2, glitch_amount/2))
            
            b_offset_x = int(random.uniform(-glitch_amount, glitch_amount))
            b_offset_y = int(random.uniform(-glitch_amount/2, glitch_amount/2))
            
            # Draw offset colored text
            r_draw.text((x + r_offset_x, y + r_offset_y), text, fill=(255, 0, 0, 180), font=font)
            g_draw.text((x + g_offset_x, y + g_offset_y), text, fill=(0, 255, 0, 180), font=font)
            b_draw.text((x + b_offset_x, y + b_offset_y), text, fill=(0, 0, 255, 180), font=font)
            
            # Combine layers
            img = Image.alpha_composite(img, r_layer)
            img = Image.alpha_composite(img, g_layer)
            img = Image.alpha_composite(img, b_layer)
            
            # Add some random glitch rectangles
            num_glitches = int(5 * simulated_volume)
            for _ in range(num_glitches):
                glitch_width = random.randint(50, 200)
                glitch_height = random.randint(5, 20)
                glitch_x = random.randint(0, w_video - glitch_width)
                glitch_y = random.randint(0, h_video - glitch_height)
                
                # Random color
                r = random.randint(0, 255)
                g = random.randint(0, 255)
                b = random.randint(0, 255)
                
                draw = ImageDraw.Draw(img)
                draw.rectangle([glitch_x, glitch_y, glitch_x + glitch_width, glitch_y + glitch_height], 
                               fill=(r, g, b, 150))
            
        elif effect["effect_type"] == "geometric":
            # Geometric patterns
            # Number of shapes depends on audio volume
            num_shapes = int(30 + 50 * simulated_volume)
            
            # Draw background shapes
            for _ in range(num_shapes):
                # Pick random properties
                size = random.randint(20, 100)
                x = random.randint(0, w_video - size)
                y = random.randint(0, h_video - size)
                
                # Random color with alpha
                h = random.random()
                s = 0.8
                v = 0.8
                r, g, b = [int(c * 255) for c in colorsys.hsv_to_rgb(h, s, v)]
                alpha = random.randint(100, 200)
                
                # Choose shape type
                shape_type = random.choice(['rect', 'circle', 'triangle'])
                
                if shape_type == 'rect':
                    draw.rectangle([x, y, x + size, y + size], fill=(r, g, b, alpha))
                elif shape_type == 'circle':
                    draw.ellipse([x, y, x + size, y + size], fill=(r, g, b, alpha))
                elif shape_type == 'triangle':
                    draw.polygon([
                        (x + size/2, y),
                        (x, y + size),
                        (x + size, y + size)
                    ], fill=(r, g, b, alpha))
            
            # Add title text
            font = ImageFont.truetype(available_fonts[0], 70)
            text_color = (255, 255, 255)
            text = TITLE
            try:
                text_width, text_height = draw.textsize(text, font=font)
            except AttributeError:
                text_bbox = draw.textbbox((0, 0), text, font=font)
                text_width = text_bbox[2] - text_bbox[0]
                text_height = text_bbox[3] - text_bbox[1]
                
            x = (w_video - text_width) // 2
            y = (h_video - text_height) // 2
            
            # Add outline for better visibility
            outline_color = (0, 0, 0)
            outline_width = 2
            for offset_x in range(-outline_width, outline_width + 1):
                for offset_y in range(-outline_width, outline_width + 1):
                    if offset_x == 0 and offset_y == 0:
                        continue
                    draw.text((x + offset_x, y + offset_y), text, fill=outline_color, font=font)
            
            draw.text((x, y), text, fill=text_color, font=font)
            
        elif effect["effect_type"] == "color_pulse":
            # Color filter pulses
            # First draw the text normally
            font = ImageFont.truetype(available_fonts[0], 70)
            text_color = (255, 255, 255)
            text = TITLE
            try:
                text_width, text_height = draw.textsize(text, font=font)
            except AttributeError:
                text_bbox = draw.textbbox((0, 0), text, font=font)
                text_width = text_bbox[2] - text_bbox[0]
                text_height = text_bbox[3] - text_bbox[1]
                
            x = (w_video - text_width) // 2
            y = (h_video - text_height) // 2
            draw.text((x, y), text, fill=text_color, font=font)
            
            # Create colored overlay based on audio
            overlay = Image.new("RGBA", (w_video, h_video), (0, 0, 0, 0))
            overlay_draw = ImageDraw.Draw(overlay)
            
            # Color changes over time
            h = (t * 0.1) % 1.0
            s = 1.0
            v = 1.0
            r, g, b = [int(c * 255) for c in colorsys.hsv_to_rgb(h, s, v)]
            
            # Alpha based on audio volume
            alpha = int(80 * simulated_volume)
            
            # Fill entire screen with colored overlay
            overlay_draw.rectangle([0, 0, w_video, h_video], fill=(r, g, b, alpha))
            
            # Composite overlay with main image
            img = Image.alpha_composite(img, overlay)
            
        elif effect["effect_type"] == "particle_text":
            # Flying particles that form text
            font = ImageFont.truetype(available_fonts[0], 70)
            text = TITLE
            
            # Create mask for text shape
            mask_img = Image.new("L", (w_video, h_video), 0)
            mask_draw = ImageDraw.Draw(mask_img)
            
            try:
                text_width, text_height = mask_draw.textsize(text, font=font)
            except AttributeError:
                text_bbox = mask_draw.textbbox((0, 0), text, font=font)
                text_width = text_bbox[2] - text_bbox[0]
                text_height = text_bbox[3] - text_bbox[1]
                
            x = (w_video - text_width) // 2
            y = (h_video - text_height) // 2
            
            # Draw text in white on black background
            mask_draw.text((x, y), text, fill=255, font=font)
            
            # Threshold mask to get text pixels
            mask_data = np.array(mask_img)
            text_pixels = np.where(mask_data > 128)
            text_points = list(zip(text_pixels[1], text_pixels[0]))  # x, y format
            
            # Randomly sample points to create particles
            num_particles = 500
            if len(text_points) > 0:
                sampled_points = random.sample(text_points, min(num_particles, len(text_points)))
                
                # For each sampled point, draw a particle
                for point in sampled_points:
                    # Original position in text
                    orig_x, orig_y = point
                    
                    # Add random movement based on time
                    noise_x = 30 * math.sin(t + orig_x * 0.01)
                    noise_y = 30 * math.cos(t + orig_y * 0.01)
                    
                    # Position moves with beat
                    beat_factor = 1.0 + 0.5 * simulated_volume
                    curr_x = orig_x + noise_x * beat_factor
                    curr_y = orig_y + noise_y * beat_factor
                    
                    # Color based on position
                    h = (orig_x / w_video + t * 0.1) % 1.0
                    s = 0.8
                    v = 1.0
                    r, g, b = [int(c * 255) for c in colorsys.hsv_to_rgb(h, s, v)]
                    
                    # Size changes with beat
                    size = int(1 + 3 * simulated_volume)
                    
                    # Draw particle
                    draw.ellipse([curr_x-size, curr_y-size, curr_x+size, curr_y+size], 
                                 fill=(r, g, b, 200))
            
        elif effect["effect_type"] == "kaleidoscope":
            # Kaleidoscope effect
            # First create a quarter of the image
            quarter_size = (w_video // 2, h_video // 2)
            quarter_img = Image.new("RGBA", quarter_size, (0, 0, 0, 0))
            quarter_draw = ImageDraw.Draw(quarter_img)
            
            # Draw some shapes in the quarter
            num_shapes = 20
            for i in range(num_shapes):
                shape_factor = i / num_shapes
                
                # Position circles along a spiral
                angle = shape_factor * 2 * math.pi * 2 + t
                radius = shape_factor * quarter_size[0] * 0.8
                
                # Position affected by beat
                x = quarter_size[0] * 0.5 + radius * math.cos(angle) * (0.7 + 0.3 * simulated_volume)
                y = quarter_size[1] * 0.5 + radius * math.sin(angle) * (0.7 + 0.3 * simulated_volume)
                
                # Size changes with beat
                size = int(20 + 20 * simulated_volume * (1 - shape_factor))
                
                # Color cycles
                h = (shape_factor + t * 0.1) % 1.0
                s = 1.0
                v = 1.0
                r, g, b = [int(c * 255) for c in colorsys.hsv_to_rgb(h, s, v)]
                
                # Draw circle
                quarter_draw.ellipse([x-size, y-size, x+size, y+size], fill=(r, g, b, 200))
            
            # Flip and mirror the quarter to create full kaleidoscope
            # Make the top-right quarter
            flipped_quarter = quarter_img.transpose(Image.FLIP_LEFT_RIGHT)
            
            # Make the bottom-left quarter
            flipped_quarter2 = quarter_img.transpose(Image.FLIP_TOP_BOTTOM)
            
            # Make the bottom-right quarter
            flipped_quarter3 = flipped_quarter.transpose(Image.FLIP_TOP_BOTTOM)
            
            # Place all quarters on the main image
            img.paste(quarter_img, (0, 0), quarter_img)
            img.paste(flipped_quarter, (w_video // 2, 0), flipped_quarter)
            img.paste(flipped_quarter2, (0, h_video // 2), flipped_quarter2)
            img.paste(flipped_quarter3, (w_video // 2, h_video // 2), flipped_quarter3)
            
            # Add text in center
            draw = ImageDraw.Draw(img)
            font = ImageFont.truetype(available_fonts[0], 70)
            text_color = (255, 255, 255)
            text = TITLE
            try:
                text_width, text_height = draw.textsize(text, font=font)
            except AttributeError:
                text_bbox = draw.textbbox((0, 0), text, font=font)
                text_width = text_bbox[2] - text_bbox[0]
                text_height = text_bbox[3] - text_bbox[1]
                
            x = (w_video - text_width) // 2
            y = (h_video - text_height) // 2
            
            # Add outline for better visibility
            outline_color = (0, 0, 0)
            outline_width = 2
            for offset_x in range(-outline_width, outline_width + 1):
                for offset_y in range(-outline_width, outline_width + 1):
                    if offset_x == 0 and offset_y == 0:
                        continue
                    draw.text((x + offset_x, y + offset_y), text, fill=outline_color, font=font)
            
            draw.text((x, y), text, fill=text_color, font=font)
        
        # Always add the effect name at the top
        small_font = ImageFont.truetype(available_fonts[0], 30) if available_fonts else ImageFont.load_default()
        draw = ImageDraw.Draw(img)  # Make sure we have the current draw object
        
        # Create a dark background for the effect name
        effect_text = effect["name"]
        try:
            text_width, text_height = draw.textsize(effect_text, font=small_font)
        except AttributeError:
            text_bbox = draw.textbbox((0, 0), effect_text, font=small_font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
        
        padding = 10
        draw.rectangle([
            20 - padding, 
            20 - padding, 
            20 + text_width + padding, 
            20 + text_height + padding
        ], fill=(0, 0, 0, 150))
        
        draw.text((20, 20), effect_text, fill=(255, 255, 255), font=small_font)
        
        # Convert to RGB for MoviePy
        if img.mode == 'RGBA':
            bg = Image.new("RGB", img.size, (0, 0, 0))
            bg.paste(img, mask=img.split()[3])  # Use alpha channel as mask
            img = bg
        
        # Save frame
        frame_path = os.path.join(temp_dir, f"effect_{effect_idx}_frame_{frame_idx:04d}.jpg")
        img.save(frame_path, quality=95)
        effect_frames[effect_idx].append(frame_path)

# Create transition frames
transition_frames = []
transition_font = ImageFont.truetype(available_fonts[0], 40) if available_fonts else ImageFont.load_default()
transition_text = "Next Effect..."

for frame_idx in range(int(0.5 * TEST_FPS)):  # Half-second transition
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
instructions = "Which effect looks best? Let me know the number."
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
segments = []

# First create all the clips
for i in range(NUM_EFFECTS):
    effect_start = i * SEGMENT_DURATION
    
    # Add this effect segment
    segment = {
        'frames': effect_frames[i],
        'start_time': effect_start,
        'duration': SEGMENT_DURATION
    }
    segments.append(segment)
    
    # Add transition after each effect (except the last one)
    if i < NUM_EFFECTS - 1:
        transition_start = effect_start + SEGMENT_DURATION - 0.5  # Half-second overlap
        
        # Add transition segment
        segment = {
            'frames': transition_frames,
            'start_time': transition_start,
            'duration': 0.5
        }
        segments.append(segment)

# Create a single clip from each frame sequence
clips = []
background = ColorClip(size=TEST_RESOLUTION, color=(0, 0, 0), duration=duration)
clips.append(background)

# Create clips from frame sequences
for segment in segments:
    frames = segment['frames']
    start_time = segment['start_time']
    segment_duration = segment['duration']
    
    # Create clip from the first frame
    segment_clip = ImageClip(frames[0]).set_duration(1/TEST_FPS)
    
    # Add the rest of the frames as overlays with appropriate timing
    for j in range(1, len(frames)):
        frame_clip = ImageClip(frames[j]).set_duration(1/TEST_FPS).set_start(j/TEST_FPS)
        segment_clip = CompositeVideoClip([segment_clip, frame_clip])
    
    # Set the final duration and start time for this segment
    segment_clip = segment_clip.set_duration(segment_duration).set_start(start_time)
    clips.append(segment_clip)

# Add instructions overlay
instructions_clip = ImageClip(instructions_path).set_duration(duration)
clips.append(instructions_clip)

# Combine all clips and add audio
print("Creating final video...")
video = CompositeVideoClip(clips)
video = video.set_audio(audio)

# Write video
print(f"Writing visual effects demo to {OUTPUT_PATH}...")
video.write_videofile(OUTPUT_PATH, fps=TEST_FPS, codec='libx264', audio_codec='aac')
print(f"Test complete! Please check {OUTPUT_PATH}")

# Clean up
import shutil
try:
    shutil.rmtree(temp_dir)
    print(f"Removed temporary directory {temp_dir}")
except Exception as e:
    print(f"Could not remove temporary directory: {e}")