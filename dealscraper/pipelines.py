from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem
import mysql.connector


class DataCleanerPipeline:

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        name = adapter['name'].lower().replace('tesco', '')
        adapter['name'] = name.strip().lstrip().rstrip()

        if '&amp;' in adapter['name']:
            adapter['name'] = adapter['name'].replace('&amp;', '&')

        if 'Clubcard Price' in adapter['discount']:
            adapter['discount'] = adapter['discount'].split('Clubcard Price')[0].strip()

        return item


class DuplicatesPipeline:

    def __init__(self):
        self.names_seen = set()

    def process_item(self, item, spider):

        if 'name' not in item:
            raise DropItem("Product name is required.")
        elif 'price' not in item:
            raise DropItem("Product price is required.")
        elif 'discount' not in item:
            item['discount'] = 'No discount available.'
        else:
            adapter = ItemAdapter(item)

        if adapter['name'] in self.names_seen:
            raise DropItem(f"Duplicate item found: {adapter['name']}")
        else:
            self.names_seen.add(adapter['name'])
            return item


class SavingToMySQLPipeline(object):

    def __init__(self):
        self.create_connection()
        self.create_table()

    def create_connection(self):
        self.conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='1234',
            database='tesco_products'
        )
        self.curr = self.conn.cursor()

    def create_table(self):
        self.curr.execute("""DROP TABLE IF EXISTS tesco_products""")
        self.curr.execute("""create table tesco_products (name text,price text,discount text)""")

    def process_item(self, item, spider):
        self.store_db(item)
        return item

    def store_db(self, item):
        adapter = ItemAdapter(item)
        self.curr.execute(""" insert into tesco_products values (%s,%s,%s)""", (
            adapter["name"],
            adapter["price"],
            adapter["discount"],
        ))
        self.conn.commit()
