# Do The Loftwah

A music visualization tool that creates beat-synchronized videos from audio tracks and images.

## Overview

This project takes an audio file and an image, and creates a video where the image pulses in sync with the beats of the music. It also adds a customizable text overlay to display the track title. The result is a professional-looking music visualization that's perfect for sharing on social media or using in presentations.

## Features

- Beat detection using librosa to synchronize visuals with music
- Image pulsing effect that responds to the beat
- Customizable text overlay
- Configurable input and output paths via environment variables

## Requirements

- Python 3.10 or higher
- ImageMagick (for text rendering)
- Libraries listed in `requirements.txt`

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/do-the-loftwah.git
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

1. The script loads the audio file and analyzes it to detect beats and tempo
2. An image is loaded and configured to pulse in sync with the detected beats
3. Text overlay is added with the track title
4. Everything is combined into a video with the original audio
5. The final video is saved to the specified output path

## Customization

You can adjust the following parameters in the script:
- The pulse intensity by changing the `pulse` value in `make_frame_pulse()`
- Text font, size, and position
- Video dimensions and other properties

## License

[Your License Information]

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
