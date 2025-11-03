import re
import logging

log = logging.getLogger(__name__)

class SqlFix():
    type: str

    def __init__(self, type: str):
        self.type = type

    def apply_fix(self, sql: str) -> str:
        pass

class SqlRegexReplaceOnceFix(SqlFix):

    def __init__(self, pattern: str, replacement: str):
        super().__init__(self.__class__.__name__)
        self.pattern = pattern
        self.replacement = replacement

    def apply_fix(self, sql: str) -> str:
        return re.sub(self.pattern, self.replacement, sql)

class SqlRegexReplaceAllFix(SqlFix):

    def __init__(self, pattern: str, replacement: str):
        super().__init__(self.__class__.__name__)
        self.pattern = pattern
        self.replacement = replacement

    def apply_fix(self, sql: str) -> str:
        return re.subn(self.pattern, self.replacement, sql)

split_not_null_fix = SqlRegexReplaceAllFix(
    pattern=r'NOT([\s\r]+)NULL',
    replacement='NOT NULL')

hanging_comma_fix = SqlRegexReplaceAllFix(
    pattern=r'([\s]+),',
    replacement=',')

random_return_fix = SqlRegexReplaceAllFix(
    pattern=r'([a-zA-Z]+)[\r\s]+([a-zA-Z\,_]+)',
    replacement=r'\1 \2')

default_fixes = [
    split_not_null_fix,
    hanging_comma_fix,
    random_return_fix
]

def apply_default_fixes(text: str):
    for fix in default_fixes:
        text, count = fix.apply_fix(text)
        log.debug(f"Applied {fix.type}: {count} substitutions")
    return text