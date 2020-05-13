# -*- coding: utf-8 -*-
import json
import scrapy



class DuzhiSpider(scrapy.Spider):
    name = 'duzhi'
    start_urls = ['http://duzhihu.cc/history']

    def parse(self, response):
        url = response.body_as_unicode()
        # print(url)
        links = response.xpath("//div[@class='panel-heading']/h3/a/@href")
        link = links.getall()

        for l in link:
            li = 'http://duzhihu.cc' +'/'+ l
            yield scrapy.Request(url=li,meta={'date': l}, callback=self.nextread)

    def nextread(self,response):
        l = response.meta['date']
        url = response.body_as_unicode
        links = response.xpath("//div[@class='answer_item']/h3/a/@href")
        link = links.getall()
        writedown = {'date': l, 'contain': link}
        yield writedown





