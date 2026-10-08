# Caching

> Load when: caching, `HybridCache`, `IDistributedCache`, Redis. Pinned: .NET 10 / C# 14.

## Existing repo
- How to recognise it: `IMemoryCache`, `IDistributedCache`, `AddStackExchangeRedisCache`, `StackExchange.Redis` / `IConnectionMultiplexer`, `Microsoft.Extensions.Caching.Hybrid`, or FusionCache.
- Rule: follow what is there. Do not migrate `IMemoryCache` or `IDistributedCache` call sites to `HybridCache` unasked.

## New repo default
- `HybridCache` (package `Microsoft.Extensions.Caching.Hybrid`, `builder.Services.AddHybridCache()`): L1 in-process memory plus optional L2 distributed cache.
- Read with `GetOrCreateAsync(key, factory, ...)`. Stampede protection is built in: per key, one caller runs the factory, the others wait (only within one `HybridCache` instance, not across servers).
- L2: install `Microsoft.Extensions.Caching.StackExchangeRedis` and call `AddStackExchangeRedisCache(o => o.Configuration = ...)`; `HybridCache` picks up the registered `IDistributedCache`. Without L2 you still get L1 plus stampede protection.
- L2 needs serialization: `string` and `byte[]` are built in, everything else uses `System.Text.Json`; configure others with `AddSerializer`.
- Keys: trusted identifiers only, with delimiters: `$"orders/{region}/{orderId}"`. Never raw user input (cache flooding). Default max key length 1024; default max payload 1 MB.
- Invalidate with `RemoveAsync(key)` or tags: pass tags to `GetOrCreateAsync`, then `RemoveByTagAsync("tag")`. Tag invalidation is logical ("ignore entries older than now"), and other servers' L1 is not cleared, so keep L1 expiry short.
- Set `Expiration` and `LocalCacheExpiration` via `DefaultEntryOptions` or per call.

```csharp
builder.Services.AddStackExchangeRedisCache(o =>
    o.Configuration = builder.Configuration.GetConnectionString("Redis"));
builder.Services.AddHybridCache(o =>
    o.DefaultEntryOptions = new HybridCacheEntryOptions
    {
        Expiration = TimeSpan.FromMinutes(10),
        LocalCacheExpiration = TimeSpan.FromMinutes(2)
    });

public sealed class ProductReader(HybridCache cache, AppDbContext db)
{
    public ValueTask<ProductDto?> GetAsync(Guid id, CancellationToken ct) =>
        cache.GetOrCreateAsync($"products/{id}",
            async token => await db.Products.AsNoTracking()
                .Where(p => p.Id == id)
                .Select(p => new ProductDto(p.Id, p.Name))
                .FirstOrDefaultAsync(token),
            tags: ["products"], cancellationToken: ct);
}
```

## Avoid
- Raw user input in cache keys → key flooding, DoS, confused entries → build keys from trusted IDs or allow-listed values.
- Concatenating keys without a delimiter (`order{a}{b}`) → `42`+`123` collides with `421`+`23` → use `/` or `_`.
- Mutating cached objects → by default each caller gets its own deserialized copy; instance reuse is only safe for a `sealed` type marked `[ImmutableObject(true)]` → cache immutable DTOs.
- Creating a `ConnectionMultiplexer` per request → the client is designed to be shared across threads → one shared instance (or let `AddStackExchangeRedisCache` own it).
- Assuming `RemoveByTagAsync` clears other servers' memory → only the current server and L2 are affected → short `LocalCacheExpiration` for data that must go stale fast.
- Hand-rolled get-then-set cache code → stampede on a cold key → `GetOrCreateAsync`.

## Sources
- https://learn.microsoft.com/aspnet/core/performance/caching/hybrid (fetched 2026-10-04)
- https://seredis.dev/ (redirect target of https://stackexchange.github.io/StackExchange.Redis/; fetched 2026-10-04)
