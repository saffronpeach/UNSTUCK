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
        # User/model text is rendered inert, not interpreted as HTML.
        page.unroute('**/api/step')
        markup = '<img src=x onerror="window.bad=true">'
        page.route('**/api/step', lambda route: route.fulfill(json={**FIRST, 'action': markup}))
        page.locator('#submit').click()
        expect(page.locator('#action-heading')).to_have_text(markup)
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
        assert not problems, problems
        browser.close()
        print('Browser checks passed: validation, intercepted configuration error/generation/retry, loading, preserved context/error state, full simulated timer session, early completion, safe rendering, refresh reset, and 320/390/1280px layout. No live Gemini call performed.')


if __name__ == '__main__':
    run()
