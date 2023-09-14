# 경제 부동산 뉴스기사 url


import scrapy
from datetime import date, datetime, timedelta
from user_agent import generate_user_agent
from urllib.parse import urljoin


headers = {'User-Agent': generate_user_agent(os='win', device_type='desktop')}

class DaumNewsSpider(scrapy.Spider):
    name = "daum_news"
    handle_httpstatus_list = [301, 302]


    def __init__(self, *args, **kwargs):
        super(DaumNewsSpider, self).__init__(*args, **kwargs)
        self.base_url = 'https://news.daum.net/breakingnews/economic/stock?page={}&regDate={}'
        self.current_date = date(2023, 9, 12)
        self.end_date = date.today()
        self.current_page = 1
        self.previous_page_content = None


    def start_requests(self):
        #크롤링 시작 url 생성
        date_str = self.current_date.strftime('%Y%m%d')
        url = self.base_url.format(self.current_page, date_str)
        yield scrapy.Request(url=url, callback=self.parse, headers=headers)

    def parse(self, response):
        current_page_content = ''.join(response.css('.box_etc > ul > li > div > strong > a::text').getall())
        # 현재 페이지의 내용과 이전 페이지의 내용이 같으면, 해당 일자 크롤링 종료
        if current_page_content == self.previous_page_content:
            self.current_date += timedelta(days=1)
            # 다음 날짜가 종료 날짜 이전일 경우 다시 parse 함수 실행
            if self.current_date <= self.end_date:
                self.current_page = 1
                date_str = self.current_date.strftime('%Y%m%d')
                url = self.base_url.format(self.current_page, date_str)
                yield scrapy.Request(url=url, callback=self.parse, headers=headers)
            return
        # 현재 페이지의 내용과 이전 페이지의 내용이 다르면, 이전 페이지 내용을 현재 페이지로 업데이트
        else:
            self.previous_page_content = current_page_content

        # 기사 목록이 있을 경우 기사 url 크롤링 진행
        detail_urls = response.xpath('//*[@id="mArticle"]/div[3]/ul/li/div/strong/a/@href').getall()
        for detail_url in detail_urls:
            try:
                yield scrapy.Request(url=detail_url, callback=self.parse_detail, headers=headers)
            except Exception as e:
                print(e)
                continue


        # 다음 페이지로 넘어감
        self.current_page += 1
        date_str = self.current_date.strftime('%Y%m%d')
        next_url = self.base_url.format(self.current_page, date_str)
        yield scrapy.Request(url=next_url, callback=self.parse, headers=headers)

    #상세 뉴스 페이지 내용 크롤링(제목, 날짜, 본문, 신문사)
    def parse_detail(self, response):
        title = response.xpath('//*[@id="mArticle"]/div[1]/h3/text()').get()
        date = response.xpath('//*[@id="mArticle"]/div[1]/div[1]/span[2]/span/text()').get()
        press = response.xpath('//*[@id="kakaoServiceLogo"]/text()').get()
        contents = response.xpath('//*[@id="mArticle"]/div[2]/div[2]/section/p/text()').getall()

        yield {
            'date': date,
            'title': title,
            'press': press,
            'contents': contents
        }



    #def parse(self, response):
    #    items=NewscrawlingItem()
    #    for news_table in response.xpath('//*[@id="mArticle"]/div[3]/ul/li/div'):

            #items['url']=news_table.xpath("strong/a/@href").get()
            
        #//*[@id="mArticle"]/div[3]/ul

class DaumNews(scrapy.Spider):
    name = "daum_detail"
    handle_httpstatus_list = [301, 302]

    def start_requests(self):
        #크롤링 시작 url 생성
        urls=['https://v.daum.net/v/20230913210305194']
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        print(response.xpath('//*[@id="mArticle"]/div[1]/h3/text()').get())
        for i in range(1,5):
            print(response.xpath(f'//*[@id="alex_action_emotion"]/div/div/button[{i}]/span/text()').get())
        
        #print(sticker)
        #for name in sticker:
        #    print(name.text())
