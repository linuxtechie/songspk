from scrapy.spider import BaseSpider
from scrapy.selector import Selector, HtmlXPathSelector
from songspk.items import SongspkItem
from scrapy.http import Request
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.http.cookies import CookieJar
from songspk.settings import USER_AGENT

import re,pdb,os,urllib2,urllib

class SongsPKSpider(BaseSpider):
    name = 'songspk'
    allowed_domains = ['songspk.name', 'songspk.info', 'mp3funda.se', 'downloadming1.com']
#    start_urls = ['http://www.songspk.info/latest.html', 'http://www.songspk.name/bollywood_music_compilations.html']
    start_urls = ['http://www.songspk.name/bollywood_music_compilations.html']
    cookieJar = None
    cookie = []
    cl = []

    
    def storeCookie(self, response):
        cl = response.headers.getlist('Set-Cookie')
        if not cl:
          return
        msg = "Received cookies from: %s" % response + os.linesep
        self.log(msg)
        for c in cl:
            msg  = ("Set-Cookie: %s" % c)
            self.log(msg)
            self.cookie.append(c)



    def parse(self, response):
        self.cookieJar = response.meta.setdefault('cookie_jar', CookieJar())
        self.cookieJar.extract_cookies(response, response.request)
        self.log("Printing cookie information");
        for cookie in self.cookieJar:
            self.cl.append(cookie)
            self.log('cookies %s' % cookie)
        self.log("Printing cookie information done");
        self.storeCookie(response)
        sel = Selector(response)
        if len(sel.xpath('//*[@height="154"]/script')) > 0:
            return self.parseSongsPKInfo(sel, response)
        if len(sel.xpath('//*[@class="manu-albums"]/li/ul/li/a/@href').extract()) > 0 :
            return self.parseSongsPKName(sel, response)

    def parseSongsPKName(self, sel, response):
        for a in sel.xpath('//*[@class="manu-albums"]/li/ul/li/a/@href'):
            yield Request("http://www.songspk.name/"+a.extract(), callback=self.parseSongsPKName_second)

    def parseSongsPKName_second(self, response):
        sel = Selector(response)
        b = sel.xpath('//td[@width="59%"]/font/b')
        title = ""
        url = ""
        if len(b) == 0:
            b = sel.xpath('//div[@class="song-title-h4"]')
            self.log("Length: " + str(len(b)))
        if len(b) > 1:
            for a in b:
                for c in a.xpath('.//a'):
                    if "320" in " ".join(c.xpath('.//text()').extract()):
                        tt = " ".join(c.xpath('.//text()').extract())
                        title = ' '.join(tt.split())
                        title = title.strip("\n\t")
                        url = c.xpath('.//@href').extract()[0]

        else:
            url = b[0].xpath('.//@href').extract()[0]
            title = " ".join(b[0].xpath('.//text()').extract())
            title = " ".join(title.split())
          
        self.log("2222>>>> Title : %s URL :%s " % (title, url))
        return self.getFileName(url, title)


    def parseSongsPKInfo(self, sel, response):
        scriptline = sel.xpath('//*[@height="154"]/script').extract()[0].split('\n')
        b=re.compile("leftrightslide.*href=\"(.*)\" target.*")
        items = []
        for line in scriptline:
            if b.match(line) == None:
                continue
            t=b.match(line).group(1)
            link = 'http://www.songspk.info/' + t
            yield Request(link, callback=self.parse_category)
    
    def parse_category(self, response):
        sel = Selector(response)
        title = sel.xpath('/html/body/table/tr[2]/td/table/tr/td[3]/table/tr[16]/td/table/tr[2]/td/table/tr[2]/td/div/a/text()').extract()
        url = sel.xpath('/html/body/table/tr[2]/td/table/tr/td[3]/table/tr[16]/td/table/tr[2]/td/table/tr[2]/td/div/a/@href').extract()
        return self.getFileName(url[0], title[0])

    def getFileName(self, url, title):
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookieJar.jar))
        opener.addheaders = [('User-agent', USER_AGENT)]
        qu = url
#        qu = urllib.quote(url[0], ":/()?")

        while True:
            try:
                resp = opener.open(qu)
                ct = resp.headers['Content-type']
                filename = os.path.split(resp.url)[1]
                resp.close()
                break
            except:
                qu = urllib.quote(qu, ":/")

        if ct == 'application/zip' or ct == 'application/x-zip-compressed':
            torrent = SongspkItem()
            torrent['url'] = qu
            torrent['title'] = title
            torrent['cookie'] = self.cl
            torrent['filename'] = urllib.unquote(filename)
            yield torrent
            return
        yield Request(qu, callback=self.parse_category)


    def save_pdf(self, response):
        path = self.get_path(response.url)
        self.log("Path: " + path)
        print path
#        with open(path, "wb") as f:
#          f.write(response.body)
