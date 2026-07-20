# Sprint 1 Presentation Script — Auth & Profile

*Suggested length: 4-5 minutes. Written to be read almost verbatim, or used as talking-point notes.*

---

## 1. Introduction (30 seconds)

"For Sprint 1, our team delivered the foundation of the Web Video Finder
platform: user registration, login, JWT-based authentication, and profile
management. Everything you'll see today is fully functional end-to-end —
frontend forms, a Flask REST API, and a DynamoDB backend running on AWS."

"Before we walk through the code, here's the request flow we followed for
every feature this sprint: the browser sends a request to our Flask API,
the API validates it and talks to DynamoDB through boto3, and the response
flows back to update the UI."

---

## 2. Ticket 1 — User Registration & Login Interface (5 SP)

"Let's start with registration and login."

**Frontend (`frontend/login.html`, `frontend/js/login.js`)**
"We built a single page with two forms side by side — one for existing users
to log in, one for new users to register. Both forms are wired to our
central API client, `js/api.js`, which wraps the browser's `fetch` API so
every page in the app calls the backend the same way."

**Backend (`backend/routes/auth.py`)**
"On the server side, `POST /api/auth/register` and `POST /api/auth/login`
handle these two flows. Registration validates the email format and
password strength — at least 8 characters with letters and numbers — before
checking DynamoDB for a duplicate account and creating the new user."

**Data layer (`backend/models/user.py`)**
"User records live in a DynamoDB table called `Users`, partitioned by
`user_id`. Because DynamoDB doesn't support arbitrary field lookups the way
a SQL `WHERE` clause does, we added a Global Secondary Index — `email-index`
— so we can look up a user by email in a single query at login time,
without scanning the whole table."

"Passwords are never stored in plain text. We use Werkzeug's
`generate_password_hash`, which applies a salted hash, so even if the table
were ever exposed, raw passwords wouldn't be."

---

## 3. Ticket 2 — Account Authentication using JWT (3 SP)

"Once a user logs in, how do we keep them authenticated on later requests?
We chose JSON Web Tokens — JWT — over server-side sessions, because our
backend on EC2 is stateless: no session store to manage, and it's a natural
fit if we ever move part of this to Lambda later."

**Core file: `backend/utils/auth_helpers.py`**
"After a successful login or registration, `generate_token()` signs a JWT
containing the user's ID and email, with a 24-hour expiry, using a secret
key from our environment configuration. The frontend stores that token in
`localStorage` and attaches it as a `Bearer` token on every subsequent
request."

"For protecting routes, we wrote two decorators: `require_auth`, which
rejects the request with a 401 if the token is missing, invalid, or
expired, and `optional_auth`, for routes that behave differently for
logged-in vs. anonymous users — we'll use that more in later sprints for
things like comments."

"You can see `require_auth` in action on every profile route — that's our
next section."

---

## 4. Ticket 3 — User Profile Management Page (3 SP)

**Backend (`backend/routes/profile.py`)**
"Once authenticated, users can view and edit their profile through three
endpoints: `GET /api/profile/me` to fetch their current info, `PUT
/api/profile/me` to update their nickname and avatar URL, and `PUT
/api/profile/me/password` to change their password — which re-verifies the
current password before accepting a new one."

**Frontend (`frontend/profile.html`, `frontend/js/profile.js`)**
"The profile page loads the user's current data on page load, and submits
changes back through those same endpoints. If someone isn't logged in, we
redirect them straight to the login page instead of showing a broken form."

---

## 5. Live Demo (suggested flow)

1. Open `login.html`, register a new account with an email, password, and
   nickname.
2. Show that we're redirected and the header now displays "Hi, `<nickname>`"
   instead of the login link — that's `js/auth.js` reading the stored user.
3. Go to `profile.html`, change the nickname, save, and refresh to prove it
   persisted (round-tripped through DynamoDB, not just local state).
4. Change the password, log out, and log back in with the new password.
5. *(Optional, if time allows)* Open DevTools → Application → Local Storage
   to show the actual JWT, and briefly decode it on jwt.io to show what's
   inside — user ID, email, expiry — with no password data.

---

## 6. What's Next / Known Limitations

"A few things we're intentionally deferring to later sprints, which we're
flagging now for transparency:

- No email verification or password-reset flow yet — registration is
  immediate.
- No server-side token revocation — logging out just clears the token
  client-side; a stolen token stays valid until it expires.
- Only the `Users` table exists so far; `Videos`, `Ratings`, `Comments`,
  `Favorites`, and `History` land in upcoming sprints, which is why the
  homepage is a placeholder today.

That wraps up Sprint 1 — happy to take questions on any part of the auth
flow or the DynamoDB schema."
