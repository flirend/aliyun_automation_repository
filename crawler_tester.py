#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import logging
from newspaper import Source
from newspaper import Article
import csv
import argparse
import sys
import time
import random


def main(param):
    logger.info("Start to process Source: {}".format(param.URL))
    source = Source(param.URL, memoize_articles=param.remember, number_threads=param.threads)
    source.download()
    source.parse()
    source.set_categories()
    source.download_categories()
    source.parse_categories()
    source.set_feeds()
    source.download_feeds()
    source.generate_articles(limit=param.limit)
    logger.info("Total article number: {}".format(source.size()))

    skip_count: int = 0
    download_count: int = 0

    with open(param.target, 'w', newline='') as f:
        writer = csv.writer(f)
        for a in source.articles:
            if param.download:
                try:
                    article = Article(a.url, fetch_images=param.image)
                    article.download()
                    article.parse()
                    writer.writerow([article.title, article.url])
                    download_count += 1
                    time.sleep(random.uniform(param.sleep_range[0], param.sleep_range[1]))
                except Exception:
                    if param.verbose:
                        logger.exception("Exception when processing URL {}".format(article.url))
                    skip_count += 1
            else:
                f.write(a.url + "\n")
                download_count += 1

    logger.info("Finish processing download list")
    logger.info("{0} page(s) downloaded, {1} page(s) skipped, total page number: {2}".format(download_count, skip_count,
                                                                                             download_count+skip_count))


def parse_arg():
    parser = argparse.ArgumentParser(description='Use newspaper lib to crawl URL(s)')
    parser.add_argument('URL', help='Target URL')
    parser.add_argument('-t', '--target', help='Full path to the output file (one article url per line)', required=True)
    parser.add_argument('-m', '--threads', help='Set thread number, default to 10', default=10, type=int)
    parser.add_argument('-l', '--limit', help='Limit the maximum number of pages to retrieve, default to 5000',
                        default=5000, type=int)
    parser.add_argument('-f', '--log_file', type=argparse.FileType('w+'), default=sys.stdout)
    parser.add_argument('-r', '--remember', help='Remember (and skip) previous articles', action='store_true')
    parser.add_argument('-i', '--image', help='download image if specified', action='store_true')
    parser.add_argument('-d', '--download', help='Download article and save title', action='store_true')
    parser.add_argument('-s', '--sleep_range', help='Range of sleep time', nargs=2, type=float, default=[0, 1])
    parser.add_argument('-v', '--verbose', help='Verbose mode', action='store_true')
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arg()
    logger = logging.getLogger("logger")
    handler = logging.StreamHandler(args.log_file)
    formatter = logging.Formatter("%(asctime)s %(name)s %(levelname)s %(message)s")
    handler.setFormatter(formatter)

    if args.verbose:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.WARN)

    logger.addHandler(handler)

    logger.info(args)
    main(args)
