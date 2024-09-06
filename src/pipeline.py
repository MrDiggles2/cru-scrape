from item import MyItem
import json
import time
import os

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