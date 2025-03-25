# # Define here the models for your scraped items
# #
# # See documentation in:
# # https://docs.scrapy.org/en/latest/topics/items.html
#
# import scrapy
#
#
# class MyspiderItem(scrapy.Item):
#     # define the fields for your item here like:
#     # name = scrapy.Field()
#     pass
# #

import scrapy

class ItcastItem(scrapy.Item):
   # name = scrapy.Field()
   # title = scrapy.Field()
   # info = scrapy.Field()
   flight_number = scrapy.Field()
   aircraft_type = scrapy.Field()
   departure_time = scrapy.Field()
   arrival_airport = scrapy.Field()
   flight_duration = scrapy.Field()
   price = scrapy.Field()