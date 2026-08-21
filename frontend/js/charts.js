/**
 * ECG Charting Module using Chart.js
 */

let ecgChartInstance = null;
let rrChartInstance = null;

/**
 * Initialize or update main ECG Waveform Chart
 */
function renderEcgChart(data, visibilityFlags = { raw: true, filtered: true, smoothed: true, peaks: true }) {
    const ctx = document.getElementById('ecgChart').getContext('2d');
    
    const timeLabels = data.time || [];
    const rawSignal = data.raw_signal || [];
    const filteredSignal = data.filtered_signal || [];
    const smoothedSignal = data.smoothed_signal || [];
    const peakIndices = data.peak_indices || [];

    // Map peak scatter points
    const peakData = [];
    peakIndices.forEach(idx => {
        if (idx < timeLabels.length) {
            peakData.push({
                x: timeLabels[idx],
                y: smoothedSignal[idx] !== undefined ? smoothedSignal[idx] : rawSignal[idx]
            });
        }
    });

    const datasets = [];

    // 1. Raw Signal
    if (visibilityFlags.raw) {
        datasets.push({
            label: 'Raw Signal',
            data: timeLabels.map((t, i) => ({ x: t, y: rawSignal[i] })),
            borderColor: '#64748b',
            borderWidth: 1.5,
            borderDash: [3, 3],
            pointRadius: 0,
            tension: 0.1,
            order: 4
        });
    }

    // 2. Butterworth Filtered
    if (visibilityFlags.filtered) {
        datasets.push({
            label: 'Butterworth Low-Pass',
            data: timeLabels.map((t, i) => ({ x: t, y: filteredSignal[i] })),
            borderColor: '#38bdf8',
            borderWidth: 2,
            pointRadius: 0,
            tension: 0.2,
            order: 3
        });
    }

    // 3. Savitzky-Golay Smoothed
    if (visibilityFlags.smoothed) {
        datasets.push({
            label: 'Savitzky-Golay Smoothed',
            data: timeLabels.map((t, i) => ({ x: t, y: smoothedSignal[i] })),
            borderColor: '#10b981',
            borderWidth: 2.5,
            pointRadius: 0,
            tension: 0.2,
            order: 2
        });
    }

    // 4. Detected R-Peaks
    if (visibilityFlags.peaks) {
        datasets.push({
            label: 'Detected R-Peaks',
            data: peakData,
            type: 'scatter',
            backgroundColor: '#ef4444',
            borderColor: '#ffffff',
            borderWidth: 1.5,
            pointRadius: 6,
            pointHoverRadius: 8,
            order: 1
        });
    }

    if (ecgChartInstance) {
        ecgChartInstance.data.datasets = datasets;
        ecgChartInstance.update('none');
    } else {
        ecgChartInstance = new Chart(ctx, {
            type: 'line',
            data: { datasets },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                animation: { duration: 300 },
                interaction: { mode: 'nearest', intersect: false },
                scales: {
                    x: {
                        type: 'linear',
                        title: { display: true, text: 'Time (Seconds)', color: '#94a3b8' },
                        grid: { color: 'rgba(255, 255, 255, 0.05)' },
                        ticks: { color: '#94a3b8' }
                    },
                    y: {
                        title: { display: true, text: 'Amplitude (mV)', color: '#94a3b8' },
                        grid: { color: 'rgba(255, 255, 255, 0.05)' },
                        ticks: { color: '#94a3b8' }
                    }
                },
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: 'rgba(18, 25, 42, 0.9)',
                        titleColor: '#f8fafc',
                        bodyColor: '#94a3b8',
                        borderColor: 'rgba(6, 182, 212, 0.3)',
                        borderWidth: 1,
                        padding: 10,
                        displayColors: true
                    }
                }
            }
        });
    }
}

/**
 * Initialize or update R-R Tachogram Chart
 */
function renderRrChart(rrIntervals) {
    const ctx = document.getElementById('rrChart').getContext('2d');
    
    const labels = rrIntervals.map((_, i) => `Beat ${i + 1}-${i + 2}`);
    
    if (rrChartInstance) {
        rrChartInstance.data.labels = labels;
        rrChartInstance.data.datasets[0].data = rrIntervals;
        rrChartInstance.update('none');
    } else {
        rrChartInstance = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'R-R Interval (ms)',
                    data: rrIntervals,
                    backgroundColor: 'rgba(6, 182, 212, 0.4)',
                    borderColor: '#06b6d4',
                    borderWidth: 1.5,
                    borderRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                animation: { duration: 300 },
                scales: {
                    x: {
                        grid: { display: false },
                        ticks: { color: '#94a3b8', font: { size: 10 } }
                    },
                    y: {
                        title: { display: true, text: 'Interval (ms)', color: '#94a3b8' },
                        grid: { color: 'rgba(255, 255, 255, 0.05)' },
                        ticks: { color: '#94a3b8' }
                    }
                },
                plugins: {
                    legend: { display: false }
                }
            }
        });
    }
}
