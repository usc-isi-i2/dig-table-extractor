__author__ = 'majid'
import json
from jsonpath_rw import jsonpath, parse
import sklearn
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score, KFold
import numpy as np

all_labels = {
    'NON-DATA': 0,
    'OUT-DOMAIN': 1,
    'MATRIX': 2,
    'ENTITY': 3,
    'RELATIONAL': 4,
    'LIST': 5,
    'LAYOUT': 6
}

if __name__ == '__main__':
    groundtruth_file = open('/Users/majid/Desktop/50-pages-groundtruth.jl')
    input_file = open('/Users/majid/Desktop/50-pages-out.jl')
    tables_jsonpath = parse('extractors.tables[*].text[*].result.value.tables[*]')

    groundtruth_file = [json.loads(line) for line in groundtruth_file.readlines()]

    ## read groundtruth data from file
    groundtruth = {}
    for x in groundtruth_file:
        if x['cdr_id'] in groundtruth:
            groundtruth[x['cdr_id']][x['fingerprint']] = x
        else:
            groundtruth[x['cdr_id']] = {x['fingerprint']: x}
    print(groundtruth)


    tables = []
    for line in input_file:
        line = json.loads(line)
        cdr_id = line['cdr_id']
        tt = [match.value for match in tables_jsonpath.find(line)]
        for t in tt:
            t['cdr_id'] = cdr_id
            tables.append(t)
    features = []
    Y = []
    for t in tables:
        cdr_id = t['cdr_id']
        fingerprint = t['fingerprint']
        labels = []
        if cdr_id in groundtruth:
            if fingerprint in groundtruth[cdr_id]:
                labels = groundtruth[cdr_id][fingerprint]['labels']

        for l in labels:
            if l not in all_labels:
                continue
            ff = [x[1] for x in sorted(t['features'].items(), key=lambda x: x[0])]
            print(t['id'], ff)
            for i,f in enumerate(ff):
                if f == True:
                    ff[i] = 1
                if f == False:
                    ff[i] = 0
            features.append(ff)
            Y.append(l)

    input_file.close()
    Y = [all_labels[x] for x in Y if x in all_labels]
    print([len(x) for x in features])
    print(Y)
    print(sklearn.__version__)
    Y = np.array(Y)
    features = np.matrix(features)
    rf_cl = RandomForestClassifier(10)
    score = cross_val_score(rf_cl, features, Y, cv=5).mean()
    print score

