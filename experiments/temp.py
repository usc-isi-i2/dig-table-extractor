__author__ = 'majid'
import json

gt = [json.loads(x) for x in open('50-pages-groundtruth.jl').readlines()]
gt2 = [json.loads(x) for x in open('50-pages-groundtruth-2.jl').readlines()]

gt_dict = dict([(x['cdr_id']+x['fingerprint'], x) for x in gt])
gt2_dict = dict([(x['cdr_id']+x['fingerprint'], x) for x in gt2])

outfile = open('50-pages-groundtruth-final.jl', 'w')

for key, val in gt2_dict.items():
    val['html'] = gt_dict[key]['html']
    if "LAYOUT" in val['labels']:
        try:
            val['labels'].remove("ENTITY")
        except:
            pass
        try:
            val['labels'].remove("RELATIONAL")
        except:
            pass
        try:
            val['labels'].remove("MATRIX")
        except:
            pass
        try:
            val['labels'].remove("LIST")
        except:
            pass
    if "THROW" in val['labels']:
        val['labels'] = ['THROW']
    outfile.write(json.dumps(val) + '\n')
outfile.close()


