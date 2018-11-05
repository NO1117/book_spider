# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy_redis.spiders import RedisCrawlSpider


class AmazonSpider(RedisCrawlSpider):
    name = 'amazon'
    allowed_domains = ['amazon.cn']
    redis_key = "amazon:start_urls"

    # reids : amazon:start_urls https://www.amazon.cn/%E5%9B%BE%E4%B9%A6/b/ref=topnav_storetab_b?ie=UTF8&node=658390051 图书首页URL
    rules = (
        # 获取一级和二级分类的URL，并请求
        Rule(LinkExtractor(restrict_xpaths=("//ul[contains(@class,'s-ref-indent')]/div/li")), follow=True),
        # 获取图书的列表页面图书详情页的地址
        Rule(LinkExtractor(restrict_xpaths=("//div[@id='mainResults']/ul/li//h2/..")), callback='parse_item', follow=True),
        # 获取列表下一页
        Rule(LinkExtractor(restrict_xpaths=("//a[@id='pagnNextLink']")),  follow=True),

        # Rule(LinkExtractor(allow=r'Items/'), callback='parse_item', follow=True),
    )

    def parse_item(self, response):
        print(response.url)
        item = {}
        item['name'] = response.xpath("//div[@id='booksTitle']/div[1]/h1/span[1]/text()").extract_first()
        temp_commment = response.xpath("//span[@id='acrCustomerReviewText']/text()").extract_first()
        item['comment'] = temp_commment.split(' 条')[0]
        item['author'] = response.xpath("//div[@id='booksTitle']/div[2]/span[1]/a/text()").extract_first()

        is_ebook = response.xpath("//div[@id='booksTitle']/div[1]/h1/span[2]/text()").extract_first()
        item['is_ebook'] = True if 'Kindle电子书' in is_ebook else False
        if item['is_ebook']:
            temp_price = response.xpath("//tr[@class='kindle-price']/td[2]/text()").extract_first()
            item['ebook_price'] = self.putter_str(temp_price)
            temp_price = response.xpath("//tr[@class='digital-list-price']/td[2]/span/text()").extract_first()
            item['ebook_origin_price'] = self.putter_str(temp_price)
        else:
            item['book_price'] = response.xpath("//div[@id='soldByThirdParty']/span[2]/text()").extract_first()
            item['book_origin_price'] = response.xpath("//div[@id='buyBoxInner']/ul/li[1]/span/span[2]/text()").extract_first()
            temp_date = response.xpath("//div[@id='booksTitle']/div[1]/h1/span[3]/text()").extract_first()
            item['date'] = temp_date.replace('– ','')
            item['publish'] = response.xpath("//td[@class='bucket']/div/ul/li[1]/text()").extract_first()
        cate_list = response.xpath("//ul[@class='zg_hrsr']/li[1]/span[@class='zg_hrsr_ladder']//a")
        for cate in cate_list:
            index_num = cate_list.index(cate) + 1
            item['cate' +  str(index_num)] = cate.xpath("./text()").extract_first()
            item['cate' +  str(index_num) + '_href'] = cate.xpath("./@href").extract_first()
        yield item


    def putter_str(self, temp_str):
        temp_str = temp_str.replace('\n', '').split()
        return temp_str[0]