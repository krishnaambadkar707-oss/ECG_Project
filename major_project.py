import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from scipy.signal import butter, filtfilt
from scipy.signal import find_peaks
from scipy.signal import savgol_filter

# -----------------------------
# Load ECG Data
# -----------------------------

mydataset = {
    'ECG': [0.12, 0.15, 0.18, 0.30, 0.45, 0.80, 1.10, 0.75, 0.40, 0.22, 0.19, 0.14, 0.32, 0.50, 0.85, 1.20, 0.90, 0.55, 0.30, 0.18, 0.16, 0.28, 0.60, 0.95, 1.30, 0.85,]
}
data = pd.DataFrame(mydataset)

ecg_signal = data["ECG"].values

# Sampling frequency
fs = 250

# -----------------------------
# Butterworth Low-Pass Filter
# -----------------------------
def butter_lowpass(cutoff, fs, order=5):
    nyquist = 0.5 * fs
    normal_cutoff = cutoff / nyquist
    b, a = butter(order, normal_cutoff, btype='low')
    return b, a

cutoff = 20

b, a = butter_lowpass(cutoff, fs)

filtered_signal = filtfilt(b, a, ecg_signal)

# -----------------------------
# Smooth Signal
# -----------------------------
smoothed_signal = savgol_filter(filtered_signal, 11, 3)

# -----------------------------
# Peak Detection
# -----------------------------
peaks, _ = find_peaks(smoothed_signal,
                      distance=fs*0.6,
                      height=np.mean(smoothed_signal))

# -----------------------------
# BPM Calculation
# -----------------------------
duration = len(ecg_signal) / fs

bpm = (len(peaks) * 60) / duration

print(f"Detected BPM: {bpm:.2f}")

# -----------------------------
# Plot ECG Signal
# -----------------------------
plt.figure(figsize=(15,6))

plt.plot(smoothed_signal, label="Filtered ECG")

plt.plot(peaks,
         smoothed_signal[peaks],
         "ro",
         label="Detected Beats")

plt.title("ECG Signal Analyzer")
plt.xlabel("Samples")
plt.ylabel("Amplitude")
plt.legend()

plt.grid(True)

plt.show()