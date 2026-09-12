# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Description
Spendly is a personal finance tracker designed to help users log expenses, identify spending patterns, and manage budgets without the complexity of spreadsheets.

## Build and Run Commands
- **Install Dependencies**: `pip install -r requirements.txt`
- **Run Application**: `python app.py` (runs on `http://127.0.0.1:5001`)
- **Run Tests**: `pytest`
- **Run Single Test**: `pytest path/to/test_file.py`

## Architecture
The project follows a standard Flask monolith pattern:
- **Backend**: Flask (`app.py`) manages the application lifecycle and request routing.
- **Frontend**: Server-side rendering using Jinja2 templates with a shared `base.html` for layout consistency.
- **Static Assets**: CSS and JS are served from the `static/` directory.
- **Database**: A SQLite-based persistence layer planned for `database/db.py`.

## Where Things Belong
- `app.py`: Route definitions and main application logic.
- `templates/`: All HTML files. Use `base.html` for shared structure.
- `static/css/`: Stylesheets. Use `style.css` for global variables/reset and page-specific files (e.g., `landing.css`) for unique layouts.
- `static/js/`: Client-side logic. Use `main.js` for global behavior.
- `database/`: All database schema definitions and connection utilities.

## Code Style
- **Python**: Follow PEP 8. Use clear, descriptive function names.
- **HTML**: Use semantic HTML5 elements. Always use `{{ url_for(...) }}` for linking assets and routes.
- **CSS**: Use CSS variables defined in `:root` for colors and spacing to maintain theme consistency.
- **JavaScript**: Vanilla JS only. Avoid global scope pollution; wrap logic in `DOMContentLoaded` listeners.

## Tech Constraints
- **No Frontend Frameworks**: Do not use React, Vue, or any other JS framework.
- **Styling**: Use plain CSS (no Tailwind or Bootstrap unless explicitly requested).
- **Database**: Use SQLite for simplicity.

## Route Status
- **Implemented**:
    - `GET /` (Landing page)
    - `GET /register` (Registration page)
    - `GET /login` (Login page)
    - `GET /terms` (Terms and Conditions)
    - `GET /privacy` (Privacy Policy)
- **Stubs (Pending Implementation)**:
    - `/logout`
    - `/profile`
    - `/expenses/add`
    - `/expenses/<id>/edit`
    - `/expenses/<id>/delete`

## Warnings & Things to Avoid
- **Hardcoded URLs**: Never hardcode paths like `/static/css/style.css`; always use `url_for`.
- **Inline Styles**: Avoid inline CSS; keep styles in the `static/css/` directory.
- **Blocking JS**: Keep JavaScript non-blocking and minimal.
- **Security**: Ensure form inputs are handled safely (though currently using basic Flask templates).
