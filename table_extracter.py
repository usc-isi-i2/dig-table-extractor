from bs4 import BeautifulSoup
import ast
import json

path = './'
#groundtruth = path + 'sample_nyu_10.jl'
#groundtruth = path + 'nyu-ddindex-fall2016qpr-cdr-deduped.jl'
groundtruth = path + 'pedro/gt_ads_nov_aa.jl'

f = open(groundtruth, 'r')

def is_data_cell(cell):
	if(cell.table):
		return False
	return True

def is_data_row(row):
	if(row.table):
		return False
	cell = row.findAll('td', recursive=False)
	if cell is None:
		cell = row.findAll('th', recursive=False)
	for td in cell:
		if(is_data_cell(td) == False):
			return False
	return True

def get_data_rows(table):
	data_rows = []
	rows = table.findAll('tr', recursive=False)
	for tr in rows:
		if(is_data_row(tr)):
			data_rows.append(str(tr))
	return data_rows

def is_data_table(table, k):
	rows = get_data_rows(table)
	if(len(rows) > k):
		return rows
	else:
		return False

def table_extract(html_doc):
	soup = BeautifulSoup(html_doc, 'html.parser')
	
	if(soup.table == None):
		return None
	else:
		dict = {}
		dict["tables"] = []
		tables = soup.findAll('table')
		for table in tables:
			data_table = {}
			rows = is_data_table(table, 2)
			if(rows != False):
				data_table["rows"] = rows
				dict["tables"].append(data_table)
		return dict


def table_decompose(html_doc):
	soup = BeautifulSoup(html_doc, 'html.parser')
	tables = soup.findAll('table')
	for table in tables:
		rows = is_data_table(table, 2)
		if(rows != False):
			table.decompose()
	
	return soup


# Output json
# outfile = open('tables_sample3.txt', 'wb')

# for index, line in enumerate(f):
# 	print index
# 	line = ast.literal_eval(line)
# 	html_doc = line['raw_content']
# 	table = table_extract(html_doc)
# 	outfile.write(json.dumps(table))
# 	outfile.write("\n")

# outfile.close()

#Output tables
#outfile = open('tables_sample3.html', 'wb')
outfile = open('table_extractions_gt_aa.html', 'wb')

words = ['name', 'phone', 'email', 'age']

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


for index, line in enumerate(f):
	print index
	try:
		line = ast.literal_eval(line)
		html_doc = line['raw_content']
		doc = table_extract(html_doc)
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
		outfile.write("</table>")
		outfile.write("<hr><hr>")

outfile.write("No.of tables: {0}".format(count) + '<br>')
outfile.write("No.of tables with empty rows: {0}".format(empty_tab_count) + '<br>')
outfile.write("No.of tables with img >= 1.0: {0}".format(img_tab_count) + '<br>')
outfile.write("No.of tables with href >= 1.0: {0}".format(href_tab_count) + '<br>')
outfile.write("No.of tables with input > 0.0: {0}".format(input_tab_count) + '<br>')
outfile.write("No.of tables with select > 0.0: {0}".format(select_tab_count) + '<br>')
outfile.write("No.of tables with colons >= 0.3: {0}".format(colon_tab_count) + '<br>')
outfile.close()

#Output complement html
# outfile = open('sample_output.txt', 'wb')

# for index, line in enumerate(f):
# 	print index
# 	line = ast.literal_eval(line)
# 	html_doc = line['raw_content']
# 	html = table_decompose(html_doc)
# 	line["raw_without_data_table"] = str(html)
# 	outfile.write(json.dumps(line))
# 	outfile.write("\n")

# outfile.close()
