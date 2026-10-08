# REST API Design

> Load when: designing or changing an endpoint — URL, verb, status code, error body, paging. Pinned: .NET 10 / C# 14.

## Existing repo
- How to recognise it: routes in `MapGroup(...)`/`[Route]`/`[HttpGet]`, error bodies in a `ProblemDetails` shape or a custom envelope, paging params already named (`page`, `limit`, `cursor`, `skip`).
- Rule: copy the existing URL style, error shape, paging parameters and envelope exactly, even if they differ from the defaults below. The conventions file (`.claude/conventions/dotnet.md`) wins over this file.
- Never switch an existing error body to ProblemDetails, or rename params, unasked — that breaks clients.

## New repo default
- Resources are plural nouns (`/orders`); nest at most one level (`/orders/{id}/items`). Deeper graphs: expose the child at top level with a filter.
- Verbs: GET and HEAD are safe; GET, PUT, DELETE are idempotent; POST is neither (RFC 9110).
- Success codes: 200 body returned; 201 + `Location` header on create; 204 no body (PUT/DELETE).
- Error codes: 400 malformed; 401 unauthenticated; 403 forbidden; 404 missing; 409 state conflict; 422 well-formed but semantically invalid; 429 rate limited (add `Retry-After`).
- Every 4xx/5xx body is ProblemDetails (RFC 9457, `application/problem+json`: `type`, `title`, `status`, `detail`, `instance`, plus extension members). Enable with `AddProblemDetails()` + `UseExceptionHandler()` + `UseStatusCodePages()`.
- Paging: cursor by default (`?limit=25&cursor=...`), offset (`?limit=&offset=`) allowed for small/static sets. Cap `limit` server-side. Envelope: `{ "items": [...], "nextCursor": "..." }`.
- Filtering and sorting via query params: `?status=open&sort=-createdAt`. Whitelist sortable fields.
- POST that must not double-apply (payments, orders): accept an `Idempotency-Key` header, store key + response, replay on repeat.
- Versioning: URL segment (`/v1/orders`) by default; setup lives in the aspnetcore-api reference.

```csharp
builder.Services.AddProblemDetails();
var app = builder.Build();
app.UseExceptionHandler();   // unhandled exception -> 500 ProblemDetails
app.UseStatusCodePages();    // empty 4xx/5xx -> ProblemDetails

app.MapPost("/v1/orders", async (CreateOrder cmd, IOrders orders, CancellationToken ct) =>
{
    var order = await orders.CreateAsync(cmd, ct);
    return TypedResults.Created($"/v1/orders/{order.Id}", order);
});

app.MapGet("/v1/orders/{id:guid}", async (Guid id, IOrders orders, CancellationToken ct) =>
    await orders.FindAsync(id, ct) is { } o
        ? TypedResults.Ok(o)
        : TypedResults.Problem(statusCode: 404, title: "Order not found"));
```

## Avoid
- Verbs in paths (`/getOrders`, `/orders/create`) → the HTTP method already carries the verb → `GET /orders`, `POST /orders`.
- 200 with an error in the body → clients and proxies read the status line → return the proper 4xx/5xx.
- Ad-hoc `{ "error": "..." }` bodies in a new repo → every client parses a private format → ProblemDetails.
- Returning the exception message/stack in `detail` → leaks internals → generic `detail`, log the exception, expose `traceId`.
- Unbounded list endpoints → memory and latency blow up → always page with a server-side max.
- Retrying non-idempotent POST blindly → duplicate side effects → require an idempotency key.

## Sources
- https://www.rfc-editor.org/rfc/rfc9457 (fetched 2026-10-04) — problem details members, media type, extensions.
- https://www.rfc-editor.org/rfc/rfc9110 (fetched 2026-10-04) — method safety/idempotency; 201, 204, 409, 422.
- https://learn.microsoft.com/aspnet/core/web-api/handle-errors (fetched 2026-10-04; redirects to the error-handling-api page) — `AddProblemDetails`, `UseExceptionHandler`, `UseStatusCodePages`.
- https://learn.microsoft.com/azure/architecture/best-practices/api-design (fetched 2026-10-04) — plural nouns, `limit`/`offset`, versioning options. It does not cover cursor paging, 429 or idempotency keys; those bullets are design conventions, not quoted from the docs.
