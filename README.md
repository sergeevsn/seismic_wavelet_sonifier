# Seismic Wavelet Sonifier

Web application for generating and analyzing seismic wavelets with real-time audio playback in the browser. Uses amazing [Bruges python library](https://github.com/agilescientific/bruges.git) for wavelet generation.

## Features

- **Wavelet Generation**: Ricker, Ormsby, Klauder, Berlage
- **Visualization**: Time and frequency domain plots
- **Audio Playback**: Play wavelets in the browser
- **Interactive Interface**: Modern web interface with responsive design

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python app.py
```

3. Open your browser and navigate to: http://localhost:5000

## Usage

1. Select wavelet type from the dropdown menu
2. Adjust parameters (frequency, duration, etc.)
3. Click "Generate Wavelet" to create the wavelet
4. Use the Play/Stop button for audio playback

## Architecture

- **Backend**: Flask API for wavelet generation and plot creation
- **Frontend**: HTML/CSS/JavaScript for user interface
- **Audio**: Web Audio API for browser playback

## API Endpoints

- `GET /` - Main page
- `POST /api/generate_wavelet` - Generate wavelet
- `POST /api/get_frequency_limits` - Get frequency limits

## Technologies

- Python 3.7+
- Flask
- NumPy, SciPy, Matplotlib
- [Bruges](https://github.com/agilescientific/bruges.git) 
- HTML5, CSS3, JavaScript (ES6+)
- Web Audio API

## Default Parameters

- **Ricker**: frequency 60 Hz, length 0.5 s
- **Ormsby**: frequencies 30, 40, 90, 100 Hz, length 0.5 s
- **Klauder**: frequencies 40, 90 Hz, length 0.5 s
- **Berlage**: frequency 60 Hz, length 0.5 s
- **dt**: 0.001 s (common for all types)