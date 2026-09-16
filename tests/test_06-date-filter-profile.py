import pytest
from app import app as flask_app
from database.db import init_db, get_db

@pytest.fixture
def app():
    flask_app.config.update({
        'TESTING': True,
        'DATABASE': 'test_spendly.db',  # Use a temporary file instead of :memory:
        'SECRET_KEY': 'test-secret',
        'WTF_CSRF_ENABLED': False,
    })
    with flask_app.app_context():
        with get_db() as conn:
            conn.execute("DROP TABLE IF EXISTS expenses")
            conn.execute("DROP TABLE IF EXISTS users")
        init_db()
        yield flask_app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def auth_client(client):
    """A test client that is already logged in."""
    client.post('/register', data={
        'name': 'Test User',
        'email': 'test@example.com',
        'password': 'testpass'
    })
    client.post('/login', data={
        'email': 'test@example.com',
        'password': 'testpass'
    })
    return client

class TestProfileDateFilter:

    def test_profile_auth_guard(self, client):
        """Unauthenticated users should be redirected to login."""
        response = client.get('/profile')
        assert response.status_code == 302
        assert '/login' in response.location

        # Even with date params
        response = client.get('/profile?date_from=2023-01-01&date_to=2023-01-31')
        assert response.status_code == 302
        assert '/login' in response.location

    def test_profile_no_filter_shows_all_expenses(self, auth_client, app):
        """Accessing profile without filters should show all expenses."""
        with app.app_context():
            with get_db() as conn:
                # Create a user
                user = conn.execute("SELECT id FROM users LIMIT 1").fetchone()
                uid = user['id']
                # Insert expenses across different months
                conn.execute(
                    "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
                    (uid, 100.0, "Food", "2023-01-15", "Jan Expense")
                )
                conn.execute(
                    "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
                    (uid, 200.0, "Bills", "2023-02-15", "Feb Expense")
                )
                conn.commit()

        response = auth_client.get('/profile')
        assert response.status_code == 200
        # Total should be 300.00
        assert b'300.00' in response.data
        assert b'Jan Expense' in response.data
        assert b'Feb Expense' in response.data

    def test_profile_valid_date_range_filters_results(self, auth_client, app):
        """Valid date range should filter stats, transactions, and categories."""
        with app.app_context():
            with get_db() as conn:
                user = conn.execute("SELECT id FROM users LIMIT 1").fetchone()
                uid = user['id']
                # Expense inside range
                conn.execute(
                    "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
                    (uid, 50.0, "Food", "2023-01-10", "Inside Range")
                )
                # Expense on the exact boundary
                conn.execute(
                    "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
                    (uid, 50.0, "Food", "2023-01-20", "Boundary Range")
                )
                # Expense outside range (before)
                conn.execute(
                    "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
                    (uid, 100.0, "Bills", "2022-12-31", "Before Range")
                )
                # Expense outside range (after)
                conn.execute(
                    "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
                    (uid, 100.0, "Bills", "2023-01-21", "After Range")
                )
                conn.commit()

        # Filter for 2023-01-10 to 2023-01-20
        response = auth_client.get('/profile?date_from=2023-01-10&date_to=2023-01-20')
        assert response.status_code == 200

        # Total should be 100.00 (50 + 50)
        assert b'100.00' in response.data
        assert b'Inside Range' in response.data
        assert b'Boundary Range' in response.data
        assert b'Before Range' not in response.data
        assert b'After Range' not in response.data

    def test_profile_no_expenses_in_range(self, auth_client, app):
        """Range with no expenses should show zeros/empty without crashing."""
        with app.app_context():
            with get_db() as conn:
                user = conn.execute("SELECT id FROM users LIMIT 1").fetchone()
                uid = user['id']
                conn.execute(
                    "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
                    (uid, 100.0, "Food", "2023-01-01", "Existing")
                )
                conn.commit()

        # Range in 2024
        response = auth_client.get('/profile?date_from=2024-01-01&date_to=2024-01-31')
        assert response.status_code == 200
        assert b'0.00' in response.data
        assert b'Existing' not in response.data

    @pytest.mark.parametrize("params", [
        {'date_from': 'not-a-date', 'date_to': '2023-01-31'},
        {'date_from': '2023-01-01', 'date_to': 'invalid'},
        {'date_from': '2023-01-01', 'date_to': '2023-01-31-extra'},
    ])
    def test_profile_malformed_dates_fallback(self, auth_client, app, params):
        """Malformed date strings should silently fallback to all time view."""
        with app.app_context():
            with get_db() as conn:
                user = conn.execute("SELECT id FROM users LIMIT 1").fetchone()
                uid = user['id']
                conn.execute(
                    "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
                    (uid, 100.0, "Food", "2023-01-01", "Expense A")
                )
                conn.commit()

        response = auth_client.get('/profile', query_string=params)
        assert response.status_code == 200
        assert b'Expense A' in response.data

    def test_profile_partial_dates_fallback(self, auth_client, app):
        """Providing only one date parameter should fallback to all time view."""
        with app.app_context():
            with get_db() as conn:
                user = conn.execute("SELECT id FROM users LIMIT 1").fetchone()
                uid = user['id']
                conn.execute(
                    "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
                    (uid, 100.0, "Food", "2023-01-01", "Expense A")
                )
                conn.commit()

        # Only date_from
        response = auth_client.get('/profile?date_from=2023-01-01')
        assert response.status_code == 200
        assert b'Expense A' in response.data

        # Only date_to
        response = auth_client.get('/profile?date_to=2023-01-01')
        assert response.status_code == 200
        assert b'Expense A' in response.data

    def test_profile_start_after_end_date_flashes_error(self, auth_client, app):
        """If date_from > date_to, flash error and fallback to all time."""
        with app.app_context():
            with get_db() as conn:
                user = conn.execute("SELECT id FROM users LIMIT 1").fetchone()
                uid = user['id']
                conn.execute(
                    "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
                    (uid, 100.0, "Food", "2023-01-01", "Expense A")
                )
                conn.commit()

        # Start date 2023-02-01 is after End date 2023-01-01
        response = auth_client.get('/profile?date_from=2023-02-01&date_to=2023-01-01')
        assert response.status_code == 200
        assert b'Start date must be before end date.' in response.data
        assert b'Expense A' in response.data
