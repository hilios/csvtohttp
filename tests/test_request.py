import pytest
from aiohttp import web
from csvtohttp.request import send_request


value = web.AppKey("value", str)


async def echo(request):
    text = await request.text()
    return web.Response(status=200, body=f'{request.method} {request.url} {text}')


@pytest.fixture
def mock_client(event_loop, aiohttp_client):
    app = web.Application()
    app.router.add_get('/hello', echo)
    app.router.add_post('/hello', echo)
    return event_loop.run_until_complete(aiohttp_client(app))


@pytest.mark.asyncio
async def test_send_request(mock_client):
    result = await send_request(mock_client, 'POST', f'/hello', {}, 'Hello, world', dry_run=False)
    assert result == f'POST {mock_client.make_url('/hello')} Hello, world'


@pytest.mark.asyncio
async def test_send_request_dry_run(mock_client):
    result = await send_request(mock_client, 'POST', '/hello', {}, 'Hello, world', dry_run=True)
    assert result == None
