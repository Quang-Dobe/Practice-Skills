---
name: dotnet
description: Back-end .NET 10 / C# 14 API development — ASP.NET Core REST APIs (Controllers or Minimal APIs), EF Core, Dapper, Redis, MongoDB, messaging, background jobs, auth, OpenTelemetry, Aspire, and xUnit/NUnit/MSTest tests. Use when writing, reviewing, structuring or testing C# code, editing .csproj/.sln/.slnx or Directory.*.props files, or starting a new .NET API. Not for Blazor, MAUI, WPF, Razor Pages or MVC views.
---

# .NET back-end

Pinned: .NET 10 LTS, C# 14. API-only (JSON).
Out of scope: Blazor, MAUI, WPF, Razor Pages, MVC views → say so, load no reference, stop.
Not a .NET/C# code or tooling task at all → this skill doesn't apply: load nothing, skip Step 1.

## Step 1 — Mode check (always first)

1. `<repo>/.claude/conventions/dotnet.md` exists → read it. It overrides every default here and in references.
2. Repo has `*.csproj` but no conventions file → read `references/detect-conventions.md`, scan only folders containing `*.csproj` (ignoring front-end folders in monorepos), write the conventions file, show it to the user; after the user confirms the file, continue to Step 2 for the original task.
3. No `*.csproj` anywhere (new repo) → read `references/choose-conventions.md`, let the user pick, write the conventions file; after the user picks and the file is written, continue to Step 2 for the original task.
4. Code you are touching contradicts the conventions file → stop, tell the user, ask which wins, update the file.

## Step 2 — Route: read every row whose signal matches the task

| Task signal | Read |
|---|---|
| Writing or reviewing any C# code | `references/csharp-style.md` |
| New project or solution, adding a layer or module, moving files, `Directory.Build.props`, `Directory.Packages.props` | `references/project-structure.md` |
| Designing or changing an endpoint: URL, verb, status code, error body, paging | `references/rest-api-design.md` |
| Adding or wiring an endpoint, `MapGet`/`MapPost`, `[ApiController]`, OpenAPI, Swagger, Scalar, API versioning | `references/aspnetcore-api.md` |
| `.proto` files, `Grpc.AspNetCore`, rpc | `references/grpc.md` |
| `Hub` classes, SignalR, real-time push to clients | `references/signalr.md` |
| Commands, queries, handlers, `ISender`, `IRequest`, MediatR, cross-cutting handler behaviour | `references/mediator-pattern.md` |
| Input validation, `AbstractValidator`, Result / ErrorOr, returning errors without exceptions | `references/validation-and-results.md` |
| DTO ↔ entity mapping, Mapster, AutoMapper | `references/mapping.md` |
| `HttpClient`, outbound calls, retry, timeout, circuit breaker, Polly | `references/resilience.md` |
| `DbContext`, EF Core, migrations, Npgsql, SQL Server | `references/efcore.md` |
| Raw SQL, Dapper | `references/dapper.md` |
| Caching, `HybridCache`, `IDistributedCache`, Redis | `references/caching.md` |
| MongoDB, `IMongoCollection` | `references/mongodb.md` |
| Events, queues, consumers, MassTransit, Wolverine, Azure Service Bus, RabbitMQ | `references/messaging.md` |
| `BackgroundService`, `IHostedService`, Hangfire, Quartz, scheduled or recurring work, work after the request returns, fire-and-forget, queued or deferred work | `references/background-jobs.md` |
| Logging, Serilog, tracing, metrics, OpenTelemetry, health checks | `references/observability.md` |
| Aspire (formerly .NET Aspire), AppHost, Dockerfile, container image | `references/aspire-and-containers.md` |
| Login, tokens, JWT, OIDC, Identity, `[Authorize]`, policies, roles | `references/auth.md` |
| Unit tests, mocks, assertions | `references/testing-unit.md` |
| Integration or API tests, `WebApplicationFactory`, Testcontainers | `references/testing-integration.md` |

Several rows match → read each. No row matches → use the always-rules only; never read references speculatively.

## Always-rules

- Nullable reference types on; no `!` suppression without a comment saying why.
- `async` all the way; pass `CancellationToken`; never `.Result` or `.Wait()`.
- Constructor injection; no `IServiceProvider.GetService` in business code.
- Errors to clients as ProblemDetails (RFC 9457).
- New repo: prefer free-licensed libraries. Existing repo: keep the libraries it has; never migrate one unasked.
- Before adding a package: check `Directory.Packages.props` for central versions.
