import aiocsv
import aiofiles
import pybars
import re
import yaml

from csvtohttp import TEMPLATE_HELPERS
from fnmatch import fnmatch


TEMPLATE_PATTERN = re.compile(r'(---)?(?P<metadata>.*?)---\n(?P<body>.*)', re.DOTALL)


async def stream_csv(filename, filters={}, batch_size=None):
    """Generator function to yield batches of rows from a CSV file."""
    async with aiofiles.open(filename, mode='r', newline='', encoding='utf-8') as csvfile:
        batch = []
        async for record in aiocsv.AsyncDictReader(csvfile):
            predicates = all(fnmatch(record[key], pattern) for key, pattern in filters.items())

            if predicates is True:
                if batch_size is None:
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
    template = template(data, helpers=TEMPLATE_HELPERS)
    # Render the template with the provided data
    bits = TEMPLATE_PATTERN.search(template)
    body = bits.group('body').strip()
    metadata = yaml.safe_load(bits.group('metadata'))
    url = metadata['url']
    method = metadata['method']
    headers = metadata['headers']

    return (method, url, headers, body)
