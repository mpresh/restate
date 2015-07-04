# -*- coding: utf-8 -*-
import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
import re

import geopy
from geopy.geocoders import Nominatim


def convert_map_url_to_zip(map_url):
    raw = map_url.split("/")[-1]
    raw = raw.replace("@", "")
    raw = raw.replace("z", "")
    values = raw.split(",")
    lat = values[0]
    long = values[1]

    geolocator = Nominatim()
    coordinates = "{}, {}".format(lat, long)
    location = geolocator.reverse(coordinates)

    address = location.address
    mo = re.findall("(\d\d\d\d\d)", address)
    if mo:
        zipcode = mo[-1]
    else:
        mo = None

    return address, zipcode

convert_map_url_to_zip("https://maps.google.com/maps/preview/@42.417300,-71.108700,16z")

class CraigItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    name = scrapy.Field()
    price = scrapy.Field()
    bedrooms = scrapy.Field()
    bathrooms = scrapy.Field()
    square_feet = scrapy.Field()
    town = scrapy.Field()
    description = scrapy.Field()
    link = scrapy.Field()    
    display_date = scrapy.Field()
    address = scrapy.Field()
    zipcode = scrapy.Field()
    city = scrapy.Field()
    state = scrapy.Field()


class BostonRealEstateSpider(CrawlSpider):
    name = "boston_real_estate"
    allowed_domains = ["boston.craigslist.org"]
    start_urls = (
        'http://boston.craigslist.org/search/rea/',
    )

    rules = (
        Rule(LinkExtractor(allow=('.html', )), callback='parse_item'),
    )
    

    def parse_item(self, response):
        self.logger.info('Hi, this is an item page! %s', response.url)
        item = CraigItem()
        item['link'] = response.url

        title_pattern = 'meta property="og:title" content="(.*?)"'
        mo = re.search(title_pattern, response.body)
        if mo:
            item["name"] = mo.group(1)

        display_date_pattern = 'time datetime="(.*?)"'
        mo = re.search(display_date_pattern, response.body)
        if mo:
            item["display_date"] = mo.group(1)

        price_pattern = '<span class="price">(.*?)</span>'
        mo = re.search(price_pattern, response.body)
        if mo:
            item["price"] = mo.group(1).replace("$", "")

        housing_pattern = '<span class="housing">(.*?)</span>'
        mo = re.search(housing_pattern, response.body)
        if mo:
            housing = mo.group(1)
            print("HOUSING", housing)

            mo = re.search("(\d*?)br", housing)
            if mo:
                item["bedrooms"] = mo.group(1)

            mo = re.search("(\d*?)ba", housing)
            if mo:
                item["bathrooms"] = mo.group(1)

            mo = re.search("(\d*?)ft", housing)
            if mo:
                item["square_feet"] = mo.group(1)

        map_url_pattern = '(https://maps.google.com/maps/preview.*)"'
        mo = re.search(map_url_pattern, response.body)
        if mo:
            address, zipcode = convert_map_url_to_zip(mo.group(1))
            item["address"] = address
            item["zipcode"] = zipcode

            if zipcode:
                from pyzipcode import ZipCodeDatabase
                zcdb = ZipCodeDatabase()
                zipcode = zcdb[zipcode]
            item["city"] = zipcode.city
            item["state"] = zipcode.state

        #item['id'] = response.xpath('//td[@id="item_id"]/text()').re(r'ID: (\d+)')
        #item['name'] = response.xpath('//td[@id="item_name"]/text()').extract()
        #item['description'] = response.xpath('//td[@id="item_description"]/text()').extract()
        #return item
        return item
