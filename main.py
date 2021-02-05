#!/bin/python3

import json
import os
import socketserver

import feedparser

from typing import TextIO, Union, Tuple

from feedparser import FeedParserDict
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, ParseResult

hostName: str = "localhost"
serverPort: int = 8079


# Title - feed["entries"][index]["title"]
# Description - feed["entries"][index]["summary"]
# Canonical - feed["entries"][index]["link"]

class MyServer(BaseHTTPRequestHandler):
    def __init__(self, request: bytes, client_address: Tuple[str, int], server: socketserver.BaseServer):
        self.working_dir: str = "working"
        self.rss_feed_url: str = "https://www.dolthub.com/blog/rss.xml"
        self.rss_cache_cache: str = os.path.join(self.working_dir, "rss.json")
        self.template: str = "templates/meta.html"

        # Load Feed To Memory
        self.feed: Union[FeedParserDict, dict] = self.load_feed()

        super().__init__(request, client_address, server)

    def load_feed(self, override_cache: bool = False) -> Union[FeedParserDict, dict]:
        if not os.path.exists(self.working_dir):
            os.mkdir(self.working_dir)

        if os.path.exists(self.rss_cache_cache) and not override_cache:
            print("Loading From Cache!!!")
            cache: TextIO = open(file=self.rss_cache_cache, mode="r")
            feed_lines: str = "\n".join(cache.readlines())
            cache.close()
            rss_feed: dict = json.loads(feed_lines)
        else:
            print("Loading From Live!!!")
            rss_feed: feedparser = feedparser.parse(self.rss_feed_url)
            cache: TextIO = open(file=self.rss_cache_cache, mode="w+")
            cache.writelines(json.dumps(rss_feed))
            cache.close()

        return rss_feed

    def do_GET(self):
        path_result: ParseResult = urlparse(url=self.path)
        path: str = path_result.path if path_result.path[-1] == "/" else path_result.path + "/"

        if not path.startswith("/blog/"):
            self.send_response(404)
            self.end_headers()
            return

        blog_path: str = "https://www.dolthub.com" + path

        # https://www.dolthub.com/blog/2021-02-03-dolt-vs-mysql/
        match = next((post for post in self.feed["entries"] if post['link'] == blog_path), None)

        if match is None:
            self.feed = self.load_feed(override_cache=True)

            match = next((post for post in self.feed["entries"] if post['link'] == blog_path), None)

            if match is None:
                print(f"Blog Post {blog_path} Not Found!!!")
                self.send_response(404)
                self.end_headers()
                return

        if 'user-agent' in self.headers and 'Twitterbot' in self.headers['user-agent']:
            self.send_response(200)
        else:
            self.send_response(301)
            self.send_header("Location", blog_path)

        self.send_header("Content-type", "text/html")
        self.end_headers()
        body_handle: TextIO = open(file=self.template, mode="r")
        body: str = "".join(body_handle.readlines()).format(post_title=match["title"], post_summary=match["summary"], post_url=match["link"])

        self.wfile.write(bytes(body, encoding="utf16"))


if __name__ == "__main__":
    # for item in feed["entries"]:
    #     print(item["link"])

    webServer = HTTPServer((hostName, serverPort), MyServer)
    print("Server started http://%s:%s" % (hostName, serverPort))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")
