# Architecture Notes

## Data Model (DynamoDB)

| Table       | Partition Key | Sort Key         | Notes                                  |
|-------------|----------------|-------------------|------------------------------------------|
| `Users`     | `user_id`      | —                 | GSI `email-index` (PK `email`) for login |
| `Videos`    | `video_id`     | —                 | `tags` (list), `sources` (list of {name,url}), `click_count`, `rating_sum`, `rating_count` |
| `Ratings`   | `video_id`     | `user_id`         | One item per (video,user) — lets a user overwrite their score |
| `Comments`  | `video_id`     | `comment_id`      | |
| `Favorites` | `user_id`      | `video_id`        | Membership table for the watchlist |
| `History`   | `user_id`      | `sort_key` (`"<iso-ts>#<video_id>"`) | Sort key embeds time so queries return most-recent-first |
| `Reports`   | `report_id`    | —                 | Broken-link reports; `status`: open/reviewed/resolved |

Average rating is **not** stored precomputed per rating — instead
`Videos.rating_sum` / `Videos.rating_count` are updated atomically
(DynamoDB `UpdateItem` with `ADD`-style expressions) whenever a rating is
submitted, and the average is computed on read. This avoids read-modify-write
races on concurrent ratings.

## Auth

Stateless JWT, signed with `JWT_SECRET`, sent as `Authorization: Bearer <token>`.
No server-side session store — logout is purely client-side (the frontend
just deletes the stored token). Consider adding a token blocklist in DynamoDB
if you need hard server-side logout/revocation.

## Request Flow Example: Submitting a Rating

1. Frontend: `POST /api/videos/{id}/rating {score}` with JWT header
2. `routes/ratings.py`: validates score (0-5), decodes JWT via `require_auth`
3. `models/rating.py`: upserts the (video_id, user_id) rating item
4. `models/video.py`: atomically adjusts `rating_sum`/`rating_count` on the video
   (only the *delta* is applied, so an updated rating doesn't double-count)
5. Response includes the freshly computed average for the frontend to render

## Known Simplifications (call out in your report)

- List/search endpoints do a full `Scan` — acceptable for a class-project
  catalog (dozens–hundreds of items); would need a GSI + pagination at scale.
- No pagination on any endpoint yet.
- `POST /api/videos` (catalog seeding) has no admin-role check — lock it down
  before a public demo, or keep it for internal seeding only.
- No refresh tokens — JWT just expires after `JWT_EXPIRES_HOURS`.
