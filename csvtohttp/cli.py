#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import aiohttp
import aiofiles
import argparse
import asyncio
import logging
import textwrap
import sys

from csvtohttp import HEADER
from csvtohttp.parser import stream_csv, build_request
from csvtohttp.request import send_request


logger = logging.getLogger(__name__)


async def csv_to_http(session, filename, template, run, batch_size, matches, data, verbose, **kwargs):
    logging.basicConfig(
        encoding='utf-8',
        level=logging.DEBUG if verbose else logging.INFO,
        format='%(asctime)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')

    dry_run = not run
    filters = {key: value for kv in matches for key, value in [kv.split('=', 1)]}
    extra_data = {key: value for kv in data for key, value in [kv.split('=', 1)]}
    logger.info(textwrap.dedent(
        f"""
        {textwrap.indent(HEADER, "        ")}
        Filename: {filename}
        Template: {template}
        Dry run: {'Y' if dry_run else 'N'}
        Batch Size: {batch_size}
        Filters: {', '.join([f"{k} = {v}" for k, v in filters.items()])}
        Data: {', '.join([f"{k} = {v}" for k, v in extra_data.items()])}
        ---
        """))

    tasks = []
    async with aiofiles.open(template, mode='r') as file:
        template = await file.read()
    filter_data = {'_filters': filters}

    async for record in stream_csv(filename, patterns=filters, batch_size=batch_size):
        # if record is a list then the values are batched
        data = {kwargs['batch_var']: data} if isinstance(record, list) else record
        (method, url, headers, body) = build_request(template, **(data | extra_data | filter_data))

        task = asyncio.create_task(send_request(session, method, url, headers, body, dry_run))
        tasks.append(task)

    return await asyncio.gather(*tasks)


async def run_cli(args):
    async with aiohttp.ClientSession() as session:
        await csv_to_http(session, **vars(args))


def parse_cli(args):
    parser = argparse.ArgumentParser(description='Executes HTTP requests from a CSV file using a template.')
    parser.add_argument('filename', help='CSV file path.')
    parser.add_argument('template', help='Handlebars template file path for HTTP requests.')
    parser.add_argument(
        '-f', '--filter', type=str, nargs='*', default=[],
        help='Column filters (name=value) with wildcard "*" support. Multiple filters allowed.')
    parser.add_argument(
        '-d', '--data', type=str, nargs='*', default=[],
        help='Data for the template (key=value). Multiple entries allowed.')
    parser.add_argument(
        '-b', '--batch-size', type=int, default=None,
        help='Number of CSV records per request.')
    parser.add_argument(
        '-v', '--verbose', action='store_true',
        help='Enables verbose output.')
    parser.add_argument(
        '--batch-var', type=str, nargs=1, default='records',
        help='The variable name in the template')
    parser.add_argument(
        '--run', action='store_true',
        help='Executes the requests.')
    return parser.parse_args(args)


def main():
    try:
        args = parse_cli(sys.argv)
        asyncio.run(run_cli(args))
        sys.exit(0)

    except Exception as e:
        import traceback
        logger.error(f'Command failed with message {e}')
        traceback.print_exc()

        sys.exit(1)
