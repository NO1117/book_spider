# -*- coding: utf-8 -*-
import scrapy
import json
from copy import deepcopy


class JdSpider(scrapy.Spider):
    name = "jd"
    allowed_domains = ["jd.com"]
    start_urls = ['https://book.jd.com/booksort.html']
    temp_price_url = 'http://p.3.cn/prices/mgets?type=1&area=1_72_4137_0&pdtk=&pduid=1222741648&pdpin=&pdbp=0&skuIds=J_{}'

    def parse(self, response):
        # 获取所有大的分类
        dt_list = response.xpath("//div[@class='mc']/dl/dt")
        for dt in dt_list:
            item = {}
            item["b_cname"] = dt.xpath("./a/text()").extract_first()
            # 获取所有小分类
            em_list = dt.xpath("./following-sibling::*[1]/em")
            for em in em_list:
                item["s_cname"] = em.xpath("./a/text()").extract_first()
                temp_href = em.xpath("./a/@href").extract_first()
                # 判断URL是否是http开头,如果不是，则应该加上，否则不加
                item['s_href'] = 'https:' + temp_href  if not temp_href.startswith('https') else temp_href
                yield scrapy.Request(
                    item['s_href'],
                    callback=self.get_book_list,
                    meta={'item':deepcopy(item)}
                )

    # 获取图书列表页面详情
    def get_book_list(self, response):
        item = deepcopy(response.meta['item'])
        li_list = response.xpath("//div[@id='plist']/ul/li")
        for li in li_list:
            item['img_href'] = li.xpath("./div/div[@class='p-img']/a/img/@data-lazy-img").extract_first()
            if item['img_href'] is None:
                item['img_href'] = li.xpath("./div/div[@class='p-img']/a/img/@src").extract_first()
            temp_name = li.xpath("./div/div[@class='p-name']/a/em/text()").extract_first()
            item['book_name'] = temp_name.replace('\n',"").split()[0]
            # item['book_brife'] = li.xpath("./div/div[@class='p-name']/a/em/text()").extract_first()
            temp_href = li.xpath("./div/div[@class='p-name']/a/@href").extract_first()
            if temp_href is not None:
                item['book_href'] = 'https:' + temp_href  if not temp_href.startswith('https') else temp_href
            item['book_author'] = li.xpath(".//span[@class='p-bi-name']/span[1]/a/@title").extract_first()
            item['book_store'] = li.xpath(".//span[@class='p-bi-store']/a/@title").extract_first()
            date = li.xpath(".//span[@class='p-bi-date']/text()").extract_first()
            item['book_data'] = date.replace('\n', '').split()[0]
            item['sku'] = li.xpath("./div/@data-sku").extract_first()
            book_price_url = self.temp_price_url.format(item['sku'])
            yield scrapy.Request(
                book_price_url,
                callback=self.get_book_price,
                meta={'item':deepcopy(item)},
                dont_filter=True
            )
        next_url_temp = response.xpath("//a[@class='pn-next']/@href").extract_first()
        if next_url_temp is not None:
            next_url = "https:" + next_url_temp if not next_url_temp.startswith('https') else next_url_temp
            yield scrapy.Request(
                next_url,
                callback=self.get_book_list,
                meta = {'item':deepcopy(response.meta['item'])}
            )

    # 获取图书价格
    def get_book_price(self, response):
        item = deepcopy(response.meta['item'])
        temp = json.loads(response.body.decode())
        item['book_price'] = temp[0].get('op')
        item['book_origin_price'] = temp[0].get('m')
        yield item