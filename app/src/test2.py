import sys
import sqlparse

from auto_dbms.app.src.utils.linter.manual_cleanup import apply_default_fixes
from utils.linter.sql_minifier import SQLMinifier
from sqlfluff.core import Linter, FluffConfig
from sqlfluff.core.errors import SQLLintError
from sqlfluff import lint, fix

sql = open('/home/daniel/documents/auto_dbms/app/src/utils/linter/demo_table.sql').read()
fixed_sql = apply_default_fixes(sql)

# print(fixed_sql)

minified_sql = SQLMinifier().minify(fixed_sql)

print(minified_sql)

config = FluffConfig.from_path(
    path='/home/daniel/documents/auto_dbms/app/src/utils/linter/',
    require_dialect=False
)

res = lint(minified_sql, config=config)
for v in res:
    if 'fixes' not in v:
        print('Unrecoverable error found in input SQL:')
        print(v)
        sys.exit(1)

out = fix(minified_sql, config=config)
print(out)

print(apply_default_fixes(out))