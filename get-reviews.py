#!/usr/bin/env python3

import concurrent.futures
import time
import requests
import json
import html
import sys
import csv
import io

def print_review(title, score, description, url):
    """
    Print the review as a CSV line to stdout with proper quoting.
    """
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=['title', 'score', 'description', 'url'], quoting=csv.QUOTE_MINIMAL)
    writer.writerow({
        'title': title,
        'score': score,
        'description': description,
        'url': url
    })

    print(output.getvalue().strip())

def fetch_review(url):
  """
  Request the url at the specified url and call the print review function
  """
  res = requests.get(url)

  # finding the album title
  start_marker = r'<meta property="og:title" content="'
  end_marker = r'"/>'

  start_index = res.text.find(start_marker)

  if start_index == -1:
      return None
  
  start_index += len(start_marker)
  end_index = res.text.find(end_marker, start_index)

  if end_index == -1:
      return None
  
  title = html.unescape(res.text[start_index:end_index + 1])

  # finding the description
  start_marker = r'<meta property="og:description" content="'
  end_marker = r'"/>'

  start_index = res.text.find(start_marker)

  if start_index == -1:
      return None
  
  start_index += len(start_marker)
  end_index = res.text.find(end_marker, start_index)

  if end_index == -1:
      return None
  
  description = html.unescape(res.text[start_index:end_index + 1].replace("\n", ""))
  


  # finding the rating 
  start_marker = 'window.__PRELOADED_STATE__ = '
  end_marker = '};'

  start_index = res.text.find(start_marker)

  if start_index == -1:
      return None
  
  start_index += len(start_marker)
  end_index = res.text.find(end_marker, start_index)

  if end_index == -1:
      return None
  
  json_text = res.text[start_index:end_index + 1] 

  data = json.loads(json_text)
  score = data.get('transformed', {}) \
              .get('review', {}) \
              .get('headerProps', {}) \
              .get('musicRating', {}) \
              .get('score')
  
  print_review_to_stdout(title, score, description, url)
  

def read_urls(path):
    with open(path) as file:
      for line in file:
          if line[0] != '!':
            yield line.strip()
    

if __name__ == '__main__':
  if len(sys.argv) != 2:
     print(' Please enter a file containing the pitchfork review urls')
     sys.exit(1)
  
  urls = read_urls(sys.argv[1])

  start_time = time.time()

  with concurrent.futures.ThreadPoolExecutor() as executor:
      futures = [executor.submit(print_review, url) for url in urls]
      for future in concurrent.futures.as_completed(futures):
          print(future.result())

  end_time = time.time()
  print(f"Requested reviews in {end_time - start_time:.2f} seconds")