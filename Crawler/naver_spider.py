import scrapy
from datetime import date, datetime, timedelta
from user_agent import generate_user_agent
from urllib.parse import urljoin
# from .clean import *

'''
#날짜 변경 _ 각자 본인이 맡은 연도로 수정
start_date = date(2015, 1, 1)
end_date = date.today()

scrapy 설치된 가상 환경 불러오기
crawler 있는 폴더로 이동 (ex. /naver_finance/naver_finance/spiders)
날짜 설정 후 scrapy 실행 코드: scrapy runspider {spider_name} -o {file_name} -t csv
'''

headers = {'User-Agent': generate_user_agent(os='win', device_type='desktop')}

class FinanceSpider(scrapy.Spider):

    name = "finance"
    allowed_domains = ["news.naver.com"]

    def __init__(self, *args, **kwargs):
        super(FinanceSpider, self).__init__(*args, **kwargs)
        self.base_url = 'https://news.naver.com/main/list.naver?mode=LS2D&sid2=259&sid1=101&mid=shm&date={}&page={}'
        self.current_date = date(2023, 9, 10)
        self.end_date = date.today()
        self.current_page = 1
        self.previous_page_content = None

    def start_requests(self):
        #크롤링 시작 url 생성
        date_str = self.current_date.strftime('%Y%m%d')
        url = self.base_url.format(date_str, self.current_page)
        yield scrapy.Request(url=url, callback=self.parse, headers=headers)

    def parse(self, response):
        current_page_content = ''.join(response.css('.list_body.newsflash_body ul > li > dl > dt > a::text').getall())
        # 현재 페이지의 내용과 이전 페이지의 내용이 같으면, 해당 일자 크롤링 종료
        if current_page_content == self.previous_page_content:
            self.current_date += timedelta(days=1)
            # 다음 날짜가 종료 날짜 이전일 경우 다시 parse 함수 실행
            if self.current_date <= self.end_date:
                self.current_page = 1
                date_str = self.current_date.strftime('%Y%m%d')
                url = self.base_url.format(date_str, self.current_page)
                yield scrapy.Request(url=url, callback=self.parse, headers=headers)
            return
        # 현재 페이지의 내용과 이전 페이지의 내용이 다르면, 이전 페이지 내용을 현재 페이지로 업데이트
        else:
            self.previous_page_content = current_page_content

        # 기사 목록이 있을 경우 기사 url 크롤링 진행
        detail_urls = response.css('.list_body.newsflash_body ul > li > dl > dt > a::attr(href)').getall()
        for detail_url in detail_urls:
            try:
                # absolute_url = urljoin('https://news.naver.com', detail_url)
                yield scrapy.Request(url=detail_url, callback=self.parse_detail, headers=headers)
            except Exception as e:
                print(e)
                continue

        # 다음 페이지로 넘어감
        self.current_page += 1
        date_str = self.current_date.strftime('%Y%m%d')
        next_url = self.base_url.format(date_str, self.current_page)
        yield scrapy.Request(url=next_url, callback=self.parse, headers=headers)

    #상세 뉴스 페이지 내용 크롤링(제목, 날짜, 본문, 신문사)
    def parse_detail(self, response):
        title = response.xpath('//*[@id="title_area"]/span/text()').get()
        date = response.xpath('//*[@id="ct"]/div[1]/div[3]/div[1]/div[1]/span/text()').get()
        press = response.xpath('//*[@id="ct"]/div[1]/div[1]/a/img[1]/@alt').get()
        contents = response.xpath('//*[@id="dic_area"]/text()').getall()


        # #본문 p태그 유무에 따라 크롤링
        # contents = response.xpath('//*[@id="dic_area"]/text()').getall()
        # # contents = content_texts if content_texts else response.xpath('//*[@id="content"]/text()').getall()

        # cleaned_title = clean_title(title)
        # cleaned_date = clean_date(date)
        # cleaned_contents = ' '.join(clean_content(c) for c in contents)
        # cleaned_press = clean_press(press)

        yield {
            'date': date,
            'title': title,
            'press': press,
            'contents': contents
        }