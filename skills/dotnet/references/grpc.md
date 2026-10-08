# gRPC

> Load when: `.proto` files, `Grpc.AspNetCore`, rpc. Pinned: .NET 10 / C# 14.

## Existing repo
- How to recognise it: `*.proto` files; `Grpc.AspNetCore` (server) or `Grpc.Net.Client` (client) and `Grpc.Tools` in a csproj; `<Protobuf Include="..." />` items; `AddGrpc()` and `MapGrpcService<T>()` in `Program.cs`; classes deriving from `Xxx.XxxBase`.
- Rule: this file loads only because the repo already uses gRPC. Edit the `.proto` first, rebuild to regenerate, then change the service. Keep the repo's package names, proto layout and field numbering.
- Never renumber or reuse a field number; add new fields with new numbers (`reserved` for removed ones).
- JSON transcoding (`Microsoft.AspNetCore.Grpc.JsonTranscoding`, `AddJsonTranscoding()`, `google.api.http` options): touch it only if the repo already has it; it supports unary and server-streaming methods only (no client or bidirectional streaming).

## New repo default
- gRPC suits internal service-to-service calls and streaming; public/browser APIs stay REST (see the rest-api-design reference). Do not add gRPC to a REST-only repo unasked.
- Contract first: `.proto` under `Protos/`, `<Protobuf Include="Protos\x.proto" GrpcServices="Server" />`; the `Grpc.Tools` package generates the base classes.
- Server: `AddGrpc()`, `app.MapGrpcService<GreeterService>()`; service derives from the generated `XxxBase`, takes dependencies by constructor.
- gRPC requires HTTP/2. Kestrel supports it; production needs TLS (ALPN) or an explicit `Http2`-only endpoint.
- Deadlines: clients set `deadline:` on every call (there is no default); services pass `context.CancellationToken` to every async call and propagate `context.Deadline` to child calls (or use `.EnableCallContextPropagation()` on the client factory).

```csharp
// Program.cs
builder.Services.AddGrpc();
app.MapGrpcService<OrderService>();

public class OrderService(IOrders orders) : Orders.OrdersBase
{
    public override async Task<OrderReply> GetOrder(GetOrderRequest request, ServerCallContext context)
    {
        var o = await orders.FindAsync(Guid.Parse(request.Id), context.CancellationToken)
            ?? throw new RpcException(new Status(StatusCode.NotFound, "Order not found"));
        return new OrderReply { Id = o.Id.ToString(), Total = o.Total };
    }
}

// Client
var reply = await client.GetOrderAsync(new GetOrderRequest { Id = id },
    deadline: DateTime.UtcNow.AddSeconds(5));
```

## Avoid
- Calls without a deadline → a hung service holds resources forever → always set `deadline`; catch `RpcException` with `StatusCode.DeadlineExceeded`.
- Ignoring `ServerCallContext.CancellationToken` → work continues after the client gave up → pass it into DB and HTTP calls.
- Throwing arbitrary exceptions from services → clients see `Unknown` → throw `RpcException` with a proper `StatusCode`.
- Editing generated code or committing the generated output → overwritten on build → change the `.proto`.
- Changing or reusing field numbers → breaks wire compatibility → add new numbers, `reserved` the old.
- Creating a `GrpcChannel` per call → connection churn → reuse the channel or use the gRPC client factory.

## Sources
- https://learn.microsoft.com/aspnet/core/grpc/ (fetched 2026-10-04) — overview, `.proto` + `<Protobuf>`, `Grpc.AspNetCore`, `MapGrpcService`.
- https://learn.microsoft.com/aspnet/core/grpc/aspnetcore (fetched 2026-10-04) — `AddGrpc`, HTTP/2 and TLS requirement.
- https://learn.microsoft.com/aspnet/core/grpc/deadlines-cancellation (fetched 2026-10-04) — deadlines, cancellation, propagation.
- https://learn.microsoft.com/aspnet/core/grpc/json-transcoding (fetched 2026-10-04) — transcoding package; streaming limited to server streaming (client and bidirectional unsupported), unary methods transcode.
