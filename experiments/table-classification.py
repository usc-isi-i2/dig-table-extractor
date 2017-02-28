__author__ = 'majid'
import json
from jsonpath_rw import jsonpath, parse
import StringIO
import sklearn
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, make_scorer, \
    classification_report, confusion_matrix, f1_score
from sklearn.model_selection import cross_val_score, KFold, train_test_split
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

def train_classifier(train_features, train_labels):
    cl = RandomForestClassifier(3)
    cl = cl.fit(train_features, train_labels)
    return cl

def predict_labels(cl, features):
    return cl.predict(features)

def analyze_classification(true_y, y, keys):
    res = StringIO.StringIO()
    for i, (x1, x2) in enumerate(zip(true_y, y)):
        if x1 != x2:
            res.write('true lab: ' + str(x1) +
                      ' | predicted: ' + str(x2) +
                      ' | (cdr_id, fingerprint): ' + str(keys[i]) + '\n')
    return res

def score_classification(clf, true_y, y):
    scorer = classification_report
    return scorer(true_y, y)

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
    # print(groundtruth)


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
    ids = []
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
            for i,f in enumerate(ff):
                if f == True:
                    ff[i] = 1
                if f == False:
                    ff[i] = 0
            features.append(ff)
            Y.append(l)
            ids.append((cdr_id, fingerprint))

    input_file.close()
    # Y = [all_labels[x] for x in Y if x in all_labels]
    # print([len(x) for x in features])

    # print(sklearn.__version__)
    Y = np.array(Y)
    features = np.matrix(features)

    X_train, X_test, y_train, y_test = train_test_split(features, Y,
                                                        train_size=0.75,
                                                        random_state=42)


    cl = train_classifier(X_train, y_train)

    y_pred = predict_labels(cl, X_test)
    print score_classification(cl, y_test, y_pred)
    print('################################# detailed report #################')
    print analyze_classification(y_test, y_pred, ids).getvalue()

    # print y_pred
    # print confusion_matrix(y_test, y_pred)
    # print classification_report(y_test, y_pred)
    # print scorer(rf_cl, features, Y)
    # score = cross_val_score(rf_cl, features, Y, cv=2).mean()
    # print score


