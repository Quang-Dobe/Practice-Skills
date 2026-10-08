# C# style

> Load when: writing or reviewing any C# code. Pinned: .NET 10 / C# 14.

## Existing repo
- How to recognise it: `.editorconfig` (`[*.cs]` sections, `dotnet_diagnostic.*` entries), `Directory.Build.props` analyzer properties, the surrounding code.
- Rule: follow what is there, including naming and `using` placement. The deepest `.editorconfig` wins; do not restyle files you are not changing.
- A new C# 14 feature is allowed only when the project's `LangVersion` / SDK supports it (C# 14 needs the .NET 10 SDK).

## New repo default
- Naming: PascalCase for types, members, constants, public fields; `I` prefix on interfaces; `Async` suffix on Task-returning methods.
- Fields: `_camelCase` for private/internal instance fields, `s_camelCase` for private static ones. Parameters and locals are camelCase.
- Primary constructor parameters: camelCase on classes and structs, PascalCase on records.
- File-scoped namespaces; `using` directives outside the namespace; `var` only when the type is obvious.
- Records for DTOs, `required` members instead of constructors to force initialisation, collection expressions (`[1, 2]`) everywhere.
- Pattern matching (`is not null`, `switch` expressions) over type checks and casts.
- C# 14, confirmed by the docs: `field` keyword in property accessors, extension members (`extension(...)` blocks incl. properties), null-conditional assignment (`a?.B = x`), `nameof` on unbound generics, modifiers on simple lambda parameters.
- If a type already has a member named `field`, write `@field` or `this.field`.
- `.editorconfig` baseline: `root = true`, `[*.cs]` with `indent_style = space`, `indent_size = 4`, severities via `dotnet_diagnostic.<ID>.severity`.
- `Directory.Build.props`: `Nullable` enable, `AnalysisLevel` `latest-recommended`, `TreatWarningsAsErrors` true, `EnforceCodeStyleInBuild` true.

```csharp
namespace Orders.Features.Create;

public sealed record CreateOrderRequest(string CustomerId, IReadOnlyList<OrderLine> Lines);

public sealed class OrderService(IOrderStore store, TimeProvider clock)
{
    private readonly List<string> _audit = [];

    public string Note
    {
        get;
        set => field = value?.Trim() ?? string.Empty;
    }

    public async Task<Order> CreateAsync(CreateOrderRequest request, CancellationToken ct)
    {
        var order = Order.Create(request.CustomerId, request.Lines, clock.GetUtcNow());
        await store.AddAsync(order, ct);
        _audit.Add(order.Id);
        return order;
    }
}
```

## Avoid
- `.Result` / `.Wait()` → blocks threads, deadlocks → `await` all the way.
- `async void` → exceptions escape, cannot await → return `Task` (event handlers excepted).
- `!` null-forgiving without a comment → hides real nulls → fix the type or comment why it is safe.
- `#region` → hides oversized types → split the type.
- Catching `Exception` without a filter → swallows bugs → catch the specific type you can handle.
- Positional string formats and string `+` in loops → noise, allocations → interpolation, `StringBuilder`.

## Sources
- https://learn.microsoft.com/dotnet/csharp/fundamentals/coding-style/coding-conventions (fetched 2026-10-04)
- https://learn.microsoft.com/dotnet/csharp/fundamentals/coding-style/identifier-names (fetched 2026-10-04)
- https://learn.microsoft.com/dotnet/csharp/whats-new/csharp-14 (fetched 2026-10-04)
- https://learn.microsoft.com/dotnet/fundamentals/code-analysis/overview (fetched 2026-10-04)
- https://learn.microsoft.com/dotnet/fundamentals/code-analysis/configuration-files (fetched 2026-10-04)
