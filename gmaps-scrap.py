import sys
import time
from parsel import Selector
from selenium import webdriver
from selenium.webdriver.common.by import By
import re

def removeDuplicates(arr, n):
 
    # Return, if array is
    # empty or contains
    # a single element
    if n == 0 or n == 1:
        return n
 
    temp = list(range(n))
 
    # Start traversing elements
    j = 0;
    for i in range(0, n-1):
 
        # If current element is
        # not equal to next
        # element then store that
        # current element
        if arr[i]['title'] != arr[i+1]['title']:
            temp[j] = arr[i]
            j += 1
 
    # Store the last element
    # as whether it is unique
    # or repeated, it hasn't
    # stored previously
    temp[j] = arr[n-1]
    j += 1
     
    # Modify original array
    for i in range(0, j):
        arr[i] = temp[i]
 
    return j

chromedrive_path = './chromedriver'
driver = webdriver.Chrome(chromedrive_path)

search_query = '+'.join(sys.argv[1:])

url = 'https://www.google.com/search?&q=psicologos+' + search_query

driver.get(url)
time.sleep(1)
next_button = driver.find_element(By.XPATH, '//*[text()="Mais lugares"]')
next_button.click()



retries = 0
results = []

query_arr = ['psicologos'] + sys.argv[1:]
query = '%20'.join(query_arr)

while retries < 3:
  try:
    page_content = driver.page_source

    response = Selector(page_content)

    if retries == 0:
      for el in response.xpath('//div[contains(@data-async-context, "query:' + query+ '")]//div[@data-record-click-time="false"]'):
        results.append({
              'title': el.xpath('.//div[@role="heading"]/span/text()').extract_first(''),
              'contact': el.xpath('.//div[re:match(text(), ".*\(\\d*\).\\d*-\\d*")]/text()').extract_first()
          })
    print(results)

    time.sleep(2)
    button = driver.find_element(By.ID, 'pnnext')
    button.click()
    retries = 0
  except Exception as e:
    print(e)
    retries+=1
    print("Retries: "+ str(retries))

pattern = r'\(\d*\).\d*-\d*'

results.sort(key=lambda x: x['title'])

n = removeDuplicates(results, len(results))

for i in range(n):
  if results[i]['contact'] != None:
    contact = re.findall(pattern,results[i]['contact'])[0]
    results[i]['contact'] = contact

file_name = " ".join(sys.argv[1:])

file_csv = open(file_name + ".csv", "w", encoding='iso-8859-1')

for i in range(n):
  try:
    if results[i]['contact'] != None:
      results[i]['contact'] = re.sub('\ |\(|\)|-|;', '', results[i]['contact'])
      results[i]['title'] = re.sub(';', '', results[i]['title'])
      file_csv.write(results[i]['title'] + ";"  + results[i]['contact'] + "\n")
  except:
      continue


driver.close()
