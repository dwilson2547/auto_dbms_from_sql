interface FormlyFieldConfig {
  key: string;
  type: string;
  templateOptions?: {
    label?: string;
    placeholder?: string;
    required?: boolean;
    maxLength?: number;
    min?: number;
    max?: number;
    pattern?: string;
    options?: Array<{ label: string; value: any }>;
  };
  validators?: any;
}

interface ColumnDefinition {
  name: string;
  type: string;
  length?: number;
  precision?: number;
  scale?: number;
  nullable: boolean;
  defaultValue?: string;
  isPrimaryKey: boolean;
  isAutoIncrement: boolean;
}

class SqlToFormlyConverter {
  /**
   * Parse a SQL CREATE TABLE statement and extract column definitions
   */
  private parseCreateTable(sql: string): ColumnDefinition[] {
    const columns: ColumnDefinition[] = [];
    
    // Remove comments and normalize whitespace
    sql = sql.replace(/--.*$/gm, '').replace(/\/\*[\s\S]*?\*\//g, '');
    
    // Extract the columns section
    const match = sql.match(/CREATE\s+TABLE\s+\w+\s*\(([\s\S]+)\)/i);
    if (!match) {
      throw new Error('Invalid CREATE TABLE statement');
    }
    
    const columnsSection = match[1];
    const lines = columnsSection.split(',').map(l => l.trim());
    
    for (const line of lines) {
      // Skip constraint definitions
      if (/^(PRIMARY KEY|FOREIGN KEY|UNIQUE|CHECK|CONSTRAINT)/i.test(line)) {
        continue;
      }
      
      const column = this.parseColumnDefinition(line);
      if (column) {
        columns.push(column);
      }
    }
    
    return columns;
  }

  /**
   * Parse a single column definition
   */
  private parseColumnDefinition(columnDef: string): ColumnDefinition | null {
    const parts = columnDef.trim().split(/\s+/);
    if (parts.length < 2) return null;
    
    const name = parts[0].replace(/[`"[\]]/g, '');
    const typeMatch = parts[1].match(/^(\w+)(?:\((\d+)(?:,(\d+))?\))?/i);
    
    if (!typeMatch) return null;
    
    const type = typeMatch[1].toUpperCase();
    const length = typeMatch[2] ? parseInt(typeMatch[2]) : undefined;
    const scale = typeMatch[3] ? parseInt(typeMatch[3]) : undefined;
    
    const defStr = columnDef.toUpperCase();
    
    return {
      name,
      type,
      length,
      precision: length,
      scale,
      nullable: !defStr.includes('NOT NULL'),
      defaultValue: this.extractDefault(columnDef),
      isPrimaryKey: defStr.includes('PRIMARY KEY'),
      isAutoIncrement: defStr.includes('AUTO_INCREMENT') || 
                       defStr.includes('AUTOINCREMENT') ||
                       defStr.includes('IDENTITY')
    };
  }

  /**
   * Extract default value from column definition
   */
  private extractDefault(columnDef: string): string | undefined {
    const match = columnDef.match(/DEFAULT\s+('([^']*)'|"([^"]*)"|(\S+))/i);
    if (match) {
      return match[2] || match[3] || match[4];
    }
    return undefined;
  }

  /**
   * Map SQL type to Formly field type
   */
  private mapSqlTypeToFormlyType(column: ColumnDefinition): string {
    const type = column.type;
    
    // Skip auto-increment fields
    if (column.isAutoIncrement || column.isPrimaryKey) {
      return 'input'; // Will be hidden or readonly
    }
    
    // Text types
    if (['VARCHAR', 'CHAR', 'TEXT', 'NVARCHAR', 'NCHAR'].includes(type)) {
      if (column.length && column.length > 255) {
        return 'textarea';
      }
      return 'input';
    }
    
    // Numeric types
    if (['INT', 'INTEGER', 'BIGINT', 'SMALLINT', 'TINYINT'].includes(type)) {
      return 'input';
    }
    
    if (['DECIMAL', 'NUMERIC', 'FLOAT', 'DOUBLE', 'REAL'].includes(type)) {
      return 'input';
    }
    
    // Boolean
    if (['BOOLEAN', 'BOOL', 'BIT'].includes(type)) {
      return 'checkbox';
    }
    
    // Date/Time
    if (['DATE', 'DATETIME', 'TIMESTAMP', 'TIME'].includes(type)) {
      return 'input';
    }
    
    // Default
    return 'input';
  }

  /**
   * Create template options for a column
   */
  private createTemplateOptions(column: ColumnDefinition): any {
    const opts: any = {
      label: this.formatLabel(column.name),
      required: !column.nullable
    };
    
    const type = column.type;
    
    // Text inputs
    if (['VARCHAR', 'CHAR', 'NVARCHAR', 'NCHAR'].includes(type)) {
      opts.type = 'text';
      if (column.length) {
        opts.maxLength = column.length;
      }
    }
    
    // Numeric inputs
    if (['INT', 'INTEGER', 'BIGINT', 'SMALLINT', 'TINYINT'].includes(type)) {
      opts.type = 'number';
      opts.pattern = '^-?\\d+$';
    }
    
    if (['DECIMAL', 'NUMERIC', 'FLOAT', 'DOUBLE', 'REAL'].includes(type)) {
      opts.type = 'number';
      opts.step = column.scale ? Math.pow(10, -column.scale) : 0.01;
    }
    
    // Date inputs
    if (type === 'DATE') {
      opts.type = 'date';
    } else if (type === 'DATETIME' || type === 'TIMESTAMP') {
      opts.type = 'datetime-local';
    } else if (type === 'TIME') {
      opts.type = 'time';
    }
    
    // Email pattern for common email columns
    if (column.name.toLowerCase().includes('email')) {
      opts.type = 'email';
      opts.pattern = '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$';
    }
    
    // Default value
    if (column.defaultValue) {
      opts.defaultValue = column.defaultValue;
    }
    
    return opts;
  }

  /**
   * Format column name to human-readable label
   */
  private formatLabel(columnName: string): string {
    return columnName
      .replace(/_/g, ' ')
      .replace(/([A-Z])/g, ' $1')
      .trim()
      .split(' ')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
      .join(' ');
  }

  /**
   * Convert a SQL CREATE TABLE statement to FormlyFieldConfig array
   */
  public convert(sql: string, options?: {
    excludeAutoIncrement?: boolean;
    excludePrimaryKey?: boolean;
    readonly?: string[];
  }): FormlyFieldConfig[] {
    const columns = this.parseCreateTable(sql);
    const fields: FormlyFieldConfig[] = [];
    
    const opts = {
      excludeAutoIncrement: true,
      excludePrimaryKey: false,
      readonly: [],
      ...options
    };
    
    for (const column of columns) {
      // Skip auto-increment if requested
      if (opts.excludeAutoIncrement && column.isAutoIncrement) {
        continue;
      }
      
      // Skip primary key if requested
      if (opts.excludePrimaryKey && column.isPrimaryKey) {
        continue;
      }
      
      const field: FormlyFieldConfig = {
        key: column.name,
        type: this.mapSqlTypeToFormlyType(column),
        templateOptions: this.createTemplateOptions(column)
      };
      
      // Mark as readonly if specified
      if (opts.readonly?.includes(column.name)) {
        field.templateOptions!.readonly = true;
      }
      
      fields.push(field);
    }
    
    return fields;
  }

  /**
   * Convert and return as JSON string
   */
  public convertToJson(sql: string, options?: any): string {
    const fields = this.convert(sql, options);
    return JSON.stringify(fields, null, 2);
  }
}

// Example usage
const converter = new SqlToFormlyConverter();

const exampleSql = `
CREATE TABLE users (
  id INT PRIMARY KEY AUTO_INCREMENT,
  username VARCHAR(50) NOT NULL,
  email VARCHAR(100) NOT NULL,
  age INT,
  bio TEXT,
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)`;

console.log('SQL Table:');
console.log(exampleSql);
console.log('\nFormly Field Config:');
console.log(converter.convertToJson(exampleSql));

// Export for use in other modules
export { SqlToFormlyConverter, FormlyFieldConfig, ColumnDefinition };