import pytest
import textwrap
from collections import deque
from csvtohttp.parser import stream_csv, build_request


@pytest.mark.asyncio
async def test_stream_csv():
    results = []
    async for row in stream_csv("tests/resources/fixtures.csv"):
        results.append(row)
    assert len(results) == 10
    assert results[0]['first_name'] == 'Clayborn'


@pytest.mark.asyncio
async def test_stream_csv_batched():
    results = []
    async for rows in stream_csv("tests/resources/fixtures.csv", batch_size=7):
        results.append(rows)
    assert len(results) == 2
    assert len(results[0]) == 7
    assert len(results[1]) == 3


@pytest.mark.asyncio
async def test_stream_csv_filter():
    results = []
    async for rows in stream_csv("tests/resources/fixtures.csv", patterns={'gender': '*queer'}):
        results.append(rows)
    assert len(results) == 1
    assert results[0]['first_name'] == 'Hermine'


def test_build_request():
    with open('tests/resources/template.hbs', mode='r') as file:
        (method, url, headers, payload) = build_request(file.read(), first_name='John Doe', token='1a2b3c')
        assert method == 'POST'
        assert url == '/hello'
        assert headers == {'Authorization': 'Bearer 1a2b3c'}
        assert payload == '{"message": "Hello, John Doe!"}'
