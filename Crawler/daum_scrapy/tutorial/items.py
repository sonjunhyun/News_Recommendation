# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field


class NewscrawlingItem(Item):
    id = Field()
    source = Field()
    category = Field()
    title = Field()
    editor = Field()
    created_date = Field()
    updated_date = Field()
    article = Field()
    url=Field()

    def initialize(self, value):
        for keys, _ in self.fields.items():
            self[keys] = value