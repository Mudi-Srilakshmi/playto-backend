## 1. The Tree (Nested Comments)

Comments are modeled using a self-referential foreign key.

- Each `Comment` belongs to a `Post`
- Each `Comment` can optionally reference another `Comment` as its parent
- Top-level comments are identified by `parent = NULL`
- Replies are accessed using the `replies` related name

To avoid N+1 queries, nested comments are not loaded recursively from the database.  
Instead, the post detail API uses `select_related` and `prefetch_related` to load the post, comments, replies, and their authors in a fixed number of queries.  
The nested structure is then assembled in memory during serialization.

---

## 2. The Math (Leaderboard – Last 24 Hours)

Karma is not stored as a derived field on the user model.

Each like creates a `KarmaTransaction` record containing the user, points, and timestamp.  
The leaderboard is calculated dynamically by aggregating only transactions from the last 24 hours:

```python
last_24_hours = timezone.now() - timedelta(hours=24)

KarmaTransaction.objects
    .filter(created_at__gte=last_24_hours)
    .values('user__username')
    .annotate(total_karma=Sum('points'))
    .order_by('-total_karma')[:5]
```

This ensures accurate, time-based results without storing daily karma on the user model.

---

## 3. The AI Audit

An AI-assisted suggestion proposed loading nested comments using recursive ORM queries.

After reviewing this approach, it was clear that it would cause N+1 query issues as the depth of replies increased.  
I replaced this with an explicit `select_related` and `prefetch_related` strategy and built the comment tree in memory, resulting in predictable query counts and improved performance.
