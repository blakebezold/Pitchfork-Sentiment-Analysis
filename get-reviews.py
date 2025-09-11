#!/usr/bin/env python3

import concurrent.futures
import time
import requests
import json
import html
import sys
import csv

def print_review(url) -> dict[str, str]:
  res = requests.get(url)

  # finding the album title
  start_marker = r'<meta property="og:title" content="'
  end_marker = r'"/>'

  start_index = res.text.find(start_marker)

  if start_index == -1:
      return {}
  
  start_index += len(start_marker)
  end_index = res.text.find(end_marker, start_index)

  if end_index == -1:
      return {}
  
  title = html.unescape(res.text[start_index:end_index + 1])

  # finding the description
  start_marker = r'<meta property="og:description" content="'
  end_marker = r'"/>'

  start_index = res.text.find(start_marker)

  if start_index == -1:
      return {}
  
  start_index += len(start_marker)
  end_index = res.text.find(end_marker, start_index)

  if end_index == -1:
      return {}
  
  description = html.unescape(res.text[start_index:end_index + 1].replace("\n", ""))
  


  # finding the rating 
  start_marker = 'window.__PRELOADED_STATE__ = '
  end_marker = '};'

  start_index = res.text.find(start_marker)

  if start_index == -1:
      return {}
  
  start_index += len(start_marker)
  end_index = res.text.find(end_marker, start_index)

  if end_index == -1:
      return {}
  
  json_text = res.text[start_index:end_index + 1] 

  data = json.loads(json_text)
  score = data.get('transformed', {}) \
              .get('review', {}) \
              .get('headerProps', {}) \
              .get('musicRating', {}) \
              .get('score')
  
  return {'title':title, 'score':score, 'description':description, 'url':url}

  

def read_urls(path):
    with open(path) as file:
      for line in file:
          if line[0] != '!':
            yield line.strip()
    

if __name__ == '__main__':
  if len(sys.argv) != 3:
     print('Incorrect usage, need 3 args')
     sys.exit(1)
  
  urls = read_urls(sys.argv[1])
  output_file = sys.argv[2]

  num_reviews = 0
  with open(output_file, 'w', newline='') as csvfile:
    fieldnames = ['title', 'score', 'description', 'url']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames, quoting=csv.QUOTE_MINIMAL)
    writer.writeheader()

    start_time = time.time()

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(print_review, url) for url in urls]
        for future in concurrent.futures.as_completed(futures):
            writer.writerow(future.result())
            num_reviews += 1

    end_time = time.time()
  print(f"Requested {num_reviews} reviews in {end_time - start_time:.2f} seconds")