# MongoDB

> Load when: MongoDB, `IMongoCollection`. Pinned: .NET 10 / C# 14 (MongoDB .NET/C# driver 3.x).

## Existing repo
- How to recognise it: `MongoDB.Driver` package, `IMongoClient`, `IMongoDatabase`, `IMongoCollection<T>`, `BsonClassMap`, `[BsonId]` attributes.
- Rule: follow what is there (attributes vs class maps, wrapper classes). Do not introduce a second mapping style.

## New repo default
- One `IMongoClient` for the whole app, registered as a singleton (the driver docs recommend a singleton lifetime for `MongoClient`).
- Register `IMongoDatabase` and inject `IMongoCollection<T>` (or a small per-aggregate store class that owns the collection); no generic repository.
- Mapping: automatic class maps match properties to fields by name. Customise with `BsonClassMap.RegisterClassMap<T>()` (keeps domain types free of driver attributes) or attributes. Register maps before the types are first used, ideally before creating the client.
- Indexes: create them at startup with `Indexes.CreateManyAsync(...)` and `CreateIndexModel<T>`.
- Transactions: the MongoDB manual lists them as supported on replica sets and sharded clusters (it does not list standalone servers). Use `client.StartSessionAsync()` plus `session.WithTransactionAsync(...)`; pass the session to every operation; no parallel operations inside one transaction. Practical advice (not from the manual): run a single-node replica set in dev and Testcontainers when you need transactions.
- Single-document writes are atomic already; model data so most operations touch one document.

```csharp
BsonClassMap.RegisterClassMap<Order>(m =>
{
    m.AutoMap();
    m.SetIgnoreExtraElements(true);
});

builder.Services.AddSingleton<IMongoClient>(
    _ => new MongoClient(builder.Configuration.GetConnectionString("Mongo")));
builder.Services.AddSingleton(sp =>
    sp.GetRequiredService<IMongoClient>().GetDatabase("shop"));
builder.Services.AddSingleton(sp =>
    sp.GetRequiredService<IMongoDatabase>().GetCollection<Order>("orders"));

// Startup (hosted service):
await orders.Indexes.CreateManyAsync(
[
    new CreateIndexModel<Order>(
        Builders<Order>.IndexKeys.Ascending(o => o.CustomerId)),
    new CreateIndexModel<Order>(
        Builders<Order>.IndexKeys.Ascending(o => o.Number),
        new CreateIndexOptions { Unique = true })
], ct);
```

## Avoid
- New `MongoClient` per request or per operation → excess memory, undisposed resources → one singleton client.
- Registering class maps after the type was already used → the automatic map already exists → register at startup, first.
- Transactions against a standalone `mongod` → the manual lists support only for replica sets and sharded clusters → use a replica set (even single node) wherever transactions run.
- Swallowing exceptions inside `WithTransactionAsync` callbacks → the driver's retry loop can spin forever → rethrow.
- Relying on no indexes, or creating them lazily on the hot path → collection scans → create at startup, review query shapes.
- Generic `IRepository<T>` over `IMongoCollection<T>` → hides filter/projection builders → inject the collection.

## Sources
- https://www.mongodb.com/docs/drivers/csharp/current/ (fetched 2026-10-04)
- https://www.mongodb.com/docs/drivers/csharp/current/connect/mongoclient/ (fetched 2026-10-04)
- https://www.mongodb.com/docs/drivers/csharp/current/crud/transactions/ (fetched 2026-10-04)
- https://www.mongodb.com/docs/manual/core/transactions/ (fetched 2026-10-04)
- https://www.mongodb.com/docs/drivers/csharp/current/indexes/ (fetched 2026-10-04)
- https://www.mongodb.com/docs/drivers/csharp/current/serialization/class-mapping/ (fetched 2026-10-04)
