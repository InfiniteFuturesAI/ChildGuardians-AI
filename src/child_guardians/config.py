# =============================================================================
# CHILD GUARDIANS - Configuration
# =============================================================================
# Application configuration with environment variable overrides
# Copy to .env for local development
# =============================================================================

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class DatabaseConfig:
    """Database configuration."""

    url: str = "sqlite:///child_guardians.db"
    pool_size: int = 5
    max_overflow: int = 10
    echo: bool = False


@dataclass
class SecurityConfig:
    """Security configuration."""

    secret_key: str = ""
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    require_tls: bool = True
    allowed_hosts: list[str] = field(default_factory=lambda: ["*"])


@dataclass
class LoggingConfig:
    """Logging configuration."""

    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file: str | None = None
    max_bytes: int = 10_000_000  # 10MB
    backup_count: int = 5


@dataclass
class AuditConfig:
    """Audit logging configuration."""

    enabled: bool = True
    log_queries: bool = True
    log_access: bool = True
    retention_days: int = 365 * 7  # 7 years for legal compliance


@dataclass
class HashRegistryConfig:
    """Hash registry configuration."""

    db_path: str = "hash_registry.db"
    cache_size: int = 10000
    perceptual_threshold: float = 0.95


@dataclass
class Config:
    """Main application configuration."""

    # Core settings
    app_name: str = "CHILD GUARDIANS"
    version: str = "0.1.0"
    environment: str = "development"
    debug: bool = False

    # Sub-configurations
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    audit: AuditConfig = field(default_factory=AuditConfig)
    hash_registry: HashRegistryConfig = field(default_factory=HashRegistryConfig)

    # API settings
    api_prefix: str = "/api/v1"
    cors_origins: list[str] = field(default_factory=list)

    # Data directories
    data_dir: Path = field(default_factory=lambda: Path("data"))
    evidence_dir: Path = field(default_factory=lambda: Path("data/evidence"))

    @classmethod
    def from_env(cls) -> Config:
        """Load configuration from environment variables."""
        config = cls()

        # Core settings
        config.environment = os.getenv("ENVIRONMENT", "development")
        config.debug = os.getenv("DEBUG", "false").lower() == "true"

        # Database
        config.database.url = os.getenv("DATABASE_URL", config.database.url)
        config.database.pool_size = int(os.getenv("DB_POOL_SIZE", str(config.database.pool_size)))

        # Security
        config.security.secret_key = os.getenv("SECRET_KEY", "")
        config.security.require_tls = os.getenv("REQUIRE_TLS", "true").lower() == "true"

        allowed_hosts = os.getenv("ALLOWED_HOSTS", "")
        if allowed_hosts:
            config.security.allowed_hosts = allowed_hosts.split(",")

        # Logging
        config.logging.level = os.getenv("LOG_LEVEL", config.logging.level)
        config.logging.file = os.getenv("LOG_FILE", None)

        # Audit
        config.audit.enabled = os.getenv("AUDIT_ENABLED", "true").lower() == "true"
        config.audit.retention_days = int(
            os.getenv("AUDIT_RETENTION_DAYS", str(config.audit.retention_days))
        )

        # Hash registry
        config.hash_registry.db_path = os.getenv("HASH_REGISTRY_PATH", config.hash_registry.db_path)

        # API settings
        cors_origins = os.getenv("CORS_ORIGINS", "")
        if cors_origins:
            config.cors_origins = cors_origins.split(",")

        # Data directories
        data_dir = os.getenv("DATA_DIR", "data")
        config.data_dir = Path(data_dir)
        config.evidence_dir = config.data_dir / "evidence"

        return config

    def validate(self) -> list[str]:
        """Validate configuration, returning list of errors."""
        errors = []

        if "*" in self.cors_origins:
            errors.append("CORS_ORIGINS must not contain '*' — list explicit origins or leave empty")

        if self.environment == "production":
            if not self.security.secret_key:
                errors.append("SECRET_KEY must be set in production")

            if not self.security.require_tls:
                errors.append("TLS should be required in production")

            if "*" in self.security.allowed_hosts:
                errors.append("ALLOWED_HOSTS should be restricted in production")

            if self.debug:
                errors.append("DEBUG should be False in production")

        return errors


# Global configuration instance
_config: Config | None = None


def get_config() -> Config:
    """Get or create configuration instance."""
    global _config
    if _config is None:
        _config = Config.from_env()
    return _config


def reset_config() -> None:
    """Reset configuration (for testing)."""
    global _config
    _config = None
