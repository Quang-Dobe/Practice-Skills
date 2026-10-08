# Background Jobs

> Load when: the task needs recurring work, scheduled jobs, a hosted worker, or fire-and-forget background processing. Pinned: .NET 10 / C# 14.

## Existing repo
- How to recognise it:
  - `: BackgroundService` or `IHostedService` classes, `AddHostedService<T>()`.
  - `Quartz`, `Quartz.Extensions.Hosting`, `IJob`, `AddQuartz(...)`.
  - `Hangfire.*` packages, `BackgroundJob.Enqueue`, `RecurringJob`, `UseHangfireDashboard`.
- Rule: follow what is there; do not move jobs between schedulers unasked.
- Hangfire: the docs list paid Pro/Ace editions as separate products; licence: check https://www.hangfire.io/ before adding add-ons. Quartz.NET and `BackgroundService` ship free.

## New repo default
- Simple loop (poll, flush, cleanup): `BackgroundService` with `PeriodicTimer`, registered via `AddHostedService<T>()`.
- Hosted services are singletons: resolve scoped services (DbContext, handlers) per iteration through `IServiceScopeFactory`, never by constructor injection.
- Cron or calendar schedules, misfire handling, clustering: Quartz.NET (`Quartz.Extensions.Hosting`; current line is 4.x, 3.x still maintained). Set `WaitForJobsToComplete = true` for graceful stop.
- Dashboard, persistent retries, fire-and-forget or delayed jobs: Hangfire (needs a storage such as SQL Server or Redis). Dashboard allows local access only by default; configure authorization before exposing it.
- Graceful shutdown: pass `stoppingToken` to every awaited call, exit the loop when it is cancelled, and keep each iteration short.
- Catch and log exceptions inside the loop; an unhandled exception in `ExecuteAsync` stops the worker.
- Work that must survive restarts belongs in a durable store (Quartz persistent store, Hangfire storage, or an outbox table), not in memory.

```csharp
public sealed class CleanupWorker(
    IServiceScopeFactory scopes, ILogger<CleanupWorker> logger) : BackgroundService
{
    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        using var timer = new PeriodicTimer(TimeSpan.FromMinutes(5));
        try
        {
            while (await timer.WaitForNextTickAsync(stoppingToken))
            {
                try
                {
                    await using var scope = scopes.CreateAsyncScope();
                    var db = scope.ServiceProvider.GetRequiredService<AppDbContext>();
                    await db.Sessions.Where(s => s.ExpiresAt < DateTime.UtcNow)
                        .ExecuteDeleteAsync(stoppingToken);
                }
                catch (Exception ex) when (ex is not OperationCanceledException)
                {
                    logger.LogError(ex, "Cleanup iteration failed");
                }
            }
        }
        catch (OperationCanceledException) { } // normal shutdown
    }
}
```

## Avoid
- Injecting a scoped service into a hosted service constructor → DI scope-validation error or a captured, stale DbContext → `IServiceScopeFactory` per iteration.
- `Task.Delay` loops with drift and no cancellation → timing slips and slow shutdown → `PeriodicTimer` with `stoppingToken`.
- `async void` or fire-and-forget `Task.Run` in request code → lost exceptions, killed on shutdown → hosted service or a job library.
- `.Wait()` or `.Result` in `ExecuteAsync` → blocks host startup → await everything.
- Hangfire dashboard exposed without an authorization filter → anyone can run or delete jobs → add an auth filter.
- Running a scheduler on multiple replicas without clustering or a lock → duplicate execution → Quartz clustered store or Hangfire storage locks.

## Sources
- https://learn.microsoft.com/dotnet/core/extensions/workers (fetched 2026-10-04)
- https://www.quartz-scheduler.net/documentation/ (fetched 2026-10-04)
- https://www.quartz-scheduler.net/documentation/quartz-3.x/packages/hosted-services-integration.html (fetched 2026-10-04)
- https://docs.hangfire.io/ (fetched 2026-10-04)
- https://docs.hangfire.io/en/latest/getting-started/aspnet-core-applications.html (fetched 2026-10-04)
