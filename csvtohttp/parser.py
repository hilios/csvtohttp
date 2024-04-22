import aiocsv
import aiofiles
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

async def stream_csv(filename, patterns={}, batch_size=1):
    """Generator function to yield batches of rows from a CSV file."""
    # Check if a given row matches all the criteria.
    predicate = lambda row: all(fnmatch(row[key], pattern) for key, pattern in patterns.items())

    async with aiofiles.open(filename, mode='r', newline='', encoding='utf-8') as csvfile:
        batch = []
        async for record in aiocsv.AsyncDictReader(csvfile):
            if predicate(record):
                if batch_size == 1:
                    yield record
                else:
                    batch.append(record)

                if len(batch) == batch_size:
                    yield batch[:]
                    batch = []

        if len(batch) > 0:
            yield batch


def build_request(source, **data):
    """Build the http request using a handlebars template"""
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
