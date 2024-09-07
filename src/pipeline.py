import json
import time
import os
import logging

from src.entities import PageItem
from src.item import MyItem
from src.utils.psql import get_connection, upsert_page

dir_path = os.path.dirname(os.path.realpath(__file__))
output_path = os.path.join(dir_path, '../output')

class MyPipeline:
    file: str

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.file = f'{output_path}/{int(time.time())}.ndjson'

    def process_item(self, item: MyItem, spider):
        with open(self.file, 'a') as f:
            f.write(
                json.dumps({
                    'url': item['url'],
                    'base_url': item['base_url'],
                    'content': item['content']
                }) + '\n'
            )

            print('Wrote to ${self.file}')

        return item

class DbPipeline:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger("dbpipeline")

    def open_spider(self, spider):
        self.conn = get_connection()

    def close_spider(self, spider):
        self.conn.close()

    def process_item(self, item: PageItem, spider):
        try:
            page_id = upsert_page(self.conn, item)
            self.logger.info(f'updated page {page_id}')
        except Exception as e:
            logging.error(e)
        else:
            self.conn.commit()