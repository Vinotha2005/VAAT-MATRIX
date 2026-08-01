import importlib


def test_local_windows_defaults_to_sqlite(monkeypatch):
    monkeypatch.delenv("LOCAL_DEV", raising=False)
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg2://postgres:postgres@db:5432/accesslearn")
    monkeypatch.setattr("os.name", "nt")

    import app.database as database
    importlib.reload(database)

    assert database.DATABASE_URL == "sqlite:///./accesslearn.db"
