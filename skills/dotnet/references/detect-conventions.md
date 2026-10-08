# Detect conventions (existing repo)

> Load when: the repo has `*.csproj` but no `.claude/conventions/dotnet.md`. Pinned: .NET 10 / C# 14.

## Existing repo
- How to recognise it: at least one `*.csproj` exists and `<repo>/.claude/conventions/dotnet.md` does not.
- Scan scope: only folders that contain a `*.csproj` (monorepo safe). Sample at most 10 source files; never read the whole repo.
- Scan order, stop reading a layer once it answers the question:
  1. `global.json` (SDK pin) then `*.sln` / `*.slnx`.
  2. `Directory.Build.props`, then `Directory.Packages.props` (`ManagePackageVersionsCentrally` means central versions).
  3. `.editorconfig` (deepest file wins; `root = true` stops inheritance), `.globalconfig`.
  4. Each csproj: `TargetFramework`, `Nullable`, `ImplicitUsings`, `TreatWarningsAsErrors`, `AnalysisLevel`, `PackageReference` ids.
- Architecture heuristics:
  - `Domain` + `Application` + `Infrastructure` projects: clean.
  - `Features/<Name>/` folders: vertical-slice.
  - `Controllers/` + `Services/` + `Repositories/`: n-layer.
  - `Modules/<Name>/` each with own data and endpoints: modular-monolith.
  - Conflicting signals: `mixed`, with one note per folder.
- Endpoint style: `[ApiController]` classes mean controllers; `MapGet`/`MapPost`/`MapGroup` mean minimal-apis; both present means mixed.
- Library detection, package id prefix to conventions field:
  - data: `Microsoft.EntityFrameworkCore*`, `Npgsql*`, `Dapper`, `MongoDB.Driver`, `StackExchange.Redis`.
  - validation: `FluentValidation*`. mapping: `Mapster`, `AutoMapper`. mediator: `MediatR`, `Mediator`, or hand-rolled `ISender`.
  - messaging: `MassTransit*`, `Wolverine*`, `Azure.Messaging.ServiceBus`, `RabbitMQ.Client`.
  - testing framework: `xunit*`, `NUnit`, `MSTest*`. assertions: `Shouldly`, `AwesomeAssertions`, `FluentAssertions`. mocks: `NSubstitute`, `Moq`.
  - integration: `Microsoft.AspNetCore.Mvc.Testing` (WebApplicationFactory), `Testcontainers*`; none of these means `none`.
  - logging: `Serilog*`, `OpenTelemetry*`.
- Licence notes: MediatR v13+ and AutoMapper v15+ need a licence key (free Community tier exists); earlier versions keep their open-source licences. FluentAssertions v8+ needs a paid licence for commercial use; MassTransit v9+ is commercial, v8 stays Apache-2.0. Record them as present and keep them.
- Rule: write what is there, not what is preferred. Record naming only where it deviates from the C# style defaults.
- Write the file: create `<repo>/.claude/conventions/` if missing, write `dotnet.md` there in the format in the code block under New repo default, `mode: existing`.
- `detected-from`: list the files you actually read, not the ones you skipped.
- Show the file to the user and wait for confirmation before coding. Still unclear: write `mixed (<notes>)` and ask which wins.

## New repo default
- Not applicable to repos with a `*.csproj`; with no `*.csproj` anywhere, use the choose-conventions reference instead.
- Same file format, `mode: new` instead of `mode: existing`.

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
- Scanning every file → slow, floods context → sample ≤ 10 files per csproj folder.
- Guessing a convention from one file → one outlier misleads → confirm with 2+ files or the `.editorconfig`.
- Writing the file without showing it → user cannot correct detection errors → show it and ask before coding.
- Suggesting migration off a commercial-licence library → never asked for → note the licence, keep it.

## Sources
- https://learn.microsoft.com/dotnet/fundamentals/code-analysis/configuration-files (fetched 2026-10-04)
- https://learn.microsoft.com/nuget/consume-packages/central-package-management (fetched 2026-10-04)
- https://github.com/LuckyPennySoftware/MediatR (fetched 2026-10-04; licence key)
- https://github.com/LuckyPennySoftware/AutoMapper (fetched 2026-10-04; licence key)
- https://github.com/fluentassertions/fluentassertions (fetched 2026-10-04; v8 commercial via Xceed)
- https://masstransit.massient.com/configuration/license (v9+ commercial, v8 Apache-2.0; fetched 2026-10-04, see the messaging reference)
