import asyncio
import pytest
import sys
from . import mock_client
from csvtohttp.cli import csv_to_http, parse_cli, main


@pytest.mark.asyncio
async def test_csv_to_http(mock_client):
    results = await csv_to_http(
        mock_client,
        filename='tests/resources/fixtures.csv',
        template='tests/resources/template.hbs',
        run=True,
        batch_size=None,
        matches=['gender=Male'],
        data=['token=123'],
        batch_var='records',
        verbose=True
    )

    (status, response) = results[0]
    url = mock_client.make_url('/hello')
    assert status == 200
    assert response == f'POST {url} {{"message": "Hello, Clayborn!"}}'


def test_parse_cli():
    cmd = 'fixtures.csv template.hbs'
    defaults = parse_cli(cmd.split())
    assert defaults.filename == 'fixtures.csv'
    assert defaults.template == 'template.hbs'
    assert defaults.run == False

    verbose = parse_cli(f'{cmd} -v'.split())
    assert verbose.verbose == True

    batched = parse_cli(f'{cmd} -b 5'.split())
    assert batched.batch_size == 5

    filters = parse_cli(f'{cmd} -f foo=bar adc=123'.split())
    assert filters.filter == ['foo=bar', 'adc=123']

    extra_data = parse_cli(f'{cmd} -d foo=bar adc=123'.split())
    assert extra_data.data == ['foo=bar', 'adc=123']

    batch = parse_cli(f'{cmd} --batch-var foo'.split())
    assert batch.batch_var == ['foo']

    batch = parse_cli(f'{cmd} --run'.split())
    assert batch.run == True
