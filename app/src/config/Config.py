import os
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum
import logging

log = logging.getLogger(__name__)

class LogLevel(Enum):
    """Logging levels"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

@dataclass
class LoggingConfig:
    """Logging configuration"""
    level: LogLevel = LogLevel.INFO
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: Optional[str] = None
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5
    console_output: bool = True
    
@dataclass
class ParseConfig:
    fluff_config_path: str = ''

class Config:
    
    project_name: str = "AutoDBMS"
    version: str = "1.0.0"
    environment: str = "development"
    api_prefix: str = "/api"

    logging_config: LoggingConfig
    parse_config: ParseConfig

    def __init__(self, config_file: Optional[str] = None):
        
        self.logging_config = LoggingConfig()
        self.parse_config = ParseConfig()
        self.module_logging: Dict[str, LoggingConfig] = {}
        
        if config_file:
            self.load_from_file(config_file)
        else:
            self.load_from_environment()
            
    
    def load_from_environment(self):
        """Load configuration from environment variables"""
        # Parse configuration
        self.parse_config.fluff_config_path = os.getenv("FLUFF_CONFIG_PATH", self.parse_config.fluff_config_path)
        
        # Logging configuration
        self.logging_config.level = LogLevel[os.getenv("LOG_LEVEL", self.logging_config.level.name.upper())]
        self.logging_config.file_path = os.getenv("LOG_FILE_PATH", self.logging_config.file_path)
        self.logging_config.max_file_size = int(os.getenv("LOG_MAX_FILE_SIZE", self.logging_config.max_file_size))
        self.logging_config.backup_count = int(os.getenv("LOG_BACKUP_COUNT", self.logging_config.backup_count))
        self.logging_config.console_output = os.getenv("LOG_CONSOLE_OUTPUT", str(self.logging_config.console_output)).lower() == "true"

    def load_from_file(self, file_path: str):
        """Load configuration from a JSON file"""
        with open(file_path, 'r') as f:
            data = json.load(f)

        self.project_name = data.get("project_name", self.project_name)
        self.version = data.get("version", self.version)
        self.environment = data.get("environment", self.environment)
        self.api_prefix = data.get("api_prefix", self.api_prefix)

        # Parse configuration
        config_dir = os.path.dirname(os.path.abspath(file_path))
        parse_data = data.get("parse", {})
        raw_fluff_path = parse_data.get("fluff_config_path", self.parse_config.fluff_config_path)
        if raw_fluff_path and not os.path.isabs(raw_fluff_path):
            raw_fluff_path = os.path.join(config_dir, raw_fluff_path)
        self.parse_config.fluff_config_path = raw_fluff_path
        
        # Logging configuration
        logging_data = data.get("logging", {})
        self.logging_config.level = LogLevel[logging_data.get("level", self.logging_config.level.name)]
        self.logging_config.file_path = logging_data.get("file_path", self.logging_config.file_path)
        self.logging_config.max_file_size = logging_data.get("max_file_size", self.logging_config.max_file_size)
        self.logging_config.backup_count = logging_data.get("backup_count", self.logging_config.backup_count)
        self.logging_config.console_output = logging_data.get("console_output", self.logging_config.console_output)
        
        module_logging_data = data.get("module_logging", {})
        for module, config in module_logging_data.items():
            mod_log_config = LoggingConfig(
                level=LogLevel[config.get("level", self.logging_config.level.name)],
                format=config.get("format", self.logging_config.format),
                file_path=config.get("file_path", self.logging_config.file_path),
                max_file_size=config.get("max_file_size", self.logging_config.max_file_size),
                backup_count=config.get("backup_count", self.logging_config.backup_count),
                console_output=config.get("console_output", self.logging_config.console_output)
            )
            self.module_logging[module] = mod_log_config
