import { FocusTimer } from './timer.js';
const $ = (id) => document.getElementById(id);
const timer = new FocusTimer();
let current = null;
let originalThoughts = '';
let busy = false;
let timerVisible = false;
let interval = null;
let lastPhase = '';

function error(message = '') {
  $('retry-notice').textContent = '';
  $('retry-notice').hidden = true;
  $('error').textContent = message;
  $('error').hidden = !message;
}
function render() {
  const display = timer.display;
  const phase = timer.phase;
  const locked = ['running', 'paused'].includes(phase);
  $('submit').disabled = busy || locked;
  $('retry').disabled = busy || locked;
  $('complete').disabled = busy || phase === 'complete';
  $('duration').disabled = busy || phase !== 'ready';
  $('start').disabled = busy;
  $('pause').disabled = busy;
  $('reset').disabled = busy;
  $('loading').hidden = !busy;
  $('thought-form').setAttribute('aria-busy', String(busy));
  $('start').hidden = phase !== 'ready';
  $('timer-panel').hidden = !timerVisible;
  $('countdown').textContent = display;
  $('focus-setup').hidden = phase === 'complete';
  $('pause').hidden = !locked;
  $('pause').textContent = phase === 'paused' ? 'Resume' : 'Pause';
  $('reset').hidden = phase === 'complete';
  if (phase !== lastPhase) {
    $('timer-status').textContent = phase === 'paused' ? 'Take a breath. Resume when you’re ready.' :
      phase === 'expired' ? 'Your focus session has finished.' : 'A little space for one small step.';
    lastPhase = phase;
  }
  $('completion').hidden = !['expired', 'complete'].includes(phase);
  if (phase === 'expired') $('completion').textContent = 'You did it! Every small step counts.';
  if (phase === 'complete') $('completion').textContent = 'One small step done. That counts.';
  if (phase !== 'running' && interval !== null) { clearInterval(interval); interval = null; }
}
function startInterval() {
  if (interval === null) interval = setInterval(render, 200);
  render();
}
async function requestStep(retry = false) {
  if (busy || ['running', 'paused'].includes(timer.phase)) return;
  const thoughts = retry ? originalThoughts : $('thoughts').value.trim();
  if (!thoughts || thoughts.length > 2000) {
    error(!thoughts ? 'Tell us a little about what’s keeping you stuck.' : 'Keep your thoughts under 2,000 characters for this step.');
    $('thoughts').focus();
    return;
  }
  busy = true;
  error();
  render();
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 35000);
  try {
    const response = await fetch('/api/step', {
      method: 'POST', headers: { 'Content-Type': 'application/json' }, signal: controller.signal,
      body: JSON.stringify({ thoughts, previous_action: retry ? current.action : null }),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(typeof data.detail === 'string' ? data.detail : 'Check your thoughts and try again.');
    if (typeof data.action !== 'string' || !data.action.trim() || typeof data.acknowledgment !== 'string' ||
        !data.acknowledgment.trim() || !Number.isInteger(data.recommended_minutes) ||
        data.recommended_minutes < 5 || data.recommended_minutes > 10) throw new Error('We couldn’t get a usable step. Please try again.');
    current = data;
    originalThoughts = thoughts;
    $('acknowledgment').textContent = data.acknowledgment;
    $('action-heading').textContent = data.action;
    $('recommendation').textContent = `Suggested focus: ${data.recommended_minutes} minutes · one small beginning`;
    timer.reset(); timer.setMinutes(7);
    $('duration').value = '7';
    timerVisible = false;
    $('result').hidden = false;
    $('result').scrollIntoView({ behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth', block: 'nearest' });
  } catch (err) {
    const message = err.name === 'AbortError' ? 'That took longer than expected. Please try again.' :
      err instanceof TypeError ? 'We couldn’t connect. Check your connection and try again.' : err.message;
    if (retry && current) {
      $('retry-notice').textContent = `Couldn't get another step. Your previous step is unchanged and ready to use. ${message}`;
      $('retry-notice').hidden = false;
    } else {
      error(message);
    }
  } finally {
    clearTimeout(timeout);
    busy = false;
    render();
  }
}
$('thought-form').addEventListener('submit', (event) => { event.preventDefault(); requestStep(); });
$('thoughts').addEventListener('input', () => { $('character-count').textContent = `${$('thoughts').value.length} / 2000`; });
$('retry').addEventListener('click', () => requestStep(true));
$('duration').addEventListener('change', () => { timer.setMinutes(Number($('duration').value)); render(); });
$('start').addEventListener('click', () => { timerVisible = true; timer.start(); startInterval(); });
$('pause').addEventListener('click', () => { timer.phase === 'paused' ? timer.start() : timer.pause(); startInterval(); });
$('reset').addEventListener('click', () => { timer.reset(); render(); });
$('complete').addEventListener('click', () => { timer.complete(); render(); });
document.addEventListener('visibilitychange', render);
render();
