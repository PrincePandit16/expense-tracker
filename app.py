from flask import Flask, render_template, session, redirect, url_for, request, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from database.db import init_db, seed_db, get_db

app = Flask(__name__)
app.secret_key = "spendly-secret-dev-key"


# ------------------------------------------------------------------ #
# Routes                                                              #
# ------------------------------------------------------------------ #

@app.route("/")
def landing():
    if session.get("user_id"):
        return redirect(url_for("profile"))
    return render_template("landing.html")


@app.route("/register", methods=['GET', 'POST'])
def register():
    if session.get("user_id"):
        return redirect(url_for("profile"))

    if request.method == 'POST':
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")

        hashed_pw = generate_password_hash(password)

        try:
            with get_db() as conn:
                cursor = conn.execute(
                    "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
                    (name, email, hashed_pw)
                )
                user_id = cursor.lastrowid
                conn.commit()

                session["user_id"] = user_id
                session["user_name"] = name
                return redirect(url_for("profile"))
        except Exception as e:
            return render_template("register.html", error="Email already exists or registration failed")

    return render_template("register.html")


@app.route("/login", methods=['GET', 'POST'])
def login():
    if session.get("user_id"):
        return redirect(url_for("profile"))

    if request.method == 'POST':
        email = request.form.get("email")
        password = request.form.get("password")

        with get_db() as conn:
            user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()

            if user and check_password_hash(user["password_hash"], password):
                session["user_id"] = user["id"]
                session["user_name"] = user["name"]
                return redirect(url_for("profile"))

            return render_template("login.html", error="Invalid email or password")

    return render_template("login.html")


@app.route("/terms")
def terms():
    return render_template("terms.html")


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


# ------------------------------------------------------------------ #
# API Routes for Profile                                                  #
# ------------------------------------------------------------------ #

@app.route("/api/profile/transactions")
def api_transactions():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    with get_db() as conn:
        expenses = conn.execute(
            "SELECT date, category, amount, description FROM expenses WHERE user_id = ? ORDER BY date DESC",
            (user_id,)
        ).fetchall()

        transactions = [dict(tx) for tx in expenses]

    return jsonify(transactions)


@app.route("/api/profile/stats")
def get_profile_stats():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    with get_db() as conn:
        # Fetch total spent and transaction count
        stats_row = conn.execute(
            "SELECT SUM(amount) as total, COUNT(*) as count FROM expenses WHERE user_id = ?",
            (user_id,)
        ).fetchone()

        total_spent = stats_row["total"] if stats_row["total"] else 0
        tx_count = stats_row["count"] if stats_row["count"] else 0

        # Fetch top category
        top_cat_row = conn.execute(
            "SELECT category FROM expenses WHERE user_id = ? GROUP BY category ORDER BY SUM(amount) DESC LIMIT 1",
            (user_id,)
        ).fetchone()
        top_category = top_cat_row["category"] if top_cat_row else "None"

        return jsonify({
            "total_spent": total_spent,
            "tx_count": tx_count,
            "top_category": top_category
        })


@app.route("/api/profile/categories")
def api_profile_categories():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    with get_db() as conn:
        # Fetch total spent for percentage calculation
        total_row = conn.execute(
            "SELECT SUM(amount) as total FROM expenses WHERE user_id = ?",
            (user_id,)
        ).fetchone()
        total_spent = total_row["total"] if total_row["total"] else 0

        # Fetch category-wise spending
        cat_rows = conn.execute(
            "SELECT category, SUM(amount) as total FROM expenses WHERE user_id = ? GROUP BY category",
            (user_id,)
        ).fetchall()

        category_totals = []
        for row in cat_rows:
            percentage = (row["total"] / total_spent * 100) if total_spent > 0 else 0
            category_totals.append({
                "name": row["category"],
                "amount": row["total"],
                "percentage": round(percentage)
            })

    return jsonify(category_totals)


# ------------------------------------------------------------------ #
# Placeholder routes — students will implement these                  #
# ------------------------------------------------------------------ #

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("landing"))


@app.route("/profile")
def profile():
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("login"))

    with get_db() as conn:
        # Fetch actual user data
        user_row = conn.execute("SELECT name, email, created_at FROM users WHERE id = ?", (user_id,)).fetchone()
        if not user_row:
            return redirect(url_for("login"))

        user = {
            "name": user_row["name"],
            "email": user_row["email"],
            "joined": user_row["created_at"][:10] # Simplified date
        }

    return render_template("profile.html",
                               user=user,
                               stats={"total_spent": "₹0.00", "tx_count": 0, "top_category": "None"},
                               transactions=[],
                               category_totals=[])


@app.route("/expenses/add")
def add_expense():
    return "Add expense — coming in Step 7"


@app.route("/expenses/<int:id>/edit")
def edit_expense(id):
    return "Edit expense — coming in Step 8"


@app.route("/expenses/<int:id>/delete")
def delete_expense(id):
    return "Delete expense — coming in Step 9"


if __name__ == "__main__":
    with app.app_context():
        init_db()
        seed_db()
    app.run(debug=True, port=5001)
