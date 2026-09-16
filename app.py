from flask import Flask, render_template, session, redirect, url_for, request, jsonify, flash
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, timedelta
from database.db import init_db, seed_db, get_db, close_db
from database.queries import get_summary_stats, get_recent_transactions, get_category_breakdown

app = Flask(__name__)
app.secret_key = "spendly-secret-dev-key"
app.config['DATABASE'] = 'spendly.db'

app.teardown_appcontext(close_db)


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

    # 1. Date filter handling
    date_from = request.args.get("date_from")
    date_to = request.args.get("date_to")
    valid_filter = False

    if date_from and date_to:
        try:
            # Validate ISO date format
            datetime.strptime(date_from, "%Y-%m-%d")
            datetime.strptime(date_to, "%Y-%m-%d")

            if date_from > date_to:
                flash("Start date must be before end date.")
                date_from, date_to = None, None
            else:
                valid_filter = True
        except ValueError:
            # Silently fallback to all time if date is malformed
            date_from, date_to = None, None

    # 2. Fetch data using centralized query helpers
    stats = get_summary_stats(user_id, date_from, date_to)
    transactions = get_recent_transactions(user_id, date_from=date_from, date_to=date_to)
    category_totals = get_category_breakdown(user_id, date_from, date_to)

    # 3. Compute Preset dates for the template buttons
    today = datetime.now()

    # This Month: First day of current month to today
    this_month_start = today.replace(day=1).strftime("%Y-%m-%d")
    this_month_end = today.strftime("%Y-%m-%d")

    # Last 3 Months: Today - 90 days to today
    three_month_start = (today - timedelta(days=90)).strftime("%Y-%m-%d")
    three_month_end = today.strftime("%Y-%m-%d")

    # Last 6 Months: Today - 180 days to today
    six_month_start = (today - timedelta(days=180)).strftime("%Y-%m-%d")
    six_month_end = today.strftime("%Y-%m-%d")

    return render_template(
        "profile.html",
        user_id=user_id,
        stats=stats,
        transactions=transactions,
        category_totals=category_totals,
        date_from=date_from,
        date_to=date_to,
        presets={
            "this_month": (this_month_start, this_month_end),
            "last_3": (three_month_start, three_month_end),
            "last_6": (six_month_start, six_month_end)
        }
    )


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
