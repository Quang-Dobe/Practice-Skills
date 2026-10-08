# SignalR

> Load when: `Hub` classes, SignalR, real-time push to clients. Pinned: .NET 10 / C# 14.

## Existing repo
- How to recognise it: classes deriving from `Hub` or `Hub<T>`; `AddSignalR()` and `MapHub<T>("/path")` in `Program.cs`; `IHubContext<T>` injected into services; client packages (`Microsoft.AspNetCore.SignalR.Client`, `@microsoft/signalr`); `Microsoft.AspNetCore.SignalR.StackExchangeRedis` or `Microsoft.Azure.SignalR` for scale-out.
- Rule: this file loads only because the repo already uses SignalR. Match the existing hub style (string `SendAsync` vs `Hub<T>`), client method names and hub routes; client method names are a public contract with the front end.
- Keep the repo's scale-out choice (Redis backplane or Azure SignalR Service); do not swap it.

## New repo default
- SignalR is for server-to-client push (notifications, dashboards, collaboration). Plain request/response stays REST.
- Strongly typed hubs: `Hub<IChatClient>` with an interface of client methods; compile-time checked, no magic strings.
- Push from outside a hub (services, endpoints, background jobs): inject `IHubContext<TestHub, IChatClient>`; never construct or inject the hub itself.
- A hub instance is created per invocation: no state in hub fields; services injected in the constructor are fine; use `IDbContextFactory` or per-call scopes for EF.
- Always `await` `Clients.*` calls.
- Auth: `[Authorize]` on the hub class (optionally a policy) or `MapHub<T>(...).RequireAuthorization()`; browser WebSocket clients send the JWT as `access_token` query string, so read it in `JwtBearerEvents.OnMessageReceived` for the hub path.
- Scale-out: more than one server needs sticky sessions plus a backplane. Azure-hosted → Azure SignalR Service (no sticky sessions needed); own infrastructure → Redis backplane (`AddSignalR().AddStackExchangeRedis(conn)`, still needs sticky sessions).

```csharp
public interface IChatClient { Task ReceiveMessage(string user, string message); }

[Authorize]
public class ChatHub : Hub<IChatClient>
{
    public Task Send(string message) =>
        Clients.All.ReceiveMessage(Context.UserIdentifier ?? "anon", message);
}

// Program.cs
builder.Services.AddSignalR();
app.MapHub<ChatHub>("/hubs/chat");

// Push from a service
public class Notifier(IHubContext<ChatHub, IChatClient> hub)
{
    public Task BroadcastAsync(string text) => hub.Clients.All.ReceiveMessage("system", text);
}
```

## Avoid
- Storing per-connection state in hub fields → each call gets a new hub instance → use `Context.Items` or an external store.
- Injecting or `new`-ing a `Hub` in a service → unsupported → `IHubContext<T>`.
- Exposing exception details to clients → leaks internals; SignalR hides them by default → throw `HubException` only for messages meant for the client.
- Multi-server deploy without a backplane or sticky sessions → messages reach only clients on the same server → Redis backplane or Azure SignalR Service.
- Un-awaited `Clients.All.SendAsync(...)` → call can fail when the hub method finishes first → `await`.
- Sharing one Redis across apps without `ChannelPrefix` → apps receive each other's messages → set a prefix per app.

## Sources
- https://learn.microsoft.com/aspnet/core/signalr/introduction (fetched 2026-10-04) — overview, hubs, transports, scale options.
- https://learn.microsoft.com/aspnet/core/signalr/hubs (fetched 2026-10-04) — `Hub<T>`, DI into hubs, per-call instances, errors.
- https://learn.microsoft.com/aspnet/core/signalr/authn-and-authz (fetched 2026-10-04) — `[Authorize]` on hubs and methods.
- https://learn.microsoft.com/aspnet/core/signalr/scale (fetched 2026-10-04) — sticky sessions, Azure SignalR Service, Redis backplane.
- https://learn.microsoft.com/aspnet/core/signalr/redis-backplane (fetched 2026-10-04) — `Microsoft.AspNetCore.SignalR.StackExchangeRedis`, `AddStackExchangeRedis`, channel prefix.
