#!/usr/bin/env python3
"""
SQL Schema Parser - Python Version
Extracts tables and their primary keys from SQL DDL statements
Supports inline and constraint-based primary key declarations (Oracle, MySQL, PostgreSQL)
"""

import re
import json
from typing import List, Dict, Any


def remove_comments(sql: str) -> str:
    """Remove SQL comments from the schema"""
    # Remove single line comments
    sql = re.sub(r'--.*$', '', sql, flags=re.MULTILINE)
    # Remove multi-line comments
    sql = re.sub(r'/\*[\s\S]*?\*/', '', sql)
    return sql


def extract_primary_keys(table_body: str) -> List[str]:
    """Extract primary key columns from table body"""
    primary_keys = []
    
    # Method 1: Inline PRIMARY KEY in column definition
    # e.g., id INT PRIMARY KEY
    inline_pattern = r'([`"]?\w+[`"]?)\s+\w+(?:\([^)]*\))?\s+(?:[^,]*?\s+)?PRIMARY\s+KEY'
    for match in re.finditer(inline_pattern, table_body, re.IGNORECASE):
        column_name = match.group(1).strip('`"')
        if column_name not in primary_keys:
            primary_keys.append(column_name)
    
    # Method 2: CONSTRAINT with PRIMARY KEY
    # e.g., CONSTRAINT pk_users PRIMARY KEY (id, tenant_id)
    constraint_pattern = r'CONSTRAINT\s+\w+\s+PRIMARY\s+KEY\s*\(([^)]+)\)'
    for match in re.finditer(constraint_pattern, table_body, re.IGNORECASE):
        columns = [col.strip().strip('`"') for col in match.group(1).split(',')]
        for col in columns:
            if col not in primary_keys:
                primary_keys.append(col)
    
    # Method 3: PRIMARY KEY without CONSTRAINT keyword
    # e.g., PRIMARY KEY (id, user_id)
    pk_pattern = r'(?:^|,)\s*PRIMARY\s+KEY\s*\(([^)]+)\)'
    for match in re.finditer(pk_pattern, table_body, re.IGNORECASE):
        columns = [col.strip().strip('`"') for col in match.group(1).split(',')]
        for col in columns:
            if col not in primary_keys:
                primary_keys.append(col)
    
    return primary_keys


def parse_sql_schema(sql_schema: str) -> List[Dict[str, Any]]:
    """Parse SQL schema and extract tables with their primary keys"""
    tables = []
    
    # Remove comments
    cleaned_sql = remove_comments(sql_schema)
    
    # Find all CREATE TABLE statements
    table_pattern = r'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?([`"]?\w+[`"]?)\s*\(([\s\S]*?)\);'
    
    for match in re.finditer(table_pattern, cleaned_sql, re.IGNORECASE):
        table_name = match.group(1).strip('`"')
        table_body = match.group(2)
        
        primary_keys = extract_primary_keys(table_body)
        
        tables.append({
            'table_name': table_name,
            'primary_keys': primary_keys
        })
    
    return tables


def format_output(tables: List[Dict[str, Any]]) -> str:
    """Format the parsed tables as a readable string"""
    if not tables:
        return 'No tables found in the schema.'
    
    output = ['Tables and Primary Keys:', '=' * 50, '']
    
    for i, table in enumerate(tables, 1):
        output.append(f"{i}. Table: {table['table_name']}")
        
        if not table['primary_keys']:
            output.append('   Primary Keys: None')
        elif len(table['primary_keys']) == 1:
            output.append(f"   Primary Key: {table['primary_keys'][0]}")
        else:
            output.append(f"   Primary Keys (Composite): {', '.join(table['primary_keys'])}")
        
        output.append('')
    
    return '\n'.join(output)


# Example usage
def demo():
    example_schema = """
-- Oracle style schema with various PK declarations

CREATE TABLE users (
    user_id NUMBER PRIMARY KEY,
    username VARCHAR2(50) NOT NULL,
    email VARCHAR2(100),
    created_date DATE
);

CREATE TABLE orders (
    order_id NUMBER,
    customer_id NUMBER,
    order_date DATE,
    total_amount NUMBER(10,2),
    CONSTRAINT pk_orders PRIMARY KEY (order_id)
);

CREATE TABLE order_items (
    order_id NUMBER,
    item_id NUMBER,
    product_id NUMBER,
    quantity NUMBER,
    price NUMBER(10,2),
    PRIMARY KEY (order_id, item_id),
    CONSTRAINT fk_order FOREIGN KEY (order_id) REFERENCES orders(order_id)
);

CREATE TABLE products (
    product_id NUMBER,
    product_name VARCHAR2(100),
    category_id NUMBER,
    price NUMBER(10,2),
    CONSTRAINT pk_products PRIMARY KEY (product_id),
    CONSTRAINT fk_category FOREIGN KEY (category_id) REFERENCES categories(category_id)
);

CREATE TABLE categories (
    category_id NUMBER,
    category_name VARCHAR2(50),
    parent_category_id NUMBER,
    PRIMARY KEY (category_id)
);

-- Table without primary key
CREATE TABLE audit_log (
    log_id NUMBER,
    action VARCHAR2(100),
    timestamp DATE
);

-- Multi-tenant table with composite key
CREATE TABLE tenant_settings (
    tenant_id NUMBER,
    setting_key VARCHAR2(100),
    setting_value VARCHAR2(500),
    CONSTRAINT pk_tenant_settings PRIMARY KEY (tenant_id, setting_key)
);

-- PostgreSQL style with IF NOT EXISTS
CREATE TABLE IF NOT EXISTS session_data (
    session_id VARCHAR(100),
    user_id NUMBER,
    last_access TIMESTAMP,
    PRIMARY KEY (session_id)
);
"""

    print('Parsing SQL Schema...\n')
    parsed_tables = parse_sql_schema(example_schema)
    print(format_output(parsed_tables))
    
    print('\nJSON Output:')
    print(json.dumps(parsed_tables, indent=2))
    
    # Example: Reading from a file
    print('\n' + '=' * 50)
    print('Example: Reading from a file')
    print('=' * 50)
    print('''
# To read from a file:
with open('schema.sql', 'r') as f:
    sql_content = f.read()
    tables = parse_sql_schema(sql_content)
    print(format_output(tables))

# To save results to JSON:
with open('schema_analysis.json', 'w') as f:
    json.dump(tables, f, indent=2)
''')