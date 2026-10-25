"""Priority UI/context regression; all AI responses are explicitly simulated."""
from playwright.sync_api import sync_playwright, expect

URL = 'http://127.0.0.1:8017'
THOUGHTS = 'Essay due tomorrow and ready to submit. Laundry after submitting the essay.'
FIRST = {'acknowledgment': 'One small step is enough.', 'action': 'Read the essay prompt.',
         'recommended_minutes': 7, 'priority': {'task': 'Essay', 'basis': 'deadline', 'evidence': 'due tomorrow'},
         'priority_reason': 'Stated deadline: “due tomorrow”'}
NEXT = {**FIRST, 'action': 'Submit the completed essay.'}
REASSESSED = {**FIRST, 'action': 'Gather one load of laundry.',
    'priority': {'task': 'Laundry', 'basis': 'dependency', 'evidence': 'Laundry after submitting the essay'},
    'priority_reason': 'Stated dependency: “Laundry after submitting the essay”'}


def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(channel='chrome', headless=True)
        page = browser.new_page(viewport={'width': 1280, 'height': 1100}, reduced_motion='reduce')
        errors, requests = [], []
        page.on('pageerror', lambda error: errors.append(str(error)))
        def respond(data, status=200):
            def handler(route):
                requests.append(route.request.post_data_json)
                route.fulfill(status=status, json=data)
            return handler
        page.route('**/api/step', respond(FIRST))
        page.goto(URL)
        page.locator('#thoughts').fill(THOUGHTS)
        page.locator('#submit').click()
        expect(page.get_by_text('Your priority right now', exact=True)).to_be_visible()
        expect(page.locator('#priority-task')).to_have_text('Essay')
        expect(page.locator('#priority-reason')).to_have_text(FIRST['priority_reason'])
        expect(page.locator('#action-heading')).to_have_text(FIRST['action'])
        assert requests[-1]['priority_context'] is None
        page.locator('#complete').click()
        page.locator('#thoughts').fill('Unsubmitted changes must not affect the original task.')
        page.unroute('**/api/step')
        page.route('**/api/step', respond({'detail': 'Gemini is temporarily unavailable.'}, 503))
        page.locator('#continue').click()
        expect(page.locator('#retry-notice')).to_be_visible()
        expect(page.locator('#priority-task')).to_have_text('Essay')
        expect(page.locator('#priority-reason')).to_have_text(FIRST['priority_reason'])
        expect(page.locator('#action-heading')).to_have_text(FIRST['action'])
        expect(page.locator('#progress')).to_have_text('1 step completed')
        expect(page.locator('#continue')).to_be_enabled()
        failed_context = requests[-1]
        page.unroute('**/api/step')
        page.route('**/api/step', respond(NEXT))
        page.locator('#continue').click()
        expect(page.locator('#action-heading')).to_have_text(NEXT['action'])
        assert requests[-1] == failed_context
        assert requests[-1]['priority_context'] == FIRST['priority']
        assert requests[-1]['thoughts'] == THOUGHTS
        assert requests[-1]['completed_actions'] == [FIRST['action']]
        page.locator('#complete').click()
        page.unroute('**/api/step')
        page.route('**/api/step', respond(REASSESSED))
        page.locator('#continue').click()
        expect(page.locator('#priority-task')).to_have_text('Laundry')
        expect(page.locator('#priority-reason')).to_have_text(REASSESSED['priority_reason'])
        assert requests[-1]['priority_context'] == NEXT['priority']
        assert requests[-1]['completed_actions'] == [FIRST['action'], NEXT['action']]
        page.locator('#retry').click()
        assert requests[-1]['priority_context'] == REASSESSED['priority']
        assert requests[-1]['mode'] == 'retry'
        # A new task discards priority/progress only when a valid response succeeds.
        neutral = {**FIRST, 'priority': {'task': 'tidy my desk', 'basis': 'unspecified', 'evidence': ''},
            'priority_reason': 'A manageable starting point; no unstated deadline or urgency is assumed.',
            'action': 'Move one item off your desk.'}
        page.unroute('**/api/step')
        page.route('**/api/step', respond(neutral))
        page.locator('#thoughts').fill('I want to tidy my desk and sort my books.')
        page.locator('#submit').click()
        expect(page.locator('#priority-reason')).to_have_text(neutral['priority_reason'])
        expect(page.locator('#progress')).to_have_text('0 steps completed')
        assert requests[-1]['priority_context'] is None and requests[-1]['completed_actions'] == []
        # Model strings remain inert text, including the new priority fields.
        page.unroute('**/api/step')
        markup = '<img src=x onerror="window.bad=true">'
        page.route('**/api/step', respond({**neutral, 'priority': {**neutral['priority'], 'task': markup}, 'priority_reason': markup}))
        page.locator('#submit').click()
        expect(page.locator('#priority-task')).to_have_text(markup)
        assert page.locator('#priority-task img, #priority-reason img').count() == 0
        page.unroute('**/api/step')
        page.route('**/api/step', respond(FIRST))
        page.locator('#thoughts').fill(THOUGHTS)
        page.locator('#submit').click()
        expect(page.locator('#priority-task')).to_have_text('Essay')
        for width in [320, 390, 1280]:
            page.set_viewport_size({'width': width, 'height': 1100})
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        page.evaluate('window.scrollTo(0, 0)')
        page.evaluate('() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)))')
        page.screenshot(path='/tmp/unstuck-priority-desktop.png', full_page=True)
        page.set_viewport_size({'width': 390, 'height': 1000})
        page.evaluate('window.scrollTo(0, 0)')
        page.evaluate('() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)))')
        page.screenshot(path='/tmp/unstuck-priority-mobile.png', full_page=True)
        assert not errors, errors
        browser.close()
        print('Priority browser checks passed: priority/reason display, one action, continuation/retry context, reassessment rendering, failure preservation, new-task reset, safe text rendering and responsive layout. AI responses simulated.')


if __name__ == '__main__':
    run()
