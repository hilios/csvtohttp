import asyncio
import logging
import textwrap
import time
import uuid

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

    index = uuid.uuid4()
    start_time = time.time()
    async with session.request(method, url, headers=headers, data=payload) as response:
        text = await response.text()
    elapsed_time = time.time() - start_time

    if logger.level == logging.DEBUG:
        logger.debug(f"[{index}] Response to took {elapsed_time:.2f} seconds\n{response}")
    else:
        logger.info(f"[{index}] Response to took {elapsed_time:.2f} seconds", extra={'response': response})

    if response.status != 200:
        logger.error(f"HTTP call failed with status {response.status}\n{text}", extra={'response': text})
        raise Exception(f"{response.status} HTTP Status")

    return (response.status, text)
