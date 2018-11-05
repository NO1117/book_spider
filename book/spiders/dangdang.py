# -*- coding: utf-8 -*-
import scrapy
from scrapy_redis.spiders import RedisSpider
from copy import deepcopy
from urllib.parse import urljoin

class DangdangSpider(RedisSpider):
    name = "dangdang"
    allowed_domains = ["dangdang.com"]
    redis_key = 'dangdang:start_urls'

    # reids:lpush dangdang:start_urls http://book.dangdang.com/
    def parse(self, response):
        item = {}
        # 获取一级分类
        div_list = response.xpath("//div[@class='con flq_body']/div")[:-1]
        for div in div_list:
            temp_name = div.xpath("./dl/dt//text()").extract()
            temp_name = ''.join(temp_name)
            item['F_cname'] = temp_name.replace('\n','').split()[0]
            # 获取二级分类
            dl_list = div.xpath(".//dl[@class='inner_dl']")
            for dl in dl_list:
                item['S_cname'] = dl.xpath(".//dt/a/@title").extract_first()
                # 获取三级分类
                dd_list = dl.xpath("./dd")
                for dd in dd_list:
                    item['T_cname'] = dd.xpath("./a/@title").extract_first()
                    item['T_href'] = dd.xpath("./a/@href").extract_first()
                    yield scrapy.Request(
                        item['T_href'],
                        callback=self.get_book_list,
                        meta={'item':deepcopy(item)}
                    )

    def get_book_list(self, response):
        item = deepcopy(response.meta['item'])
        li_list = response.xpath("//div[@id='search_nature_rg']/ul/li")
        for li in li_list:
            item['book_name'] = li.xpath("./a/@title").extract_first()
            item['book_href'] = li.xpath("./a/@href").extract_first()
            item['detail'] = li.xpath("./p[@class='detail']/text()").extract_first()
            item['price'] = li.xpath("./p[@class='price']/span[1]/text()").extract_first()
            item['origin_price'] = li.xpath("./p[@class='price']/span[2]/text()").extract_first()
            temp_comment = li.xpath("./p[4]/a/text()").extract_first()
            item['comment_num'] = temp_comment.replace("条评论",'')
            item['authors'] = li.xpath("./p[5]//span/a/text()").extract_first()
            date = li.xpath("./p[@class='search_book_author']/span[2]/text()").extract_first()
            item['publish_date'] = date.replace('/','').split()[0] if date else date
            item['book_store'] = li.xpath("./p[@class='search_book_author']/span[3]/a/@title").extract_first()
            yield item
        temp_url = response.xpath("//li[@class='next']/a/@href").extract_first()
        if temp_url:
            next_page_url = urljoin(response.url, temp_url)
            print("Next Page!", next_page_url)
            yield scrapy.Request(
                next_page_url,
                callback=self.get_book_list,
                meta={'item':deepcopy(item)}
            )

