from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem


class DuplicatesPipeline:

    def __init__(self):
        self.names_seen = set()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        if adapter['name'] in self.names_seen:
            raise DropItem(f"Duplicate item found: {adapter['name']}")
        else:
            self.names_seen.add(adapter['name'])
            return item
