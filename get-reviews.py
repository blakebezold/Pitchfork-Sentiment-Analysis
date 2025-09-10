#!/usr/bin/env python3

import concurrent.futures
import time
import requests
import json
import sys

def print_review(url):
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
  
  title = res.text[start_index:end_index + 1] 

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
  
  description = res.text[start_index:end_index + 1].replace("\n", "")

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
  
  return f'{title}|{score}|{description}|{url}'
  

def read_urls():
    with open('urls.txt') as file:
      for line in file:
          if line[0] != '!':
            yield line.strip()
    

if __name__ == '__main__':
  urls = read_urls()

  start_time = time.time()

  with concurrent.futures.ThreadPoolExecutor() as executor:
      futures = [executor.submit(print_review, url) for url in urls]
      for future in concurrent.futures.as_completed(futures):
          print(future.result())

  end_time = time.time()
  print(f"Requested reviews in {end_time - start_time:.2f} seconds")