#!/usr/bin/env python3
"""
SQL Minifier Utility
A practical utility for minifying SQL statements
"""

import sqlparse

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