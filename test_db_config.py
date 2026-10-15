
import db_config


def test_database_url_is_read_from_environment(monkeypatch):
    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql://example:example@localhost:5432/expenses"
    )

    assert db_config.get_database_url() == (
        "postgresql://example:example@localhost:5432/expenses"
    )


def test_database_url_is_empty_when_not_configured(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)

    assert db_config.get_database_url() == ""
