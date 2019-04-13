#!/usr/bin/env python
# -*- coding: utf-8 -*-
import scrapy
from scrapy import Selector
from scrapy.utils.project import get_project_settings
from scrapy.crawler import CrawlerProcess
import re
from 金鸡奖获奖电影.Award_winning_movie.items import AwardWinningMovieItem
from 金鸡奖获奖电影.Award_winning_movie.Tools import List

class MainSpider(scrapy.Spider):
    name = "Award_winning_movie"
    allowed_domains = ['baike.baidu.com']

    # 构造初始URL
    def start_requests(self):
        # 金马奖
        url = "https://baike.baidu.com/item/第{no}届台湾电影金马奖"
        urls_year = [(url.format(no=x), x+1963) for x in range(15, 56)]   # 构造初始URL和年份(1978~2018)。
        headers = {'User-Agent':"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:63.0) Gecko/20100101 Firefox/63.0"}
        for uy in urls_year:
            request = scrapy.Request(uy[0], headers=headers, callback=self.parse_form)
            request.meta['year'] = uy[1]
            yield request

    # 得到提名和获奖电影表单
    def parse_form(self, response):
        sresponse = Selector(response)
        # 获取提名表单
        nominates = sresponse.xpath(r'.//h2[text()="提名名单"]/../../table//tr/th[contains(., "提名")]/../..')
        year = sresponse.response.meta['year']
        items2 = []
        if len(nominates) == 1:    # 只有一个表单，50届(2013年)之前
            items1 = self.parse_result1(nominates[0], year)
        elif len(nominates) > 1:   # 处理多个表单，50届(2013年)之后
            items1 = self.parse_result1(nominates[0], year)
            items2 = self.parse_result2(nominates[1], year)
        else: raise Exception("---没有获取到提名表单！---")
        # 返回数据到 pipelines
        for i in items1:
            yield i
        if items2:
           for i in items2:
               yield i

    # 解析提名表单一
    def parse_result1(self, tbody, year):
        trs = [tr for tr in tbody.xpath(r'.//tr') if len(tr.xpath(r'.//text()')) != 0]   # 获取不为空的tr
        trs = trs[1:]  # 去掉第一个列名
        title = ""   # 奖项名称
        ans = []    # 最终的 item列表
        persons = ['最佳男主角', '最佳女主角', '最佳男配角', '最佳女配角']
        for tr in trs:   # 为兼容50届(2013年)前后的表单格式
            tds = tr.xpath(r'./td')
            if len(tds) == 2:   # 兼容表单格式不统一
                titles = tds[0].xpath(r'.//text()').extract()
                title = List.GetOneStrip(titles)     # 对于使用 // 匹配符匹配的内容时，一定要注意空内容！
            message = "".join(tds[len(tds)-1].xpath(r'.//text()').extract())  # 获取表单中的信息
            if title.strip() in persons:  # 如果是‘最佳主配角’中的一种
                person_movie = re.findall(r'(.*?)《(.*?)》', message)
                for p, m in person_movie:
                    item = AwardWinningMovieItem(title=title.strip(), person=str(p).strip(), movie=str(m).strip(), year=year)
                    ans.append(item)
                continue
            else:
               movies = re.findall(r'《(.*?)》', message)
               for m in movies:
                   item = AwardWinningMovieItem(title=title.strip(), movie=str(m).strip(), year=year)
                   ans.append(item)
        return ans

    # 解析提名表单二
    def parse_result2(self, tbody, year):
        trs = [tr for tr in tbody.xpath(r'./tr') if len(tr.xpath(r'.//text()')) != 0]  # 获取不为空的tr
        trs = trs[1:]  # 去掉第一个列名
        title = ""  # 奖项名称
        ans = []  # 最终的 item列表
        persons = ['最佳男主角', '最佳女主角', '最佳男配角', '最佳女配角']
        for tr in trs:  # 为兼容50届(2013年)前后的表单格式
            tds = tr.xpath(r'./td')
            if len(tds) == 3:  # 兼容表单格式不统一
                titles = tds[0].xpath(r'.//text()').extract()
                title = List.GetOneStrip(titles)
            if title in persons:
                persons = tds[len(tds)-2].xpath(r'.//text()').extract()
                person = List.GetOneStrip(persons)
                ms = tds[len(tds)-1].xpath(r'.//text()').extract()
                m = List.GetOneStrip(ms)
                movies = re.findall(r'《(.*?)》', m)
                movie = List.GetOneStrip(movies)
                item = AwardWinningMovieItem(title=title.strip(), person=str(person).strip(), movie=str(movie).strip(), year=year)
                ans.append(item)
            else:
                ms = tds[len(tds)-1].xpath(r'.//text()').extract()
                m = List.GetOneStrip(ms)
                movies = re.findall(r'《(.*?)》', m)
                movie = List.GetOneStrip(movies)
                item = AwardWinningMovieItem(title=title.strip(), movie=str(movie).strip(), year=year)
                ans.append(item)
        return ans

if __name__ == "__main__":
    process = CrawlerProcess(get_project_settings())
    process.crawl("Award_winning_movie")
    process.start()
