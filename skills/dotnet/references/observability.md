# Observability: logging, tracing, metrics, health checks

> Load when: task touches logging, Serilog, OpenTelemetry, tracing, metrics, or health checks. Pinned: .NET 10 / C# 14.

## Existing repo
- How to recognise it: `Serilog.AspNetCore`, `UseSerilogRequestLogging`, `OpenTelemetry.*` packages, `MapHealthChecks`, an Aspire `ServiceDefaults` project with `ConfigureOpenTelemetry`, or Application Insights SDK calls.
- Rule: follow what is there. Extend the existing logger and exporter; do not add a second logging stack beside it.

## New repo default
- Logging: Serilog (`Serilog.AspNetCore`). Register with `builder.Services.AddSerilog(...)` and add `app.UseSerilogRequestLogging()` once, early in the pipeline. It condenses the per-request log events into one completion event.
- Pass `writeToProviders: true` to `AddSerilog` so events also reach the OpenTelemetry logging provider; by default Serilog does not write to registered `ILoggerProvider`s, so `UseOtlpExporter()` would export traces and metrics but no logs.
- Use a bootstrap logger (`CreateBootstrapLogger()`) only if startup code needs logging before configuration and DI exist.
- Log with message templates: named placeholders, values passed as arguments, so properties stay structured.
- Telemetry: OpenTelemetry via `AddOpenTelemetry().WithTracing().WithMetrics()`. .NET already emits logs (`ILogger`), metrics (`Meter`) and traces (`ActivitySource`); OTel collects and exports them.
- Export with OTLP (`UseOtlpExporter()`, package `OpenTelemetry.Exporter.OpenTelemetryProtocol`). Set the endpoint through the standard OTel environment variables, not code.
- Instrument ASP.NET Core and `HttpClient` (`OpenTelemetry.Instrumentation.AspNetCore`, `.Http`); add `.SqlClient` only if the repo uses it.
- Health checks: `AddHealthChecks()` + `MapHealthChecks`. Split liveness (no checks, `Predicate = _ => false`) from readiness (checks tagged `ready`).
- Protect health endpoints (`RequireAuthorization()` or `RequireHost("*:port")`) when they are reachable from outside the cluster. With a fallback authorization policy, probes need `.AllowAnonymous()` (else 401 and restart loops); then restrict them with `RequireHost("*:port")` or an internal-only port.

```csharp
builder.Services.AddSerilog((sp, cfg) => cfg
    .ReadFrom.Configuration(builder.Configuration)
    .ReadFrom.Services(sp)
    .Enrich.FromLogContext()
    .WriteTo.Console(), writeToProviders: true);

builder.Services.AddOpenTelemetry()
    .ConfigureResource(r => r.AddService("orders-api"))
    .WithTracing(t => t.AddAspNetCoreInstrumentation().AddHttpClientInstrumentation())
    .WithMetrics(m => m.AddAspNetCoreInstrumentation().AddHttpClientInstrumentation())
    .UseOtlpExporter();

builder.Services.AddHealthChecks()
    .AddCheck<DbReadyCheck>("db", tags: ["ready"]);

var app = builder.Build();
app.UseSerilogRequestLogging();
app.MapHealthChecks("/health/live", new() { Predicate = _ => false })
    .AllowAnonymous().RequireHost("*:8081");
app.MapHealthChecks("/health/ready", new() { Predicate = c => c.Tags.Contains("ready") })
    .AllowAnonymous().RequireHost("*:8081");
```

## Avoid
- `logger.LogInformation($"Order {id} created")` → loses structure, allocates, defeats filtering → `logger.LogInformation("Order {OrderId} created", id)`.
- Logging secrets, tokens, or full request bodies → leaks into log sinks → log ids and outcomes only.
- One `/health` endpoint that runs every dependency check for liveness → a database blip restarts healthy pods → liveness runs no dependency checks.
- Public, unauthenticated health endpoints exposing dependency detail → reveals infrastructure → restrict by authorization or host/port.
- Hard-coding the OTLP endpoint → breaks per environment → use `OTEL_EXPORTER_OTLP_ENDPOINT`.

## Sources
- https://learn.microsoft.com/dotnet/core/diagnostics/observability-with-otel (fetched 2026-10-04)
- https://github.com/serilog/serilog-aspnetcore (fetched 2026-10-04)
- https://github.com/serilog/serilog-extensions-hosting (`SerilogServiceCollectionExtensions.cs`, fetched 2026-10-04; `writeToProviders` default false, XML doc quoted above)
- https://learn.microsoft.com/aspnet/core/host-and-deploy/health-checks (fetched 2026-10-04)
