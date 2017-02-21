import os
import sys
import codecs
import json

import unittest

from digTableExtractor.table_extractor import TableExtractor
from digExtractor.extractor_processor import ExtractorProcessor


class TestTableExtractor(unittest.TestCase):

    def load_file(self, name):
        file = os.path.join(os.path.dirname(__file__), name)
        text = codecs.open(file, 'r', 'utf-8').read().replace('\n', '')
        return text

    def test_table_extractor(self):
        dig_html = self.load_file("dig.html")
        dig_text = self.load_file("dig.txt")
        doc = {"foo": dig_html}
        e = TableExtractor()
        ep = ExtractorProcessor().set_input_fields('foo')\
                                 .set_output_field('extracted')\
                                 .set_extractor(e)
        updated_doc = ep.extract(doc)
        # with open("dig_out.txt", "w") as f:
        #     f.write(json.dumps(updated_doc['extracted'][0]['value']))
        self.assertEquals(str(updated_doc['extracted'][0]['value']),
                          dig_text)


if __name__ == '__main__':
    unittest.main()