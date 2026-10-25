"""Browser regressions with a fake Web Speech engine; no real microphone or AI calls.
Run against UNSTUCK on port 8017 after installing optional Playwright.
"""
from playwright.sync_api import sync_playwright, expect

URL = 'http://127.0.0.1:8017'
RESULT = {'acknowledgment': 'One small beginning is enough.', 'action': 'Open the assignment document.', 'recommended_minutes': 7, 'priority': {'task': 'submission', 'basis': 'unspecified', 'evidence': ''}, 'priority_reason': 'A manageable starting point; no unstated deadline or urgency is assumed.'}
MOCK = r"""
window.__speech = [];
window.__emitSpeech = (texts, resultIndex = 0) => {
  const results = texts.map(({text, final = true}) => Object.assign([{transcript: text}], {isFinal: final}));
  window.__speech.at(-1).onresult?.({results, resultIndex});
};
class FakeSpeechRecognition {
  constructor() { window.__speech.push(this); this.stops = 0; this.aborts = 0; }
  start() {
    if (window.__startError) throw new DOMException('Do not expose raw engine details', window.__startError);
    if (!window.__delayStart) this.onstart?.();
  }
  stop() {
    this.stops++;
    if (window.__stopResult) window.__emitSpeech([{text: window.__stopResult}]);
    if (!window.__delayEnd) this.onend?.();
  }
  abort() { this.aborts++; this.onend?.(); }
}
Object.defineProperty(window, 'SpeechRecognition', {value: FakeSpeechRecognition, configurable: true});
Object.defineProperty(window, 'webkitSpeechRecognition', {value: undefined, configurable: true});
Object.defineProperty(navigator, 'language', {get: () => 'tr-TR', configurable: true});
"""


def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(channel='chrome', headless=True)
        context = browser.new_context(viewport={'width': 1280, 'height': 1100}, reduced_motion='reduce')
        context.add_init_script(MOCK)
        page = context.new_page()
        errors, calls = [], []
        page.on('pageerror', lambda error: errors.append(str(error)))
        def respond(route):
            calls.append(route.request.post_data_json)
            route.fulfill(json=RESULT)
        page.route('**/api/step', respond)
        page.goto(URL)
        expect(page.locator('#microphone')).to_be_enabled()
        expect(page.locator('#microphone')).to_have_attribute('type', 'button')
        page.locator('#thoughts').fill('I need help:')
        # Keyboard operation starts listening in the configured browser language.
        page.locator('#microphone').focus()
        page.keyboard.press('Enter')
        expect(page.locator('#microphone')).to_have_attribute('aria-pressed', 'true')
        expect(page.locator('#voice-status')).to_contain_text('Listening')
        expect(page.locator('#submit')).to_be_disabled()
        assert page.evaluate('window.__speech[0].lang') == 'tr-TR'
        assert page.evaluate('window.__speech[0].continuous') is True
        page.evaluate("window.__emitSpeech([{text: 'unfinished', final: false}])")
        expect(page.locator('#thoughts')).to_have_value('I need help:')
        page.evaluate("window.__emitSpeech([{text: 'I have three assignments.'}])")
        expect(page.locator('#thoughts')).to_have_value('I need help: I have three assignments.')
        # Re-delivery of finalized results must not duplicate speech or overwrite edits.
        page.locator('#thoughts').fill('Edited: I have three assignments.')
        page.evaluate("window.__emitSpeech([{text: 'I have three assignments.'}, {text: 'And little time.'}], 0)")
        expect(page.locator('#thoughts')).to_have_value('Edited: I have three assignments. And little time.')
        expect(page.locator('#character-count')).to_have_text('50 / 2000')
        assert calls == []
        page.evaluate("document.getElementById('thought-form').requestSubmit()")
        assert calls == []
        page.locator('#microphone').click()
        expect(page.locator('#microphone')).to_have_attribute('aria-pressed', 'false')
        expect(page.locator('#submit')).to_be_enabled()
        assert page.evaluate('window.__speech[0].stops') == 1
        assert calls == []
        # Only an explicit submit sends the editable transcription to Gemini.
        page.locator('#thoughts').fill('Edited once more before submission.')
        page.locator('#submit').click()
        expect(page.locator('#action-heading')).to_have_text(RESULT['action'])
        assert len(calls) == 1 and calls[0]['thoughts'] == 'Edited once more before submission.'
        page.locator('#complete').click()
        expect(page.locator('#continue')).to_be_visible()
        # Speech edits must not change the task/progression context until submitted.
        page.locator('#microphone').click()
        page.evaluate("window.__emitSpeech([{text: 'An unsent voice edit.'}])")
        expect(page.locator('#continue')).to_be_disabled()
        page.locator('#microphone').click()
        page.locator('#continue').click()
        expect(page.locator('#progress')).to_have_text('1 step completed')
        assert calls[-1]['thoughts'] == 'Edited once more before submission.'
        assert calls[-1]['completed_actions'] == [RESULT['action']]
        # Focus starts and stops dictation; the existing timer remains usable.
        page.locator('#microphone').click()
        page.locator('#start').click()
        expect(page.locator('#microphone')).to_have_attribute('aria-pressed', 'false')
        expect(page.locator('#microphone')).to_be_disabled()
        page.locator('#pause').click()
        expect(page.locator('#pause')).to_have_text('Resume')
        page.locator('#pause').click()
        page.locator('#reset').click()
        expect(page.locator('#microphone')).to_be_enabled()
        # Permission, device, service, and recognition errors preserve typed text.
        for code, text in [('not-allowed', 'permission was denied'), ('audio-capture', 'No microphone'),
                           ('network', 'could not connect'), ('no-speech', 'No speech'),
                           ('service-not-allowed', 'not allowed'), ('language-not-supported', 'language'),
                           ('unknown-error', 'could not finish')]:
            before = page.locator('#thoughts').input_value()
            page.locator('#microphone').click()
            page.evaluate('(code) => window.__speech.at(-1).onerror({error: code})', code)
            expect(page.locator('#voice-status')).to_contain_text(text)
            expect(page.locator('#microphone')).to_have_attribute('aria-pressed', 'false')
            expect(page.locator('#thoughts')).to_have_value(before)
            expect(page.locator('#submit')).to_be_enabled()
        page.evaluate("window.__startError = 'NotAllowedError'")
        page.locator('#microphone').click()
        expect(page.locator('#voice-status')).to_contain_text('permission was denied')
        page.evaluate('window.__startError = null')
        # Starting then stopping before permission resolves must ignore stale callbacks.
        page.evaluate('window.__delayStart = true')
        page.locator('#microphone').click()
        expect(page.locator('#voice-status')).to_contain_text('Starting microphone')
        page.locator('#microphone').click()
        previous = page.locator('#thoughts').input_value()
        page.evaluate("window.__speech.at(-1).onstart(); window.__emitSpeech([{text: 'stale callback'}])")
        expect(page.locator('#thoughts')).to_have_value(previous)
        expect(page.locator('#microphone')).to_have_attribute('aria-pressed', 'false')
        page.evaluate('window.__delayStart = false')
        # A final result delivered by stop is retained without automatic submission.
        before = len(calls)
        page.evaluate("window.__stopResult = 'A final phrase.'")
        page.locator('#microphone').click()
        page.locator('#microphone').click()
        expect(page.locator('#thoughts')).to_have_value(previous + ' A final phrase.')
        assert len(calls) == before
        page.evaluate('window.__stopResult = null')
        # Respect the existing length limit and update its counter.
        page.locator('#thoughts').fill('x' * 1995)
        page.locator('#microphone').click()
        page.evaluate("window.__emitSpeech([{text: 'additional words'}])")
        assert len(page.locator('#thoughts').input_value()) == 2000
        expect(page.locator('#character-count')).to_have_text('2000 / 2000')
        expect(page.locator('#microphone')).to_have_attribute('aria-pressed', 'false')
        # Browser-native end and bounded cancellation restore manual input.
        page.locator('#thoughts').fill('')
        page.locator('#microphone').click()
        page.evaluate('window.__speech.at(-1).onend()')
        expect(page.locator('#submit')).to_be_enabled()
        page.clock.install()
        page.evaluate('window.__delayEnd = true')
        page.locator('#microphone').click()
        page.locator('#microphone').click()
        expect(page.locator('#microphone')).to_have_text('Stopping…')
        page.clock.fast_forward(2100)
        expect(page.locator('#microphone')).to_have_attribute('aria-pressed', 'false')
        expect(page.locator('#submit')).to_be_enabled()
        page.evaluate('window.__delayEnd = false')
        # Fallback language and prefixed implementation work without a new API.
        fallback = browser.new_context()
        fallback.add_init_script(MOCK + "Object.defineProperty(navigator, 'language', {get: () => ''}); Object.defineProperty(navigator, 'languages', {get: () => []}); Object.defineProperty(window, 'webkitSpeechRecognition', {value: window.SpeechRecognition}); Object.defineProperty(window, 'SpeechRecognition', {value: undefined});")
        fallback_page = fallback.new_page()
        fallback_page.goto(URL)
        fallback_page.locator('#microphone').click()
        assert fallback_page.evaluate('window.__speech[0].lang') == 'en-US'
        fallback_page.locator('#microphone').click()
        fallback.close()
        # Unsupported browsers retain full manual-input functionality.
        unsupported = browser.new_context()
        unsupported.add_init_script("Object.defineProperty(window,'SpeechRecognition',{value:undefined}); Object.defineProperty(window,'webkitSpeechRecognition',{value:undefined});")
        unsupported_page = unsupported.new_page()
        unsupported_page.route('**/api/step', lambda route: route.fulfill(json=RESULT))
        unsupported_page.goto(URL)
        expect(unsupported_page.locator('#microphone')).to_be_disabled()
        expect(unsupported_page.locator('#voice-status')).to_contain_text('not supported')
        unsupported_page.locator('#thoughts').fill('Manual input still works.')
        unsupported_page.locator('#submit').click()
        expect(unsupported_page.locator('#action-heading')).to_have_text(RESULT['action'])
        unsupported.close()
        # Use a fresh page without the simulated clock for stable visual capture.
        visual = context.new_page()
        visual.goto(URL)
        visual.locator('#thoughts').fill('A short task, spoken or typed.')
        visual.locator('#microphone').click()
        for width in [320, 390, 1280]:
            visual.set_viewport_size({'width': width, 'height': 1100})
            assert visual.evaluate('document.documentElement.scrollWidth <= innerWidth')
        visual.screenshot(path='/tmp/unstuck-speech-desktop.png', full_page=True)
        visual.set_viewport_size({'width': 390, 'height': 900})
        visual.evaluate('() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)))')
        visual.screenshot(path='/tmp/unstuck-speech-mobile.png', full_page=True)
        visual.locator('#microphone').click()
        assert not errors, errors
        browser.close()
        print('Speech browser checks passed: start/stop, keyboard access, final/editable text, no auto-submit, language/prefix fallback, permission/device/service errors, cancellation, length limit, progression context, timer compatibility, and responsive layouts. Speech engine simulated; real microphone permission/transcription requires manual review.')


if __name__ == '__main__':
    run()
