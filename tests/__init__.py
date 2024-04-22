import pytest
from aiohttp import web


async def echo(request):
    text = await request.text()
    return web.Response(status=200, body=f'{request.method} {request.url} {text}')


@pytest.fixture
def mock_client(event_loop, aiohttp_client):
    app = web.Application()
    app.router.add_get('/hello', echo)
    app.router.add_post('/hello', echo)
    return event_loop.run_until_complete(aiohttp_client(app))
