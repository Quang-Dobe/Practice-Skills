# EF Core

> Load when: `DbContext`, EF Core, migrations, Npgsql, SQL Server. Pinned: .NET 10 / C# 14 (EF Core 10, LTS, supported to 2028-11-10).

## Existing repo
- How to recognise it: `Microsoft.EntityFrameworkCore.*` package, a class deriving `DbContext`, a `Migrations/` folder with a `*ModelSnapshot.cs`, `UseNpgsql` / `UseSqlServer` calls.
- Rule: follow what is there (provider, config style, repository or none). Check the EF Core package version before using a feature below; EF Core 10 needs .NET 10 and will not run on earlier .NET.
- Never rewrite old migrations; add a new one.

## New repo default
- Provider: Npgsql (`Npgsql.EntityFrameworkCore.PostgreSQL`, `UseNpgsql(connectionString)`). SQL Server: `UseSqlServer` from the SQL Server provider package. Match the provider major version to EF Core 10.
- Register with `AddDbContext`; switch to `AddDbContextPool` only when profiling shows context setup cost. Pooled contexts are reused: no per-request state in fields or `OnConfiguring`.
- One `IEntityTypeConfiguration<T>` class per entity; load with `modelBuilder.ApplyConfigurationsFromAssembly(...)` (order undefined, parameterless constructors only).
- Reads: `AsNoTracking()` plus `Select` projection to DTOs; avoid lazy loading (N+1); use `Take` or keyset paging.
- Bulk changes: `ExecuteUpdateAsync` / `ExecuteDeleteAsync`. They run immediately, bypass the change tracker and open no transaction; do not mix with tracked `SaveChanges` edits on the same rows. EF Core 10 accepts a plain (non-expression) lambda in `ExecuteUpdateAsync`, so conditional `SetProperty` calls are easy.
- Migrations: `dotnet ef migrations add <Name>`; deploy with `dotnet ef migrations bundle --output artifacts/efbundle` run as a one-shot job (or `dotnet ef migrations script --idempotent` when SQL needs review). Use a schema-capable identity for deploy, a data-only identity at runtime. Review every generated migration.
- No generic repository over EF: `DbContext` is already unit of work and `DbSet<T>` a repository. Inject the context into handlers/services.
- EF Core 10 features, if needed: named query filters (`HasQueryFilter("name", ...)`), complex types mapped with `ToJson()`, `LeftJoin`/`RightJoin` LINQ operators.

```csharp
builder.Services.AddDbContext<AppDbContext>(o =>
    o.UseNpgsql(builder.Configuration.GetConnectionString("Db")));

public sealed class OrderConfiguration : IEntityTypeConfiguration<Order>
{
    public void Configure(EntityTypeBuilder<Order> b)
    {
        b.ToTable("orders");
        b.HasKey(o => o.Id);
        b.Property(o => o.Number).HasMaxLength(32).IsRequired();
    }
}

// AppDbContext.OnModelCreating:
// modelBuilder.ApplyConfigurationsFromAssembly(typeof(AppDbContext).Assembly);

var rows = await db.Orders.AsNoTracking()
    .Where(o => o.CustomerId == customerId)
    .Select(o => new OrderDto(o.Id, o.Number, o.Total))
    .ToListAsync(ct);

await db.Orders.Where(o => o.Status == Status.Expired)
    .ExecuteDeleteAsync(ct);
```

## Avoid
- `FromSqlRaw` with string concatenation or interpolation → SQL injection (EF Core 10 analyzer warns on concatenation) → `FromSql` / `FromSqlInterpolated` so values become parameters.
- Generic `IRepository<T>` over `DbContext` → hides `Include`/projection, duplicates what EF gives → use the context directly.
- `Database.MigrateAsync()` at startup in production → needs schema rights in the app, no SQL review → migration bundle or script.
- `EnsureCreatedAsync()` before or instead of migrations → bypasses migrations, later `MigrateAsync()` fails → migrations only.
- Tracking queries for read-only endpoints → needless snapshot cost → `AsNoTracking()`.
- Loading entities then looping to update/delete → many round trips → `ExecuteUpdateAsync` / `ExecuteDeleteAsync`.
- Lazy loading proxies → hidden N+1 → `Include`, projection, or split queries.
- Owned entity types for JSON or table splitting in EF Core 10 → reference semantics, no `ExecuteUpdate` support → complex types.

## Sources
- https://learn.microsoft.com/ef/core/ (fetched 2026-10-04)
- https://learn.microsoft.com/ef/core/what-is-new/ef-core-10.0/whatsnew (fetched 2026-10-04)
- https://learn.microsoft.com/ef/core/managing-schemas/migrations/ (fetched 2026-10-04)
- https://learn.microsoft.com/ef/core/managing-schemas/migrations/applying (fetched 2026-10-04)
- https://learn.microsoft.com/ef/core/saving/execute-insert-update-delete (fetched 2026-10-04)
- https://learn.microsoft.com/ef/core/performance/efficient-querying (fetched 2026-10-04)
- https://learn.microsoft.com/ef/core/performance/advanced-performance-topics (fetched 2026-10-04)
- https://learn.microsoft.com/ef/core/modeling/ (fetched 2026-10-04)
- https://www.npgsql.org/efcore/ (fetched 2026-10-04)
- https://www.npgsql.org/efcore/release-notes/10.0.html (fetched 2026-10-04)
