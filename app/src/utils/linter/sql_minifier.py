#!/usr/bin/env python3
"""
SQL Minifier Utility
A practical utility for minifying SQL statements
"""

import sqlparse
import argparse
import sys
from pathlib import Path

class SQLMinifier:
    def __init__(self, 
                 strip_comments=True, 
                 strip_whitespace=True, 
                 use_space_around_operators=False,
                 keyword_case='upper'):
        self.strip_comments = strip_comments
        self.strip_whitespace = strip_whitespace
        self.use_space_around_operators = use_space_around_operators
        self.keyword_case = keyword_case
    
    def minify(self, sql_text):
        """Minify a SQL string"""
        return sqlparse.format(
            sql_text,
            strip_comments=self.strip_comments,
            strip_whitespace=self.strip_whitespace,
            use_space_around_operators=self.use_space_around_operators,
            reindent=False,
            keyword_case=self.keyword_case
        )
    
    def minify_file(self, input_file, output_file=None):
        """Minify SQL from a file"""
        with open(input_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        minified = self.minify(sql_content)
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(minified)
            return f"Minified SQL written to: {output_file}"
        else:
            return minified
    
    def get_stats(self, original, minified):
        """Get compression statistics"""
        original_size = len(original)
        minified_size = len(minified)
        reduction = (1 - minified_size / original_size) * 100
        
        return {
            'original_size': original_size,
            'minified_size': minified_size,
            'reduction_percent': reduction,
            'bytes_saved': original_size - minified_size
        }

# Interactive functions
def minify_sql_interactive():
    """Interactive SQL minification"""
    print("SQL Minifier - Enter your SQL (type 'quit' to exit, 'help' for options)")
    print("=" * 60)
    
    minifier = SQLMinifier()
    
    while True:
        try:
            print("\nEnter SQL (multi-line, press Ctrl+D when done):")
            sql_lines = []
            
            while True:
                try:
                    line = input()
                    if line.lower() == 'quit':
                        return
                    elif line.lower() == 'help':
                        print_help()
                        break
                    sql_lines.append(line)
                except EOFError:
                    break
            
            if sql_lines and sql_lines != ['help']:
                sql_text = '\n'.join(sql_lines)
                minified = minifier.minify(sql_text)
                stats = minifier.get_stats(sql_text, minified)
                
                print(f"\nOriginal ({stats['original_size']} chars):")
                print(sql_text)
                print(f"\nMinified ({stats['minified_size']} chars, {stats['reduction_percent']:.1f}% reduction):")
                print(minified)
                print("-" * 60)
        
        except KeyboardInterrupt:
            print("\nExiting...")
            break

def print_help():
    """Print help information"""
    print("""
Available options:
- Type SQL statements (multi-line supported)
- Press Ctrl+D after entering SQL to minify
- Type 'quit' to exit
- Type 'help' to see this message

Minification removes:
- Extra whitespace and line breaks
- Comments (if enabled)
- Unnecessary spaces around operators
    """)

def main():
    """Command line interface"""
    parser = argparse.ArgumentParser(description='SQL Minifier using sqlparse')
    parser.add_argument('input', nargs='?', help='Input SQL file (optional)')
    parser.add_argument('-o', '--output', help='Output file for minified SQL')
    parser.add_argument('--no-strip-comments', action='store_true', 
                       help='Keep SQL comments')
    parser.add_argument('--spaces-around-operators', action='store_true',
                       help='Keep spaces around operators')
    parser.add_argument('--lowercase-keywords', action='store_true',
                       help='Use lowercase keywords instead of uppercase')
    parser.add_argument('-i', '--interactive', action='store_true',
                       help='Run in interactive mode')
    
    args = parser.parse_args()
    
    # Configure minifier
    minifier = SQLMinifier(
        strip_comments=not args.no_strip_comments,
        use_space_around_operators=args.spaces_around_operators,
        keyword_case='lower' if args.lowercase_keywords else 'upper'
    )
    
    if args.interactive or not args.input:
        minify_sql_interactive()
    else:
        # File mode
        if not Path(args.input).exists():
            print(f"Error: File '{args.input}' not found")
            sys.exit(1)
        
        try:
            result = minifier.minify_file(args.input, args.output)
            
            if args.output:
                print(result)
                # Show stats
                with open(args.input, 'r') as f:
                    original = f.read()
                with open(args.output, 'r') as f:
                    minified = f.read()
                stats = minifier.get_stats(original, minified)
                print(f"Compression: {stats['reduction_percent']:.1f}% ({stats['bytes_saved']} bytes saved)")
            else:
                print(result)
        
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()