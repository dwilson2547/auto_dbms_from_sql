import re
import sys

class SQLToFlaskSQLAlchemy:
    def __init__(self):
        self.type_mapping = {
            'INTEGER': 'Integer',
            'INT': 'Integer',
            'SMALLINT': 'SmallInteger',
            'BIGINT': 'BigInteger',
            'VARCHAR': 'String',
            'CHAR': 'String',
            'TEXT': 'Text',
            'BOOLEAN': 'Boolean',
            'BOOL': 'Boolean',
            'DATE': 'Date',
            'DATETIME': 'DateTime',
            'TIMESTAMP': 'DateTime',
            'TIME': 'Time',
            'FLOAT': 'Float',
            'DOUBLE': 'Float',
            'DECIMAL': 'Numeric',
            'NUMERIC': 'Numeric',
            'BLOB': 'LargeBinary',
            'BINARY': 'LargeBinary',
            'JSON': 'JSON',
        }
    
    def to_camel_case(self, snake_str):
        """Convert snake_case to CamelCase"""
        components = snake_str.split('_')
        return ''.join(x.title() for x in components)
    
    def parse_column_type(self, col_type):
        """Parse SQL column type and return SQLAlchemy type"""
        col_type = col_type.strip().upper()
        
        # Handle types with length like VARCHAR(255)
        match = re.match(r'(\w+)\((\d+)\)', col_type)
        if match:
            base_type = match.group(1)
            length = match.group(2)
            if base_type in ['VARCHAR', 'CHAR']:
                return f'String({length})'
            elif base_type in ['DECIMAL', 'NUMERIC']:
                return f'Numeric({length})'
        
        # Handle types with precision like DECIMAL(10,2)
        match = re.match(r'(\w+)\((\d+),\s*(\d+)\)', col_type)
        if match:
            base_type = match.group(1)
            precision = match.group(2)
            scale = match.group(3)
            if base_type in ['DECIMAL', 'NUMERIC']:
                return f'Numeric(precision={precision}, scale={scale})'
        
        # Simple type mapping
        for sql_type, sa_type in self.type_mapping.items():
            if col_type.startswith(sql_type):
                return sa_type
        
        return 'String'  # Default fallback
    
    def parse_create_table(self, sql):
        """Parse a CREATE TABLE statement"""
        # Extract table name
        table_match = re.search(r'CREATE TABLE\s+(?:IF NOT EXISTS\s+)?`?(\w+)`?\s*\(', sql, re.IGNORECASE)
        if not table_match:
            return None
        
        table_name = table_match.group(1)
        class_name = self.to_camel_case(table_name)
        
        # Extract columns section
        columns_section = re.search(r'\((.*)\)', sql, re.DOTALL | re.IGNORECASE)
        if not columns_section:
            return None
        
        columns_text = columns_section.group(1)
        
        # Split by comma, but be careful with commas inside parentheses
        columns = []
        current_col = []
        paren_depth = 0
        
        for char in columns_text + ',':
            if char == '(':
                paren_depth += 1
                current_col.append(char)
            elif char == ')':
                paren_depth -= 1
                current_col.append(char)
            elif char == ',' and paren_depth == 0:
                col_str = ''.join(current_col).strip()
                if col_str:
                    columns.append(col_str)
                current_col = []
            else:
                current_col.append(char)
        
        # Parse each column
        parsed_columns = []
        primary_keys = []
        foreign_keys = []
        
        for col in columns:
            col = col.strip()
            
            # Skip constraint definitions
            if re.match(r'(PRIMARY KEY|FOREIGN KEY|CONSTRAINT|UNIQUE|INDEX|KEY)\s*\(', col, re.IGNORECASE):
                # Extract primary key
                pk_match = re.search(r'PRIMARY KEY\s*\(\s*`?(\w+)`?\s*\)', col, re.IGNORECASE)
                if pk_match:
                    primary_keys.append(pk_match.group(1))
                
                # Extract foreign key
                fk_match = re.search(r'FOREIGN KEY\s*\(\s*`?(\w+)`?\s*\)\s*REFERENCES\s+`?(\w+)`?\s*\(\s*`?(\w+)`?\s*\)', col, re.IGNORECASE)
                if fk_match:
                    foreign_keys.append({
                        'column': fk_match.group(1),
                        'ref_table': fk_match.group(2),
                        'ref_column': fk_match.group(3)
                    })
                continue
            
            # Parse column definition
            parts = col.split()
            if len(parts) < 2:
                continue
            
            col_name = parts[0].strip('`')
            col_type = parts[1]
            
            # Parse constraints
            is_primary = 'PRIMARY KEY' in col.upper() or col_name in primary_keys
            is_nullable = 'NOT NULL' not in col.upper() and not is_primary
            is_unique = 'UNIQUE' in col.upper()
            is_autoincrement = 'AUTO_INCREMENT' in col.upper() or 'AUTOINCREMENT' in col.upper()
            
            # Check for foreign key
            fk_ref = None
            for fk in foreign_keys:
                if fk['column'] == col_name:
                    fk_ref = f"{fk['ref_table']}.{fk['ref_column']}"
                    break
            
            # Check inline foreign key
            fk_inline = re.search(r'REFERENCES\s+`?(\w+)`?\s*\(\s*`?(\w+)`?\s*\)', col, re.IGNORECASE)
            if fk_inline:
                fk_ref = f"{fk_inline.group(1)}.{fk_inline.group(2)}"
            
            # Extract default value
            default_match = re.search(r'DEFAULT\s+([^\s,]+)', col, re.IGNORECASE)
            default_value = default_match.group(1) if default_match else None
            
            parsed_columns.append({
                'name': col_name,
                'type': self.parse_column_type(col_type),
                'primary_key': is_primary,
                'nullable': is_nullable,
                'unique': is_unique,
                'autoincrement': is_autoincrement,
                'foreign_key': fk_ref,
                'default': default_value
            })
        
        return {
            'table_name': table_name,
            'class_name': class_name,
            'columns': parsed_columns
        }
    
    def generate_model(self, table_info):
        """Generate Flask-SQLAlchemy model code"""
        lines = []
        lines.append(f"class {table_info['class_name']}(db.Model):")
        lines.append(f"    __tablename__ = '{table_info['table_name']}'")
        lines.append("")
        
        for col in table_info['columns']:
            col_def = f"    {col['name']} = db.Column(db.{col['type']}"
            
            constraints = []
            if col['foreign_key']:
                constraints.append(f"db.ForeignKey('{col['foreign_key']}')")
            if col['primary_key']:
                constraints.append("primary_key=True")
            if col['autoincrement'] and col['primary_key']:
                constraints.append("autoincrement=True")
            if not col['nullable'] and not col['primary_key']:
                constraints.append("nullable=False")
            if col['unique']:
                constraints.append("unique=True")
            if col['default']:
                if col['default'].upper() in ['TRUE', 'FALSE']:
                    constraints.append(f"default={col['default'].capitalize()}")
                elif col['default'].isdigit():
                    constraints.append(f"default={col['default']}")
                else:
                    constraints.append(f"default='{col['default']}'")
            
            if constraints:
                col_def += ", " + ", ".join(constraints)
            
            col_def += ")"
            lines.append(col_def)
        
        return "\n".join(lines)
    
    def convert(self, sql_script):
        """Convert SQL script to Flask-SQLAlchemy models"""
        # Split by CREATE TABLE statements
        tables = re.split(r'(?=CREATE TABLE)', sql_script, flags=re.IGNORECASE)
        
        output = []
        output.append("from flask_sqlalchemy import SQLAlchemy")
        output.append("")
        output.append("db = SQLAlchemy()")
        output.append("")
        output.append("")
        
        for table_sql in tables:
            table_sql = table_sql.strip()
            if not table_sql:
                continue
            
            table_info = self.parse_create_table(table_sql)
            if table_info:
                model_code = self.generate_model(table_info)
                output.append(model_code)
                output.append("")
                output.append("")
        
        return "\n".join(output)


def main():
    if len(sys.argv) < 2:
        print("Usage: python script.py <sql_file>")
        print("Or pipe SQL: cat schema.sql | python script.py")
        sys.exit(1)
    
    # Read from file or stdin
    if sys.argv[1] == '-':
        sql_script = sys.stdin.read()
    else:
        with open(sys.argv[1], 'r') as f:
            sql_script = f.read()
    
    converter = SQLToFlaskSQLAlchemy()
    result = converter.convert(sql_script)
    print(result)


if __name__ == "__main__":
    # Example usage if no arguments provided
    if len(sys.argv) == 1:
        example_sql = """
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username VARCHAR(80) NOT NULL UNIQUE,
            email VARCHAR(120) NOT NULL UNIQUE,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title VARCHAR(200) NOT NULL,
            content TEXT,
            user_id INTEGER NOT NULL,
            published BOOLEAN DEFAULT FALSE,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
        """
        
        converter = SQLToFlaskSQLAlchemy()
        result = converter.convert(example_sql)
        print("Example output:")
        print("=" * 50)
        print(result)
        print("=" * 50)
        print("\nTo use with your own SQL file:")
        print("  python script.py schema.sql")
    else:
        main()