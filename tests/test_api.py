"""Provider calls are explicit test doubles; these tests do not prove live access."""
import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock
import httpx
import pytest
from fastapi.testclient import TestClient
from app import ai, main

client = TestClient(main.app)
GOOD = {"acknowledgment": "That is a lot to hold.", "action": "Open the assignment and read the first instruction.", "recommended_minutes": 7, "priority": {"task": "assignments", "basis": "unspecified", "evidence": ""}}


@pytest.mark.parametrize("payload", [{}, {"thoughts": ""}, {"thoughts": "   "}, {"thoughts": "x" * 2001}, {"thoughts": 9}, {"thoughts": "ok", "previous_action": "x" * 501}])
def test_input_validation(payload, monkeypatch):
    mock = AsyncMock()
    monkeypatch.setattr(main, "generate_step", mock)
    assert client.post('/api/step', json=payload).status_code == 422
    mock.assert_not_called()


def test_success_and_retry(monkeypatch):
    mock = AsyncMock(return_value=ai.Step(**GOOD))
    monkeypatch.setattr(main, "generate_step", mock)
    assert client.post('/api/step', json={"thoughts": "  assignments  "}).json() == ai.Step(**GOOD).model_dump()
    mock.assert_awaited_with("assignments", None, [], "suggest", None)
    client.post('/api/step', json={"thoughts": "assignments", "previous_action": GOOD['action']})
    mock.assert_awaited_with("assignments", GOOD['action'], [], "suggest", None)


def test_progression_context_reaches_generator(monkeypatch):
    completed = ['Open the assignment.', 'Read the first question.']
    mock = AsyncMock(return_value=ai.Step(**GOOD))
    monkeypatch.setattr(main, 'generate_step', mock)
    response = client.post('/api/step', json={'thoughts': '  Finish my assignment  ',
        'previous_action': completed[-1], 'completed_actions': completed, 'mode': 'continue'})
    assert response.status_code == 200
    mock.assert_awaited_with('Finish my assignment', completed[-1], completed, 'continue', None)


@pytest.mark.parametrize('extra', [
    {'mode': 'continue'},
    {'mode': 'continue', 'completed_actions': ['Read the question.'], 'previous_action': 'Unrelated context.'},
    {'mode': 'unknown'}, {'completed_actions': [' ']},
    {'completed_actions': ['x' * 501]}, {'completed_actions': ['done'] * 101},
])
def test_invalid_progress_context_does_not_call_gemini(extra, monkeypatch):
    mock = AsyncMock()
    monkeypatch.setattr(main, 'generate_step', mock)
    response = client.post('/api/step', json={'thoughts': 'assignments', **extra})
    assert response.status_code == 422
    mock.assert_not_called()


def test_progression_provider_failure_is_recoverable(monkeypatch):
    mock = AsyncMock(side_effect=ai.GenerationError(503, 'Please try again shortly.'))
    monkeypatch.setattr(main, 'generate_step', mock)
    payload = {'thoughts': 'assignments', 'mode': 'continue',
               'previous_action': 'Open the assignment.', 'completed_actions': ['Open the assignment.']}
    assert client.post('/api/step', json=payload).status_code == 503
    mock.side_effect = None
    mock.return_value = ai.Step(**GOOD)
    assert client.post('/api/step', json=payload).status_code == 200
    assert mock.await_args_list[0] == mock.await_args_list[1]


def test_missing_key(monkeypatch):
    monkeypatch.delenv('GEMINI_API_KEY', raising=False)
    response = client.post('/api/step', json={"thoughts": "assignments"})
    assert response.status_code == 503
    assert '.env' in response.json()['detail']


@pytest.mark.parametrize("status", [429, 502, 503, 504])
def test_error_contract(status, monkeypatch):
    monkeypatch.setattr(main, 'generate_step', AsyncMock(side_effect=ai.GenerationError(status, 'Please try again.')))
    response = client.post('/api/step', json={"thoughts": "assignments"})
    assert response.status_code == status
    assert response.json() == {'detail': 'Please try again.'}


def fake_provider(monkeypatch, text=None, failure=None):
    monkeypatch.setenv('GEMINI_API_KEY', 'test-key-not-a-real-credential')
    call = AsyncMock(return_value=SimpleNamespace(text=text), side_effect=failure)
    class FakeAsyncClient:
        models = SimpleNamespace(generate_content=call)
        async def __aenter__(self): return self
        async def __aexit__(self, *args): return False
    def factory(**kwargs):
        call.client_options = kwargs['http_options']
        return SimpleNamespace(aio=FakeAsyncClient())
    monkeypatch.setattr(ai.genai, 'Client', factory)
    return call


def test_sdk_contract(monkeypatch):
    import json
    call = fake_provider(monkeypatch, json.dumps(GOOD))
    result = asyncio.run(ai.generate_step('assignments', 'Read a different task.'))
    assert result.action == GOOD['action']
    args = call.await_args.kwargs
    assert json.loads(args['contents'])['previous_action'] == 'Read a different task.'
    assert args['config'].response_mime_type == 'application/json'
    assert args['config'].response_schema is ai.OUTPUT_SCHEMA
    assert call.client_options.retry_options.attempts == 2
    assert call.client_options.retry_options.http_status_codes == [503]


def test_gemini_schema_omits_unsupported_additional_properties():
    schema = ai.OUTPUT_SCHEMA.model_dump(exclude_none=True, by_alias=True)
    assert 'additionalProperties' not in schema
    assert 'additional_properties' not in schema
    assert set(schema['required']) == {'acknowledgment', 'action', 'recommended_minutes', 'priority'}
    assert schema['properties']['recommended_minutes']['minimum'] == 5
    # Local validation must still reject unexpected provider fields.
    with pytest.raises(ai.ValidationError):
        ai.Step.model_validate({**GOOD, 'unexpected': 'must be rejected'})


def test_schema_rejection_is_not_masked_as_service_outage(monkeypatch):
    failure = ai.errors.ClientError(400, {'error': {'status': 'INVALID_ARGUMENT', 'message': 'Unknown name additional_properties'}})
    fake_provider(monkeypatch, failure=failure)
    response = client.post('/api/step', json={'thoughts': 'assignments'})
    assert response.status_code == 502
    assert 'configuration' in response.json()['detail']


def test_invalid_key_error_is_actionable_and_sanitized(monkeypatch):
    failure = ai.errors.ClientError(400, {'error': {'message': 'private information', 'details': [{'reason': 'API_KEY_INVALID'}]}})
    fake_provider(monkeypatch, failure=failure)
    response = client.post('/api/step', json={'thoughts': 'assignments'})
    assert response.status_code == 503
    assert 'API key' in response.json()['detail']
    assert 'private information' not in response.text


@pytest.mark.parametrize('text', ['', None, 'not json', '{"action":"missing fields"}', '{"acknowledgment":"x","action":"y","recommended_minutes":20}', '{"acknowledgment":"x","action":"y","recommended_minutes":"7"}'])
def test_invalid_provider_output(monkeypatch, text):
    fake_provider(monkeypatch, text)
    response = client.post('/api/step', json={"thoughts": "assignments"})
    assert response.status_code == 502


def test_identical_retry(monkeypatch):
    import json
    fake_provider(monkeypatch, json.dumps(GOOD))
    response = client.post('/api/step', json={"thoughts": "assignments", "previous_action": GOOD['action'].upper()})
    assert response.status_code == 502


def test_completed_actions_are_sent_in_order_and_not_repeated(monkeypatch):
    import json
    completed = ['Open the assignment.', 'Read the first instruction.']
    call = fake_provider(monkeypatch, json.dumps({**GOOD, 'action': 'Write a rough answer to the first question.'}))
    asyncio.run(ai.generate_step('assignments', completed[-1], completed, 'continue'))
    content = json.loads(call.await_args.kwargs['contents'])
    assert content == {'thoughts': 'assignments', 'previous_action': completed[-1],
                       'completed_actions': completed, 'mode': 'continue', 'priority_context': None}
    assert 'next logical small action' in call.await_args.kwargs['config'].system_instruction
    call.return_value = SimpleNamespace(text=json.dumps({**GOOD, 'action': ' OPEN   THE ASSIGNMENT! '}))
    with pytest.raises(ai.GenerationError) as caught:
        asyncio.run(ai.generate_step('assignments', completed[-1], completed, 'continue'))
    assert caught.value.status == 502
    assert 'completed step' in caught.value.message


@pytest.mark.parametrize('failure,status', [(TimeoutError('private information'), 504), (httpx.ReadTimeout('private information'), 504), (httpx.ConnectError('private information'), 503), (ai.errors.ClientError(429, {'error': {'message': 'private information'}}), 429), (ai.errors.ClientError(403, {'error': {'message': 'private information'}}), 503), (ai.errors.ServerError(504, {'error': {'message': 'private information'}}), 504)])
def test_sanitized_provider_failures(monkeypatch, failure, status):
    fake_provider(monkeypatch, failure=failure)
    response = client.post('/api/step', json={"thoughts": "assignments"})
    assert response.status_code == status
    assert 'private information' not in response.text


def test_sdk_configuration_compatible():
    # Validate installed SDK options without making an external request.
    options = ai.types.HttpOptions(timeout=30000, retry_options=ai.types.HttpRetryOptions(attempts=1))
    assert options.timeout == 30000
    assert options.retry_options.attempts == 1


@pytest.mark.parametrize('path', ['/.env', '/static/../.env', '/static/%2e%2e/.env', '/devpost/learner-profile.md', '/app/ai.py', '/.git/config'])
def test_private_files_not_served(path):
    assert client.get(path).status_code == 404


def test_page_and_assets():
    page = client.get('/')
    assert page.status_code == 200
    assert "What's keeping" in page.text
    for name in ['app.js', 'timer.js', 'speech.js', 'styles.css']:
        assert client.get('/static/' + name).status_code == 200


@pytest.mark.parametrize('basis,evidence', [
    ('deadline', 'essay due tomorrow'), ('urgency', 'urgent application'),
    ('importance', 'exam counts for most of my grade'), ('dependency', 'notes before drafting'),
])
def test_priority_factors_use_stated_evidence(basis, evidence, monkeypatch):
    import json
    thoughts = f'Finish my assignment: {evidence}; other tasks can wait.'
    raw = {**GOOD, 'priority': {'task': 'assignment', 'basis': basis, 'evidence': evidence},
           'priority_reason': 'Invented deadline next Friday!'}
    fake_provider(monkeypatch, json.dumps(raw))
    result = asyncio.run(ai.generate_step(thoughts, None))
    assert evidence in result.priority_reason
    assert 'next Friday' not in result.priority_reason
    assert result.action == GOOD['action']


def test_missing_ranking_information_uses_neutral_explanation(monkeypatch):
    import json
    raw = {**GOOD, 'priority': {'task': 'tidy my desk', 'basis': 'unspecified', 'evidence': ''}}
    fake_provider(monkeypatch, json.dumps(raw))
    result = asyncio.run(ai.generate_step('I want to tidy my desk and sort my books.', None))
    assert result.priority_reason == 'A manageable starting point; no unstated deadline or urgency is assumed.'
    assert 'Never invent deadlines' in ai.SYSTEM
    assert 'Respect negation' in ai.SYSTEM
    assert 'basis MUST be unspecified' in ai.SYSTEM


@pytest.mark.parametrize('priority', [
    {'task': 'essay', 'basis': 'deadline', 'evidence': 'due Friday'},
    {'task': 'urgent essay due Friday', 'basis': 'unspecified', 'evidence': ''},
    {'task': 'essay', 'basis': 'urgency', 'evidence': ''},
    {'task': 'essay', 'basis': 'unspecified', 'evidence': 'due tomorrow'},
])
def test_unsupported_or_invented_priority_is_rejected(priority, monkeypatch):
    import json
    fake_provider(monkeypatch, json.dumps({**GOOD, 'priority': priority}))
    response = client.post('/api/step', json={'thoughts': 'My essay is due tomorrow. Laundry has no deadline.'})
    assert response.status_code == 502


def test_priority_context_continues_and_can_be_reassessed(monkeypatch):
    import json
    thoughts = 'Essay due tomorrow. Laundry after submitting the essay.'
    context = ai.PriorityContext(task='Essay', basis='deadline', evidence='due tomorrow')
    completed = ['Submit the completed essay.']
    raw = {**GOOD, 'action': 'Gather one load of laundry.',
           'priority': {'task': 'Laundry', 'basis': 'dependency', 'evidence': 'Laundry after submitting the essay'}}
    call = fake_provider(monkeypatch, json.dumps(raw))
    response = client.post('/api/step', json={'thoughts': thoughts, 'mode': 'continue',
        'previous_action': completed[-1], 'completed_actions': completed, 'priority_context': context.model_dump()})
    assert response.status_code == 200
    assert response.json()['priority']['task'] == 'Laundry'
    sent = json.loads(call.await_args.kwargs['contents'])
    assert sent['priority_context'] == context.model_dump()
    assert sent['completed_actions'] == completed and sent['thoughts'] == thoughts
    assert 'One small completed action does not mean the whole task is done' in ai.SYSTEM


@pytest.mark.parametrize('context', [
    {'task': 'invented task', 'basis': 'unspecified', 'evidence': ''},
    {'task': 'essay', 'basis': 'deadline', 'evidence': 'due Friday'},
])
def test_unstated_incoming_priority_context_is_invalid(context, monkeypatch):
    mock = AsyncMock()
    monkeypatch.setattr(main, 'generate_step', mock)
    response = client.post('/api/step', json={'thoughts': 'Essay due tomorrow.',
        'priority_context': context, 'mode': 'retry', 'previous_action': 'Read the essay prompt.'})
    assert response.status_code == 422
    mock.assert_not_called()


@pytest.mark.parametrize('basis,evidence', [('deadline', 'no deadline'), ('urgency', 'not urgent'),
                                         ('urgency', 'can wait'), ('importance', 'not important')])
def test_negated_priority_factor_is_not_treated_as_positive(basis, evidence, monkeypatch):
    import json
    fake_provider(monkeypatch, json.dumps({**GOOD, 'priority': {'task': 'notes', 'basis': basis, 'evidence': evidence}}))
    response = client.post('/api/step', json={'thoughts': f'Read my notes; {evidence}.'})
    assert response.status_code == 502
