/**
 * Web Audio API Heartbeat Synthesizer
 */

class HeartbeatAudio {
    constructor() {
        this.ctx = null;
        this.isMuted = true;
        this.timers = [];
    }

    init() {
        if (!this.ctx) {
            const AudioContext = window.AudioContext || window.webkitAudioContext;
            if (AudioContext) {
                this.ctx = new AudioContext();
            }
        }
        if (this.ctx && this.ctx.state === 'suspended') {
            this.ctx.resume();
        }
    }

    toggle() {
        this.isMuted = !this.isMuted;
        if (!this.isMuted) {
            this.init();
        } else {
            this.stopAll();
        }
        return !this.isMuted;
    }

    stopAll() {
        this.timers.forEach(t => clearTimeout(t));
        this.timers = [];
    }

    playSingleBeat() {
        if (this.isMuted || !this.ctx) return;
        
        try {
            const osc = this.ctx.createOscillator();
            const gain = this.ctx.createGain();

            osc.type = 'sine';
            osc.frequency.setValueAtTime(880, this.ctx.currentTime); // Pitch (880 Hz beep)
            osc.frequency.exponentialRampToValueAtTime(440, this.ctx.currentTime + 0.08);

            gain.gain.setValueAtTime(0.15, this.ctx.currentTime);
            gain.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + 0.08);

            osc.connect(gain);
            gain.connect(this.ctx.destination);

            osc.start();
            osc.stop(this.ctx.currentTime + 0.08);
        } catch (e) {
            console.warn("Audio play error:", e);
        }
    }

    scheduleBeats(peakTimesSec) {
        this.stopAll();
        if (this.isMuted || !peakTimesSec || peakTimesSec.length === 0) return;

        const startTime = Date.now();
        peakTimesSec.forEach(tSec => {
            const delayMs = tSec * 1000;
            const timer = setTimeout(() => {
                this.playSingleBeat();
            }, delayMs);
            this.timers.push(timer);
        });
    }
}

window.heartbeatAudio = new HeartbeatAudio();
