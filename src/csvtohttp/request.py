import asyncio
import logging
import textwrap
import time

from csvtohttp.parser import build_request


logger = logging.getLogger(__name__)


async def send_request(session, method, url, headers, payload, dry_run=True):
    logger.debug(textwrap.dedent(f"""
      Sending request:
      {method} {url} HTTP/1.1
      {'\n      '.join([f"{k}: {v}" for (k,v) in headers.items()])}
      \t\t
    """).lstrip() + payload)

    if dry_run:
        return None
    else:
        async with session.request(method, url, headers=headers, json=payload) as response:
            text = await response.text()
            if response.status != 200:
                logger.error(f"HTTP call failed with status {response.status}", extra={'response': text})
                raise Exception(f"{response.status} HTTP Status")
            return text


async def build_and_send(session, template, index, rows, extra_data, dry_run=True):
    logger.info(f"[{index}] Request {len(rows)} items, first={rows[0]}")
    start_time = time.time()
    data = {'rows': list(rows)} if len(rows) > 1 else rows[0]
    (method, url, headers, body) = build_request(template, **(data | extra_data))
    response = await send_request(session, method, url, headers, body, dry_run)
    elapsed_time = time.time() - start_time
    if logger.level == logging.DEBUG:
        logger.debug(f"[{index}] Response to took {elapsed_time:.2f} seconds\n{response}")
    else:
        logger.info(f"[{index}] Response to took {elapsed_time:.2f} seconds", extra={'response': response})
