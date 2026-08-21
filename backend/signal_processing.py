import numpy as np
import pandas as pd
from scipy.signal import butter, filtfilt, find_peaks, savgol_filter
from typing import Dict, Any, List, Optional, Tuple

def butter_lowpass(cutoff: float, fs: float, order: int = 5):
    """
    Calculate Butterworth low-pass filter coefficients.
    """
    nyquist = 0.5 * fs
    normal_cutoff = min(cutoff / nyquist, 0.99)  # Avoid exceeding Nyquist
    b, a = butter(order, normal_cutoff, btype='low')
    return b, a

def apply_butterworth_filter(signal: np.ndarray, cutoff: float, fs: float, order: int = 5) -> np.ndarray:
    """
    Apply zero-phase Butterworth low-pass filter to the ECG signal.
    """
    if len(signal) < 15:
        return signal.copy()
    try:
        b, a = butter_lowpass(cutoff, fs, order)
        # Calculate minimum required padlen
        padlen = 3 * max(len(a), len(b))
        if len(signal) <= padlen:
            padlen = len(signal) - 1
        filtered = filtfilt(b, a, signal, padlen=padlen)
        return filtered
    except Exception as e:
        print(f"Butterworth filter warning: {e}")
        return signal.copy()

def apply_savgol_filter(signal: np.ndarray, window_length: int = 11, polyorder: int = 3) -> np.ndarray:
    """
    Apply Savitzky-Golay smoothing filter to ECG signal.
    Ensures window_length is odd and less than signal length.
    """
    if len(signal) < 5:
        return signal.copy()
    
    # Adjust window_length to be odd and valid
    wl = min(window_length, len(signal))
    if wl % 2 == 0:
        wl -= 1
    if wl <= polyorder:
        wl = polyorder + 2 if (polyorder + 2) % 2 != 0 else polyorder + 3
    
    if wl > len(signal):
        return signal.copy()
        
    try:
        smoothed = savgol_filter(signal, wl, polyorder)
        return smoothed
    except Exception as e:
        print(f"Savitzky-Golay filter warning: {e}")
        return signal.copy()

def detect_peaks(signal: np.ndarray, fs: float, distance_factor: float = 0.35, height_threshold: Optional[float] = None) -> Tuple[np.ndarray, Dict[str, Any]]:
    """
    Detect R-peaks in filtered/smoothed ECG signal.
    """
    min_distance = max(1, int(fs * distance_factor))
    if height_threshold is None:
        height_threshold = float(np.mean(signal))
        
    peaks, properties = find_peaks(
        signal,
        distance=min_distance,
        height=height_threshold
    )
    return peaks, properties

def calculate_metrics(signal: np.ndarray, peaks: np.ndarray, fs: float) -> Dict[str, Any]:
    """
    Calculate BPM, R-R intervals, HRV metrics (SDNN, RMSSD), and health status.
    """
    n_samples = len(signal)
    duration_sec = n_samples / fs if fs > 0 else 1.0
    
    bpm = float((len(peaks) * 60.0) / duration_sec) if duration_sec > 0 else 0.0
    
    if len(peaks) > 1:
        # Peak time points in seconds
        peak_times_sec = peaks / fs
        # R-R intervals in milliseconds
        rr_intervals_ms = np.diff(peak_times_sec) * 1000.0
        
        mean_rr = float(np.mean(rr_intervals_ms))
        min_rr = float(np.min(rr_intervals_ms))
        max_rr = float(np.max(rr_intervals_ms))
        
        # Standard deviation of NN intervals (SDNN)
        sdnn = float(np.std(rr_intervals_ms))
        
        # Root mean square of successive differences (RMSSD)
        if len(rr_intervals_ms) > 1:
            rr_diffs = np.diff(rr_intervals_ms)
            rmssd = float(np.sqrt(np.mean(np.square(rr_diffs))))
        else:
            rmssd = 0.0
    else:
        rr_intervals_ms = []
        mean_rr = 0.0
        min_rr = 0.0
        max_rr = 0.0
        sdnn = 0.0
        rmssd = 0.0

    # Diagnostic Status Classification
    if len(peaks) < 2:
        status = "Insufficient Beats Detected"
        status_code = "warning"
        description = "Adjust peak detection sensitivity or cutoff threshold."
    elif bpm < 60.0:
        status = "Bradycardia Alert"
        status_code = "caution"
        description = f"Heart rate is low ({bpm:.1f} BPM)."
    elif bpm > 100.0:
        status = "Tachycardia Alert"
        status_code = "caution"
        description = f"Heart rate is elevated ({bpm:.1f} BPM)."
    elif sdnn > 120.0 or rmssd > 100.0:
        status = "Arrhythmia Warning"
        status_code = "danger"
        description = f"High R-R interval variation (SDNN: {sdnn:.1f} ms, RMSSD: {rmssd:.1f} ms)."
    else:
        status = "Normal Sinus Rhythm"
        status_code = "normal"
        description = f"Healthy heart rate ({bpm:.1f} BPM) with stable cardiac rhythm."

    # Signal Noise Estimation (Signal-to-Noise Ratio proxy)
    signal_power = np.mean(signal ** 2)
    noise_est = np.var(signal - savgol_filter(signal, min(15, max(5, len(signal)//2*2-1)), 2)) if len(signal) > 15 else 0.001
    snr_db = float(10 * np.log10(signal_power / max(noise_est, 1e-6)))

    return {
        "bpm": round(bpm, 2),
        "peak_count": len(peaks),
        "duration_sec": round(duration_sec, 2),
        "mean_rr_ms": round(mean_rr, 2),
        "min_rr_ms": round(min_rr, 2),
        "max_rr_ms": round(max_rr, 2),
        "sdnn_ms": round(sdnn, 2),
        "rmssd_ms": round(rmssd, 2),
        "snr_db": round(snr_db, 2),
        "status": status,
        "status_code": status_code,
        "description": description,
        "rr_intervals_ms": [round(float(x), 2) for x in rr_intervals_ms]
    }

def process_ecg_pipeline(
    raw_signal: List[float],
    fs: float = 250.0,
    cutoff: float = 20.0,
    order: int = 5,
    savgol_window: int = 11,
    savgol_poly: int = 3,
    distance_factor: float = 0.35,
    height_threshold: Optional[float] = None
) -> Dict[str, Any]:
    """
    Complete end-to-end ECG Processing Pipeline.
    """
    signal_arr = np.array(raw_signal, dtype=float)
    
    # 1. Butterworth Low-Pass Filter
    filtered_signal = apply_butterworth_filter(signal_arr, cutoff, fs, order)
    
    # 2. Savitzky-Golay Smoothing Filter
    smoothed_signal = apply_savgol_filter(filtered_signal, savgol_window, savgol_poly)
    
    # 3. Peak Detection
    peaks, _ = detect_peaks(smoothed_signal, fs, distance_factor, height_threshold)
    
    # 4. Metrics & Diagnostics Calculation
    metrics = calculate_metrics(smoothed_signal, peaks, fs)
    
    # Format time array
    time_array = np.arange(len(signal_arr)) / fs
    
    return {
        "time": [round(float(t), 4) for t in time_array],
        "raw_signal": [round(float(v), 4) for v in signal_arr],
        "filtered_signal": [round(float(v), 4) for v in filtered_signal],
        "smoothed_signal": [round(float(v), 4) for v in smoothed_signal],
        "peak_indices": [int(p) for p in peaks],
        "peak_times": [round(float(p / fs), 4) for p in peaks],
        "peak_amplitudes": [round(float(smoothed_signal[p]), 4) for p in peaks],
        "metrics": metrics,
        "fs": fs
    }
