// Optional browser-native dictation. No audio is sent to the UNSTUCK backend.
export function setupSpeechInput({ input, button, status, onStateChange = () => {} }) {
  const Recognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  let recognition = null;
  let phase = 'idle';
  let disabled = false;
  let stopTimeout = null;
  const stoppedMessage = 'Voice input stopped. Your text is ready to edit.';
  let endMessage = stoppedMessage;
  const active = () => phase !== 'idle';

  function paint() {
    button.disabled = (!active() && disabled) || phase === 'stopping' || !Recognition;
    button.setAttribute('aria-pressed', String(active()));
    button.dataset.listening = String(active());
    button.querySelector('span').textContent = phase === 'stopping' ? 'Stopping…' : active() ? 'Stop dictation' : 'Use microphone';
    button.setAttribute('aria-label', active() ? 'Stop voice input' : 'Start voice input');
  }
  function finish(message) {
    clearTimeout(stopTimeout);
    recognition = null;
    phase = 'idle';
    status.textContent = message;
    paint();
    onStateChange();
  }
  function stop() {
    if (!recognition || phase === 'stopping') return;
    const session = recognition;
    phase = 'stopping';
    status.textContent = 'Stopping voice input…';
    paint();
    try { session.stop(); } catch { try { session.abort(); } catch {} }
    // Some engines fail to fire end after cancelling a permission request.
    if (recognition === session) stopTimeout = setTimeout(() => {
      if (recognition !== session) return;
      try { session.abort(); } catch {}
      if (recognition === session) finish(endMessage);
    }, 2000);
  }
  const errorMessages = {
    'not-allowed': 'Microphone permission was denied. Allow microphone access in your browser settings, or type instead.',
    'service-not-allowed': 'Voice input is not allowed by this browser. You can type instead.',
    'audio-capture': 'No microphone is available. Check your microphone, or type instead.',
    'no-speech': 'No speech was heard. Try the microphone again, or type instead.',
    'network': 'The browser’s speech service could not connect. Try again, or type instead.',
    'language-not-supported': 'Your browser could not recognize this language. You can type instead.',
    'aborted': 'Voice input stopped. Your text is ready to edit.',
  };
  button.addEventListener('click', () => {
    if (active()) { stop(); return; }
    if (!Recognition || disabled) return;
    if (input.value.length >= input.maxLength) {
      status.textContent = 'The 2,000-character limit is reached. Edit your text before dictating more.';
      return;
    }
    let session;
    try {
      session = new Recognition();
      session.lang = navigator.language || navigator.languages?.[0] || 'en-US';
      session.continuous = true;
      // Final phrases append once; users can edit freely while dictating.
      session.interimResults = false;
      session.maxAlternatives = 1;
      const consumed = new Set();
      endMessage = stoppedMessage;
      recognition = session;
      phase = 'starting';
      status.textContent = 'Starting microphone… Allow access if your browser asks.';
      session.onstart = () => {
        if (recognition !== session || phase === 'stopping') return;
        phase = 'listening';
        status.textContent = 'Listening… Speak your thoughts. Click the microphone again to stop.';
        paint();
      };
      session.onresult = (event) => {
        if (recognition !== session) return;
        for (let index = event.resultIndex; index < event.results.length; index++) {
          const result = event.results[index];
          if (!result.isFinal || consumed.has(index)) continue;
          consumed.add(index);
          const text = result[0]?.transcript?.trim();
          if (!text) continue;
          const separator = input.value && !/\s$/.test(input.value) ? ' ' : '';
          const combined = input.value + separator + text;
          input.value = combined.slice(0, input.maxLength);
          input.dispatchEvent(new Event('input', { bubbles: true }));
          if (combined.length >= input.maxLength) {
            endMessage = 'The 2,000-character limit is reached. Your text is ready to edit.';
            stop();
            status.textContent = endMessage;
            break;
          }
        }
      };
      session.onerror = (event) => {
        if (recognition !== session) return;
        finish(errorMessages[event.error] || 'Voice recognition could not finish. Your text is kept; try again or type instead.');
        try { session.abort(); } catch {}
      };
      session.onend = () => {
        if (recognition === session) finish(endMessage);
      };
      paint();
      onStateChange();
      session.start();
    } catch (error) {
      finish(error.name === 'NotAllowedError' ? errorMessages['not-allowed'] : 'Voice input could not start. Your text is kept; try again or type instead.');
      try { session?.abort(); } catch {}
    }
  });
  window.addEventListener('pagehide', () => {
    const session = recognition;
    if (!session) return;
    finish('Voice input stopped.');
    try { session.abort(); } catch {}
  });
  if (!Recognition) status.textContent = 'Voice input is not supported in this browser. You can still type your thoughts.';
  paint();
  return {
    get active() { return active(); },
    stop,
    setDisabled(value) { disabled = value; paint(); },
  };
}
