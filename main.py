import sys
import argparse
import json
import requests
from bs4 import BeautifulSoup
import csv
import math
import pandas as pd
from redfin import Redfin

def scrapeProxies():
    resp = requests.get('https://free-proxy-list.net/') 
    df = pd.read_html(resp.text)[0]
    return df

# manipulate url to get the listings around the given lat, lng and page
# returns huge json with lots of other useful data that isn't used in the script
def scrapeZillow(url, northLatBound, westLngBound, pageNum):
    # get url's key index's. Used to manipulate url
    paginationIndex = url.find('pagination')
    mapBoundsIndex = url.find('mapBounds')
    isMapVisibleIndex = url.find('isMapVisible')
    
    # manipulate url's page and mapBounds
    print('Getting data by trying proxies...')
    while True:
        for index, row in proxies.iterrows():
            proxy = {
                'http': f'http://{row["IP Address"]}:{row["Port"]}',
                'https': f'http://{row["IP Address"]}:{row["Port"]}',
            }       
            try:
                paginatedUrl = url[:paginationIndex+19] + '%22currentPage%22%3A' + str(pageNum) + '%7D%2C%22' + url[paginationIndex+28:mapBoundsIndex] + 'mapBounds%22%3A%7B%22west%22%3A' + str(westLngBound) + '%2C%22east%22%3A' + str(westLngBound+0.1) + '%2C%22south%22%3A' + str(northLatBound-0.1) + '%2C%22north%22%3A' + str(northLatBound) + '%7D%2C%22' + url[isMapVisibleIndex:]
                soup = BeautifulSoup(requests.get(paginatedUrl, headers=headers, allow_redirects=False, proxies=proxy, timeout=5).content, "html.parser")
                data = json.loads(
                    soup.select_one("script[data-zrr-shared-data-key]")
                    .contents[0]
                    .strip("!<>-")
                )
            except:
                continue
            return data

def scrapeRedfin(address):
    try:
        print(address)
        rf = Redfin()
        response = rf.search(address)
        url = response['payload']['exactMatch']['url']
        initial_info = rf.initial_info(url)
        property_id = initial_info['payload']['propertyId']
        mls_data = rf.below_the_fold(property_id)
        return mls_data
    except:
        print(f'> redfin data could not be retrieved')
        return None

def getRentEstimate(listing):
    # if monthly rent estimate doesn't exist, set rent estimate to 0
    try:
        return listing['hdpData']['homeInfo']['rentZestimate']
    except:
        print("> Rent estimate doesn't exist")
        return 0

def getDaysOnZillow(listing):
    # get days on zillow
    if (listing['variableData']['type'] == 'DAYS_ON'):
        return listing['variableData']['text'].split()[0]
    else:
        print("> Days on Zillow doesn't exist")
        return 0

def getHouseSize(mls_data):
    try:
        return mls_data['payload']['publicRecordsInfo']['basicInfo']['totalSqFt']
    except:
        print("> House size doesn't exist")
        return 0

def getLotSize(mls_data):
    try:
        return mls_data['payload']['publicRecordsInfo']['basicInfo']['lotSqFt']
    except:
        print("> Lot size doesn't exist")
        return 0

def getYearBuilt(mls_data):
    try:
        return mls_data['payload']['publicRecordsInfo']['basicInfo']['yearBuilt']
    except:
        print("> Year built doesn't exist")
        return 0


def getSchoolsRating(mls_data):
    try:
        str = mls_data['payload']['schoolsAndDistrictsInfo']['sectionPreviewText']
        numberFound = False
        numStr = ""
        for c in str:
            if (c.isdigit() or c == '.'):
                numberFound = True
                numStr += c

            if(numberFound and not (c.isdigit() or c == '.')):
                break

        return numStr
    except:
        print('> school rating doesn\"t exist')
        return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", action='store_true', help="Print listing data")
    parser.add_argument("-n", "--north", help="North bound of area you would like to scrape")
    parser.add_argument("-s", "--south", help="South bound of area you would like to scrape")
    parser.add_argument("-e", "--east", help="East bound of area you would like to scrape")
    parser.add_argument("-w", "--west", help="West bound of area you would like to scrape")
    args = parser.parse_args()

    # Houston is default area
    mapBounds = {
        "west": -96.0,
        "east": -94.7,
        "south": 29.2,
        "north": 30.4,
    }
    
    # if a bound is given, all bounds must be given. Otherwise, set mapbounds to given latlngs
    if (args.north or args.south or args.east or args.west):
        try:
            mapBounds = {
                "west": float(args.west),
                "east": float(args.east),
                "south": float(args.south),
                "north": float(args.north),
            }
        except:
            print("Error: North, south, east, west bounds are all required for a region to be set. Bounds must be numbers")
            sys.exit()

        if (mapBounds['north'] > 85 or mapBounds['north'] < -85 or mapBounds['south'] > 85 or mapBounds['south'] < -85):
            print("Error: The north and south bounds must be between -85 and 85")
            sys.exit()
        elif (mapBounds['west'] > 180 or mapBounds['west'] < -180 or mapBounds['east'] > 180 or mapBounds['east'] < -180):
            print("Error: The east and west bounds must be between -180 and 180")
            sys.exit()
        elif (mapBounds['north'] < mapBounds['south']):
            print("Error: The north bound needs to be greater than the south bound")
            sys.exit()
        elif (mapBounds['east'] < mapBounds['west']):
            print("Error: The east bound needs to be greater than the west bound")            
            sys.exit()

    # base url. This url is manipulated to get listing data
    url = 'https://www.zillow.com/homes/for_sale/house_type/?searchQueryState=%7B%22pagination%22%3A%7B%7D%2C%22usersSearchTerm%22%3A%22Houston%2C%20TX%22%2C%22mapBounds%22%3A%7B%22west%22%3A-96.16867123046876%2C%22east%22%3A-94.89151058593751%2C%22south%22%3A29.313542401165876%2C%22north%22%3A30.23375640913141%7D%2C%22isMapVisible%22%3Atrue%2C%22filterState%22%3A%7B%22sort%22%3A%7B%22value%22%3A%22globalrelevanceex%22%7D%2C%22ah%22%3A%7B%22value%22%3Atrue%7D%2C%22con%22%3A%7B%22value%22%3Afalse%7D%2C%22mf%22%3A%7B%22value%22%3Afalse%7D%2C%22manu%22%3A%7B%22value%22%3Afalse%7D%2C%22land%22%3A%7B%22value%22%3Afalse%7D%2C%22tow%22%3A%7B%22value%22%3Afalse%7D%2C%22apa%22%3A%7B%22value%22%3Afalse%7D%2C%22apco%22%3A%7B%22value%22%3Afalse%7D%7D%2C%22isListVisible%22%3Atrue%7D'
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0"
    }

    # scrape Zillow
    with open('./output.tsv', 'w', newline="") as out_file:
        tsv_writer = csv.writer(out_file, delimiter='\t')         # init file writer
        tsv_writer.writerow([ 'Days on Zillow', 'Status', 'Url', 'ImageUrl', 'Price', 'Zipcode', 'Address', 'House Size', 'Lot Size', 'Year Built', 'Schools Rating', 'Rent Estimate', 'Rent to Price'])         # create header row in tsv file


        # get number of times 0.1 latitudes can go between the north and south map bounds
        rows = (mapBounds['north'] - mapBounds['south']) / 0.1
        cols = (mapBounds['east'] - mapBounds['west']) / 0.1
        rows = math.ceil(rows)
        cols = math.ceil(cols)
        print(f"{rows} rows & {cols} cols")

        for deltaLat in range(rows):
            for deltaLng in range(cols):
                proxies = scrapeProxies()

                # get north and west bound in this map section
                northLatBound = mapBounds['north'] - 0.1 * deltaLat
                westLngBound = mapBounds['west'] + 0.1 * deltaLng

                print(f"searching section ({deltaLat},{deltaLng})",)
                pg1_listings = scrapeZillow(url, northLatBound, westLngBound, 1)
                totalPages = pg1_listings['cat1']['searchList']['totalPages']  # get total pages in this map section
                print(f"{totalPages} total pages...")
                # loop each page
                for page in range(1, totalPages + 1):
                    print(f'getting data from page {page}')
                    if page == 1:
                        listings = pg1_listings
                    else:
                        listings = scrapeZillow(url, northLatBound, westLngBound, page)

                    # loop each listing
                    for listing in listings["cat1"]['searchResults']['listResults']:

                        homeInfo = listing['hdpData']['homeInfo']

                        # write listing data to tsv file
                        numDays = getDaysOnZillow(listing)
                        statusText = listing['statusText']
                        zillowUrl = listing['detailUrl']
                        image = listing['imgSrc']
                        price = listing['unformattedPrice']
                        zip = homeInfo['zipcode']
                        address = f"{homeInfo['streetAddress']}, {homeInfo['city']}, {homeInfo['state']} {homeInfo['zipcode']}"
                        redfinData = scrapeRedfin(address)
                        houseSize = getHouseSize(redfinData)
                        lotSize = getLotSize(redfinData)
                        yearBuilt = getYearBuilt(redfinData)
                        schoolsRating = getSchoolsRating(redfinData)
                        rentZestimate = getRentEstimate(listing)
                        rentToPrice = rentZestimate / price
                        tsv_writer.writerow([numDays, statusText, zillowUrl, image, price, zip, address, houseSize, lotSize, yearBuilt, schoolsRating, rentZestimate, rentToPrice])
