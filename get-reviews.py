#!/usr/bin/env python3

import concurrent.futures
import time
import requests
import json
import html
import sys
import csv
import argparse

def fetch_review(url) -> dict[str, str]:
  ''' Scrapes the desired url and returns a dict containing the relevant information '''
  output_dict = {'url':url}

  res = requests.get(url)
  res.raise_for_status()

  # finding the album title
  start_marker = r'<meta property="og:title" content="'
  end_marker = r'"/>'

  start_index = res.text.find(start_marker)

  if start_index == -1:
      return output_dict
  
  start_index += len(start_marker)
  end_index = res.text.find(end_marker, start_index)

  if end_index == -1:
      return output_dict
  
  output_dict['title'] = html.unescape(res.text[start_index:end_index + 1])

  # finding the description
  start_marker = r'<meta property="og:description" content="'
  end_marker = r'"/>'

  start_index = res.text.find(start_marker)

  if start_index == -1:
      return output_dict
  
  start_index += len(start_marker)
  end_index = res.text.find(end_marker, start_index)

  if end_index == -1:
      return output_dict
  
  output_dict['description'] = html.unescape(res.text[start_index:end_index + 1].replace("\n", ""))
  
  # finding the rating 
  start_marker = 'window.__PRELOADED_STATE__ = '
  end_marker = '};'

  start_index = res.text.find(start_marker)

  if start_index == -1:
      return output_dict
  
  start_index += len(start_marker)
  end_index = res.text.find(end_marker, start_index)

  if end_index == -1:
      return output_dict
  
  json_text = res.text[start_index:end_index + 1] 

  data = json.loads(json_text)
  score = data.get('transformed', {}) \
              .get('review', {}) \
              .get('headerProps', {}) \
              .get('musicRating', {}) \
              .get('score')
  
  output_dict['score'] = score
  
  return output_dict

  

def read_urls(path):
    ''' Reads a file to create a generator object that returns each url line by line '''
    with open(path) as file:
      for line in file:
          if line[0] != '!':
            yield line.strip()
    

if __name__ == '__main__':
  description = 'Searches the Pitchfork reviews and outputs their information'
  parser = argparse.ArgumentParser(description=description)
  parser.add_argument('-i', '--input', type=str, help='Input file ')
  parser.add_argument('-o', '--output', type=str, default='reviews.txt', help='Output file (defaults to stdout)')

  args = parser.parse_args()

  input_file = args.input
  output_file = args.output

  urls = read_urls(input_file)

  num_reviews = 0
  with open(output_file, 'w', newline='') as csvfile:
    fieldnames = ['title', 'score', 'description', 'url']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames, quoting=csv.QUOTE_MINIMAL)
    writer.writeheader()

    start_time = time.time()

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(fetch_review, url) for url in urls]
        for future in concurrent.futures.as_completed(futures):
            writer.writerow(future.result())
            num_reviews += 1

    end_time = time.time()
  print(f"Requested {num_reviews} reviews in {end_time - start_time:.2f} seconds")