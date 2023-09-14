from pathlib import Path

import scrapy


class QuotesSpider(scrapy.Spider):
    name = "test"

    def start_requests(self):
        urls = [
            "https://quotes.toscrape.com/page/1/",
            "https://quotes.toscrape.com/page/2/",
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        page = response.url.split("/")[-2]
        filename = f"quotes-{page}.html"
        Path(filename).write_bytes(response.body)
        self.log(f"Saved file {filename}")

        quotes=response.css(".quote.text::attr(itemporp)").getall()
        print(quotes[0])
        #print(quotes[0].attrib["innerText"])
        data=[" ".join(quotes), '123', '456']
        with open("./result.csv", "a", encoding="utf-8") as f:
            f.write(",".join(data)+"\n") 