# Project structure

> Load when: new project or solution, adding a layer or module, moving files, `Directory.Build.props`, `Directory.Packages.props`. Pinned: .NET 10 / C# 14.

## Existing repo
- How to recognise it: `*.sln` / `*.slnx`, `Directory.Build.props`, `Directory.Packages.props`, project folders under `src/` and `tests/`.
- Rule: keep the layout and solution format that exist. Never convert `.sln` to `.slnx` or enable central package management unasked.
- MSBuild uses the first `Directory.Build.props` found walking up from the project and stops there; a nested one must import its parent with `GetPathOfFileAbove`. Same for `Directory.Packages.props`.

## New repo default
- Solution: `dotnet new sln` creates `.slnx` on the .NET 10 SDK (`.sln` on .NET 9 and earlier). Convert with `dotnet sln <file>.sln migrate`.
- Trees (each has `src/` and `tests/`):

```text
n-layer             vertical-slice          clean                     modular-monolith
src/Shop.Api        src/Shop.Api            src/Shop.Domain           src/Shop.Host
src/Shop.Services     Features/Orders/      src/Shop.Application      src/Modules/Orders/{Api,Core,Data}
src/Shop.Data         Common/               src/Shop.Infrastructure   src/Modules/Billing/{Api,Core,Data}
tests/Shop.Tests    tests/Shop.Api.Tests    src/Shop.Api              src/Shared
                                            tests/Shop.Domain.Tests   tests/Orders.Tests
                                            tests/Shop.Api.Tests      tests/Shop.Host.Tests
```
- Dependency direction:
  - n-layer: top to bottom only; Api never touches Data directly.
  - vertical-slice: slices do not reference each other; share via `Common`.
  - clean: Domain references nothing; Application references Domain; Infrastructure and Api reference Application; Api also references Infrastructure, for the composition root only.
  - modular-monolith: modules talk through public contracts or events, never another module's internals or tables.
- `Directory.Build.props` at repo root holds shared settings (see the C# style reference for the analyzer values); `ImplicitUsings` enable.
- Central versions in `Directory.Packages.props`; project files then omit `Version`.

```xml
<Project>
  <PropertyGroup>
    <TargetFramework>net10.0</TargetFramework>
    <Nullable>enable</Nullable>
    <ImplicitUsings>enable</ImplicitUsings>
    <TreatWarningsAsErrors>true</TreatWarningsAsErrors>
    <AnalysisLevel>latest-recommended</AnalysisLevel>
    <ManagePackageVersionsCentrally>true</ManagePackageVersionsCentrally>
  </PropertyGroup>
  <ItemGroup>
    <PackageVersion Include="Serilog.AspNetCore" Version="x.y.z" />
  </ItemGroup>
</Project>
```
- Above is two files shown as one: the first four-plus properties belong in `Directory.Build.props`, `ManagePackageVersionsCentrally` and `PackageVersion` items in `Directory.Packages.props`.

## Avoid
- Version attributes in csproj under central management → conflicts with `Directory.Packages.props` → `VersionOverride` only with a comment.
- Domain referencing EF Core or ASP.NET Core → inverts clean architecture → define interfaces in Application, implement in Infrastructure.
- Cross-slice or cross-module references → hidden coupling → shared contract or event.
- Settings repeated in every csproj → drift → `Directory.Build.props`.
- Relying on `Directory.Build.props` property order for late values → it imports early → use `Directory.Build.targets`.

## Sources
- https://learn.microsoft.com/visualstudio/msbuild/customize-by-directory (fetched 2026-10-04)
- https://learn.microsoft.com/nuget/consume-packages/central-package-management (fetched 2026-10-04)
- https://learn.microsoft.com/dotnet/architecture/modern-web-apps-azure/common-web-application-architectures (fetched 2026-10-04)
- https://learn.microsoft.com/dotnet/core/tools/dotnet-sln (fetched 2026-10-04)
