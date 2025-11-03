#!/usr/bin/env python3
"""
SQL to SQLAlchemy Model Converter
Converts SQL CREATE TABLE statements into SQLAlchemy model classes.

Usage:
    python sql_to_sqlalchemy.py input.sql
    python sql_to_sqlalchemy.py input.sql -o output.py
    cat input.sql | python sql_to_sqlalchemy.py
"""

import re
import sys
import argparse
from typing import List, Dict, Tuple


class SQLColumn:
    def __init__(self, name: str, sql_type: str, type_args: str = "", 
                 is_primary: bool = False, is_not_null: bool = False,
                 is_unique: bool = False, is_auto_increment: bool = False,
                 has_default: bool = False):
        self.name = name
        self.sql_type = sql_type.upper()
        self.type_args = type_args
        self.is_primary = is_primary
        self.is_not_null = is_not_null
        self.is_unique = is_unique
        self.is_auto_increment = is_auto_increment
        self.has_default = has_default


class SQLTable:
    def __init__(self, name: str, columns: List[SQLColumn]):
        self.name = name
        self.columns = columns


def parse_sql_tables(sql_text: str) -> List[SQLTable]:
    """Parse SQL CREATE TABLE statements and extract table information."""
    tables = []
    
    # Match CREATE TABLE statements
    table_pattern = r'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?`?(\w+)`?\s*\(([\s\S]*?)\);'
    
    for match in re.finditer(table_pattern, sql_text, re.IGNORECASE):
        table_name = match.group(1)
        columns_text = match.group(2)
        columns = parse_columns(columns_text)
        tables.append(SQLTable(table_name, columns))
    
    return tables


def parse_columns(columns_text: str) -> List[SQLColumn]:
    """Parse column definitions from CREATE TABLE statement."""
    columns = []
    lines = [line.strip() for line in columns_text.split(',') if line.strip()]
    
    for line in lines:
        # Skip constraint definitions
        if re.match(r'^(PRIMARY KEY|FOREIGN KEY|CONSTRAINT|KEY|INDEX|UNIQUE KEY)', 
                   line, re.IGNORECASE):
            continue
        
        # Match column definition
        col_match = re.match(r'^`?(\w+)`?\s+(\w+)(\([^)]+\))?(.*)$', line, re.IGNORECASE)
        if col_match:
            name = col_match.group(1)
            sql_type = col_match.group(2)
            type_args = col_match.group(3) or ""
            constraints = col_match.group(4) or ""
            
            # Parse constraints
            is_primary = bool(re.search(r'PRIMARY\s+KEY', constraints, re.IGNORECASE))
            is_not_null = bool(re.search(r'NOT\s+NULL', constraints, re.IGNORECASE))
            is_unique = bool(re.search(r'UNIQUE', constraints, re.IGNORECASE))
            is_auto_increment = bool(re.search(r'AUTO_INCREMENT', constraints, re.IGNORECASE))
            has_default = bool(re.search(r'DEFAULT', constraints, re.IGNORECASE))
            
            columns.append(SQLColumn(
                name, sql_type, type_args, is_primary, is_not_null, 
                is_unique, is_auto_increment, has_default
            ))
    
    return columns


def sql_type_to_sqlalchemy(sql_type: str, type_args: str) -> str:
    """Convert SQL type to SQLAlchemy type."""
    type_map = {
        'INT': 'Integer',
        'INTEGER': 'Integer',
        'BIGINT': 'BigInteger',
        'SMALLINT': 'SmallInteger',
        'TINYINT': 'SmallInteger',
        'VARCHAR': f'String{type_args}',
        'CHAR': f'String{type_args}',
        'TEXT': 'Text',
        'MEDIUMTEXT': 'Text',
        'LONGTEXT': 'Text',
        'FLOAT': 'Float',
        'DOUBLE': 'Float',
        'DECIMAL': 'Numeric',
        'NUMERIC': 'Numeric',
        'DATE': 'Date',
        'DATETIME': 'DateTime',
        'TIMESTAMP': 'DateTime',
        'TIME': 'Time',
        'BOOLEAN': 'Boolean',
        'BOOL': 'Boolean',
        'BLOB': 'LargeBinary',
        'BINARY': 'LargeBinary',
        'VARBINARY': 'LargeBinary',
        'JSON': 'JSON',
    }
    
    return type_map.get(sql_type, 'String')


def to_pascal_case(snake_str: str) -> str:
    """Convert snake_case to PascalCase."""
    return ''.join(word.capitalize() for word in snake_str.split('_'))


def generate_column_definition(column: SQLColumn) -> str:
    """Generate SQLAlchemy Column definition."""
    sa_type = sql_type_to_sqlalchemy(column.sql_type, column.type_args)
    args = []
    
    if column.is_primary:
        args.append('primary_key=True')
    if column.is_auto_increment:
        args.append('autoincrement=True')
    if column.is_not_null and not column.is_primary:
        args.append('nullable=False')
    if column.is_unique and not column.is_primary:
        args.append('unique=True')
    
    args_str = ', '.join(args)
    if args_str:
        return f"Column({sa_type}, {args_str})"
    return f"Column({sa_type})"


def generate_model(table: SQLTable) -> str:
    """Generate SQLAlchemy model class from table."""
    class_name = to_pascal_case(table.name)
    lines = []
    
    lines.append(f"class {class_name}(Base):")
    lines.append(f"    __tablename__ = '{table.name}'")
    lines.append("")
    
    for column in table.columns:
        col_def = generate_column_definition(column)
        lines.append(f"    {column.name} = {col_def}")
    
    return '\n'.join(lines)


def generate_imports() -> str:
    """Generate import statements."""
    return """from sqlalchemy import Column, Integer, BigInteger, SmallInteger, String, Text
from sqlalchemy import Float, Numeric, Date, DateTime, Time, Boolean, LargeBinary, JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
"""


def convert_sql_to_sqlalchemy(sql_text: str) -> str:
    """Main conversion function."""
    tables = parse_sql_tables(sql_text)
    
    if not tables:
        raise ValueError("No valid CREATE TABLE statements found")
    
    output = [generate_imports()]
    
    for table in tables:
        output.append(generate_model(table))
        output.append("")  # Empty line between models
    
    return '\n'.join(output)


def main():
    parser = argparse.ArgumentParser(
        description='Convert SQL CREATE TABLE statements to SQLAlchemy models'
    )
    parser.add_argument('input', nargs='?', help='Input SQL file (or read from stdin)')
    parser.add_argument('-o', '--output', help='Output Python file')
    
    args = parser.parse_args()
    
    # Read input
    if args.input:
        try:
            with open(args.input, 'r') as f:
                sql_text = f.read()
        except FileNotFoundError:
            print(f"Error: File '{args.input}' not found", file=sys.stderr)
            sys.exit(1)
    else:
        # Read from stdin
        sql_text = sys.stdin.read()
    
    # Convert
    try:
        output = convert_sql_to_sqlalchemy(sql_text)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Write output
    if args.output:
        with open(args.output, 'w') as f:
            f.write(output)
        print(f"Models written to {args.output}")
    else:
        print(output)


if __name__ == '__main__':
    main()