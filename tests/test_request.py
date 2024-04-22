import pytest
from csvtohttp.request import send_request


@pytest.mark.asyncio
async def test_send_request(mock_client):
    (status, result) = await send_request(mock_client, 'POST', '/hello', {}, 'Hello, world', dry_run=False)
    assert status == 200
    assert result == f'POST {mock_client.make_url('/hello')} Hello, world'


@pytest.mark.asyncio
async def test_send_request_dry_run(mock_client):
    result = await send_request(mock_client, 'POST', '/hello', {}, 'Hello, world', dry_run=True)
    assert result is None
