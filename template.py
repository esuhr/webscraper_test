from bs4 import BeautifulSoup as bs
import requests
import numpy as np
import re
import csv


# adjust these variables for each site
brandName = 'American Crew'
baseURL = 'https://www.americancrew.com/'
categoryURL = 'collections/styling'
productURL = '/products'
urlLength = len(categoryURL + productURL)
maxPages = 6 

pageUrls = []
pageSources = []
allHref = []
productLinks = []
session = requests.Session()

HEADERS = {
    'User-Agent': ('Mozilla/5.0 (X11; Linux x86_64)'
                    'AppleWebKit/537.36 (KHTML, like Gecko)'
                    'Chrome/44.0.2403.157 Safari/537.36'),
    'Accept-Language': 'en-US, en;q=0.5'
}

# iterate through product listing pages
i = 0
while i < maxPages:
    pageUrls.append(baseURL + categoryURL + '?page=' + str(i))
    i += 1

# get page source data
for url in pageUrls:
    pageSources.append(session.get(url, headers=HEADERS))

# get product links from product listing page sources
for source in pageSources:
    soup = bs(source.text, 'html.parser')
    for link in soup.find_all('a'):
        href = link.get('href')
        # check whether link is for product
        if categoryURL + productURL in href:
            allHref.append(href)

# return all unique product links
productHref = np.unique(allHref)

# get product information
products = {}
for link in productHref:
    linkSplit = link.rsplit('/', 1)

    # get product name from url
    productName = linkSplit[len(linkSplit)-1]

    # parse each product page
    url = baseURL + link
    response = session.get(url, headers=HEADERS)
    soup = bs(response.text, 'html.parser')

    # search for ingredient div
    ingreDivs = soup.find_all('div', class_='tt-collapse-content')

    # narrow down list of products to soft products and get product specific info
    for div in ingreDivs:

        # 'aqua' is unique to ingredient div. also delimits soft/hard goods. 'water' doesn't work because it's also present in product description.
        if 'Aqua' in str(div):

            # get inner text of ingredient div
            ingredientString = div.get_text()

            # clean/process text and convert string into list
            ingredientList = ingredientString.strip().replace('\n','').split(',')

            # find price of item
            priceSpan = soup.find('span', class_='new-price')

            # create new product with productName in products dict
            products[productName] = {}
            products[productName]['brand'] = brandName
            products[productName]['name'] = productName
            products[productName]['price'] = priceSpan.get_text()
            products[productName]['ingredients'] = ingredientList

        else:
            pass


# get list of product dicts
productnames = products.keys()
prodDictList = []
for name in productnames:
    prodDictList.append(products[name])

# print to csv
field_names = ['brand', 'name', 'price', 'ingredients']
with open('americancrew.csv', 'w') as f:
    writer = csv.DictWriter(f, fieldnames = field_names)
    writer.writeheader()
    writer.writerows(prodDictList)