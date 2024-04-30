import pytest
from csvtohttp.request import send_request


@pytest.mark.asyncio
async def test_send_request(mock_client):
    (status, response) = await send_request(mock_client, 'POST', '/hello', {}, 'Hello, world', dry_run=False)
    assert status == 200
    (method, url, payload) = response.split('\t')
    assert method == 'POST'
    assert url == str(mock_client.make_url('/hello'))
    assert payload == 'Hello, world'


@pytest.mark.asyncio
async def test_send_request_dry_run(mock_client):
    result = await send_request(mock_client, 'POST', '/hello', {}, 'Hello, world', dry_run=True)
    assert result is None
