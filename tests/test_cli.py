import pytest
import textwrap
from csvtohttp.cli import csv_to_http, parse_cli


@pytest.mark.asyncio
async def test_csv_to_http(mock_client):
    results = await csv_to_http(
        mock_client,
        filename='tests/resources/fixtures.csv',
        template='tests/resources/template.hbs',
        run=True,
        batch_size=None,
        filters=['gender=Male'],
        data=['token=123'],
        batch_var='records',
        verbose=True
    )

    (status, response) = results[0]
    url = mock_client.make_url('/hello')
    assert status == 200

    (method, url, payload) = response.split('\t')
    assert method == 'POST'
    assert url == str(mock_client.make_url('/hello'))
    assert payload == '{"message": "Hello, Clayborn!"}'

@pytest.mark.asyncio
async def test_csv_to_http_batch(mock_client):
    results = await csv_to_http(
        mock_client,
        filename='tests/resources/fixtures.csv',
        template='tests/resources/template_batch.hbs',
        run=True,
        batch_size=5,
        filters=['gender=Female'],
        data=['token=123'],
        batch_var='rows',
        verbose=True
    )

    assert len(results) == 2

    (status, response) = results[0]
    url = mock_client.make_url('/hello')
    assert status == 200

    (method, url, payload) = response.split('\t')
    assert method == 'POST'
    assert url == str(mock_client.make_url('/hello'))
    assert payload == textwrap.dedent("""
        {
          "messages": [
            "Hello, Winnifred!",
            "Hello, Essa!",
            "Hello, Bessie!",
            "Hello, Letisha!",
            "Hello, Olimpia!"
          ]
        }
    """).strip()


def test_parse_cli():
    cmd = 'fixtures.csv template.hbs'
    defaults = parse_cli(cmd.split())
    assert defaults.filename == 'fixtures.csv'
    assert defaults.template == 'template.hbs'
    assert defaults.run is False

    verbose = parse_cli(f'{cmd} -v'.split())
    assert verbose.verbose is True

    batched = parse_cli(f'{cmd} -b 5'.split())
    assert batched.batch_size == 5

    filters = parse_cli(f'{cmd} -f foo=bar adc=123'.split())
    assert filters.filters == ['foo=bar', 'adc=123']

    extra_data = parse_cli(f'{cmd} -d foo=bar adc=123'.split())
    assert extra_data.data == ['foo=bar', 'adc=123']

    batch = parse_cli(f'{cmd} --batch-var foo'.split())
    assert batch.batch_var == ['foo']

    batch = parse_cli(f'{cmd} --run'.split())
    assert batch.run is True
