import pytest
import textwrap
from collections import deque

from csvtohttp.parser import stream_csv, read_file, build_request


@pytest.mark.asyncio
async def test_stream_csv():
    value = await anext(stream_csv("tests/fixture.csv"))
    assert value['first_name'] == 'Clayborn'


@pytest.mark.asyncio
async def test_read_file():
    value = await read_file('tests/template.hbs')
    assert value.strip() == 'Lorem ipsum dolor sit amet'


def test_build_request():
    source = textwrap.dedent("""
    ---
    method: POST
    url: https://localhost
    headers:
        Authorization: "Bearer {{token}}"
    ---
    {"message": "{{message}}"}
    """).lstrip()
    (method, url, headers, payload) = build_request(source, message='Lorem ipsum', token='1a2b3c')
    assert method == 'POST'
    assert url == 'https://localhost'
    assert headers == {'Authorization': 'Bearer 1a2b3c'}
    assert payload == '{"message": "Lorem ipsum"}'
