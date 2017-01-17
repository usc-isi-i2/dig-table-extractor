from bs4 import BeautifulSoup

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