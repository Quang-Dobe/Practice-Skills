# Resilience

> Load when: calling external HTTP services, or adding retry, timeout, or circuit-breaker logic. Pinned: .NET 10 / C# 14.

## Existing repo
- How to recognise it: `AddHttpClient`, `Microsoft.Extensions.Http.Resilience`, `Microsoft.Extensions.Http.Polly` (older), `Polly` / `Polly.Core`, `AddResilienceHandler`, `ResiliencePipeline`.
- Rule: follow what is there. Keep legacy Polly v7 policies (`Policy.Handle...`) unless asked to move.

## New repo default
- Typed clients: `builder.Services.AddHttpClient<TClient>(...)`; the client takes `HttpClient` in its constructor.
- Add `AddStandardResilienceHandler()` (package `Microsoft.Extensions.Http.Resilience`). Defaults, outermost to innermost: rate limiter, 30 s total timeout, 3 retries with exponential backoff and jitter, circuit breaker, 10 s per-attempt timeout.
- Add one resilience handler per client; do not stack them. For a custom set, use `AddResilienceHandler("name", builder => ...)` instead.
- Retries apply to all HTTP methods by default; call `options.Retry.DisableForUnsafeHttpMethods()` for non-idempotent POST, PATCH, PUT, DELETE.
- Non-HTTP work (database, queue, SDK calls): Polly v8 `ResiliencePipeline` (package `Polly.Core`; DI via `Polly.Extensions`).

```csharp
builder.Services.AddHttpClient<PaymentsClient>(c => c.BaseAddress = new("https://payments.example.com"))
    .AddStandardResilienceHandler(o => o.Retry.DisableForUnsafeHttpMethods());

builder.Services.AddHttpClient<SearchClient>(c => c.BaseAddress = new("https://search.example.com"))
    .AddResilienceHandler("search", b => b
        .AddRetry(new HttpRetryStrategyOptions { MaxRetryAttempts = 2, UseJitter = true })
        .AddTimeout(TimeSpan.FromSeconds(5)));

// Non-HTTP: Polly v8
ResiliencePipeline pipeline = new ResiliencePipelineBuilder()
    .AddRetry(new RetryStrategyOptions())
    .AddTimeout(TimeSpan.FromSeconds(10))
    .Build();
await pipeline.ExecuteAsync(static async token => { /* call */ }, ct);
```

## Avoid
- `new HttpClient()` per call → socket exhaustion, no handler pipeline → `AddHttpClient` typed clients.
- Stacking several resilience handlers on one client → compounded retries and timeouts → one handler, or `AddResilienceHandler`.
- Retrying non-idempotent requests → duplicate side effects → `DisableForUnsafeHttpMethods()`.
- Custom retry `ShouldHandle` that ignores Polly's `TimeoutRejectedException` (not `TimeoutException`) → timeouts never retried → handle it explicitly.
- Hand-rolling retry loops with `Task.Delay` → no jitter, no breaker → a Polly pipeline.

## Sources
- https://learn.microsoft.com/dotnet/core/resilience/http-resilience (fetched 2026-10-04; defaults table, `AddResilienceHandler`, retry disabling)
- https://www.pollydocs.org/ (fetched 2026-10-04)
- https://www.pollydocs.org/getting-started.html (fetched 2026-10-04; `Polly.Core`, `Polly.Extensions`, `AddResiliencePipeline`)
