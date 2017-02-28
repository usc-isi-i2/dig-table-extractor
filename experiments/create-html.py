__author__ = 'majid'
import sys
import json
import re
from jsonpath_rw import jsonpath, parse


# sys.path.append('/Users/majid/DIG/dig-table-extractor/')
from digTableExtractor.table_extractor import TableExtractor
from digExtractor.extractor_processor import ExtractorProcessor
from digExtractor.extractor import Extractor

if __name__ == '__main__':
    annotated = open('/Users/majid/DIG/dig-groundtruth-data/annotated-tables/HT/annotated_tables_compact.jl').readlines()
    annotated = dict([(json.loads(x)['cdr_id'],json.loads(x)) for x in annotated])
    infile = open('/Users/majid/DIG/table-extraction/50-pages-with-tables-raw.json')
    outfile = open('/Users/majid/Desktop/50-pages-groundtruth.jl', 'w')
    html_file = open('/Users/majid/Desktop/50-pages-groundtruth.htm', 'w')
    table_extractor_init = TableExtractor().set_metadata({'type': 'table'})
    # extractor = Extractor(table_extractor_init, 'raw_content', 'extractors.tables.text')
    processor = ExtractorProcessor() \
                .set_input_fields('raw_content') \
                .set_output_field('extractors.tables.text') \
                .set_extractor(table_extractor_init) \
                .set_name('TABLE')
    html_file.write('<html>\n<body>\n')
    # Extractor(table_extractor_init, 'raw_content', 'extractors.tables.text')
    for line_num, line in enumerate(infile):
        line = json.loads(line)
        key = line['_id']
        tables = processor.extract(line)
        line.update(tables)
        tables_jsonpath = parse('extractors.tables[*].text[*].result.value.tables[*]')
        unan_tables = [match.value for match in tables_jsonpath.find(line)]
        annotated_tables = {}
        if key in annotated:
            anline = annotated[key]
            an_tables = [match.value for match in tables_jsonpath.find(anline)]
        for i, t in enumerate(unan_tables):
            print(t)
            fingerprint = t['fingerprint']
            jobj = {'cdr_id': key,
                    'fingerprint': fingerprint,
                    'labels': [],
                    'html': t['html'],
                    'header_rows': [],
                    'header_cols': []}
            if len(an_tables) == len(unan_tables):
                if 'labels' in an_tables[i]:
                    jobj['labels'] = an_tables[i]['labels']
                    jobj['header_rows'] = an_tables[i]['header_rows']
                    jobj['header_cols'] = an_tables[i]['header_cols']
            html_file.write('##############################################################################\n'+
                            '##############################################################################\n'+
                            '##############################################################################\n')
            html_file.write('<div style="border:1px solid red;">\n')
            html_file.write('<div style="border:1px solid brown;">\n')
            html_file.write('line_num: ' + str(line_num) + '<br>\n')
            html_file.write('cdr_id: ' + str(jobj['cdr_id']) + '<br>\n')
            html_file.write('fingerprint: ' + str(jobj['fingerprint']) + '<br>\n')
            html_file.write('labels: ' + str(jobj['labels']) + '<br>\n')
            html_file.write('header rows: ' + str(jobj['header_rows']) + '<br>\n')
            html_file.write('header columns: ' + str(jobj['header_cols']) + '<br>\n')
            html_file.write('</div>\n')
            temp = re.sub('img src="(.+)"', 'img src=""',t['html'])
            temp = re.sub('<table [^<>]+>', '<table border="1">', temp)
            temp = re.sub('<table>', '<table border="1">', temp)
            temp = re.sub('color="[#0-9A-Za-z]+"', '#000000', temp)
            html_file.write(temp + '\n')
            html_file.write('</div>')
            outfile.write(json.dumps(jobj) + '\n')
    html_file.write('\n</body>\n</html>\n')
    outfile.close()
    print('here22')
