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
import time
from datetime import datetime

# Set ImageMagick path (adjust if needed)
mpconf.change_settings({"IMAGEMAGICK_BINARY": "/opt/homebrew/bin/convert"})

# Load environment variables
load_dotenv()
TRACK_PATH = os.getenv("TRACK_PATH", "do_the_loftwah.mp3")
IMAGE_PATH = os.getenv("IMAGE_PATH", "cover.jpg")
TITLE = os.getenv("TITLE", "Do the Loftwah")  # This is the correct title to use

# Generate unique output filename with timestamp
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
OUTPUT_PATH = f"awesome_visualizer_{timestamp}.mp4"

# Settings
FPS = 24
FULL_SONG = True  # Set to True to process the entire song

print(f"Creating AWESOME VISUALIZER video for \"{TITLE}\"")
print(f"Output will be saved to: {OUTPUT_PATH}")

# Create temporary directory
temp_dir = tempfile.mkdtemp()
print(f"Created temporary directory: {temp_dir}")

# Load audio
start_time = time.time()
full_audio = AudioFileClip(TRACK_PATH)

if FULL_SONG:
    audio = full_audio
    duration = full_audio.duration
    print(f"Processing entire song: {duration:.2f} seconds")
else:
    # Just use 60 seconds for testing
    duration = min(60, full_audio.duration)
    audio = full_audio.subclip(0, duration)
    print(f"Processing first {duration:.2f} seconds of song")

# Video dimensions - 16:9 aspect ratio
W, H = 1280, 720

# Load background image
try:
    bg_img = Image.open(IMAGE_PATH)
    bg_img = bg_img.resize((W, H), Image.LANCZOS)
    has_bg_image = True
    print(f"Loaded background image: {IMAGE_PATH}")
except Exception as e:
    print(f"Could not load background image: {e}")
    has_bg_image = False
    bg_img = Image.new("RGB", (W, H), (0, 0, 0))

# Font setup
fonts_to_try = [
    "Arial Bold", "Impact", "Helvetica Bold", "Verdana Bold", 
    "Arial", "Helvetica", "Verdana", "Georgia Bold"
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

main_font = available_fonts[0]

# Visualization style options
styles = [
    {
        "name": "Particle Rings",
        "duration": 10.0,
        "blend_in": 1.0,
        "blend_out": 1.0
    },
    {
        "name": "Wave Spectrum",
        "duration": 8.0,
        "blend_in": 1.0,
        "blend_out": 1.0
    },
    {
        "name": "Geometric Pulse",
        "duration": 10.0,
        "blend_in": 1.0,
        "blend_out": 1.0
    },
    {
        "name": "Color Storm",
        "duration": 8.0,
        "blend_in": 1.0,
        "blend_out": 1.0
    },
    {
        "name": "3D Wireframe",
        "duration": 10.0,
        "blend_in": 1.0,
        "blend_out": 1.0
    }
]

# Calculate total style durations
total_style_duration = sum(style["duration"] for style in styles)
# If song is longer than our styles, repeat styles to fill
num_repeats = math.ceil(duration / total_style_duration)

# Extend styles list if needed
full_styles = []
for _ in range(num_repeats):
    full_styles.extend(styles)

# Calculate style timing
timing = []
current_time = 0
for style in full_styles:
    if current_time >= duration:
        break
        
    # Adjust duration if this would exceed the song length
    actual_duration = min(style["duration"], duration - current_time)
    if actual_duration <= 0:
        break
        
    timing.append({
        "name": style["name"],
        "start": current_time,
        "end": current_time + actual_duration,
        "duration": actual_duration,
        "blend_in": min(style["blend_in"], actual_duration / 2),
        "blend_out": min(style["blend_out"], actual_duration / 2)
    })
    current_time += actual_duration

print(f"Created timing plan with {len(timing)} segments")

# Generate frames
total_frames = int(duration * FPS)
frames_paths = []

print(f"Generating {total_frames} frames...")

for frame_idx in range(total_frames):
    if frame_idx % 100 == 0:
        print(f"Processing frame {frame_idx}/{total_frames} ({frame_idx/total_frames*100:.1f}%)")
    
    t = frame_idx / FPS  # Current time in seconds
    
    # Find current active style(s)
    active_styles = []
    for style in timing:
        if style["start"] <= t <= style["end"]:
            # Calculate blend factor (0 to 1)
            if t < style["start"] + style["blend_in"]:
                # Blending in
                blend = (t - style["start"]) / style["blend_in"]
            elif t > style["end"] - style["blend_out"]:
                # Blending out
                blend = (style["end"] - t) / style["blend_out"]
            else:
                # Fully visible
                blend = 1.0
                
            active_styles.append({"name": style["name"], "blend": blend})
    
    # Create base image
    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)
    
    # Start with darkened background
    if has_bg_image:
        bg_copy = bg_img.copy().convert("RGBA")
        enhancer = ImageEnhance.Brightness(bg_copy)
        bg_copy = enhancer.enhance(0.3)  # Darker to make effects stand out
        img.paste(bg_copy, (0, 0), bg_copy.split()[3] if len(bg_copy.split()) > 3 else None)
    
    # Simulate audio volume with multiple waves for more dynamic response
    beat_freq_1 = 1.2  # Primary beat
    beat_freq_2 = 2.4  # Double-time
    beat_freq_3 = 0.6  # Half-time
    
    vol_1 = 0.5 + 0.5 * math.sin(t * 2 * math.pi * beat_freq_1)
    vol_2 = 0.5 + 0.5 * math.sin(t * 2 * math.pi * beat_freq_2)
    vol_3 = 0.5 + 0.5 * math.sin(t * 2 * math.pi * beat_freq_3)
    
    # Weight volumes to create more interesting patterns
    # Main beat gets highest weight, but all contribute
    simulated_volume = 0.6 * vol_1 + 0.25 * vol_2 + 0.15 * vol_3
    
    # Apply each active style with blending
    for style_info in active_styles:
        style_name = style_info["name"]
        blend_factor = style_info["blend"]
        
        # Create style layer
        style_img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        style_draw = ImageDraw.Draw(style_img)
        
        #---------------------------------------------------------------------
        # Style: Particle Rings
        #---------------------------------------------------------------------
        if style_name == "Particle Rings":
            # Draw concentric rings of particles
            num_rings = 6
            particles_per_ring = 80
            center_x, center_y = W // 2, H // 2
            
            for ring in range(num_rings):
                ring_factor = ring / (num_rings - 1)
                
                # Base radius grows over time and pulses with audio
                base_radius = 50 + 250 * ring_factor
                pulse_amount = 30 * simulated_volume * (1 - ring_factor * 0.5)
                
                # Add time-based movement
                time_offset = t * (1 + ring_factor)
                radius = base_radius + pulse_amount * math.sin(time_offset * 3)
                
                # Each ring has particles
                for p in range(particles_per_ring):
                    angle = (p / particles_per_ring) * 2 * math.pi
                    
                    # Add time-based rotation
                    angle += t * (1 - ring_factor) * 2
                    
                    # Position affected by audio
                    x = center_x + radius * math.cos(angle)
                    y = center_y + radius * math.sin(angle)
                    
                    # Color cycles over time
                    hue = (ring_factor + t * 0.1) % 1.0
                    sat = 1.0
                    val = 1.0
                    r, g, b = [int(c * 255) for c in colorsys.hsv_to_rgb(hue, sat, val)]
                    
                    # Particle size varies with audio
                    size = int(2 + 4 * simulated_volume)
                    
                    # Particle alpha also varies with audio and ring
                    alpha = int((150 + 100 * simulated_volume) * (1 - ring_factor * 0.3))
                    
                    # Draw particle
                    style_draw.ellipse([x-size, y-size, x+size, y+size], 
                                     fill=(r, g, b, alpha))
            
            # Add text in center
            font_size = int(70 + 20 * simulated_volume)
            font = ImageFont.truetype(main_font, font_size) if main_font else ImageFont.load_default()
            
            # Text color pulses with audio
            brightness = int(200 + 55 * simulated_volume)
            text_color = (brightness, brightness, brightness, 255)
            
            # Use the correct title here - using TITLE variable
            text = TITLE
            try:
                text_width, text_height = style_draw.textsize(text, font=font)
            except AttributeError:
                text_bbox = style_draw.textbbox((0, 0), text, font=font)
                text_width = text_bbox[2] - text_bbox[0]
                text_height = text_bbox[3] - text_bbox[1]
                
            x = (W - text_width) // 2
            y = (H - text_height) // 2
            
            # Add glow effect on text
            glow_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            glow_draw = ImageDraw.Draw(glow_layer)
            glow_draw.text((x, y), text, fill=(text_color[0], text_color[1], text_color[2], 100), font=font)
            glow = glow_layer.filter(ImageFilter.GaussianBlur(10))
            style_img = Image.alpha_composite(style_img, glow)
            
            # Draw main text
            style_draw.text((x, y), text, fill=text_color, font=font)
            
        #---------------------------------------------------------------------
        # Style: Wave Spectrum
        #---------------------------------------------------------------------
        elif style_name == "Wave Spectrum":
            # Create audio spectrum visualization with wave effect
            num_bars = 60
            bar_width = W // num_bars
            max_height = H * 0.6
            
            for i in range(num_bars):
                bar_factor = i / num_bars
                
                # Calculate bar height with multiple waves for complexity
                # This creates a mix of frequencies for a more organic look
                bar_volume = (
                    math.sin((bar_factor * 6 + t) * math.pi * 2) * 0.4 +
                    math.sin((bar_factor * 3 - t * 1.5) * math.pi * 2) * 0.3 +
                    math.sin((bar_factor * 9 + t * 0.7) * math.pi * 2) * 0.2 +
                    math.sin((0.5 - bar_factor) * math.pi * 4) * 0.1
                )
                
                # Apply audio reactivity
                bar_height = int(abs(bar_volume) * max_height * (0.3 + 0.7 * simulated_volume))
                
                # Calculate color (spectrum from blue to purple to red)
                hue = (bar_factor + t * 0.05) % 1.0
                sat = 0.8
                val = 0.9
                r, g, b = [int(c * 255) for c in colorsys.hsv_to_rgb(hue, sat, val)]
                
                # Position bar at bottom of screen
                x1 = i * bar_width
                y1 = H - bar_height
                x2 = x1 + bar_width - 1
                y2 = H
                
                # Draw with semi-transparency for glow effect
                style_draw.rectangle([x1, y1, x2, y2], fill=(r, g, b, 180))
                
                # Add a glow point at top of bar
                glow_size = int(4 + 4 * simulated_volume)
                glow_center_x = x1 + bar_width // 2
                glow_center_y = y1
                
                # Draw glow point
                style_draw.ellipse(
                    [glow_center_x - glow_size, glow_center_y - glow_size,
                     glow_center_x + glow_size, glow_center_y + glow_size],
                    fill=(r, g, b, 200)
                )
            
            # Add title text at top with shadow - using correct title
            font_size = 80
            font = ImageFont.truetype(main_font, font_size) if main_font else ImageFont.load_default()
            text = TITLE
            
            try:
                text_width, text_height = style_draw.textsize(text, font=font)
            except AttributeError:
                text_bbox = style_draw.textbbox((0, 0), text, font=font)
                text_width = text_bbox[2] - text_bbox[0]
                text_height = text_bbox[3] - text_bbox[1]
                
            x = (W - text_width) // 2
            y = H // 6
            
            # Draw shadow
            shadow_offset = int(4 + 2 * simulated_volume)
            style_draw.text((x + shadow_offset, y + shadow_offset), 
                          text, fill=(0, 0, 0, 180), font=font)
            
            # Draw text with vertical oscillation based on audio
            # REMOVED y_offset to keep title centered
            # y_offset = int(10 * simulated_volume * math.sin(t * 4))
            # style_draw.text((x, y + y_offset), text, fill=(255, 255, 255, 230), font=font)
            
            # Keep title centered - no y_offset
            style_draw.text((x, y), text, fill=(255, 255, 255, 230), font=font)
            
        #---------------------------------------------------------------------
        # Style: Geometric Pulse
        #---------------------------------------------------------------------
        elif style_name == "Geometric Pulse":
            # Create pulsating geometric patterns
            center_x, center_y = W // 2, H // 2
            
            # Number of shapes affected by audio
            num_shapes = int(30 + 50 * simulated_volume)
            max_size = int(180 + 100 * simulated_volume)
            
            # Layer multiple geometric patterns
            for layer in range(3):
                layer_factor = layer / 2  # 0, 0.5, 1
                
                # Rotation speed and direction varies by layer
                rotation = t * (1 + layer_factor) * (1 if layer % 2 == 0 else -1)
                
                for i in range(num_shapes):
                    shape_factor = i / num_shapes
                    
                    # Create a spiral pattern
                    angle = shape_factor * math.pi * 2 + rotation
                    
                    # Distance from center affected by audio and time
                    distance = max_size * shape_factor * (0.2 + 0.8 * (0.5 + 0.5 * math.sin(t * 2 + layer_factor * math.pi)))
                    
                    # Position
                    x = center_x + distance * math.cos(angle)
                    y = center_y + distance * math.sin(angle)
                    
                    # Size decreases as we move outward
                    size = int(max_size * (0.1 + 0.2 * (1 - shape_factor)) * (0.5 + 0.5 * simulated_volume))
                    
                    # Color cycles over time and by position
                    hue = (shape_factor + t * 0.1 + layer_factor * 0.3) % 1.0
                    sat = 0.8
                    val = 0.9
                    r, g, b = [int(c * 255) for c in colorsys.hsv_to_rgb(hue, sat, val)]
                    
                    # Transparency increases with distance from center
                    alpha = int(200 * (1 - shape_factor * 0.7))
                    
                    # Alternate between different shapes
                    shape_type = i % 3  # 0=circle, 1=square, 2=triangle
                    
                    if shape_type == 0:  # Circle
                        style_draw.ellipse([x-size, y-size, x+size, y+size], 
                                         fill=(r, g, b, alpha))
                    elif shape_type == 1:  # Square
                        # Rotate square
                        square_angle = angle * 2
                        corners = []
                        for corner in range(4):
                            corner_angle = square_angle + corner * math.pi / 2
                            corner_x = x + size * math.cos(corner_angle)
                            corner_y = y + size * math.sin(corner_angle)
                            corners.append((corner_x, corner_y))
                        style_draw.polygon(corners, fill=(r, g, b, alpha))
                    else:  # Triangle
                        # Rotate triangle
                        triangle_angle = angle * 3
                        corners = []
                        for corner in range(3):
                            corner_angle = triangle_angle + corner * (2 * math.pi / 3)
                            corner_x = x + size * math.cos(corner_angle)
                            corner_y = y + size * math.sin(corner_angle)
                            corners.append((corner_x, corner_y))
                        style_draw.polygon(corners, fill=(r, g, b, alpha))
            
            # Add title with scaling effect - using correct title
            scale_factor = 1.0 + 0.2 * simulated_volume
            font_size = int(70 * scale_factor)
            font = ImageFont.truetype(main_font, font_size) if main_font else ImageFont.load_default()
            
            text = TITLE
            try:
                text_width, text_height = style_draw.textsize(text, font=font)
            except AttributeError:
                text_bbox = style_draw.textbbox((0, 0), text, font=font)
                text_width = text_bbox[2] - text_bbox[0]
                text_height = text_bbox[3] - text_bbox[1]
                
            x = (W - text_width) // 2
            y = (H - text_height) // 2
            
            # Create outline with multiple colors
            num_outlines = 3
            for outline in range(num_outlines):
                outline_factor = outline / (num_outlines - 1)
                
                # Color for this outline
                h = (t * 0.1 + outline_factor) % 1.0
                s = 1.0
                v = 1.0
                r, g, b = [int(c * 255) for c in colorsys.hsv_to_rgb(h, s, v)]
                
                # Size of outline
                outline_size = (num_outlines - outline) * 2
                
                # Draw outline text in all 8 directions
                for dx in [-outline_size, 0, outline_size]:
                    for dy in [-outline_size, 0, outline_size]:
                        if dx == 0 and dy == 0:
                            continue
                        style_draw.text((x + dx, y + dy), text, fill=(r, g, b, 200), font=font)
            
            # Draw main text
            style_draw.text((x, y), text, fill=(255, 255, 255, 255), font=font)
            
        #---------------------------------------------------------------------
        # Style: Color Storm
        #---------------------------------------------------------------------
        elif style_name == "Color Storm":
            # Create swirling color clouds
            # Start with a dark base
            color_layer = Image.new("RGBA", (W, H), (0, 0, 0, 180))
            color_draw = ImageDraw.Draw(color_layer)
            
            # Create multiple cloud clusters
            num_clusters = 5
            particles_per_cluster = 300
            
            for cluster in range(num_clusters):
                cluster_factor = cluster / (num_clusters - 1)
                
                # Cluster center moves in a circular pattern
                cluster_angle = t * (0.2 + 0.2 * cluster_factor) + cluster_factor * math.pi * 2
                cluster_radius = W * 0.3 * (0.5 + 0.5 * math.sin(t + cluster_factor * math.pi))
                
                cluster_x = W // 2 + cluster_radius * math.cos(cluster_angle)
                cluster_y = H // 2 + cluster_radius * math.sin(cluster_angle)
                
                # Create particles for this cluster
                for p in range(particles_per_cluster):
                    p_factor = p / particles_per_cluster
                    
                    # Particle stays close to cluster center, with some randomness
                    p_radius = random.uniform(0, 150) * (0.5 + 0.5 * simulated_volume)
                    p_angle = p_factor * math.pi * 2 + t * (1 - cluster_factor)
                    
                    x = cluster_x + p_radius * math.cos(p_angle)
                    y = cluster_y + p_radius * math.sin(p_angle)
                    
                    # Skip if outside screen
                    if x < 0 or x >= W or y < 0 or y >= H:
                        continue
                    
                    # Color based on cluster and position
                    h = (cluster_factor + p_factor * 0.1 + t * 0.05) % 1.0
                    s = 0.8
                    v = 0.9
                    r, g, b = [int(c * 255) for c in colorsys.hsv_to_rgb(h, s, v)]
                    
                    # Size and alpha affected by audio
                    size = int(2 + 6 * simulated_volume * (1 - p_factor * 0.5))
                    alpha = int(100 + 100 * simulated_volume * (1 - p_factor * 0.7))
                    
                    # Draw particle as a soft glow
                    color_draw.ellipse([x-size, y-size, x+size, y+size], 
                                     fill=(r, g, b, alpha))
            
            # Apply blur to create a soft, cloudy effect
            color_layer = color_layer.filter(ImageFilter.GaussianBlur(5))
            
            # Composite color layer onto style image
            style_img = Image.alpha_composite(style_img, color_layer)
            style_draw = ImageDraw.Draw(style_img)
            
            # Add title text with motion trail effect - using correct title
            font_size = 80
            font = ImageFont.truetype(main_font, font_size) if main_font else ImageFont.load_default()
            
            text = TITLE
            try:
                text_width, text_height = style_draw.textsize(text, font=font)
            except AttributeError:
                text_bbox = style_draw.textbbox((0, 0), text, font=font)
                text_width = text_bbox[2] - text_bbox[0]
                text_height = text_bbox[3] - text_bbox[1]
                
            # Base position - center of screen
            base_x = W // 2 - text_width // 2
            base_y = H // 2 - text_height // 2
            
            # Draw multiple instances with decreasing opacity
            num_trails = 10
            
            # KEEP CENTERED - Draw only one instance in center
            style_draw.text((base_x, base_y), text, fill=(255, 255, 255, 255), font=font)
            
            # REMOVED: Motion trail effect that moves title away from center
            # for trail in range(num_trails, 0, -1):
            #     trail_factor = trail / num_trails
            #     alpha = int(255 * trail_factor)
            #     
            #     # Position shifts based on time and audio
            #     x_offset = int(20 * (1 - trail_factor) * math.sin(t * 3) * simulated_volume)
            #     y_offset = int(10 * (1 - trail_factor) * math.cos(t * 5) * simulated_volume)
            #     
            #     x = base_x + x_offset
            #     y = base_y + y_offset
            #     
            #     # Color shifts for trail
            #     h = (t * 0.1 + (1 - trail_factor) * 0.2) % 1.0
            #     s = 0.9 - trail_factor * 0.5  # Trails become less saturated
            #     v = 1.0
            #     r, g, b = [int(c * 255) for c in colorsys.hsv_to_rgb(h, s, v)]
            #     
            #     style_draw.text((x, y), text, fill=(r, g, b, alpha), font=font)
            
        #---------------------------------------------------------------------
        # Style: 3D Wireframe
        #---------------------------------------------------------------------
        elif style_name == "3D Wireframe":
            # Create a 3D wireframe grid effect
            # Start with a grid of points that we'll transform
            grid_size = 20
            point_spacing = max(W, H) / (grid_size - 1)
            center_x, center_y = W // 2, H // 2
            
            # Create perspective projection matrices
            # Rotation angles that change with time
            angle_x = t * 0.2
            angle_y = t * 0.3
            angle_z = t * 0.1
            
            # Rotation matrices (simplified for visualization)
            sin_x, cos_x = math.sin(angle_x), math.cos(angle_x)
            sin_y, cos_y = math.sin(angle_y), math.cos(angle_y)
            sin_z, cos_z = math.sin(angle_z), math.cos(angle_z)
            
            # Store transformed points
            points = []
            
            # Create grid of points in 3D space
            for i in range(grid_size):
                for j in range(grid_size):
                    # Map to 3D space (-1 to 1 range)
                    x = (i / (grid_size - 1)) * 2 - 1
                    y = (j / (grid_size - 1)) * 2 - 1
                    
                    # Create different 3D shapes by manipulating z
                    # This creates a wave pattern that changes over time
                    z = 0.5 * math.sin(x * 3 + t) * math.cos(y * 3 + t * 0.7)
                    
                    # Audio affects the wave height
                    z *= (0.5 + 1.0 * simulated_volume)
                    
                    # Apply 3D rotations (simplified)
                    # Rotate around X axis
                    y2 = y * cos_x - z * sin_x
                    z2 = y * sin_x + z * cos_x
                    
                    # Rotate around Y axis
                    x3 = x * cos_y + z2 * sin_y
                    z3 = -x * sin_y + z2 * cos_y
                    
                    # Rotate around Z axis
                    x4 = x3 * cos_z - y2 * sin_z
                    y4 = x3 * sin_z + y2 * cos_z
                    
                    # Apply perspective projection
                    scale = 8.0 / (5.0 + z3)  # Perspective divide with z-shift
                    screen_x = center_x + x4 * scale * min(W, H) * 0.4
                    screen_y = center_y + y4 * scale * min(W, H) * 0.4
                    
                    # Store the point with its original indices and z depth
                    points.append({
                        'x': screen_x,
                        'y': screen_y,
                        'i': i,
                        'j': j,
                        'z': z3  # Store z for color gradient
                    })
            
            # Sort points by Z for depth effect (simple painter's algorithm)
            points.sort(key=lambda p: p['z'])
            
            # Draw the wireframe grid
            for p in points:
                i, j = p['i'], p['j']
                
                # Color based on depth and time
                # Map z from [-1,1] to [0,1] for color mapping
                depth = (p['z'] + 1) / 2
                
                # HSV color mapping with time variation
                h = (depth * 0.7 + t * 0.05) % 1.0
                s = 0.9
                v = 0.9
                r, g, b = [int(c * 255) for c in colorsys.hsv_to_rgb(h, s, v)]
                
                # Point size varies with audio
                size = int(2 + 3 * simulated_volume)
                
                # Draw the point
                style_draw.ellipse([p['x']-size, p['y']-size, p['x']+size, p['y']+size], 
                                 fill=(r, g, b, 180))
                
                # Draw lines to adjacent points (right and down)
                if i < grid_size - 1:
                    # Find the point to the right
                    for p2 in points:
                        if p2['i'] == i + 1 and p2['j'] == j:
                            # Only draw if both points are reasonably close
                            # (avoids lines crossing the entire grid)
                            if abs(p['z'] - p2['z']) < 0.5:
                                # Line alpha based on z distance (fade distant lines)
                                line_alpha = int(100 * (1 - abs(p['z'] - p2['z'])))
                                style_draw.line([p['x'], p['y'], p2['x'], p2['y']], 
                                             fill=(r, g, b, line_alpha), width=1)
                            break
                            
                if j < grid_size - 1:
                    # Find the point below
                    for p2 in points:
                        if p2['i'] == i and p2['j'] == j + 1:
                            if abs(p['z'] - p2['z']) < 0.5:
                                line_alpha = int(100 * (1 - abs(p['z'] - p2['z'])))
                                style_draw.line([p['x'], p['y'], p2['x'], p2['y']], 
                                             fill=(r, g, b, line_alpha), width=1)
                            break
            
            # Add title at center with dynamic scale - using correct title (TITLE)
            scale_factor = 1.0 + 0.15 * math.sin(t * 2) * simulated_volume
            font_size = int(80 * scale_factor)
            font = ImageFont.truetype(main_font, font_size) if main_font else ImageFont.load_default()
            
            text = TITLE  # Using correct variable
            try:
                text_width, text_height = style_draw.textsize(text, font=font)
            except AttributeError:
                text_bbox = style_draw.textbbox((0, 0), text, font=font)
                text_width = text_bbox[2] - text_bbox[0]
                text_height = text_bbox[3] - text_bbox[1]
                
            x = (W - text_width) // 2
            y = (H - text_height) // 2
            
            # REMOVED: 3D text position offsets that move title away from center
            # Apply the same 3D rotation to text
            # For simplicity, we'll just oscillate the text position slightly
            # x_offset = int(10 * math.sin(angle_y * 2))
            # y_offset = int(10 * math.sin(angle_x * 2))
            
            # Draw text with glow
            glow_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            glow_draw = ImageDraw.Draw(glow_layer)
            
            # Keep title centered - no offsets
            glow_draw.text((x, y), text, fill=(200, 200, 255, 100), font=font)
            glow = glow_layer.filter(ImageFilter.GaussianBlur(10))
            style_img = Image.alpha_composite(style_img, glow)
            
            # Main text - perfectly centered
            style_draw.text((x, y), text, fill=(255, 255, 255, 220), font=font)
        
        # Apply style blending
        if blend_factor < 1.0:
            # Create a version with adjusted alpha for blending
            style_data = np.array(style_img)
            if style_data.shape[2] >= 4:  # If it has an alpha channel
                style_data[..., 3] = (style_data[..., 3] * blend_factor).astype(np.uint8)
                style_img = Image.fromarray(style_data)
        
        # Composite style onto main image
        img = Image.alpha_composite(img, style_img)
    
    # Add progress bar at bottom
    progress = t / duration
    bar_height = 5
    bar_y = H - bar_height - 5
    draw = ImageDraw.Draw(img)
    
    # Background of progress bar (dark)
    draw.rectangle([10, bar_y, W - 10, bar_y + bar_height], fill=(50, 50, 50, 150))
    
    # Filled portion of progress bar (color changes with progress)
    bar_width = int((W - 20) * progress)
    h = progress  # Progress determines hue
    s = 0.8
    v = 1.0
    r, g, b = [int(c * 255) for c in colorsys.hsv_to_rgb(h, s, v)]
    draw.rectangle([10, bar_y, 10 + bar_width, bar_y + bar_height], fill=(r, g, b, 200))
    
    # Add time indicator
    minutes = int(t // 60)
    seconds = int(t % 60)
    total_minutes = int(duration // 60)
    total_seconds = int(duration % 60)
    time_text = f"{minutes}:{seconds:02d} / {total_minutes}:{total_seconds:02d}"
    
    small_font = ImageFont.truetype(main_font, 16) if main_font else ImageFont.load_default()
    try:
        time_width, time_height = draw.textsize(time_text, font=small_font)
    except AttributeError:
        time_bbox = draw.textbbox((0, 0), time_text, font=small_font)
        time_width = time_bbox[2] - time_bbox[0]
        time_height = time_bbox[3] - time_bbox[1]
    
    time_x = W - time_width - 15
    time_y = bar_y - time_height - 5
    
    # Draw with background for readability
    draw.rectangle([time_x - 5, time_y - 2, time_x + time_width + 5, time_y + time_height + 2],
                  fill=(0, 0, 0, 150))
    draw.text((time_x, time_y), time_text, fill=(255, 255, 255), font=small_font)
    
    # Convert to RGB for MoviePy
    if img.mode == 'RGBA':
        bg = Image.new("RGB", img.size, (0, 0, 0))
        bg.paste(img, mask=img.split()[3])  # Use alpha channel as mask
        img = bg
    
    # Save frame
    frame_path = os.path.join(temp_dir, f"frame_{frame_idx:05d}.jpg")
    img.save(frame_path, quality=95)
    frames_paths.append(frame_path)

# Create video from frames
print("Creating video from frames...")
clips = []

# Create background clip
background = ColorClip(size=(W, H), color=(0, 0, 0), duration=duration)
clips.append(background)

# Add frames as clip
for i, frame_path in enumerate(frames_paths):
    frame_clip = ImageClip(frame_path).set_duration(1/FPS).set_start(i/FPS)
    clips.append(frame_clip)

# Combine all clips and add audio
print("Compositing final video...")
video = CompositeVideoClip(clips)
video = video.set_audio(audio)

# Write video
print(f"Writing final video to {OUTPUT_PATH}...")
video.write_videofile(OUTPUT_PATH, fps=FPS, codec='libx264', audio_codec='aac')

print(f"Visualizer complete! Total time: {time.time() - start_time:.1f} seconds")
print(f"Output saved to: {OUTPUT_PATH}")

# Clean up
import shutil
try:
    shutil.rmtree(temp_dir)
    print(f"Removed temporary directory {temp_dir}")
except Exception as e:
    print(f"Could not remove temporary directory: {e}")