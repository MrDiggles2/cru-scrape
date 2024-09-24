import logging
import json

from src.entities import PageItem
from src.utils.psql import get_connection, upsert_page

class DbPipeline:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger("dbpipeline")

    def process_item(self, item: PageItem, spider):
        with get_connection() as conn:
            try:
                page_id = upsert_page(conn, item)
                self.logger.info(f'updated page {page_id}')
            except Exception as e:
                logging.error(e)
            else:
                conn.commit()

class StdoutPipeline:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger("stdoutpipeline")

    def process_item(self, item: PageItem, spider):
        self.logger.info(json.dumps(item.to_dict(), indent=4))
        