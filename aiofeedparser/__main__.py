#!/usr/bin/env python3

import argparse
import sys
import asyncio
import os

from dataclasses import dataclass
from typing import List

from .feed_worker import parse_feed
from .output import PrintOutput

@dataclass
class Config:
    feeds: List[str]

async def async_main(config: Config):
    done_event = asyncio.Event()
    outbound_queue = PrintOutput()
    
    feed_list = config.feeds

    loop = asyncio.get_event_loop()

    output_handler = loop.create_task(handle_output(outbound_queue, done_event))

    workers = [
        parse_feed(f, done_event, outbound_queue) for i, f in enumerate(feed_list)
        ]

    await asyncio.gather(*workers+[output_handler])


async def handle_output(outbound_queue: asyncio.Queue, done_event: asyncio.Event):
    while not done_event.is_set():
        doc = await outbound_queue.get()
        print(doc)


def main(args):
    """
    Main method for feedparser, takes arguments and parses them and calls async_main method
    """
    parser = argparse.ArgumentParser()

    parser.add_argument('-f', '--feeds', help='list of feed links', required=True)

    parsed_args = parser.parse_args(args)

    config = Config(
        feeds=parsed_args.feeds.split(',')
    )

  
    loop = asyncio.get_event_loop()
    asyncio.run(async_main(config))

    return os.EX_OK

if __name__ == '__main__':
    args = sys.argv[1:]
    sys.exit(main(args))

