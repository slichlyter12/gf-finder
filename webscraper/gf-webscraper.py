import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import csv
import re
import os
import os.path
import hashlib
from time import sleep

# user created
from Restaurant import Restaurant


BASE_URL = "https://www.findmeglutenfree.com/search?a=97330&lat=44.6385&lng=-123.2929&sort=best"
CACHE_DIR = "../cache/"
OUTPUT_DIR = "../output/"


def get_file_path(url, out_dir):
    """computes the correct filename for reading/writing cached content at the specified URL"""
    os.makedirs(out_dir, exist_ok=True)
    filename = re.sub("[^a-zA-Z0-9]+", "-", url)
    if len(filename) > 30:
        filename = filename[0:15] + "..." + filename[-15:]
    url_hash = hashlib.sha224(url.encode("UTF-8")).hexdigest()
    filename = filename + "_" + url_hash + ".html"
    return out_dir + "/" + filename


def retrieve(url: str):

    file_path = get_file_path(url, CACHE_DIR)
    file_path = os.path.abspath(file_path)
    if os.path.exists(file_path) and os.stat(file_path).st_size > 0:
        with open(file_path, 'rb') as f:
            content = f.read()
            soup = BeautifulSoup(content, "lxml", from_encoding="UTF-8")
            if soup is not None:
                return soup

    print("*", url)
    sleep(1)
    r = requests.get(url, verify=False)
    soup = BeautifulSoup(r.text, "lxml")
    with open(file_path, 'wb') as f:
        print("->", file_path)
        html = soup.prettify()
        if len(html) == 0:
            html = " "
        f.write(html.encode("UTF-8"))
    return soup


def get_restaurants():
    results = {}

    def load_detail_links(url):
        soup = retrieve(url)

        detail_links = soup.select(".data-details-url")
        for link in detail_links:
            restaurant_url = urljoin(url, link.get('href'))
            restaurant_title = link.text
            results[restaurant_url] = restaurant_title

        next_link = None
        next_links = soup.select('.pagination ul li a')
        for link in next_links:
            if link.text == "»" and link.get('href') != '#':
                next_link = link
                break
        if next_link is not None:
            next_href = next_link.get("href")
            if next_href is not None:
                next_url = urljoin(url, next_link.get("href"))
                load_detail_links(next_url)

    load_detail_links(BASE_URL)
    return results


def get_restaurant_details(url):
    restaurant = Restaurant()

    soup = retrieve(url)

    # get title
    title = soup.select_one(".biz-name")
    restaurant.title = title.text

    # get url
    restaurant.url = url

    # get rating
    rating = soup.select_one(".rating")
    restaurant.rating = rating.text

    # get votes
    votes = soup.select_one(".votes")
    restaurant.votes = votes.text

    # get tags
    tags = soup.select_one(".biz-tags")
    if tags.text is not None:
        tags = clean_tags(tags.text)
    restaurant.tags = tags

    # get address
    address = soup.select_one("h2")
    address = clean_address(address)
    restaurant.address = address.text

    # get hours
    hours = soup.select(".biz-hours")
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    for index, hour in enumerate(hours):
        hour = clean_hour(hour.text)
        restaurant.add_hour_to_day(hour, days[index])

    return restaurant


def clean_hour(hour):
    clean_hour = re.match("\\n\s+(.*)\\n\s+", hour)
    if clean_hour is not None:
        clean_hour = clean_hour.group(1)
        return clean_hour
    else:
        return hour


def clean_tags(tags):
    if "+" in tags:
        tags = tags.split("+")
        tags = tags[0]
    tags = tags.split(", ")
    return tags

def clean_address(address):
    if "Directions" in address:
        address = address.split("Directions")
        address = address[0]
    return address


restaurants = get_restaurants()
filepath = get_file_path(BASE_URL, OUTPUT_DIR)
with open(filepath + ".csv", 'w+') as outfile:
    fieldnames = ['title', 'url', 'rating', 'votes', 'tags', 'address', 'hours']
    writer = csv.DictWriter(outfile, fieldnames=fieldnames)
    writer.writeheader()

    for link, title in restaurants.items():
        restaurant = get_restaurant_details(link)

        writer.writerow({'title': title,
                         'url': link,
                         'rating': restaurant.rating,
                         'votes': restaurant.votes,
                         'tags': restaurant.tags,
                         'address': restaurant.address,
                         'hours': restaurant.hours})