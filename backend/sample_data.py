import numpy as np
from typing import Dict, List, Any

# Original dataset from major_project.py
ORIGINAL_ECG_DATA = [
    0.12, 0.15, 0.18, 0.30, 0.45, 0.80, 1.10, 0.75, 0.40, 0.22, 0.19, 0.14, 
    0.32, 0.50, 0.85, 1.20, 0.90, 0.55, 0.30, 0.18, 0.16, 0.28, 0.60, 0.95, 
    1.30, 0.85
]

def generate_synthetic_ecg(
    bpm: float = 72.0,
    fs: float = 250.0,
    duration_sec: float = 8.0,
    noise_level: float = 0.05,
    arrhythmia_type: str = "normal"
) -> List[float]:
    """
    Generate realistic synthetic ECG waveform with P, Q, R, S, T waves.
    """
    t = np.linspace(0, duration_sec, int(fs * duration_sec))
    beat_freq = bpm / 60.0  # Beats per second
    
    ecg = np.zeros_like(t)
    
    # Calculate heart beat peak times
    if arrhythmia_type == "arrhythmia":
        # Irregular beat intervals
        beat_times = []
        curr_t = 0.2
        np.random.seed(42)
        while curr_t < duration_sec - 0.2:
            beat_times.append(curr_t)
            # Add random jitter to RR interval
            interval = (1.0 / beat_freq) * np.random.uniform(0.6, 1.4)
            curr_t += interval
    else:
        beat_times = np.arange(0.2, duration_sec, 1.0 / beat_freq)
        
    for b_time in beat_times:
        dt = t - b_time
        
        # P-wave (small bump before R)
        p_wave = 0.15 * np.exp(-((dt + 0.16) / 0.03) ** 2)
        
        # Q-wave (small negative dip before R)
        q_wave = -0.15 * np.exp(-((dt + 0.05) / 0.015) ** 2)
        
        # R-wave (sharp tall positive peak)
        r_wave = 1.25 * np.exp(-(dt / 0.018) ** 2)
        
        # S-wave (sharp negative dip after R)
        s_wave = -0.35 * np.exp(-((dt - 0.04) / 0.018) ** 2)
        
        # T-wave (broader positive wave after S)
        t_wave = 0.30 * np.exp(-((dt - 0.22) / 0.06) ** 2)
        
        ecg += (p_wave + q_wave + r_wave + s_wave + t_wave)
        
    # Baseline wander (low frequency noise)
    baseline_wander = 0.08 * np.sin(2 * np.pi * 0.3 * t)
    
    # Random Gaussian noise
    if noise_level > 0:
        np.random.seed(123)
        high_freq_noise = np.random.normal(0, noise_level, size=len(t))
    else:
        high_freq_noise = np.zeros_like(t)
        
    final_signal = ecg + baseline_wander + high_freq_noise + 0.2
    return [round(float(val), 4) for val in final_signal]

def get_preset_datasets() -> Dict[str, Dict[str, Any]]:
    """
    Returns curated preset datasets for the frontend dashboard.
    """
    return {
        "baseline": {
            "name": "Original Major Project Data",
            "fs": 250,
            "description": "The exact baseline 26-point ECG signal from major_project.py",
            "signal": ORIGINAL_ECG_DATA
        },
        "normal": {
            "name": "Normal Sinus Rhythm (72 BPM)",
            "fs": 250,
            "description": "Synthetic multi-cycle ECG showing regular P-QRS-T complexes at healthy 72 BPM.",
            "signal": generate_synthetic_ecg(bpm=72.0, fs=250.0, duration_sec=6.0, noise_level=0.04, arrhythmia_type="normal")
        },
        "tachycardia": {
            "name": "Tachycardia (130 BPM)",
            "fs": 250,
            "description": "Rapid heart rate simulation with shortened R-R intervals (>100 BPM).",
            "signal": generate_synthetic_ecg(bpm=130.0, fs=250.0, duration_sec=6.0, noise_level=0.05, arrhythmia_type="normal")
        },
        "bradycardia": {
            "name": "Bradycardia (48 BPM)",
            "fs": 250,
            "description": "Slow heart rate simulation with elongated R-R intervals (<60 BPM).",
            "signal": generate_synthetic_ecg(bpm=48.0, fs=250.0, duration_sec=6.0, noise_level=0.04, arrhythmia_type="normal")
        },
        "arrhythmia": {
            "name": "Atrial Arrhythmia",
            "fs": 250,
            "description": "Irregular sinus rhythm with variable R-R spacing and ectopic beat triggers.",
            "signal": generate_synthetic_ecg(bpm=78.0, fs=250.0, duration_sec=8.0, noise_level=0.06, arrhythmia_type="arrhythmia")
        },
        "noisy": {
            "name": "High Noise & Motion Artifacts",
            "fs": 250,
            "description": "ECG signal corrupted by muscle tremors, baseline drift, and powerline interference.",
            "signal": generate_synthetic_ecg(bpm=75.0, fs=250.0, duration_sec=6.0, noise_level=0.22, arrhythmia_type="normal")
        }
    }
