import logging

from src.entities import PageItem
from src.utils.psql import get_connection, upsert_page

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