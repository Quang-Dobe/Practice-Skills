# Integration testing

> Load when: writing API or data-access integration tests, or a task names WebApplicationFactory, Testcontainers or Respawn. Pinned: .NET 10 / C# 14.

## Existing repo
- How to recognise it: `Microsoft.AspNetCore.Mvc.Testing`, `Testcontainers.*`, `Respawn` package references; classes deriving `WebApplicationFactory<...>`; `IClassFixture` / `ICollectionFixture` factories; a docker-compose file used by tests.
- Rule: extend the existing factory and fixtures; keep its database reset strategy and container images. Do not replace a working setup unasked.

## New repo default
- Host: `WebApplicationFactory<Program>` from `Microsoft.AspNetCore.Mvc.Testing`; the app's `Program` must be visible to the test project (`public partial class Program;`).
- Override in `ConfigureWebHost`: swap the connection string / `DbContext` registration for the container, and use `ConfigureTestServices` to replace external clients (payment, email) with fakes.
- Containers: `Testcontainers.PostgreSql` (`PostgreSqlBuilder`), `Testcontainers.Redis` (`RedisBuilder`), `Testcontainers.MongoDb` (`MongoDbBuilder`), `Testcontainers.RabbitMq` (`RabbitMqBuilder`). Pass the image to the builder, for example `new PostgreSqlBuilder("postgres:17")`. Docker must be running.
- Lifetime: one container per test collection, not per test. Implement `IAsyncLifetime` on a shared fixture (`StartAsync` in `InitializeAsync`, `DisposeAsync` in teardown) and share it with a collection fixture (`[CollectionDefinition]`, `ICollectionFixture<T>`, `[Collection]`).
- Schema: apply EF Core migrations once, right after the container starts.
- Isolation: reset data between tests with Respawn (`Respawner.CreateAsync` once, `ResetAsync` before each test) or by rolling back a per-test transaction.
- Keep unit and integration tests in separate projects; keep integration tests for critical paths.

```csharp
public sealed class ApiFactory : WebApplicationFactory<Program>, IAsyncLifetime
{
    private readonly PostgreSqlContainer _db = new PostgreSqlBuilder("postgres:17").Build();

    protected override void ConfigureWebHost(IWebHostBuilder builder) =>
        builder.UseSetting("ConnectionStrings:Default", _db.GetConnectionString());

    public async ValueTask InitializeAsync()
    {
        await _db.StartAsync();
        using var scope = Services.CreateScope();
        await scope.ServiceProvider.GetRequiredService<AppDbContext>().Database.MigrateAsync();
    }

    public override async ValueTask DisposeAsync()
    {
        await _db.DisposeAsync();
        await base.DisposeAsync();
    }
}

[CollectionDefinition("api")]
public sealed class ApiCollection : ICollectionFixture<ApiFactory>;
```

## Avoid
- EF Core in-memory provider for integration tests → it is not a relational database: no transactions, no raw SQL, fewer query types, different semantics (for example case sensitivity), and slower than SQLite in-memory; the EF Core testing-strategy page calls it "highly discouraged" and "only supported for legacy applications" → run against the real engine in a container.
- SQLite as a stand-in for Postgres → different SQL and string comparison behaviour, provider-specific functions fail → Testcontainers with the production engine.
- A new container per test → minutes of startup → one per collection, reset data between tests.
- Tests that share data and run in parallel → flaky failures → one collection, reset with Respawn or rollback.
- Mocking `DbContext` in an integration test → defeats its purpose → use the real one.

## Sources
- https://learn.microsoft.com/aspnet/core/test/integration-tests (fetched 2026-10-04)
- https://dotnet.testcontainers.org/ (fetched 2026-10-04)
- https://dotnet.testcontainers.org/modules/postgres/ (fetched 2026-10-04)
- https://learn.microsoft.com/ef/core/testing/choosing-a-testing-strategy (fetched 2026-10-04)
- https://github.com/jbogard/Respawn (fetched 2026-10-04)
- https://xunit.net/docs/shared-context (fetched 2026-10-04)
- https://xunit.net/docs/getting-started/v3/migration (fetched 2026-10-04)
- https://learn.microsoft.com/dotnet/api/microsoft.aspnetcore.mvc.testing.webapplicationfactory-1.disposeasync (fetched 2026-10-04)
