from digExtractor.extractor import Extractor
from itertools import ifilter
import copy 
import table_ext_helper

class TableExtractor(Extractor):

    def __init__(self):
        self.renamed_input_fields = 'html'
        self.metadata = {'extractor': "table"}

    def extract(self, doc):
        try:
            if 'html' in doc:
                html = doc['html']
                return table_ext_helper.table_extract(html)
            else:
                return ''
        except Exception, e:
            print 'Error in extracting tables %s' % e
            return ''

    def get_metadata(self):
        return copy.copy(self.metadata)

    def set_metadata(self, metadata):
        self.metadata = metadata
        return self

    def get_renamed_input_fields(self):
        return self.renamed_input_fields;