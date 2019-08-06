#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import csv
import logging
import time
import random
from newspaper import Article
import argparse
import concurrent.futures
import datetime as dt


def download_url(url, sleep_range, download_only, writer=None, fetch_image=False, verbose=False):
    try:
        article = Article(url, fetch_images=fetch_image)
        article.download()
        if not download_only:
            article.parse()
            writer.writerow([article.title, article.url])
        if sleep_range[0] == sleep_range[1]:
            time.sleep(sleep_range[0])
        else:
            time.sleep(random.uniform(sleep_range[0], sleep_range[1]))
    except Exception as e:
        if verbose:
            logger.exception("Exception when processing URL {}".format(article.url))


def main(param):
    logger.info("Start to process download list")
    start_time = dt.datetime.now()
    writer = csv.writer(param.outfile)
    url_count = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=param.threads) as e:
        if param.verbose:
            logger.info("Thread number: {}".format(param.threads))
        for line in param.infile:
            url = line.strip()
            if not url:
                # Skip the empty line
                logger.info("Skipping one empty line")
                continue
            else:
                url_count += 1
                # logger.debug("No. {}".format(url_count))
                e.submit(download_url, url, param.sleep_range, param.download_only, writer=writer,
                         fetch_image=param.image, verbose=param.verbose)

    logger.info("Finish processing download list")
    end_time = dt.datetime.now()
    duration = (end_time - start_time).seconds
    # CSV format: [prefix, threads, duration_in_seconds]
    writer.writerow([param.prefix, param.threads, duration])
    param.infile.close()
    param.outfile.close()


def parse_arg():
    parser = argparse.ArgumentParser(description='Use newspaper lib to crawl URL(s)')
    parser.add_argument('infile', help='Input file, one URL per line', type=argparse.FileType('r'))
    parser.add_argument('outfile', help='Output file, one URL per line', type=argparse.FileType('w'))
    parser.add_argument('-l', '--log_file', type=argparse.FileType('w+'), default=sys.stdout)
    parser.add_argument('-m', '--threads', help='Set thread number, default to 5 per core', type=int)
    parser.add_argument('-i', '--image', help='download image if specified', action='store_true')
    parser.add_argument('-r', '--sleep_range', help='Range of sleep time', nargs=2, type=float, default=[0, 1])
    parser.add_argument('-v', '--verbose', help='Verbose mode', action='store_true')
    parser.add_argument('-d', '--download_only', help='Download URL, no parsing', action='store_true')
    parser.add_argument('-p', '--prefix', help='Prefix')

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
