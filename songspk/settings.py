# Scrapy settings for songspk project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'songspk'

SPIDER_MODULES = ['songspk.spiders']
NEWSPIDER_MODULE = 'songspk.spiders'

COOKIES_DEBUG = True

# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = 'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:25.0) Gecko/20100101 Firefox/25.0'

ITEM_PIPELINES = {
    'songspk.pipeline.SaveFile.SaveFilePipeline': 300,
}
