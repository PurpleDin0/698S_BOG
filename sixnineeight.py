# -*- coding: utf-8 -*-
"""
    Following PEP8 Style Guide and Google format function docstrings
    Website spider to extract list of URLs and saves to file.
    root/
    |_____file.json
"""

# Standard library imports one per line
import sys
import argparse
from urllib.parse import urlparse, urljoin

# Third party library imports one per line
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor
from scrapy.spiders import Rule

# Authorship constants
__authors__ = ['BA', 'JP']
__copyright__ = "Copyright 2020, NIU"
__credits__ = [None]
__version__ = "0.1"
__status__ = "Alpha"
__date__ = "10 March 2020"

# Global variables
visited = list()
NAME = 'sixnineeight'

parser = argparse.ArgumentParser()
parser.add_argument("ALLOWED_DOMAINS", help="The DOMAIN for the spider to crawl. Format: site.com")
parser.add_argument("URLS", help="The URL for the spider to crawl. Format: https://www.site.com")
args = parser.parse_args()

ALLOWED_DOMAINS = args.ALLOWED_DOMAINS.split('=')[1] # Base URL goes here  ## USER UPDATEABLE VALUE! ##
URLS = args.URLS.split('=')[1] # Fully qualified domain goes here  ## USER UPDATEABLE VALUE! ##


class SixnineeightSpider(scrapy.Spider):
    """
        Summary:
            `SixnineeightSpider` instantiates the custom spider object.
            Parameters:
                scrapy.Spider (obj):
            Returns:
                (None)
    """
    name = NAME
    allowed_domains = [ALLOWED_DOMAINS]
    start_urls = [URLS]
    custom_settings = {
        'DEPTH_LIMIT': 1  # Gets deep quick...2 is very deep on large sites e.g. 45K+ unique links on CNN. 0=no limit
    }
    rules = (
        Rule(
            LxmlLinkExtractor(allow=()),
            callback='parse_obj',
            follow=True),
    )

    def parse(self, response):
        """
            Summary:
                `parse` method to parse spider responses.
                Parameters:
                    self (obj): self
                    response (obj): scrapy.Response
                Returns:
                    (None)
        """
        links = response.xpath('//a//@href').extract()
        for link in links:
            if "#" in link:
                link = link.split("#")[0]
            if link in visited or urljoin(URLS,
                                          link) in visited or "mailto:" in link or "tel:" in link or "javascript:" in link:
                continue
            else:
                if ALLOWED_DOMAINS in link and link in urlparse(link).netloc:
                    if urlparse(link).scheme == '':
                        link = urljoin(urlparse(URLS).scheme, urlparse(URLS).path, link)
                    visited.append(link)
                    yield {
                        "link": link
                    }
                    continue
                if urlparse(link).netloc == '' and link not in visited:
                    visited.append(urljoin(URLS, link))
                    yield {
                        "link": urljoin(URLS, link)
                    }
                    continue
                if urlparse(link).netloc != '' and ALLOWED_DOMAINS not in link:
                    continue

        for next_page in links:
            if next_page is not None and urlparse(next_page).netloc == '' or ALLOWED_DOMAINS in next_page:
                if urlparse(next_page).netloc == '':
                    next_page = urljoin(URLS, next_page)
                next_page = response.urljoin(next_page)
                yield scrapy.Request(next_page, callback=self.parse, dont_filter=True)

        pass


# Cool banner printer
def banner(t, s='~'):
    l = s * (len(t) + 4)
    print(l + '\n' + '{0} {1} {0}'.format(s, t) + '\n' + l)

# Formatted line
def line(t):
  print("\n", "~"*(26-(len(t)//2)), t, "~"*(26-(len(t)//2)))


if __name__ == '__main__':
  # Prints a banner
  from time import time, ctime, strftime, gmtime

  def elapsed(start_time):
    """
      Calcuilates the elapsed time of script start of exeution until
      code completes. This allows for baselining different runtime enviroments
    """
    current_time = time()
    elapsed_time = current_time - start_time
    print("\n\n" + "~"*50)
    print("             End : " + ctime(current_time))
    print("        Run Time : " + strftime("%H:%M:%S", gmtime(elapsed_time)))
    print("~"*50)

  start_time = time()

  banner('Running the Spider for links')

  # Generic spider object with custom settings
  process = CrawlerProcess(
              settings={
                # 'FEED_FORMAT': 'pickle',
                # 'FEED_URI': 'file:///***/links.pkl',
                # 'LOG_LEVEL': 'INFO',  # Uncomment if you don't want scrapy to puke DEBUG to the console
                # 'DOWNLOAD_DELAY': 0.25,   # 250 ms of delay, default is random between 0.5 - 1.5
                'TELNETCONSOLE_ENABLED': False,  # On by default...that's dumb ¯\_(ツ)_/¯
                'FEED_FORMAT': 'json',
                'FEED_URI': 'links.json',
                'LOG_LEVEL': 'CRITICAL',
                'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36',
                'CLOSESPIDER_TIMEOUT': 60
              } 
            )

  # Instantiates the custom spider class object
  process.crawl(SixnineeightSpider)
  try:
      # Kick off the custom spider and crawl
      process.start()

      print("It worked!!")
      print("Output {} file written to {}.".format(process.settings['FEED_FORMAT'], process.settings['FEED_URI']))
      elapsed(start_time)
  except Exception as e:
      print("Well, that didn't work... \n {}".format(e))