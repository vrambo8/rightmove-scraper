import json
import requests
from lxml import html
from collections import OrderedDict
import argparse
import hashlib


## Search in div class=l-propertySearch-results propertySearch-results
##           div id = l-searchResults
##           div if = property-(property number)
##           div class = propertyCard
##           div class = propertyCard-wrapper
##           div class = propertyCard-images
##           a class = propertyCard-additionalImgs href="/property-to-rent/property-(property number).html"




def parse(username, password):
    for j in range(5):
       # try:
            safe_password = hashlib.sha3_512(password.encode('utf-8')).hexdigest()
            
            payload = {
                'email': username,
                'password': password
                }

    # Use 'with' to ensure the session context is closed after use.
            with requests.Session() as s:
                headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36'}
               # p = s.post('https://www.rightmove.co.uk/login.html', data=payload, headers=headers)
                #print(p.text)
                
                url = "https://www.rightmove.co.uk/property-to-rent/find.html?locationIdentifier=USERDEFINEDAREA%5E%7B%22id%22%3A5287605%7D&maxPrice=2500&savedSearchId=28733232&minBedrooms=4"
                url_result = "https://www.rightmove.co.uk/property-to-rent/property-29888501.html"
                response = s.get(url_result, headers=headers, verify=False)
                parser = html.fromstring(response.text)
                print(response.text)
                json_data_xpath = parser.xpath("//script[@id='cachedResultsJson']//text()")
                raw_json = json.loads(json_data_xpath[0] if json_data_xpath else '')
                property_data = json.loads(raw_json["content"])


                property_info = OrderedDict()
                lists = []
                
                
                print(property_data['legs'])
                #for i in property_data['legs'].keys():

        #except ValueError:
        #        print("Retrying...")
    pass
    #raise ValueError     


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument('username', help="Email")
    argparser.add_argument('password', help="Password")
    #argparser.add_argument('url', help="URL of result list")
    
    args = argparser.parse_args()
    username = args.username
    password = args.password
    #url = args.url
    print("Fetching property details")
    parse(username, password)