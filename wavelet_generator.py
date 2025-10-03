#!/usr/bin/env python3
"""
Wavelet Generator module for Seismic Wavelet Sonifier.
Supports Ricker, Ormsby, Klauder, and Berlage wavelets.
"""

import numpy as np
import bruges as bg


class WaveletGenerator:
    """Class to generate different types of seismic wavelets."""
    
    def __init__(self, dt=0.001):
        self.dt = dt
        
    def generate_ricker(self, frequency, length):
        """Generate Ricker wavelet."""
        w, t = bg.filters.ricker(duration=length, dt=self.dt, f=frequency, return_t=True)
        return w, t
    
    def generate_ormsby(self, f1, f2, f3, f4, length):
        """Generate Ormsby wavelet."""
        w, t = bg.filters.ormsby(duration=length, dt=self.dt, f=[f1, f2, f3, f4], return_t=True)
        return w, t
    
    def generate_klauder(self, f1, f2, length):
        """Generate Klauder wavelet."""
        w, t = bg.filters.klauder(duration=length, dt=self.dt, f=[f1, f2], return_t=True)
        return w, t
    
    def generate_berlage(self, frequency, length):
        """Generate Berlage wavelet."""
        w, t = bg.filters.berlage(duration=length, dt=self.dt, f=frequency, return_t=True)
        return w, t
