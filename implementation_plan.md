# Full-Stack ECG Signal Analyzer & Diagnostics Web Application

Transform the standalone `major_project.py` script into a feature-rich, interactive web application featuring a Python FastAPI backend for biomedical signal processing and a dynamic frontend UI with real-time charting, parameter tuning, audio synthesis, and HRV analysis.

## User Review Required

> [!IMPORTANT]
> - **Backend Framework**: We will use Python **FastAPI** with `scipy`, `numpy`, and `pandas` for advanced digital signal processing (DSP).
> - **Frontend Stack**: Built with vanilla HTML5, CSS3 (Glassmorphism design system), and JavaScript with Chart.js for smooth performance and responsive signal rendering.
> - **Compatibility**: The existing `major_project.py` script will remain untouched for legacy/reference purposes.

## Open Questions

None at present. Standard ports (`8000` for FastAPI backend, served statically or via API CORS) will be configured.

## Proposed Changes

### Backend (Python FastAPI)

#### [NEW] [requirements.txt](file:///c:/Users/krish/OneDrive/Desktop/Matplotlib/major_project/backend/requirements.txt)
Define backend dependencies: `fastapi`, `uvicorn`, `scipy`, `numpy`, `pandas`, `pydantic`.

#### [NEW] [signal_processing.py](file:///c:/Users/krish/OneDrive/Desktop/Matplotlib/major_project/backend/signal_processing.py)
Core DSP engine extending original logic:
- Butterworth Low-Pass Filter (`butter`, `filtfilt`)
- Savitzky-Golay Smoothing (`savgol_filter`)
- Dynamic R-Peak Detection (`find_peaks`) with adaptive thresholds
- Heart Rate (BPM) calculation
- Heart Rate Variability (HRV) metrics: SDNN, RMSSD, R-R intervals
- Diagnostic status classification (Normal Sinus Rhythm, Tachycardia, Bradycardia, Arrhythmia alert)

#### [NEW] [sample_data.py](file:///c:/Users/krish/OneDrive/Desktop/Matplotlib/major_project/backend/sample_data.py)
Generates realistic synthetic ECG signals for testing:
- Normal Sinus Rhythm (60–100 BPM)
- Tachycardia (> 100 BPM)
- Bradycardia (< 60 BPM)
- Arrhythmia with premature ventricular contractions (PVCs)
- High-Noise ECG (powerline noise & motion artifacts)

#### [NEW] [app.py](file:///c:/Users/krish/OneDrive/Desktop/Matplotlib/major_project/backend/app.py)
FastAPI application with endpoints:
- `POST /api/process_ecg`: Accepts signal data/preset + filter parameters, returns filtered waveforms, peaks, and diagnostics.
- `POST /api/upload_csv`: Processes user CSV uploads.
- `GET /api/presets`: Returns available ECG presets.
- Serves static frontend files for a single unified web experience.

---

### Frontend (Modern Web UI)

#### [NEW] [index.html](file:///c:/Users/krish/OneDrive/Desktop/Matplotlib/major_project/frontend/index.html)
Semantic HTML5 layout featuring:
- Hero header with live connection indicator & patient telemetry summary
- Signal Processing Control Panel (Cutoff frequency, filter order, Savgol window/polyorder, peak distance/height sliders)
- Main Visualization Canvas (Raw vs Butterworth vs Savitzky-Golay vs Detected Peaks)
- Metrics & Diagnostics Grid (BPM card, HRV stats, R-R interval distribution)
- ECG Presets & File Upload zone
- Audio Heartbeat Toggle

#### [NEW] [style.css](file:///c:/Users/krish/OneDrive/Desktop/Matplotlib/major_project/frontend/css/style.css)
Modern medical dark theme with glassmorphic cards, custom range sliders, glowing pulse animations, and responsive layout.

#### [NEW] [charts.js](file:///c:/Users/krish/OneDrive/Desktop/Matplotlib/major_project/frontend/js/charts.js)
Chart.js integration for dual-axis / multi-dataset ECG plotting with custom peak annotations.

#### [NEW] [audio.js](file:///c:/Users/krish/OneDrive/Desktop/Matplotlib/major_project/frontend/js/audio.js)
Web Audio API synthesizer that plays subtle heartbeat audio ticks mapped to R-peak intervals.

#### [NEW] [app.js](file:///c:/Users/krish/OneDrive/Desktop/Matplotlib/major_project/frontend/js/app.js)
Frontend controller managing API requests, parameter debouncing, CSV parsing, preset selection, and state updates.

---

### Execution Script

#### [NEW] [run_server.py](file:///c:/Users/krish/OneDrive/Desktop/Matplotlib/major_project/run_server.py)
A convenience runner script to launch the FastAPI server and open the web dashboard in the default browser.

## Verification Plan

### Automated Tests
- Run `python backend/signal_processing.py` to verify DSP functions, filter operations, peak detection accuracy, and HRV metric calculations.
- Test FastAPI endpoint payloads using Python HTTP test client or `pytest`.

### Manual Verification
- Start FastAPI server and navigate to `http://localhost:8000`.
- Adjust filter sliders (Cutoff, Savgol window, Peak distance) and confirm real-time chart re-rendering.
- Switch between ECG presets (Normal, Tachycardia, Bradycardia, Arrhythmia, Noisy) and verify diagnostic status updates.
- Test CSV file upload with custom ECG data points.
- Verify heartbeat audio toggle output against peak timings.
