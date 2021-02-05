#!/bin/python3

import json
import os
import feedparser

from typing import TextIO, Union

from feedparser import FeedParserDict

working_dir: str = "working"

rss_feed_url: str = "https://www.dolthub.com/blog/rss.xml"
rss_cache_cache: str = os.path.join(working_dir, "rss.json")


def load_feed(override_cache: bool = False) -> Union[FeedParserDict, dict]:
    if not os.path.exists(working_dir):
        os.mkdir(working_dir)

    if os.path.exists(rss_cache_cache) and not override_cache:
        print("Loading From Cache!!!")
        cache: TextIO = open(file=rss_cache_cache, mode="r")
        feed_lines: str = "\n".join(cache.readlines())
        cache.close()
        rss_feed: dict = json.loads(feed_lines)
    else:
        print("Loading From Live!!!")
        rss_feed: feedparser = feedparser.parse(rss_feed_url)
        cache: TextIO = open(file=rss_cache_cache, mode="w+")
        cache.writelines(json.dumps(rss_feed))
        cache.close()

    return rss_feed


feed: Union[FeedParserDict, dict] = load_feed()

# Title - feed["entries"][index]["title"]
# Description - feed["entries"][index]["summary"]
# Canonical - feed["entries"][index]["link"]

for item in feed["entries"]:
    print(item["link"])