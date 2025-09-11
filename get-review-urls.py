#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
import sys
import argparse

def find_reviews(url) -> list[str]:
  ''' Searches the Pitchfork sitemap and returns all of the album reviews found within  '''
  sitemaps = []
  try:
      res = requests.get(url)
      res.raise_for_status()

      soup = BeautifulSoup(res.content, 'xml')

      for loc in soup.find_all('loc'):
        site = loc.text
        if 'https://pitchfork.com/reviews/albums/' in site:
            sitemaps.append(site)
      
      return sitemaps
  

  except requests.exceptions.RequestException as e:
      print(f"Error fetching URL: {e}", file=sys.stdout)
  return []
    
def search(start, stop, destination):
  ''' Calls the find_reviews function for the specified years and outputs to the specified file  '''
  if destination == 'stdout':
      output_stream = sys.stdout
  else:
      output_stream = open(destination, 'w')

  num_reviews = 0
  for year in range(start, stop):
      for month in range(1, 13):
          for week in range(1, 6):
              url = f'https://pitchfork.com/sitemap.xml?year={year}&month={month}&week={week}'
              print(f'!{year} {month} {week}', file=output_stream)
              for page in find_reviews(url):
                    print(page, file=output_stream)


if __name__ == '__main__':
    description = 'searches Pitchfork index for album reviews from a specified period of time'
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('-s', '--start-year', type=int, help='Specify the stat year')
    parser.add_argument('-e', '--end-year', type=int, help='Specify the end year')
    parser.add_argument('-o', '--output', type=str, default='stdout', help='Output file (defaults to stdout)')

    args = parser.parse_args()

    starting_year = args.start_year
    ending_year = args.end_year
    output = args.output

    if ending_year is None:
        ending_year = starting_year + 1

    search(starting_year, ending_year, output)