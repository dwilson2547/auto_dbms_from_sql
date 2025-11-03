import sys
from config.Config import Config
from utils.minifier.minifier import SQLMinifier
from utils.manual_cleanup.cleanup import apply_default_fixes
import logging

from utils.linter.manual_cleanup import apply_default_fixes
from utils.linter.sql_minifier import SQLMinifier
from sqlfluff.core import FluffConfig
from sqlfluff import lint, fix

log = logging.getLogger(__name__)



class TableSqlFormatter:
    def __init__(self, config: Config):
        self.config = config
        self.fluff_config_path = self.config.parse_config.fluff_config_path
        self.minifier = SQLMinifier()
        self.fluff_config = FluffConfig.from_path(
            path=self.fluff_config_path,
            require_dialect=False
        )
        
    def fix_table_sql(self, sql_text: str) -> str:
        fixed_sql = apply_default_fixes(sql_text)
        minified_sql = self.minifier.minify(fixed_sql)

        linter_errors = lint(minified_sql, config=self.fluff_config)
        for error in linter_errors:
            if 'fixes' not in error:
                log.error('Unrecoverable error found in input SQL:', error)
                sys.exit(1)

        repaired = apply_default_fixes(fix(minified_sql, config=self.fluff_config))
        log.debug(f'Repaired SQL: {repaired}')

        return repaired

