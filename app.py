#!/usr/bin/env python3
"""
Seismic Wavelet Sonifier - Flask web application for generating and playing seismic wavelets.
Supports Ricker, Ormsby, Klauder, and Berlage wavelets.
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import io
import base64
from flask import Flask, render_template, request, jsonify
from wavelet_generator import WaveletGenerator

app = Flask(__name__)


def create_plot(time_data, wavelet_data, wavelet_type, dt):
    """Create matplotlib plot and return as base64 encoded image."""
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
    
    # Time domain plot
    ax1.plot(time_data, wavelet_data, 'b-', linewidth=2)
    ax1.set_title(f'{wavelet_type} Wavelet - Time Domain')
    ax1.set_xlabel('Time (s)')
    ax1.set_ylabel('Amplitude')
    ax1.grid(True, alpha=0.3)
    
    # Frequency domain plot
    fft_data = np.fft.rfft(wavelet_data)
    freqs = np.fft.rfftfreq(len(wavelet_data), dt)
    magnitude = np.abs(fft_data)
    
    ax2.plot(freqs, magnitude, 'r-', linewidth=2)
    ax2.set_title(f'{wavelet_type} Wavelet - Frequency Domain')
    ax2.set_xlabel('Frequency (Hz)')
    ax2.set_ylabel('Magnitude')
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # Convert plot to base64 string
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png', dpi=100, bbox_inches='tight')
    img_buffer.seek(0)
    img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
    plt.close(fig)
    
    return img_base64


@app.route('/')
def index():
    """Serve the main page."""
    return render_template('index.html')


@app.route('/api/generate_wavelet', methods=['POST'])
def generate_wavelet():
    """Generate wavelet and return plot and audio data."""
    try:
        data = request.get_json()
        wavelet_type = data.get('wavelet_type')
        dt = data.get('dt', 0.001)
        
        generator = WaveletGenerator(dt)
        
        # Generate wavelet based on type
        if wavelet_type == 'Ricker':
            frequency = data.get('frequency')
            length = data.get('length')
            wavelet_data, time_data = generator.generate_ricker(frequency, length)
            
        elif wavelet_type == 'Ormsby':
            f1, f2, f3, f4 = data.get('f1'), data.get('f2'), data.get('f3'), data.get('f4')
            length = data.get('length')
            wavelet_data, time_data = generator.generate_ormsby(f1, f2, f3, f4, length)
            
        elif wavelet_type == 'Klauder':
            f1, f2 = data.get('f1'), data.get('f2')
            length = data.get('length')
            wavelet_data, time_data = generator.generate_klauder(f1, f2, length)
            
        elif wavelet_type == 'Berlage':
            frequency = data.get('frequency')
            length = data.get('length')
            wavelet_data, time_data = generator.generate_berlage(frequency, length)
        else:
            return jsonify({'error': 'Invalid wavelet type'}), 400
        
        # Create plot
        plot_base64 = create_plot(time_data, wavelet_data, wavelet_type, dt)
        
        # Prepare audio data (normalized to [-1, 1])
        max_abs = np.max(np.abs(wavelet_data))
        if max_abs > 0:
            audio_data = (wavelet_data / max_abs).tolist()
        else:
            audio_data = wavelet_data.tolist()
        
        # Calculate sample rate
        sample_rate = int(round(1.0 / dt))
        
        return jsonify({
            'success': True,
            'plot': plot_base64,
            'audio_data': audio_data,
            'sample_rate': sample_rate,
            'time_data': time_data.tolist(),
            'wavelet_data': wavelet_data.tolist()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/get_frequency_limits', methods=['POST'])
def get_frequency_limits():
    """Get frequency limits based on dt value."""
    try:
        data = request.get_json()
        dt = data.get('dt', 0.001)
        
        nyquist_freq = 1.0 / (2.0 * dt)
        min_freq = 10.0  # Минимум 10 Гц
        max_freq = nyquist_freq - 10.0  # Найквист - 10 Гц
        
        return jsonify({
            'min_freq': min_freq,
            'max_freq': max_freq,
            'nyquist_freq': nyquist_freq
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
