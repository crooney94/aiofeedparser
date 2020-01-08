
#!/usr/bin/env python3

import asyncio
import logging
import aiohttp
import feedparser

from typing import List
from dataclasses import dataclass
from datetime import datetime
from time import mktime
from contextlib import asynccontextmanager

from .errors import RequestError

logger = logging.getLogger(__name__)


@dataclass
class Feed:
    link: str
    title: str
    timestamp: str
    summary: str


async def parse_feed(feed_url, done_event: asyncio.Event, output_queue: asyncio.Queue):
    last_scraped = None
    backoff = 1
    sequence_id = None

    while not done_event.is_set():
        raw_feed = None
        try:
            async with safely_fetch():
                raw_feed = await fetch(feed_url)

        except RequestError as e:
            logger.error('failed trying to get response for feed url %s', feed_url)
            logger.exception(e)

        if raw_feed:

            parsed_feed = feedparser.parse(raw_feed)

            if parsed_feed:
                output_count = 0

                async for feed_obj in handle_feed_links(parsed_feed.get('entries'), sequence_id):
                    if feed_obj:
                        if not sequence_id:
                            sequence_id = feed_obj.timestamp
                        elif feed_obj.timestamp > sequence_id:
                            sequence_id = feed_obj.timestamp
                    
                        await output_queue.put(feed_obj)
                        output_count += 1
                
                if not output_count:
                    backoff *= 2
                    logger.warning('No new entries for url %s, sleeping for %d', feed_url, backoff)
                    await asyncio.sleep(backoff)
                else:
                    backoff = 1

        else:
            backoff *= 2
            logger.warning('failed to get response for url %s, sleeping for %d', feed_url, backoff)
            await asyncio.sleep(backoff)
    
async def handle_feed_links(entries, sequence_id):
    for entry in entries:
        published_parsed = datetime.fromtimestamp(mktime(entry.get('published_parsed')))

        if sequence_id and sequence_id >= published_parsed:
            continue
        else:

            link = entry.get('url')
            title = entry.get('title')
            summary = entry.get('summary')

            feed = Feed(link=link,
                        title=title,
                        timestamp=published_parsed,
                        summary=summary
            )

            yield feed

@asynccontextmanager
async def safely_fetch():
    try:
        yield 

    except Exception as e:
        raise RequestError(e)


async def fetch(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, timeout=10.0) as response: 
            return await response.text()