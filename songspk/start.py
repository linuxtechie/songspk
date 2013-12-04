from twisted.internet import reactor
from scrapy.crawler import Crawler
from scrapy.settings import CrawlerSettings
from scrapy import log, signals
from spiders.songspk_spider import SongsPKSpider
from scrapy.xlib.pydispatch import dispatcher

def stop_reactor():
    reactor.stop()

dispatcher.connect(stop_reactor, signal=signals.spider_closed)

spider = SongsPKSpider(domain='aqaq.com')
crawler = Crawler(CrawlerSettings())
crawler.configure()
crawler.crawl(spider)
crawler.start()
log.start(loglevel=log.DEBUG)
log.msg("------------>Running reactor")
result = reactor.run()
print result
log.msg("------------>Running stoped")
