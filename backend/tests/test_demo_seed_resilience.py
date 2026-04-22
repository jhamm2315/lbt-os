import unittest

from app.services.demo_data import reset_org_operating_data


class _DeleteQuery:
    def __init__(self, table: str, missing_tables: set[str], calls: list[str]):
        self.table = table
        self.missing_tables = missing_tables
        self.calls = calls

    def delete(self):
        return self

    def eq(self, _field, _value):
        return self

    def execute(self):
        self.calls.append(self.table)
        if self.table in self.missing_tables:
            raise Exception(f"Could not find the table 'public.{self.table}' in the schema cache")
        return {"status": "ok"}


class _FakeDb:
    def __init__(self, missing_tables: set[str]):
        self.missing_tables = missing_tables
        self.calls: list[str] = []

    def table(self, table: str):
        return _DeleteQuery(table, self.missing_tables, self.calls)


class DemoSeedResilienceTests(unittest.TestCase):
    def test_reset_org_operating_data_ignores_missing_integration_tables(self):
        db = _FakeDb({"integration_connections", "integration_sync_runs", "integration_record_links"})
        reset_org_operating_data(db, "org_123")
        self.assertIn("leads", db.calls)
        self.assertIn("expenses", db.calls)


if __name__ == "__main__":
    unittest.main()
