# -*- coding: utf-8 -*-
import scrapy
import time
import os
from scrapy_selenium import SeleniumRequest
from scrapy.selector import Selector
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor
import re
from ..items import CollectionItem


class GetdetailsSpider(scrapy.Spider):
    name = 'getdetails'

    # blog = '-'
    # service = '-'
    # services_list = []
    blog_list = []
    final_email = []
    company = ''
    company_link = ''



    def start_requests(self):
        index = 0
        yield SeleniumRequest(
            url="https://www.google.com/",
            wait_time=1000,
            screenshot=True,
            callback=self.parse,
            meta={'index': index},
            dont_filter=True
        )



    def parse(self, response):


        if (os.stat(os.path.abspath(os.curdir) + '\company.txt').st_size != 0 and os.stat(os.path.abspath(os.curdir) + '\websitelink.txt').st_size != 0 ):
            company_inputs = os.path.abspath(os.curdir) + "\company.txt"
            website_inputs = os.path.abspath(os.curdir) + "\websitelink.txt"

            f = open(company_inputs, "r")
            company = f.read().splitlines()

            f = open(website_inputs, "r")
            website = f.read().splitlines()

            self.company = company[0]
            self.company_link = website[0]

            company.pop(0)
            website.pop(0)

            with open(os.path.abspath(os.curdir) + '\company.txt', 'w') as f:
                f.write('')

            new_company = ''
            for b in company:
                new_company += b + "\n"

            with open(os.path.abspath(os.curdir) + '\company.txt', 'a') as f:
                f.write(str(new_company))





            with open(os.path.abspath(os.curdir) + '\websitelink.txt', 'w') as f:
                f.write('')

            new_website = ''
            for b in website:
                new_website += b + "\n"

            with open(os.path.abspath(os.curdir) + '\websitelink.txt', 'a') as f:
                f.write(str(new_website))



            yield SeleniumRequest(
                url=self.company_link,
                wait_time=1000,
                screenshot=True,
                callback=self.parsedata,
                errback=self.savedata,
                dont_filter=True
            )




    def parsedata(self,response):
        time.sleep(10)
        driver = response.meta['driver']
        html = driver.page_source
        response_obj = Selector(text=html)

        links = LxmlLinkExtractor(allow=()).extract_links(response)
        Finallinks = [str(link.url) for link in links]

        # print('services')
        # for s in Finallinks:
        #     # print('\n'*2)
        #     # if('services/' in i):
        #     #     print(i)
        #     # k = s.split('services/')[-1]
        #     # if (k != ''):
        #     self.services_list.append(s)

        # k = s.split('blog/x')[-1]
        #
        # # print(k)
        # if (k == ''):
        #     print('no blogs there')
        # else:
        #     print('blogs are present')

        print('blogs')
        flag = 0
        self.blog_list = []
        for s in Finallinks:
            # print('\n'*2)
            # if('services/' in i):
            #     print(i)
            # k = s.split('blog/')[-1]
            # if (k != ''):
            if ('blog/' in s):
                k = s.split('blog/')[-1]
                if (k != ''):
                    self.blog_list.append(s)
                    flag = 1
            if (flag == 1):
                break

        yield SeleniumRequest(
            url=self.company_link,
            wait_time=1000,
            screenshot=True,
            callback=self.emailtrack,
            errback=self.savedata,
            dont_filter=True
        )




    def emailtrack(self,response):

        driver = response.meta['driver']
        html = driver.page_source
        response_obj = Selector(text=html)

        links = LxmlLinkExtractor(allow=()).extract_links(response)
        Finallinks = [str(link.url) for link in links]
        links = []
        for link in Finallinks:
            if ('Contact' in link or 'contact' in link or 'About' in link or 'about' in link or 'CONTACT' in link or 'ABOUT' in link):
                links.append(link)

        links.append(str(response.url))

        if (len(links) > 0):
            l = links[0]
            links.pop(0)
            uniqueemail = set()

            yield SeleniumRequest(
                url=l,
                wait_time=1000,
                screenshot=True,
                callback=self.finalemail,
                errback=self.savedata,
                # errback=self.errback_finalemail,
                meta={'uniqueemail': uniqueemail,'links':links},
                dont_filter=True
            )
        # else:
        #     finalemail = []
        #     yield SeleniumRequest(
        #         url='https://www.google.com/',
        #         wait_time=1000,
        #         screenshot=True,
        #         callback=self.parse_email,
        #         # errback=self.errback_google,
        #         # meta={'web_name': web_name, 'web_link': web_link, 'web_phone': web_phone,
        #         #       'web_business': web_business, 'site_url': site_url, 'finalemail': finalemail, 'index': index,
        #         #       'web_description': web_description, 'web_directon': web_directon},
        #         dont_filter=True
        #     )

    def finalemail(self,response):
        links = response.meta['links']
        driver = response.meta['driver']
        html = driver.page_source
        response_obj = Selector(text=html)

        uniqueemail = response.meta['uniqueemail']

        flag = 0
        bad_words = ['facebook', 'instagram', 'youtube', 'twitter', 'wiki', 'linkedin']
        for word in bad_words:
            if word in str(response.url):
                # return
                flag = 1
        if (flag != 1):
            html_text = str(response.text)
            mail_list = re.findall('\w+@\w+\.{1}\w+', html_text)
            #
            mail_list = set(mail_list)
            if (len(mail_list) != 0):
                for i in mail_list:
                    mail_list = i
                    if (mail_list not in uniqueemail):
                        uniqueemail.add(mail_list)
                        print("\n"*2)
                        print(uniqueemail)
                        print("\n"*2)
            else:
                pass

        if (len(links) > 0 and len(uniqueemail) < 5):
            print("\n"*2)
            print('hi', len(links))
            print("\n"*2)
            l = links[0]
            links.pop(0)
            yield SeleniumRequest(
                url=l,
                wait_time=1000,
                screenshot=True,
                callback=self.finalemail,
                errback=self.savedata,
                # errback=self.errback_finalemail,
                dont_filter=True,
                meta={'uniqueemail': uniqueemail,'links':links}

            )
        else:
            print("\n" * 2)
            print('hello')
            print("\n"*2)
            emails = list(uniqueemail)
            finalemail = []
            discard = ['robert@broofa.com']
            for email in emails:
                if ('.in' in email or '.com' in email or 'info' in email or '.org' in email or '.app' in email or '.agency' in email):
                    for dis in discard:
                        if (dis not in email):
                            finalemail.append(email)
            print("\n"*2)
            print('final', finalemail)
            print("\n"*2)
            # yield SeleniumRequest(
            #     url='https://www.google.com/',
            #     wait_time=1000,
            #     screenshot=True,
            #     callback=self.parse_email,
            #     errback=self.errback_google,
            #     dont_filter=True,
            #     meta={'finalemail': finalemail}
            #
            # )

            print('\n'*2)
            print(finalemail)
            print('\n' * 2)
            print('blogs',self.blog_list)
            # print('\n' * 2)
            # print('services',self.services_list)
            # print('\n'*2)

            self.final_email = finalemail
            yield SeleniumRequest(
                url='https://www.google.com/',
                wait_time=1000,
                screenshot=True,
                callback=self.savedata,
                errback=self.savedata,
                # errback=self.errback_finalemail,
                # meta={'uniqueemail': uniqueemail, 'links': links},
                dont_filter=True
            )



    def savedata(self,response):


        print('\n'*2)
        print('In save data')
        print('\n' * 2)
        Collection_Item = CollectionItem()

        Collection_Item['company'] = self.company
        Collection_Item['website_link'] = self.company_link

        if(len(self.blog_list)==0):
            Collection_Item['blog'] = '-'
        else:
            Collection_Item['blog'] = self.blog_list[0]

        finalemails = ''
        if(len(self.final_email) == 0):
            finalemails = '-'
        else:
            for idx,email in enumerate(self.final_email):
                if(idx+1 == len(self.final_email)):
                    finalemails += email
                else:
                    finalemails += email + ' , '

        Collection_Item['company_emailId'] = finalemails

        yield Collection_Item

        self.blog_list = []
        self.final_email = []

        yield SeleniumRequest(
            url='https://www.google.com/',
            wait_time=1000,
            screenshot=True,
            callback=self.parse,
            # errback=self.errback_finalemail,
            # meta={'uniqueemail': uniqueemail, 'links': links},
            dont_filter=True
        )

















