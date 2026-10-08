# Mapping

> Load when: converting between entities, DTOs and responses, or touching AutoMapper/Mapster. Pinned: .NET 10 / C# 14.

## Existing repo
- How to recognise it: `AutoMapper` package, `Profile` classes, `IMapper`; or `Mapster` (`Adapt<T>()`, `TypeAdapterConfig`).
- Rule: follow what is there; do not mix mappers.
- Licence: AutoMapper is commercial from v15.0.0 (earlier versions stay Apache 2.0 / MIT). A free Community tier exists under $5M annual revenue, under $10M outside capital, non-government and non-higher-education. Check the installed version before upgrading; never upgrade or migrate unasked.

## New repo default
- Manual mapping: a static `FromEntity` or an extension method per DTO. Explicit, compile-checked, debuggable.
- Mapster (MIT, package `Mapster`) only when there are many mappings; `ProjectToType<T>()` supports queryable projection.
- For reads, project in the query with `Select` to the DTO so EF Core fetches only the needed columns.
- Map at the boundary (handler or endpoint), never inside the domain model.

```csharp
public sealed record OrderDto(Guid Id, string Customer, decimal Total);

public static class OrderMappings
{
    public static OrderDto ToDto(this Order o) => new(o.Id, o.Customer.Name, o.Total);

    // Query-side projection: translated to SQL, no entity materialised.
    public static IQueryable<OrderDto> SelectDto(this IQueryable<Order> q) =>
        q.Select(o => new OrderDto(o.Id, o.Customer.Name, o.Total));
}

// var page = await db.Orders.Where(o => o.Id == id).SelectDto().ToListAsync(ct);
```

## Avoid
- Calling `ToDto()` on a materialised entity list from a big query → loads whole rows and graphs → `Select` projection into the DTO.
- Instance methods or non-translatable calls inside `Select` expressions → client evaluation or runtime errors → keep the expression to constructors and member access.
- AutoMapper in a new repo → commercial from v15 → manual mapping or Mapster.
- Mixing AutoMapper and Mapster, or mapping in `DbContext` → two conventions, hidden coupling → one mapper, mapping at the boundary.

## Sources
- https://github.com/MapsterMapper/Mapster (fetched 2026-10-04; MIT, `Adapt`, `ProjectToType`)
- https://github.com/AutoMapper/AutoMapper (fetched 2026-10-04; README points to licence key and LICENSE.md; terms not stated there)
- https://automapper.io (fetched 2026-10-04; commercial from 15.0.0, Community tier terms)
