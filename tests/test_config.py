"""
Tests for child_guardians.config module.

Tests configuration loading, environment variable overrides,
and production validation.
"""

import os
from pathlib import Path
from unittest.mock import patch

from child_guardians.config import (
    AuditConfig,
    Config,
    DatabaseConfig,
    HashRegistryConfig,
    LoggingConfig,
    SecurityConfig,
    get_config,
    reset_config,
)


class TestDatabaseConfig:
    """Tests for DatabaseConfig dataclass."""

    def test_default_values(self):
        """Test default database configuration."""
        config = DatabaseConfig()
        assert config.url == "sqlite:///child_guardians.db"
        assert config.pool_size == 5
        assert config.max_overflow == 10
        assert config.echo is False

    def test_custom_values(self):
        """Test custom database configuration."""
        config = DatabaseConfig(
            url="postgresql://localhost/test",
            pool_size=10,
            max_overflow=20,
            echo=True,
        )
        assert config.url == "postgresql://localhost/test"
        assert config.pool_size == 10
        assert config.max_overflow == 20
        assert config.echo is True


class TestSecurityConfig:
    """Tests for SecurityConfig dataclass."""

    def test_default_values(self):
        """Test default security configuration."""
        config = SecurityConfig()
        assert config.secret_key == ""
        assert config.algorithm == "HS256"
        assert config.access_token_expire_minutes == 30
        assert config.require_tls is True
        assert config.allowed_hosts == ["*"]

    def test_custom_values(self):
        """Test custom security configuration."""
        config = SecurityConfig(
            secret_key="my-secret-key",
            algorithm="HS512",
            access_token_expire_minutes=60,
            require_tls=False,
            allowed_hosts=["example.com"],
        )
        assert config.secret_key == "my-secret-key"
        assert config.algorithm == "HS512"
        assert config.access_token_expire_minutes == 60
        assert config.require_tls is False
        assert config.allowed_hosts == ["example.com"]


class TestLoggingConfig:
    """Tests for LoggingConfig dataclass."""

    def test_default_values(self):
        """Test default logging configuration."""
        config = LoggingConfig()
        assert config.level == "INFO"
        assert "%(asctime)s" in config.format
        assert config.file is None
        assert config.max_bytes == 10_000_000
        assert config.backup_count == 5


class TestAuditConfig:
    """Tests for AuditConfig dataclass."""

    def test_default_values(self):
        """Test default audit configuration."""
        config = AuditConfig()
        assert config.enabled is True
        assert config.log_queries is True
        assert config.log_access is True
        assert config.retention_days == 365 * 7  # 7 years


class TestHashRegistryConfig:
    """Tests for HashRegistryConfig dataclass."""

    def test_default_values(self):
        """Test default hash registry configuration."""
        config = HashRegistryConfig()
        assert config.db_path == "hash_registry.db"
        assert config.cache_size == 10000
        assert config.perceptual_threshold == 0.95


class TestConfig:
    """Tests for main Config class."""

    def test_default_values(self):
        """Test default configuration values."""
        config = Config()
        assert config.app_name == "CHILD GUARDIANS"
        assert config.version == "0.1.0"
        assert config.environment == "development"
        assert config.debug is False
        assert config.api_prefix == "/api/v1"
        assert isinstance(config.database, DatabaseConfig)
        assert isinstance(config.security, SecurityConfig)
        assert isinstance(config.logging, LoggingConfig)
        assert isinstance(config.audit, AuditConfig)
        assert isinstance(config.hash_registry, HashRegistryConfig)

    def test_data_directories(self):
        """Test default data directories."""
        config = Config()
        assert config.data_dir == Path("data")
        assert config.evidence_dir == Path("data/evidence")

    def test_from_env_defaults(self):
        """Test from_env with no environment variables set."""
        reset_config()
        # Clear any existing env vars that might interfere
        env_vars = [
            "ENVIRONMENT",
            "DEBUG",
            "DATABASE_URL",
            "DB_POOL_SIZE",
            "SECRET_KEY",
            "REQUIRE_TLS",
            "ALLOWED_HOSTS",
            "LOG_LEVEL",
            "LOG_FILE",
            "AUDIT_ENABLED",
            "AUDIT_RETENTION_DAYS",
            "HASH_REGISTRY_PATH",
            "CORS_ORIGINS",
            "DATA_DIR",
        ]
        with patch.dict(os.environ, {}, clear=True):
            for var in env_vars:
                os.environ.pop(var, None)
            config = Config.from_env()
            assert config.environment == "development"
            assert config.debug is False

    def test_from_env_with_overrides(self):
        """Test from_env with environment variable overrides."""
        reset_config()
        env = {
            "ENVIRONMENT": "production",
            "DEBUG": "true",
            "DATABASE_URL": "postgresql://prod/db",
            "DB_POOL_SIZE": "20",
            "SECRET_KEY": "super-secret",
            "REQUIRE_TLS": "false",
            "ALLOWED_HOSTS": "example.com,api.example.com",
            "LOG_LEVEL": "DEBUG",
            "LOG_FILE": "/var/log/app.log",
            "AUDIT_ENABLED": "false",
            "AUDIT_RETENTION_DAYS": "365",
            "HASH_REGISTRY_PATH": "/data/hashes.db",
            "CORS_ORIGINS": "https://app.example.com",
            "DATA_DIR": "/app/data",
        }
        with patch.dict(os.environ, env, clear=True):
            config = Config.from_env()

            assert config.environment == "production"
            assert config.debug is True
            assert config.database.url == "postgresql://prod/db"
            assert config.database.pool_size == 20
            assert config.security.secret_key == "super-secret"
            assert config.security.require_tls is False
            assert config.security.allowed_hosts == ["example.com", "api.example.com"]
            assert config.logging.level == "DEBUG"
            assert config.logging.file == "/var/log/app.log"
            assert config.audit.enabled is False
            assert config.audit.retention_days == 365
            assert config.hash_registry.db_path == "/data/hashes.db"
            assert config.cors_origins == ["https://app.example.com"]
            assert config.data_dir == Path("/app/data")
            assert config.evidence_dir == Path("/app/data/evidence")


class TestConfigValidation:
    """Tests for configuration validation."""

    def test_validate_development_passes(self):
        """Test that development config validates without errors."""
        config = Config()
        config.environment = "development"
        errors = config.validate()
        assert errors == []

    def test_validate_production_missing_secret(self):
        """Test that production config requires SECRET_KEY."""
        config = Config()
        config.environment = "production"
        config.security.secret_key = ""
        errors = config.validate()
        assert "SECRET_KEY must be set in production" in errors

    def test_validate_production_tls_required(self):
        """Test that production config requires TLS."""
        config = Config()
        config.environment = "production"
        config.security.secret_key = "secret"
        config.security.require_tls = False
        errors = config.validate()
        assert "TLS should be required in production" in errors

    def test_validate_production_allowed_hosts(self):
        """Test that production config restricts allowed hosts."""
        config = Config()
        config.environment = "production"
        config.security.secret_key = "secret"
        config.security.allowed_hosts = ["*"]
        errors = config.validate()
        assert "ALLOWED_HOSTS should be restricted in production" in errors

    def test_validate_production_debug_disabled(self):
        """Test that production config disables debug."""
        config = Config()
        config.environment = "production"
        config.security.secret_key = "secret"
        config.debug = True
        errors = config.validate()
        assert "DEBUG should be False in production" in errors

    def test_validate_production_all_good(self):
        """Test that properly configured production passes validation."""
        config = Config()
        config.environment = "production"
        config.security.secret_key = "super-secret-key"
        config.security.require_tls = True
        config.security.allowed_hosts = ["api.example.com"]
        config.debug = False
        errors = config.validate()
        assert errors == []


class TestGetConfig:
    """Tests for get_config and reset_config functions."""

    def test_get_config_singleton(self):
        """Test that get_config returns the same instance."""
        reset_config()
        config1 = get_config()
        config2 = get_config()
        assert config1 is config2

    def test_reset_config(self):
        """Test that reset_config clears the singleton."""
        reset_config()
        config1 = get_config()
        reset_config()
        config2 = get_config()
        # Different instances after reset
        assert config1 is not config2

    def test_get_config_loads_from_env(self):
        """Test that get_config loads from environment."""
        reset_config()
        with patch.dict(os.environ, {"ENVIRONMENT": "staging"}):
            config = get_config()
            assert config.environment == "staging"
        reset_config()
