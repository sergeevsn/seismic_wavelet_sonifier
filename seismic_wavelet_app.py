#!/usr/bin/env python3
"""
Interactive PyQt5 application for generating and playing seismic wavelets.
Supports Ricker, Ormsby, Klauder, and Berlage wavelets.
"""

import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QComboBox, QLabel, QDoubleSpinBox, 
                             QPushButton, QGroupBox, QGridLayout, QSpinBox)
from PyQt5.QtCore import Qt, QBuffer, QByteArray, QTimer
import sounddevice as sd

import bruges as bg


class WaveletGenerator:
    """Class to generate different types of seismic wavelets."""
    
    def __init__(self, dt=0.001):
        self.dt = dt
        
    def generate_ricker(self, frequency, length):
        """Generate Ricker wavelet."""
        w, t = bg.filters.ricker(duration=length, dt=self.dt, f=frequency, return_t=True)
        return w
    
    def generate_ormsby(self, f1, f2, f3, f4, length):
        """Generate Ormsby wavelet."""
        w, t = bg.filters.ormsby(duration=length, dt=self.dt, f=[f1, f2, f3, f4], return_t=True)
        return w
    
    def generate_klauder(self, f1, f2, length):
        """Generate Klauder wavelet."""
        w, t = bg.filters.klauder(duration=length, dt=self.dt, f=[f1, f2], return_t=True)
        return w
    
    def generate_berlage(self, frequency, length):
        """Generate Berlage wavelet."""
        w, t = bg.filters.berlage(duration=length, dt=self.dt, f=frequency, return_t=True)
        return w


class PlotWidget(QWidget):
    """Widget for displaying wavelet plots."""
    
    def __init__(self):
        super().__init__()
        self.dt = 0.001            # <- по умолчанию, будет перезаписано из приложения
        self.figure = Figure(figsize=(12, 8))
        self.canvas = FigureCanvas(self.figure)
        
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)
        
    def plot_wavelet(self, time_data, wavelet_data, wavelet_type):
        """Plot wavelet in time and frequency domains."""
        self.figure.clear()
        
        # Time domain plot
        ax1 = self.figure.add_subplot(2, 1, 1)
        ax1.plot(time_data, wavelet_data, 'b-', linewidth=2)
        ax1.set_title(f'{wavelet_type} Wavelet - Time Domain')
        ax1.set_xlabel('Time (s)')
        ax1.set_ylabel('Amplitude')
        ax1.grid(True, alpha=0.3)
        
        # Frequency domain plot
        ax2 = self.figure.add_subplot(2, 1, 2)
        # используем rfft / rfftfreq для одностороннего спектра
        fft_data = np.fft.rfft(wavelet_data)
        freqs = np.fft.rfftfreq(len(wavelet_data), self.dt)
        magnitude = np.abs(fft_data)
        
        ax2.plot(freqs, magnitude, 'r-', linewidth=2)
        ax2.set_title(f'{wavelet_type} Wavelet - Frequency Domain')
        ax2.set_xlabel('Frequency (Hz)')
        ax2.set_ylabel('Magnitude')
        ax2.grid(True, alpha=0.3)
        
        self.figure.tight_layout()
        self.canvas.draw()


class ParameterWidget(QWidget):
    """Widget for wavelet parameter controls."""
    
    def __init__(self):
        super().__init__()
        self.parameters = {}
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Wavelet type selection
        self.wavelet_type_combo = QComboBox()
        self.wavelet_type_combo.addItems(['Ricker', 'Ormsby', 'Klauder', 'Berlage'])
        self.wavelet_type_combo.currentTextChanged.connect(self.update_parameters)
        
        layout.addWidget(QLabel("Wavelet Type:"))
        layout.addWidget(self.wavelet_type_combo)
        
        # Parameters group
        self.params_group = QGroupBox("Parameters")
        self.params_layout = QGridLayout()
        self.params_group.setLayout(self.params_layout)
        layout.addWidget(self.params_group)
        
        # Common parameters
        self.dt_spinbox = QDoubleSpinBox()
        self.dt_spinbox.setRange(0.0001, 0.004)
        self.dt_spinbox.setSingleStep(0.0001)
        self.dt_spinbox.setValue(0.001)
        self.dt_spinbox.setDecimals(4)
        self.dt_spinbox.valueChanged.connect(self.update_frequency_limits)
        
        self.params_layout.addWidget(QLabel("dt (s):"), 0, 0)
        self.params_layout.addWidget(self.dt_spinbox, 0, 1)
        
        # Initialize parameter controls
        self.update_parameters()
        
        self.setLayout(layout)
        
    def update_parameters(self):
        """Update parameter controls based on selected wavelet type."""
        # Clear existing parameter controls (except dt)
        while self.params_layout.count() > 2:  # Keep dt row (2 items)
            child = self.params_layout.takeAt(self.params_layout.count() - 1)
            if child.widget():
                child.widget().deleteLater()
        
        wavelet_type = self.wavelet_type_combo.currentText()
        self.parameters = {}
        
        # Calculate frequency limits based on current dt
        dt = self.dt_spinbox.value() if hasattr(self, 'dt_spinbox') else 0.001
        nyquist_freq = 1.0 / (2.0 * dt)
        min_freq = 0.1
        max_freq = nyquist_freq * 0.9
        
        if wavelet_type == 'Ricker':
            self.add_parameter('Frequency (Hz)', 'frequency', 60, min_freq, max_freq)
            self.add_parameter('Length (s)', 'length', 0.5, 0.1, 2.0)
            
        elif wavelet_type == 'Ormsby':
            self.add_parameter('f1 (Hz)', 'f1', 30, min_freq, max_freq)
            self.add_parameter('f2 (Hz)', 'f2', 40, min_freq, max_freq)
            self.add_parameter('f3 (Hz)', 'f3', 90, min_freq, max_freq)
            self.add_parameter('f4 (Hz)', 'f4', 100, min_freq, max_freq)
            self.add_parameter('Length (s)', 'length', 0.5, 0.1, 2.0)
            
        elif wavelet_type == 'Klauder':
            self.add_parameter('f1 (Hz)', 'f1', 40, min_freq, max_freq)
            self.add_parameter('f2 (Hz)', 'f2', 90, min_freq, max_freq)
            self.add_parameter('Length (s)', 'length', 0.5, 0.1, 2.0)
            
        elif wavelet_type == 'Berlage':
            self.add_parameter('Frequency (Hz)', 'frequency', 60, min_freq, max_freq)
            self.add_parameter('Length (s)', 'length', 0.5, 0.1, 2.0)
    
    def add_parameter(self, label_text, param_name, default_value, min_val, max_val):
        """Add a parameter control."""
        row = self.params_layout.rowCount()
        
        label = QLabel(label_text)
        spinbox = QDoubleSpinBox()
        spinbox.setRange(min_val, max_val)
        spinbox.setValue(default_value)
        spinbox.setDecimals(1)
        
        self.params_layout.addWidget(label, row, 0)
        self.params_layout.addWidget(spinbox, row, 1)
        
        self.parameters[param_name] = spinbox
    
    def update_frequency_limits(self):
        """Update frequency limits based on current dt value."""
        if hasattr(self, 'dt_spinbox') and self.dt_spinbox:
            dt = self.dt_spinbox.value()
            # Nyquist frequency = 1/(2*dt)
            nyquist_freq = 1.0 / (2.0 * dt)
            # Set reasonable limits: 0.1 Hz to 90% of Nyquist
            min_freq = 0.1
            max_freq = nyquist_freq * 0.9
            
            # Update frequency spinboxes
            for name, widget in self.parameters.items():
                if 'freq' in name.lower() or name in ['frequency', 'f1', 'f2', 'f3', 'f4']:
                    if widget:
                        current_value = widget.value()
                        widget.setRange(min_freq, max_freq)
                        # Keep current value if it's within new range
                        if current_value > max_freq:
                            widget.setValue(max_freq)
                        elif current_value < min_freq:
                            widget.setValue(min_freq)
    
    def get_parameters(self):
        """Get current parameter values."""
        params = {}
        for name, widget in self.parameters.items():
            if widget and not widget.isHidden():
                params[name] = widget.value()
        if hasattr(self, 'dt_spinbox') and self.dt_spinbox:
            params['dt'] = self.dt_spinbox.value()
        return params


class SeismicWaveletApp(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        self.wavelet_generator = WaveletGenerator()
        # audio-related
        self.audio_output = None
        self.audio_buffer = None
        self.loop_timer = None
        self.is_playing = False
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle("Seismic Wavelet Generator")
        self.setGeometry(100, 100, 1200, 800)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout()
        
        # Left panel for parameters
        left_panel = QVBoxLayout()
        
        self.param_widget = ParameterWidget()
        left_panel.addWidget(self.param_widget)
        
        # Generate and Play buttons
        button_layout = QHBoxLayout()
        
        self.generate_btn = QPushButton("Generate Wavelet")
        self.generate_btn.clicked.connect(self.generate_wavelet)
        
        self.play_btn = QPushButton("Play Audio")
        self.play_btn.clicked.connect(self.toggle_audio)
        self.play_btn.setEnabled(False)
        
        button_layout.addWidget(self.generate_btn)
        button_layout.addWidget(self.play_btn)
        
        left_panel.addLayout(button_layout)
        left_panel.addStretch()
        
        # Right panel for plots
        self.plot_widget = PlotWidget()
        
        main_layout.addLayout(left_panel, 1)
        main_layout.addWidget(self.plot_widget, 2)
        
        central_widget.setLayout(main_layout)
        
    def generate_wavelet(self):
        """Generate and display wavelet based on current parameters."""
        # Stop any currently playing audio
        if self.is_playing:
            self.stop_audio()
            
        params = self.param_widget.get_parameters()
        wavelet_type = self.param_widget.wavelet_type_combo.currentText()
        
        # Update generator dt
        self.wavelet_generator.dt = params['dt']
        
        # Generate wavelet based on type
        if wavelet_type == 'Ricker':
            wavelet_data = self.wavelet_generator.generate_ricker(
                params['frequency'], params['length'])
        elif wavelet_type == 'Ormsby':
            wavelet_data = self.wavelet_generator.generate_ormsby(
                params['f1'], params['f2'], params['f3'], params['f4'], params['length'])
        elif wavelet_type == 'Klauder':
            wavelet_data = self.wavelet_generator.generate_klauder(
                params['f1'], params['f2'], params['length'])
        elif wavelet_type == 'Berlage':
            wavelet_data = self.wavelet_generator.generate_berlage(
                params['frequency'], params['length'])
        
        # Generate time vector for plotting - match the length of wavelet_data
        time_data = np.arange(len(wavelet_data)) * params['dt']
        
        # Store data for audio playback
        self.current_wavelet_data = wavelet_data
        self.current_time_data = time_data
        
        # Plot the wavelet
        self.plot_widget.dt = params['dt']
        self.plot_widget.plot_wavelet(time_data, wavelet_data, wavelet_type)
        
        # Enable play button
        self.play_btn.setEnabled(True)
        
    def toggle_audio(self):
        """Toggle between play and stop audio."""
        if self.is_playing:
            self.stop_audio()
        else:
            self.play_audio()
        
    def play_audio(self):
        """Play generated wavelet as audio (looped) using sounddevice."""
        if hasattr(self, 'current_wavelet_data') and not self.is_playing:
            samplerate = int(round(1.0 / self.wavelet_generator.dt))

            # normalize to [-1, 1]
            data = self.current_wavelet_data
            max_abs = np.max(np.abs(data))
            if max_abs > 0:
                data = data / max_abs

            # play looped
            sd.play(data, samplerate=samplerate, loop=True)

            self.is_playing = True
            self.play_btn.setText("Stop Audio")

    def stop_audio(self):
        """Stop playback."""
        if self.is_playing:
            sd.stop()
            self.is_playing = False
            self.play_btn.setText("Play Audio")

    def closeEvent(self, event):
        """Stop audio on close."""
        if self.is_playing:
            self.stop_audio()
        event.accept()


def main():
    app = QApplication(sys.argv)
    window = SeismicWaveletApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
