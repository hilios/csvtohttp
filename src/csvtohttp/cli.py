#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import aiohttp
import argparse
import asyncio
import csv
import itertools
import json
import logging
import os
import re
import textwrap
import sys

from csvtohttp import HEADER
from csvtohttp.parser import stream_csv, read_file
from csvtohttp.request import build_and_send


logger = logging.getLogger(__name__)


async def csv_to_http(session, filename, template, run, batch_size, filter, data, **kwargs):
    dry_run = not run
    filters = {key: value for kv in filter for key, value in [kv.split('=', 1)]}
    extra_data = {key: value for kv in data for key, value in [kv.split('=', 1)]}
    logger.debug(textwrap.dedent(f"""
        {textwrap.indent(HEADER, "        ")}
        Filename: {filename}
        Template: {template}
        Dry run: {'Y' if dry_run else 'N'}
        Batch Size: {batch_size}
        Filters: {', '.join([f"{k} = {v}" for k, v in filters.items()])}
        Data: {', '.join([f"{k} = {v}" for k, v in extra_data.items()])}
        ---
    """))
    i = 0
    tasks = []
    template = await read_file(template)
    filter_data = {'_filters': filters}
    async for rows in stream_csv(filename, filters=filters, batch_size=batch_size):
        i += 1
        task = asyncio.create_task(
          build_and_send(session, template, i, rows, extra_data | filter_data, dry_run=dry_run)
        )
        tasks.append(task)

    await asyncio.gather(*tasks)


async def run_cli(args):
  async with aiohttp.ClientSession() as session:
      await csv_to_http(session, **vars(args))


def main():
    parser = argparse.ArgumentParser(description=f'Executes HTTP requests from a CSV file using a template.')
    parser.add_argument('filename', help='CSV file path.')
    parser.add_argument('template', help='Handlebars template file path for HTTP requests.')
    parser.add_argument('-f', '--filter', type=str, nargs='*', default=[],
        help='Column filters (name=value) with wildcard "*" support. Multiple filters allowed.')
    parser.add_argument('-d', '--data', type=str, nargs='*', default=[],
        help='Data for the template (key=value). Multiple entries allowed.')
    parser.add_argument('-b', '--batch-size', type=int, default=1,
        help='Number of CSV records per request.')
    parser.add_argument('-v', '--verbose', action='store_true',
        help='Enables verbose output.')
    parser.add_argument('--run', action='store_true',
        help='Executes the requests.')
    args = parser.parse_args()

    logging.basicConfig(encoding='utf-8', level=logging.DEBUG if args.verbose else logging.INFO,
        format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    try:
      asyncio.run(run_cli(args))
      sys.exit(0)

    except Exception as e:
      import traceback
      logger.error(f'Command failed with message {e}:\n{traceback.format_exc()}')
      sys.exit(1)



if __name__ == "__main__":
    main()
