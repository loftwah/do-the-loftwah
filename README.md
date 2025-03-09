# Do The Loftwah

A music visualization tool that creates beat-synchronized videos from audio tracks and images.

## Overview

This project takes an audio file and an image, and creates a video where the image pulses in sync with the beats of the music. It also adds a customizable text overlay to display the track title, visual effects like flashing, a waveform visualization, and a progress bar. The result is a professional-looking music visualization that's perfect for sharing on social media or using in presentations.

## Features

- Beat detection using librosa to synchronize visuals with music
- Image panning and zooming effects that respond to the beat
- Dynamic brightness adjustment based on audio intensity
- Real-time waveform visualization
- Flash effect synchronized with beats
- Progress bar showing playback position
- Customizable text overlay
- Configurable input and output paths via environment variables

## Requirements

- Python 3.10 or higher
- ImageMagick (for text rendering)
- Libraries listed in `requirements.txt`:
  - moviepy
  - librosa
  - numpy
  - pillow
  - python-dotenv

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/loftwah/do-the-loftwah.git
   cd do-the-loftwah
   ```

2. Install dependencies using uv (or pip):
   ```
   uv pip install -r requirements.txt
   ```

3. Install ImageMagick (required for text rendering):
   - macOS: `brew install imagemagick`
   - Linux: `sudo apt-get install imagemagick`
   - Windows: Download from [ImageMagick website](https://imagemagick.org/script/download.php)

4. Update the ImageMagick path in the script if needed (currently set to `/opt/homebrew/bin/convert` for macOS)

## Configuration

Create a `.env` file in the project root with the following variables (or use the defaults):

```
TRACK_PATH=your_audio_file.mp3
IMAGE_PATH=your_image.jpg
TITLE=Your Track Title
OUTPUT_PATH=output_video.mp4
```

## Usage

Run the script:

```
uv run script.py
```

Or using standard Python:

```
python script.py
```

## How It Works

1. The script loads the audio file and analyzes it to detect beats and tempo using librosa
2. Audio is analyzed for RMS energy to control dynamic effects
3. An image is loaded and configured with various effects:
   - Panning from left to right across the duration of the track
   - Zooming effect synchronized with detected beats
   - Brightness adjustment based on audio energy
4. Visual elements are added:
   - Real-time waveform visualization that changes color with audio intensity
   - Flash effect that triggers on beats
   - Progress bar showing playback position
   - Text overlay with the track title
5. Everything is combined into a video with the original audio
6. The final video is saved to the specified output path

## Customization

You can adjust the following parameters in the script:

- Video dimensions by changing `w_video` and `h_video`
- Zoom intensity by modifying the `zoom_func` function
- Flash opacity and duration in the `make_flash_mask` function
- Waveform size and position
- Progress bar height and color
- Text font, size, and position
- Color schemes for various elements

## Troubleshooting

- If you encounter an error related to ImageMagick, make sure it's properly installed and update the path in the script
- For font-related issues, try changing the font to one that's available on your system or remove the font parameter entirely
- If you experience performance issues, consider reducing the video dimensions or frame rate

## License

This project is licensed under the MIT License:

```
MIT License

Copyright (c) 2025 Dean Lofts (Loftwah)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.