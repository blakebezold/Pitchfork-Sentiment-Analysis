#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
import sys

def find_locs(url) -> list[str]:
    sitemaps = []
    try:
        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'xml')

        for loc in soup.find_all('loc'):
            sitemaps.append(loc.text)
        return sitemaps
    

    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL: {e}", file=sys.stderr)
    return []


if __name__ == '__main__':
    if len(sys.argv) != 4:
        print('Wrong number of arguments')
        sys.exit(1)

    starting_year = int(sys.argv[2])
    ending_year = int(sys.argv[3])

    output_file = sys.argv[1]

    num_reviews = 0
    with open(output_file, 'w', newline='') as f:
      for year in range(starting_year, ending_year):
          for month in range(1, 13):
              for week in range(1, 6):
                  url = f'https://pitchfork.com/sitemap.xml?year={year}&month={month}&week={week}'
                  f.write(f'!{year} {month} {week}')
                  for page in find_locs(url):
                      if 'https://pitchfork.com/reviews/' in page:
                          f.write(page)