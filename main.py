import json
import requests
from bs4 import BeautifulSoup
import csv

mapBounds = {
    "west": -96.06292782226564,
    "east": -94.78576717773439,
    "south": 29.356641349441453,
    "north": 30.27646089800536,
}

url = 'https://www.zillow.com/homes/for_sale/house_type/?searchQueryState=%7B%22pagination%22%3A%7B%7D%2C%22usersSearchTerm%22%3A%22Houston%2C%20TX%22%2C%22mapBounds%22%3A%7B%22west%22%3A-96.16867123046876%2C%22east%22%3A-94.89151058593751%2C%22south%22%3A29.313542401165876%2C%22north%22%3A30.23375640913141%7D%2C%22isMapVisible%22%3Atrue%2C%22filterState%22%3A%7B%22sort%22%3A%7B%22value%22%3A%22globalrelevanceex%22%7D%2C%22ah%22%3A%7B%22value%22%3Atrue%7D%2C%22con%22%3A%7B%22value%22%3Afalse%7D%2C%22mf%22%3A%7B%22value%22%3Afalse%7D%2C%22manu%22%3A%7B%22value%22%3Afalse%7D%2C%22land%22%3A%7B%22value%22%3Afalse%7D%2C%22tow%22%3A%7B%22value%22%3Afalse%7D%2C%22apa%22%3A%7B%22value%22%3Afalse%7D%2C%22apco%22%3A%7B%22value%22%3Afalse%7D%7D%2C%22isListVisible%22%3Atrue%7D'
headers = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0"
}

def scrapeZillow(url, lat, lng, pageNum):
    paginationIndex = url.find('pagination')
    mapBoundsIndex = url.find('mapBounds')
    isMapVisibleIndex = url.find('isMapVisible')
    paginatedUrl = url[:paginationIndex+19] + '%22currentPage%22%3A' + str(pageNum) + '%7D%2C%22' + url[paginationIndex+28:mapBoundsIndex] + 'mapBounds%22%3A%7B%22west%22%3A' + str(lng) + '%2C%22east%22%3A' + str(lng+0.1) + '%2C%22south%22%3A' + str(lat-0.1) + '%2C%22north%22%3A' + str(lat) + '%7D%2C%22' + url[isMapVisibleIndex:]
    soup = BeautifulSoup(requests.get(paginatedUrl, headers=headers, allow_redirects=False).content, "html.parser")

    # print(paginatedUrl)

    data = json.loads(
        soup.select_one("script[data-zrr-shared-data-key]")
        .contents[0]
        .strip("!<>-")
    )
    return data


with open('./output.tsv', 'w', newline="") as out_file:
    tsv_writer = csv.writer(out_file, delimiter='\t')
    tsv_writer.writerow(['Zipcode', 'Status', 'Url', 'ImageUrl', 'Price', 'Rent Estimate'])

    for deltaLat in range(13):
        for deltaLng in range(13):
            try:
                totalPages = scrapeZillow(url, mapBounds['north'] - 0.1 * deltaLat, mapBounds['west'] + 0.1 * deltaLng, 1)['cat1']['searchList']['totalPages']
                print(f"searching section ({deltaLat},{deltaLng}): {totalPages} total pages...",)
                for page in range(1, totalPages + 1):
                    print(f'getting data from page {page}')
                    data = scrapeZillow(url, mapBounds['north'] - 0.1 * deltaLat, mapBounds['west'] + 0.1 * deltaLng, page)
                    for result in data["cat1"]['searchResults']['listResults']:
                        try:
                            rentZestimate = result['hdpData']['homeInfo']['rentZestimate']
                        except:
                            rentZestimate = 0
                        tsv_writer.writerow([result['hdpData']['homeInfo']['zipcode'], result['statusText'], result['detailUrl'], result['imgSrc'], result['unformattedPrice'], rentZestimate])
            except:
                print('something went wrong with this section')



# totalPages = scrapeZillow(url, 29.8, -95, 1)['cat1']['searchList']['totalPages']
# print(totalPages)
# data = scrapeZillow(url, mapBounds['north'], mapBounds['west'], 1)
# print(json.dumps(data, indent=4))