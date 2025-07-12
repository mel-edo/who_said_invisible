# Invisible

*Like the song which is totally present in the MGS series.*

I got a bout of inspiration and built this in about a day.

> **Note:** Only works on Wayland right now due to the usage of `grim` as the screenshot utility.

## Demo

https://github.com/user-attachments/assets/fa96937e-b0e3-4104-bdb6-eb436c3b9d53

## What It Does

This tool constantly monitors your screen and:

* Matches visual content using ORB + OpenCV
* Extracts text using Tesseract OCR and checks for relevant keywords
* Captures the screen using `grim` (Wayland screenshot utility)
* Plays an MP4 audio clip using `ffplay` from FFmpeg
* Displays a fullscreen animated overlay using PyQt5

## Requirements

* Python 3.8 or newer
* Wayland display server
* [Tesseract OCR](https://github.com/tesseract-ocr/tesseract)
* `ffplay` (part of FFmpeg)

### Python Dependencies

Install using pip:

```bash
pip install opencv-python pytesseract PyQt5
```

### For Arch Linux Users

Install all system dependencies with:

```bash
sudo pacman -S \
  tesseract tesseract-data-eng \
  python-pytesseract opencv python-opencv \
  python-pyqt5 grim ffmpeg --needed
```
## Usage

Run the detector script:

```bash
python3 main.py
```
