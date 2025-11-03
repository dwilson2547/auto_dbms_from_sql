#!/usr/bin/env python3
"""
SQL Linter and Formatter
Validates and formats SQL statements using sqlparse and sqlvalidator.

Installation:
    pip install sqlparse sqlvalidator

Usage:
    python sql_linter.py input.sql
    python sql_linter.py input.sql -o output.sql
    python sql_linter.py input.sql --validate-only
    cat input.sql | python sql_linter.py
"""

import sys
import argparse
from pathlib import Path
from typing import Dict, List, Tuple
import sqlparse
from sqlparse import format as sql_format


class SQLLinter:
    """SQL Linter and Formatter with validation."""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
    
    def format_sql(self, sql: str, 
                   reindent: bool = True,
                   keyword_case: str = 'upper',
                   comma_first: bool = False) -> str:
        """
        Format SQL statement.
        
        Args:
            sql: SQL statement to format
            reindent: Whether to reindent the SQL
            keyword_case: 'upper', 'lower', or 'capitalize'
            indent_width: Number of spaces for indentation
            wrap_after: Column width to wrap at
            comma_first: Put commas at the beginning of lines
            
        Returns:
            Formatted SQL string
        """
        formatted = sql_format(
            sql,
            reindent=reindent,
            keyword_case=keyword_case,
            indent_width=1,
            indent_tabs=True,
            comma_first=comma_first,
            strip_comments=False
        )
        return formatted.strip()
    
    def validate_sql(self, sql: str) -> Tuple[bool, List[str]]:
        """
        Validate SQL syntax.
        
        Args:
            sql: SQL statement to validate
            
        Returns:
            Tuple of (is_valid, list of error messages)
        """
        errors = []
        
        try:
            # Parse the SQL
            parsed = sqlparse.parse(sql)
            
            if not parsed:
                errors.append("Empty or invalid SQL statement")
                return False, errors
            
            # Check for common issues
            for statement in parsed:
                # Check if statement is empty
                if not statement.tokens:
                    errors.append("Empty statement found")
                    continue
                
                # Get statement type
                stmt_type = statement.get_type()
                
                # Basic validation checks
                sql_upper = str(statement).upper()
                
                # Check for unterminated strings
                if sql_upper.count("'") % 2 != 0:
                    errors.append("Unterminated string literal detected")
                
                # Check for mismatched parentheses
                open_parens = str(statement).count('(')
                close_parens = str(statement).count(')')
                if open_parens != close_parens:
                    errors.append(f"Mismatched parentheses: {open_parens} open, {close_parens} close")
                
                # Check for SQL injection patterns (basic check)
                dangerous_patterns = ['--', '/*', '*/', 'UNION SELECT', 'DROP TABLE', 'DELETE FROM']
                for pattern in dangerous_patterns:
                    if pattern in sql_upper and pattern not in ['--', '/*', '*/']:
                        self.warnings.append(f"Potentially dangerous pattern found: {pattern}")
            
            return len(errors) == 0, errors
            
        except Exception as e:
            errors.append(f"Parse error: {str(e)}")
            return False, errors
    
    def analyze_sql(self, sql: str) -> Dict:
        """
        Analyze SQL statement and return detailed information.
        
        Args:
            sql: SQL statement to analyze
            
        Returns:
            Dictionary with analysis results
        """
        analysis = {
            'statement_count': 0,
            'statement_types': [],
            'table_names': [],
            'keywords': [],
            'has_subqueries': False,
            'complexity': 'simple'
        }
        
        try:
            parsed = sqlparse.parse(sql)
            analysis['statement_count'] = len(parsed)
            
            for statement in parsed:
                stmt_type = statement.get_type()
                if stmt_type:
                    analysis['statement_types'].append(stmt_type)
                
                # Extract table names
                for token in statement.tokens:
                    if isinstance(token, sqlparse.sql.Identifier):
                        analysis['table_names'].append(str(token))
                    elif token.ttype is sqlparse.tokens.Keyword:
                        analysis['keywords'].append(str(token).upper())
                
                # Check for subqueries
                if 'SELECT' in str(statement).upper().split('SELECT')[1:]:
                    analysis['has_subqueries'] = True
                
                # Assess complexity
                keyword_count = len(analysis['keywords'])
                if keyword_count > 15 or analysis['has_subqueries']:
                    analysis['complexity'] = 'complex'
                elif keyword_count > 8:
                    analysis['complexity'] = 'moderate'
        
        except Exception:
            pass
        
        return analysis
    
    def lint_file(self, input_path: str, output_path: str = None, 
                  validate_only: bool = False, **format_options) -> bool:
        """
        Lint and format SQL file.
        
        Args:
            input_path: Path to input SQL file
            output_path: Optional path to save formatted SQL
            validate_only: Only validate, don't format
            **format_options: Options to pass to format_sql()
            
        Returns:
            True if validation passed, False otherwise
        """
        # Read input file
        try:
            with open(input_path, 'r') as f:
                sql_content = f.read()
        except FileNotFoundError:
            print(f"Error: File '{input_path}' not found", file=sys.stderr)
            return False
        
        # Validate
        is_valid, errors = self.validate_sql(sql_content)
        
        # Print validation results
        print(f"Validating: {input_path}")
        print("=" * 60)
        
        if is_valid:
            print("✓ SQL is valid")
        else:
            print("✗ SQL validation failed:")
            for error in errors:
                print(f"  - {error}")
        
        if self.warnings:
            print("\nWarnings:")
            for warning in self.warnings:
                print(f"  - {warning}")
        
        # Analyze
        analysis = self.analyze_sql(sql_content)
        print(f"\nAnalysis:")
        print(f"  Statements: {analysis['statement_count']}")
        print(f"  Types: {', '.join(set(analysis['statement_types']))}")
        print(f"  Complexity: {analysis['complexity']}")
        
        if validate_only:
            return is_valid
        
        # Format
        if is_valid or not errors:  # Format even if minor issues
            formatted_sql = self.format_sql(sql_content, **format_options)
            
            if output_path:
                with open(output_path, 'w') as f:
                    f.write(formatted_sql)
                print(f"\n✓ Formatted SQL written to: {output_path}")
            else:
                print("\n" + "=" * 60)
                print("Formatted SQL:")
                print("=" * 60)
                print(formatted_sql)
        
        return is_valid


def main():
    parser = argparse.ArgumentParser(
        description='Lint and format SQL statements with validation'
    )
    parser.add_argument('input', nargs='?', help='Input SQL file (or read from stdin)')
    parser.add_argument('-o', '--output', help='Output file for formatted SQL')
    parser.add_argument('--validate-only', action='store_true',
                       help='Only validate, do not format')
    parser.add_argument('--keyword-case', choices=['upper', 'lower', 'capitalize'],
                       default='upper', help='Keyword case style (default: upper)')
    parser.add_argument('--indent-width', type=int, default=4,
                       help='Indentation width (default: 4)')
    parser.add_argument('--no-reindent', action='store_true',
                       help='Do not reindent the SQL')
    parser.add_argument('--comma-first', action='store_true',
                       help='Place commas at the beginning of lines')
    parser.add_argument('--wrap-after', type=int, default=80,
                       help='Column width to wrap at (default: 80)')
    
    args = parser.parse_args()
    
    linter = SQLLinter()
    
    # Handle stdin or file input
    if args.input:
        format_options = {
            'keyword_case': args.keyword_case,
            'indent_width': args.indent_width,
            'reindent': not args.no_reindent,
            'comma_first': args.comma_first,
            'wrap_after': args.wrap_after
        }
        
        is_valid = linter.lint_file(
            args.input,
            args.output,
            args.validate_only,
            **format_options
        )
        
        sys.exit(0 if is_valid else 1)
    else:
        # Read from stdin
        sql_content = sys.stdin.read()
        
        is_valid, errors = linter.validate_sql(sql_content)
        
        if is_valid:
            print("✓ SQL is valid", file=sys.stderr)
            if not args.validate_only:
                formatted = linter.format_sql(
                    sql_content,
                    keyword_case=args.keyword_case,
                    indent_width=args.indent_width,
                    reindent=not args.no_reindent,
                    comma_first=args.comma_first,
                    wrap_after=args.wrap_after
                )
                print(formatted)
        else:
            print("✗ SQL validation failed:", file=sys.stderr)
            for error in errors:
                print(f"  - {error}", file=sys.stderr)
            sys.exit(1)


if __name__ == '__main__':
    main()