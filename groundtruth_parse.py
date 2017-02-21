from bs4 import BeautifulSoup
import ast
import json
import re

from digTableExtractor.table_extractor import TableExtractor
from digTableExtractor.table_ext_helper import table_decompose
from digExtractor.extractor_processor import ExtractorProcessor

path = '../'
#groundtruth = path + 'sample_nyu_10.jl'
#groundtruth = path + 'nyu-ddindex-fall2016qpr-cdr-deduped.jl'
groundtruth = path + 'pedro/gt_ads_nov_ab.jl'
#groundtruth = path + 'soccer_tables.jl'

#file_out = path + 'sample_output.txt'
#file_out = path + 'tables_sample3.txt'
#file_out = path + 'tables_sample4.html'
#file_out = path + 'table_extractions_1000_nyu_re_col_new.html'
file_out = path + 'table_extractions_gt_ads_nov_ab_new.html'
#file_out = path + 'table_extractions_soccer.html'

# Computes mean of a list of numbers
def mean(numbers):
    return float(sum(numbers)) / max(len(numbers), 1)

# Check if a string contains a digit
_digits = re.compile('\d')
def contains_digits(d):
    return bool(_digits.search(d))


# Output json
def output_json(file_in, file_out):
	f = open(file_in, 'r')
	outfile = open(file_out, 'wb')

	for index, line in enumerate(f):
		print index
	 	try:
			line = ast.literal_eval(line)
			html_doc = {"foo": line['raw_content']}
			e = TableExtractor()
			ep = ExtractorProcessor().set_input_fields('foo').set_output_field('extracted').set_extractor(e)
			updated_doc = ep.extract(html_doc)
			doc = updated_doc['extracted'][0]['value']
			outfile.write(json.dumps(doc))
			outfile.write("\n")
		except Exception as e:
			continue

	outfile.close()


#Output complement html without the tables
def output_complement_html(file_in, file_out):
	f = open(file_in, 'r')
	outfile = open(file_out, 'wb')

	for index, line in enumerate(f):
		print index
		line = ast.literal_eval(line)
		html_doc = line['raw_content']
		html = table_decompose(html_doc)
		line["raw_without_data_table"] = str(html)
		outfile.write(json.dumps(line))
		outfile.write("\n")

	outfile.close()


#Output tables as html
def output_tables(file_in, file_out):
	f = open(file_in, 'r')
	outfile = open(file_out, 'wb')

	style = """<head>
	<style>
	table {
	    border-collapse: collapse;
	}

	table, td, th {
	    border: 2px solid black;
	}
	</style>
	</head>"""
	outfile.write(style)

	count = 0
	img_tab_count = 0
	href_tab_count = 0
	input_tab_count = 0
	select_tab_count = 0
	colon_tab_count = 0
	empty_tab_count = 0
	colspan_tab_count = 0

	for index, line in enumerate(f):
		print index
		try:
			line = ast.literal_eval(line)
			html_doc = {"foo": line['raw_content']}
			e = TableExtractor()
			ep = ExtractorProcessor().set_input_fields('foo').set_output_field('extracted').set_extractor(e)
			updated_doc = ep.extract(html_doc)
			doc = updated_doc['extracted'][0]['value']
		except Exception as e:
			continue
		if doc is None:
			continue
		tables = doc["tables"]
		count += len(tables)
		for table in tables:
			rows = table["rows"]
			outfile.write("CDR: " + line['_id'] + "<br>")
			outfile.write('<table>\n')
			for row in rows:
				outfile.write('<tr>\n')
				cells = row["cells"]
				for cell in cells:
					outfile.write(cell["cell"])
					outfile.write('\n')
				outfile.write('</tr>\n')
			features = table["features"]
			for key, val in features.iteritems():
				outfile.write(key + ': ' + str(val))
				outfile.write('<br>')
			if(features["no_of_rows"] == 0):
				empty_tab_count += 1
			if(features["ratio_of_img_tags_to_cells"] >= 1.0):
				img_tab_count += 1
			if(features["ratio_of_href_tags_to_cells"] >= 1.0):
				href_tab_count += 1
			if(features["ratio_of_input_tags_to_cells"] > 0.0):
				input_tab_count += 1
			if(features["ratio_of_select_tags_to_cells"] > 0.0):
				select_tab_count += 1
			if(features["ratio_of_colons_to_cells"] >= 0.3):
				colon_tab_count += 1
			if(features["ratio_of_colspan_tags_to_cells"] > 0.0):
				colspan_tab_count += 1


			outfile.write("</table>")
			outfile.write("<hr><hr>")

	outfile.write("No.of tables: {0}".format(count) + '<br>')
	outfile.write("No.of tables with empty rows: {0}".format(empty_tab_count) + '<br>')
	outfile.write("No.of tables with img >= 1.0: {0}".format(img_tab_count) + '<br>')
	outfile.write("No.of tables with href >= 1.0: {0}".format(href_tab_count) + '<br>')
	outfile.write("No.of tables with input > 0.0: {0}".format(input_tab_count) + '<br>')
	outfile.write("No.of tables with select > 0.0: {0}".format(select_tab_count) + '<br>')
	outfile.write("No.of tables with colons >= 0.3: {0}".format(colon_tab_count) + '<br>')
	outfile.write("No.of tables with colspan > 0.0: {0}".format(colspan_tab_count) + '<br>')
	outfile.close()


if __name__ == '__main__':
    output_tables(groundtruth, file_out)