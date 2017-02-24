__author__ = 'majid'
import json
from jsonpath_rw import jsonpath, parse


def extract_cell_features(cell):
    extractors_suceeded = set()
    features = [0 for x in range(10)]
    cell_extraction = parse('data_extractors')
    cell_text_path = parse('text[*].result.value')
    cell_text = [match.value for match in cell_text_path.find(cell)]
    cell_data = [match.value for match in cell_extraction.find(cell)]
    for text in cell_text:
        if text.lower() in all_attr_tags:
            extractors_suceeded.add('SEMANTIC_TYPE')
            features[0] = 1
    for fields in cell_data:
        fields = fields.items()
        for key, val in fields:
            if len(val) != 0:
                extractors_suceeded.add(key)
                if key not in all_extractors:
                    all_extractors[key] = len(all_extractors.items())
                features[all_extractors[key]+1] = 1
    # if len(extractors_suceeded) == 0:
    #     return None
    cell['features'] = features
    return features
def put_back_features():
    return None

def add_arrays(a,b):
    return [x+y for (x,y) in zip(a,b)]


all_extractors = {}
tags = open("HT-attribute-labels.json")
all_attr_tags = json.load(tags)
in_file = open("/Users/majid/Desktop/50-pages-out.jl")
out_file = open("/Users/majid/Desktop/50-pages-out-features.jl", 'w')
tables_jsonpath = parse('extractors.tables[*].text[*].result.value.tables[*]')
counter = 0
for line in in_file:
    counter += 1
    line = json.loads(line)
    tables = [match.value for match in tables_jsonpath.find(line)]
    for table in tables:
        print(line['cdr_id'])
        # print(table)
        row_features_aggr = []
        num_cols = table['features']['max_cols_in_a_row']
        num_rows = table['features']['no_of_rows']
        if num_cols == 0 or num_rows == 0:
            continue
        print(num_cols,num_rows)
        col_features_aggr = [[0 for x in range(10)] for xx in range(num_cols)]
        for row_i, row in enumerate(table['rows']):
            row_features = [0 for x in range(10)]
            for i, cell in enumerate(row['cells']):
                cell_features = extract_cell_features(cell)
                row_features = add_arrays(row_features, cell_features)
                row_features_aggr.append(row_features)
                col_features_aggr[i] = add_arrays(col_features_aggr[i], cell_features)
                # if cell_features is not None:
                #     print(cell_features)
            # print('###########')
        # table['features']['row_aggr_features'] = row_features_aggr
        # table['features']['col_aggr_features'] = col_features_aggr
        table['features']['max_sem_type_names_col'] = max([x[0] for x in col_features_aggr])
        table['features']['max_sem_type_names_row'] = max([x[0] for x in row_features_aggr])
        table['features']['avg_recognized_value_row'] = sum([len(filter(lambda x: x>0, xx)) for xx in row_features_aggr])/num_rows
        table['features']['avg_recognized_value_col'] = sum([len(filter(lambda x: x>0, xx)) for xx in row_features_aggr])/num_cols
        print(table['features'])
        print('$$$$$$$$$$$$$$$$$$$$$$$$$')
                # print(cell)
                # print(cell)
    out_file.write(json.dumps(line) + '\n')
print(all_extractors)
out_file.close()
    # print(line)
    # print(line)