__author__ = 'majid'
import sys
import json
import re
from jsonpath_rw import jsonpath, parse

all_labels = set([
    "LAYOUT",
    "IN-DOMAIN",
    "ENTITY",
    "RELATIONAL",
    "MATRIX",
    "LIST"
])

# sys.path.append('/Users/majid/DIG/dig-table-extractor/')
# from digTableExtractor.table_extractor import TableExtractor
# from digExtractor.extractor_processor import ExtractorProcessor
# from digExtractor.extractor import Extractor

if __name__ == '__main__':
    # annotated = open('/Users/majid/DIG/dig-groundtruth-data/annotated-tables/HT/annotated_tables_compact.jl').readlines()
    # annotated = dict([(json.loads(x)['cdr_id'],json.loads(x)) for x in annotated])
    infile = open('50-pages-groundtruth-final.jl')
    # outfile = open('/Users/majid/Desktop/50-pages-groundtruth.jl', 'w')
    html_file = open('50-pages-groundtruth.htm', 'w')
    # table_extractor_init = TableExtractor().set_metadata({'type': 'table'})
    # extractor = Extractor(table_extractor_init, 'raw_content', 'extractors.tables.text')
    # processor = ExtractorProcessor() \
    #             .set_input_fields('raw_content') \
    #             .set_output_field('extractors.tables.text') \
    #             .set_extractor(table_extractor_init) \
    #             .set_name('TABLE')
    html_file.write('<html>\n')
    html_file.write('''
        <head>
          <script src = "https://code.jquery.com/jquery-1.10.2.js"></script>
        <script>
            $(function() {
                $("#submitter").click(function(){
                    // var txtFile =new File(file_name);
                    // var tables, index, i, types;
                    var cdrid, fingerprint, type, domain, layout, not_good;
                    var alltext = "";
                    tables = document.getElementsByName('table_annotation__');
                    $('#output_temp').val('here');
                    for (index = 0; index < tables.length; ++index){
                        cdrid = tables[index].getElementsByTagName("cdrid")[0].getAttribute("value");
                        fingerprint = tables[index].getElementsByTagName("fingerprint")[0].getAttribute("value");
                        not_good = null;
                        layout = null;
                        domain = null;
                        type = null;
                        // deal with inputs[index] element.
                        inputs = tables[index].getElementsByTagName("input");
                        for (i = 0 ; i < inputs.length ; ++i){

                            if(inputs[i].name == "type_")
                                if(inputs[i].checked)
                                     type = inputs[i].value;
                            if(inputs[i].name == "domain_")
                                if(inputs[i].checked)
                                     domain = inputs[i].value;
                            if(inputs[i].name == "layout_")
                                if(inputs[i].checked)
                                     layout = inputs[i].value;
                            if(inputs[i].name == "not_good")
                                if(inputs[i].checked)
                                     not_good = inputs[i].value;
                        }
                        labels = [];
                        if(not_good != null)
                            labels.push(not_good);
                        if(layout != null)
                            labels.push(layout);
                        if(domain != null)
                            labels.push(domain);
                        if(type != null)
                            labels.push(type);
                        jobj = {};
                        jobj["cdr_id"] = cdrid;
                        jobj["fingerprint"] = fingerprint;
                        jobj["labels"] = labels;
                        alltext += JSON.stringify(jobj) + "\\n";
                    }
                    // alltext += 'majid';
                   $('#output_temp').val(alltext);
                   // txtFile.close();
                });
            });
        </script>
        </head>\n
    ''')
    html_file.write('<body>\n')
    # Extractor(table_extractor_init, 'raw_content', 'extractors.tables.text')
    for line_num, line in enumerate(infile):
        line = json.loads(line)
        # key = line['cdr_id']
        # tables = processor.extract(line)
        # line.update(tables)
        # tables_jsonpath = parse('extractors.tables[*].text[*].result.value.tables[*]')
        # unan_tables = [match.value for match in tables_jsonpath.find(line)]
        # annotated_tables = {}
        # if key in annotated:
        #     anline = annotated[key]
        #     an_tables = [match.value for match in tables_jsonpath.find(anline)]
        # for i, t in enumerate(unan_tables):
        #     print(t)
        # fingerprint = t['fingerprint']
        # jobj =  'header_cols': []}
        html_file.write('##############################################################################<br>\n'+
                        '##############################################################################<br>\n'+
                        '##############################################################################<br>\n')
        html_file.write('<div style="border:1px solid red;" name="table_annotation__">\n')
        html_file.write('<div style="border:1px solid brown;">\n')
        html_file.write('line_num: ' + str(line_num+1) + '<br>\n')
        html_file.write('cdr_id: <cdrid value="' + str(line['cdr_id']) + '">' + str(line['cdr_id']) + '</cdrid><br>\n')
        html_file.write('fingerprint: <fingerprint value="' + str(line['fingerprint']) + '">' + str(line['fingerprint']) + '</fingerprint><br>\n')

        labels = line['labels']
        throw = False
        out_domain = False
        layout = False
        type = 'ENTITY'


        text = """
        <div style="border:2px solid red;width: 100%;float:left">
            annotate: \n
            <div style="width: 100%;float:left">
            <form>\n
                <input type="checkbox" name="not_good" value="THROW">  throw away this table\n
            </form>\n
            </div>
            <div style="width: 30%;float:left">
            <form>\n
                <input type="radio" name="domain_" value="IN-DOMAIN"> IN-DOMAIN<br>\n
                <input type="radio" name="domain_" value="OUT-DOMAIN"> OUT-DOMAIN<br>\n
            </form>
            </div>
            <div style="width: 30%;float:left">
            <form>\n
                <input type="radio" name="layout_" value="LAYOUT"> LAYOUT<br>\n
                <input type="radio" name="layout_" value="NOT-LAYOUT"> NOT-LAYOUT\n
            </form>
            </div>
            <div style="width: 30%;float:left">
            <form>\n
                <input type="radio" name="type_" value="ENTITY"> ENTITY<br>\n
                <input type="radio" name="type_" value="RELATIONAL"> RELATIONAL<br>\n
                <input type="radio" name="type_" value="MATRIX"> MATRIX<br>\n
                <input type="radio" name="type_" value="LIST"> LIST\n
            </form>\n
            </div>
        </div>
        """
        for x in labels:
            x = '"' + x + '"'
            if x in text:
                args_ = text.split(x)
                text = args_[0] + x +' checked' + args_[1]

        html_file.write(text)

        html_file.write('labels: ' + str(line['labels']) + '<br>\n')
        # html_file.write('header rows: ' + str(line['header_rows']) + '<br>\n')
        # html_file.write('header columns: ' + str(line['header_cols']) + '<br>\n')
        html_file.write('</div>\n')
        temp = line['html'].encode('utf-8')
        # temp = re.sub('img src="(.+)"', 'img src=""', temp)
        temp = re.sub('<table [^<>]+>', '<table border="1">', temp)
        temp = re.sub('<table>', '<table border="1">', temp)
        # temp = re.sub('color="[#0-9A-Za-z]+"', '#000000', temp)
        html_file.write(temp + '\n')
        html_file.write('</div>\n')
    html_file.write('''
        <button id="submitter"> submit </button>
        <textarea rows="4" cols="50" id="output_temp">
        </textarea>
    ''')
    html_file.write('\n</body>\n</html>\n')
