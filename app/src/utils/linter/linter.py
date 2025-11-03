#!/usr/bin/env python3
"""
SQLFluff Linter and Formatter Implementation
Advanced SQL linting and formatting using SQLFluff.

Installation:
    pip install sqlfluff

Usage:
    python sqlfluff_linter.py input.sql
    python sqlfluff_linter.py input.sql --dialect mysql
    python sqlfluff_linter.py input.sql --fix
    python sqlfluff_linter.py input.sql --config .sqlfluff
"""

import sys
import argparse
from pathlib import Path
from typing import List, Dict, Optional
from sqlfluff.core import Linter, FluffConfig
from sqlfluff.core.errors import SQLLintError


class SQLFluffLinter:
    """Wrapper for SQLFluff linting and formatting."""
    
    def __init__(self, dialect: str = "ansi", config_path: Optional[str] = None):
        """
        Initialize SQLFluff linter.
        
        Args:
            dialect: SQL dialect (ansi, mysql, postgres, sqlite, etc.)
            config_path: Path to .sqlfluff config file
        """
        self.dialect = dialect
        
        # Create configuration
        if config_path and Path(config_path).exists():
            self.config = FluffConfig.from_path(config_path, require_dialect=False)
        else:
            self.config = FluffConfig.from_kwargs(
                dialect=dialect,
                rules=None,  # Use all default rules
                exclude_rules=None,
                # noqa=False
            )
        
        self.linter = Linter(config=self.config)
    
    def lint_string(self, sql: str, fix: bool = False) -> Dict:
        """
        Lint SQL string.
        
        Args:
            sql: SQL string to lint
            fix: Whether to auto-fix issues
            
        Returns:
            Dictionary with linting results
        """
        if fix:
            result = self.linter.lint_string_wrapped(sql, fix=True)
            return {
                'violations': result.get_violations(),
                'num_violations': len(result.get_violations()),
                'fixed_string': result.tree.raw if result.tree else sql,
                'is_clean': len(result.get_violations()) == 0
            }
        else:
            result = self.linter.lint_string(sql)
            return {
                'violations': result.get_violations(),
                'num_violations': len(result.get_violations()),
                'fixed_string': None,
                'is_clean': len(result.get_violations()) == 0
            }
    
    def lint_file(self, file_path: str, fix: bool = False) -> Dict:
        """
        Lint SQL file.
        
        Args:
            file_path: Path to SQL file
            fix: Whether to auto-fix issues
            
        Returns:
            Dictionary with linting results
        """
        with open(file_path, 'r') as f:
            sql = f.read()
        
        return self.lint_string(sql, fix=fix)
    
    def format_violations(self, violations: List[SQLLintError]) -> str:
        """
        Format violations for display.
        
        Args:
            violations: List of SQLLintError objects
            
        Returns:
            Formatted string of violations
        """
        if not violations:
            return "✓ No violations found!"
        
        output = []
        output.append(f"Found {len(violations)} violation(s):\n")
        
        # Group violations by type
        violations_by_rule = {}
        for v in violations:
            rule_code = v.rule_code()
            if rule_code not in violations_by_rule:
                violations_by_rule[rule_code] = []
            violations_by_rule[rule_code].append(v)
        
        for rule_code, rule_violations in violations_by_rule.items():
            output.append(f"\n[{rule_code}] {rule_violations[0].description}")
            for v in rule_violations:
                output.append(f"  Line {v.line_no}, Position {v.line_pos}")
                if hasattr(v, 'source_slice'):
                    output.append(f"    {v.source_slice()}")
        
        return '\n'.join(output)
    
    def fix_file(self, input_path: str, output_path: Optional[str] = None) -> bool:
        """
        Fix SQL file and optionally save to output path.
        
        Args:
            input_path: Path to input SQL file
            output_path: Optional path to save fixed SQL
            
        Returns:
            True if successful, False otherwise
        """
        result = self.lint_file(input_path, fix=True)
        
        if result['fixed_string']:
            if output_path:
                with open(output_path, 'w') as f:
                    f.write(result['fixed_string'])
                print(f"✓ Fixed SQL written to: {output_path}")
            else:
                # Overwrite original file
                with open(input_path, 'w') as f:
                    f.write(result['fixed_string'])
                print(f"✓ Fixed SQL written to: {input_path}")
            return True
        return False


def create_example_config():
    """Create an example .sqlfluff configuration file."""
    config_content = """[sqlfluff]
# Dialect to use
dialect = mysql

# Templater to use
templater = jinja

# Exclude specific rules
exclude_rules = L003, L009

# Line length
max_line_length = 80

[sqlfluff:rules]
# Indent size
tab_space_size = 4

# Comma placement
comma_style = trailing

[sqlfluff:rules:L010]
# Keywords should be capitalized
capitalisation_policy = upper

[sqlfluff:rules:L030]
# Function names
extended_capitalisation_policy = upper
"""
    
    with open('.sqlfluff', 'w') as f:
        f.write(config_content)
    
    print("✓ Created example .sqlfluff configuration file")


def main():
    parser = argparse.ArgumentParser(
        description='Lint and fix SQL files using SQLFluff',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Lint a file
  python sqlfluff_linter.py schema.sql
  
  # Lint with specific dialect
  python sqlfluff_linter.py schema.sql --dialect postgres
  
  # Auto-fix issues
  python sqlfluff_linter.py schema.sql --fix
  
  # Fix and save to different file
  python sqlfluff_linter.py schema.sql --fix -o fixed.sql
  
  # Use custom config
  python sqlfluff_linter.py schema.sql --config .sqlfluff
  
  # Create example config file
  python sqlfluff_linter.py --create-config

Supported dialects:
  ansi, bigquery, clickhouse, databricks, db2, duckdb, exasol, 
  hive, mysql, oracle, postgres, redshift, snowflake, sparksql, 
  sqlite, teradata, tsql
        """
    )
    
    parser.add_argument('input', nargs='?', help='Input SQL file')
    parser.add_argument('-o', '--output', help='Output file for fixed SQL')
    parser.add_argument('--dialect', default='ansi',
                       help='SQL dialect (default: ansi)')
    parser.add_argument('--config', help='Path to .sqlfluff config file')
    parser.add_argument('--fix', action='store_true',
                       help='Auto-fix violations')
    parser.add_argument('--create-config', action='store_true',
                       help='Create example .sqlfluff config file')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Verbose output')
    
    args = parser.parse_args()
    
    # Create example config
    if args.create_config:
        create_example_config()
        return
    
    # Require input file
    if not args.input:
        parser.print_help()
        sys.exit(1)
    
    # Check if file exists
    if not Path(args.input).exists():
        print(f"Error: File '{args.input}' not found", file=sys.stderr)
        sys.exit(1)
    
    # Initialize linter
    print(f"Initializing SQLFluff linter (dialect: {args.dialect})...")
    linter = SQLFluffLinter(config_path=args.config, dialect=args.dialect)
    
    # Lint file
    print(f"Linting: {args.input}")
    print("=" * 60)
    
    result = linter.lint_file(args.input, fix=args.fix)
    
    # Display results
    if args.verbose:
        print(f"\nDialect: {args.dialect}")
        print(f"Violations found: {result['num_violations']}")
    
    print("\n" + linter.format_violations(result['violations']))
    
    # Handle fixes
    if args.fix:
        if result['fixed_string']:
            output_path = args.output if args.output else args.input
            with open(output_path, 'w') as f:
                f.write(result['fixed_string'])
            
            print(f"\n✓ Fixed SQL written to: {output_path}")
            
            # Re-lint to show remaining issues
            print("\nRe-linting fixed SQL...")
            recheck = linter.lint_string(result['fixed_string'])
            if recheck['is_clean']:
                print("✓ All fixable violations resolved!")
            else:
                print(f"⚠ {recheck['num_violations']} unfixable violation(s) remain")
                print(linter.format_violations(recheck['violations']))
        else:
            print("\n⚠ No fixes applied")
    
    # Exit code
    sys.exit(0 if result['is_clean'] else 1)


# Example usage as a module
def example_usage():
    """Example of using SQLFluff programmatically."""
    
    # Example SQL with issues
    bad_sql = """
    select id,name,email from users where status='active' and role='admin';
    
    SELECT * FROM orders WHERE total>100;
    """
    
    print("Example: Linting SQL")
    print("=" * 60)
    
    # Initialize linter
    linter = SQLFluffLinter(dialect='mysql')
    
    # Lint the SQL
    result = linter.lint_string(bad_sql, fix=False)
    
    print(f"Original SQL:\n{bad_sql}\n")
    print(linter.format_violations(result['violations']))
    
    # Fix the SQL
    print("\n" + "=" * 60)
    print("Fixing SQL...")
    print("=" * 60)
    
    fixed_result = linter.lint_string(bad_sql, fix=True)
    
    if fixed_result['fixed_string']:
        print(f"\nFixed SQL:\n{fixed_result['fixed_string']}")
        print(f"\nRemaining violations: {fixed_result['num_violations']}")


if __name__ == '__main__':
    # Uncomment to see example usage:
    # example_usage()
    
    main()