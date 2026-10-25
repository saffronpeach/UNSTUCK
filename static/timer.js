// Pure timer logic with an injectable clock for deterministic verification.
export class FocusTimer {
  constructor(now = () => Date.now()) {
    this.now = now;
    this.minutes = 7;
    this.reset();
  }
  setMinutes(minutes) {
    if (this.phase !== 'ready' || !Number.isInteger(minutes) || minutes < 5 || minutes > 10) return;
    this.minutes = minutes;
    this.reset();
  }
  reset() {
    this.phase = 'ready';
    this.remaining = this.minutes * 60000;
    this.deadline = null;
  }
  tick() {
    if (this.phase === 'running') {
      this.remaining = Math.max(0, this.deadline - this.now());
      if (this.remaining === 0) { this.phase = 'expired'; this.deadline = null; }
    }
    return this.remaining;
  }
  start() {
    if (!['ready', 'paused'].includes(this.phase)) return;
    this.deadline = this.now() + this.remaining;
    this.phase = 'running';
  }
  pause() {
    if (this.phase !== 'running') return;
    this.tick();
    if (this.phase === 'expired') return;
    this.phase = 'paused';
    this.deadline = null;
  }
  complete() {
    this.tick();
    this.phase = 'complete';
    this.deadline = null;
  }
  get display() {
    this.tick();
    const seconds = Math.ceil(this.remaining / 1000);
    return `${String(Math.floor(seconds / 60)).padStart(2, '0')}:${String(seconds % 60).padStart(2, '0')}`;
  }
}
