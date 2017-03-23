__author__ = 'majid'
import json
from jsonpath_rw import jsonpath, parse
import StringIO
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.cross_decomposition import CCA
from sklearn.preprocessing import label_binarize
import sklearn
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, make_scorer, \
    classification_report, confusion_matrix, f1_score, roc_curve, auc
from sklearn.model_selection import cross_val_score, KFold, train_test_split, StratifiedKFold
from itertools import cycle
from scipy import interp



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

data_labels = {
    'MATRIX': 2,
    'ENTITY': 3,
    'RELATIONAL': 4,
    'LIST': 5
}

def train_classifier(train_features, train_labels):
    cl = RandomForestClassifier(3)
    cl = cl.fit(train_features, train_labels)
    return cl

def predict_labels(cl, features):
    return cl.predict(features), cl.predict_proba(features)

def analyze_classification(true_y, y, probs, keys, features, f_names, classes, gt):
    res = StringIO.StringIO()
    corrects = StringIO.StringIO()
    incorrects = StringIO.StringIO()
    res.write('<html>\n<body>\n')
    for i, (x1, x2) in enumerate(zip(true_y, y)):
        if x1 == x2:
            corrects.write("================================== <br>\n")
            corrects.write('true lab: ' + str(x1) +
                      ' <br> predicted: ' + str(x2) +
                      ' <br> (cdr_id, fingerprint): ' + str(keys[i]) + '<br>\n')
            html = gt[keys[i][0]][keys[i][1]]['html']
            corrects.write(html)
            corrects.write('\n')
            corrects.write('<br> features: ' + str([str(x[1]) + ': ' + str(x[0]) for x in zip(features[i], f_names)]) + '<br>\n')
            corrects.write('<br> probs: ' + str([str(x[1]) + ': ' + str(x[0]) for x in zip(probs[i], classes)]) + '<br>\n')
        else:
            incorrects.write("================================== <br>\n")
            incorrects.write('true lab: ' + str(x1) +
                      ' <br> predicted: ' + str(x2) +
                      ' <br> (cdr_id, fingerprint): ' + str(keys[i]) + '<br>\n')
            html = gt[keys[i][0]][keys[i][1]]['html']
            incorrects.write(html)
            incorrects.write('\n')
            incorrects.write('<br> features: ' + str([str(x[1]) + ': ' + str(x[0]) for x in zip(features[i], f_names)]) + '<br>\n')
            incorrects.write('<br> probs: ' + str([str(x[1]) + ': ' + str(x[0]) for x in zip(probs[i], classes)]) + '<br>\n')
    res.write("############################ corrects: #######################<br>\n")
    res.write(corrects.getvalue())
    res.write("############################ incorrects: #######################<br>\n")
    res.write(incorrects.getvalue())
    res.write('</body>\n</html>')
    return res

def report_feature_importance(features, labels, feature_names):
    cl = RandomForestClassifier(3)
    cl = cl.fit(features, labels)
    fi = cl.feature_importances_
    return sorted(zip(feature_names, fi), key=lambda x: x[1], reverse=True)


def score_classification(clf, true_y, y):
    scorer = classification_report
    return scorer(true_y, y)

def plot_points():
    plt.figure(figsize=(8, 6))
    plot_subfigure(features, Y, 1, "test1", "pca", 'ENTITY', 'MATRIX')
    plot_subfigure(features, Y, 2, "test2", "pca", 'ENTITY', 'RELATIONAL')
    plot_subfigure(features, Y, 3, "test2", "pca", 'OUT-DOMAIN', 'RELATIONAL')
    plot_subfigure(features, Y, 4, "test2", "pca", 'ENTITY', 'MATRIX')
    plt.subplots_adjust(.04, .02, .97, .94, .09, .2)
    plt.show()

def plot_subfigure(X, Y, subplot, title, transform, cl1, cl2):
    if transform == "pca":
        X = PCA(n_components=2).fit_transform(X)
    elif transform == "cca":
        X = CCA(n_components=2).fit(X, Y).transform(X)
    else:
        raise ValueError

    min_x = np.min(X[:, 0])
    max_x = np.max(X[:, 0])

    min_y = np.min(X[:, 1])
    max_y = np.max(X[:, 1])

    # classif = OneVsRestClassifier(SVC(kernel='linear'))
    # classif.fit(X, Y)

    plt.subplot(2, 2, subplot)
    plt.title(title)
    zero_class = np.where(Y == cl1)
    one_class = np.where(Y == cl2)
    plt.scatter(X[:, 0], X[:, 1], s=40, c='gray')
    plt.scatter(X[zero_class, 0], X[zero_class, 1], s=160, edgecolors='b',
               facecolors='none', linewidths=2, label=cl1)
    plt.scatter(X[one_class, 0], X[one_class, 1], s=80, edgecolors='orange',
               facecolors='none', linewidths=2, label=cl2)

    # plot_hyperplane(classif.estimators_[0], min_x, max_x, 'k--',
    #                 'Boundary\nfor class 1')
    # plot_hyperplane(classif.estimators_[1], min_x, max_x, 'k-.',
    #                 'Boundary\nfor class 2')
    plt.xticks(())
    plt.yticks(())

    plt.xlim(min_x - .5 * max_x, max_x + .5 * max_x)
    plt.ylim(min_y - .5 * max_y, max_y + .5 * max_y)
    plt.xlabel('First principal component')
    plt.ylabel('Second principal component')
    plt.legend(loc="upper left")


def produce_roc_curves(clf, features, labelss, classes, n_folds=3):
    # print(classes)
    # print(labelss)
    n_classes = len(classes)+1
    labelss = np.array([classes.index(x) for x in labelss])
    labels = label_binarize(labelss, classes=range(n_classes))[:,:-1]
    n_classes = labels.shape[1]
    print(labels)
    n_samples, n_features = features.shape
    cv = StratifiedKFold(n_splits=n_folds)
    colors = cycle(['cyan', 'indigo', 'seagreen', 'yellow', 'blue', 'darkorange'])
    mean_tpr = 0.0
    lw = 2
    mean_fpr = np.linspace(0, 1, 100)
    i = 0
    fpr = dict()
    tpr = dict()
    roc_auc = dict()

    sum_fpr = dict()
    sum_tpr = dict()
    sum_roc_auc = dict()
    for ii in range(n_classes):
        sum_fpr[ii] = np.linspace(0, 1, 100)
        sum_tpr[ii] = 0.0
        sum_roc_auc[ii] = 0.0
    sum_fpr['micro'] = np.linspace(0, 1, 100)
    sum_tpr['micro'] = 0.0
    sum_roc_auc['micro'] = 0.0

    # print(sum_fpr['micro'])

    for (train, test) in cv.split(features, labelss):
        plt.subplot(n_folds/2+1, n_folds/2+1, i+1)
        # print(xx)
        # color = 'cyan'
        probas_ = clf.fit(features[train], labelss[train]).predict_proba(features[test])
        for ii, color in zip(range(n_classes), colors):
            # Compute ROC curve and area the curve
            fpr[ii], tpr[ii], thresholds = roc_curve(labels[test, ii], probas_[:, ii])
            xx = interp(sum_fpr[ii], fpr[ii], tpr[ii])
            sum_tpr[ii] += xx
            sum_tpr[ii][0] = 0
            # print(xx)
            roc_auc[ii] = auc(fpr[ii], tpr[ii])
            sum_roc_auc[ii] += roc_auc[ii]
            plt.plot(fpr[ii], tpr[ii], color=color, lw=lw-1,
                     label='ROC curve of class {0} (area = {1:0.2f})'
                     ''.format(classes[ii], roc_auc[ii]))

        print(probas_)
        # Compute micro-average ROC curve and ROC area
        fpr["micro"], tpr["micro"], _ = roc_curve(labels[test].ravel(), probas_.ravel())
        roc_auc["micro"] = auc(fpr["micro"], tpr["micro"])
        color = 'red'
        plt.plot(fpr['micro'], tpr['micro'], lw=lw, color=color,
                     label='ROC micro (area = %0.2f)' % (roc_auc['micro']))
        sum_tpr['micro'] += interp(sum_fpr['micro'], fpr['micro'], tpr['micro'])
        sum_tpr['micro'][0] = 0
        sum_roc_auc['micro'] += roc_auc['micro']

        plt.plot([0, 1], [0, 1], 'k--', lw=lw)
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title('Fold {0}'.format(i))
        plt.legend(loc="lower right", prop={'size': 10})
        i += 1

    plt.subplot(n_folds/2+1, n_folds/2+1, n_folds+1)
    for ii, color in zip(range(n_classes), colors):
        plt.plot(sum_fpr[ii], sum_tpr[ii]/n_folds, color=color, lw=lw-1,
                 label='ROC curve of class {0} (area = {1:0.2f})'
                 ''.format(classes[ii], auc(sum_fpr[ii], sum_tpr[ii]/n_folds)))
    color = 'red'
    plt.plot(sum_fpr['micro'], sum_tpr['micro']/n_folds, lw=lw, color=color,
             label='ROC micro (area = %0.2f)' % (auc(sum_fpr['micro'], sum_tpr['micro']/n_folds)))
    plt.plot([0, 1], [0, 1], 'k--', lw=lw)
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('Average on all folds')
    plt.legend(loc="lower right", prop={'size': 10})
    plt.show()


def create_feature_vector(tables, groundtruth):
    features = []
    Y = []
    ids = []
    feature_names = []
    print('num tables: ' + str(len(tables)))
    for t in tables:
        cdr_id = t['cdr_id']
        fingerprint = t['fingerprint']
        labels = []
        if cdr_id in groundtruth:
            if fingerprint in groundtruth[cdr_id]:
                labels = groundtruth[cdr_id][fingerprint]['labels']
        if "THROW" in labels:
            continue
        labels_temp = []
        if "IN-DOMAIN" in labels:
            labels_temp.append("IN-DOMAIN")
        else:
            labels_temp.append("OUT-DOMAIN")
        if "LAYOUT" in labels:
            labels_temp.append("LAYOUT")
        else:
            labels_temp.append("NOT-LAYOUT")
        for l in labels:
            if l in data_labels:
                labels_temp.append(l)
        if len(labels_temp) < 3:
            labels_temp.append("NON-DATA")
        if len(labels_temp) > 3:
            print("labels cannot be more than 3!!")
            exit(-1)
            # if l not in all_labels:
            #     continue
        ff = [x[1] for x in sorted(t['features'].items(), key=lambda x: x[0])]
        if feature_names == []:
            feature_names = [x[0] for x in sorted(t['features'].items(), key=lambda x: x[0])]
        for i,f in enumerate(ff):
            if f == True:
                ff[i] = 1
            if f == False:
                ff[i] = 0
        features.append(ff)
        Y.append(labels_temp)
        ids.append((cdr_id, fingerprint))
    # Y = [all_labels[x] for x in Y if x in all_labels]
    ids = np.array(ids)
    Y = np.array(Y)
    features = np.array(features)
    return features, Y, ids, feature_names

if __name__ == '__main__':
    # groundtruth_file = open('/Users/majid/Downloads/50-pages-groundtruth.jl')
    groundtruth_file = open('50-pages-groundtruth-final.jl')
    input_file = open('50-pages-out-features.jl')
    tables_jsonpath = parse('extractors.tables[*].text[*].result.value.tables[*]')

    groundtruth_file = [json.loads(line) for line in groundtruth_file.readlines()]

    ##########################################
    ## read groundtruth data from file #######
    ##########################################
    groundtruth = {}
    for x in groundtruth_file:
        if x['cdr_id'] in groundtruth:
            groundtruth[x['cdr_id']][x['fingerprint']] = x
        else:
            groundtruth[x['cdr_id']] = {x['fingerprint']: x}


    tables = []
    for line in input_file:
        line = json.loads(line)
        cdr_id = line['cdr_id']
        tt = [match.value for match in tables_jsonpath.find(line)]
        for t in tt:
            t['cdr_id'] = cdr_id
            tables.append(t)
    input_file.close()

    ##########################################
    ## create features and labels vectors ####
    ##########################################
    features, Y, ids, feature_names = create_feature_vector(tables, groundtruth)
    ##########################################
    ## create ROC curves for classifier ######
    #############dfdsfa#uce_roc_curves(clf, features, Y, classes)
    # clf = RandomForestClassifier(10)
    # classes = ["IN-DOMAIN", "OUT-DOMAIN"]
    # classes2 = ["LAYOUT", "NOT-LAYOUT"]
    # classes3 = ["ENTITY", "MATRIX", "RELATIONAL", "LIST", "NON-DATA"]
    # produce_roc_curves(clf, features, Y[:,0], classes)
    # exit(0)
    ###########################################################
    ## analyze feature importance, and false predictions ######
    ###########################################################

    cv = StratifiedKFold(n_splits=10)
    Y = Y[:,0]
    for (train, test) in cv.split(features, Y):
        zip(Y[train],ids[train])
        X_train, X_test, y_train, y_test = features[train], features[test], zip(Y[train],ids[train]), zip(Y[test],ids[test])

        y_train, train_keys = [x[0] for x in y_train], [x[1] for x in y_train]
        y_test, test_keys = [x[0] for x in y_test], [x[1] for x in y_test]

        cl = train_classifier(X_train, y_train)
        print(feature_names)
        print report_feature_importance(features, Y, feature_names)

        y_pred, probs = predict_labels(cl, X_test)
        classes = cl.classes_
        print score_classification(cl, y_test, y_pred)
        print('################################# detailed report #################')
        logfile = open('report.htm', 'w')

        analyze_report = analyze_classification(y_test, y_pred, probs, test_keys, X_test, feature_names, classes, groundtruth).getvalue()
        # print(analyze_report)
        logfile.write(analyze_report.encode('utf-8'))
    exit(0)
    # plot_points()

    # print y_pred
    # print confusion_matrix(y_test, y_pred)
    # print classification_report(y_test, y_pred)
    # print scorer(rf_cl, features, Y)
    # score = cross_val_score(rf_cl, features, Y, cv=2).mean()
    # print score


