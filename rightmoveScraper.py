
import requests
import certifi
import urllib3
from collections import OrderedDict
import argparse
import hashlib
from datetime import datetime

from bs4 import BeautifulSoup
import re
import smtplib, ssl

import math
import pickle

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def parse(date, new_properties_only = True):
    
    availability = datetime.strptime(date, '%d/%m/%Y')
    suitable_properties = []
    new_properties = []

    try:
        previous_search = pickle.load(open('rightmove-properties.txt', 'rb'))
    except FileNotFoundError:
        previous_search = []

    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36'}

    url = "https://www.rightmove.co.uk/property-to-rent/find.html?locationIdentifier=USERDEFINEDAREA%5E%7B%22id%22%3A5287605%7D&maxPrice=2500&savedSearchId=28733232&minBedrooms=4"
    print("Sending Requests\n")
    response = requests.get(url, headers=headers, verify=False)

    soup = BeautifulSoup(response.content, 'html.parser')
    result_number = int(
        soup.find('span', {'class': 'searchHeader-resultCount'}).get_text())
    results = str(soup.find('div', class_='l-searchResults'))

    results = re.findall(
        r'/property-to-rent/property-[0-9]*\.html', results, re.M | re.I)
    
    if result_number > 24:
        page_number = math.ceil(result_number/24)

        for i in range(1, page_number+1):
            next_page_url = url + '&index=%d' % 24*i
            next_page_response = requests.get(next_page_url, headers=headers, verify=False)
            next_page_soup = BeautifulSoup(next_page_response.content, 'html.parser')
            next_page_results = str(next_page_soup.find('div', class_='l-searchResults'))
            next_page_results = re.findall(r'/property-to-rent/property-[0-9]*\.html', next_page_results, re.M | re.I)
            results = results + next_page_results

    url_results = list(set(results))
    print("Inspecting Properties\n")
    for u in url_results:
        u = "https://www.rightmove.co.uk/" + u
        result_response = requests.get(u, headers=headers, verify=False)
        result_soup = BeautifulSoup(result_response.content, 'html.parser')
        result_table = result_soup.find('table', {'class': 'table-reset width-100'})
        result_available_date = result_table.find_all('td')[1].get_text()
        try:
            result_available_date = datetime.strptime(result_available_date, '%d/%m/%Y')
            
        except ValueError:
            result_available_date = datetime.now()

        if result_available_date >= availability:
                suitable_properties.append(u)
        
        for s in suitable_properties:
            if s not in previous_search:
                new_properties.append(s)
        
        previous_search = previous_search + new_properties

    with open('rightmove-properties.txt', 'wb') as f:
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

    TEXT = ""

    if properties!=[]:
        for p in properties:
            print(p + '\n')
            TEXT = TEXT + '\n' + str(p)

    else: 
        print("No new properties")
        TEXT = "No new properties"
    
    SUBJECT = "Rightmove New Available Properties"

    message = 'Subject: {}\n\n{}'.format(SUBJECT, TEXT)

    port = 465  # For SSL
    smtp_server = "smtp.gmail.com"
    sender_email = "bob.ross3940@gmail.com"  # Enter your address
    receiver_email = "vittotre@gmail.com"  # Enter receiver address
    password = "Tatotoio3940@"
    

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message)
