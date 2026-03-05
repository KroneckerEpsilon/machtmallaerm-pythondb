import re
from collections import defaultdict

def parse_sql_dump(dump: str):
    tables = {}
    current_table = None
    inside_insert = False
    insert_buffer = ''

    lines = dump.splitlines()

    for line in lines:
        line = line.strip()

        # Neue Tabelle beginnt
        if line.startswith('CREATE TABLE'):
            current_table = re.findall(r'`(\w+)`', line)[0]
            tables[current_table] = {'columns': [], 'rows': []}

        # Spalten definieren
        elif current_table and line.startswith('`'):
            column_name = re.findall(r'`(\w+)`', line)[0]
            tables[current_table]['columns'].append(column_name)

        # INSERT block beginnt
        elif line.startswith('INSERT INTO'):
            inside_insert = True
            insert_buffer = line
            if line.endswith(';'):
                inside_insert = False
                rows = extract_rows_from_insert(insert_buffer)
                tables[current_table]['rows'].extend(rows)
        
        elif inside_insert:
            insert_buffer += ' ' + line
            if line.endswith(';'):
                inside_insert = False
                rows = extract_rows_from_insert(insert_buffer)
                tables[current_table]['rows'].extend(rows)

    # Konvertiere rows zu dicts
    for table in tables:
        columns = tables[table]['columns']
        rowdicts = [dict(zip(columns, row)) for row in tables[table]['rows']]
        tables[table] = rowdicts

    return tables

def extract_rows_from_insert(insert_line):
    """
    Extract tuples of values from an INSERT INTO ... VALUES (...) SQL statement.
    Assumes values are simple and comma-separated, possibly with NULLs and strings in single quotes.
    """
    match = re.search(r'VALUES\s*(.*);', insert_line, re.IGNORECASE | re.DOTALL)
    if not match:
        return []

    values_str = match.group(1).strip()

    # Split by '),(' while preserving contents
    raw_rows = re.findall(r'\((.*?)\)', values_str, re.DOTALL)

    parsed_rows = []
    for row in raw_rows:
        values = parse_sql_values(row)
        parsed_rows.append(values)
    return parsed_rows

def parse_sql_values(row_str):
    """
    Parses a single row string like:  'abc', NULL, 3, 'text with ''quotes'''
    into: ['abc', None, 3, "text with 'quotes'"]
    """
    values = []
    token = ''
    in_string = False
    escape = False
    i = 0

    while i < len(row_str):
        char = row_str[i]

        if in_string:
            if escape:
                # Accept escaped character
                if char == "'":
                    token += "'"
                elif char == "\\":
                    token += "\\"
                else:
                    token += '\\' + char
                escape = False
            elif char == "\\":
                escape = True
            elif char == "'":
                in_string = False
                values.append(token)
                token = ''
            else:
                token += char
        else:
            if char == "'":
                in_string = True
                token = ''
                #print("char '")
            elif char == ',':
                #print("char ,")
                if token.strip().upper() == 'NULL':
                    #print(f"in_string=False: Appending value None")
                    values.append(None)
                elif token.strip() == '':
                    pass
                    #print(f"omitting ")
                    #values.append(None)
                    #continue
                else:
                    #print(f"in_string=False: Appending value {token}")
                    try:
                        values.append(int(token))
                    except ValueError:
                        try:
                            values.append(float(token))
                        except ValueError:
                            values.append(token.strip())
                token = ''
            else:
                token += char
        i += 1

    # letzte Spalte verarbeiten
    if token:
        if token.strip().upper() == 'NULL':
            values.append(None)
        else:
            try:
                values.append(int(token))
            except ValueError:
                try:
                    values.append(float(token))
                except ValueError:
                    values.append(token.strip())

    return values