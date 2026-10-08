# Choose conventions (new repo)

> Load when: no `*.csproj` anywhere (new repo). Pinned: .NET 10 / C# 14.

## Existing repo
- How to recognise it: a `*.csproj` exists. Then this file does not apply; use the detect-conventions reference.
- Rule: an existing conventions file or existing code always beats the defaults below.

## New repo default
- Present the menus below, recommend the default, wait for the user's pick, then write `<repo>/.claude/conventions/dotnet.md` (`mode: new`, `detected-from: []`, one `libraries` line per area) in the format below; create the folder if missing.
- Architecture, one line on when to pick each:
  - n-layer: small CRUD service, few rules.
  - vertical-slice: feature-heavy API. Default recommendation.
  - clean: complex domain, long-lived, many consumers of the core.
  - modular-monolith: several bounded contexts, possible future split.
- Endpoint style: Minimal APIs (default; the ASP.NET Core docs recommend them for new projects) or Controllers (pick when you need model-binder extensibility, `IModelValidator`, application parts, or OData).
- API style: REST with ProblemDetails errors.
- Default free library set. Defaults chosen by the user (2026-10-04), not a doc-verified fact:
  - Data: EF Core + Npgsql. Validation: FluentValidation.
  - Mediator: hand-rolled (see the mediator-pattern reference). Mapping: manual.
  - Testing: xUnit v3 + Shouldly + NSubstitute; integration with WebApplicationFactory + Testcontainers.
  - Logging: Serilog + OpenTelemetry. Packages: Central Package Management.

```markdown
---
stack: dotnet
mode: existing | new
updated: YYYY-MM-DD
detected-from: [paths]
---
architecture: clean | vertical-slice | n-layer | modular-monolith | mixed (<per-folder notes>)
endpoints: controllers | minimal-apis | mixed
api-style: rest | <other>
naming: <deviations from csharp-style.md defaults, or "default">
libraries: <one line per area: data, validation, mapping, mediator, messaging, testing, logging>
testing: <framework> + <assertions> + <mocks>; integration: <WebApplicationFactory/Testcontainers/none>
```

## Avoid
- Choosing for the user → they own the trade-off → show options, recommend, wait.
- Commercial-licence defaults (MediatR v13+, AutoMapper v15+: licence key; FluentAssertions v8: paid for commercial use; MassTransit v9+: commercial) → licence cost in a fresh repo → use the free set above.
- Clean or modular-monolith for a small CRUD API → ceremony without payoff → n-layer or vertical-slice.
- Mixing Controllers and Minimal APIs without a reason → two styles to maintain → pick one, record it.

## Sources
- https://learn.microsoft.com/dotnet/architecture/modern-web-apps-azure/common-web-application-architectures (fetched 2026-10-04)
- https://learn.microsoft.com/aspnet/core/fundamentals/apis (fetched 2026-10-04)
- https://xunit.net/docs/getting-started/v3/getting-started (xUnit v3, fetched 2026-10-04)
- https://docs.shouldly.org/ (Shouldly, fetched 2026-10-04)
- https://nsubstitute.github.io/ (NSubstitute, fetched 2026-10-04)
- https://serilog.net/ (Serilog, fetched 2026-10-04)
- https://docs.fluentvalidation.net/en/latest/ (FluentValidation, fetched 2026-10-04)
- https://testcontainers.com/guides/getting-started-with-testcontainers-for-dotnet/ (Testcontainers, fetched 2026-10-04)
- https://learn.microsoft.com/ef/core/ (EF Core, fetched 2026-10-04)
- https://www.npgsql.org/efcore/ (Npgsql EF Core provider, fetched 2026-10-04)
- https://opentelemetry.io/docs/languages/dotnet/ (OpenTelemetry .NET, fetched 2026-10-04)
- https://learn.microsoft.com/aspnet/core/test/integration-tests (WebApplicationFactory, fetched 2026-10-04)
- https://github.com/LuckyPennySoftware/MediatR and https://github.com/LuckyPennySoftware/AutoMapper (licence key, fetched 2026-10-04)
- https://github.com/fluentassertions/fluentassertions (v8 commercial via Xceed, fetched 2026-10-04)
- https://masstransit.massient.com/configuration/license (v9+ commercial; fetched 2026-10-04, see the messaging reference)
