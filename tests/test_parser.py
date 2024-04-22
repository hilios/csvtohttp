import pytest
import textwrap
from collections import deque

from csvtohttp.parser import stream_csv, build_request


@pytest.mark.asyncio
async def test_stream_csv():
    results = []
    async for row in stream_csv("tests/fixture.csv"):
        results.append(row)
    assert len(results) == 10
    assert results[0]['first_name'] == 'Clayborn'


@pytest.mark.asyncio
async def test_stream_csv_batched():
    results = []
    async for rows in stream_csv("tests/fixture.csv", batch_size=7):
        results.append(rows)
    assert len(results) == 2
    assert len(results[0]) == 7
    assert len(results[1]) == 3


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
