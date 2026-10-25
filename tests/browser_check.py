"""Optional browser check. Uses explicit intercepted AI responses, never a live AI claim.
Run after starting Uvicorn: .venv/bin/python tests/browser_check.py
Requires Playwright and local Google Chrome; not an application dependency.
"""
from playwright.sync_api import sync_playwright, expect

URL = 'http://127.0.0.1:8017'
FIRST = {'acknowledgment': 'That sounds like a lot to hold at once.', 'action': 'Open your nearest-deadline assignment and read the first instruction.', 'recommended_minutes': 6}
SECOND = {'acknowledgment': 'A different starting point is okay.', 'action': 'Clear one small area of your desk for the assignment.', 'recommended_minutes': 5}


def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(channel='chrome', headless=True)
        page = browser.new_page(viewport={'width': 1280, 'height': 1000}, reduced_motion='reduce')
        problems = []
        page.on('pageerror', lambda exc: problems.append(str(exc)))
        page.goto(URL)
        expect(page.get_by_role('heading', name="What's keeping you stuck?")).to_be_visible()
        expect(page.locator('#result')).to_be_hidden()
        page.locator('#submit').click()
        expect(page.locator('#error')).to_contain_text('Tell us a little')
        # Intercept every AI request so this script can never spend real quota.
        page.route('**/api/step', lambda route: route.fulfill(status=503, json={'detail': 'Add your Gemini API key to the local .env file, then restart UNSTUCK.'}))
        page.locator('#thoughts').fill('I have three assignments and do not know where to begin.')
        page.locator('#submit').click()
        expect(page.locator('#error')).to_contain_text('API key')
        expect(page.locator('#thoughts')).to_have_value('I have three assignments and do not know where to begin.')
        page.unroute('**/api/step')
        payloads = []
        counter = 0
        def respond(route):
            nonlocal counter
            payloads.append(route.request.post_data_json)
            counter += 1
            route.fulfill(json=FIRST if counter == 1 else SECOND)
        held = []
        page.route('**/api/step', lambda route: held.append(route))
        page.locator('#submit').click()
        expect(page.locator('#loading')).to_be_visible()
        expect(page.locator('#submit')).to_be_disabled()
        assert len(held) == 1
        respond(held[0])
        expect(page.locator('#action-heading')).to_have_text(FIRST['action'])
        page.unroute('**/api/step')
        page.route('**/api/step', respond)
        expect(page.locator('#duration')).to_have_value('7')
        expect(page.locator('#recommendation')).to_contain_text('6 minutes')
        # Retry preserves original context despite an edited input field.
        page.locator('#thoughts').fill('This edited text is a new thought, not the retry context.')
        page.locator('#retry').click()
        expect(page.locator('#action-heading')).to_have_text(SECOND['action'])
        assert payloads[1]['thoughts'] == payloads[0]['thoughts']
        assert payloads[1]['previous_action'] == FIRST['action']
        page.unroute('**/api/step')
        page.locator('#duration').select_option('6')
        for status in [503, 429]:
            page.route('**/api/step', lambda route: route.fulfill(status=status, json={'detail': 'Please try again later.'}))
            page.locator('#retry').click()
            expect(page.locator('#retry-notice')).to_contain_text('Your previous step is unchanged and ready to use.')
            expect(page.locator('#retry-notice')).to_contain_text('Please try again later.')
            expect(page.locator('#error')).to_be_hidden()
            expect(page.locator('#action-heading')).to_have_text(SECOND['action'])
            expect(page.locator('#acknowledgment')).to_have_text(SECOND['acknowledgment'])
            expect(page.locator('#recommendation')).to_contain_text('5 minutes')
            expect(page.locator('#duration')).to_have_value('6')
            expect(page.locator('#start')).to_be_enabled()
            expect(page.locator('#thoughts')).to_have_value('This edited text is a new thought, not the retry context.')
            assert page.locator('#result #retry-notice').count() == 1
            page.unroute('**/api/step')
        page.screenshot(path='/tmp/unstuck-retry-notice.png', full_page=True)
        page.route('**/api/step', lambda route: route.fulfill(json=FIRST))
        page.locator('#retry').click()
        expect(page.locator('#action-heading')).to_have_text(FIRST['action'])
        expect(page.locator('#retry-notice')).to_be_hidden()
        expect(page.locator('#error')).to_be_hidden()
        page.unroute('**/api/step')
        page.locator('#duration').select_option('7')
        page.route('**/api/step', lambda route: route.fulfill(status=503, json={'detail': 'Please try again later.'}))
        page.clock.install()
        page.locator('#start').click()
        expect(page.locator('#countdown')).to_have_text('07:00')
        expect(page.locator('#retry')).to_be_disabled()
        expect(page.locator('#submit')).to_be_disabled()
        page.clock.fast_forward(30000)
        expect(page.locator('#countdown')).to_have_text('06:30')
        page.locator('#pause').click()
        page.clock.fast_forward(60000)
        expect(page.locator('#countdown')).to_have_text('06:30')
        page.locator('#pause').click()
        page.clock.fast_forward(30000)
        expect(page.locator('#countdown')).to_have_text('06:00')
        page.locator('#reset').click()
        expect(page.locator('#countdown')).to_have_text('07:00')
        expect(page.locator('#retry')).to_be_enabled()
        page.locator('#duration').select_option('5')
        page.locator('#start').click()
        page.clock.fast_forward(300000)
        expect(page.locator('#countdown')).to_have_text('00:00')
        expect(page.locator('#completion')).to_have_text('You did it! Every small step counts.')
        expect(page.locator('#complete')).to_be_enabled()
        # A failed retry after expiry must preserve the result and completion choice.
        page.locator('#retry').click()
        expect(page.locator('#retry-notice')).to_be_visible()
        expect(page.locator('#error')).to_be_hidden()
        expect(page.locator('#countdown')).to_have_text('00:00')
        expect(page.locator('#completion')).to_have_text('You did it! Every small step counts.')
        page.locator('#complete').click()
        expect(page.locator('#completion')).to_have_text('One small step done. That counts.')
        # New generation clears completion and timer; early completion freezes time.
        page.unroute('**/api/step')
        page.route('**/api/step', lambda route: route.fulfill(json=FIRST))
        page.locator('#submit').click()
        expect(page.locator('#completion')).to_be_hidden()
        expect(page.locator('#retry-notice')).to_be_hidden()
        page.locator('#start').click()
        page.clock.fast_forward(5000)
        page.locator('#complete').click()
        snapshot = page.locator('#countdown').inner_text()
        page.clock.fast_forward(100000)
        expect(page.locator('#countdown')).to_have_text(snapshot)
        expect(page.locator('#completion')).to_have_text('One small step done. That counts.')
        expect(page.locator('#progress')).to_have_text('1 step completed')
        expect(page.locator('#continue')).to_be_visible()
        # Continue preserves completed progress on failure and sends full task context.
        task_input = 'This edited text is a new thought, not the retry context.'
        page.locator('#thoughts').fill('An unsent edit must not replace the original task.')
        page.unroute('**/api/step')
        progress_payloads = []
        def fail_continue(route):
            progress_payloads.append(route.request.post_data_json)
            route.fulfill(status=503, json={'detail': 'Gemini is temporarily unavailable.'})
        page.route('**/api/step', fail_continue)
        page.locator('#continue').click()
        expect(page.locator('#retry-notice')).to_contain_text('Your completed steps are kept for this session.')
        expect(page.locator('#continue')).to_be_enabled()
        expect(page.locator('#progress')).to_have_text('1 step completed')
        expect(page.locator('#action-heading')).to_have_text(FIRST['action'])
        expect(page.locator('#completion')).to_have_text('One small step done. That counts.')
        assert progress_payloads[-1] == {'thoughts': task_input, 'previous_action': FIRST['action'],
            'completed_actions': [FIRST['action']], 'mode': 'continue'}
        page.unroute('**/api/step')
        next_step = {**FIRST, 'action': 'Write a rough answer to the first question.'}
        alternate = {**FIRST, 'action': 'List two ideas for answering the first question.'}
        later_step = {**FIRST, 'action': 'Turn your two ideas into a rough answer.'}
        def progress_response(result):
            def respond_progress(route):
                progress_payloads.append(route.request.post_data_json)
                route.fulfill(json=result)
            return respond_progress
        held_progress = []
        page.route('**/api/step', lambda route: held_progress.append(route))
        page.locator('#continue').click()
        expect(page.locator('#continue')).to_be_disabled()
        expect(page.locator('#complete')).to_be_disabled()
        assert len(held_progress) == 1
        progress_response(next_step)(held_progress[0])
        expect(page.locator('#action-heading')).to_have_text(next_step['action'])
        expect(page.locator('#continue')).to_be_hidden()
        expect(page.locator('#completion')).to_be_hidden()
        expect(page.locator('#progress')).to_have_text('1 step completed')
        expect(page.locator('#duration')).to_have_value('7')
        expect(page.locator('#retry-notice')).to_be_hidden()
        page.unroute('**/api/step')
        page.route('**/api/step', progress_response(alternate))
        page.locator('#retry').click()
        expect(page.locator('#action-heading')).to_have_text(alternate['action'])
        assert progress_payloads[-1]['mode'] == 'retry'
        assert progress_payloads[-1]['completed_actions'] == [FIRST['action']]
        assert progress_payloads[-1]['previous_action'] == next_step['action']
        page.locator('#complete').click()
        expect(page.locator('#progress')).to_have_text('2 steps completed')
        # A disabled completion button cannot count the same action twice.
        page.locator('#complete').evaluate('(button) => button.click()')
        expect(page.locator('#progress')).to_have_text('2 steps completed')
        page.unroute('**/api/step')
        page.route('**/api/step', progress_response(later_step))
        page.locator('#continue').click()
        expect(page.locator('#action-heading')).to_have_text(later_step['action'])
        assert progress_payloads[-1]['completed_actions'] == [FIRST['action'], alternate['action']]
        assert progress_payloads[-1]['previous_action'] == alternate['action']
        assert progress_payloads[-1]['thoughts'] == task_input
        page.locator('#complete').click()
        expect(page.locator('#progress')).to_have_text('3 steps completed')
        page.screenshot(path='/tmp/unstuck-progression.png', full_page=True)
        # User/model text is rendered inert, not interpreted as HTML.
        page.unroute('**/api/step')
        markup = '<img src=x onerror="window.bad=true">'
        page.route('**/api/step', lambda route: route.fulfill(json={**FIRST, 'action': markup}))
        page.locator('#submit').click()
        expect(page.locator('#action-heading')).to_have_text(markup)
        expect(page.locator('#progress')).to_have_text('0 steps completed')
        assert page.locator('#action-heading img').count() == 0
        # Keep screenshots outside project source; check all major states fit mobile.
        for width in [320, 390, 1280]:
            page.set_viewport_size({'width': width, 'height': 1000})
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), f'Overflow at {width}px'
        page.unroute('**/api/step')
        page.route('**/api/step', lambda route: route.fulfill(json=FIRST))
        page.locator('#submit').click()
        expect(page.locator('#action-heading')).to_have_text(FIRST['action'])
        page.screenshot(path='/tmp/unstuck-desktop.png', full_page=True)
        page.set_viewport_size({'width': 390, 'height': 844})
        page.screenshot(path='/tmp/unstuck-mobile.png', full_page=True)
        page.reload()
        expect(page.locator('#thoughts')).to_have_value('')
        expect(page.locator('#result')).to_be_hidden()
        page.locator('#thoughts').fill('Start a fresh session.')
        with page.expect_request('**/api/step') as fresh_request:
            page.locator('#submit').click()
        assert fresh_request.value.post_data_json['completed_actions'] == []
        assert fresh_request.value.post_data_json['mode'] == 'suggest'
        expect(page.locator('#progress')).to_have_text('0 steps completed')
        assert not problems, problems
        browser.close()
        print('Browser checks passed: three-step progression, ordered context, failed-Continue recovery, retry continuity, duplicate completion prevention, progress reset, validation/loading, full simulated timer lifecycle, completion before/after expiry, safe rendering, and responsive layout. All browser AI requests intercepted.')


if __name__ == '__main__':
    run()
