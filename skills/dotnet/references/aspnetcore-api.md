# ASP.NET Core API Wiring

> Load when: adding or wiring an endpoint, `MapGet`/`MapPost`, `[ApiController]`, OpenAPI, Swagger, Scalar, API versioning. Pinned: .NET 10 / C# 14.

## Existing repo
- How to recognise it: `app.MapGet/MapPost/MapGroup` in `Program.cs` or `*Endpoints.cs` (Minimal APIs); `[ApiController]` classes + `app.MapControllers()` (Controllers); `Swashbuckle.AspNetCore` (`AddSwaggerGen`) or `Microsoft.AspNetCore.OpenApi` (`AddOpenApi`) in the csproj; `Asp.Versioning.*` packages.
- Rule: adding an endpoint = copy the sibling endpoint. Same style (Minimal vs Controller), same group/route prefix, same return-type style, same auth call, same OpenAPI metadata. Never mix styles in one project or migrate unasked.
- Keep Swashbuckle if it is present; do not swap it for built-in OpenAPI unasked.

## New repo default
- Minimal APIs (Microsoft's recommendation for new projects); Controllers only when the repo needs them (complex model validation, filters, conventions).
- One static class per feature with `MapXxx(this IEndpointRouteBuilder)`; compose with `MapGroup` so prefix, auth and tags are set once.
- Return `TypedResults` (`Ok`, `Created`, `NotFound`, `Problem`); several outcomes → `Results<Ok<T>, NotFound>` so OpenAPI sees every response.
- Controllers: `[ApiController]` + `ControllerBase`, `ActionResult<T>`; attribute-validation and 400 ProblemDetails come automatically.
- OpenAPI: package `Microsoft.AspNetCore.OpenApi`; `AddOpenApi()` and `MapOpenApi()` (Development only). UI: Scalar via `Scalar.AspNetCore` (MIT) and `MapScalarApiReference()`, also Development only.
- Versioning: `Asp.Versioning.Http` (Minimal) or `Asp.Versioning.Mvc` (Controllers), MIT; URL segment `/v{version:apiVersion}/...`; add `Asp.Versioning.Mvc.ApiExplorer` for versioned OpenAPI with controllers.
- Add the endpoint, register its `MapXxx` in `Program.cs`, and write a `WebApplicationFactory` test.

```csharp
public static class OrderEndpoints
{
    public static IEndpointRouteBuilder MapOrders(this IEndpointRouteBuilder app)
    {
        var g = app.MapGroup("/v1/orders").WithTags("Orders").RequireAuthorization();

        g.MapGet("/{id:guid}", async Task<Results<Ok<OrderDto>, NotFound>> (
            Guid id, IOrders orders, CancellationToken ct) =>
            await orders.FindAsync(id, ct) is { } o ? TypedResults.Ok(o) : TypedResults.NotFound());

        g.MapPost("/", async (CreateOrder cmd, IOrders orders, CancellationToken ct) =>
        {
            var o = await orders.CreateAsync(cmd, ct);
            return TypedResults.Created($"/v1/orders/{o.Id}", o);
        });
        return app;
    }
}
// Program.cs: builder.Services.AddOpenApi(); ... app.MapOrders();
// if (app.Environment.IsDevelopment()) { app.MapOpenApi(); app.MapScalarApiReference(); }
```

## Avoid
- Business logic inside the lambda or controller action → untestable, bloats `Program.cs` → call a service/handler, keep the endpoint to bind → call → map result.
- Untyped `Results.Ok(...)` where the shape matters → OpenAPI loses the response type → `TypedResults`.
- Exposing OpenAPI/Scalar/Swagger UI in production → information disclosure (Microsoft's guidance: development only) → guard with `IsDevelopment()`.
- Adding Swashbuckle to a new repo → the .NET 10 Web API template uses built-in `AddOpenApi` → use `AddOpenApi` + Scalar.
- Hand-rolled `/api/v2/` copies of handlers → drift → `Asp.Versioning` with a version set.
- Routing/status/error-body questions here → they live in the rest-api-design reference.

## Sources
- https://learn.microsoft.com/aspnet/core/fundamentals/minimal-apis (fetched 2026-10-04) — `MapGroup`, `TypedResults`, binding, auth.
- https://learn.microsoft.com/aspnet/core/fundamentals/openapi/overview (fetched 2026-10-04) — `AddOpenApi`, `MapOpenApi`, `Microsoft.AspNetCore.OpenApi`.
- https://learn.microsoft.com/aspnet/core/fundamentals/openapi/using-openapi-documents (fetched 2026-10-04) — Scalar and Swagger UI snippets, development-only advice.
- https://github.com/dotnet/aspnet-api-versioning (fetched 2026-10-04) — package names, MIT licence.
- https://github.com/scalar/scalar (fetched 2026-10-04) — `Scalar.AspNetCore`, MIT licence.
