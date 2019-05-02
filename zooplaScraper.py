import requests
import certifi
import urllib3
from collections import OrderedDict
import argparse
import hashlib
from datetime import datetime

from bs4 import BeautifulSoup
import re
import pickle

import math
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def parse(date, new_properties_only=True):    

    availability = datetime.strptime(date, '%d/%m/%Y')
    suitable_properties = []
    new_properties = []

    try:
        previous_search = pickle.load(open('zoopla-properties.txt', 'rb'))
    except FileNotFoundError:
        previous_search = []

    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36'}

    url = "https://www.zoopla.co.uk/to-rent/flats/4-bedrooms/uk/?polyenc=eeltI%60biRsDcB~DdB&polyenc=eeltI%60biRfV%7CK~Jvu%40sKr%7BCjAhjB%7Bp%40jDeRqFaQtWyXdAsHsGg%7C%40%7DbCy%40st%40lMi~%40dUor%40v%7CAor%40&price_frequency=per_month&price_max=2500&q=Edinburgh&results_sort=newest_listings&search_source=refine&user_alert_id=8483748"
    response = requests.get(url, headers=headers, verify= False)

    soup = BeautifulSoup(response.content, 'html.parser')
    result_number = (
        soup.find('span', {'class': 'listing-results-utils-count'})
    )
    result_number = int((result_number.get_text()).split()[4])
    
    raw_results = soup.find_all('li', {'data-listing-id': re.compile(r'\d+')})
    
    if result_number > 25:
        page_number = math.ceil(result_number/25)

        for i in range(2, page_number+1):
            next_page_url = url + '&pn=%d' % i
            next_page_response = requests.get(next_page_url, headers=headers, verify=False)
            next_page_soup = BeautifulSoup(next_page_response.content, 'html.parser')
            next_page_raw_results = next_page_soup.find_all('li', {'data-listing-id': re.compile(r'\d+')}) 
            raw_results = raw_results + next_page_raw_results
    
    for r in raw_results:
        raw_date = r.find('p', {'class': 'available-from'})
        raw_date_list= raw_date.get_text().split()
        if len(raw_date_list) == 2:
            date = datetime.now()
        else:
            day = re.search(r'\d+',raw_date_list[2]).group(0)
            month = raw_date_list[3]
            year = raw_date_list[4]
            date = datetime.strptime('%s/%s/%s'%(day, month, year), '%d/%b/%Y')
        
        if date >= availability:
            property_link = r.find('a', {'class': 'listing-results-price text-price'}, href=True)
            suitable_properties.append('https://www.zoopla.co.uk/' + property_link['href'])

        for s in suitable_properties:
            if s not in previous_search:
                new_properties.append(s)
        
        previous_search = previous_search + new_properties

    with open('zoopla-properties.txt', 'wb') as f:
        pickle.dump(previous_search, f)
    
    if new_properties_only:
        return new_properties
    else:
        return suitable_properties

   

if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument('date', help="Availability date")
    #argparser.add_argument('url', help="URL of result list")

    args = argparser.parse_args()
    date = args.date
    #url = args.url
    print("Fetching property details\n")
    properties = parse(date)

    if properties!=[]:
        for p in properties:
            print(p + '\n')
    else: print("No new properties")
