import os
import pickle
import time
import re
import emoji
import xlrd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
import pymysql
import datetime
import csv
from lxml import etree
import xlwt
from xlutils.copy import copy

chrome_options = Options()
prefs = {
    'profile.default_content_setting_values':
        {
            'notifications': 2
        }
}
chrome_options.add_experimental_option('prefs', prefs)
chrome_options.add_experimental_option('w3c', False)

# MAC版本
# browser = webdriver.Chrome(chrome_options=chrome_options)

# Windows版本
chrome_driver = r"C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe"  # 修改webdriver的绝对位置
browser = webdriver.Chrome(chrome_options=chrome_options, executable_path=chrome_driver)

wait = WebDriverWait(browser, 10)
browser.implicitly_wait(1800)


def isElementExist(element):
    flag = True
    try:
        browser.find_element_by_xpath(element)
        return flag
    except:
        flag = False
        return flag


def review(html):
    dic = {}
    review_num = html.xpath('h2[@class = "CommentTopbar-title"]/text()')  # 评论数量
    review = html.xpath('//ul[@class = "NestComment"]')
    for i in range(len(review)):
        temp = {}
        now_node = html.xpath('//ul[@class = "NestComment"]')[i]
        html2 = etree.tostring(now_node, encoding='utf-8').decode('utf-8')
        html2 = etree.HTML(html2)
        review_author = html2.xpath('//a[@class = "UserLink-link"]/text()')
        review_author_link = html2.xpath('//a[@class = "UserLink-link"]/@href')
        review_contain = html2.xpath('//div[@class = "RichText ztext"]/text()')
        agree = html2.xpath('//button[@class = "Button CommentItemV2-likeBtn Button--plain"]/text()')
        time = html2.xpath('//span[@class = "CommentItemV2-time"]/text()')
        temp['review_author'] = review_author  # 作者
        temp['review_author_link'] = review_author_link  # 作者主页
        temp['review_contain'] = emoji.demojize(str(review_contain))  # 评论内容
        temp['agree'] = agree  # 赞同数
        temp['time'] = time  # 发布时间
        dic[i] = temp
    return dic


def jx(html):
    dic = {}
    title = html.xpath('//h1[@class = "QuestionHeader-title"]/text()')[0]
    question_tags = html.xpath('//div[@class = "Popover"]/div/text()')
    question_description = html.xpath('//div[@class = "QuestionRichText QuestionRichText--expandable"]//p/text()')
    question_description2 = html.xpath('//div[@class = "QuestionRichText QuestionRichText--collapsed"]//p/text()')
    question_description_images = html.xpath(
        '//div[@class = "QuestionRichText QuestionRichText--expandable"]//img/@src')
    Followers = html.xpath('//strong[@class = "NumberBoard-itemValue"]/text()')[0]
    view_times = html.xpath('//strong[@class = "NumberBoard-itemValue"]/text()')[1]
    item = html.xpath('//div[@class = "List-item"]')
    dic['title'] = title  # 题目
    dic['question_tags'] = question_tags  # 问题标签
    dic['question_description'] = emoji.emojize(str(question_description))
    if not dic['question_description']:
        dic['question_description'] = emoji.emojize(str(question_description2))
    dic['question_description_images'] = question_description_images
    dic['Followers'] = Followers
    dic['view_times'] = view_times
    dic['answer'] = {}
    for i in range(1, len(item) + 1):
        temp = {}
        link_path = '//div[@class = "List-item"][' + str(i) + ']//a[@class = "UserLink-link"]/@href'
        name_path = '//div[@class = "List-item"][' + str(i) + ']//a[@class = "UserLink-link"]/text()'
        article_path = '//div[@class = "List-item"][' + str(
            i) + ']//span[@class = "RichText ztext CopyrightRichText-richText"]'
        post_time_path = '//div[@class = "List-item"][' + str(
            i) + ']//div[@class = "ContentItem-time"]/a/span/@data-tooltip'
        agree_path = '//div[@class = "List-item"][' + str(
            i) + ']//button[@class = "Button VoteButton VoteButton--up"]/@aria-label'
        img_path = '//div[@class = "List-item"][' + str(
            i) + ']//span[@class = "RichText ztext CopyrightRichText-richText"]//img/@src'
        try:
            author_link = html.xpath(link_path)[0]
            author_name = html.xpath(name_path)[0]
        except:
            author_link = '匿名'
            author_name = '匿名用户'
        article = html.xpath(article_path)
        article_contain = article[0].xpath('string(.)')
        img = html.xpath(img_path)
        post_time = html.xpath(post_time_path)
        agree = html.xpath(agree_path)
        temp['author_name'] = author_name
        temp['author_link'] = author_link
        temp['article'] = emoji.emojize(str(article_contain))
        temp['img'] = img
        temp['post_time'] = post_time
        temp['agree'] = agree
        dic['answer'][i] = temp
    return dic


def resquest(url):
    readPath = open('zhihuCookies.pickle', 'rb')
    tbCookies = pickle.load(readPath)
    browser.get(url)
    for cookie in tbCookies:
        browser.add_cookie({
            "domain": ".zhihu.com",
            "name": cookie,
            "value": tbCookies[cookie],
            "path": '/',
            "expires": None
        })
    time.sleep(1)
    browser.get(url)
    html = browser.page_source
    if html.find('显示全部') != -1:
        browser.find_element_by_xpath('//button[@class = "Button QuestionRichText-more Button--plain"]').click()
    time.sleep(1)
    html = browser.page_source
    html = etree.HTML(html, parser=etree.HTMLParser(encoding='utf-8'))
    question = jx(html)
    time.sleep(3)
    # pld = html.xpath('//button[@class = "Button ContentItem-action Button--plain Button--withIcon Button--withLabel"]/text()')
    # print(pld)
    for i in range(len(question['answer'])):
        if question['answer'][i + 1]['author_name'].find('盐选') != -1:
            question['answer'][i + 1]['review'] = {}
            continue
        print('第' + str(i) + '个回答')
        question['answer'][i + 1]['review'] = {}
        browser.find_elements_by_xpath(
            '//button[@class = "Button ContentItem-action Button--plain Button--withIcon Button--withLabel"]')[
            0 + 3 * i].click()
        time.sleep(3)
        html = browser.page_source
        flag1 = html.find('下一页')
        html = etree.HTML(html, parser=etree.HTMLParser(encoding='utf-8'))
        page = 1
        review1 = review(html)
        question['answer'][i + 1]['review'][page] = review1
        if flag1 != -1:
            temp = html.xpath('//button[@class = "Button PaginationButton Button--plain"]/text()')
            tempmax = [int(float(x)) for x in temp]
            maxpage = tempmax[-1]
        else:
            maxpage = 1
        while page < maxpage:
            page = page + 1
            browser.find_elements_by_xpath('//button[contains(text(),"下一页")]')[0].click()
            time.sleep(0.5)
            html = browser.page_source
            html = etree.HTML(html, parser=etree.HTMLParser(encoding='utf-8'))
            review1 = review(html)
            question['answer'][i + 1]['review'][page] = review1
            print('review page:', page)
        time.sleep(3)
        print('评论爬完了')
        browser.execute_script("window.scrollTo(800,0)")
        time.sleep(2)
        browser.find_elements_by_xpath(
            '//button[contains(text(),"收起评论")]')[
            0].click()
        print('评论收起')
        # for z in range(len(  browser.find_elements_by_xpath('//button[@aria-label = "关闭"]'))):
        #     browser.find_elements_by_xpath('//button[@aria-label = "关闭"]')[z].click()
        time.sleep(3)
    return question


if __name__ == '__main__':
    path = r'D:\360MoveData\Users\Fanghao\Desktop\Link' ###link的地址
    for dirpath, dirnames, filenames in os.walk(path):
        ljs = filenames
    for lj in ljs:
        txt_place = path + '\\' + lj
        print(txt_place)
        print('start')
        if os.path.exists(lj.split('.')[0] + '.xlsx') == False:
            writebook = xlwt.Workbook()
            sheet1 = writebook.add_sheet('question')
            sheet2 = writebook.add_sheet('answer')
            sheet3 = writebook.add_sheet('review')
            line1 = 0
            line2 = 0
            line3 = 0
            name_line1 = ['排序', '问题', '问题描述', '关注者', '浏览数', '问题图片链接', '问题标签']
            name_line2 = ['问题', '回答正文', '回答者', '回答时间', '点赞数', '回答者链接']
            name_line3 = ['问题', '评论的回答', '评论者', '评论正文', '评论者链接', '点赞数', '评论时间']
            for i in range(len(name_line1)):
                sheet1.write(0, i, name_line1[i])
            for i in range(len(name_line2)):
                sheet2.write(0, i, name_line2[i])
            for i in range(len(name_line3)):
                sheet3.write(0, i, name_line3[i])
            writebook.save(lj.split('.')[0] + '.xlsx')
        with open(txt_place, "r") as f:
            for line in f.readlines():
                # try:
                old_excel = xlrd.open_workbook(lj.split('.')[0] + '.xlsx', formatting_info=True)
                line1 = old_excel.sheet_by_name('question').nrows - 1
                line2 = old_excel.sheet_by_name('answer').nrows - 1
                line3 = old_excel.sheet_by_name('review').nrows - 1
                new_excel = copy(old_excel)
                sheet1 = new_excel.get_sheet(0)
                sheet2 = new_excel.get_sheet(1)
                sheet3 = new_excel.get_sheet(2)
                line1 = line1 + 1
                line = line.strip('\n')  # 去掉列表中每一个元素的换行符
                print('第' + str(line1) + '个问题开始了')
                dic = resquest(line)
                print('第' + str(line1) + '个问题爬完了，开始写入')
                time.sleep(1)
                # except:
                #     continue
                dy_1 = [line1, dic['title'], dic['question_description'], dic['Followers'], dic['view_times'],
                        dic['question_description_images'], dic['question_tags']]
                for temp in range(len(dy_1)):
                    sheet1.write(line1, temp, dy_1[temp])
                for i in dic['answer']:
                    line2 = line2 + 1
                    dy_2 = [line1, dic['answer'][i]['article'], dic['answer'][i]['author_name'],
                            dic['answer'][i]['post_time'], dic['answer'][i]['agree'], dic['answer'][i]['author_link']]
                    for temp in range(len(dy_2)):
                        sheet2.write(line2, temp, dy_2[temp])
                    for j in dic['answer'][i]['review']:
                        for jj in dic['answer'][i]['review'][j]:
                            line3 = line3 + 1
                            dy_3 = [line1, line2, dic['answer'][i]['review'][j][jj]['review_author'],
                                    dic['answer'][i]['review'][j][jj]['review_contain'],
                                    dic['answer'][i]['review'][j][jj]['review_author_link'],
                                    dic['answer'][i]['review'][j][jj]['agree'],
                                    dic['answer'][i]['review'][j][jj]['time']]
                            for temp in range(len(dy_3)):
                                sheet3.write(line3, temp, dy_3[temp])
                new_excel.save(lj.split('.')[0] + '.xlsx')

