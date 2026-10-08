# Mediator Pattern

> Load when: adding or changing request/handler plumbing, pipeline behaviors, or `IMediator` / `ISender` usage. Pinned: .NET 10 / C# 14.

## Contents
- Existing repo
- New repo default
- Avoid
- Sources

## Existing repo
- How to recognise it: `MediatR` package reference, `IMediator`, `IRequest<T>`, `IPipelineBehavior<,>`, `services.AddMediatR(...)`.
- Rule: keep it and extend it in its own style (behaviors, not decorators). Never migrate unasked.
- Licence: MediatR is commercial from v13.0.0 (earlier versions stay Apache 2.0). A free Community License exists for orgs under $5M annual revenue, under $10M outside capital, and not government or higher-education. Server apps need a license key. Check the installed version before upgrading.

## New repo default
- No MediatR dependency. Hand-roll three interfaces plus a `Sender`, and add cross-cutting concerns as decorators.
- One handler per request. Handlers never call other handlers; share logic through a plain service.
- `Sender` resolves the handler from `IServiceProvider`. This is the one allowed service-locator spot; nowhere else may inject `IServiceProvider` to resolve services.
- Register handlers with Scrutor `Scan`, wrap with `Decorate`. Rule: the last `Decorate` is the outermost (README: `OtherDecorator -> Decorator -> Decorated`).
- A decorator that needs optional collaborators takes `IEnumerable<T>`. The container injects an empty sequence when none are registered, so it must not throw.

Contracts (exact):

```csharp
public interface IRequest<TResponse>;

public interface IRequestHandler<in TRequest, TResponse>
    where TRequest : IRequest<TResponse>
{
    Task<TResponse> Handle(TRequest request, CancellationToken ct);
}

public interface ISender
{
    Task<TResponse> Send<TResponse>(IRequest<TResponse> request, CancellationToken ct = default);
}
```

Sender (typed wrapper, no `dynamic`):

```csharp
internal sealed class Sender(IServiceProvider sp) : ISender
{
    public Task<TResponse> Send<TResponse>(IRequest<TResponse> request, CancellationToken ct = default)
    {
        var type = typeof(Invoker<,>).MakeGenericType(request.GetType(), typeof(TResponse));
        var invoker = (Invoker<TResponse>)Activator.CreateInstance(type)!;
        return invoker.Invoke(sp, request, ct);
    }
}

internal abstract class Invoker<TResponse>
{
    public abstract Task<TResponse> Invoke(IServiceProvider sp, IRequest<TResponse> request, CancellationToken ct);
}

internal sealed class Invoker<TRequest, TResponse> : Invoker<TResponse>
    where TRequest : IRequest<TResponse>
{
    public override Task<TResponse> Invoke(IServiceProvider sp, IRequest<TResponse> request, CancellationToken ct) =>
        sp.GetRequiredService<IRequestHandler<TRequest, TResponse>>().Handle((TRequest)request, ct);
}
```

Validation decorator:

```csharp
internal sealed class ValidationDecorator<TRequest, TResponse>(
    IRequestHandler<TRequest, TResponse> inner,
    IEnumerable<IValidator<TRequest>> validators) : IRequestHandler<TRequest, TResponse>
    where TRequest : IRequest<TResponse>
{
    public async Task<TResponse> Handle(TRequest request, CancellationToken ct)
    {
        var failures = (await Task.WhenAll(validators.Select(v => v.ValidateAsync(request, ct))))
            .SelectMany(r => r.Errors).ToList();
        if (failures.Count > 0) throw new ValidationException(failures);
        return await inner.Handle(request, ct);
    }
}
```

Registration:

```csharp
services.AddScoped<ISender, Sender>();
services.Scan(s => s.FromAssemblyOf<Program>()
    .AddClasses(c => c.AssignableTo(typeof(IRequestHandler<,>))
        .Where(t => !t.IsGenericTypeDefinition), publicOnly: false)
    .AsImplementedInterfaces().WithScopedLifetime());
services.Decorate(typeof(IRequestHandler<,>), typeof(LoggingDecorator<,>));
services.Decorate(typeof(IRequestHandler<,>), typeof(ValidationDecorator<,>)); // outermost: runs first
```

Notes: the `Where(t => !t.IsGenericTypeDefinition)` filter keeps the open-generic decorators out of the handler scan; they also implement `IRequestHandler<,>`, and registering them as handlers would make a decorator resolve as its own inner handler (circular or wrong resolution). `Decorate(Type, Type)` is a public Scrutor overload; the README shows no open-generic example, so cover it with one integration test. `Decorate` throws when no matching registration exists (`TryDecorate` returns false). `AddClasses` defaults to public types only. The decorator's `ValidationException` becomes a 400 through the global exception handler in the validation-and-results reference; business errors inside handlers stay `Result` values.

## Avoid
- Notifications or domain events through the mediator → hidden fan-out, no delivery guarantees → use the messaging approach.
- Handlers calling other handlers or `ISender` → hidden coupling, nested pipelines → extract a shared service.
- Injecting `IServiceProvider` outside `Sender` → service locator → constructor injection.
- Adding MediatR to a new repo → commercial licence from v13 → the hand-rolled version above.
- Decorators that throw when no validator exists → breaks requests without validators → inject `IEnumerable<IValidator<T>>`.

## Sources
- https://github.com/khellang/Scrutor (fetched 2026-10-04; README and `ServiceCollectionExtensions.Decoration.cs`)
- https://github.com/jbogard/MediatR (fetched 2026-10-04; README: licence key, mediatr.io)
- https://mediatr.io (fetched 2026-10-04; commercial from 13.0.0, Community License terms)
- https://learn.microsoft.com/dotnet/core/extensions/dependency-injection (fetched 2026-10-04)
