# Aspire and containers

> Load when: task touches Aspire, AppHost, ServiceDefaults, local orchestration, container images, or Dockerfiles. Pinned: .NET 10 / C# 14.

## Existing repo
- How to recognise it: an `*.AppHost` project (`Aspire.AppHost.Sdk`, `AddProject<Projects.X>`), an `*.ServiceDefaults` project, `Aspire.Hosting.*` packages; a `Dockerfile`; or `ContainerRepository`/`PublishContainer` in csproj or CI.
- Rule: follow what is there. If the repo has a `Dockerfile`, edit and build through it; do not replace it with SDK container publish unasked.

## New repo default
- Product name is now "Aspire" (formerly ".NET Aspire"). Docs moved from Microsoft Learn to aspire.dev; the old Learn overview URL returns a 301 to it. Aspire is an orchestration and observability layer for local development and wiring, not an application framework or a production runtime.
- Add Aspire only when the repo has two or more services or backing resources worth wiring (database, cache, queue). A single API plus one database does not need it.
- AppHost project: declares the whole system in code. Resources via `AddPostgres`, services via `AddProject<Projects.Api>("api")`, wiring via `WithReference(db)`.
- ServiceDefaults project: shared setup referenced by every service (OpenTelemetry, health checks `/health` and `/alive`, service discovery, HTTP resilience); services call `AddServiceDefaults()`.
- Container images: `dotnet publish --os linux --arch x64 /t:PublishContainer`. No Dockerfile, and no Docker needed to build; the image goes to the local daemon by default.
- Useful properties: `ContainerRepository` (image name), `ContainerRegistry` (push target, for example `ghcr.io`), `ContainerArchiveOutputPath` (tarball, no daemon needed).

```csharp
// AppHost
var builder = DistributedApplication.CreateBuilder(args);

var db = builder.AddPostgres("pg").AddDatabase("orders");

builder.AddProject<Projects.Orders_Api>("api")
    .WithReference(db)
    .WaitFor(db);

builder.Build().Run();
```

## Avoid
- Treating Aspire as a deployment tool → it is not a production runtime → use it for local orchestration and telemetry; deploy the published images with the repo's existing pipeline.
- Adding a Dockerfile to a repo that has none → duplicate build paths → use `/t:PublishContainer`.
- Rewriting an existing Dockerfile to SDK publish unasked → changes the build contract → leave it.
- Hard-coding connection strings that `WithReference` already injects → drift between AppHost and services → read the injected configuration.
- Citing `learn.microsoft.com/dotnet/aspire` pages or the name ".NET Aspire" → stale → cite aspire.dev.

## Sources
- https://aspire.dev/get-started/what-is-aspire/ (redirect target of https://learn.microsoft.com/dotnet/aspire/get-started/aspire-overview; fetched 2026-10-04)
- https://learn.microsoft.com/dotnet/core/containers/sdk-publish (fetched 2026-10-04)
- https://learn.microsoft.com/dotnet/core/diagnostics/observability-with-otel (ServiceDefaults contents; fetched 2026-10-04)
