# API Reference

Base URL: `/api`. Endpoints marked 🔒 require `Authorization: Bearer <token>`.

## Auth
| Method | Path                | Body                              |
|--------|----------------------|------------------------------------|
| POST   | `/auth/register`     | `{email, password, nickname}`     |
| POST   | `/auth/login`        | `{email, password}`               |

## Profile 🔒
| Method | Path                    | Body |
|--------|--------------------------|------|
| GET    | `/profile/me`            | — |
| PUT    | `/profile/me`             | `{nickname?, avatar_url?}` |
| PUT    | `/profile/me/password`   | `{old_password, new_password}` |

## Videos
| Method | Path                        | Notes |
|--------|------------------------------|-------|
| GET    | `/videos?tag=&sort=`         | `sort`: `clicks` \| `rating` |
| GET    | `/videos/{id}`                | includes `is_favorite` if logged in |
| POST   | `/videos`                     | create/seed a video (see architecture notes on locking this down) |
| POST   | `/videos/{id}/click`          | increments click count, logs history if logged in |
| GET    | `/search?q=...`               | fuzzy title/description search |

## Ratings 🔒
| Method | Path                          | Body |
|--------|--------------------------------|------|
| POST   | `/videos/{id}/rating`          | `{score: 0-5}` |

## Comments
| Method | Path                                        | Auth |
|--------|-----------------------------------------------|------|
| GET    | `/videos/{id}/comments`                       | public |
| POST   | `/videos/{id}/comments`                       | 🔒 `{text}` |
| POST   | `/videos/{id}/comments/{comment_id}/like`     | 🔒 |

## Favorites 🔒
| Method | Path                    |
|--------|--------------------------|
| GET    | `/favorites`             |
| POST   | `/favorites/{video_id}`  |
| DELETE | `/favorites/{video_id}`  |

## History 🔒
| Method | Path        |
|--------|--------------|
| GET    | `/history`   |

## Reports 🔒
| Method | Path                        | Body |
|--------|-------------------------------|------|
| POST   | `/videos/{id}/report`         | `{source_name?, note?}` |
