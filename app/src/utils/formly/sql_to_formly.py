#!/usr/bin/env python3
"""
SQL to Formly Field Config Converter
Converts SQL CREATE TABLE statements to Angular Formly field configurations
"""

import re
import json
import argparse
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict


@dataclass
class ColumnDefinition:
    """Represents a SQL column definition"""
    name: str
    type: str
    length: Optional[int] = None
    precision: Optional[int] = None
    scale: Optional[int] = None
    nullable: bool = True
    default_value: Optional[str] = None
    is_primary_key: bool = False
    is_auto_increment: bool = False


class SqlToFormlyConverter:
    """Converts SQL CREATE TABLE statements to Formly field configurations"""
    
    def __init__(self):
        self.text_types = ['VARCHAR', 'CHAR', 'TEXT', 'NVARCHAR', 'NCHAR', 'CLOB']
        self.integer_types = ['INT', 'INTEGER', 'BIGINT', 'SMALLINT', 'TINYINT']
        self.decimal_types = ['DECIMAL', 'NUMERIC', 'FLOAT', 'DOUBLE', 'REAL']
        self.boolean_types = ['BOOLEAN', 'BOOL', 'BIT']
        self.date_types = ['DATE', 'DATETIME', 'TIMESTAMP', 'TIME']
    
    def parse_create_table(self, sql: str) -> List[ColumnDefinition]:
        """Parse a SQL CREATE TABLE statement and extract column definitions"""
        columns = []
        
        # Remove comments
        sql = re.sub(r'--.*$', '', sql, flags=re.MULTILINE)
        sql = re.sub(r'/\*[\s\S]*?\*/', '', sql)
        
        # Extract the columns section
        match = re.search(r'CREATE\s+TABLE\s+\w+\s*\(([\s\S]+)\)', sql, re.IGNORECASE)
        if not match:
            raise ValueError('Invalid CREATE TABLE statement')
        
        columns_section = match.group(1)
        
        # Split by commas, but be careful with commas inside parentheses
        lines = self._split_column_definitions(columns_section)
        
        for line in lines:
            line = line.strip()
            # Skip constraint definitions
            if re.match(r'^(PRIMARY KEY|FOREIGN KEY|UNIQUE|CHECK|CONSTRAINT)', line, re.IGNORECASE):
                continue
            
            column = self._parse_column_definition(line)
            if column:
                columns.append(column)
        
        return columns
    
    def _split_column_definitions(self, columns_section: str) -> List[str]:
        """Split column definitions by comma, respecting parentheses"""
        lines = []
        current = []
        depth = 0
        
        for char in columns_section:
            if char == '(':
                depth += 1
            elif char == ')':
                depth -= 1
            elif char == ',' and depth == 0:
                lines.append(''.join(current))
                current = []
                continue
            current.append(char)
        
        if current:
            lines.append(''.join(current))
        
        return lines
    
    def _parse_column_definition(self, column_def: str) -> Optional[ColumnDefinition]:
        """Parse a single column definition"""
        parts = column_def.strip().split()
        if len(parts) < 2:
            return None
        
        # Extract column name (remove quotes/backticks)
        name = re.sub(r'[`"\[\]]', '', parts[0])
        
        # Extract type with optional length/precision
        type_match = re.match(r'^(\w+)(?:\((\d+)(?:,(\d+))?\))?', parts[1], re.IGNORECASE)
        if not type_match:
            return None
        
        col_type = type_match.group(1).upper()
        length = int(type_match.group(2)) if type_match.group(2) else None
        scale = int(type_match.group(3)) if type_match.group(3) else None
        
        # Check for constraints
        def_upper = column_def.upper()
        nullable = 'NOT NULL' not in def_upper
        is_primary_key = 'PRIMARY KEY' in def_upper
        is_auto_increment = any(keyword in def_upper for keyword in 
                               ['AUTO_INCREMENT', 'AUTOINCREMENT', 'IDENTITY'])
        
        # Extract default value
        default_value = self._extract_default(column_def)
        
        return ColumnDefinition(
            name=name,
            type=col_type,
            length=length,
            precision=length,
            scale=scale,
            nullable=nullable,
            default_value=default_value,
            is_primary_key=is_primary_key,
            is_auto_increment=is_auto_increment
        )
    
    def _extract_default(self, column_def: str) -> Optional[str]:
        """Extract default value from column definition"""
        match = re.search(r"DEFAULT\s+('([^']*)'|\"([^\"]*)\"|(\S+))", column_def, re.IGNORECASE)
        if match:
            return match.group(2) or match.group(3) or match.group(4)
        return None
    
    def _map_sql_type_to_formly_type(self, column: ColumnDefinition) -> str:
        """Map SQL type to Formly field type"""
        col_type = column.type
        
        # Skip auto-increment fields
        if column.is_auto_increment or column.is_primary_key:
            return 'input'
        
        # Text types
        if col_type in self.text_types:
            if column.length and column.length > 255:
                return 'textarea'
            return 'input'
        
        # Numeric types
        if col_type in self.integer_types or col_type in self.decimal_types:
            return 'input'
        
        # Boolean
        if col_type in self.boolean_types:
            return 'checkbox'
        
        # Date/Time
        if col_type in self.date_types:
            return 'input'
        
        return 'input'
    
    def _create_template_options(self, column: ColumnDefinition) -> Dict[str, Any]:
        """Create template options for a column"""
        opts = {
            'label': self._format_label(column.name),
            'required': not column.nullable
        }
        
        col_type = column.type
        
        # Text inputs
        if col_type in self.text_types:
            opts['type'] = 'text'
            if column.length:
                opts['maxLength'] = column.length
        
        # Integer inputs
        if col_type in self.integer_types:
            opts['type'] = 'number'
            opts['pattern'] = r'^-?\d+$'
        
        # Decimal inputs
        if col_type in self.decimal_types:
            opts['type'] = 'number'
            opts['step'] = 10 ** -column.scale if column.scale else 0.01
        
        # Date inputs
        if col_type == 'DATE':
            opts['type'] = 'date'
        elif col_type in ['DATETIME', 'TIMESTAMP']:
            opts['type'] = 'datetime-local'
        elif col_type == 'TIME':
            opts['type'] = 'time'
        
        # Email pattern for common email columns
        if 'email' in column.name.lower():
            opts['type'] = 'email'
            opts['pattern'] = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        # Default value
        if column.default_value:
            opts['defaultValue'] = column.default_value
        
        return opts
    
    def _format_label(self, column_name: str) -> str:
        """Format column name to human-readable label"""
        # Replace underscores with spaces
        label = column_name.replace('_', ' ')
        # Add space before capital letters
        label = re.sub(r'([A-Z])', r' \1', label)
        # Title case each word
        label = ' '.join(word.capitalize() for word in label.split())
        return label.strip()
    
    def convert(self, sql: str, 
                exclude_auto_increment: bool = True,
                exclude_primary_key: bool = False,
                readonly: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Convert a SQL CREATE TABLE statement to FormlyFieldConfig array
        
        Args:
            sql: SQL CREATE TABLE statement
            exclude_auto_increment: Skip auto-increment fields
            exclude_primary_key: Skip primary key fields
            readonly: List of field names to mark as readonly
        
        Returns:
            List of Formly field configuration dictionaries
        """
        columns = self.parse_create_table(sql)
        fields = []
        readonly = readonly or []
        
        for column in columns:
            # Skip auto-increment if requested
            if exclude_auto_increment and column.is_auto_increment:
                continue
            
            # Skip primary key if requested
            if exclude_primary_key and column.is_primary_key:
                continue
            
            field = {
                'key': column.name,
                'type': self._map_sql_type_to_formly_type(column),
                'templateOptions': self._create_template_options(column)
            }
            
            # Mark as readonly if specified
            if column.name in readonly:
                field['templateOptions']['readonly'] = True
            
            fields.append(field)
        
        return fields
    
    def convert_to_json(self, sql: str, **kwargs) -> str:
        """Convert and return as JSON string"""
        fields = self.convert(sql, **kwargs)
        return json.dumps(fields, indent=2)


def main():
    """Command-line interface"""
    parser = argparse.ArgumentParser(
        description='Convert SQL CREATE TABLE statements to Formly field configurations'
    )
    parser.add_argument(
        'input',
        nargs='?',
        help='SQL file or SQL string (if not provided, reads from stdin)'
    )
    parser.add_argument(
        '-o', '--output',
        help='Output file (if not provided, writes to stdout)'
    )
    parser.add_argument(
        '--include-auto-increment',
        action='store_true',
        help='Include auto-increment fields in output'
    )
    parser.add_argument(
        '--exclude-primary-key',
        action='store_true',
        help='Exclude primary key fields from output'
    )
    parser.add_argument(
        '--readonly',
        nargs='+',
        help='Fields to mark as readonly'
    )
    
    args = parser.parse_args()
    
    # Read input
    if args.input:
        try:
            with open(args.input, 'r') as f:
                sql = f.read()
        except FileNotFoundError:
            # Treat as SQL string if file doesn't exist
            sql = args.input
    else:
        import sys
        sql = sys.stdin.read()
    
    # Convert
    converter = SqlToFormlyConverter()
    try:
        result = converter.convert_to_json(
            sql,
            exclude_auto_increment=not args.include_auto_increment,
            exclude_primary_key=args.exclude_primary_key,
            readonly=args.readonly
        )
        
        # Write output
        if args.output:
            with open(args.output, 'w') as f:
                f.write(result)
            print(f"Output written to {args.output}")
        else:
            print(result)
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    
    return 0


if __name__ == '__main__':
    # Example usage when run directly
    # example_sql = """
    # CREATE TABLE users (
    #   id INT PRIMARY KEY AUTO_INCREMENT,
    #   username VARCHAR(50) NOT NULL,
    #   email VARCHAR(100) NOT NULL,
    #   age INT,
    #   bio TEXT,
    #   is_active BOOLEAN DEFAULT TRUE,
    #   created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    # )
    # """
    
    # print("Example SQL Table:")
    # print(example_sql)
    # print("\nFormly Field Config:")
    
    # converter = SqlToFormlyConverter()
    # print(converter.convert_to_json(example_sql))
    
    # print("\n" + "="*50)
    # print("Run with --help for command-line usage")
    # print("="*50)
    
    main()