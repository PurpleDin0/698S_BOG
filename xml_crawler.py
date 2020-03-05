#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    Following PEP8 Style Guide and Google format function docstrings
    Script takes a list of .rss links and parses them for content and writes output to .csv
    root/
    |____log/
    |    |____pull.log
    |____content/
    |    |____`file.csv`
    |____temp/
         |____`timestamp.xml`
"""

# Standard library imports one per line
import sys
import os
import requests
import logging
import csv
from time import time

# Third party library imports one per line
import bs4 as soup
from tqdm import tqdm

# Authorship constants
__authors__ = ['BA', 'JP']
__copyright__ = "Copyright 2020, NIU"
__credits__ = [None]
__version__ = "0.1"
__status__ = "Alpha"
__date__ = "5 March 2020"
__location__ = os.path.dirname(os.path.realpath(__file__))

# Global variables
logging.basicConfig(filename=r"log\pull.log",
                    level=logging.INFO,
                    format="%(asctime)s %(message)s",
                    datefmt="%m/%d/%Y %I:%M:%S %p")
URLS = ("http://www.****.***.**/n1146290/n1146402/n7039597/rss.xml",
        "http://www.****.***.**/n1146290/n1146402/rss.xml",
        "http://www.****.***.**/n1146295/rss.xml",
        "http://www.****.***.**/n1278117/rss.xml")
CSV_FILE = "****.csv"
CSV_FIELDS = ["url", "published", "title", "content"]


def download(url, filename):
    """
    Summary:
        `download` requests the .rss link and saves the raw xml to file in timestamp format `1583450018-0560708.xml`
        in the folder `temp`.
        Parameters:
            url (str): Site to downlaod.
            filename (str): Base filename is timestamped like `1583450018-0560708`.
        Returns:
            bool: Returns `filename` or `None`.
    """
    r = requests.get(url, stream=True)
    if r.status_code == 200:
        total_size = int(r.headers.get('content-length', 0))
        block_size = 1024
        t = tqdm(total=total_size, unit='b', unit_scale=True, ncols=100, desc="Downloading", position=0, ascii=True)
        with open(os.path.join("temp", filename + ".xml"), 'wb') as f:
            for data in r.iter_content(block_size):
                t.update(len(data))
                f.write(data)
        t.clear()
        logging.info("200 SUCCESS " + str(url) + " " + filename + ".xml")
        return filename
    elif r.status_code == 404:
        print("ERROR 404, page not found.")
        logging.warning("404 ERROR " + str(url))
        return None
    else:
        print("ERROR {}, something went wrong.".format(r.status_code))
        logging.warning("{} ERROR, something went wrong.".format(r.status_code) + " " + str(url))
        return None


def extract_content(filename):
    """
    Summary:
            `extract_content` reads the raw xml from the temp file and extracts the elements and writes to the
            cvs file in the folder `content`.
            Parameters:
                filename (str): Base filename is timestamped like `1583450018-0560708`.
            Returns:
                Null: No return
    """
    if not os.path.isfile(os.path.join("content", CSV_FILE)):
        with open(os.path.join("content", CSV_FILE), 'w', newline='', encoding="utf-8") as csvfile:
            csv.writer(csvfile, quoting=csv.QUOTE_ALL).writerow(CSV_FIELDS)
    with open(os.path.join("temp", filename + ".xml"), 'rb') as f:
        xml_page = f.read()
    soup_page = soup.BeautifulSoup(xml_page, "xml")
    for item in soup_page.find_all('item'):
        link = str(item.link.text).strip()
        pub = str(item.publishTime.text).strip()
        title = str(item.title.text).strip()
        content = str(item.description.text).replace('\n', ' ').replace('\r', ' ').strip()
        with open(os.path.join("content", CSV_FILE), 'a', newline='', encoding="utf-8") as csvfile:
            csv.writer(csvfile, quoting=csv.QUOTE_ALL).writerow([link, pub, title, content])


def dedupe(url):
    """
    Summary:
            `dedupe` checks the `pull.log` file for `url`, skips `url` and contimnues if already pulled.
            Parameters:
                url (str): Site.
            Returns:
                bool: Returns `True` if new content or `None` if site has already been pulled.
    """
    with open(os.path.join("log", "pull.log"), 'r') as log:
        if url in log.read():
            return None
        else:
            return True


if __name__ == '__main__':
    for url in URLS:
        if dedupe(url):
            print("-" * 100 + "\n" + "Requesting: " + str(url))
            new_content = download(url, str(time()).replace(".", "-"))
            if new_content:
                print("Extracting content from: " + url)
                extract_content(new_content)
        else:
            print("-" * 100 + "\n" + "Skipping: " + str(url))
    print("-" * 100 + "\n" + "DONE!")
    sys.exit()
