#!/usr/bin/env python3
"""
SQL CREATE TABLE Statement Splitter
Splits a SQL string into individual CREATE TABLE statements.

Usage:
    python split_sql_tables.py input.sql
    python split_sql_tables.py input.sql --output-dir tables/
    cat input.sql | python split_sql_tables.py
"""

import re
import sys
import argparse
from pathlib import Path
from typing import List


def split_create_table_statements(sql_text: str) -> List[str]:
    """
    Split SQL text into individual CREATE TABLE statements.
    
    Args:
        sql_text: SQL string containing one or more CREATE TABLE statements
        
    Returns:
        List of strings, each containing one CREATE TABLE statement
    """
    # Pattern to match CREATE TABLE statements
    # Handles: CREATE TABLE, CREATE TABLE IF NOT EXISTS
    # Captures everything until the closing semicolon
    pattern = r'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?[^\s;]+\s*\([^)]*(?:\([^)]*\)[^)]*)*\)\s*[^;]*;'
    
    matches = re.findall(pattern, sql_text, re.IGNORECASE | re.DOTALL)
    
    # Clean up whitespace while preserving structure
    cleaned_statements = []
    for match in matches:
        # Remove leading/trailing whitespace but keep internal formatting
        cleaned = match.strip()
        cleaned_statements.append(cleaned)
    
    return cleaned_statements


def extract_table_name(create_statement: str) -> str:
    """Extract table name from CREATE TABLE statement."""
    pattern = r'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?`?(\w+)`?'
    match = re.search(pattern, create_statement, re.IGNORECASE)
    return match.group(1) if match else "unknown_table"


def split_sql_file(input_file: str, output_dir: str = None) -> List[str]:
    """
    Split SQL file into individual CREATE TABLE statements.
    
    Args:
        input_file: Path to input SQL file
        output_dir: Optional directory to save individual table files
        
    Returns:
        List of CREATE TABLE statements
    """
    with open(input_file, 'r') as f:
        sql_text = f.read()
    
    statements = split_create_table_statements(sql_text)
    
    if output_dir:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        for statement in statements:
            table_name = extract_table_name(statement)
            output_file = output_path / f"{table_name}.sql"
            with open(output_file, 'w') as f:
                f.write(statement)
            print(f"Wrote {output_file}")
    
    return statements


def main():
    parser = argparse.ArgumentParser(
        description='Split SQL CREATE TABLE statements into individual strings/files'
    )
    parser.add_argument('input', nargs='?', help='Input SQL file (or read from stdin)')
    parser.add_argument('-o', '--output-dir', help='Output directory for individual table files')
    parser.add_argument('-c', '--count', action='store_true', 
                       help='Only print count of CREATE TABLE statements')
    parser.add_argument('-l', '--list', action='store_true',
                       help='List table names only')
    parser.add_argument('-n', '--numbered', action='store_true',
                       help='Print statements with numbers')
    
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
    
    # Split statements
    statements = split_create_table_statements(sql_text)
    
    if not statements:
        print("No CREATE TABLE statements found", file=sys.stderr)
        sys.exit(1)
    
    # Handle output options
    if args.count:
        print(f"Found {len(statements)} CREATE TABLE statement(s)")
    elif args.list:
        for statement in statements:
            table_name = extract_table_name(statement)
            print(table_name)
    elif args.output_dir:
        output_path = Path(args.output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        for statement in statements:
            table_name = extract_table_name(statement)
            output_file = output_path / f"{table_name}.sql"
            with open(output_file, 'w') as f:
                f.write(statement)
            print(f"Wrote {output_file}")
    else:
        # Print all statements
        if args.numbered:
            for i, statement in enumerate(statements, 1):
                table_name = extract_table_name(statement)
                print(f"\n{'='*60}")
                print(f"Table {i}: {table_name}")
                print('='*60)
                print(statement)
        else:
            for statement in statements:
                print(statement)
                print()  # Empty line between statements


# Example usage as a module
def example_usage():
    """Example of using the function programmatically."""
    sql_string = """
    CREATE TABLE users (
        id INT PRIMARY KEY AUTO_INCREMENT,
        username VARCHAR(50) NOT NULL,
        email VARCHAR(100)
    );
    
    CREATE TABLE IF NOT EXISTS posts (
        id INT PRIMARY KEY,
        user_id INT NOT NULL,
        title VARCHAR(200),
        content TEXT,
        created_at DATETIME
    );
    
    CREATE TABLE comments (
        id INT PRIMARY KEY,
        post_id INT,
        text TEXT
    );
    """
    
    # Split into individual statements
    statements = split_create_table_statements(sql_string)
    
    print(f"Found {len(statements)} CREATE TABLE statements:\n")
    
    for i, stmt in enumerate(statements, 1):
        table_name = extract_table_name(stmt)
        print(f"{i}. Table: {table_name}")
        print(f"   Length: {len(stmt)} characters")
        print(f"   Preview: {stmt[:50]}...")
        print()


if __name__ == '__main__':
    # Uncomment to see example usage:
    # example_usage()
    
    main()