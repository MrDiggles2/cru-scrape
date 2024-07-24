from item import MyItem
import json
import time


class MyPipeline:
    file: str

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.file = f'./output/{int(time.time())}.ndjson'

    def process_item(self, item: MyItem, spider):
        with open(self.file, 'w') as f:
            f.write(
                json.dumps({
                    'url': item['url'],
                    'original_date': item['original_date'],
                    'content': item['content']
                }) + '\n'
            )

        return item