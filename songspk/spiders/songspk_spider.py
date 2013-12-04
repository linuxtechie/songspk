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
    allowed_domains = ['songspk.info', 'mp3funda.se', 'downloadming1.com']
    start_urls = ['http://www.songspk.info/latest.html']
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

        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookieJar.jar))
        opener.addheaders = [('User-agent', USER_AGENT)]
        qu = url[0]
#        qu = urllib.quote(url[0], ":/()?")

        while True:
            try:
                self.log(">>>>>>>>>>>>>>>>>>>> URL: %s" % qu)
                resp = opener.open(qu)
                ct = resp.headers['Content-type']
                self.log(">>>>>>>>>>>>>>>>>>>> Content-Type: %s" % ct)
                filename = os.path.split(resp.url)[1]
                resp.close()
                break
            except:
                qu = urllib.quote(qu, ":/")

        if ct == 'application/zip' or ct == 'application/x-zip-compressed':
            torrent = SongspkItem()
            torrent['url'] = qu
            torrent['title'] = title[0]
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
