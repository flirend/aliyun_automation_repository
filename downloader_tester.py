#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import csv
import logging
import time
import random
from newspaper import Article
import argparse


def main(param):
    logger.info("Start to process download list")
    writer = csv.writer(param.outfile)
    skip_count: int = 0
    download_count: int = 0
    for line in param.infile:
        url = line.strip()
        if not url:
            # Skip the empty line
            logger.info("Skipping one empty line")
            continue
        else:
            try:
                article = Article(url, fetch_images=param.image)
                article.download()
                article.parse()
                writer.writerow([article.title, article.url])
                download_count += 1
            except Exception as e:
                if param.verbose:
                    logger.exception("Exception when processing URL {}".format(article.url))
                skip_count += 1
        time.sleep(random.uniform(param.sleep_range[0], param.sleep_range[1]))

    logger.info("Finish processing download list")
    logger.info("{0} page(s) downloaded, {1} page(s) skipped, total page number: {2}".format(download_count, skip_count,
                                                                                             download_count+skip_count))
    param.infile.close()
    param.outfile.close()


def parse_arg():
    parser = argparse.ArgumentParser(description='Use newspaper lib to crawl URL(s)')
    parser.add_argument('infile', help='Input file, one URL per line', type=argparse.FileType('r'))
    parser.add_argument('outfile', help='Output file, one URL per line', type=argparse.FileType('w'))
    parser.add_argument('-l', '--log_file', type=argparse.FileType('w+'), default=sys.stdout)
    parser.add_argument('-m', '--threads', help='Set thread number, default to 1', default=1, type=int)
    parser.add_argument('-i', '--image', help='download image if specified', action='store_true')
    parser.add_argument('-r', '--sleep_range', help='Range of sleep time', nargs=2, type=float, default=[0, 1])
    parser.add_argument('-v', '--verbose', help='Verbose mode', action='store_true')

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arg()
    global logger
    logger = logging.getLogger("logger")
    handler = logging.StreamHandler(args.log_file)
    formatter = logging.Formatter("%(asctime)s %(name)s %(levelname)s %(message)s")
    handler.setFormatter(formatter)

    if args.verbose:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.WARN)

    logger.addHandler(handler)
    main(args)
