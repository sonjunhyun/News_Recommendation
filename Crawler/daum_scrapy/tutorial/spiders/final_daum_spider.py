import scrapy
from datetime import date, timedelta
from user_agent import generate_user_agent
import requests
import json
import pandas as pd


headers = {'User-Agent': generate_user_agent(os='win', device_type='desktop')}

class DaumFinanceSpider(scrapy.Spider):
    name = "daum_finance"
    handle_httpstatus_list = [301, 302]


    def __init__(self, *args, **kwargs):
        super(DaumFinanceSpider, self).__init__(*args, **kwargs)
        self.base_url = 'https://news.daum.net/breakingnews/economic/finance?page={}&regDate={}'
        self.start_date = date(2023, 9, 13)
        self.end_date = self.start_date-pd.DateOffset(year=1)
        self.current_page = 1
        self.previous_page_content = None


    def start_requests(self):
        #크롤링 시작 url 생성
        date_str = self.start_date.strftime('%Y%m%d')
        url = self.base_url.format(self.current_page, date_str)
        yield scrapy.Request(url=url, callback=self.parse, headers=headers)

    def parse(self, response):
        current_page_content = ''.join(response.css('.box_etc > ul > li > div > strong > a::text').getall())
        # 현재 페이지의 내용과 이전 페이지의 내용이 같으면, 해당 일자 크롤링 종료
        if current_page_content == self.previous_page_content:
            self.start_date -= timedelta(days=1)
            # 다음 날짜가 종료 날짜 이전일 경우 다시 parse 함수 실행
            if self.start_date >= self.end_date:
                self.current_page = 1
                date_str = self.start_date.strftime('%Y%m%d')
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
        date_str = self.start_date.strftime('%Y%m%d')
        next_url = self.base_url.format(self.current_page, date_str)
        yield scrapy.Request(url=next_url, callback=self.parse, headers=headers)

    #상세 뉴스 페이지 내용 크롤링(url, 날짜, 수정날짜, 제목, 기자, 신문사, 본문, 스티커)
    def parse_detail(self, response):
        current_url=response.url
        article_id=current_url.split("/")[-1]
        s_header = {"User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36",
                    "referer": current_url,
                    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmb3J1bV9rZXkiOiJuZXdzIiwidXNlcl92aWV3Ijp7ImlkIjo4NDQ5Mjc0NiwiaWNvbiI6Imh0dHBzOi8vdDEuZGF1bWNkbi5uZXQvcHJvZmlsZS84WWJFVEhhcEpHYzAiLCJwcm92aWRlcklkIjoiREFVTSIsImRpc3BsYXlOYW1lIjoi67CV7IiY7KCVIn0sImdyYW50X3R5cGUiOiJhbGV4X2NyZWRlbnRpYWxzIiwic2NvcGUiOltdLCJleHAiOjE2OTQ3MTU4NTIsImF1dGhvcml0aWVzIjpbIlJPTEVfSU5URUdSQVRFRCIsIlJPTEVfREFVTSIsIlJPTEVfSURFTlRJRklFRCIsIlJPTEVfVVNFUiJdLCJqdGkiOiIwOTM2ZTRjZC1kNTczLTQzMzItYTkwZi0xYmRjMTk2NWViY2QiLCJmb3J1bV9pZCI6LTk5LCJjbGllbnRfaWQiOiIyNkJYQXZLbnk1V0Y1WjA5bHI1azc3WTgifQ.prTC8lYD7WMdr_Qglv7DimBEy3kfYYph6Twoy16ZmTI"
                    }
        res=requests.get(url="https://action.daum.net/apis/v1/reactions/home?itemKey={}".format(article_id), headers=s_header)
        sticker={key: value for key, value in json.loads(res.text)["item"]["stats"].items() if key in ["LIKE","SAD", "ANGRY", "RECOMMEND", "IMPRESS"]}
        
        title = response.xpath('//*[@id="mArticle"]/div[1]/h3/text()').get()
        reporter = "".join([text for text in response.css('.txt_info::text').getall() if text not in ["입력 ", "수정 ", "개"]])
        date = response.css('.num_date::text').get()
        change_date="".join([c_date for c_date in response.css(".num_date::text").getall() if c_date != date])
        press = response.xpath('//*[@id="kakaoServiceLogo"]/text()').get()
        contents = " ".join([sent.strip() for sent in response.xpath('//*[@id="mArticle"]/div[2]/div/section/p/text()').getall()])


        yield {
            'Url' : current_url,
            'date': date,
            'change_date' : change_date,
            'title': title,
            'reporter':reporter,
            'press': press,
            'contents': contents,
            'sticker' : sticker
        }

class DaumIndustrySpider(scrapy.Spider):
    name = "daum_industry"
    handle_httpstatus_list = [301, 302]


    def __init__(self, *args, **kwargs):
        super(DaumIndustrySpider, self).__init__(*args, **kwargs)
        self.base_url = 'https://news.daum.net/breakingnews/economic/industry?page={}&regDate={}'
        self.start_date = date(2023, 9, 13)
        self.end_date = self.start_date-pd.DateOffset(year=1)
        self.current_page = 1
        self.previous_page_content = None


    def start_requests(self):
        #크롤링 시작 url 생성
        date_str = self.start_date.strftime('%Y%m%d')
        url = self.base_url.format(self.current_page, date_str)
        yield scrapy.Request(url=url, callback=self.parse, headers=headers)

    def parse(self, response):
        current_page_content = ''.join(response.css('.box_etc > ul > li > div > strong > a::text').getall())
        # 현재 페이지의 내용과 이전 페이지의 내용이 같으면, 해당 일자 크롤링 종료
        if current_page_content == self.previous_page_content:
            self.start_date -= timedelta(days=1)
            # 다음 날짜가 종료 날짜 이전일 경우 다시 parse 함수 실행
            if self.start_date >= self.end_date:
                self.current_page = 1
                date_str = self.start_date.strftime('%Y%m%d')
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
        date_str = self.start_date.strftime('%Y%m%d')
        next_url = self.base_url.format(self.current_page, date_str)
        yield scrapy.Request(url=next_url, callback=self.parse, headers=headers)

    #상세 뉴스 페이지 내용 크롤링(url, 날짜, 수정날짜, 제목, 기자, 신문사, 본문, 스티커)
    def parse_detail(self, response):
        current_url=response.url
        article_id=current_url.split("/")[-1]
        s_header = {"User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36",
                    "referer": current_url,
                    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmb3J1bV9rZXkiOiJuZXdzIiwidXNlcl92aWV3Ijp7ImlkIjo4NDQ5Mjc0NiwiaWNvbiI6Imh0dHBzOi8vdDEuZGF1bWNkbi5uZXQvcHJvZmlsZS84WWJFVEhhcEpHYzAiLCJwcm92aWRlcklkIjoiREFVTSIsImRpc3BsYXlOYW1lIjoi67CV7IiY7KCVIn0sImdyYW50X3R5cGUiOiJhbGV4X2NyZWRlbnRpYWxzIiwic2NvcGUiOltdLCJleHAiOjE2OTQ3MTU4NTIsImF1dGhvcml0aWVzIjpbIlJPTEVfSU5URUdSQVRFRCIsIlJPTEVfREFVTSIsIlJPTEVfSURFTlRJRklFRCIsIlJPTEVfVVNFUiJdLCJqdGkiOiIwOTM2ZTRjZC1kNTczLTQzMzItYTkwZi0xYmRjMTk2NWViY2QiLCJmb3J1bV9pZCI6LTk5LCJjbGllbnRfaWQiOiIyNkJYQXZLbnk1V0Y1WjA5bHI1azc3WTgifQ.prTC8lYD7WMdr_Qglv7DimBEy3kfYYph6Twoy16ZmTI"
                    }
        res=requests.get(url="https://action.daum.net/apis/v1/reactions/home?itemKey={}".format(article_id), headers=s_header)
        sticker={key: value for key, value in json.loads(res.text)["item"]["stats"].items() if key in ["LIKE","SAD", "ANGRY", "RECOMMEND", "IMPRESS"]}
        
        title = response.xpath('//*[@id="mArticle"]/div[1]/h3/text()').get()
        reporter = "".join([text for text in response.css('.txt_info::text').getall() if text not in ["입력 ", "수정 ", "개"]])
        date = response.css('.num_date::text').get()
        change_date="".join([c_date for c_date in response.css(".num_date::text").getall() if c_date != date])
        press = response.xpath('//*[@id="kakaoServiceLogo"]/text()').get()
        contents = " ".join([sent.strip() for sent in response.xpath('//*[@id="mArticle"]/div[2]/div/section/p/text()').getall()])


        yield {
            'Url' : current_url,
            'date': date,
            'change_date' : change_date,
            'title': title,
            'reporter':reporter,
            'press': press,
            'contents': contents,
            'sticker' : sticker
        }

class DaumOthersSpider(scrapy.Spider):
    name = "daum_others"
    handle_httpstatus_list = [301, 302]


    def __init__(self, *args, **kwargs):
        super(DaumOthersSpider, self).__init__(*args, **kwargs)
        self.base_url = 'https://news.daum.net/breakingnews/economic/others?page={}&regDate={}'
        self.start_date = date(2023, 9, 13)
        self.end_date = self.start_date-pd.DateOffset(year=1)
        self.current_page = 1
        self.previous_page_content = None


    def start_requests(self):
        #크롤링 시작 url 생성
        date_str = self.start_date.strftime('%Y%m%d')
        url = self.base_url.format(self.current_page, date_str)
        yield scrapy.Request(url=url, callback=self.parse, headers=headers)

    def parse(self, response):
        current_page_content = ''.join(response.css('.box_etc > ul > li > div > strong > a::text').getall())
        # 현재 페이지의 내용과 이전 페이지의 내용이 같으면, 해당 일자 크롤링 종료
        if current_page_content == self.previous_page_content:
            self.start_date -= timedelta(days=1)
            # 다음 날짜가 종료 날짜 이전일 경우 다시 parse 함수 실행
            if self.start_date >= self.end_date:
                self.current_page = 1
                date_str = self.start_date.strftime('%Y%m%d')
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
        date_str = self.start_date.strftime('%Y%m%d')
        next_url = self.base_url.format(self.current_page, date_str)
        yield scrapy.Request(url=next_url, callback=self.parse, headers=headers)

    #상세 뉴스 페이지 내용 크롤링(url, 날짜, 수정날짜, 제목, 기자, 신문사, 본문, 스티커)
    def parse_detail(self, response):
        current_url=response.url
        article_id=current_url.split("/")[-1]
        s_header = {"User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36",
                    "referer": current_url,
                    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmb3J1bV9rZXkiOiJuZXdzIiwidXNlcl92aWV3Ijp7ImlkIjo4NDQ5Mjc0NiwiaWNvbiI6Imh0dHBzOi8vdDEuZGF1bWNkbi5uZXQvcHJvZmlsZS84WWJFVEhhcEpHYzAiLCJwcm92aWRlcklkIjoiREFVTSIsImRpc3BsYXlOYW1lIjoi67CV7IiY7KCVIn0sImdyYW50X3R5cGUiOiJhbGV4X2NyZWRlbnRpYWxzIiwic2NvcGUiOltdLCJleHAiOjE2OTQ3MTU4NTIsImF1dGhvcml0aWVzIjpbIlJPTEVfSU5URUdSQVRFRCIsIlJPTEVfREFVTSIsIlJPTEVfSURFTlRJRklFRCIsIlJPTEVfVVNFUiJdLCJqdGkiOiIwOTM2ZTRjZC1kNTczLTQzMzItYTkwZi0xYmRjMTk2NWViY2QiLCJmb3J1bV9pZCI6LTk5LCJjbGllbnRfaWQiOiIyNkJYQXZLbnk1V0Y1WjA5bHI1azc3WTgifQ.prTC8lYD7WMdr_Qglv7DimBEy3kfYYph6Twoy16ZmTI"
                    }
        res=requests.get(url="https://action.daum.net/apis/v1/reactions/home?itemKey={}".format(article_id), headers=s_header)
        sticker={key: value for key, value in json.loads(res.text)["item"]["stats"].items() if key in ["LIKE","SAD", "ANGRY", "RECOMMEND", "IMPRESS"]}
        
        title = response.xpath('//*[@id="mArticle"]/div[1]/h3/text()').get()
        reporter = "".join([text for text in response.css('.txt_info::text').getall() if text not in ["입력 ", "수정 ", "개"]])
        date = response.css('.num_date::text').get()
        change_date="".join([c_date for c_date in response.css(".num_date::text").getall() if c_date != date])
        press = response.xpath('//*[@id="kakaoServiceLogo"]/text()').get()
        contents = " ".join([sent.strip() for sent in response.xpath('//*[@id="mArticle"]/div[2]/div/section/p/text()').getall()])


        yield {
            'Url' : current_url,
            'date': date,
            'change_date' : change_date,
            'title': title,
            'reporter':reporter,
            'press': press,
            'contents': contents,
            'sticker' : sticker
        }

class DaumEmploySpider(scrapy.Spider):
    name = "daum_employ"
    handle_httpstatus_list = [301, 302]


    def __init__(self, *args, **kwargs):
        super(DaumEmploySpider, self).__init__(*args, **kwargs)
        self.base_url = 'https://news.daum.net/breakingnews/economic/employ?page={}&regDate={}'
        self.start_date = date(2023, 9, 13)
        self.end_date = self.start_date-pd.DateOffset(year=1)
        self.current_page = 1
        self.previous_page_content = None


    def start_requests(self):
        #크롤링 시작 url 생성
        date_str = self.start_date.strftime('%Y%m%d')
        url = self.base_url.format(self.current_page, date_str)
        yield scrapy.Request(url=url, callback=self.parse, headers=headers)

    def parse(self, response):
        current_page_content = ''.join(response.css('.box_etc > ul > li > div > strong > a::text').getall())
        # 현재 페이지의 내용과 이전 페이지의 내용이 같으면, 해당 일자 크롤링 종료
        if current_page_content == self.previous_page_content:
            self.start_date -= timedelta(days=1)
            # 다음 날짜가 종료 날짜 이전일 경우 다시 parse 함수 실행
            if self.start_date >= self.end_date:
                self.current_page = 1
                date_str = self.start_date.strftime('%Y%m%d')
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
        date_str = self.start_date.strftime('%Y%m%d')
        next_url = self.base_url.format(self.current_page, date_str)
        yield scrapy.Request(url=next_url, callback=self.parse, headers=headers)

    #상세 뉴스 페이지 내용 크롤링(url, 날짜, 수정날짜, 제목, 기자, 신문사, 본문, 스티커)
    def parse_detail(self, response):
        current_url=response.url
        article_id=current_url.split("/")[-1]
        s_header = {"User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36",
                    "referer": current_url,
                    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmb3J1bV9rZXkiOiJuZXdzIiwidXNlcl92aWV3Ijp7ImlkIjo4NDQ5Mjc0NiwiaWNvbiI6Imh0dHBzOi8vdDEuZGF1bWNkbi5uZXQvcHJvZmlsZS84WWJFVEhhcEpHYzAiLCJwcm92aWRlcklkIjoiREFVTSIsImRpc3BsYXlOYW1lIjoi67CV7IiY7KCVIn0sImdyYW50X3R5cGUiOiJhbGV4X2NyZWRlbnRpYWxzIiwic2NvcGUiOltdLCJleHAiOjE2OTQ3MTU4NTIsImF1dGhvcml0aWVzIjpbIlJPTEVfSU5URUdSQVRFRCIsIlJPTEVfREFVTSIsIlJPTEVfSURFTlRJRklFRCIsIlJPTEVfVVNFUiJdLCJqdGkiOiIwOTM2ZTRjZC1kNTczLTQzMzItYTkwZi0xYmRjMTk2NWViY2QiLCJmb3J1bV9pZCI6LTk5LCJjbGllbnRfaWQiOiIyNkJYQXZLbnk1V0Y1WjA5bHI1azc3WTgifQ.prTC8lYD7WMdr_Qglv7DimBEy3kfYYph6Twoy16ZmTI"
                    }
        res=requests.get(url="https://action.daum.net/apis/v1/reactions/home?itemKey={}".format(article_id), headers=s_header)
        sticker={key: value for key, value in json.loads(res.text)["item"]["stats"].items() if key in ["LIKE","SAD", "ANGRY", "RECOMMEND", "IMPRESS"]}
        
        title = response.xpath('//*[@id="mArticle"]/div[1]/h3/text()').get()
        reporter = "".join([text for text in response.css('.txt_info::text').getall() if text not in ["입력 ", "수정 ", "개"]])
        date = response.css('.num_date::text').get()
        change_date="".join([c_date for c_date in response.css(".num_date::text").getall() if c_date != date])
        press = response.xpath('//*[@id="kakaoServiceLogo"]/text()').get()
        contents = " ".join([sent.strip() for sent in response.xpath('//*[@id="mArticle"]/div[2]/div/section/p/text()').getall()])


        yield {
            'Url' : current_url,
            'date': date,
            'change_date' : change_date,
            'title': title,
            'reporter':reporter,
            'press': press,
            'contents': contents,
            'sticker' : sticker
        }

class DaumAutosSpider(scrapy.Spider):
    name = "daum_autos"
    handle_httpstatus_list = [301, 302]


    def __init__(self, *args, **kwargs):
        super(DaumAutosSpider, self).__init__(*args, **kwargs)
        self.base_url = 'https://news.daum.net/breakingnews/economic/autos?page={}&regDate={}'
        self.start_date = date(2023, 9, 13)
        self.end_date = self.start_date-pd.DateOffset(year=1)
        self.current_page = 1
        self.previous_page_content = None


    def start_requests(self):
        #크롤링 시작 url 생성
        date_str = self.start_date.strftime('%Y%m%d')
        url = self.base_url.format(self.current_page, date_str)
        yield scrapy.Request(url=url, callback=self.parse, headers=headers)

    def parse(self, response):
        current_page_content = ''.join(response.css('.box_etc > ul > li > div > strong > a::text').getall())
        # 현재 페이지의 내용과 이전 페이지의 내용이 같으면, 해당 일자 크롤링 종료
        if current_page_content == self.previous_page_content:
            self.start_date -= timedelta(days=1)
            # 다음 날짜가 종료 날짜 이전일 경우 다시 parse 함수 실행
            if self.start_date >= self.end_date:
                self.current_page = 1
                date_str = self.start_date.strftime('%Y%m%d')
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
        date_str = self.start_date.strftime('%Y%m%d')
        next_url = self.base_url.format(self.current_page, date_str)
        yield scrapy.Request(url=next_url, callback=self.parse, headers=headers)

    #상세 뉴스 페이지 내용 크롤링(url, 날짜, 수정날짜, 제목, 기자, 신문사, 본문, 스티커)
    def parse_detail(self, response):
        current_url=response.url
        article_id=current_url.split("/")[-1]
        s_header = {"User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36",
                    "referer": current_url,
                    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmb3J1bV9rZXkiOiJuZXdzIiwidXNlcl92aWV3Ijp7ImlkIjo4NDQ5Mjc0NiwiaWNvbiI6Imh0dHBzOi8vdDEuZGF1bWNkbi5uZXQvcHJvZmlsZS84WWJFVEhhcEpHYzAiLCJwcm92aWRlcklkIjoiREFVTSIsImRpc3BsYXlOYW1lIjoi67CV7IiY7KCVIn0sImdyYW50X3R5cGUiOiJhbGV4X2NyZWRlbnRpYWxzIiwic2NvcGUiOltdLCJleHAiOjE2OTQ3MTU4NTIsImF1dGhvcml0aWVzIjpbIlJPTEVfSU5URUdSQVRFRCIsIlJPTEVfREFVTSIsIlJPTEVfSURFTlRJRklFRCIsIlJPTEVfVVNFUiJdLCJqdGkiOiIwOTM2ZTRjZC1kNTczLTQzMzItYTkwZi0xYmRjMTk2NWViY2QiLCJmb3J1bV9pZCI6LTk5LCJjbGllbnRfaWQiOiIyNkJYQXZLbnk1V0Y1WjA5bHI1azc3WTgifQ.prTC8lYD7WMdr_Qglv7DimBEy3kfYYph6Twoy16ZmTI"
                    }
        res=requests.get(url="https://action.daum.net/apis/v1/reactions/home?itemKey={}".format(article_id), headers=s_header)
        sticker={key: value for key, value in json.loads(res.text)["item"]["stats"].items() if key in ["LIKE","SAD", "ANGRY", "RECOMMEND", "IMPRESS"]}
        
        title = response.xpath('//*[@id="mArticle"]/div[1]/h3/text()').get()
        reporter = "".join([text for text in response.css('.txt_info::text').getall() if text not in ["입력 ", "수정 ", "개"]])
        date = response.css('.num_date::text').get()
        change_date="".join([c_date for c_date in response.css(".num_date::text").getall() if c_date != date])
        press = response.xpath('//*[@id="kakaoServiceLogo"]/text()').get()
        contents = " ".join([sent.strip() for sent in response.xpath('//*[@id="mArticle"]/div[2]/div/section/p/text()').getall()])


        yield {
            'Url' : current_url,
            'date': date,
            'change_date' : change_date,
            'title': title,
            'reporter':reporter,
            'press': press,
            'contents': contents,
            'sticker' : sticker
        }

class DaumStockSpider(scrapy.Spider):
    name = "daum_stock"
    handle_httpstatus_list = [301, 302]


    def __init__(self, *args, **kwargs):
        super(DaumStockSpider, self).__init__(*args, **kwargs)
        self.base_url = 'https://news.daum.net/breakingnews/economic/stock?page={}&regDate={}'
        self.start_date = date(2023, 9, 13)
        self.end_date = self.start_date-pd.DateOffset(year=1)
        self.current_page = 1
        self.previous_page_content = None


    def start_requests(self):
        #크롤링 시작 url 생성
        date_str = self.start_date.strftime('%Y%m%d')
        url = self.base_url.format(self.current_page, date_str)
        yield scrapy.Request(url=url, callback=self.parse, headers=headers)

    def parse(self, response):
        current_page_content = ''.join(response.css('.box_etc > ul > li > div > strong > a::text').getall())
        # 현재 페이지의 내용과 이전 페이지의 내용이 같으면, 해당 일자 크롤링 종료
        if current_page_content == self.previous_page_content:
            self.start_date -= timedelta(days=1)
            # 다음 날짜가 종료 날짜 이전일 경우 다시 parse 함수 실행
            if self.start_date >= self.end_date:
                self.current_page = 1
                date_str = self.start_date.strftime('%Y%m%d')
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
        date_str = self.start_date.strftime('%Y%m%d')
        next_url = self.base_url.format(self.current_page, date_str)
        yield scrapy.Request(url=next_url, callback=self.parse, headers=headers)

    #상세 뉴스 페이지 내용 크롤링(url, 날짜, 수정날짜, 제목, 기자, 신문사, 본문, 스티커)
    def parse_detail(self, response):
        current_url=response.url
        article_id=current_url.split("/")[-1]
        s_header = {"User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36",
                    "referer": current_url,
                    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmb3J1bV9rZXkiOiJuZXdzIiwidXNlcl92aWV3Ijp7ImlkIjo4NDQ5Mjc0NiwiaWNvbiI6Imh0dHBzOi8vdDEuZGF1bWNkbi5uZXQvcHJvZmlsZS84WWJFVEhhcEpHYzAiLCJwcm92aWRlcklkIjoiREFVTSIsImRpc3BsYXlOYW1lIjoi67CV7IiY7KCVIn0sImdyYW50X3R5cGUiOiJhbGV4X2NyZWRlbnRpYWxzIiwic2NvcGUiOltdLCJleHAiOjE2OTQ3MTU4NTIsImF1dGhvcml0aWVzIjpbIlJPTEVfSU5URUdSQVRFRCIsIlJPTEVfREFVTSIsIlJPTEVfSURFTlRJRklFRCIsIlJPTEVfVVNFUiJdLCJqdGkiOiIwOTM2ZTRjZC1kNTczLTQzMzItYTkwZi0xYmRjMTk2NWViY2QiLCJmb3J1bV9pZCI6LTk5LCJjbGllbnRfaWQiOiIyNkJYQXZLbnk1V0Y1WjA5bHI1azc3WTgifQ.prTC8lYD7WMdr_Qglv7DimBEy3kfYYph6Twoy16ZmTI"
                    }
        res=requests.get(url="https://action.daum.net/apis/v1/reactions/home?itemKey={}".format(article_id), headers=s_header)
        sticker={key: value for key, value in json.loads(res.text)["item"]["stats"].items() if key in ["LIKE","SAD", "ANGRY", "RECOMMEND", "IMPRESS"]}
        
        title = response.xpath('//*[@id="mArticle"]/div[1]/h3/text()').get()
        reporter = "".join([text for text in response.css('.txt_info::text').getall() if text not in ["입력 ", "수정 ", "개"]])
        date = response.css('.num_date::text').get()
        change_date="".join([c_date for c_date in response.css(".num_date::text").getall() if c_date != date])
        press = response.xpath('//*[@id="kakaoServiceLogo"]/text()').get()
        contents = " ".join([sent.strip() for sent in response.xpath('//*[@id="mArticle"]/div[2]/div/section/p/text()').getall()])


        yield {
            'Url' : current_url,
            'date': date,
            'change_date' : change_date,
            'title': title,
            'reporter':reporter,
            'press': press,
            'contents': contents,
            'sticker' : sticker
        }

class DaumMarketSpider(scrapy.Spider):
    name = "daum_market"
    handle_httpstatus_list = [301, 302]


    def __init__(self, *args, **kwargs):
        super(DaumMarketSpider, self).__init__(*args, **kwargs)
        self.base_url = 'https://news.daum.net/breakingnews/economic/stock/market?page={}&regDate={}'
        self.start_date = date(2023, 9, 13)
        self.end_date = self.start_date-pd.DateOffset(year=1)
        self.current_page = 1
        self.previous_page_content = None


    def start_requests(self):
        #크롤링 시작 url 생성
        date_str = self.start_date.strftime('%Y%m%d')
        url = self.base_url.format(self.current_page, date_str)
        yield scrapy.Request(url=url, callback=self.parse, headers=headers)

    def parse(self, response):
        current_page_content = ''.join(response.css('.box_etc > ul > li > div > strong > a::text').getall())
        # 현재 페이지의 내용과 이전 페이지의 내용이 같으면, 해당 일자 크롤링 종료
        if current_page_content == self.previous_page_content:
            self.start_date -= timedelta(days=1)
            # 다음 날짜가 종료 날짜 이전일 경우 다시 parse 함수 실행
            if self.start_date >= self.end_date:
                self.current_page = 1
                date_str = self.start_date.strftime('%Y%m%d')
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
        date_str = self.start_date.strftime('%Y%m%d')
        next_url = self.base_url.format(self.current_page, date_str)
        yield scrapy.Request(url=next_url, callback=self.parse, headers=headers)

    #상세 뉴스 페이지 내용 크롤링(url, 날짜, 수정날짜, 제목, 기자, 신문사, 본문, 스티커)
    def parse_detail(self, response):
        current_url=response.url
        article_id=current_url.split("/")[-1]
        s_header = {"User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36",
                    "referer": current_url,
                    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmb3J1bV9rZXkiOiJuZXdzIiwidXNlcl92aWV3Ijp7ImlkIjo4NDQ5Mjc0NiwiaWNvbiI6Imh0dHBzOi8vdDEuZGF1bWNkbi5uZXQvcHJvZmlsZS84WWJFVEhhcEpHYzAiLCJwcm92aWRlcklkIjoiREFVTSIsImRpc3BsYXlOYW1lIjoi67CV7IiY7KCVIn0sImdyYW50X3R5cGUiOiJhbGV4X2NyZWRlbnRpYWxzIiwic2NvcGUiOltdLCJleHAiOjE2OTQ3MTU4NTIsImF1dGhvcml0aWVzIjpbIlJPTEVfSU5URUdSQVRFRCIsIlJPTEVfREFVTSIsIlJPTEVfSURFTlRJRklFRCIsIlJPTEVfVVNFUiJdLCJqdGkiOiIwOTM2ZTRjZC1kNTczLTQzMzItYTkwZi0xYmRjMTk2NWViY2QiLCJmb3J1bV9pZCI6LTk5LCJjbGllbnRfaWQiOiIyNkJYQXZLbnk1V0Y1WjA5bHI1azc3WTgifQ.prTC8lYD7WMdr_Qglv7DimBEy3kfYYph6Twoy16ZmTI"
                    }
        res=requests.get(url="https://action.daum.net/apis/v1/reactions/home?itemKey={}".format(article_id), headers=s_header)
        sticker={key: value for key, value in json.loads(res.text)["item"]["stats"].items() if key in ["LIKE","SAD", "ANGRY", "RECOMMEND", "IMPRESS"]}
        
        title = response.xpath('//*[@id="mArticle"]/div[1]/h3/text()').get()
        reporter = "".join([text for text in response.css('.txt_info::text').getall() if text not in ["입력 ", "수정 ", "개"]])
        date = response.css('.num_date::text').get()
        change_date="".join([c_date for c_date in response.css(".num_date::text").getall() if c_date != date])
        press = response.xpath('//*[@id="kakaoServiceLogo"]/text()').get()
        contents = " ".join([sent.strip() for sent in response.xpath('//*[@id="mArticle"]/div[2]/div/section/p/text()').getall()])


        yield {
            'Url' : current_url,
            'date': date,
            'change_date' : change_date,
            'title': title,
            'reporter':reporter,
            'press': press,
            'contents': contents,
            'sticker' : sticker
        }

class DaumPublicnoticeSpider(scrapy.Spider):
    name = "daum_publicnotice"
    handle_httpstatus_list = [301, 302]


    def __init__(self, *args, **kwargs):
        super(DaumPublicnoticeSpider, self).__init__(*args, **kwargs)
        self.base_url = 'https://news.daum.net/breakingnews/economic/stock/publicnotice?page={}&regDate={}'
        self.start_date = date(2023, 9, 13)
        self.end_date = self.start_date-pd.DateOffset(year=1)
        self.current_page = 1
        self.previous_page_content = None


    def start_requests(self):
        #크롤링 시작 url 생성
        date_str = self.start_date.strftime('%Y%m%d')
        url = self.base_url.format(self.current_page, date_str)
        yield scrapy.Request(url=url, callback=self.parse, headers=headers)

    def parse(self, response):
        current_page_content = ''.join(response.css('.box_etc > ul > li > div > strong > a::text').getall())
        # 현재 페이지의 내용과 이전 페이지의 내용이 같으면, 해당 일자 크롤링 종료
        if current_page_content == self.previous_page_content:
            self.start_date -= timedelta(days=1)
            # 다음 날짜가 종료 날짜 이전일 경우 다시 parse 함수 실행
            if self.start_date >= self.end_date:
                self.current_page = 1
                date_str = self.start_date.strftime('%Y%m%d')
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
        date_str = self.start_date.strftime('%Y%m%d')
        next_url = self.base_url.format(self.current_page, date_str)
        yield scrapy.Request(url=next_url, callback=self.parse, headers=headers)

    #상세 뉴스 페이지 내용 크롤링(url, 날짜, 수정날짜, 제목, 기자, 신문사, 본문, 스티커)
    def parse_detail(self, response):
        current_url=response.url
        article_id=current_url.split("/")[-1]
        s_header = {"User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36",
                    "referer": current_url,
                    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmb3J1bV9rZXkiOiJuZXdzIiwidXNlcl92aWV3Ijp7ImlkIjo4NDQ5Mjc0NiwiaWNvbiI6Imh0dHBzOi8vdDEuZGF1bWNkbi5uZXQvcHJvZmlsZS84WWJFVEhhcEpHYzAiLCJwcm92aWRlcklkIjoiREFVTSIsImRpc3BsYXlOYW1lIjoi67CV7IiY7KCVIn0sImdyYW50X3R5cGUiOiJhbGV4X2NyZWRlbnRpYWxzIiwic2NvcGUiOltdLCJleHAiOjE2OTQ3MTU4NTIsImF1dGhvcml0aWVzIjpbIlJPTEVfSU5URUdSQVRFRCIsIlJPTEVfREFVTSIsIlJPTEVfSURFTlRJRklFRCIsIlJPTEVfVVNFUiJdLCJqdGkiOiIwOTM2ZTRjZC1kNTczLTQzMzItYTkwZi0xYmRjMTk2NWViY2QiLCJmb3J1bV9pZCI6LTk5LCJjbGllbnRfaWQiOiIyNkJYQXZLbnk1V0Y1WjA5bHI1azc3WTgifQ.prTC8lYD7WMdr_Qglv7DimBEy3kfYYph6Twoy16ZmTI"
                    }
        res=requests.get(url="https://action.daum.net/apis/v1/reactions/home?itemKey={}".format(article_id), headers=s_header)
        sticker={key: value for key, value in json.loads(res.text)["item"]["stats"].items() if key in ["LIKE","SAD", "ANGRY", "RECOMMEND", "IMPRESS"]}
        
        title = response.xpath('//*[@id="mArticle"]/div[1]/h3/text()').get()
        reporter = "".join([text for text in response.css('.txt_info::text').getall() if text not in ["입력 ", "수정 ", "개"]])
        date = response.css('.num_date::text').get()
        change_date="".join([c_date for c_date in response.css(".num_date::text").getall() if c_date != date])
        press = response.xpath('//*[@id="kakaoServiceLogo"]/text()').get()
        contents = " ".join([sent.strip() for sent in response.xpath('//*[@id="mArticle"]/div[2]/div/section/p/text()').getall()])


        yield {
            'Url' : current_url,
            'date': date,
            'change_date' : change_date,
            'title': title,
            'reporter':reporter,
            'press': press,
            'contents': contents,
            'sticker' : sticker
        }


class DaumStockworldSpider(scrapy.Spider):
    name = "daum_stockworld"
    handle_httpstatus_list = [301, 302]

    def __init__(self, *args, **kwargs):
        super(DaumStockworldSpider, self).__init__(*args, **kwargs)
        self.base_url = 'https://news.daum.net/breakingnews/economic/stock/world?page={}&regDate={}'
        self.start_date = date(2023, 8, 13)
        self.end_date = self.start_date-pd.DateOffset(year=1)
        self.current_page = 1
        self.previous_page_content = None


    def start_requests(self):
        #크롤링 시작 url 생성
        date_str = self.start_date.strftime('%Y%m%d')
        url = self.base_url.format(self.current_page, date_str)
        yield scrapy.Request(url=url, callback=self.parse, headers=headers)
        
    def parse(self, response):
        current_page_content = ''.join(response.css('.box_etc > ul > li > div > strong > a::text').getall())
        # 현재 페이지의 내용과 이전 페이지의 내용이 같으면, 해당 일자 크롤링 종료
        if current_page_content == self.previous_page_content:
            self.start_date -= timedelta(days=1)
            # 다음 날짜가 종료 날짜 이전일 경우 다시 parse 함수 실행
            if self.start_date >= self.end_date:
                self.current_page = 1
                date_str = self.start_date.strftime('%Y%m%d')
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
        date_str = self.start_date.strftime('%Y%m%d')
        next_url = self.base_url.format(self.current_page, date_str)
        yield scrapy.Request(url=next_url, callback=self.parse, headers=headers)

    #상세 뉴스 페이지 내용 크롤링(url, 날짜, 수정날짜, 제목, 기자, 신문사, 본문, 스티커)
    def parse_detail(self, response):
        current_url=response.url
        article_id=current_url.split("/")[-1]
        s_header = {"User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36",
                    "referer": current_url,
                    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmb3J1bV9rZXkiOiJuZXdzIiwidXNlcl92aWV3Ijp7ImlkIjo4NDQ5Mjc0NiwiaWNvbiI6Imh0dHBzOi8vdDEuZGF1bWNkbi5uZXQvcHJvZmlsZS84WWJFVEhhcEpHYzAiLCJwcm92aWRlcklkIjoiREFVTSIsImRpc3BsYXlOYW1lIjoi67CV7IiY7KCVIn0sImdyYW50X3R5cGUiOiJhbGV4X2NyZWRlbnRpYWxzIiwic2NvcGUiOltdLCJleHAiOjE2OTQ3MTU4NTIsImF1dGhvcml0aWVzIjpbIlJPTEVfSU5URUdSQVRFRCIsIlJPTEVfREFVTSIsIlJPTEVfSURFTlRJRklFRCIsIlJPTEVfVVNFUiJdLCJqdGkiOiIwOTM2ZTRjZC1kNTczLTQzMzItYTkwZi0xYmRjMTk2NWViY2QiLCJmb3J1bV9pZCI6LTk5LCJjbGllbnRfaWQiOiIyNkJYQXZLbnk1V0Y1WjA5bHI1azc3WTgifQ.prTC8lYD7WMdr_Qglv7DimBEy3kfYYph6Twoy16ZmTI"
                    }
        res=requests.get(url="https://action.daum.net/apis/v1/reactions/home?itemKey={}".format(article_id), headers=s_header)
        sticker={key: value for key, value in json.loads(res.text)["item"]["stats"].items() if key in ["LIKE","SAD", "ANGRY", "RECOMMEND", "IMPRESS"]}
        
        title = response.xpath('//*[@id="mArticle"]/div[1]/h3/text()').get()
        reporter = "".join([text for text in response.css('.txt_info::text').getall() if text not in ["입력 ", "수정 ", "개"]])
        date = response.css('.num_date::text').get()
        change_date="".join([c_date for c_date in response.css(".num_date::text").getall() if c_date != date])
        press = response.xpath('//*[@id="kakaoServiceLogo"]/text()').get()
        contents = " ".join([sent.strip() for sent in response.xpath('//*[@id="mArticle"]/div[2]/div/section/p/text()').getall()])


        yield {
            'Url' : current_url,
            'date': date,
            'change_date' : change_date,
            'title': title,
            'reporter':reporter,
            'press': press,
            'contents': contents,
            'sticker' : sticker
        }


class DaumBondsfuturesSpider(scrapy.Spider):
    name = "daum_bondfutures"
    handle_httpstatus_list = [301, 302]

    def __init__(self, *args, **kwargs):
        super(DaumBondsfuturesSpider, self).__init__(*args, **kwargs)
        self.base_url = 'https://news.daum.net/breakingnews/economic/stock/bondsfutures?page={}&regDate={}'
        self.start_date = date(2023, 8, 13)
        self.end_date = self.start_date-pd.DateOffset(year=1)
        self.current_page = 1
        self.previous_page_content = None


    def start_requests(self):
        #크롤링 시작 url 생성
        date_str = self.start_date.strftime('%Y%m%d')
        url = self.base_url.format(self.current_page, date_str)
        yield scrapy.Request(url=url, callback=self.parse, headers=headers)
        
    def parse(self, response):
        current_page_content = ''.join(response.css('.box_etc > ul > li > div > strong > a::text').getall())
        # 현재 페이지의 내용과 이전 페이지의 내용이 같으면, 해당 일자 크롤링 종료
        if current_page_content == self.previous_page_content:
            self.start_date -= timedelta(days=1)
            # 다음 날짜가 종료 날짜 이전일 경우 다시 parse 함수 실행
            if self.start_date >= self.end_date:
                self.current_page = 1
                date_str = self.start_date.strftime('%Y%m%d')
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
        date_str = self.start_date.strftime('%Y%m%d')
        next_url = self.base_url.format(self.current_page, date_str)
        yield scrapy.Request(url=next_url, callback=self.parse, headers=headers)

    #상세 뉴스 페이지 내용 크롤링(url, 날짜, 수정날짜, 제목, 기자, 신문사, 본문, 스티커)
    def parse_detail(self, response):
        current_url=response.url
        article_id=current_url.split("/")[-1]
        s_header = {"User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36",
                    "referer": current_url,
                    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmb3J1bV9rZXkiOiJuZXdzIiwidXNlcl92aWV3Ijp7ImlkIjo4NDQ5Mjc0NiwiaWNvbiI6Imh0dHBzOi8vdDEuZGF1bWNkbi5uZXQvcHJvZmlsZS84WWJFVEhhcEpHYzAiLCJwcm92aWRlcklkIjoiREFVTSIsImRpc3BsYXlOYW1lIjoi67CV7IiY7KCVIn0sImdyYW50X3R5cGUiOiJhbGV4X2NyZWRlbnRpYWxzIiwic2NvcGUiOltdLCJleHAiOjE2OTQ3MTU4NTIsImF1dGhvcml0aWVzIjpbIlJPTEVfSU5URUdSQVRFRCIsIlJPTEVfREFVTSIsIlJPTEVfSURFTlRJRklFRCIsIlJPTEVfVVNFUiJdLCJqdGkiOiIwOTM2ZTRjZC1kNTczLTQzMzItYTkwZi0xYmRjMTk2NWViY2QiLCJmb3J1bV9pZCI6LTk5LCJjbGllbnRfaWQiOiIyNkJYQXZLbnk1V0Y1WjA5bHI1azc3WTgifQ.prTC8lYD7WMdr_Qglv7DimBEy3kfYYph6Twoy16ZmTI"
                    }
        res=requests.get(url="https://action.daum.net/apis/v1/reactions/home?itemKey={}".format(article_id), headers=s_header)
        sticker={key: value for key, value in json.loads(res.text)["item"]["stats"].items() if key in ["LIKE","SAD", "ANGRY", "RECOMMEND", "IMPRESS"]}
        
        title = response.xpath('//*[@id="mArticle"]/div[1]/h3/text()').get()
        reporter = "".join([text for text in response.css('.txt_info::text').getall() if text not in ["입력 ", "수정 ", "개"]])
        date = response.css('.num_date::text').get()
        change_date="".join([c_date for c_date in response.css(".num_date::text").getall() if c_date != date])
        press = response.xpath('//*[@id="kakaoServiceLogo"]/text()').get()
        contents = " ".join([sent.strip() for sent in response.xpath('//*[@id="mArticle"]/div[2]/div/section/p/text()').getall()])


        yield {
            'Url' : current_url,
            'date': date,
            'change_date' : change_date,
            'title': title,
            'reporter':reporter,
            'press': press,
            'contents': contents,
            'sticker' : sticker
        }


class DaumFxSpider(scrapy.Spider):
    name = "daum_fx"
    handle_httpstatus_list = [301, 302]

    def __init__(self, *args, **kwargs):
        super(DaumBondsfuturesSpider, self).__init__(*args, **kwargs)
        self.base_url = 'https://news.daum.net/breakingnews/economic/stock/fx?page={}&regDate={}'
        self.start_date = date(2023, 8, 13)
        self.end_date = date.today()
        self.current_page = 1
        self.previous_page_content = None


    def start_requests(self):
        #크롤링 시작 url 생성
        date_str = self.start_date.strftime('%Y%m%d')
        url = self.base_url.format(self.current_page, date_str)
        yield scrapy.Request(url=url, callback=self.parse, headers=headers)
        
    def parse(self, response):
        current_page_content = ''.join(response.css('.box_etc > ul > li > div > strong > a::text').getall())
        # 현재 페이지의 내용과 이전 페이지의 내용이 같으면, 해당 일자 크롤링 종료
        if current_page_content == self.previous_page_content:
            self.start_date -= timedelta(days=1)
            # 다음 날짜가 종료 날짜 이전일 경우 다시 parse 함수 실행
            if self.start_date >= self.end_date:
                self.current_page = 1
                date_str = self.start_date.strftime('%Y%m%d')
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
        date_str = self.start_date.strftime('%Y%m%d')
        next_url = self.base_url.format(self.current_page, date_str)
        yield scrapy.Request(url=next_url, callback=self.parse, headers=headers)

    #상세 뉴스 페이지 내용 크롤링(url, 날짜, 수정날짜, 제목, 기자, 신문사, 본문, 스티커)
    def parse_detail(self, response):
        current_url=response.url
        article_id=current_url.split("/")[-1]
        s_header = {"User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36",
                    "referer": current_url,
                    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmb3J1bV9rZXkiOiJuZXdzIiwidXNlcl92aWV3Ijp7ImlkIjo4NDQ5Mjc0NiwiaWNvbiI6Imh0dHBzOi8vdDEuZGF1bWNkbi5uZXQvcHJvZmlsZS84WWJFVEhhcEpHYzAiLCJwcm92aWRlcklkIjoiREFVTSIsImRpc3BsYXlOYW1lIjoi67CV7IiY7KCVIn0sImdyYW50X3R5cGUiOiJhbGV4X2NyZWRlbnRpYWxzIiwic2NvcGUiOltdLCJleHAiOjE2OTQ3MTU4NTIsImF1dGhvcml0aWVzIjpbIlJPTEVfSU5URUdSQVRFRCIsIlJPTEVfREFVTSIsIlJPTEVfSURFTlRJRklFRCIsIlJPTEVfVVNFUiJdLCJqdGkiOiIwOTM2ZTRjZC1kNTczLTQzMzItYTkwZi0xYmRjMTk2NWViY2QiLCJmb3J1bV9pZCI6LTk5LCJjbGllbnRfaWQiOiIyNkJYQXZLbnk1V0Y1WjA5bHI1azc3WTgifQ.prTC8lYD7WMdr_Qglv7DimBEy3kfYYph6Twoy16ZmTI"
                    }
        res=requests.get(url="https://action.daum.net/apis/v1/reactions/home?itemKey={}".format(article_id), headers=s_header)
        sticker={key: value for key, value in json.loads(res.text)["item"]["stats"].items() if key in ["LIKE","SAD", "ANGRY", "RECOMMEND", "IMPRESS"]}
        
        title = response.xpath('//*[@id="mArticle"]/div[1]/h3/text()').get()
        reporter = "".join([text for text in response.css('.txt_info::text').getall() if text not in ["입력 ", "수정 ", "개"]])
        date = response.css('.num_date::text').get()
        change_date="".join([c_date for c_date in response.css(".num_date::text").getall() if c_date != date])
        press = response.xpath('//*[@id="kakaoServiceLogo"]/text()').get()
        contents = " ".join([sent.strip() for sent in response.xpath('//*[@id="mArticle"]/div[2]/div/section/p/text()').getall()])


        yield {
            'Url' : current_url,
            'date': date,
            'change_date' : change_date,
            'title': title,
            'reporter':reporter,
            'press': press,
            'contents': contents,
            'sticker' : sticker
        }


class DaumStockothersSpider(scrapy.Spider):
    name = "daum_stockothers"
    handle_httpstatus_list = [301, 302]

    def __init__(self, *args, **kwargs):
        super(DaumOthersSpider, self).__init__(*args, **kwargs)
        self.base_url = 'https://news.daum.net/breakingnews/economic/stock/others?page={}&regDate={}'
        self.start_date = date(2023, 8, 13)
        self.end_date = self.start_date-pd.DateOffset(year=1)
        self.current_page = 1
        self.previous_page_content = None


    def start_requests(self):
        #크롤링 시작 url 생성
        date_str = self.start_date.strftime('%Y%m%d')
        url = self.base_url.format(self.current_page, date_str)
        yield scrapy.Request(url=url, callback=self.parse, headers=headers)
        
    def parse(self, response):
        current_page_content = ''.join(response.css('.box_etc > ul > li > div > strong > a::text').getall())
        # 현재 페이지의 내용과 이전 페이지의 내용이 같으면, 해당 일자 크롤링 종료
        if current_page_content == self.previous_page_content:
            self.start_date -= timedelta(days=1)
            # 다음 날짜가 종료 날짜 이전일 경우 다시 parse 함수 실행
            if self.start_date >= self.end_date:
                self.current_page = 1
                date_str = self.start_date.strftime('%Y%m%d')
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
        date_str = self.start_date.strftime('%Y%m%d')
        next_url = self.base_url.format(self.current_page, date_str)
        yield scrapy.Request(url=next_url, callback=self.parse, headers=headers)

    #상세 뉴스 페이지 내용 크롤링(url, 날짜, 수정날짜, 제목, 기자, 신문사, 본문, 스티커)
    def parse_detail(self, response):
        current_url=response.url
        article_id=current_url.split("/")[-1]
        s_header = {"User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36",
                    "referer": current_url,
                    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmb3J1bV9rZXkiOiJuZXdzIiwidXNlcl92aWV3Ijp7ImlkIjo4NDQ5Mjc0NiwiaWNvbiI6Imh0dHBzOi8vdDEuZGF1bWNkbi5uZXQvcHJvZmlsZS84WWJFVEhhcEpHYzAiLCJwcm92aWRlcklkIjoiREFVTSIsImRpc3BsYXlOYW1lIjoi67CV7IiY7KCVIn0sImdyYW50X3R5cGUiOiJhbGV4X2NyZWRlbnRpYWxzIiwic2NvcGUiOltdLCJleHAiOjE2OTQ3MTU4NTIsImF1dGhvcml0aWVzIjpbIlJPTEVfSU5URUdSQVRFRCIsIlJPTEVfREFVTSIsIlJPTEVfSURFTlRJRklFRCIsIlJPTEVfVVNFUiJdLCJqdGkiOiIwOTM2ZTRjZC1kNTczLTQzMzItYTkwZi0xYmRjMTk2NWViY2QiLCJmb3J1bV9pZCI6LTk5LCJjbGllbnRfaWQiOiIyNkJYQXZLbnk1V0Y1WjA5bHI1azc3WTgifQ.prTC8lYD7WMdr_Qglv7DimBEy3kfYYph6Twoy16ZmTI"
                    }
        res=requests.get(url="https://action.daum.net/apis/v1/reactions/home?itemKey={}".format(article_id), headers=s_header)
        sticker={key: value for key, value in json.loads(res.text)["item"]["stats"].items() if key in ["LIKE","SAD", "ANGRY", "RECOMMEND", "IMPRESS"]}
        
        title = response.xpath('//*[@id="mArticle"]/div[1]/h3/text()').get()
        reporter = "".join([text for text in response.css('.txt_info::text').getall() if text not in ["입력 ", "수정 ", "개"]])
        date = response.css('.num_date::text').get()
        change_date="".join([c_date for c_date in response.css(".num_date::text").getall() if c_date != date])
        press = response.xpath('//*[@id="kakaoServiceLogo"]/text()').get()
        contents = " ".join([sent.strip() for sent in response.xpath('//*[@id="mArticle"]/div[2]/div/section/p/text()').getall()])


        yield {
            'Url' : current_url,
            'date': date,
            'change_date' : change_date,
            'title': title,
            'reporter':reporter,
            'press': press,
            'contents': contents,
            'sticker' : sticker
        }


class DaumEstateSpider(scrapy.Spider):
    name = "daum_estate"
    handle_httpstatus_list = [301, 302]

    def __init__(self, *args, **kwargs):
        super(DaumEstateSpider, self).__init__(*args, **kwargs)
        self.base_url = 'https://news.daum.net/breakingnews/economic/estate?page={}&regDate={}'
        self.start_date = date(2023, 8, 13)
        self.end_date = self.start_date-pd.DateOffset(year=1)
        self.current_page = 1
        self.previous_page_content = None


    def start_requests(self):
        #크롤링 시작 url 생성
        date_str = self.start_date.strftime('%Y%m%d')
        url = self.base_url.format(self.current_page, date_str)
        yield scrapy.Request(url=url, callback=self.parse, headers=headers)
        
    def parse(self, response):
        current_page_content = ''.join(response.css('.box_etc > ul > li > div > strong > a::text').getall())
        # 현재 페이지의 내용과 이전 페이지의 내용이 같으면, 해당 일자 크롤링 종료
        if current_page_content == self.previous_page_content:
            self.start_date -= timedelta(days=1)
            # 다음 날짜가 종료 날짜 이전일 경우 다시 parse 함수 실행
            if self.start_date >= self.end_date:
                self.current_page = 1
                date_str = self.start_date.strftime('%Y%m%d')
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
        date_str = self.start_date.strftime('%Y%m%d')
        next_url = self.base_url.format(self.current_page, date_str)
        yield scrapy.Request(url=next_url, callback=self.parse, headers=headers)

    #상세 뉴스 페이지 내용 크롤링(url, 날짜, 수정날짜, 제목, 기자, 신문사, 본문, 스티커)
    def parse_detail(self, response):
        current_url=response.url
        article_id=current_url.split("/")[-1]
        s_header = {"User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36",
                    "referer": current_url,
                    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmb3J1bV9rZXkiOiJuZXdzIiwidXNlcl92aWV3Ijp7ImlkIjo4NDQ5Mjc0NiwiaWNvbiI6Imh0dHBzOi8vdDEuZGF1bWNkbi5uZXQvcHJvZmlsZS84WWJFVEhhcEpHYzAiLCJwcm92aWRlcklkIjoiREFVTSIsImRpc3BsYXlOYW1lIjoi67CV7IiY7KCVIn0sImdyYW50X3R5cGUiOiJhbGV4X2NyZWRlbnRpYWxzIiwic2NvcGUiOltdLCJleHAiOjE2OTQ3MTU4NTIsImF1dGhvcml0aWVzIjpbIlJPTEVfSU5URUdSQVRFRCIsIlJPTEVfREFVTSIsIlJPTEVfSURFTlRJRklFRCIsIlJPTEVfVVNFUiJdLCJqdGkiOiIwOTM2ZTRjZC1kNTczLTQzMzItYTkwZi0xYmRjMTk2NWViY2QiLCJmb3J1bV9pZCI6LTk5LCJjbGllbnRfaWQiOiIyNkJYQXZLbnk1V0Y1WjA5bHI1azc3WTgifQ.prTC8lYD7WMdr_Qglv7DimBEy3kfYYph6Twoy16ZmTI"
                    }
        res=requests.get(url="https://action.daum.net/apis/v1/reactions/home?itemKey={}".format(article_id), headers=s_header)
        sticker={key: value for key, value in json.loads(res.text)["item"]["stats"].items() if key in ["LIKE","SAD", "ANGRY", "RECOMMEND", "IMPRESS"]}
        
        title = response.xpath('//*[@id="mArticle"]/div[1]/h3/text()').get()
        reporter = "".join([text for text in response.css('.txt_info::text').getall() if text not in ["입력 ", "수정 ", "개"]])
        date = response.css('.num_date::text').get()
        change_date="".join([c_date for c_date in response.css(".num_date::text").getall() if c_date != date])
        press = response.xpath('//*[@id="kakaoServiceLogo"]/text()').get()
        contents = " ".join([sent.strip() for sent in response.xpath('//*[@id="mArticle"]/div[2]/div/section/p/text()').getall()])


        yield {
            'Url' : current_url,
            'date': date,
            'change_date' : change_date,
            'title': title,
            'reporter':reporter,
            'press': press,
            'contents': contents,
            'sticker' : sticker
        }


class DaumConsumerSpider(scrapy.Spider):
    name = "daum_consumer"
    handle_httpstatus_list = [301, 302]

    def __init__(self, *args, **kwargs):
        super(DaumConsumerSpider, self).__init__(*args, **kwargs)
        self.base_url = 'https://news.daum.net/breakingnews/economic/consumer?page={}&regDate={}'
        self.start_date = date(2023, 8, 13)
        self.end_date = self.start_date-pd.DateOffset(year=1)
        self.current_page = 1
        self.previous_page_content = None


    def start_requests(self):
        #크롤링 시작 url 생성
        date_str = self.start_date.strftime('%Y%m%d')
        url = self.base_url.format(self.current_page, date_str)
        yield scrapy.Request(url=url, callback=self.parse, headers=headers)
        
    def parse(self, response):
        current_page_content = ''.join(response.css('.box_etc > ul > li > div > strong > a::text').getall())
        # 현재 페이지의 내용과 이전 페이지의 내용이 같으면, 해당 일자 크롤링 종료
        if current_page_content == self.previous_page_content:
            self.start_date -= timedelta(days=1)
            # 다음 날짜가 종료 날짜 이전일 경우 다시 parse 함수 실행
            if self.start_date >= self.end_date:
                self.current_page = 1
                date_str = self.start_date.strftime('%Y%m%d')
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
        date_str = self.start_date.strftime('%Y%m%d')
        next_url = self.base_url.format(self.current_page, date_str)
        yield scrapy.Request(url=next_url, callback=self.parse, headers=headers)

    #상세 뉴스 페이지 내용 크롤링(url, 날짜, 수정날짜, 제목, 기자, 신문사, 본문, 스티커)
    def parse_detail(self, response):
        current_url=response.url
        article_id=current_url.split("/")[-1]
        s_header = {"User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36",
                    "referer": current_url,
                    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmb3J1bV9rZXkiOiJuZXdzIiwidXNlcl92aWV3Ijp7ImlkIjo4NDQ5Mjc0NiwiaWNvbiI6Imh0dHBzOi8vdDEuZGF1bWNkbi5uZXQvcHJvZmlsZS84WWJFVEhhcEpHYzAiLCJwcm92aWRlcklkIjoiREFVTSIsImRpc3BsYXlOYW1lIjoi67CV7IiY7KCVIn0sImdyYW50X3R5cGUiOiJhbGV4X2NyZWRlbnRpYWxzIiwic2NvcGUiOltdLCJleHAiOjE2OTQ3MTU4NTIsImF1dGhvcml0aWVzIjpbIlJPTEVfSU5URUdSQVRFRCIsIlJPTEVfREFVTSIsIlJPTEVfSURFTlRJRklFRCIsIlJPTEVfVVNFUiJdLCJqdGkiOiIwOTM2ZTRjZC1kNTczLTQzMzItYTkwZi0xYmRjMTk2NWViY2QiLCJmb3J1bV9pZCI6LTk5LCJjbGllbnRfaWQiOiIyNkJYQXZLbnk1V0Y1WjA5bHI1azc3WTgifQ.prTC8lYD7WMdr_Qglv7DimBEy3kfYYph6Twoy16ZmTI"
                    }
        res=requests.get(url="https://action.daum.net/apis/v1/reactions/home?itemKey={}".format(article_id), headers=s_header)
        sticker={key: value for key, value in json.loads(res.text)["item"]["stats"].items() if key in ["LIKE","SAD", "ANGRY", "RECOMMEND", "IMPRESS"]}
        
        title = response.xpath('//*[@id="mArticle"]/div[1]/h3/text()').get()
        reporter = "".join([text for text in response.css('.txt_info::text').getall() if text not in ["입력 ", "수정 ", "개"]])
        date = response.css('.num_date::text').get()
        change_date="".join([c_date for c_date in response.css(".num_date::text").getall() if c_date != date])
        press = response.xpath('//*[@id="kakaoServiceLogo"]/text()').get()
        contents = " ".join([sent.strip() for sent in response.xpath('//*[@id="mArticle"]/div[2]/div/section/p/text()').getall()])


        yield {
            'Url' : current_url,
            'date': date,
            'change_date' : change_date,
            'title': title,
            'reporter':reporter,
            'press': press,
            'contents': contents,
            'sticker' : sticker
        }

class DaumWorldSpider(scrapy.Spider):
    name = "daum_world"
    handle_httpstatus_list = [301, 302]

    def __init__(self, *args, **kwargs):
        super(DaumWorldSpider, self).__init__(*args, **kwargs)
        self.base_url = 'https://news.daum.net/breakingnews/economic/world?page={}&regDate={}'
        self.start_date = date(2023, 8, 13)
        self.end_date = self.start_date-pd.DateOffset(year=1)
        self.current_page = 1
        self.previous_page_content = None


    def start_requests(self):
        #크롤링 시작 url 생성
        date_str = self.start_date.strftime('%Y%m%d')
        url = self.base_url.format(self.current_page, date_str)
        yield scrapy.Request(url=url, callback=self.parse, headers=headers)
        
    def parse(self, response):
        current_page_content = ''.join(response.css('.box_etc > ul > li > div > strong > a::text').getall())
        # 현재 페이지의 내용과 이전 페이지의 내용이 같으면, 해당 일자 크롤링 종료
        if current_page_content == self.previous_page_content:
            self.start_date -= timedelta(days=1)
            # 다음 날짜가 종료 날짜 이전일 경우 다시 parse 함수 실행
            if self.start_date >= self.end_date:
                self.current_page = 1
                date_str = self.start_date.strftime('%Y%m%d')
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
        date_str = self.start_date.strftime('%Y%m%d')
        next_url = self.base_url.format(self.current_page, date_str)
        yield scrapy.Request(url=next_url, callback=self.parse, headers=headers)

    #상세 뉴스 페이지 내용 크롤링(url, 날짜, 수정날짜, 제목, 기자, 신문사, 본문, 스티커)
    def parse_detail(self, response):
        current_url=response.url
        article_id=current_url.split("/")[-1]
        s_header = {"User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36",
                    "referer": current_url,
                    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmb3J1bV9rZXkiOiJuZXdzIiwidXNlcl92aWV3Ijp7ImlkIjo4NDQ5Mjc0NiwiaWNvbiI6Imh0dHBzOi8vdDEuZGF1bWNkbi5uZXQvcHJvZmlsZS84WWJFVEhhcEpHYzAiLCJwcm92aWRlcklkIjoiREFVTSIsImRpc3BsYXlOYW1lIjoi67CV7IiY7KCVIn0sImdyYW50X3R5cGUiOiJhbGV4X2NyZWRlbnRpYWxzIiwic2NvcGUiOltdLCJleHAiOjE2OTQ3MTU4NTIsImF1dGhvcml0aWVzIjpbIlJPTEVfSU5URUdSQVRFRCIsIlJPTEVfREFVTSIsIlJPTEVfSURFTlRJRklFRCIsIlJPTEVfVVNFUiJdLCJqdGkiOiIwOTM2ZTRjZC1kNTczLTQzMzItYTkwZi0xYmRjMTk2NWViY2QiLCJmb3J1bV9pZCI6LTk5LCJjbGllbnRfaWQiOiIyNkJYQXZLbnk1V0Y1WjA5bHI1azc3WTgifQ.prTC8lYD7WMdr_Qglv7DimBEy3kfYYph6Twoy16ZmTI"
                    }
        res=requests.get(url="https://action.daum.net/apis/v1/reactions/home?itemKey={}".format(article_id), headers=s_header)
        sticker={key: value for key, value in json.loads(res.text)["item"]["stats"].items() if key in ["LIKE","SAD", "ANGRY", "RECOMMEND", "IMPRESS"]}
        
        title = response.xpath('//*[@id="mArticle"]/div[1]/h3/text()').get()
        reporter = "".join([text for text in response.css('.txt_info::text').getall() if text not in ["입력 ", "수정 ", "개"]])
        date = response.css('.num_date::text').get()
        change_date="".join([c_date for c_date in response.css(".num_date::text").getall() if c_date != date])
        press = response.xpath('//*[@id="kakaoServiceLogo"]/text()').get()
        contents = " ".join([sent.strip() for sent in response.xpath('//*[@id="mArticle"]/div[2]/div/section/p/text()').getall()])


        yield {
            'Url' : current_url,
            'date': date,
            'change_date' : change_date,
            'title': title,
            'reporter':reporter,
            'press': press,
            'contents': contents,
            'sticker' : sticker
        }






 
