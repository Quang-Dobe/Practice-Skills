# Messaging

> Load when: the task touches a message bus, queues, publish/consume, sagas, or integration events. Pinned: .NET 10 / C# 14.

## Existing repo
- How to recognise it:
  - `MassTransit*` packages, `AddMassTransit(...)`, `IConsumer<T>`, `IPublishEndpoint`.
  - `WolverineFx*` packages, `UseWolverine(...)`, handler classes with `Handle(...)` methods.
  - `Azure.Messaging.ServiceBus`, `ServiceBusClient`, `ServiceBusProcessor`.
  - `RabbitMQ.Client`, `ConnectionFactory`, `IChannel`, `IAsyncBasicConsumer`.
- Rule: follow what is there; never swap the bus library unasked.
- MassTransit licence (verified 2026-10-04 on the project's own site):
  - v9 and later need a paid commercial licence (vendor: Massient); the key must be present at runtime on dev, CI, test and prod machines. Source stays on GitHub (source-available).
  - v8 remains open source under a permissive licence (Apache 2.0 per the GitHub repo page); the vendor's pages give no v8 support end date, so confirm patch support at https://masstransit.massient.com/ before promising patches.
  - Before bumping MassTransit to 9.x in an existing repo, stop and tell the user about the licence. Stay on 8.x unless they decide otherwise.
- Wolverine is MIT licensed; the Service Bus and RabbitMQ SDKs are free.

## New repo default
- Do NOT pick the library silently. Present both options and let the user choose:

| Option | Fits when | Trade-off |
|---|---|---|
| Wolverine (MIT) | want handlers, retries, and a durable outbox/inbox built in | framework conventions to learn; more magic |
| Raw client (`Azure.Messaging.ServiceBus` or `RabbitMQ.Client`) | one broker, simple flows, full control | you write retry, outbox, and dispatch yourself |

- Avoid MassTransit v9 in new repos (commercial); prefer one of the two above.
- Publish-after-commit needs the outbox pattern: write the message to an outbox table in the same DB transaction as the state change, then a dispatcher publishes it. Wolverine ships this (EF Core transactions plus a durable outbox on sending endpoints); with a raw client, build the table and a `BackgroundService` dispatcher.
- Consumers must be idempotent: brokers deliver at least once. Record processed message ids (unique key) or make the handler a natural upsert.
- Message contracts are `record` types in a small shared project with no behaviour and no framework references. Add fields only; never rename or repurpose.
- Azure Service Bus: `ServiceBusClient`, senders and processors are safe to cache as singletons; prefer `DefaultAzureCredential` over connection strings; settle explicitly (`CompleteMessageAsync`).
- RabbitMQ.Client 7+: async API (`CreateConnectionAsync`, `BasicPublishAsync`); keep connections long-lived; never share a channel across threads for publishing; use publisher confirms; copy the payload before the handler returns.

```csharp
// Contract in the shared project.
public sealed record OrderPlaced(Guid MessageId, Guid OrderId, decimal Total);

// Wolverine: transactional outbox over EF Core (host setup).
builder.Host.UseWolverine(opts =>
{
    opts.UseEntityFrameworkCoreTransactions();
    opts.Policies.AutoApplyTransactions();
    opts.Policies.UseDurableOutboxOnAllSendingEndpoints();
});

// Handler discovered by convention; messages it sends or publishes go through the outbox.
public static class OrderPlacedHandler
{
    public static async Task Handle(OrderPlaced msg, AppDbContext db, CancellationToken ct)
    {
        if (await db.Processed.AnyAsync(p => p.Id == msg.MessageId, ct)) return; // idempotent
        db.Processed.Add(new ProcessedMessage(msg.MessageId));
        // ... apply the change; the commit also flushes outgoing messages
    }
}
```

## Avoid
- Publish to the broker inside the request, then `SaveChanges` (or the reverse) → a crash between them loses or duplicates the event → use the outbox.
- Assuming exactly-once delivery → duplicates corrupt state → idempotent consumers keyed on `MessageId`.
- New `ServiceBusClient` or RabbitMQ connection per message → connection churn and port exhaustion → one long-lived instance.
- Sharing domain entities as message contracts → couples services to your schema → dedicated records.
- Upgrading MassTransit to v9 unasked → surprise commercial licence → stay on v8 until the user decides.

## Sources
- https://masstransit.io/ (fetched 2026-10-04; redirects to https://masstransit.massient.com/)
- https://masstransit.massient.com/configuration/license (fetched 2026-10-04)
- https://massient.com/ (fetched 2026-10-04)
- https://github.com/MassTransit/MassTransit (fetched 2026-10-04)
- https://wolverinefx.net/ (fetched 2026-10-04)
- https://wolverinefx.net/guide/durability/ (fetched 2026-10-04)
- https://learn.microsoft.com/azure/service-bus-messaging/service-bus-dotnet-get-started-with-queues (fetched 2026-10-04)
- https://www.rabbitmq.com/client-libraries/dotnet-api-guide (fetched 2026-10-04)
