import sqlite3
from database.db import get_db

def get_summary_stats(user_id, date_from=None, date_to=None):
    """
    Fetches total spent, transaction count, and the top category for a user,
    optionally filtered by a date range.
    """
    with get_db() as conn:
        # Base query for total and count
        query = "SELECT SUM(amount) as total, COUNT(*) as count FROM expenses WHERE user_id = ?"
        params = [user_id]

        if date_from and date_to:
            query += " AND date BETWEEN ? AND ?"
            params.extend([date_from, date_to])

        stats_row = conn.execute(query, params).fetchone()
        total_spent = stats_row["total"] if stats_row["total"] else 0
        tx_count = stats_row["count"] if stats_row["count"] else 0

        # Top category query
        cat_query = "SELECT category FROM expenses WHERE user_id = ?"
        cat_params = [user_id]
        if date_from and date_to:
            cat_query += " AND date BETWEEN ? AND ?"
            cat_params.extend([date_from, date_to])

        cat_query += " GROUP BY category ORDER BY SUM(amount) DESC LIMIT 1"
        top_cat_row = conn.execute(cat_query, cat_params).fetchone()
        top_category = top_cat_row["category"] if top_cat_row else "None"

        return {
            "total_spent": total_spent,
            "tx_count": tx_count,
            "top_category": top_category
        }

def get_recent_transactions(user_id, limit=10, date_from=None, date_to=None):
    """
    Fetches the most recent transactions for a user, optionally filtered by date range.
    """
    with get_db() as conn:
        query = "SELECT date, category, amount, description FROM expenses WHERE user_id = ?"
        params = [user_id]

        if date_from and date_to:
            query += " AND date BETWEEN ? AND ?"
            params.extend([date_from, date_to])

        query += " ORDER BY date DESC LIMIT ?"
        params.append(limit)

        expenses = conn.execute(query, params).fetchall()
        return [dict(tx) for tx in expenses]

def get_category_breakdown(user_id, date_from=None, date_to=None):
    """
    Fetches spending totals per category, optionally filtered by date range.
    """
    with get_db() as conn:
        # First, get total spent for percentage calculation
        total_query = "SELECT SUM(amount) as total FROM expenses WHERE user_id = ?"
        total_params = [user_id]
        if date_from and date_to:
            total_query += " AND date BETWEEN ? AND ?"
            total_params.extend([date_from, date_to])

        total_row = conn.execute(total_query, total_params).fetchone()
        total_spent = total_row["total"] if total_row["total"] else 0

        # Category-wise totals
        cat_query = "SELECT category, SUM(amount) as total FROM expenses WHERE user_id = ?"
        cat_params = [user_id]
        if date_from and date_to:
            cat_query += " AND date BETWEEN ? AND ?"
            cat_params.extend([date_from, date_to])

        cat_query += " GROUP BY category"
        cat_rows = conn.execute(cat_query, cat_params).fetchall()

        breakdown = []
        for row in cat_rows:
            percentage = (row["total"] / total_spent * 100) if total_spent > 0 else 0
            breakdown.append({
                "category": row["category"],
                "amount": row["total"],
                "percentage": round(percentage)
            })

        return breakdown
