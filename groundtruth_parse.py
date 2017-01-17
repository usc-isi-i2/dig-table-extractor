from bs4 import BeautifulSoup
import ast
import json
import re

from digTableExtractor.table_extractor import TableExtractor
from digTableExtractor.table_ext_helper import table_decompose
from digExtractor.extractor_processor import ExtractorProcessor

path = '../'
groundtruth = path + 'sample_nyu_10.jl'
#groundtruth = path + 'nyu-ddindex-fall2016qpr-cdr-deduped.jl'
#groundtruth = path + 'pedro/gt_ads_nov_aa.jl'

#file_out = path + 'sample_output.txt'
#file_out = path + 'tables_sample3.txt'
file_out = path + 'tables_sample3.html'
#file_out = path + 'table_extractions_1000_nyu_re_col.html'

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
			tdcount = 0
			max_tdcount = 0
			img_count = 0
			href_count = 0
			inp_count = 0
			sel_count = 0
			colspan_count = 0
			colon_count = 0
			len_row = 0
			rows = table["rows"]
			table_data = ""
			outfile.write('<table>\n')
			#outfile.write('<tr><td> No. of rows: ' + str(len(rows)) + "</td></tr>")
			for row in rows:
				soup = BeautifulSoup(row, 'html.parser')
				row_data = ""
				for string in soup.stripped_strings:
					row_data += string
				if row_data is not '':
					#row_tdcount = row.count("<td") + row.count("<th")
					row_tdcount = len(soup.findAll('td')) + len(soup.findAll('th'))
					if(row_tdcount > max_tdcount):
						max_tdcount = row_tdcount
					tdcount += row_tdcount
					#img_count += row.count("<img")
					img_count += len(soup.findAll('img'))
					#href_count += row.count("href")
					href_count += len(soup.findAll('a'))
					#inp_count += row.count("<input")
					inp_count += len(soup.findAll('input'))
					#sel_count += row.count("<select")
					sel_count += len(soup.findAll('select'))
					colspan_count += row_data.count("colspan")
					colon_count += row_data.count(":")
					len_row += 1
					table_data += row
					outfile.write(row)
					outfile.write("\n")
			if len_row == 0:
				empty_tab_count += 1
				tdcount = 1
			if(img_count*1.0/tdcount >= 1.0):
				img_tab_count += 1
			if(href_count*1.0/tdcount >= 1.0):
				href_tab_count += 1
			if(inp_count*1.0/tdcount > 0.0):
				input_tab_count += 1
			if(sel_count*1.0/tdcount > 0.0):
				select_tab_count += 1
			if(colon_count*1.0/tdcount >= 0.3):
				colon_tab_count += 1
			if(colspan_count*1.0/tdcount > 0.0):
				colspan_tab_count += 1
			outfile.write('No. of rows: {0}'.format(len_row) + '<br>')
			outfile.write('No. of cells: {0}'.format(tdcount) + '<br>')
			outfile.write('Avg cols: {0:.2f}'.format(tdcount/(len(rows)*1.0)) + '<br>')
			outfile.write('Max cols in a row: {0}'.format(max_tdcount) + '<br>')
			outfile.write('Ratio of img tags to cells: {0:.2f}'.format(img_count*1.0/tdcount) + '<br>')
			outfile.write('Ratio of href tags to cells: {0:.2f}'.format(href_count*1.0/tdcount) + '<br>')
			outfile.write('Ratio of input tags to cells: {0:.2f}'.format(inp_count*1.0/tdcount) + '<br>')
			outfile.write('Ratio of select tags to cells: {0:.2f}'.format(sel_count*1.0/tdcount) + '<br>')
			outfile.write('Ratio of colspan tags to cells: {0:.2f}'.format(colspan_count*1.0/tdcount) + '<br>')
			outfile.write('Ratio of colons to cells: {0:.2f}'.format(colon_count*1.0/tdcount) + '<br>')
			# Column features 
			if(colspan_count == 0.0 and len_row != 0 and (tdcount/(len_row * 1.0)) == max_tdcount):
				col_data = {}
				for i in range(max_tdcount):
					col_data['c_{0}'.format(i)] = []
				soup = BeautifulSoup(table_data, 'html.parser')
				for row in soup.findAll('tr'):
					h_index = 0
					h_bool = True
					for col in row.findAll('th'):
						col_content = col.string
						h_bool = False
						if col_content is None:
							continue
						else:
							col_data['c_{0}'.format(h_index)].append(col_content)
						h_index += 1
					d_index = 0
					if(h_index == 0 and h_bool == False):
						d_index = 1
					for col in row.findAll('td'):
						col_content = col.string
						if col_content is None:
							continue
						else:
							col_data['c_{0}'.format(d_index)].append(col_content)
						d_index += 1

				for key, value in col_data.iteritems():
					outfile.write("Column " + str(key) + " average len: {0:.2f}".format(mean([len(x) for x in value])) + '<br>')
					outfile.write("Column " + str(key) + " contains num: {0}".format(contains_digits(''.join(value))) + '<br>')

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