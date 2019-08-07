
#!/usr/bin/env python3

import asyncio

from typing import List

import feedparser

import logging

from dataclasses import dataclass

from datetime import datetime

from time import mktime

logger = logging.getLogger(__name__)

@dataclass
class Feed:
    link: str
    title: str
    timestamp: str
    summary: str

async def parse_feeds(worker_num: int, feed_list: List[str], done_event: asyncio.Event, output_queue: asyncio.Queue):
    last_scraped = None
    while not done_event.is_set():
        for feed in feed_list:
            d = feedparser.parse(feed)
  
            await asyncio.sleep(0.25)
            async for feed in handle_feed_links(d.get('entries'), last_scraped):
                await output_queue.put(feed)
    last_scraped = datetime.utcnow()
    
async def handle_feed_links(entries, last_scraped):
    for entry in entries:
        published_parsed = datetime.fromtimestamp(mktime(entry.get('published_parsed')))
        if last_scraped is not None:
            if last_scraped > published_parsed:
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