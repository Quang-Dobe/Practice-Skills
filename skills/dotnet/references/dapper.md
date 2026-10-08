# Dapper

> Load when: raw SQL, Dapper. Pinned: .NET 10 / C# 14.

## Existing repo
- How to recognise it: `Dapper` package, `using Dapper;`, calls to `QueryAsync`, `ExecuteAsync`, `QuerySingleAsync` on a `DbConnection`.
- Rule: follow what is there (connection factory vs `NpgsqlDataSource`, SQL in code vs files). Audit any string-built SQL you touch and fix it to parameters.

## New repo default
- Dapper is for reads and hot or reporting queries; EF Core stays the write path (`SaveChanges`, migrations). Both can share one database and one connection string.
- Every value goes in as a parameter: `new { Id = id }` or `DynamicParameters`. Never build SQL from user input.
- Get connections from a singleton `NpgsqlDataSource` (thread-safe; build one per app) and `await using` each connection so it returns to the pool.
- Use the async API (`QueryAsync<T>`, `QuerySingleOrDefaultAsync<T>`, `ExecuteAsync`) and pass a `CommandDefinition` with the `CancellationToken`.
- Multi-mapping: `QueryAsync<Post, User, Post>(sql, map, splitOn: "Id")`; `splitOn` defaults to a column named `Id`.
- Map to small read-model records, not EF entities.

```csharp
builder.Services.AddSingleton(NpgsqlDataSource.Create(
    builder.Configuration.GetConnectionString("Db")!));

public sealed class OrderReadStore(NpgsqlDataSource dataSource)
{
    public async Task<IReadOnlyList<OrderRow>> ForCustomerAsync(
        Guid customerId, CancellationToken ct)
    {
        const string sql = """
            select id, number, total from orders
            where customer_id = @customerId order by created_at desc
            """;
        await using var conn = await dataSource.OpenConnectionAsync(ct);
        var rows = await conn.QueryAsync<OrderRow>(
            new CommandDefinition(sql, new { customerId }, cancellationToken: ct));
        return rows.AsList();
    }
}
```

## Avoid
- String concatenation or interpolation into SQL (`$"... where name = '{name}'"`) → SQL injection → named parameters (`@name`) with an anonymous object or `DynamicParameters`.
- Dynamic identifiers (table, column, `ORDER BY`) from user input → cannot be parameterised → map input to a hard-coded allow-list and pick the SQL fragment from it.
- Dapper literal replacements (`{=name}`) with untrusted values → inlined into SQL → use only for trusted values, sparingly.
- One shared open connection across requests → not thread-safe → one `NpgsqlDataSource`, short-lived connections.
- Dapper for writes that EF already tracks → two sources of truth, bypasses concurrency tokens and interceptors → writes via EF unless a bulk path is measured and justified.
- Forgetting `splitOn` with non-`Id` key columns → wrong object split → set `splitOn` explicitly.

## Sources
- https://github.com/DapperLib/Dapper (fetched 2026-10-04)
- https://www.npgsql.org/doc/basic-usage.html (fetched 2026-10-04)
