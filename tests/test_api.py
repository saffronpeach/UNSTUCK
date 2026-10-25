"""Provider calls are explicit test doubles; these tests do not prove live access."""
import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock
import httpx
import pytest
from fastapi.testclient import TestClient
from app import ai, main

client = TestClient(main.app)
GOOD = {"acknowledgment": "That is a lot to hold.", "action": "Open the assignment and read the first instruction.", "recommended_minutes": 7}


@pytest.mark.parametrize("payload", [{}, {"thoughts": ""}, {"thoughts": "   "}, {"thoughts": "x" * 2001}, {"thoughts": 9}, {"thoughts": "ok", "previous_action": "x" * 501}])
def test_input_validation(payload, monkeypatch):
    mock = AsyncMock()
    monkeypatch.setattr(main, "generate_step", mock)
    assert client.post('/api/step', json=payload).status_code == 422
    mock.assert_not_called()


def test_success_and_retry(monkeypatch):
    mock = AsyncMock(return_value=ai.Step(**GOOD))
    monkeypatch.setattr(main, "generate_step", mock)
    assert client.post('/api/step', json={"thoughts": "  assignments  "}).json() == GOOD
    mock.assert_awaited_with("assignments", None)
    client.post('/api/step', json={"thoughts": "assignments", "previous_action": GOOD['action']})
    mock.assert_awaited_with("assignments", GOOD['action'])


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
    assert set(schema['required']) == {'acknowledgment', 'action', 'recommended_minutes'}
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
    for name in ['app.js', 'timer.js', 'styles.css']:
        assert client.get('/static/' + name).status_code == 200
