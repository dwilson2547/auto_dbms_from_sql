"""
Test suite for common Python SQL formatters
Tests sqlparse, sqlfluff, and demonstrates usage patterns
"""

# Test 1: sqlparse - Basic formatting
print("=" * 60)
print("TEST 1: sqlparse - Basic SQL Formatting")
print("=" * 60)

try:
    import sqlparse
    
    sql = "SELECT id,name,email FROM users WHERE status='active' AND created_at>='2024-01-01' ORDER BY name"
    
    formatted = sqlparse.format(
        sql,
        reindent=True,
        keyword_case='upper'
    )
    
    print("Original SQL:")
    print(sql)
    print("\nFormatted SQL:")
    print(formatted)
    print("✓ sqlparse test passed\n")
except ImportError:
    print("✗ sqlparse not installed. Install with: pip install sqlparse\n")
except Exception as e:
    print(f"✗ Error: {e}\n")


# Test 2: sqlparse - Complex query with joins
print("=" * 60)
print("TEST 2: sqlparse - Complex Query with Joins")
print("=" * 60)

try:
    import sqlparse
    
    complex_sql = """
    SELECT u.id, u.name, COUNT(o.id) as order_count, SUM(o.total) as total_spent 
    FROM users u LEFT JOIN orders o ON u.id = o.user_id 
    WHERE u.status = 'active' AND o.created_at >= '2024-01-01' 
    GROUP BY u.id, u.name HAVING COUNT(o.id) > 5 ORDER BY total_spent DESC
    """
    
    formatted = sqlparse.format(
        complex_sql,
        reindent=True,
        keyword_case='upper',
        indent_width=2
    )
    
    print("Formatted Complex Query:")
    print(formatted)
    print("✓ Complex query test passed\n")
except ImportError:
    print("✗ sqlparse not installed\n")
except Exception as e:
    print(f"✗ Error: {e}\n")


# Test 3: sqlparse - Multiple statements
print("=" * 60)
print("TEST 3: sqlparse - Multiple SQL Statements")
print("=" * 60)

try:
    import sqlparse
    
    multi_sql = """
    INSERT INTO users (name, email) VALUES ('John', 'john@example.com');
    UPDATE users SET status = 'active' WHERE id = 1;
    DELETE FROM sessions WHERE expired = true;
    """
    
    formatted = sqlparse.format(
        multi_sql,
        reindent=True,
        keyword_case='upper'
    )
    
    print("Formatted Multiple Statements:")
    print(formatted)
    
    # Split into individual statements
    statements = sqlparse.split(multi_sql)
    print(f"\n✓ Found {len(statements)} statements")
    print("✓ Multiple statements test passed\n")
except ImportError:
    print("✗ sqlparse not installed\n")
except Exception as e:
    print(f"✗ Error: {e}\n")


# Test 4: sqlparse - Parse and analyze
print("=" * 60)
print("TEST 4: sqlparse - Parse and Analyze SQL")
print("=" * 60)

try:
    import sqlparse
    
    sql = "SELECT * FROM users WHERE id = 1"
    parsed = sqlparse.parse(sql)[0]
    
    print(f"SQL Statement Type: {parsed.get_type()}")
    print(f"Token count: {len(parsed.tokens)}")
    print("\nTokens:")
    for token in parsed.tokens:
        print(f"  {token.ttype}: {token.value!r}")
    
    print("\n✓ Parse and analyze test passed\n")
except ImportError:
    print("✗ sqlparse not installed\n")
except Exception as e:
    print(f"✗ Error: {e}\n")


# Test 5: sqlfluff - Linting (if available)
print("=" * 60)
print("TEST 5: sqlfluff - SQL Linting")
print("=" * 60)

try:
    from sqlfluff.core import Linter
    
    sql = """
    select id,name from users
    where status='active'
    """
    
    linter = Linter(dialect="ansi")
    result = linter.lint_string(sql)
    
    print("Linting Results:")
    if result.violations:
        for violation in result.violations:
            print(f"  Line {violation.line_no}: {violation.description}")
    else:
        print("  No violations found")
    
    print("\n✓ sqlfluff linting test passed\n")
except ImportError:
    print("✗ sqlfluff not installed. Install with: pip install sqlfluff\n")
except Exception as e:
    print(f"✗ Error: {e}\n")


# Test 6: sqlfluff - Fixing
print("=" * 60)
print("TEST 6: sqlfluff - Auto-fixing SQL")
print("=" * 60)

try:
    from sqlfluff.core import Linter
    
    sql = "select id,name from users where status='active'"
    
    linter = Linter(dialect="ansi")
    result = linter.lint_string(sql, fix=True)
    
    print("Original SQL:")
    print(sql)
    print("\nFixed SQL:")
    print(result.tree.raw if result.tree else "No fixes applied")
    print("\n✓ sqlfluff fixing test passed\n")
except ImportError:
    print("✗ sqlfluff not installed\n")
except Exception as e:
    print(f"✗ Error: {e}\n")


# Test 7: Comparison of different formatting styles
print("=" * 60)
print("TEST 7: Formatting Style Comparison")
print("=" * 60)

try:
    import sqlparse
    
    sql = "SELECT u.id, u.name, o.total FROM users u JOIN orders o ON u.id=o.user_id WHERE u.status='active'"
    
    styles = [
        ("Compact", {'reindent': False, 'keyword_case': 'upper'}),
        ("Indented", {'reindent': True, 'keyword_case': 'upper'}),
        ("Lowercase", {'reindent': True, 'keyword_case': 'lower'}),
    ]
    
    for style_name, options in styles:
        formatted = sqlparse.format(sql, **options)
        print(f"\n{style_name} Style:")
        print(formatted)
    
    print("\n✓ Style comparison test passed\n")
except ImportError:
    print("✗ sqlparse not installed\n")
except Exception as e:
    print(f"✗ Error: {e}\n")


# Test 8: Handling SQL with Python string formatting
print("=" * 60)
print("TEST 8: SQL with Python Variables")
print("=" * 60)

try:
    import sqlparse
    
    table_name = "users"
    status = "active"
    
    # Bad practice (SQL injection risk) - for demonstration only
    sql = f"SELECT * FROM {table_name} WHERE status = '{status}'"
    
    formatted = sqlparse.format(sql, reindent=True, keyword_case='upper')
    
    print("Formatted SQL with variables:")
    print(formatted)
    print("\nNote: Use parameterized queries in production!")
    print("✓ Variable formatting test passed\n")
except ImportError:
    print("✗ sqlparse not installed\n")
except Exception as e:
    print(f"✗ Error: {e}\n")


print("=" * 60)
print("TEST SUITE COMPLETE")
print("=" * 60)
print("\nInstallation commands:")
print("  pip install sqlparse")
print("  pip install sqlfluff")