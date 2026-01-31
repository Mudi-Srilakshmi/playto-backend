## 1. The Tree (Nested Comments)

Nested comments are modeled using a self-referential foreign key.

- Each `Comment` belongs to a `Post`
- Each `Comment` may optionally reference another `Comment` as its parent
- Top-level comments are identified by `parent = NULL`
- This structure allows arbitrary depth, similar to Reddit-style threads

To avoid N+1 queries, the post detail API fetches all comments for a post in a single query using `prefetch_related` and `select_related` for authors.  
No recursive database queries are performed.

The nested comment tree is constructed in memory using a single-pass algorithm that maps comments by ID and attaches each comment to its parent.  
This guarantees predictable query counts regardless of comment depth.

---

## 2. The Math (Leaderboard – Last 24 Hours)

Karma is not stored as a derived field on the user model.

Each like creates a `KarmaTransaction` record containing the user, the number of points earned, and a timestamp.  
The leaderboard is calculated dynamically by aggregating only transactions from the last 24 hours:

last_24_hours = timezone.now() - timedelta(hours=24)

KarmaTransaction.objects  
    .filter(created_at__gte=last_24_hours)  
    .values('user__username')  
    .annotate(total_karma=Sum('points'))  
    .order_by('-total_karma')[:5]

This approach ensures accurate, time-based results without storing daily or cached karma values on the user model.

---

## 3. The AI Audit

An AI-assisted suggestion proposed serializing nested comments using recursive ORM access patterns.

After reviewing this approach, it was clear that it could lead to N+1 query issues as comment depth increased.  
To address this, I avoided recursive serializers and database access entirely.

Instead, all comments are fetched in a single query and the nested structure is built explicitly in memory, resulting in consistent performance and clear, debuggable logic.
