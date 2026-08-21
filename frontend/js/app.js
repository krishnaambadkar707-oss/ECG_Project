/**
 * Main Frontend Application Controller
 */

document.addEventListener('DOMContentLoaded', () => {
    // Current Application State
    const state = {
        preset: 'normal',
        customSignal: null,
        fs: 250,
        cutoff: 20.0,
        order: 5,
        savgolWindow: 11,
        savgolPoly: 3,
        distFactor: 0.35,
        visibility: {
            raw: true,
            filtered: true,
            smoothed: true,
            peaks: true
        },
        currentData: null
    };

    // DOM Element References
    const elements = {
        presetSelect: document.getElementById('presetSelect'),
        csvFileInput: document.getElementById('csvFileInput'),
        dropzone: document.getElementById('dropzone'),
        fileUploadInfo: document.getElementById('fileUploadInfo'),
        
        // Sliders & Values
        cutoffSlider: document.getElementById('cutoffSlider'),
        cutoffVal: document.getElementById('cutoffVal'),
        fsSlider: document.getElementById('fsSlider'),
        fsVal: document.getElementById('fsVal'),
        orderSlider: document.getElementById('orderSlider'),
        orderVal: document.getElementById('orderVal'),
        savgolWindowSlider: document.getElementById('savgolWindowSlider'),
        savgolWindowVal: document.getElementById('savgolWindowVal'),
        savgolPolySlider: document.getElementById('savgolPolySlider'),
        savgolPolyVal: document.getElementById('savgolPolyVal'),
        distFactorSlider: document.getElementById('distFactorSlider'),
        distFactorVal: document.getElementById('distFactorVal'),
        resetParamsBtn: document.getElementById('resetParamsBtn'),

        // Visibility Toggles
        toggleRaw: document.getElementById('toggleRaw'),
        toggleFiltered: document.getElementById('toggleFiltered'),
        toggleSmoothed: document.getElementById('toggleSmoothed'),
        togglePeaks: document.getElementById('togglePeaks'),
        
        // Audio & Export
        audioToggleBtn: document.getElementById('audioToggleBtn'),
        audioIcon: document.getElementById('audioIcon'),
        audioText: document.getElementById('audioText'),
        exportCsvBtn: document.getElementById('exportCsvBtn'),

        // Metrics Display
        bpmValue: document.getElementById('bpmValue'),
        statusBadge: document.getElementById('statusBadge'),
        heartPulse: document.getElementById('heartPulse'),
        rrMeanValue: document.getElementById('rrMeanValue'),
        sdnnValue: document.getElementById('sdnnValue'),
        rmssdValue: document.getElementById('rmssdValue'),
        peaksCountValue: document.getElementById('peaksCountValue'),
        durationValue: document.getElementById('durationValue'),
        snrValue: document.getElementById('snrValue'),
        assessmentTitle: document.getElementById('assessmentTitle'),
        assessmentDesc: document.getElementById('assessmentDesc'),
        assessmentIcon: document.getElementById('assessmentIcon'),
        beatTableBody: document.getElementById('beatTableBody'),

        // API Status
        apiStatusBadge: document.getElementById('apiStatusBadge'),
        apiStatusText: document.getElementById('apiStatusText')
    };

    // Debounce timer for smooth slider updates
    let fetchDebounceTimer = null;

    function triggerFetchWithDebounce(delay = 150) {
        clearTimeout(fetchDebounceTimer);
        fetchDebounceTimer = setTimeout(() => {
            fetchAndProcessECG();
        }, delay);
    }

    /**
     * Fetch API process request
     */
    async function fetchAndProcessECG() {
        const payload = {
            preset: state.customSignal ? null : state.preset,
            raw_signal: state.customSignal,
            fs: parseFloat(state.fs),
            cutoff: parseFloat(state.cutoff),
            order: parseInt(state.order),
            savgol_window: parseInt(state.savgolWindow),
            savgol_poly: parseInt(state.savgolPoly),
            distance_factor: parseFloat(state.distFactor)
        };

        try {
            const response = await fetch('/api/process_ecg', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                const err = await response.json();
                throw new Error(err.detail || 'Server processing error');
            }

            const data = await response.json();
            state.currentData = data;
            
            // Render UI
            updateMetricsUI(data.metrics);
            renderEcgChart(data, state.visibility);
            renderRrChart(data.metrics.rr_intervals_ms || []);
            updateBeatTable(data);

            // Audio bleeps
            if (window.heartbeatAudio && !window.heartbeatAudio.isMuted) {
                window.heartbeatAudio.scheduleBeats(data.peak_times);
            }

            setApiStatus(true, "FastAPI Engine Online");
        } catch (error) {
            console.error("ECG Processing Error:", error);
            setApiStatus(false, "Connection / Processing Error");
        }
    }

    /**
     * Update Metrics & Assessment Cards
     */
    function updateMetricsUI(metrics) {
        if (!metrics) return;

        elements.bpmValue.textContent = metrics.bpm.toFixed(1);
        elements.rrMeanValue.textContent = metrics.mean_rr_ms.toFixed(0);
        elements.sdnnValue.textContent = metrics.sdnn_ms.toFixed(1);
        elements.rmssdValue.textContent = metrics.rmssd_ms.toFixed(1);
        elements.peaksCountValue.textContent = metrics.peak_count;
        elements.durationValue.textContent = metrics.duration_sec.toFixed(1);
        elements.snrValue.textContent = metrics.snr_db.toFixed(1);

        // Status Badge
        elements.statusBadge.textContent = metrics.status;
        elements.statusBadge.className = `badge ${metrics.status_code}`;

        // Pulsing animation
        if (metrics.bpm > 0) {
            elements.heartPulse.classList.add('pulsing');
            // Adjust pulse rate matching BPM
            const duration = (60 / metrics.bpm).toFixed(2);
            elements.heartPulse.style.animationDuration = `${duration}s`;
        } else {
            elements.heartPulse.classList.remove('pulsing');
        }

        // Assessment text
        elements.assessmentTitle.textContent = metrics.status;
        elements.assessmentDesc.textContent = metrics.description;
    }

    /**
     * Update Beat Event Timings Table
     */
    function updateBeatTable(data) {
        const peakTimes = data.peak_times || [];
        const peakAmps = data.peak_amplitudes || [];
        const rrIntervals = data.metrics?.rr_intervals_ms || [];

        if (peakTimes.length === 0) {
            elements.beatTableBody.innerHTML = '<tr><td colspan="4" class="text-center text-muted">No peaks detected</td></tr>';
            return;
        }

        let html = '';
        peakTimes.forEach((t, i) => {
            const rr = i > 0 ? rrIntervals[i - 1] + ' ms' : '--';
            html += `
                <tr>
                    <td><strong>#${i + 1}</strong></td>
                    <td>${t.toFixed(3)}s</td>
                    <td>${peakAmps[i] !== undefined ? peakAmps[i].toFixed(3) : '--'}</td>
                    <td>${rr}</td>
                </tr>
            `;
        });

        elements.beatTableBody.innerHTML = html;
    }

    /**
     * API Status Helper
     */
    function setApiStatus(isOnline, text) {
        elements.apiStatusText.textContent = text;
        const dot = elements.apiStatusBadge.querySelector('.status-dot');
        if (dot) {
            dot.className = `status-dot ${isOnline ? 'green' : 'red'}`;
        }
    }

    /**
     * Event Listeners & Controls Binding
     */

    // Preset selector
    elements.presetSelect.addEventListener('change', (e) => {
        state.preset = e.target.value;
        state.customSignal = null;
        elements.fileUploadInfo.classList.add('hidden');
        triggerFetchWithDebounce(0);
    });

    // CSV File Upload
    elements.csvFileInput.addEventListener('change', async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        const formData = new FormData();
        formData.append('file', file);

        try {
            const res = await fetch('/api/upload_csv', {
                method: 'POST',
                body: formData
            });

            if (!res.ok) {
                const err = await res.json();
                throw new Error(err.detail || 'Failed to parse CSV file');
            }

            const data = await res.json();
            state.customSignal = data.signal;
            elements.fileUploadInfo.textContent = `Loaded '${data.filename}' (${data.sample_count} points, col: ${data.column_used})`;
            elements.fileUploadInfo.classList.remove('hidden');
            triggerFetchWithDebounce(0);
        } catch (err) {
            alert("CSV Upload Error: " + err.message);
        }
    });

    // Sliders
    elements.cutoffSlider.addEventListener('input', (e) => {
        state.cutoff = e.target.value;
        elements.cutoffVal.textContent = `${parseFloat(state.cutoff).toFixed(1)} Hz`;
        triggerFetchWithDebounce();
    });

    elements.fsSlider.addEventListener('input', (e) => {
        state.fs = e.target.value;
        elements.fsVal.textContent = `${state.fs} Hz`;
        triggerFetchWithDebounce();
    });

    elements.orderSlider.addEventListener('input', (e) => {
        state.order = e.target.value;
        elements.orderVal.textContent = state.order;
        triggerFetchWithDebounce();
    });

    elements.savgolWindowSlider.addEventListener('input', (e) => {
        let val = parseInt(e.target.value);
        if (val % 2 === 0) val += 1; // Ensure odd
        state.savgolWindow = val;
        elements.savgolWindowVal.textContent = val;
        triggerFetchWithDebounce();
    });

    elements.savgolPolySlider.addEventListener('input', (e) => {
        state.savgolPoly = e.target.value;
        elements.savgolPolyVal.textContent = state.savgolPoly;
        triggerFetchWithDebounce();
    });

    elements.distFactorSlider.addEventListener('input', (e) => {
        state.distFactor = e.target.value;
        elements.distFactorVal.innerHTML = `${parseFloat(state.distFactor).toFixed(2)} &times; f_s`;
        triggerFetchWithDebounce();
    });

    // Reset Parameters
    elements.resetParamsBtn.addEventListener('click', () => {
        state.cutoff = 20.0;
        state.fs = 250;
        state.order = 5;
        state.savgolWindow = 11;
        state.savgolPoly = 3;
        state.distFactor = 0.35;

        elements.cutoffSlider.value = 20.0;
        elements.cutoffVal.textContent = "20.0 Hz";
        elements.fsSlider.value = 250;
        elements.fsVal.textContent = "250 Hz";
        elements.orderSlider.value = 5;
        elements.orderVal.textContent = "5";
        elements.savgolWindowSlider.value = 11;
        elements.savgolWindowVal.textContent = "11";
        elements.savgolPolySlider.value = 3;
        elements.savgolPolyVal.textContent = "3";
        elements.distFactorSlider.value = 0.35;
        elements.distFactorVal.innerHTML = "0.35 &times; f_s";

        triggerFetchWithDebounce(0);
    });

    // Waveform Visibility Toggles
    const updateVisibility = () => {
        state.visibility.raw = elements.toggleRaw.checked;
        state.visibility.filtered = elements.toggleFiltered.checked;
        state.visibility.smoothed = elements.toggleSmoothed.checked;
        state.visibility.peaks = elements.togglePeaks.checked;

        if (state.currentData) {
            renderEcgChart(state.currentData, state.visibility);
        }
    };

    elements.toggleRaw.addEventListener('change', updateVisibility);
    elements.toggleFiltered.addEventListener('change', updateVisibility);
    elements.toggleSmoothed.addEventListener('change', updateVisibility);
    elements.togglePeaks.addEventListener('change', updateVisibility);

    // Audio Toggle
    elements.audioToggleBtn.addEventListener('click', () => {
        if (window.heartbeatAudio) {
            const active = window.heartbeatAudio.toggle();
            elements.audioText.textContent = active ? "Audio Enabled" : "Audio Muted";
            elements.audioIcon.setAttribute('data-lucide', active ? 'volume-2' : 'volume-x');
            lucide.createIcons();
            
            if (active && state.currentData) {
                window.heartbeatAudio.scheduleBeats(state.currentData.peak_times);
            }
        }
    });

    // Export Processed CSV Data
    elements.exportCsvBtn.addEventListener('click', () => {
        if (!state.currentData) return;

        const d = state.currentData;
        let csvContent = "data:text/csv;charset=utf-8,Time_sec,Raw_Signal,Filtered_Signal,Smoothed_Signal,Is_R_Peak\n";
        
        const peakSet = new Set(d.peak_indices || []);
        d.time.forEach((t, i) => {
            const isPeak = peakSet.has(i) ? 1 : 0;
            csvContent += `${t},${d.raw_signal[i]},${d.filtered_signal[i]},${d.smoothed_signal[i]},${isPeak}\n`;
        });

        const encodedUri = encodeURI(csvContent);
        const link = document.createElement("a");
        link.setAttribute("href", encodedUri);
        link.setAttribute("download", `ecg_analysis_${state.preset}.csv`);
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    });

    // Initial load
    fetchAndProcessECG();
});
