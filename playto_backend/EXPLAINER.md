# EXPLAINER.md

## 1. Nested Comments (The Tree)

Threaded comments are implemented using a self-referential foreign key on the `Comment` model.  
Top-level comments have `parent = NULL`, while replies reference another comment.

All comments for a post are fetched in a single query using `select_related` and `prefetch_related`, avoiding the N+1 query problem.  
The nested structure is then built in memory, ensuring predictable and efficient database access even for deep comment threads.

---

## 2. Leaderboard Calculation (Last 24 Hours)

Karma is tracked using an immutable `KarmaTransaction` model instead of storing aggregated values on the user model.

The leaderboard is calculated dynamically by aggregating only transactions created within the last 24 hours:

- Filters by `created_at >= now - 24 hours`
- Groups by user
- Sums karma points
- Orders by total karma
- Returns top 5 users

This approach ensures accuracy, flexibility, and compliance with the assignment constraint of not storing daily karma.

---

## 3. Concurrency & Double-Like Protection

Likes are modeled using two explicit tables:
- `PostLike`
- `CommentLike`

Each table enforces a database-level `UniqueConstraint` to guarantee that a user can like a post or comment only once.

All like operations are wrapped inside `transaction.atomic()` blocks, and duplicate likes are handled gracefully via `IntegrityError`.  
This prevents race conditions and karma inflation under concurrent requests.

---

## 4. AI Audit

An initial design used a single generic `Like` model with nullable foreign keys.  
This was refactored into separate `PostLike` and `CommentLike` models to improve data integrity, simplify constraints, and make concurrency handling more robust.

This change was made after reviewing the generated code and validating it against real-world database constraints.

---

## Summary

- Threaded comments are efficiently modeled and fetched without N+1 queries
- Leaderboard is calculated dynamically for the last 24 hours only
- Concurrency and double-like issues are handled at the database and transaction levels
- All design choices prioritize correctness, performance, and clarity
