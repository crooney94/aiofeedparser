
#!/usr/bin/env python3

import argparse

from dataclasses import dataclass

from typing import List

import sys

import asyncio

import os

from .feed_worker import parse_feeds

@dataclass
class Config:
    num_of_workers: int
    feeds: List[str]

async def async_main(config: Config):
    breakpoint()
    done_event = asyncio.Event()
    outbound_queue = asyncio.Queue()
    chunked_list = list(chunk_list(config.feeds, config.num_of_workers))

    loop = asyncio.get_event_loop()

    output_handler = loop.create_task(handle_output(outbound_queue, done_event))

    workers = [
        parse_feeds(i+1, f, done_event, outbound_queue) for i, f in enumerate(chunked_list)
        ]

    await asyncio.gather(*workers+[output_handler])


async def handle_output(outbound_queue: asyncio.Queue, done_event: asyncio.Event):
    while not done_event.is_set():
        doc = await outbound_queue.get()
        print(doc)

def chunk_list(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]


def main(args):
    """
    Main method for feedparser, takes arguments and parses them and calls async_main method
    """
    parser = argparse.ArgumentParser()

    parser.add_argument('-f', '--feeds', help='list of feed links', required=True)
    parser.add_argument('-nw', '--num_of_workers', help='number of workers to work on feeds', default=5)

    parsed_args = parser.parse_args(args)

    config = Config(
        feeds=parsed_args.feeds.split(','),
        num_of_workers=parsed_args.num_of_workers
    )

  
    loop = asyncio.get_event_loop()
    asyncio.run(async_main(config))

    return os.EX_OK

if __name__ == '__main__':
    args = sys.argv[1:]
    sys.exit(main(args))

