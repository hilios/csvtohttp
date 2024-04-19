import asyncio
import pybars
import csv
import itertools
import json
import logging
import os
import re
import textwrap
import time
import yaml

from csvtohttp import TEMPLATE_HELPERS
from fnmatch import fnmatch


TEMPLATE_PATTERN = re.compile(r'(---)?(?P<metadata>.*?)---\n(?P<body>.*)', re.DOTALL)


async def stream_csv(filename, filters=[], batch_size=50_000):
    """Generator function to yield batches of rows from a CSV file."""
    # Check if a given row matches all the criteria.
    matches_criteria = lambda row: all(fnmatch(row[key], pattern) for key, pattern in filters.items())
    def _read_in_batches():
        with open(filename, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            data = [row for row in reader if matches_criteria(row)]
            return itertools.batched(data, batch_size)

    batched = await asyncio.to_thread(_read_in_batches)
    for batch in batched:
        yield batch


async def read_file(filename):
    def _open_and_read():
        with open(filename, 'r', encoding='utf-8') as file:
            return file.read()

    return await asyncio.to_thread(_open_and_read)


def build_request(source, **data):
    """Build the http request using a mustache template

    >>> build_request("test.mustache", token=123, message="Hello, World!")
    ('POST', 'https://localhost', {'Authorization': 'Bearer 123'}, '{"message": "Hello, World!"}')
    """
    template = pybars.Compiler().compile(source)
    template = template(data, helpers = TEMPLATE_HELPERS)
    # Render the template with the provided data
    bits = TEMPLATE_PATTERN.search(template)
    body = bits.group('body').strip()
    metadata = yaml.safe_load(bits.group('metadata'))
    url = metadata['url']
    method = metadata['method']
    headers = metadata['headers']

    return (method, url, headers, body)
