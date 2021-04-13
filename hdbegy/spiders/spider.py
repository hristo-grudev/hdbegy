import scrapy

from scrapy.loader import ItemLoader

from ..items import HdbegyItem
from itemloaders.processors import TakeFirst


class HdbegySpider(scrapy.Spider):
	name = 'hdbegy'
	start_urls = ['https://www.hdb-egy.com/hdb-news/']

	def parse(self, response):
		post_links = response.xpath('//article//article')
		for post in post_links:
			url = post.xpath('.//a[@class="more-link"]/@href').get()
			title = post.xpath('.//h2//text()[normalize-space()]').get()
			date = post.xpath('.//span[@class="published"]/text()').get()
			yield response.follow(url, self.parse_post, cb_kwargs={'date': date, 'title': title})

		next_page = response.xpath('//div[@class="alignleft"]/a/@href').getall()
		yield from response.follow_all(next_page, self.parse)

	def parse_post(self, response, title, date):
		description = response.xpath('//div[@class="et_pb_text_inner"]//text()[normalize-space()]').getall()
		description = [p.strip() for p in description if '{' not in p]
		description = ' '.join(description).strip()

		item = ItemLoader(item=HdbegyItem(), response=response)
		item.default_output_processor = TakeFirst()
		item.add_value('title', title)
		item.add_value('description', description)
		item.add_value('date', date)

		return item.load_item()
