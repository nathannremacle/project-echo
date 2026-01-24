"""
Unit tests for health check utilities
"""

import os
import pytest
from unittest.mock import patch, MagicMock

from src.schemas.health import ComponentCheck, HealthCheckResponse
from src.utils.health_check import (
    check_database,
    check_github_actions,
    check_dependencies,
    check_configuration,
    perform_health_check,
)


class TestCheckDatabase:
    """Tests for database health check"""

    def test_check_database_success(self):
        """Test successful database check"""
        with patch("src.utils.health_check.SessionLocal") as mock_session:
            mock_db = MagicMock()
            mock_session.return_value.__enter__.return_value = mock_db
            mock_db.execute.return_value = None
            mock_db.commit.return_value = None
            
            status, message = check_database()
            
            assert status == "ok"
            assert "successful" in message.lower()

    def test_check_database_failure(self):
        """Test database check failure"""
        with patch("src.utils.health_check.SessionLocal") as mock_session:
            from sqlalchemy.exc import SQLAlchemyError
            
            mock_session.return_value.__enter__.side_effect = SQLAlchemyError("Connection failed")
            
            status, message = check_database()
            
            assert status == "error"
            assert "failed" in message.lower()


class TestCheckGitHubActions:
    """Tests for GitHub Actions environment check"""

    def test_check_github_actions_detected(self):
        """Test GitHub Actions environment detection"""
        with patch.dict(os.environ, {
            "GITHUB_ACTIONS": "true",
            "GITHUB_WORKFLOW": "test-workflow",
            "GITHUB_REPOSITORY": "user/repo",
        }):
            status, message = check_github_actions()
            
            assert status == "ok"
            assert "github actions" in message.lower()

    def test_check_github_actions_not_detected(self):
        """Test when not running in GitHub Actions"""
        with patch.dict(os.environ, {}, clear=True):
            status, message = check_github_actions()
            
            assert status == "ok"
            assert "not running" in message.lower() or "local" in message.lower()


class TestCheckDependencies:
    """Tests for dependencies check"""

    def test_check_dependencies_success(self):
        """Test successful dependencies check"""
        with patch("builtins.__import__", return_value=MagicMock()):
            status, message = check_dependencies()
            
            assert status == "ok"
            assert "available" in message.lower()

    def test_check_dependencies_missing(self):
        """Test missing dependencies"""
        def mock_import(name):
            if name == "missing_module":
                raise ImportError(f"No module named '{name}'")
            return MagicMock()
        
        with patch("builtins.__import__", side_effect=mock_import):
            # Temporarily add a missing dependency to the list
            original_deps = check_dependencies.__globals__.get("REQUIRED_DEPENDENCIES", [])
            with patch.object(
                check_dependencies.__globals__,
                "REQUIRED_DEPENDENCIES",
                ["missing_module"]
            ):
                status, message = check_dependencies()
                
                assert status == "error"
                assert "missing" in message.lower()


class TestCheckConfiguration:
    """Tests for configuration check"""

    def test_check_configuration_success(self):
        """Test successful configuration check"""
        with patch("src.utils.health_check.settings") as mock_settings:
            mock_settings.DATABASE_URL = "sqlite:///test.db"
            mock_settings.is_production.return_value = False
            
            status, message = check_configuration()
            
            assert status == "ok"
            assert "successfully" in message.lower()

    def test_check_configuration_missing_database_url(self):
        """Test configuration check with missing DATABASE_URL"""
        with patch("src.utils.health_check.settings") as mock_settings:
            mock_settings.DATABASE_URL = ""
            mock_settings.is_production.return_value = False
            
            status, message = check_configuration()
            
            assert status == "error"
            assert "database_url" in message.lower()

    def test_check_configuration_production_missing_secrets(self):
        """Test configuration check in production with missing secrets"""
        with patch("src.utils.health_check.settings") as mock_settings:
            mock_settings.DATABASE_URL = "postgresql://localhost/db"
            mock_settings.is_production.return_value = True
            mock_settings.JWT_SECRET_KEY = ""
            mock_settings.ENCRYPTION_KEY = ""
            
            status, message = check_configuration()
            
            assert status == "error"
            assert "issues" in message.lower()


class TestPerformHealthCheck:
    """Tests for complete health check"""

    def test_perform_health_check_healthy(self):
        """Test health check when all components are healthy"""
        with patch("src.utils.health_check.check_database", return_value=("ok", "OK")):
            with patch("src.utils.health_check.check_github_actions", return_value=("ok", "OK")):
                with patch("src.utils.health_check.check_dependencies", return_value=("ok", "OK")):
                    with patch("src.utils.health_check.check_configuration", return_value=("ok", "OK")):
                        result = perform_health_check()
                        
                        assert isinstance(result, HealthCheckResponse)
                        assert result.status == "healthy"
                        assert len(result.checks) == 4
                        assert all(check.status == "ok" for check in result.checks.values())

    def test_perform_health_check_degraded(self):
        """Test health check when some components fail"""
        with patch("src.utils.health_check.check_database", return_value=("error", "Failed")):
            with patch("src.utils.health_check.check_github_actions", return_value=("ok", "OK")):
                with patch("src.utils.health_check.check_dependencies", return_value=("ok", "OK")):
                    with patch("src.utils.health_check.check_configuration", return_value=("ok", "OK")):
                        result = perform_health_check()
                        
                        assert result.status == "degraded"
                        assert result.checks["database"].status == "error"

    def test_perform_health_check_unhealthy(self):
        """Test health check when all components fail"""
        with patch("src.utils.health_check.check_database", return_value=("error", "Failed")):
            with patch("src.utils.health_check.check_github_actions", return_value=("error", "Failed")):
                with patch("src.utils.health_check.check_dependencies", return_value=("error", "Failed")):
                    with patch("src.utils.health_check.check_configuration", return_value=("error", "Failed")):
                        result = perform_health_check()
                        
                        assert result.status == "unhealthy"
                        assert all(check.status == "error" for check in result.checks.values())
