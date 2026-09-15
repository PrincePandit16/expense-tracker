# Spec: Profile Page Backend Routes

## Overview
While the profile page currently displays user data and spending statistics, it lacks the ability for users to manage their account information. This feature implements the backend logic and necessary routes to allow users to update their name, email, and password, ensuring that the user's profile remains up-to-date.

## Depends on
- 04-profile-page

## Routes
- `POST /profile/update` — Updates the current logged-in user's name, email, or password — logged-in

## Database changes
No database changes. Uses `UPDATE users SET ... WHERE id = ?`.

## Templates
- **Modify:** `templates/profile.html` — Add an "Edit Profile" section or modal with a form that posts to `/profile/update`.

## Files to change
- `app.py`
- `templates/profile.html`

## Files to create
No new files.

## New dependencies
No new dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only
- Passwords hashed with werkzeug
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- Validate that the new email is not already taken by another user before updating.

## Definition of done
- [ ] A user can successfully update their name via the profile page.
- [ ] A user can successfully update their email, and the system prevents updating to an email already in use.
- [ ] A user can update their password, and the new password is correctly hashed in the database.
- [ ] An unauthenticated user attempting to access `/profile/update` is redirected to the login page.
- [ ] Profile updates are reflected immediately on the profile page after submission.
